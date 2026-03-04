"""
Combination Experiments: Scaffolding x ToM Interactions
=======================================================

Tests how PHAS-EAI scaffolding mechanisms interact with Theory of Mind
(alterity). Organised in three tiers:

  Tier 1: Scaffolding amplifies ToM (steady state)
  Tier 2: Scaffolding + ToM under disturbance
  Tier 3: Dynamic gamma diagnostic

Usage:
    python -m phas_eai.experiments.run_combinations --tier 1
    python -m phas_eai.experiments.run_combinations --tier 2
    python -m phas_eai.experiments.run_combinations --tier 3
    python -m phas_eai.experiments.run_combinations --tier all
    python -m phas_eai.experiments.run_combinations --tier 1 --quick
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


# ---------------------------------------------------------------------------
# Shared baselines (included in every tier)
# ---------------------------------------------------------------------------
BASELINES = {
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

# ---------------------------------------------------------------------------
# Tier 1: Scaffolding amplifies ToM (steady state)
# ---------------------------------------------------------------------------
TIER1_CONDITIONS = {
    "C1_tom_niche": dict(
        model_label="C1: ToM + niche",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0.5, 0.5), alignment=0,
        niche_construction=True, niche_boost=0.25, niche_radius=3,
    ),
    "C2_tom_h": dict(
        model_label="C2: ToM + h",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0.5, 0.5), alignment=0,
        h=(0.0, 0.3),
    ),
    "C3_tom_niche_h": dict(
        model_label="C3: ToM + niche + h",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0.5, 0.5), alignment=0,
        h=(0.0, 0.3),
        niche_construction=True, niche_boost=0.25, niche_radius=3,
    ),
    "C6_niche_only": dict(
        model_label="C6: niche only (no ToM)",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0, 0), alignment=0,
        niche_construction=True, niche_boost=0.25, niche_radius=3,
    ),
}

# ---------------------------------------------------------------------------
# Tier 2: Scaffolding + ToM under disturbance
# ---------------------------------------------------------------------------

def _tier2_conditions(disturbance_epoch):
    """Build Tier 2 conditions with the given disturbance epoch."""
    return {
        "K1_dist": dict(
            model_label="K1: Baseline + dist",
            perceptiveness=MAX_SENSE_PROBABILITY,
            alterity=(0, 0), alignment=0,
            disturbance_epoch=disturbance_epoch,
        ),
        "K4_dist": dict(
            model_label="K4: ToM+Align + dist",
            perceptiveness=MAX_SENSE_PROBABILITY,
            alterity=(0.5, 0.5), alignment=0.5,
            disturbance_epoch=disturbance_epoch,
        ),
        "C4_tom_niche_dist": dict(
            model_label="C4: ToM + niche + dist",
            perceptiveness=MAX_SENSE_PROBABILITY,
            alterity=(0.5, 0.5), alignment=0,
            niche_construction=True, niche_boost=0.25, niche_radius=3,
            disturbance_epoch=disturbance_epoch,
        ),
        "C5_full_dist": dict(
            model_label="C5: full scaffold + dist",
            perceptiveness=MAX_SENSE_PROBABILITY,
            alterity=(0.5, 0.5), alignment=0,
            h=(0.0, 0.3),
            niche_construction=True, niche_boost=0.25, niche_radius=3,
            practice_interval=20, practice_fidelity=0.5,
            dynamic_gamma=True, gamma_lr=0.01,
            disturbance_epoch=disturbance_epoch,
        ),
    }

# ---------------------------------------------------------------------------
# Tier 3: Dynamic gamma diagnostic
# ---------------------------------------------------------------------------
TIER3_CONDITIONS = {
    "C7_dyn_niche": dict(
        model_label="C7: ToM + dyn gamma + niche (lr=0.05)",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0.5, 0.5), alignment=0,
        niche_construction=True, niche_boost=0.25, niche_radius=3,
        dynamic_gamma=True, gamma_lr=0.05,
    ),
    "C7b_dyn_niche_fast": dict(
        model_label="C7b: ToM + dyn gamma + niche (lr=0.1)",
        perceptiveness=MAX_SENSE_PROBABILITY,
        alterity=(0.5, 0.5), alignment=0,
        niche_construction=True, niche_boost=0.25, niche_radius=3,
        dynamic_gamma=True, gamma_lr=0.1,
    ),
}


def _get_conditions(tier, epochs=EPOCHS):
    """Return the conditions dict for a given tier."""
    disturbance_epoch = epochs // 2
    if tier == "1":
        return {**BASELINES, **TIER1_CONDITIONS}
    elif tier == "2":
        return _tier2_conditions(disturbance_epoch)
    elif tier == "3":
        return {**BASELINES, **TIER3_CONDITIONS}
    elif tier == "all":
        return {
            **BASELINES,
            **TIER1_CONDITIONS,
            **_tier2_conditions(disturbance_epoch),
            **TIER3_CONDITIONS,
        }
    else:
        raise ValueError(f"Unknown tier: {tier}. Use 1, 2, 3, or all.")


def _output_dir(tier, base_dir=None):
    """Return the output directory for a given tier."""
    if base_dir is not None:
        return base_dir
    root = os.path.join(os.path.dirname(__file__), "..", "results")
    return os.path.join(root, f"combinations_tier{tier}")


def _generate_figures(results, output_dir, tier):
    """Generate all figures for the given tier and results."""
    prefix = f"tier{tier}"

    plot_aggregate_comparison(
        results,
        save_path=os.path.join(output_dir, f"{prefix}_aggregate.png"),
        title=f"Tier {tier}: Scaffolding x ToM Combinations",
    )
    plot_system_free_energy(
        results,
        save_path=os.path.join(output_dir, f"{prefix}_free_energy.png"),
        title=f"Tier {tier}: System Free Energy",
    )
    plot_convergence_overlay(
        results, agent="weak",
        save_path=os.path.join(output_dir, f"{prefix}_convergence_weak.png"),
        title=f"Tier {tier}: Weak Agent Convergence",
    )
    plot_convergence_overlay(
        results, agent="strong",
        save_path=os.path.join(output_dir, f"{prefix}_convergence_strong.png"),
        title=f"Tier {tier}: Strong Agent Convergence",
    )

    # Gamma evolution for tiers that have dynamic gamma conditions
    if tier in ("3", "all"):
        plot_gamma_evolution(
            results,
            save_path=os.path.join(output_dir, f"{prefix}_gamma.png"),
            title=f"Tier {tier}: Gamma Evolution",
        )
    elif tier == "2":
        gamma_results = {
            k: v for k, v in results.items()
            if not results[k][5].empty
        }
        if gamma_results:
            plot_gamma_evolution(
                gamma_results,
                save_path=os.path.join(output_dir, f"{prefix}_gamma.png"),
                title=f"Tier {tier}: Gamma Evolution (C5)",
            )


def run_tier(tier, no_of_cycles=3, seed=None, output_dir=None, epochs=EPOCHS):
    """Run all conditions for a given tier."""
    if seed is not None:
        np.random.seed(seed)
        os.environ["PYTHONHASHSEED"] = "0"

    out = _output_dir(tier, output_dir)
    os.makedirs(out, exist_ok=True)

    conditions = _get_conditions(tier, epochs=epochs)
    results = {}

    for key, params in conditions.items():
        result = simulate_runs(
            no_of_cycles=no_of_cycles, epochs=epochs, **params,
        )
        results[key] = result

    _generate_figures(results, out, tier)

    print(f"\nTier {tier} figures saved to: {out}")
    return results


def run_all(no_of_cycles=3, seed=None, output_dir=None, epochs=EPOCHS):
    """Run all tiers and produce cross-tier summary."""
    all_results = {}

    for tier in ("1", "2", "3"):
        tier_results = run_tier(
            tier, no_of_cycles=no_of_cycles, seed=seed, epochs=epochs,
        )
        all_results.update(tier_results)

    # Cross-tier summary
    out = _output_dir("all", output_dir)
    os.makedirs(out, exist_ok=True)
    _generate_figures(all_results, out, "all")

    print(f"\nCross-tier summary saved to: {out}")
    return all_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Combination Experiments: Scaffolding x ToM",
    )
    parser.add_argument(
        "--tier", type=str, default="1",
        choices=["1", "2", "3", "all"],
        help="Which tier to run (1, 2, 3, or all)",
    )
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=str, default=None)
    args = parser.parse_args()

    cycles = 1 if args.quick else 3
    epochs = 50 if args.quick else EPOCHS

    if args.tier == "all":
        run_all(
            no_of_cycles=cycles, seed=args.seed,
            output_dir=args.output_dir, epochs=epochs,
        )
    else:
        run_tier(
            args.tier, no_of_cycles=cycles, seed=args.seed,
            output_dir=args.output_dir, epochs=epochs,
        )
