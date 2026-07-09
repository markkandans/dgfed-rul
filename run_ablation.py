"""One-toggle-at-a-time ablation of DGFed components.

Maps directly to the ablation table in the paper: every reviewer question of
the form "is the gain from X?" corresponds to one row here.
"""
import argparse
import json
import os

import numpy as np

from config import Config
from main import run_experiment

VARIANTS = {
    "full": {},
    "no_personal_head": {"personalize_head": False},
    "no_drift_signal": {"use_drift_detector": False},
    "no_event_trigger": {"event_trigger": False},
    "no_compression": {"compress": False},
    "plain_aggregation": {"staleness_aware": False, "drift_aware_agg": False},
    # rebased ablation: base config "proposed" = full minus the personalized
    # head (federated head), each row switching one component off from there
    "proposed_no_drift_signal": {"personalize_head": False, "use_drift_detector": False},
    "proposed_no_event_trigger": {"personalize_head": False, "event_trigger": False},
    "proposed_plain_aggregation": {
        "personalize_head": False,
        "staleness_aware": False,
        "drift_aware_agg": False,
    },
    "proposed_no_compression": {"personalize_head": False, "compress": False},
}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--subset", default="FD004")
    p.add_argument("--rounds", type=int, default=200)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--seeds", type=int, default=1, help="run N seeds, report mean±std")
    p.add_argument(
        "--variants",
        default=None,
        help="comma-separated subset of variants to run (default: all)",
    )
    p.add_argument(
        "--partition",
        default=None,
        choices=["condition", "unit", "regime"],
        help="override Config.partition (client formation strategy)",
    )
    args = p.parse_args()

    variants = VARIANTS
    if args.variants:
        wanted = args.variants.split(",")
        unknown = [w for w in wanted if w not in VARIANTS]
        if unknown:
            raise SystemExit(f"unknown variants: {unknown}; choose from {list(VARIANTS)}")
        variants = {k: VARIANTS[k] for k in wanted}

    table, cfg = {}, None
    for name, overrides in variants.items():
        print(f"\n=== ablation: {name} ===")
        runs = []
        for s in range(args.seeds):
            cfg = Config(
                method="dgfed",
                subset=args.subset,
                rounds=args.rounds,
                seed=args.seed + s,
                run_tag=name,
            )
            if args.partition is not None:
                cfg.partition = args.partition
            for k, v in overrides.items():
                setattr(cfg, k, v)
            res = run_experiment(cfg)
            res["seed"] = cfg.seed
            runs.append(res)

        def _ms(key):
            vals = [r[key] for r in runs]
            return float(np.mean(vals)), float(np.std(vals))

        rmse_m, rmse_s = _ms("rmse")
        score_m, score_s = _ms("score")
        table[name] = {
            "rmse_mean": rmse_m,
            "rmse_std": rmse_s,
            "score_mean": score_m,
            "score_std": score_s,
            "per_client_var_mean": _ms("per_client_var")[0],
            "worst_client_rmse_mean": _ms("worst_client_rmse")[0],
            "total_MB_uploaded_mean": _ms("total_MB_uploaded")[0],
            "n_clients": runs[0].get("n_clients"),
            "retention_rmse_bins": [r.get("retention_rmse_bins") for r in runs],
            "diagnostics": [r.get("diagnostics") for r in runs],
            "seen_unseen": [
                {
                    k: r["seen_unseen"][k]
                    for k in ("seen_rmse", "unseen_rmse", "n_seen", "n_unseen")
                }
                if r.get("seen_unseen")
                else None
                for r in runs
            ],
            "rmse_per_seed": [r["rmse"] for r in runs],
            "seeds": [r["seed"] for r in runs],
        }
        print(
            f"{name}: RMSE={rmse_m:.3f}±{rmse_s:.3f} score={score_m:.1f}±{score_s:.1f} "
            f"MB={table[name]['total_MB_uploaded_mean']:.2f}"
        )

    os.makedirs(cfg.results_dir, exist_ok=True)
    path = os.path.join(cfg.results_dir, f"ablation_{args.subset}.json")
    with open(path, "w") as f:
        json.dump(table, f, indent=2)
    print(f"\n[saved] {path}")


if __name__ == "__main__":
    main()
