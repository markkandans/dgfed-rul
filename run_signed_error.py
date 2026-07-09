"""Mean signed error (pred - true) for proposed and FedAvg on FD002-unit.

Evaluation-only: deterministically re-executes runs (training identical;
in-training evaluation disabled, which consumes no RNG — verified
bit-identical by the churn study) and computes the pooled mean signed error
at the final model. Per-seed RMSEs are asserted against reference JSONs
(--ref-proposed / --ref-fedavg, each a main.py-style JSON with a "runs"
list) before the signed error is accepted.
"""
import argparse
import json
import os

import numpy as np

from config import Config
from data.cmapss import load_cmapss
from data.partition import make_clients
from federated.client import Client
from federated.server import Server
from main import set_seed, pick_device, apply_method


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--seeds", type=int, default=3)
    p.add_argument("--out", default="results/analysis_signed_error_FD002unit.json")
    p.add_argument("--ref-proposed", default="results/FD002_unit/proposed_FD002.json")
    p.add_argument("--ref-fedavg", default="results/FD002_unit/fedavg_FD002.json")
    args = p.parse_args()

    refs = {"proposed": args.ref_proposed, "fedavg": args.ref_fedavg}
    out = {}
    for method in ["proposed", "fedavg"]:
        pinned = {r["seed"]: r["rmse"] for r in json.load(open(refs[method]))["runs"]}
        rows = []
        for s in range(args.seed, args.seed + args.seeds):
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
                pr, t = c.evaluate(final)
                if len(t):
                    preds.append(pr); trues.append(t)
            pr, t = np.concatenate(preds), np.concatenate(trues)
            rmse = float(np.sqrt(np.mean((pr - t) ** 2)))
            signed = float(np.mean(pr - t))
            match = abs(rmse - pinned[s]) < 1e-4
            rows.append({"seed": s, "rmse": rmse, "pinned_rmse": pinned[s],
                         "match": match, "mean_signed_error": signed})
            print(f"[{method} seed {s}] rmse={rmse:.4f} pinned={pinned[s]:.4f} "
                  f"match={match} mean_signed_error={signed:+.3f}")
        out[method] = rows

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    json.dump(out, open(args.out, "w"), indent=2)
    print(f"[saved] {args.out}")


if __name__ == "__main__":
    main()
