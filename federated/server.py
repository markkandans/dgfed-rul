"""Federated server: orchestrates rounds and tracks communication cost.

Simulation notes:
  * Partial participation: a fraction of clients is sampled each round.
  * Stragglers: some sampled clients "drop" (their update is discarded this
    round). Because the staleness weight uses each client's last-synced round,
    a client that skips/drops and returns later is naturally down-weighted —
    this is our lightweight stand-in for semi-synchronous FL. A true async
    buffer would replace `run_round` without touching the aggregation rule.
"""
import numpy as np
import torch

from models.model import RULNet
from .aggregation import aggregate


class Server:
    def __init__(self, clients, cfg, n_features, device):
        self.clients = clients
        self.cfg = cfg
        self.device = device
        # global body initialized from a fresh net
        ref = RULNet(cfg, n_features).to(device)
        self.global_body = ref.shared_state(head_local=cfg.personalize_head)
        self.total_bytes = 0
        self.round_bytes = []
        self.diag_rows = []   # one diagnostics dict per round (logging only)
        self.rng = np.random.default_rng(cfg.seed)

    def _sample(self):
        m = max(1, int(self.cfg.clients_per_round * len(self.clients)))
        idx = self.rng.choice(len(self.clients), size=m, replace=False)
        return [self.clients[i] for i in idx]

    def run_round(self, round_idx):
        sampled = self._sample()
        updates, round_bytes = [], 0
        n_straggle = n_skip = n_drift = 0
        delta_norms = []
        for c in sampled:
            # straggler drop
            if self.rng.random() < self.cfg.straggler_rate:
                n_straggle += 1
                continue
            up = c.local_update(self.global_body, round_idx)
            st = c.last_stats
            if st is not None:
                delta_norms.append(st["delta_norm"])
                n_drift += int(st["drift"])
                n_skip += int(st["skipped"])
            if up is None:            # event-trigger skip
                continue
            updates.append(up)
            round_bytes += up["bytes"]

        self.global_body, clip_stats = aggregate(self.global_body, updates, self.cfg)
        self.total_bytes += round_bytes
        self.round_bytes.append(round_bytes)
        self.diag_rows.append(
            {
                "round": round_idx,
                "n_sampled": len(sampled),
                "n_straggle": n_straggle,
                "n_trained": len(sampled) - n_straggle,
                "n_skip": n_skip,
                "n_drift": n_drift,
                "uploads": len(updates),
                "bytes": round_bytes,
                "median_delta_norm": float(np.median(delta_norms)) if delta_norms else None,
                "p90_delta_norm": float(np.percentile(delta_norms, 90)) if delta_norms else None,
                "n_clipped": clip_stats["n_clipped"],
                "mean_clip_scale": clip_stats["mean_clip_scale"],
            }
        )
        return len(updates), round_bytes

    def train(self, evaluator=None, log_every=20):
        for r in range(1, self.cfg.rounds + 1):
            n_up, rb = self.run_round(r)
            if evaluator and (r % log_every == 0 or r == self.cfg.rounds):
                m = evaluator(self.global_body)
                print(
                    f"[round {r:4d}] uploads={n_up:2d} bytes/round={rb:8d} "
                    f"RMSE={m['rmse']:.3f} score={m['score']:.1f} "
                    f"var={m['per_client_var']:.2f} total_MB={self.total_bytes/1e6:.2f}"
                )
        return self.global_body
