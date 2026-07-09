"""Communication compression for body deltas.

Pipeline per client upload:
    delta = body_after_local_training - body_received
    delta += error_feedback_residual          # add back last round's dropped mass
    keep top-k entries (per layer, k allocated by a RUL-sensitivity proxy)
    optionally quantize kept values to `quant_bits`
    residual = delta - decompressed(compressed)   # stored for next round

`bytes_uploaded` accounts only for kept values (index + quantized/float value),
so the reported communication cost reflects the compression honestly.
"""
import torch


class Compressor:
    """Stateful (keeps per-layer error-feedback residuals) per client."""

    def __init__(self, cfg):
        self.cfg = cfg
        self.residual = {}   # layer -> tensor

    # ---- sensitivity proxy -------------------------------------------------
    @staticmethod
    def _layer_sensitivity(delta):
        """Proxy for how much RUL error responds to perturbing a layer.

        We use the layer's delta energy (L2) as a cheap, gradient-free proxy:
        layers that changed a lot this round are the ones carrying task signal.
        A more faithful proxy (loss Hessian diag) can be swapped in here.
        """
        return {k: float(v.pow(2).sum().sqrt()) + 1e-12 for k, v in delta.items()}

    def _alloc_k(self, delta, base_ratio):
        """Distribute the global keep-budget across layers by sensitivity."""
        total = sum(v.numel() for v in delta.values())
        budget = max(1, int(base_ratio * total))
        if not self.cfg.sensitivity_weighting:
            return {k: max(1, int(base_ratio * v.numel())) for k, v in delta.items()}
        sens = self._layer_sensitivity(delta)
        s_sum = sum(sens.values())
        k = {}
        for name, v in delta.items():
            share = sens[name] / s_sum
            k[name] = min(v.numel(), max(1, int(budget * share)))
        return k

    # ---- (de)compression ---------------------------------------------------
    def compress(self, delta):
        """Return (compressed_payload, bytes_uploaded).

        compressed_payload is a dict: layer -> (indices, values, shape).
        """
        if not self.cfg.compress:
            payload = {k: (None, v.clone(), tuple(v.shape)) for k, v in delta.items()}
            nbytes = sum(v.numel() * 4 for v in delta.values())
            return payload, nbytes

        # error feedback
        for name, v in delta.items():
            if name in self.residual:
                delta[name] = v + self.residual[name]

        kmap = self._alloc_k(delta, self.cfg.topk_ratio)
        payload, nbytes = {}, 0
        for name, v in delta.items():
            flat = v.flatten()
            k = min(kmap[name], flat.numel())
            _, idx = torch.topk(flat.abs(), k)
            vals = flat[idx].clone()

            if self.cfg.quant_bits:
                vals, scale, zero = _quantize(vals, self.cfg.quant_bits)
                bytes_val = k * self.cfg.quant_bits / 8 + 8   # +scale/zero
                dvals = _dequantize(vals, scale, zero)
            else:
                bytes_val = k * 4
                dvals = vals

            payload[name] = (idx.cpu(), dvals.cpu(), tuple(v.shape))
            nbytes += bytes_val + k * 4   # +4 bytes per index

            # update error-feedback residual
            recon = torch.zeros_like(flat)
            recon[idx] = dvals.to(flat.dtype)
            self.residual[name] = (flat - recon).reshape(v.shape).clone()

        return payload, int(nbytes)

    @staticmethod
    def decompress(payload, ref_state):
        """Rebuild a full body-delta state dict from a sparse payload."""
        out = {}
        for name, (idx, vals, shape) in payload.items():
            if idx is None:              # uncompressed path
                out[name] = vals.clone().reshape(shape)
                continue
            flat = torch.zeros(int(torch.tensor(shape).prod()), dtype=vals.dtype)
            flat[idx] = vals
            out[name] = flat.reshape(shape)
        return out


def _quantize(x, bits):
    qmax = (1 << bits) - 1
    lo, hi = float(x.min()), float(x.max())
    scale = (hi - lo) / qmax if hi > lo else 1.0
    zero = lo
    q = torch.clamp(((x - zero) / scale).round(), 0, qmax)
    return q, scale, zero


def _dequantize(q, scale, zero):
    return q * scale + zero
