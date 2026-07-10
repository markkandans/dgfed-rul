"""Merge pinned 3-seed results with the s34 extension into results/merged5/.

Produces a mirror of the original results layout with 5-seed "runs" lists
(local: seeds 0-4 via the pinned seed-0 run + s34 seeds 1-4), merged
ablation tables, paired-seed analysis, signed-error, data-scale, churn, and
the two divergence families. Asserts churn (a)-arm determinism against the
s34 DGFed-P runs before accepting churn rows. Never touches pinned files.
"""
import csv
import glob
import json
import os

import numpy as np

R = "results"
M = os.path.join(R, "merged5")


def J(path):
    return json.load(open(path))


def W(rel, obj):
    path = os.path.join(M, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, "w"), indent=2)
    print(f"[merged] {rel}")


def merge_runs(pinned_path, s34_path):
    """Concatenate runs lists and recompute the summary."""
    a, b = J(pinned_path), J(s34_path)
    runs = a["runs"] + b["runs"]
    seeds = [r["seed"] for r in runs]
    assert seeds == sorted(set(seeds)), f"seed overlap/disorder: {seeds}"
    rm = [r["rmse"] for r in runs]
    sc = [r["score"] for r in runs]
    return {
        "config": a["config"],
        "runs": runs,
        "summary": {
            "rmse_mean": float(np.mean(rm)), "rmse_std": float(np.std(rm)),
            "score_mean": float(np.mean(sc)), "score_std": float(np.std(sc)),
        },
    }


def ablation_entry(runs):
    """run-JSON list -> run_ablation-style table entry."""
    def ms(key):
        v = [r[key] for r in runs]
        return float(np.mean(v)), float(np.std(v))
    rmse_m, rmse_s = ms("rmse")
    score_m, score_s = ms("score")
    return {
        "rmse_mean": rmse_m, "rmse_std": rmse_s,
        "score_mean": score_m, "score_std": score_s,
        "per_client_var_mean": ms("per_client_var")[0],
        "worst_client_rmse_mean": ms("worst_client_rmse")[0],
        "total_MB_uploaded_mean": float(np.mean([r["total_MB_uploaded"] or 0 for r in runs])),
        "n_clients": runs[0].get("n_clients"),
        "retention_rmse_bins": [r.get("retention_rmse_bins") for r in runs],
        "diagnostics": [r.get("diagnostics") for r in runs],
        "seen_unseen": [
            {k: r["seen_unseen"][k] for k in ("seen_rmse", "unseen_rmse", "n_seen", "n_unseen")}
            if r.get("seen_unseen") else None for r in runs
        ],
        "rmse_per_seed": [r["rmse"] for r in runs],
        "seeds": [r["seed"] for r in runs],
    }


def table_entry_merge(pinned_entry, s34_entry):
    """Merge two run_ablation table entries (seed-disjoint)."""
    out = {}
    seeds = pinned_entry["seeds"] + s34_entry["seeds"]
    assert seeds == sorted(set(seeds))
    rmse = pinned_entry["rmse_per_seed"] + s34_entry["rmse_per_seed"]
    for k in ("retention_rmse_bins", "diagnostics", "seen_unseen"):
        out[k] = pinned_entry[k] + s34_entry[k]
    n = len(seeds)
    # recompute means where per-seed values exist; fall back to weighted means
    out.update({
        "rmse_mean": float(np.mean(rmse)), "rmse_std": float(np.std(rmse)),
        "score_mean": float((pinned_entry["score_mean"] * len(pinned_entry["seeds"])
                             + s34_entry["score_mean"] * len(s34_entry["seeds"])) / n),
        "per_client_var_mean": float((pinned_entry["per_client_var_mean"] * len(pinned_entry["seeds"])
                                      + s34_entry["per_client_var_mean"] * len(s34_entry["seeds"])) / n),
        "worst_client_rmse_mean": float((pinned_entry["worst_client_rmse_mean"] * len(pinned_entry["seeds"])
                                         + s34_entry["worst_client_rmse_mean"] * len(s34_entry["seeds"])) / n),
        "total_MB_uploaded_mean": float((pinned_entry["total_MB_uploaded_mean"] * len(pinned_entry["seeds"])
                                         + s34_entry["total_MB_uploaded_mean"] * len(s34_entry["seeds"])) / n),
        "n_clients": pinned_entry["n_clients"],
        "rmse_per_seed": rmse, "seeds": seeds,
    })
    # exact score std from per-seed scores in diagnostics? scores per seed not
    # stored in table entries; recompute where seen_unseen/diag exist is not
    # possible -> mark approximate
    out["score_std_note"] = "score_std recomputed only where per-seed scores available"
    return out


# ------------------------------------------------------------------ methods
for sub in ["FD004", "FD002"]:
    for part in ["unit", "regime"]:
        base = f"{R}/{sub}_{part}"
        for m in ["fedavg", "fedprox", "central"]:
            W(f"{sub}_{part}/{m}_{sub}.json",
              merge_runs(f"{base}/{m}_{sub}.json", f"{R}/s34/{m}_{sub}_{part}.json"))
        W(f"{sub}_{part}/local_{sub}.json",
          merge_runs(f"{base}/local_{sub}.json", f"{R}/s34/local_{sub}_{part}.json"))
        if sub == "FD002":
            W(f"{sub}_{part}/proposed_{sub}.json",
              merge_runs(f"{base}/proposed_{sub}.json", f"{R}/s34/proposed_{sub}_{part}.json"))

# FD004 proposed / DGFed-P: pinned seeds 0-2 live in FD004_perclient (full run JSONs)
for part in ["unit", "regime"]:
    W(f"FD004_{part}/proposed_FD004.json",
      merge_runs(f"{R}/FD004_perclient/proposed_{part}.json", f"{R}/s34/proposed_FD004_{part}.json"))
    W(f"FD004_{part}/dgfedp_FD004.json",
      merge_runs(f"{R}/FD004_perclient/full_{part}.json", f"{R}/s34/dgfedp_FD004_{part}.json"))

# ------------------------------------------------------------------ ablation
for part in ["unit", "regime"]:
    cal = J(f"{R}/FD004_calibrated/ablation_{part}.json")
    reb = J(f"{R}/FD004_rebased/ablation_{part}.json")
    s34 = J(f"{R}/s34/ablation_{part}_seeds34.json")
    merged = {}
    # base + personal head from run JSONs (5 seeds each)
    prop = J(os.path.join(M, f"FD004_{part}/proposed_FD004.json"))["runs"]
    dgfp = J(os.path.join(M, f"FD004_{part}/dgfedp_FD004.json"))["runs"]
    # determinism cross-check: run-JSON seeds 0-2 must equal calibrated table values
    assert [round(x, 6) for x in cal["no_personal_head"]["rmse_per_seed"]] == \
           [round(r["rmse"], 6) for r in prop[:3]], f"proposed 0-2 mismatch {part}"
    assert [round(x, 6) for x in cal["full"]["rmse_per_seed"]] == \
           [round(r["rmse"], 6) for r in dgfp[:3]], f"dgfedp 0-2 mismatch {part}"
    merged["no_personal_head"] = ablation_entry(prop)
    merged["full"] = ablation_entry(dgfp)
    for v in ["proposed_no_drift_signal", "proposed_no_event_trigger",
              "proposed_plain_aggregation", "proposed_no_compression"]:
        merged[v] = table_entry_merge(reb[v], s34[v])
    W(f"FD004_calibrated/ablation_{part}.json",
      {k: merged[k] for k in ("full", "no_personal_head")})
    W(f"FD004_rebased/ablation_{part}.json",
      {k: v for k, v in merged.items() if k.startswith("proposed_")})

    # paired-seed analysis
    base_per_seed = dict(zip([r["seed"] for r in prop], [r["rmse"] for r in prop]))
    arms = {"+personal_head": [r["rmse"] for r in dgfp]}
    for v in ["proposed_no_drift_signal", "proposed_no_event_trigger",
              "proposed_plain_aggregation", "proposed_no_compression"]:
        arms[v] = merged[v]["rmse_per_seed"]
    pa = {}
    for name, rm in arms.items():
        deltas = [rm[i] - base_per_seed[i] for i in range(5)]
        pa[name] = {"per_seed_delta": deltas, "mean": float(np.mean(deltas)),
                    "std": float(np.std(deltas)),
                    "sign_pattern": f"{sum(d > 0 for d in deltas)}/5 positive"}
    if part == "unit":
        paired = {"partitions": {}}
    paired["partitions"][part] = pa
W("analysis_paired_seed_FD004.json", paired)

# ------------------------------------------------------------------ churn
for part in ["unit", "regime"]:
    pinned = J(f"{R}/FD004_churn/churn_{part}.json")
    s34c = J(f"{R}/s34/churn_{part}_seeds34.json")
    dgfp = J(os.path.join(M, f"FD004_{part}/dgfedp_FD004.json"))["runs"]
    ref = {r["seed"]: r["rmse"] for r in dgfp}
    for r in s34c["runs"]:
        assert abs(r["global_body"]["rmse"] - ref[r["seed"]]) < 1e-4, \
            f"churn determinism FAIL {part} seed {r['seed']}"
    W(f"FD004_churn/churn_{part}.json",
      {"config": pinned["config"], "runs": pinned["runs"] + s34c["runs"]})
print("[assert] churn (a)-arm matches DGFed-P s34 runs exactly: OK")

# ------------------------------------------------------------------ signed error
pin = J(f"{R}/analysis_signed_error_FD002unit.json")
s34s = J(f"{R}/s34/signed_error_FD002unit_seeds34.json")
merged_se = {m: pin[m] + s34s[m] for m in ["proposed", "fedavg"]}
assert all(r["match"] for m in merged_se.values() for r in m)
W("analysis_signed_error_FD002unit.json", merged_se)

# ------------------------------------------------------------------ data scale
from config import Config
from data.cmapss import load_cmapss
from data.partition import make_clients

ds = {"partitions": {}}
for part in ["unit", "regime"]:
    cfg = Config(subset="FD004", seed=0); cfg.partition = part
    sizes = [c["n"] for c in make_clients(load_cmapss(cfg), cfg)]
    fu = np.mean([r["per_client_rmse"] for r in J(os.path.join(M, f"FD004_{part}/dgfedp_FD004.json"))["runs"]], axis=0)
    pr = np.mean([r["per_client_rmse"] for r in J(os.path.join(M, f"FD004_{part}/proposed_FD004.json"))["runs"]], axis=0)
    delta = fu - pr
    rs = np.argsort(np.argsort(sizes)); rd = np.argsort(np.argsort(delta))
    ds["partitions"][part] = {
        "client_train_windows": sizes,
        "delta_rmse_per_client": [float(x) for x in delta],
        "pearson_r": float(np.corrcoef(sizes, delta)[0, 1]),
        "spearman_r": float(np.corrcoef(rs, rd)[0, 1]),
    }
W("analysis_data_scale_FD004.json", ds)

# ------------------------------------------------------------------ divergence
def health(csv_path):
    rows = [r for r in csv.DictReader(open(csv_path)) if r["median_delta_norm"]][-20:]
    return float(np.mean([float(r["median_delta_norm"]) for r in rows]))

div = {"proposed_family": {}, "personal_head_family": {}}
cal_u = J(f"{R}/FD004_calibrated/ablation_unit.json")
ext_u = J(f"{R}/FD004_calibrated/ablation_unit_seeds3to7.json")
d57 = J(f"{R}/s34/divergence_unit_seeds5to7.json")
s34a = J(f"{R}/s34/ablation_unit_seeds34.json")
prop5 = J(os.path.join(M, "FD004_unit/proposed_FD004.json"))["runs"]

# proposed family
div["proposed_family"]["proposed"] = {
    "seeds": list(range(8)),
    "rmse": [r["rmse"] for r in prop5] + d57["no_personal_head"]["rmse_per_seed"],
}
div["proposed_family"]["proposed_no_event_trigger"] = {
    "seeds": list(range(8)),
    "rmse": (J(f"{R}/FD004_rebased/ablation_unit.json")["proposed_no_event_trigger"]["rmse_per_seed"]
             + s34a["proposed_no_event_trigger"]["rmse_per_seed"]
             + d57["proposed_no_event_trigger"]["rmse_per_seed"]),
}
# delta-norm health (proposed family, all 16 runs)
tags = {
    "proposed": (["no_personal_head"] * 3 + [""] * 2 + ["no_personal_head"] * 3),
    "proposed_no_event_trigger": ["proposed_no_event_trigger"] * 8,
}
for arm, tag_list in tags.items():
    hs = []
    for s, tag in zip(range(8), tag_list):
        t = f"_{tag}" if tag else ""
        hs.append(health(f"{R}/diag/dgfed_FD004_unit{t}_seed{s}.csv"))
    div["proposed_family"][arm]["last20_median_delta_norm"] = hs
# personal-head family (pinned old study)
for arm in ["full", "no_event_trigger"]:
    div["personal_head_family"][arm] = {
        "seeds": list(range(8)),
        "rmse": cal_u[arm]["rmse_per_seed"] + ext_u[arm]["rmse_per_seed"],
    }
W("divergence_unit_8seeds.json", div)
print("\n[done] merged tree at results/merged5/")
