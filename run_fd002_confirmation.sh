#!/bin/zsh
# FD002 held-out confirmation (frozen config, ph_lambda=5000):
#   proposed (dgfed --no-personal-head), fedavg, fedprox, local, central
#   3 seeds x 200 rounds, both partitions.
# Plus FD004 per-client recovery runs (deterministic re-execution of the
# calibrated full / proposed arms via main.py, which persists per_client_rmse).
set -u
cd "$(dirname "$0")"
source .venv/bin/activate
mkdir -p logs results/FD002_unit results/FD002_regime results/FD004_perclient

run_step() {
  local name="$1"; shift
  echo "=== START $name : $* ==="
  if "$@" > "logs/${name}.log" 2>&1; then
    echo "=== PASS  $name ==="
  else
    echo "=== FAIL  $name (exit $?) — see logs/${name}.log ==="
  fi
}

for PART in unit regime; do
  run_step proposed_FD002_${PART} python main.py --method dgfed --no-personal-head --subset FD002 --rounds 200 --seeds 3 --partition $PART
  mv results/dgfed_FD002.json results/FD002_${PART}/proposed_FD002.json
  run_step fedavg_FD002_${PART}   python main.py --method fedavg  --subset FD002 --rounds 200 --seeds 3 --partition $PART
  run_step fedprox_FD002_${PART}  python main.py --method fedprox --subset FD002 --rounds 200 --seeds 3 --partition $PART
  run_step local_FD002_${PART}    python main.py --method local   --subset FD002 --partition $PART
  run_step central_FD002_${PART}  python main.py --method central --subset FD002 --seeds 3 --partition $PART
  mv results/*_FD002.json results/FD002_${PART}/ 2>/dev/null || true
done

for PART in unit regime; do
  run_step perclient_full_${PART}     python main.py --method dgfed --subset FD004 --rounds 200 --seeds 3 --partition $PART
  mv results/dgfed_FD004.json results/FD004_perclient/full_${PART}.json
  run_step perclient_proposed_${PART} python main.py --method dgfed --no-personal-head --subset FD004 --rounds 200 --seeds 3 --partition $PART
  mv results/dgfed_FD004.json results/FD004_perclient/proposed_${PART}.json
done
echo "=== ALL DONE ==="
