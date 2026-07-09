#!/bin/zsh
# Paper-freeze suite: rebased ablation (4 new arms; base + personal-head arm
# reused from results/FD004_calibrated/) + churn diagnostic.
set -u
cd "$(dirname "$0")"
source .venv/bin/activate
mkdir -p logs results/FD004_rebased

VARS="proposed_no_drift_signal,proposed_no_event_trigger,proposed_plain_aggregation,proposed_no_compression"

run_step() {
  local name="$1"; shift
  echo "=== START $name : $* ==="
  if "$@" > "logs/${name}.log" 2>&1; then
    echo "=== PASS  $name ==="
  else
    echo "=== FAIL  $name (exit $?) — see logs/${name}.log ==="
  fi
}

run_step rebased_ablation_unit python run_ablation.py --subset FD004 --rounds 200 --seeds 3 --partition unit --variants $VARS
mv results/ablation_FD004.json results/FD004_rebased/ablation_unit.json

run_step rebased_ablation_regime python run_ablation.py --subset FD004 --rounds 200 --seeds 3 --partition regime --variants $VARS
mv results/ablation_FD004.json results/FD004_rebased/ablation_regime.json

run_step churn_unit python run_churn.py --partition unit --rounds 200 --seeds 3
run_step churn_regime python run_churn.py --partition regime --rounds 200 --seeds 3

echo "=== ALL DONE ==="
