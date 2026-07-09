"""One-factor-at-a-time sensitivity probes: trigger_alpha and drift_boost.

Proposed config (no personal head), FD004-unit, 100 rounds, seed 0.
The base point (alpha=0.3, rho=1.5) is run once and shared.
"""
import json

from config import Config
from main import run_experiment

PROBES = [("trigger_alpha", 0.1), ("trigger_alpha", 0.3), ("trigger_alpha", 0.5),
          ("drift_boost", 1.0), ("drift_boost", 1.5), ("drift_boost", 2.0)]

if __name__ == "__main__":
    table, base_row = {}, None
    for param, val in PROBES:
        is_base = (param, val) in (("trigger_alpha", 0.3), ("drift_boost", 1.5))
        if is_base and base_row is not None:
            table[f"{param}={val:g}"] = dict(base_row, note="base (shared run)")
            continue
        cfg = Config(method="dgfed", subset="FD004", rounds=100, seed=0,
                     run_tag=f"sens_{param}{val:g}")
        cfg.partition = "unit"
        cfg.personalize_head = False
        setattr(cfg, param, val)
        res = run_experiment(cfg)
        d = res["diagnostics"]
        row = {"rmse": res["rmse"], "skip_rate": d["skip_rate"],
               "drift_fire_rate": d["drift_fire_rate"]}
        if is_base:
            base_row = row
            row = dict(row, note="base")
        table[f"{param}={val:g}"] = row
        print(f"[{param}={val:g}] rmse={res['rmse']:.3f} "
              f"skip={d['skip_rate']:.4f} fire={d['drift_fire_rate']:.4f}")
    json.dump(table, open("results/s34/sensitivity_FD004unit.json", "w"), indent=2)
    print("[saved] results/s34/sensitivity_FD004unit.json")
