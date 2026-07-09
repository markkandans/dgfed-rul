"""A simulated federated client.

Holds its own data, a full RULNet, a persistent drift detector, and a
persistent compressor (for error feedback). Which parameters are *shared* with
the server depends on cfg.personalize_head:
  True  -> only the body is federated; the RUL head stays local (DGFed).
  False -> the full model is federated (faithful FedAvg / FedProx baselines).

Each round the client:
  1. loads the current global shared parameters,
  2. trains locally (optionally with a FedProx proximal term),
  3. measures residuals on its held-out ordered tail -> updates drift detector,
  4. if event-triggered, decides whether to upload at all,
  5. compresses the delta and returns it with metadata (drift flag, bytes, age).
"""
import numpy as np
import torch
from torch.utils.data import TensorDataset, DataLoader

from models.model import RULNet
from .drift import PageHinkley
from .compression import Compressor


class Client:
    def __init__(self, cid, data, cfg, n_features, device):
        self.id = cid
        self.cfg = cfg
        self.device = device
        self.head_local = cfg.personalize_head
        self.net = RULNet(cfg, n_features).to(device)
        self.detector = PageHinkley(cfg.ph_delta, cfg.ph_lambda, cfg.ph_alpha)
        self.compressor = Compressor(cfg)
        self.last_sync_round = 0          # for staleness
        self.drifting = False
        self.past_delta_norms = []        # history for the relative event trigger
        # diagnostics only (read by the server after each local_update)
        self.last_stats = None

        Xtr = torch.tensor(data["X_train"], dtype=torch.float32)
        ytr = torch.tensor(data["y_train"], dtype=torch.float32)
        self.train_ds = TensorDataset(Xtr, ytr)
        self.Xte = torch.tensor(data["X_test"], dtype=torch.float32)
        self.yte = torch.tensor(data["y_test"], dtype=torch.float32)
        self.n = len(ytr)

    def _shared_module(self):
        return self.net.body if self.head_local else self.net

    # ---- drift signal from residuals on the (ordered) tail -----------------
    def _check_drift(self):
        if not self.cfg.use_drift_detector or len(self.yte) == 0:
            return False
        self.net.eval()
        with torch.no_grad():
            pred = self.net(self.Xte.to(self.device)).cpu().numpy()
        resid = np.abs(pred - self.yte.numpy())
        return self.detector.update_stream(resid)

    # ---- one round of local work -------------------------------------------
    def local_update(self, global_shared, round_idx):
        # load shared params; the personalized head (if any) persists locally
        self.net.load_shared_state(global_shared, head_local=self.head_local)
        global_ref = {k: v.clone().to(self.device) for k, v in global_shared.items()}

        opt = torch.optim.Adam(self.net.parameters(), lr=self.cfg.lr)
        loader = DataLoader(self.train_ds, batch_size=self.cfg.batch_size, shuffle=True)
        self.net.train()
        for _ in range(self.cfg.local_epochs):
            for xb, yb in loader:
                xb, yb = xb.to(self.device), yb.to(self.device)
                opt.zero_grad()
                loss = torch.nn.functional.mse_loss(self.net(xb), yb)
                if self.cfg.method == "fedprox" and self.cfg.fedprox_mu > 0:
                    # NB: iterate named_parameters (NOT state_dict) so the
                    # proximal term participates in autograd.
                    prox = 0.0
                    for name, p in self._shared_module().named_parameters():
                        prox = prox + (p - global_ref[name]).pow(2).sum()
                    loss = loss + 0.5 * self.cfg.fedprox_mu * prox
                loss.backward()
                opt.step()

        # drift signal (after training)
        self.drifting = self._check_drift()

        # shared-parameter delta
        after = self.net.shared_state(head_local=self.head_local)
        delta = {k: (after[k] - global_shared[k]) for k in after}
        delta_norm = float(torch.sqrt(sum(v.pow(2).sum() for v in delta.values())))

        self.last_stats = {
            "delta_norm": delta_norm,
            "drift": bool(self.drifting),
            "skipped": False,
        }

        # event-triggered communication: quiescent + non-drifting -> skip upload.
        # Relative rule: skip iff delta norm falls below trigger_alpha times the
        # running median of this client's own past delta norms. An empty history
        # (first update) always sends.
        hist_median = (
            float(np.median(self.past_delta_norms)) if self.past_delta_norms else None
        )
        self.past_delta_norms.append(delta_norm)
        if (
            self.cfg.event_trigger
            and not self.drifting
            and hist_median is not None
            and delta_norm < self.cfg.trigger_alpha * hist_median
        ):
            self.last_stats["skipped"] = True
            return None

        age = round_idx - self.last_sync_round
        self.last_sync_round = round_idx
        payload, nbytes = self.compressor.compress(
            {k: v.clone() for k, v in delta.items()}
        )
        return {
            "id": self.id,
            "payload": payload,
            "n": self.n,
            "drift": self.drifting,
            "age": age,
            "delta_norm": delta_norm,
            "bytes": nbytes,
        }

    # ---- local evaluation (uses personalized head when head_local) ----------
    @torch.no_grad()
    def evaluate(self, global_shared=None):
        if global_shared is not None:
            self.net.load_shared_state(global_shared, head_local=self.head_local)
        self.net.eval()
        if len(self.yte) == 0:
            z = np.zeros(0, dtype=np.float32)
            return z, z
        pred = self.net(self.Xte.to(self.device)).cpu().numpy()
        return pred, self.yte.numpy()
