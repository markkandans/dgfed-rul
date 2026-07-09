"""Churn diagnostic for the personal-head arm (evaluation-only).

At the end of training, evaluate every client two ways:
  (a) final GLOBAL body + the client's personal head   [standard eval]
  (b) the client's OWN final local body + personal head [post its last update]

If (b) is clearly better, the personal head is mismatched with the moving
global body (head-body churn), confirming the mechanism behind the
personal-head underperformance.

Training is identical to main.run_experiment for method=dgfed except that the
periodic in-training evaluation is disabled: that evaluation loads the global
body into every client net (behavior-neutral for training, since local_update
always reloads the global body first), which would destroy the "own final
local body" state that (b) needs.
"""
import argparse
import json
import os

import numpy as np
import torch

from config import Config
from data.cmapss import load_cmapss
from data.partition import make_clients
from federated.client import Client
from federated.server import Server
from main import set_seed, pick_device
from metrics import rmse


def _stratified(clients, shared):
    """Pooled RMSE + seen/unseen RMSE; shared=None -> each client's own body."""
    p_all, t_all = [], []
    p_seen, t_seen, p_uns, t_uns = [], [], [], []
    for c in clients:
        pred, true = c.evaluate(shared)
        if len(true) == 0:
            continue
        train_vals = np.unique(c.train_ds.tensors[1].numpy())
        mask = np.isin(true, train_vals)
        p_all.append(pred)
        t_all.append(true)
        if mask.any():
            p_seen.append(pred[mask])
            t_seen.append(true[mask])
        if (~mask).any():
            p_uns.append(pred[~mask])
            t_uns.append(true[~mask])
    return {
        "rmse": rmse(np.concatenate(p_all), np.concatenate(t_all)),
        "seen_rmse": rmse(np.concatenate(p_seen), np.concatenate(t_seen)) if p_seen else None,
        "unseen_rmse": rmse(np.concatenate(p_uns), np.concatenate(t_uns)) if p_uns else None,
    }


def run_one(cfg):
    set_seed(cfg.seed)
    device = pick_device(cfg.device)
    bundle = load_cmapss(cfg)
    raw_clients = make_clients(bundle, cfg)
    print(f"[data] subset={cfg.subset} clients={len(raw_clients)} device={device}")
    clients = [
        Client(c["id"], c, cfg, bundle["n_features"], device) for c in raw_clients
    ]
    server = Server(clients, cfg, bundle["n_features"], device)
    final_shared = server.train(evaluator=None)  # no in-training eval (see docstring)

    # (b) FIRST: own final local body + personal head (evaluate(None) leaves
    # each net exactly as its last local_update left it)
    own = _stratified(clients, None)
    # (a) global body + personal head (loads final_shared into every net)
    glob = _stratified(clients, final_shared)
    return {"seed": cfg.seed, "global_body": glob, "own_body": own}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--subset", default="FD004")
    p.add_argument("--partition", required=True, choices=["condition", "unit", "regime"])
    p.add_argument("--rounds", type=int, default=200)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--seeds", type=int, default=3)
    args = p.parse_args()

    runs = []
    for s in range(args.seeds):
        cfg = Config(
            method="dgfed",   # personal-head arm: personalize_head stays True
            subset=args.subset,
            rounds=args.rounds,
            seed=args.seed + s,
            run_tag="churn",
        )
        cfg.partition = args.partition
        res = run_one(cfg)
        runs.append(res)
        print(
            f"[seed {res['seed']}] global: RMSE={res['global_body']['rmse']:.3f} "
            f"seen={res['global_body']['seen_rmse']:.3f} | "
            f"own: RMSE={res['own_body']['rmse']:.3f} "
            f"seen={res['own_body']['seen_rmse']:.3f}"
        )

    out_dir = os.path.join(cfg.results_dir, "FD004_churn")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"churn_{args.partition}.json")
    with open(path, "w") as f:
        json.dump({"config": cfg.to_dict(), "runs": runs}, f, indent=2)
    print(f"[saved] {path}")


if __name__ == "__main__":
    main()
