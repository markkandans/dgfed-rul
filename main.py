"""Entry point.

Examples:
    python main.py --method dgfed   --subset FD004 --rounds 200
    python main.py --method fedavg  --subset FD004 --rounds 200 --seeds 3
    python main.py --method fedprox --subset FD002 --rounds 200
    python main.py --method local   --subset FD004
    python main.py --method central --subset FD004

Writes results to ./results/<method>_<subset>.json
"""
import argparse
import json
import os
import random

import numpy as np
import torch

from config import Config
from data.cmapss import load_cmapss
from data.partition import make_clients
from federated.client import Client
from federated.server import Server
from metrics import evaluate_clients, retention_curve, seen_unseen_rmse
from baselines import run_central, run_local


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def apply_method(cfg: Config) -> Config:
    """Turn DGFed components off for the standard-FL baselines so each method
    is faithful: FedAvg/FedProx share the FULL model, communicate every round,
    uncompressed, with plain data-size aggregation."""
    if cfg.method in ("fedavg", "fedprox"):
        cfg.personalize_head = False
        cfg.use_drift_detector = False
        cfg.event_trigger = False
        cfg.compress = False
        cfg.staleness_aware = False
        cfg.drift_aware_agg = False
    if cfg.method == "fedavg":
        cfg.fedprox_mu = 0.0
    return cfg


def pick_device(pref: str) -> torch.device:
    """cpu = strict; cuda/auto = best available (cuda > mps > cpu); mps = mps > cpu."""
    if pref == "cpu":
        return torch.device("cpu")
    if pref in ("cuda", "auto") and torch.cuda.is_available():
        return torch.device("cuda")
    if pref in ("cuda", "mps", "auto") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def _diag_summary(rows):
    """Aggregate the server's per-round diagnostics into scalar rates."""
    if not rows:
        return None
    tot_trained = sum(r["n_trained"] for r in rows)
    tot_skip = sum(r["n_skip"] for r in rows)
    tot_drift = sum(r["n_drift"] for r in rows)
    tot_uploads = sum(r["uploads"] for r in rows)
    tot_clipped = sum(r["n_clipped"] for r in rows)
    clip_scales = [r["mean_clip_scale"] for r in rows if r["mean_clip_scale"] is not None]
    med = [r["median_delta_norm"] for r in rows if r["median_delta_norm"] is not None]
    p90 = [r["p90_delta_norm"] for r in rows if r["p90_delta_norm"] is not None]
    mean_upload_bytes = (
        sum(r["bytes"] for r in rows) / tot_uploads if tot_uploads else 0.0
    )
    return {
        "rounds": len(rows),
        "total_trained": tot_trained,
        "drift_fire_rate": tot_drift / tot_trained if tot_trained else 0.0,
        "skip_rate": tot_skip / tot_trained if tot_trained else 0.0,
        "clip_rate": tot_clipped / tot_uploads if tot_uploads else 0.0,
        "mean_clip_scale": float(np.mean(clip_scales)) if clip_scales else None,
        "median_delta_norm": float(np.median(med)) if med else None,
        "p90_delta_norm": float(np.median(p90)) if p90 else None,
        "mean_upload_bytes": mean_upload_bytes,
        "trigger_skipped_uploads": tot_skip,
        "trigger_bytes_saved_MB": tot_skip * mean_upload_bytes / 1e6,
    }


def _write_diag_csv(rows, cfg):
    diag_dir = os.path.join(cfg.results_dir, "diag")
    os.makedirs(diag_dir, exist_ok=True)
    tag = f"_{cfg.run_tag}" if cfg.run_tag else ""
    path = os.path.join(
        diag_dir, f"{cfg.method}_{cfg.subset}_{cfg.partition}{tag}_seed{cfg.seed}.csv"
    )
    cols = [
        "round", "n_sampled", "n_straggle", "n_trained", "n_skip", "n_drift",
        "uploads", "bytes", "median_delta_norm", "p90_delta_norm",
        "n_clipped", "mean_clip_scale",
    ]
    with open(path, "w") as f:
        f.write(",".join(cols) + "\n")
        for r in rows:
            f.write(",".join("" if r[c] is None else str(r[c]) for c in cols) + "\n")
    return path


def run_experiment(cfg: Config) -> dict:
    set_seed(cfg.seed)
    device = pick_device(cfg.device)

    bundle = load_cmapss(cfg)
    raw_clients = make_clients(bundle, cfg)
    print(
        f"[data] subset={cfg.subset} clients={len(raw_clients)} "
        f"features={bundle['n_features']} device={device}"
    )
    if cfg.method not in ("local", "central") and len(raw_clients) < 2:
        raise RuntimeError(
            f"Federated method '{cfg.method}' needs at least 2 clients, but "
            f"partition='{cfg.partition}' produced {len(raw_clients)} client(s) "
            f"on {cfg.subset}. Use a different --partition (unit | regime)."
        )

    if cfg.method == "central":
        res = run_central(raw_clients, bundle, cfg, device)
        res["n_clients"] = len(raw_clients)
        return res
    if cfg.method == "local":
        res = run_local(raw_clients, bundle, cfg, device)
        res["n_clients"] = len(raw_clients)
        return res

    clients = [
        Client(c["id"], c, cfg, bundle["n_features"], device) for c in raw_clients
    ]
    server = Server(clients, cfg, bundle["n_features"], device)

    def evaluator(shared):
        return evaluate_clients(clients, shared)

    final_shared = server.train(
        evaluator=evaluator, log_every=max(1, cfg.rounds // 10)
    )

    res = evaluate_clients(clients, final_shared)
    res["retention_rmse_bins"] = retention_curve(clients, final_shared)
    res["seen_unseen"] = seen_unseen_rmse(clients, final_shared)
    res["total_MB_uploaded"] = server.total_bytes / 1e6
    res["mean_bytes_per_round"] = (
        float(np.mean(server.round_bytes)) if server.round_bytes else 0.0
    )
    res["method"] = cfg.method
    res["n_clients"] = len(raw_clients)
    res["diagnostics"] = _diag_summary(server.diag_rows)
    res["diagnostics_csv"] = _write_diag_csv(server.diag_rows, cfg)
    return res


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--method",
        default="dgfed",
        choices=["dgfed", "fedavg", "fedprox", "local", "central"],
    )
    p.add_argument("--subset", default="FD004")
    p.add_argument("--rounds", type=int, default=200)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--seeds", type=int, default=1, help="run N seeds, report mean±std")
    p.add_argument("--data-root", default="./datasets/CMAPSS")
    p.add_argument(
        "--device",
        default=None,
        choices=["auto", "cpu", "cuda", "mps"],
        help="override Config.device",
    )
    p.add_argument(
        "--partition",
        default=None,
        choices=["condition", "unit", "regime"],
        help="override Config.partition (client formation strategy)",
    )
    p.add_argument("--straggler-rate", type=float, default=None)
    p.add_argument("--clients-per-round", type=float, default=None)
    p.add_argument("--no-drift-injection", action="store_true")
    p.add_argument(
        "--no-personal-head",
        action="store_true",
        help="federate the full model incl. head (the 'proposed' configuration)",
    )
    args = p.parse_args()

    runs, cfg = [], None
    for s in range(args.seeds):
        cfg = Config(
            method=args.method,
            subset=args.subset,
            rounds=args.rounds,
            seed=args.seed + s,
            data_root=args.data_root,
        )
        if args.device is not None:
            cfg.device = args.device
        if args.partition is not None:
            cfg.partition = args.partition
        if args.straggler_rate is not None:
            cfg.straggler_rate = args.straggler_rate
        if args.clients_per_round is not None:
            cfg.clients_per_round = args.clients_per_round
        if args.no_drift_injection:
            cfg.inject_drift = False
        if args.no_personal_head:
            cfg.personalize_head = False
        apply_method(cfg)

        res = run_experiment(cfg)
        res["seed"] = cfg.seed
        runs.append(res)
        print(f"[seed {cfg.seed}] RMSE={res['rmse']:.3f} score={res['score']:.1f}")

    out = {"config": cfg.to_dict(), "runs": runs}
    if args.seeds > 1:
        rm = [r["rmse"] for r in runs]
        sc = [r["score"] for r in runs]
        out["summary"] = {
            "rmse_mean": float(np.mean(rm)),
            "rmse_std": float(np.std(rm)),
            "score_mean": float(np.mean(sc)),
            "score_std": float(np.std(sc)),
        }
        print(
            f"[summary over {args.seeds} seeds] "
            f"RMSE {np.mean(rm):.3f} ± {np.std(rm):.3f} | "
            f"score {np.mean(sc):.1f} ± {np.std(sc):.1f}"
        )

    os.makedirs(cfg.results_dir, exist_ok=True)
    path = os.path.join(cfg.results_dir, f"{args.method}_{args.subset}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[saved] {path}")


if __name__ == "__main__":
    main()
