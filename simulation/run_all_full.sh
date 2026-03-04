#!/bin/bash
# Run ALL PHAS-EAI experiments at full scale (200 epochs, 3 cycles, seed 42).
# Expected total runtime: ~7 hours.
set -e

cd "$(dirname "$0")"
source .venv/bin/activate
export PYTHONHASHSEED=0
export MPLBACKEND=Agg

SEED=42
echo "=== PHAS-EAI Full Experiment Suite ==="
echo "Start: $(date)"
echo ""

echo "--- Extension 1: Designed Cognitive Reserve (h) ---"
python -m phas_eai.experiments.run_extension1 --seed $SEED
echo ""

echo "--- Extension 2: Regimes of Attention (niche) ---"
python -m phas_eai.experiments.run_extension2 --seed $SEED
echo ""

echo "--- Extension 3: Dynamic Shared Expectations (gamma) ---"
python -m phas_eai.experiments.run_extension3 --seed $SEED
echo ""

echo "--- Extension 4: Patterned Practices ---"
python -m phas_eai.experiments.run_extension4 --seed $SEED
echo ""

echo "--- Extension 5: Disturbance Episodes ---"
python -m phas_eai.experiments.run_extension5 --seed $SEED
echo ""

echo "--- Combined Model ---"
python -m phas_eai.experiments.run_combined --seed $SEED
echo ""

echo "--- Combination Experiments (Tiers 1-3) ---"
python -m phas_eai.experiments.run_combinations --tier all --seed $SEED
echo ""

echo "--- Alignment 2x2 Factorial ---"
python -m phas_eai.experiments.run_alignment --seed $SEED
echo ""

echo "=== ALL EXPERIMENTS COMPLETE ==="
echo "End: $(date)"
