"""
Extension 3: Dynamic Shared Expectations (Phi)
===============================================

Tests whether authority weights (gamma) self-organise to appropriate values
and whether the weak agent learns to defer more to the strong agent.

Experimental design:
  - Kaufmann baselines K3 (static alignment=0.5) and K4 (static ToM+alignment).
  - Dynamic gamma starting from various initial values, with different
    learning rates.
  - Track gamma evolution over time as a diagnostic.

Fills Kaufmann gap: Section 4.1 identifies making alpha and gamma endogenous
as key future work.

Usage:
    python -m phas_eai.experiments.run_extension3 [--quick] [--seed 42]
"""

import argparse
import os
import sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from phas_eai.core.simulation import simulate_runs, EPOCHS, MAX_SENSE_PROBABILITY
from phas_eai.plotting.figures import (
    plot_aggregate_comparison,
    plot_system_free_energy,
    plot_convergence_overlay,
    plot_gamma_evolution,
)


KAUFMANN_BASELINES = {
    "K1": dict(
        model_label="K1: Baseline",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0, 0), alignment=0,
    ),
    "K3": dict(
        model_label="K3: Goal Alignment (static)",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0, 0), alignment=0.5,
    ),
    "K4": dict(
        model_label="K4: ToM + Alignment (static)",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0.5, 0.5), alignment=0.5,
    ),
}

# Extension 3: dynamic gamma from different starting points
EXT3_CONDITIONS = {
    "E3_g0.0_lr01": dict(
        model_label="E3: dyn gamma=0.0, lr=0.01",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0, 0), alignment=0.0,
        dynamic_gamma=True, gamma_lr=0.01,
    ),
    "E3_g0.5_lr01": dict(
        model_label="E3: dyn gamma=0.5, lr=0.01",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0, 0), alignment=0.5,
        dynamic_gamma=True, gamma_lr=0.01,
    ),
    "E3_g0.0_lr05": dict(
        model_label="E3: dyn gamma=0.0, lr=0.05",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0, 0), alignment=0.0,
        dynamic_gamma=True, gamma_lr=0.05,
    ),
    "E3_tom_dyn": dict(
        model_label="E3: ToM + dyn gamma",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0.5, 0.5), alignment=0.0,
        dynamic_gamma=True, gamma_lr=0.01,
    ),
}


def run_extension3(no_of_cycles=3, seed=None, output_dir=None, epochs=EPOCHS):
    """Run Extension 3 experiment and generate figures."""
    if seed is not None:
        np.random.seed(seed)
        os.environ["PYTHONHASHSEED"] = "0"

    if output_dir is None:
        output_dir = os.path.join(
            os.path.dirname(__file__), "..", "results", "extension3",
        )
    os.makedirs(output_dir, exist_ok=True)

    results = {}

    for key, params in {**KAUFMANN_BASELINES, **EXT3_CONDITIONS}.items():
        result = simulate_runs(
            no_of_cycles=no_of_cycles, epochs=epochs, **params,
        )
        results[key] = result

    # Figures
    plot_aggregate_comparison(
        results,
        save_path=os.path.join(output_dir, "ext3_aggregate.png"),
        title="Extension 3: Dynamic Shared Expectations",
    )
    plot_system_free_energy(
        results,
        save_path=os.path.join(output_dir, "ext3_free_energy.png"),
        title="Extension 3: System Free Energy",
    )
    plot_convergence_overlay(
        results, agent="weak",
        save_path=os.path.join(output_dir, "ext3_convergence_weak.png"),
        title="Extension 3: Weak Agent Convergence",
    )
    # Split gamma evolution into two readable figures
    gamma_baselines = {k: results[k] for k in KAUFMANN_BASELINES if k in results}
    gamma_dynamic = {k: results[k] for k in EXT3_CONDITIONS if k in results}
    plot_gamma_evolution(
        gamma_baselines,
        save_path=os.path.join(output_dir, "ext3_gamma_baselines.png"),
    )
    plot_gamma_evolution(
        gamma_dynamic,
        save_path=os.path.join(output_dir, "ext3_gamma_dynamic.png"),
    )

    print(f"\nAll Extension 3 figures saved to: {output_dir}")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extension 3: Dynamic Shared Expectations",
    )
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=str, default=None)
    args = parser.parse_args()

    cycles = 1 if args.quick else 3
    epochs = 50 if args.quick else EPOCHS

    run_extension3(
        no_of_cycles=cycles, seed=args.seed,
        output_dir=args.output_dir, epochs=epochs,
    )
