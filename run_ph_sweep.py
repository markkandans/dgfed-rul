"""Page-Hinkley lambda calibration sweep.

Short dgfed runs per candidate lambda, reporting the drift-detector fire rate
(fraction of trained client-rounds that flag drift). Used to pick the paper's
ph_lambda so the drift signal is selective rather than near-constant.
"""
import argparse
import json
import os

from config import Config
from main import run_experiment


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--subset", default="FD004")
    p.add_argument("--partition", default="unit")
    p.add_argument("--rounds", type=int, default=50)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument(
        "--lambdas", default="250,500,1000,2500,5000",
        help="comma-separated ph_lambda candidates",
    )
    args = p.parse_args()

    table = {}
    for lam in [float(x) for x in args.lambdas.split(",")]:
        cfg = Config(
            method="dgfed",
            subset=args.subset,
            rounds=args.rounds,
            seed=args.seed,
            run_tag=f"lam{lam:g}",
        )
        cfg.partition = args.partition
        cfg.ph_lambda = lam
        res = run_experiment(cfg)
        d = res["diagnostics"]
        table[f"{lam:g}"] = {
            "drift_fire_rate": d["drift_fire_rate"],
            "skip_rate": d["skip_rate"],
            "rmse": res["rmse"],
        }
        print(
            f"[lambda={lam:g}] fire_rate={d['drift_fire_rate']:.4f} "
            f"skip_rate={d['skip_rate']:.4f} rmse={res['rmse']:.3f}"
        )

    os.makedirs(cfg.results_dir, exist_ok=True)
    path = os.path.join(cfg.results_dir, f"ph_sweep_{args.subset}_{args.partition}.json")
    with open(path, "w") as f:
        json.dump(table, f, indent=2)
    print(f"[saved] {path}")


if __name__ == "__main__":
    main()
