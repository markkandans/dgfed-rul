"""Server-side aggregation of body deltas.

Given the updates uploaded this round (each already decompressed to a full body
delta), combine them into a new global body. Two rules:

  fedavg          : data-size weighted mean of deltas.
  dgfed (ours)    : weight = data_size * staleness_factor * drift_factor, with
                    per-update divergence clipping to protect the shared
                    representation from stale / anomalous clients.

The drift signal that scheduled each client's communication is the *same* signal
used here to weight it — closing the control loop.
"""
import numpy as np
import torch

from .compression import Compressor


def _weight(update, cfg):
    w = float(update["n"])
    if cfg.staleness_aware:
        age = max(0, update["age"])
        w *= cfg.stale_tau0 / (cfg.stale_tau0 + age)
    if cfg.drift_aware_agg and update["drift"]:
        w *= cfg.drift_boost         # a freshly-drifted client carries new info
    return w


def _clip_delta(delta, max_norm):
    norm = float(torch.sqrt(sum(v.pow(2).sum() for v in delta.values())))
    if norm > max_norm and norm > 0:
        scale = max_norm / norm
        return {k: v * scale for k, v in delta.items()}, scale
    return delta, 1.0


def aggregate(global_body, updates, cfg):
    """Return (new_global_body, clip_stats). Body tensors live on CPU.

    clip_stats is diagnostics only: {"n_clipped", "mean_clip_scale"} where
    mean_clip_scale averages the applied scale over clipped updates (None if
    no update was clipped this round).
    """
    stats = {"n_clipped": 0, "mean_clip_scale": None}
    if not updates:
        return global_body, stats  # nobody uploaded this round

    # decompress each payload back to a full delta
    deltas = [Compressor.decompress(u["payload"], global_body) for u in updates]

    # _weight collapses to plain data-size weighting when staleness/drift flags
    # are off, so FedAvg/FedProx fall out of the same code path.
    weights = [_weight(u, cfg) for u in updates]
    if cfg.drift_aware_agg and cfg.clip_factor:
        # adaptive divergence clip: bound each delta by a multiple of the
        # median delta norm of the CURRENT round's uploads
        norms = [
            float(torch.sqrt(sum(v.pow(2).sum() for v in d.values()))) for d in deltas
        ]
        max_norm = cfg.clip_factor * float(np.median(norms))
        clipped, scales = [], []
        for d in deltas:
            d2, scale = _clip_delta(d, max_norm)
            clipped.append(d2)
            if scale < 1.0:
                scales.append(scale)
        deltas = clipped
        stats["n_clipped"] = len(scales)
        stats["mean_clip_scale"] = float(sum(scales) / len(scales)) if scales else None

    wsum = sum(weights) + 1e-12
    new_body = {}
    for name in global_body:
        acc = torch.zeros_like(global_body[name].cpu())
        for d, w in zip(deltas, weights):
            acc += (w / wsum) * d[name].to(acc.dtype)
        new_body[name] = global_body[name].cpu() + acc
    return new_body, stats
