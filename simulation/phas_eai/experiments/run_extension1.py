"""
Extension 1: Designed Cognitive Reserve (h)
===========================================

Tests hypothesis H3: designed scaffolding (h > 0) for the weak agent can
match the performance benefit of Theory of Mind.

Experimental design:
  - Kaufmann baselines (Models 1-4) with h=0 for both agents.
  - Extension 1 conditions: h swept in {0.1, 0.2, 0.3, 0.4} for the weak
    agent while the strong agent remains at h=0.  Uses Model 1 (no ToM,
    no goal alignment) as the base, so any improvement comes solely from
    the designed cognitive reserve.

Usage:
    python -m phas_eai.experiments.run_extension1 [--quick] [--seed 42]
"""

import argparse
import os
import sys
import numpy as np

# Ensure simulation/ is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from phas_eai.core.simulation import simulate_runs, EPOCHS, MAX_SENSE_PROBABILITY
from phas_eai.plotting.figures import (
    plot_aggregate_comparison,
    plot_system_free_energy,
    plot_convergence_overlay,
)


# ---------------------------------------------------------------------------
# Kaufmann baselines (matching Kaufmann's 4-model structure)
# ---------------------------------------------------------------------------
KAUFMANN_CONDITIONS = {
    "K1": dict(
        model_label="K1: Baseline",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0, 0), alignment=0,
    ),
    "K2": dict(
        model_label="K2: Theory of Mind",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0.5, 0.5), alignment=0,
    ),
    "K3": dict(
        model_label="K3: Goal Alignment",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0, 0), alignment=0.5,
    ),
    "K4": dict(
        model_label="K4: ToM + Alignment",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0.5, 0.5), alignment=0.5,
    ),
}

# Extension 1: sweep h for weak agent on the baseline (no ToM, no alignment)
H_VALUES = [0.1, 0.2, 0.3, 0.4]
EXT1_CONDITIONS = {}
for h_val in H_VALUES:
    key = f"E1_h{h_val:.1f}"
    EXT1_CONDITIONS[key] = dict(
        model_label=f"E1: h={h_val:.1f} (weak)",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0, 0), alignment=0,
        h=(0.0, h_val),
    )


def run_extension1(no_of_cycles=3, seed=None, output_dir=None, epochs=EPOCHS):
    """Run Extension 1 experiment and generate figures."""
    if seed is not None:
        np.random.seed(seed)
        os.environ["PYTHONHASHSEED"] = "0"

    if output_dir is None:
        output_dir = os.path.join(
            os.path.dirname(__file__), "..", "results", "extension1",
        )
    os.makedirs(output_dir, exist_ok=True)

    results = {}

    # Run Kaufmann baselines
    for key, params in KAUFMANN_CONDITIONS.items():
        result = simulate_runs(
            no_of_cycles=no_of_cycles, epochs=epochs, **params,
        )
        results[key] = result

    # Run Extension 1 conditions
    for key, params in EXT1_CONDITIONS.items():
        result = simulate_runs(
            no_of_cycles=no_of_cycles, epochs=epochs, **params,
        )
        results[key] = result

    # ---- Generate figures ----

    # Figure A: Full aggregate comparison (all conditions)
    plot_aggregate_comparison(
        results,
        save_path=os.path.join(output_dir, "ext1_aggregate.png"),
        title="Extension 1: Designed Cognitive Reserve",
    )

    # Figure B: System free energy comparison
    plot_system_free_energy(
        results,
        save_path=os.path.join(output_dir, "ext1_free_energy.png"),
        title="Extension 1: System Free Energy",
    )

    # Figure C: Weak agent convergence overlay
    plot_convergence_overlay(
        results, agent="weak",
        save_path=os.path.join(output_dir, "ext1_convergence_weak.png"),
        title="Extension 1: Weak Agent Convergence",
    )

    # Figure D: Kaufmann-only aggregate (for direct comparison)
    kaufmann_results = {k: results[k] for k in KAUFMANN_CONDITIONS}
    plot_aggregate_comparison(
        kaufmann_results,
        save_path=os.path.join(output_dir, "ext1_kaufmann_baseline.png"),
        title="Kaufmann Baselines (h=0)",
    )

    print(f"\nAll Extension 1 figures saved to: {output_dir}")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extension 1: Designed Cognitive Reserve (h)",
    )
    parser.add_argument(
        "--quick", action="store_true",
        help="Quick run with 1 cycle and 50 epochs",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed (default: 42)",
    )
    parser.add_argument(
        "--output-dir", type=str, default=None,
        help="Output directory for figures",
    )
    args = parser.parse_args()

    cycles = 1 if args.quick else 3
    epochs = 50 if args.quick else EPOCHS

    run_extension1(
        no_of_cycles=cycles,
        seed=args.seed,
        output_dir=args.output_dir,
        epochs=epochs,
    )
