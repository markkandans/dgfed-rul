"""Write results_manifest.json pinning every paper table to its source files.

Each source file is recorded with its git-style blob hash
(sha1 of b"blob <size>\\0<content>"), so any later regeneration that changes a
number is detectable with `git hash-object <file>` or by rerunning this script.
"""
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def blob_hash(path):
    data = open(path, "rb").read()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


TABLES = {
    "method_table_unit": {
        "description": "Main method comparison, FD004 unit partition. Baselines "
        "(fedavg/fedprox/local/central) from the v2 suite; 'proposed' = "
        "calibrated no_personal_head row; '+personal_head' = calibrated full row.",
        "sources": [
            "results/FD004_unit/fedavg_FD004.json",
            "results/FD004_unit/fedprox_FD004.json",
            "results/FD004_unit/local_FD004.json",
            "results/FD004_unit/central_FD004.json",
            "results/FD004_calibrated/ablation_unit.json",
        ],
    },
    "method_table_regime": {
        "description": "Main method comparison, FD004 regime partition (same layout).",
        "sources": [
            "results/FD004_regime/fedavg_FD004.json",
            "results/FD004_regime/fedprox_FD004.json",
            "results/FD004_regime/local_FD004.json",
            "results/FD004_regime/central_FD004.json",
            "results/FD004_calibrated/ablation_regime.json",
        ],
    },
    "rebased_ablation_unit": {
        "description": "6-row rebased ablation, unit: proposed & +personal_head "
        "reused from the calibrated ablation; four proposed_* arms fresh.",
        "sources": [
            "results/FD004_calibrated/ablation_unit.json",
            "results/FD004_rebased/ablation_unit.json",
        ],
    },
    "rebased_ablation_regime": {
        "description": "6-row rebased ablation, regime (same layout).",
        "sources": [
            "results/FD004_calibrated/ablation_regime.json",
            "results/FD004_rebased/ablation_regime.json",
        ],
    },
    "ph_lambda_sweep": {
        "description": "Page-Hinkley lambda calibration sweep (50-round dgfed, "
        "FD004 unit); chosen ph_lambda=5000.",
        "sources": ["results/ph_sweep_FD004_unit.json"],
    },
    "mechanism_seen_unseen": {
        "description": "Seen/unseen RUL stratification for full vs "
        "no_personal_head (calibrated runs; 'seen_unseen' field per seed).",
        "sources": [
            "results/FD004_calibrated/ablation_unit.json",
            "results/FD004_calibrated/ablation_regime.json",
        ],
    },
    "churn_diagnostic": {
        "description": "Personal-head arm evaluated with final global body vs "
        "each client's own final local body (head-body mismatch mechanism).",
        "sources": [
            "results/FD004_churn/churn_unit.json",
            "results/FD004_churn/churn_regime.json",
        ],
    },
    "method_table_fd002_unit": {
        "description": "Held-out FD002 confirmation, unit partition: proposed "
        "(dgfed, personalize_head=False) + baselines, frozen FD004 config.",
        "sources": [
            "results/FD002_unit/proposed_FD002.json",
            "results/FD002_unit/fedavg_FD002.json",
            "results/FD002_unit/fedprox_FD002.json",
            "results/FD002_unit/local_FD002.json",
            "results/FD002_unit/central_FD002.json",
        ],
    },
    "method_table_fd002_regime": {
        "description": "Held-out FD002 confirmation, regime partition (same layout).",
        "sources": [
            "results/FD002_regime/proposed_FD002.json",
            "results/FD002_regime/fedavg_FD002.json",
            "results/FD002_regime/fedprox_FD002.json",
            "results/FD002_regime/local_FD002.json",
            "results/FD002_regime/central_FD002.json",
        ],
    },
    "paired_seed_analysis": {
        "description": "Per-seed paired RMSE deltas of each FD004 ablation arm "
        "vs proposed (same seed & partition), with sign patterns.",
        "sources": ["results/analysis_paired_seed_FD004.json"],
    },
    "data_scale_analysis": {
        "description": "Per-client personal-head penalty vs training-window "
        "count (FD004). Per-client RMSEs from deterministic re-executions of "
        "the calibrated arms (verified to reproduce calibrated per-seed RMSE "
        "exactly).",
        "sources": [
            "results/analysis_data_scale_FD004.json",
            "results/FD004_perclient/full_unit.json",
            "results/FD004_perclient/proposed_unit.json",
            "results/FD004_perclient/full_regime.json",
            "results/FD004_perclient/proposed_regime.json",
        ],
    },
    "signed_error_check": {
        "description": "Mean signed error (pred - true) for proposed and "
        "FedAvg on FD002-unit from deterministic re-executions (per-seed "
        "RMSEs verified against the pinned runs).",
        "sources": ["results/analysis_signed_error_FD002unit.json"],
    },
    "divergence_study": {
        "description": "8-seed per-seed RMSE for full and no_event_trigger "
        "(unit): seeds 0-2 from the calibrated ablation, seeds 3-7 from the "
        "extension file. 0/8 diverged.",
        "sources": [
            "results/FD004_calibrated/ablation_unit.json",
            "results/FD004_calibrated/ablation_unit_seeds3to7.json",
        ],
    },
}



def _expand_dynamic(manifest):
    """v2: auto-pin the s34 extension and merged 5-seed trees."""
    import glob as _g
    for name, pattern, desc in [
        ("extension_s34", "results/s34/**/*.json",
         "Seed 3-4 extension runs (+local 1-4, divergence 5-7, tier-3 micro-studies)."),
        ("merged_5seed", "results/merged5/**/*.json",
         "Merged 5-seed summaries behind the revised tables (pinned 0-2 + s34)."),
    ]:
        entry = {"description": desc, "sources": {}}
        for path in sorted(_g.glob(os.path.join(ROOT, pattern), recursive=True)):
            rel = os.path.relpath(path, ROOT)
            entry["sources"][rel] = blob_hash(path)
        manifest["tables"][name] = entry

def main():
    manifest = {"tables": {}}
    missing = []
    for name, spec in TABLES.items():
        entry = {"description": spec["description"], "sources": {}}
        for rel in spec["sources"]:
            path = os.path.join(ROOT, rel)
            if not os.path.exists(path):
                missing.append(rel)
                continue
            entry["sources"][rel] = blob_hash(path)
        manifest["tables"][name] = entry
    if missing:
        raise SystemExit(f"missing source files, manifest NOT written: {missing}")
    _expand_dynamic(manifest)
    out = os.path.join(ROOT, "results_manifest.json")
    with open(out, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"[saved] {out} ({sum(len(t['sources']) for t in manifest['tables'].values())} pinned files)")


if __name__ == "__main__":
    main()
