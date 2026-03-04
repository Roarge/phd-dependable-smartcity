#!/usr/bin/env python3
"""
Reproduce the simulation results from:
  Kaufmann, R., Gupta, P. and Taylor, J. (2021).
  "An Active Inference Model of Collective Intelligence."
  Entropy, 23(7), 830.

Runs all four models (180 runs each) and generates Figures 7, 8, and 9.

Usage:
  python run_simulation.py              # Run all models, generate all figures
  python run_simulation.py --quick      # Quick test run (1 cycle instead of 3)
  python run_simulation.py --fig7-only  # Generate Figure 7 only (single run)
"""

import os
import sys
import argparse
import numpy as np

# Ensure we can import sibling modules when run as a script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aif_collective import (
    single_run, simulate_runs, CONDITIONS, ENV_SIZE,
    EPOCHS, MAX_SENSE_PROBABILITY,
)
from plotting import plot_figure7, plot_figure8, plot_figure9


def main():
    parser = argparse.ArgumentParser(
        description="Active Inference Collective Intelligence simulation"
    )
    parser.add_argument(
        "--quick", action="store_true",
        help="Quick test: 1 cycle (60 runs) instead of 3 (180 runs)",
    )
    parser.add_argument(
        "--fig7-only", action="store_true",
        help="Only generate Figure 7 (single run of Model 4)",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    parser.add_argument(
        "--output-dir", type=str, default=None,
        help="Directory for output figures (default: simulation/results/)",
    )
    args = parser.parse_args()

    # Deterministic execution
    np.random.seed(args.seed)

    # Output directory
    if args.output_dir:
        results_dir = args.output_dir
    else:
        results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
    os.makedirs(results_dir, exist_ok=True)

    print("=" * 60)
    print("Active Inference Model of Collective Intelligence")
    print("Kaufmann, Gupta & Taylor (2021), Entropy 23(7) 830")
    print("=" * 60)
    print()

    # ── Figure 7: Single run of Model 4 ──
    print("Generating Figure 7: Single run of Model 4...")
    np.random.seed(args.seed)  # Reset seed for reproducible single run
    shared_target = 15
    agents = single_run(
        shared_target,
        MAX_SENSE_PROBABILITY,
        CONDITIONS[4]['tom'],
        CONDITIONS[4]['alignment'],
        plot=True,
    )
    plot_figure7(
        agents, shared_target,
        save_path=os.path.join(results_dir, "figure7_single_run_model4.png"),
    )
    print()

    if args.fig7_only:
        print("Done (--fig7-only).")
        return

    # ── Run all four models ──
    no_of_cycles = 1 if args.quick else 3
    results = {}

    for model_num in [1, 2, 3, 4]:
        np.random.seed(args.seed)  # Same seed per model for comparability
        model, t_df, c_df, b_df, fe_df = simulate_runs(
            model=model_num,
            no_of_cycles=no_of_cycles,
        )
        results[model_num] = (model, t_df, c_df, b_df, fe_df)
        print()

    # ── Figure 8: Aggregate results ──
    print("Generating Figure 8: Aggregate simulation results...")
    plot_figure8(
        results,
        save_path=os.path.join(results_dir, "figure8_all_models.png"),
    )

    # ── Figure 9: System-level free energy ──
    print("Generating Figure 9: System-level free energy...")
    plot_figure9(
        results,
        save_path=os.path.join(results_dir, "figure9_system_free_energy.png"),
    )

    print()
    print("=" * 60)
    print(f"All figures saved to: {results_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
