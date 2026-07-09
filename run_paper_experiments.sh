#!/bin/zsh
# Sequential paper experiments for FD004, run twice: --partition unit, then regime.
# Each step logs to logs/<name>.log; each suite's JSONs land in results/FD004_<partition>/.
set -u
cd "$(dirname "$0")"
source .venv/bin/activate
mkdir -p logs results

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
  run_step dgfed_FD004_${PART}    python main.py --method dgfed   --subset FD004 --rounds 200 --seeds 3 --partition $PART
  run_step fedavg_FD004_${PART}   python main.py --method fedavg  --subset FD004 --rounds 200 --seeds 3 --partition $PART
  run_step fedprox_FD004_${PART}  python main.py --method fedprox --subset FD004 --rounds 200 --seeds 3 --partition $PART
  run_step local_FD004_${PART}    python main.py --method local   --subset FD004 --partition $PART
  run_step central_FD004_${PART}  python main.py --method central --subset FD004 --seeds 3 --partition $PART
  run_step ablation_FD004_${PART} python run_ablation.py --subset FD004 --rounds 200 --seeds 3 --partition $PART
  mkdir -p "results/FD004_${PART}"
  mv results/*_FD004.json "results/FD004_${PART}/" 2>/dev/null || true
  echo "=== SUITE ${PART} DONE (results in results/FD004_${PART}/) ==="
done
echo "=== ALL DONE ==="
