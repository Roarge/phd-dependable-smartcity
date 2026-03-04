"""
Combined PHAS-EAI Model
========================

Runs the full PHAS-EAI model with all extensions enabled, comparing against
Kaufmann baselines and individual extensions.

This is the headline experiment: it tests whether the full combination of
environmental scaffolding mechanisms (h, niche construction, Patterned
Practices, dynamic gamma) can match or exceed the collective performance
of Kaufmann Model 4 (ToM + Goal Alignment) without requiring those
individual cognitive capabilities.

Usage:
    python -m phas_eai.experiments.run_combined [--quick] [--seed 42]
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


CONDITIONS = {
    # Kaufmann baselines
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
    # Individual extensions (best from each)
    "E1_best": dict(
        model_label="E1: h=0.3 only",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0, 0), alignment=0,
        h=(0.0, 0.3),
    ),
    "E2_best": dict(
        model_label="E2: niche only",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0, 0), alignment=0,
        niche_construction=True, niche_boost=0.25, niche_radius=3,
    ),
    # Combined: scaffolding without ToM
    "PHAS_scaffold": dict(
        model_label="PHAS: scaffold (no ToM)",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0, 0), alignment=0,
        h=(0.0, 0.3),
        niche_construction=True, niche_boost=0.25, niche_radius=3,
        practice_interval=20, practice_fidelity=0.5,
    ),
    # Combined: scaffolding with dynamic gamma (no ToM)
    "PHAS_dyn": dict(
        model_label="PHAS: scaffold + dyn gamma",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0, 0), alignment=0.0,
        h=(0.0, 0.3),
        niche_construction=True, niche_boost=0.25, niche_radius=3,
        practice_interval=20, practice_fidelity=0.5,
        dynamic_gamma=True, gamma_lr=0.01,
    ),
    # Full model: all extensions including ToM and alignment
    "PHAS_full": dict(
        model_label="PHAS: full model",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0.5, 0.5), alignment=0.5,
        h=(0.0, 0.3),
        niche_construction=True, niche_boost=0.25, niche_radius=3,
        practice_interval=20, practice_fidelity=0.5,
        dynamic_gamma=True, gamma_lr=0.01,
    ),
}


def run_combined(no_of_cycles=3, seed=None, output_dir=None, epochs=EPOCHS):
    """Run the combined PHAS-EAI experiment."""
    if seed is not None:
        np.random.seed(seed)
        os.environ["PYTHONHASHSEED"] = "0"

    if output_dir is None:
        output_dir = os.path.join(
            os.path.dirname(__file__), "..", "results", "combined",
        )
    os.makedirs(output_dir, exist_ok=True)

    results = {}

    for key, params in CONDITIONS.items():
        result = simulate_runs(
            no_of_cycles=no_of_cycles, epochs=epochs, **params,
        )
        results[key] = result

    # Figures
    plot_aggregate_comparison(
        results,
        save_path=os.path.join(output_dir, "combined_aggregate.png"),
        title="Combined PHAS-EAI Model Comparison",
    )
    plot_system_free_energy(
        results,
        save_path=os.path.join(output_dir, "combined_free_energy.png"),
        title="Combined: System Free Energy",
    )
    plot_convergence_overlay(
        results, agent="weak",
        save_path=os.path.join(output_dir, "combined_convergence_weak.png"),
        title="Combined: Weak Agent Convergence",
    )
    plot_convergence_overlay(
        results, agent="strong",
        save_path=os.path.join(output_dir, "combined_convergence_strong.png"),
        title="Combined: Strong Agent Convergence",
    )
    # Split gamma evolution into two readable figures
    gamma_baselines = {k: results[k] for k in ["K1", "K4", "E1_best", "E2_best"]
                       if k in results}
    gamma_phas = {k: results[k] for k in ["PHAS_scaffold", "PHAS_dyn", "PHAS_full"]
                  if k in results}
    plot_gamma_evolution(
        gamma_baselines,
        save_path=os.path.join(output_dir, "combined_gamma_baselines.png"),
    )
    plot_gamma_evolution(
        gamma_phas,
        save_path=os.path.join(output_dir, "combined_gamma_phas.png"),
    )

    print(f"\nAll combined figures saved to: {output_dir}")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Combined PHAS-EAI Model",
    )
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=str, default=None)
    args = parser.parse_args()

    cycles = 1 if args.quick else 3
    epochs = 50 if args.quick else EPOCHS

    run_combined(
        no_of_cycles=cycles, seed=args.seed,
        output_dir=args.output_dir, epochs=epochs,
    )
