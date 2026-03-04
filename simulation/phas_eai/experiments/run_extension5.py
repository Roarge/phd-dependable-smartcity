"""
Extension 5: Disturbance Episodes (Resilience Testing)
======================================================

Tests whether PHAS-EAI extensions improve resilience (faster recovery after
unexpected target relocation).

Experimental design:
  - All targets relocate at epoch 100 (disturbance event).
  - Agents must re-converge from their current positions.
  - Compare recovery across: K1, K4, h-augmented, niche-augmented, combined.

Measures:
  - Epochs to re-converge within threshold distance.
  - System free energy trajectory after disturbance.

Usage:
    python -m phas_eai.experiments.run_extension5 [--quick] [--seed 42]
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


def _conditions(disturbance_epoch):
    """Build conditions dict with the given disturbance epoch."""
    return {
        "K1_dist": dict(
            model_label="K1: Baseline + disturbance",
            perceptiveness=MAX_SENSE_PROBABILITY,
            alterity=(0, 0), alignment=0,
            disturbance_epoch=disturbance_epoch,
        ),
        "K4_dist": dict(
            model_label="K4: ToM+Align + disturbance",
            perceptiveness=MAX_SENSE_PROBABILITY,
            alterity=(0.5, 0.5), alignment=0.5,
            disturbance_epoch=disturbance_epoch,
        ),
        "E5_h": dict(
            model_label="E5: h=0.3 + disturbance",
            perceptiveness=MAX_SENSE_PROBABILITY,
            alterity=(0, 0), alignment=0,
            h=(0.0, 0.3),
            disturbance_epoch=disturbance_epoch,
        ),
        "E5_niche": dict(
            model_label="E5: niche + disturbance",
            perceptiveness=MAX_SENSE_PROBABILITY,
            alterity=(0, 0), alignment=0,
            niche_construction=True, niche_boost=0.25, niche_radius=3,
            disturbance_epoch=disturbance_epoch,
        ),
        "E5_combined": dict(
            model_label="E5: h+niche+practice + dist",
            perceptiveness=MAX_SENSE_PROBABILITY,
            alterity=(0, 0), alignment=0,
            h=(0.0, 0.3),
            niche_construction=True, niche_boost=0.25, niche_radius=3,
            practice_interval=20, practice_fidelity=0.5,
            disturbance_epoch=disturbance_epoch,
        ),
        "E5_full": dict(
            model_label="E5: full PHAS-EAI + dist",
            perceptiveness=MAX_SENSE_PROBABILITY,
            alterity=(0.5, 0.5), alignment=0.0,
            h=(0.0, 0.3),
            niche_construction=True, niche_boost=0.25, niche_radius=3,
            practice_interval=20, practice_fidelity=0.5,
            dynamic_gamma=True, gamma_lr=0.01,
            disturbance_epoch=disturbance_epoch,
        ),
    }


def run_extension5(no_of_cycles=3, seed=None, output_dir=None, epochs=EPOCHS):
    """Run Extension 5 experiment and generate figures."""
    if seed is not None:
        np.random.seed(seed)
        os.environ["PYTHONHASHSEED"] = "0"

    if output_dir is None:
        output_dir = os.path.join(
            os.path.dirname(__file__), "..", "results", "extension5",
        )
    os.makedirs(output_dir, exist_ok=True)

    # Scale disturbance to midpoint of actual epoch count
    disturbance_epoch = epochs // 2
    conditions = _conditions(disturbance_epoch)

    results = {}

    for key, params in conditions.items():
        result = simulate_runs(
            no_of_cycles=no_of_cycles, epochs=epochs, **params,
        )
        results[key] = result

    # Figures
    plot_aggregate_comparison(
        results,
        save_path=os.path.join(output_dir, "ext5_aggregate.png"),
        title="Extension 5: Disturbance Recovery",
    )
    plot_system_free_energy(
        results,
        save_path=os.path.join(output_dir, "ext5_free_energy.png"),
        title="Extension 5: System Free Energy Under Disturbance",
    )
    plot_convergence_overlay(
        results, agent="weak",
        save_path=os.path.join(output_dir, "ext5_convergence_weak.png"),
        title="Extension 5: Weak Agent Recovery",
    )
    plot_convergence_overlay(
        results, agent="strong",
        save_path=os.path.join(output_dir, "ext5_convergence_strong.png"),
        title="Extension 5: Strong Agent Recovery",
    )

    print(f"\nAll Extension 5 figures saved to: {output_dir}")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extension 5: Disturbance Episodes",
    )
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=str, default=None)
    args = parser.parse_args()

    cycles = 1 if args.quick else 3
    epochs = 50 if args.quick else EPOCHS

    run_extension5(
        no_of_cycles=cycles, seed=args.seed,
        output_dir=args.output_dir, epochs=epochs,
    )
