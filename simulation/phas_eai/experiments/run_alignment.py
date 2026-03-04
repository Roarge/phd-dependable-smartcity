"""
Alignment Experiment: ToM x Alignment 2x2 Factorial
====================================================

Demonstrates that Theory of Mind requires goal alignment to be productive.
Without alignment, ToM enables competitive modelling that interferes with
collective performance.

Experimental design (2x2 factorial + scaffold conditions):
  A1: No ToM, no alignment  (= K1 baseline)
  A2: ToM, no alignment     (competitive: the counterproductive case)
  A3: No ToM, alignment     (aligned but blind to partner)
  A4: ToM + alignment       (= K4 baseline)
  A5: Scaffold, no alignment (best scaffold without ToM)
  A6: Scaffold + ToM + alignment (the missing condition: superadditive?)

Usage:
    python -m phas_eai.experiments.run_alignment [--quick] [--seed 42]
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
    plot_2x2_alignment,
)


CONDITIONS = {
    # 2x2 factorial core
    "A1_none": dict(
        model_label="A1: No ToM, no align",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0, 0), alignment=0,
    ),
    "A2_tom_only": dict(
        model_label="A2: ToM, no align",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0.5, 0.5), alignment=0,
    ),
    "A3_align_only": dict(
        model_label="A3: No ToM, align",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0, 0), alignment=0.5,
    ),
    "A4_tom_align": dict(
        model_label="A4: ToM + align",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0.5, 0.5), alignment=0.5,
    ),
    # Scaffold conditions
    "A5_scaffold": dict(
        model_label="A5: Scaffold, no align",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0, 0), alignment=0,
        h=(0.0, 0.3),
        niche_construction=True, niche_boost=0.25, niche_radius=3,
        practice_interval=20, practice_fidelity=0.5,
    ),
    "A6_scaffold_tom_align": dict(
        model_label="A6: Scaffold + ToM + align",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0.5, 0.5), alignment=0.5,
        h=(0.0, 0.3),
        niche_construction=True, niche_boost=0.25, niche_radius=3,
        practice_interval=20, practice_fidelity=0.5,
    ),
}

# Keys for the 2x2 summary plot
CORE_2X2 = {
    "no_tom_no_align": "A1_none",
    "tom_no_align": "A2_tom_only",
    "no_tom_align": "A3_align_only",
    "tom_align": "A4_tom_align",
}


def run_alignment(no_of_cycles=3, seed=None, output_dir=None, epochs=EPOCHS):
    """Run the alignment 2x2 experiment and generate figures."""
    if seed is not None:
        np.random.seed(seed)
        os.environ["PYTHONHASHSEED"] = "0"

    if output_dir is None:
        output_dir = os.path.join(
            os.path.dirname(__file__), "..", "results", "alignment",
        )
    os.makedirs(output_dir, exist_ok=True)

    results = {}

    for key, params in CONDITIONS.items():
        result = simulate_runs(
            no_of_cycles=no_of_cycles, epochs=epochs, **params,
        )
        results[key] = result

    # Standard figures
    plot_aggregate_comparison(
        results,
        save_path=os.path.join(output_dir, "alignment_aggregate.png"),
        title="Alignment x ToM Factorial",
    )
    plot_system_free_energy(
        results,
        save_path=os.path.join(output_dir, "alignment_free_energy.png"),
        title="Alignment x ToM: System Free Energy",
    )
    plot_convergence_overlay(
        results, agent="weak",
        save_path=os.path.join(output_dir, "alignment_convergence_weak.png"),
        title="Alignment x ToM: Weak Agent Convergence",
    )
    plot_convergence_overlay(
        results, agent="strong",
        save_path=os.path.join(output_dir, "alignment_convergence_strong.png"),
        title="Alignment x ToM: Strong Agent Convergence",
    )

    # Headline 2x2 interaction figure
    plot_2x2_alignment(
        results,
        core_keys=CORE_2X2,
        save_path=os.path.join(output_dir, "alignment_2x2_summary.png"),
        title="ToM Requires Alignment: 2x2 Interaction",
    )

    print(f"\nAll alignment figures saved to: {output_dir}")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Alignment Experiment: ToM x Alignment 2x2 Factorial",
    )
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=str, default=None)
    args = parser.parse_args()

    cycles = 1 if args.quick else 3
    epochs = 50 if args.quick else EPOCHS

    run_alignment(
        no_of_cycles=cycles, seed=args.seed,
        output_dir=args.output_dir, epochs=epochs,
    )
