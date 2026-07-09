# DGFed — Artifact Repository

Code, results, and verification manifest for the paper:

> Markkandan S, "DGFed: Drift-Governed Federated Learning for Industrial
> Remaining Useful Life Estimation," submitted to *IEEE Transactions on
> Industrial Informatics*. [CITATION / DOI TO BE ADDED ON PUBLICATION]

Archived at: [ZENODO DOI]

## What this repository contains

- `main.py`, `config.py`, `metrics.py`, `baselines.py` — entry point,
  configuration, metrics (RMSE, asymmetric C-MAPSS score, retention bins,
  seen/unseen strata), and the centralized/local baselines.
- `data/` — C-MAPSS loading, preprocessing, the unit/regime federation
  partitions, and drift injection.
- `models/`, `federated/` — the shared CNN–LSTM backbone; drift detection
  (Page–Hinkley on residuals), event-triggered uploads, error-feedback
  top-k + 8-bit compression, drift/staleness-aware aggregation with
  adaptive clipping.
- `run_ablation.py`, `run_churn.py`, `run_ph_sweep.py`,
  `run_signed_error.py`, and the suite runner scripts (`run_*.sh`) —
  ablation arms (including the `proposed_*` rebased variants), the
  counterfactual-body study, the detector-threshold sweep, the
  signed-error check, and the sequential experiment suites.
- `results/` — every result JSON behind the paper's tables, organized as
  `FD004_unit/`, `FD004_regime/`, `FD004_calibrated/`, `FD004_rebased/`,
  `FD004_churn/`, `FD004_perclient/`, `FD002_*/`, per-round diagnostics in
  `diag/`, the λ-sweep table (`ph_sweep_FD004_unit.json`), the analysis
  JSONs (paired-seed, data-scale, signed-error), and archived earlier
  generations (`archive_*/`).
- `results_manifest.json` + `generate_manifest.py` — pins all 38 artifact
  files behind the paper's tables with git blob hashes.
- `paper/` — figure-generation scripts (`make_figures.py`) and supplementary
  material (see below).

The pipeline is dataset-agnostic: a loader returning the same per-client
structures as `data/cmapss.py` slots FEMTO/PRONOSTIA or CWRU into the
identical federation, ablation, and manifest tooling — the second-family
validation named in the paper's future work.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # torch, numpy, pandas, scikit-learn
```

**Dataset (not redistributed here):** download NASA C-MAPSS from the NASA
Prognostics Center of Excellence data repository and place
`train/test/RUL_FD00x.txt` under `datasets/CMAPSS/`.

## Reproducing the paper's tables

Seeds 0–2 throughout; `--partition unit` (12 clients) or `regime` (6).

| Paper item | Command |
|---|---|
| Tables II–III, baselines | `python main.py --method {fedavg,fedprox,local,central} --subset {FD004,FD002} --partition {unit,regime} --rounds 200 --seeds 3` (local: single seed, omit `--seeds`) |
| Tables II–III, DGFed (proposed) | `python main.py --method dgfed --no-personal-head --subset ... --partition ... --rounds 200 --seeds 3` |
| Table IV ablation + DGFed-P | `python run_ablation.py --subset FD004 --partition {unit,regime} --rounds 200 --seeds 3` (arms incl. `proposed_*`) |
| Table V panel A (strata) | recorded per run (seen/unseen in each results JSON) |
| Table V panel B (churn) | `python run_churn.py --partition {unit,regime} --rounds 200 --seeds 3` |
| λ sweep (Sec. V-C) | `python run_ph_sweep.py --subset FD004 --partition unit --rounds 50` → `results/ph_sweep_FD004_unit.json` |
| Signed-error check (Sec. VI-B) | `python run_signed_error.py` → `results/analysis_signed_error_FD002unit.json` |

## Verifying the paper's numbers

Every number in the paper traces to a file pinned in
`results_manifest.json`. To verify:

```bash
python generate_manifest.py          # refuses to write if any source is missing
git hash-object results/<file>.json  # compare against the manifest entry
```

Determinism note: runs are exactly reproducible on the same machine
(Apple-silicon MPS; per-seed RMSEs reproduce bit-for-bit, exploited by the
counterfactual study). CPU backends differ numerically by ~1.4%.

## Supplementary material

`paper/supplementary/` contains material referenced during review but not in
the 10-page manuscript: `fig3_paired_deltas.*` (per-seed ablation deltas;
summarized by Table IV's sign column), `fig5_lambda_sweep.*` (detector
calibration curve; numbers appear in Secs. V-C and VI-E), and
`analysis_signed_error_FD002unit.json` (shared late-bias check, Sec. VI-B).

## License

Code: [MIT suggested — author to confirm]. Result files and figures:
[CC BY 4.0 suggested — author to confirm]. The C-MAPSS dataset remains
subject to NASA's own distribution terms and is not included.

## Contact

Markkandan S — School of Electronics Engineering, Vellore Institute of
Technology, Chennai, India. ORCID: 0000-0003-3704-4536.
E-mail: markkandan.s@vit.ac.in
