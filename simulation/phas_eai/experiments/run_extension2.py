"""
Extension 2: Regimes of Attention (Niche Construction)
======================================================

Tests whether environment shaping reduces system free energy even without
increasing individual cognitive capability.

Experimental design:
  - Kaufmann baseline K1 (no ToM, no alignment, no niche).
  - Niche construction ON with varying boost strength and kernel radius.
  - Compare system free energy and convergence against K1-K4 baselines.

Usage:
    python -m phas_eai.experiments.run_extension2 [--quick] [--seed 42]
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

# Extension 2: niche construction on baseline (no ToM, no alignment)
EXT2_CONDITIONS = {
    "E2_b0.10": dict(
        model_label="E2: niche boost=0.10",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0, 0), alignment=0,
        niche_construction=True, niche_boost=0.10, niche_radius=3,
    ),
    "E2_b0.15": dict(
        model_label="E2: niche boost=0.15",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0, 0), alignment=0,
        niche_construction=True, niche_boost=0.15, niche_radius=3,
    ),
    "E2_b0.25": dict(
        model_label="E2: niche boost=0.25",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0, 0), alignment=0,
        niche_construction=True, niche_boost=0.25, niche_radius=3,
    ),
    "E2_r5": dict(
        model_label="E2: niche radius=5",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0, 0), alignment=0,
        niche_construction=True, niche_boost=0.15, niche_radius=5,
    ),
}


def run_extension2(no_of_cycles=3, seed=None, output_dir=None, epochs=EPOCHS):
    """Run Extension 2 experiment and generate figures."""
    if seed is not None:
        np.random.seed(seed)
        os.environ["PYTHONHASHSEED"] = "0"

    if output_dir is None:
        output_dir = os.path.join(
            os.path.dirname(__file__), "..", "results", "extension2",
        )
    os.makedirs(output_dir, exist_ok=True)

    results = {}

    for key, params in {**KAUFMANN_BASELINES, **EXT2_CONDITIONS}.items():
        result = simulate_runs(
            no_of_cycles=no_of_cycles, epochs=epochs, **params,
        )
        results[key] = result

    # Figures
    plot_aggregate_comparison(
        results,
        save_path=os.path.join(output_dir, "ext2_aggregate.png"),
        title="Extension 2: Regimes of Attention (Niche Construction)",
    )
    plot_system_free_energy(
        results,
        save_path=os.path.join(output_dir, "ext2_free_energy.png"),
        title="Extension 2: System Free Energy",
    )
    plot_convergence_overlay(
        results, agent="weak",
        save_path=os.path.join(output_dir, "ext2_convergence_weak.png"),
        title="Extension 2: Weak Agent Convergence",
    )

    print(f"\nAll Extension 2 figures saved to: {output_dir}")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extension 2: Regimes of Attention",
    )
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=str, default=None)
    args = parser.parse_args()

    cycles = 1 if args.quick else 3
    epochs = 50 if args.quick else EPOCHS

    run_extension2(
        no_of_cycles=cycles, seed=args.seed,
        output_dir=args.output_dir, epochs=epochs,
    )
