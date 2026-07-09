#!/bin/zsh
# Tier-1 5-seed extension (+Tier-3 micro-studies). Frozen config; seeds only.
# All outputs -> results/s34/ (pinned 3-seed files are never touched).
# Dedupe: per-client persistence (item 7) comes free from the main.py JSONs of
# item 1; divergence seeds 3-4 (item 4) reuse items 1/3; only 5-7 run here.
set -u
cd "$(dirname "$0")"
source .venv/bin/activate
mkdir -p logs/s34 results/s34

run_step() {
  local name="$1"; shift
  echo "=== START $name : $* ==="
  if "$@" > "logs/s34/${name}.log" 2>&1; then
    echo "=== PASS  $name ==="
  else
    echo "=== FAIL  $name (exit $?) — see logs/s34/${name}.log ==="
  fi
}

# ---- item 1: mains, seeds 3-4 (+ item 7 per-client data for FD004 rows) ----
for SUB in FD004 FD002; do
  for PART in unit regime; do
    run_step proposed_${SUB}_${PART} python main.py --method dgfed --no-personal-head --subset $SUB --partition $PART --rounds 200 --seed 3 --seeds 2
    mv results/dgfed_${SUB}.json results/s34/proposed_${SUB}_${PART}.json
    run_step fedavg_${SUB}_${PART} python main.py --method fedavg --subset $SUB --partition $PART --rounds 200 --seed 3 --seeds 2
    mv results/fedavg_${SUB}.json results/s34/fedavg_${SUB}_${PART}.json
    run_step fedprox_${SUB}_${PART} python main.py --method fedprox --subset $SUB --partition $PART --rounds 200 --seed 3 --seeds 2
    mv results/fedprox_${SUB}.json results/s34/fedprox_${SUB}_${PART}.json
    run_step central_${SUB}_${PART} python main.py --method central --subset $SUB --partition $PART --seed 3 --seeds 2
    mv results/central_${SUB}.json results/s34/central_${SUB}_${PART}.json
    # ---- item 2: local, seeds 1-4 ----
    run_step local_${SUB}_${PART} python main.py --method local --subset $SUB --partition $PART --seed 1 --seeds 4
    mv results/local_${SUB}.json results/s34/local_${SUB}_${PART}.json
  done
done
for PART in unit regime; do
  run_step dgfedp_FD004_${PART} python main.py --method dgfed --subset FD004 --partition $PART --rounds 200 --seed 3 --seeds 2
  mv results/dgfed_FD004.json results/s34/dgfedp_FD004_${PART}.json
done

# ---- item 3: rebased ablation arms, seeds 3-4 ----
VARS="proposed_no_drift_signal,proposed_no_event_trigger,proposed_plain_aggregation,proposed_no_compression"
for PART in unit regime; do
  run_step ablation_${PART}_s34 python run_ablation.py --subset FD004 --rounds 200 --seed 3 --seeds 2 --partition $PART --variants $VARS
  mv results/ablation_FD004.json results/s34/ablation_${PART}_seeds34.json
done

# ---- item 4: divergence seeds 5-7 (unit; both arm families' proposed side) --
run_step divergence_unit_s57 python run_ablation.py --subset FD004 --rounds 200 --seed 5 --seeds 3 --partition unit --variants no_personal_head,proposed_no_event_trigger
mv results/ablation_FD004.json results/s34/divergence_unit_seeds5to7.json

# ---- item 5: churn, seeds 3-4 ----
for PART in unit regime; do
  run_step churn_${PART}_s34 python run_churn.py --partition $PART --rounds 200 --seed 3 --seeds 2 --out results/s34/churn_${PART}_seeds34.json
done

# ---- item 6: signed error, seeds 3-4 (refs = item-1 s34 outputs) ----
run_step signed_error_s34 python run_signed_error.py --seed 3 --seeds 2 \
  --out results/s34/signed_error_FD002unit_seeds34.json \
  --ref-proposed results/s34/proposed_FD002_unit.json \
  --ref-fedavg results/s34/fedavg_FD002_unit.json

# ---- tier 3 ----
run_step overhead_bench python run_overhead_bench.py
run_step sensitivity python run_sensitivity.py

echo "=== ALL DONE ==="
