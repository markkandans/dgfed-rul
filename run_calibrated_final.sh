#!/bin/zsh
# Final calibrated dgfed runs (ph_lambda=5000 via config default).
# A/B: 5-variant ablation, 3 seeds, both partitions (paper's dgfed numbers).
# C:   item-3 divergence study — full,no_event_trigger (unit) seeds 3..7,
#      combined with A's seeds 0..2 for 8 seeds total.
set -u
cd "$(dirname "$0")"
source .venv/bin/activate
mkdir -p logs results/FD004_calibrated

VARS="full,no_drift_signal,no_event_trigger,plain_aggregation,no_personal_head"

run_step() {
  local name="$1"; shift
  echo "=== START $name : $* ==="
  if "$@" > "logs/${name}.log" 2>&1; then
    echo "=== PASS  $name ==="
  else
    echo "=== FAIL  $name (exit $?) — see logs/${name}.log ==="
  fi
}

run_step calib_ablation_unit python run_ablation.py --subset FD004 --rounds 200 --seeds 3 --partition unit --variants $VARS
mv results/ablation_FD004.json results/FD004_calibrated/ablation_unit.json

run_step calib_ablation_regime python run_ablation.py --subset FD004 --rounds 200 --seeds 3 --partition regime --variants $VARS
mv results/ablation_FD004.json results/FD004_calibrated/ablation_regime.json

run_step calib_divergence_unit python run_ablation.py --subset FD004 --rounds 200 --seed 3 --seeds 5 --partition unit --variants full,no_event_trigger
mv results/ablation_FD004.json results/FD004_calibrated/ablation_unit_seeds3to7.json

echo "=== ALL DONE ==="
