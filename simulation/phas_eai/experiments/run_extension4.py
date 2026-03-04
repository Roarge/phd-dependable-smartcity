"""
Extension 4: Patterned Practices (Periodic Synchronisation)
============================================================

Tests the impact of structured coordination routines (stand-ups, threat
modelling sessions, retrospectives) on collective performance.

Experimental design:
  - Kaufmann baselines K1 and K4.
  - Patterned Practices with varying sync interval P and fidelity lambda.
  - All conditions use no ToM, no alignment (baseline), so any improvement
    comes solely from the synchronisation mechanism.

Usage:
    python -m phas_eai.experiments.run_extension4 [--quick] [--seed 42]
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
)


KAUFMANN_BASELINES = {
    "K1": dict(
        model_label="K1: Baseline",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0, 0), alignment=0,
    ),
    "K4": dict(
        model_label="K4: ToM + Alignment",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0.5, 0.5), alignment=0.5,
    ),
}

# Extension 4: periodic synchronisation
EXT4_CONDITIONS = {
    "E4_P10_f0.5": dict(
        model_label="E4: P=10, f=0.5",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0, 0), alignment=0,
        practice_interval=10, practice_fidelity=0.5,
    ),
    "E4_P20_f0.5": dict(
        model_label="E4: P=20, f=0.5",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0, 0), alignment=0,
        practice_interval=20, practice_fidelity=0.5,
    ),
    "E4_P50_f0.5": dict(
        model_label="E4: P=50, f=0.5",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0, 0), alignment=0,
        practice_interval=50, practice_fidelity=0.5,
    ),
    "E4_P10_f0.2": dict(
        model_label="E4: P=10, f=0.2",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0, 0), alignment=0,
        practice_interval=10, practice_fidelity=0.2,
    ),
    "E4_P10_f0.8": dict(
        model_label="E4: P=10, f=0.8",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0, 0), alignment=0,
        practice_interval=10, practice_fidelity=0.8,
    ),
}


def run_extension4(no_of_cycles=3, seed=None, output_dir=None, epochs=EPOCHS):
    """Run Extension 4 experiment and generate figures."""
    if seed is not None:
        np.random.seed(seed)
        os.environ["PYTHONHASHSEED"] = "0"

    if output_dir is None:
        output_dir = os.path.join(
            os.path.dirname(__file__), "..", "results", "extension4",
        )
    os.makedirs(output_dir, exist_ok=True)

    results = {}

    for key, params in {**KAUFMANN_BASELINES, **EXT4_CONDITIONS}.items():
        result = simulate_runs(
            no_of_cycles=no_of_cycles, epochs=epochs, **params,
        )
        results[key] = result

    # Figures
    plot_aggregate_comparison(
        results,
        save_path=os.path.join(output_dir, "ext4_aggregate.png"),
        title="Extension 4: Patterned Practices",
    )
    plot_system_free_energy(
        results,
        save_path=os.path.join(output_dir, "ext4_free_energy.png"),
        title="Extension 4: System Free Energy",
    )
    plot_convergence_overlay(
        results, agent="weak",
        save_path=os.path.join(output_dir, "ext4_convergence_weak.png"),
        title="Extension 4: Weak Agent Convergence",
    )

    print(f"\nAll Extension 4 figures saved to: {output_dir}")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extension 4: Patterned Practices",
    )
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=str, default=None)
    args = parser.parse_args()

    cycles = 1 if args.quick else 3
    epochs = 50 if args.quick else EPOCHS

    run_extension4(
        no_of_cycles=cycles, seed=args.seed,
        output_dir=args.output_dir, epochs=epochs,
    )
