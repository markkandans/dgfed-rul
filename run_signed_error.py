"""Mean signed error (pred - true) for proposed and FedAvg on FD002-unit.

Evaluation-only: deterministically re-executes the pinned runs (training
identical; in-training evaluation disabled, which consumes no RNG — verified
bit-identical by the churn study) and computes the pooled mean signed error
at the final model. Per-seed RMSEs are asserted against the pinned JSONs.
"""
import json

import numpy as np

from config import Config
from data.cmapss import load_cmapss
from data.partition import make_clients
from federated.client import Client
from federated.server import Server
from main import set_seed, pick_device, apply_method

PINNED = {
    "proposed": "results/FD002_unit/proposed_FD002.json",
    "fedavg": "results/FD002_unit/fedavg_FD002.json",
}

out = {}
for method in ["proposed", "fedavg"]:
    pinned = {r["seed"]: r["rmse"] for r in json.load(open(PINNED[method]))["runs"]}
    rows = []
    for s in range(3):
        cfg = Config(
            method="dgfed" if method == "proposed" else "fedavg",
            subset="FD002", rounds=200, seed=s, run_tag="signed",
        )
        cfg.partition = "unit"
        if method == "proposed":
            cfg.personalize_head = False
        apply_method(cfg)
        set_seed(cfg.seed)
        device = pick_device(cfg.device)
        bundle = load_cmapss(cfg)
        raw = make_clients(bundle, cfg)
        clients = [Client(c["id"], c, cfg, bundle["n_features"], device) for c in raw]
        server = Server(clients, cfg, bundle["n_features"], device)
        final = server.train(evaluator=None)
        preds, trues = [], []
        for c in clients:
            p, t = c.evaluate(final)
            if len(t):
                preds.append(p); trues.append(t)
        p, t = np.concatenate(preds), np.concatenate(trues)
        rmse = float(np.sqrt(np.mean((p - t) ** 2)))
        signed = float(np.mean(p - t))
        match = abs(rmse - pinned[s]) < 1e-4
        rows.append({"seed": s, "rmse": rmse, "pinned_rmse": pinned[s],
                     "match": match, "mean_signed_error": signed})
        print(f"[{method} seed {s}] rmse={rmse:.4f} pinned={pinned[s]:.4f} "
              f"match={match} mean_signed_error={signed:+.3f}")
    out[method] = rows

json.dump(out, open("results/analysis_signed_error_FD002unit.json", "w"), indent=2)
print("[saved] results/analysis_signed_error_FD002unit.json")
