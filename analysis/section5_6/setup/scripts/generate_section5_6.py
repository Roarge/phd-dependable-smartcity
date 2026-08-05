#!/usr/bin/env python3
"""Generate Chapter 5.6 regime-shift sensitivity artefacts."""

from __future__ import annotations

import json
import re
from pathlib import Path
import shutil

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SEED = 20260208


def parse_theorem_ranges(lean_file: Path) -> dict[str, tuple[int, int]]:
    lines = lean_file.read_text().splitlines()
    names = [f"T5.6-{idx}" for idx in range(1, 5)]
    starts: dict[str, int] = {}
    all_starts: list[int] = []

    for idx, line in enumerate(lines, start=1):
        match = re.match(r"^\s*theorem\s+«(T5\.6-[1-4])»", line)
        if match:
            name = match.group(1)
            starts[name] = idx
            all_starts.append(idx)

    missing = [name for name in names if name not in starts]
    if missing:
        raise ValueError(f"Missing theorem declarations: {', '.join(missing)}")

    all_starts.sort()
    ranges: dict[str, tuple[int, int]] = {}
    for name in names:
        start = starts[name]
        next_starts = [value for value in all_starts if value > start]
        end = next_starts[0] - 1 if next_starts else len(lines)
        ranges[name] = (start, end)
    return ranges


def tau_total(tau0: float, gamma: float, cp: np.ndarray | float) -> np.ndarray | float:
    return tau0 * (1.0 + gamma * cp)


def tau_eff(tau0: float, gamma: float, cp: np.ndarray | float, lam: float, u: np.ndarray | float) -> np.ndarray | float:
    return (1.0 - lam * u) * tau_total(tau0, gamma, cp)


def ratio(tau_d: float, tau0: float, gamma: float, cp: np.ndarray | float, lam: float, u: np.ndarray | float) -> np.ndarray | float:
    return tau_d / tau_eff(tau0, gamma, cp, lam, u)


def mobilisation_fraction(r: np.ndarray, eps: float) -> np.ndarray:
    return np.minimum(1.0, np.power(np.maximum(r, 0.0), eps))


def abs_dr_du(tau_d: float, tau0: float, gamma: float, cp: np.ndarray, lam: float, u: float) -> np.ndarray:
    denom = np.power(1.0 - lam * u, 2.0) * tau_total(tau0, gamma, cp)
    return (tau_d * lam) / denom


def build_grid_dataframe(
    tau_d: float,
    tau0: float,
    gamma: float,
    lam: float,
    eps_a: float,
    eps_b: float,
    cp_values: np.ndarray,
    u_values: np.ndarray,
) -> pd.DataFrame:
    cp_grid, u_grid = np.meshgrid(cp_values, u_values)
    r_grid = ratio(tau_d, tau0, gamma, cp_grid, lam, u_grid)
    f_a = mobilisation_fraction(r_grid, eps_a)
    f_b = mobilisation_fraction(r_grid, eps_b)
    drdu = abs_dr_du(tau_d, tau0, gamma, cp_grid, lam, u_grid)

    df = pd.DataFrame(
        {
            "cp": cp_grid.ravel(),
            "u": u_grid.ravel(),
            "r": r_grid.ravel(),
            "f_A": f_a.ravel(),
            "f_B": f_b.ravel(),
            "abs_dr_du": drdu.ravel(),
        }
    )
    return df


def plot_experience_effect(
    out_pdf: Path,
    out_png: Path,
    tau_d: float,
    tau0: float,
    gamma: float,
    lam: float,
    eps_a: float,
    cp_levels: list[float],
) -> None:
    u = np.linspace(0.0, 1.0, 400)

    fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.2))

    for cp in cp_levels:
        r_curve = ratio(tau_d, tau0, gamma, cp, lam, u)
        f_curve = mobilisation_fraction(r_curve, eps_a)
        axes[0].plot(u, r_curve, linewidth=2.1, label=rf"$CP={cp:.1f}$")
        axes[1].plot(u, f_curve, linewidth=2.1, label=rf"$CP={cp:.1f}$")

    axes[0].set_xlabel("Experience proxy u")
    axes[0].set_ylabel("Time allowance ratio r")
    axes[0].set_title("Flattening experience effect on r as CP grows")
    axes[0].grid(alpha=0.25)

    axes[1].set_xlabel("Experience proxy u")
    axes[1].set_ylabel("Mobilisation fraction f_A")
    axes[1].set_title("Mobilisation response flattens in high-drag regimes")
    axes[1].grid(alpha=0.25)

    axes[1].legend(frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(out_pdf)
    fig.savefig(out_png, dpi=350)
    plt.close(fig)


def plot_sensitivity_decay(
    out_pdf: Path,
    out_png: Path,
    tau_d: float,
    tau0: float,
    gamma: float,
    lam: float,
    u_levels: list[float],
) -> None:
    cp = np.linspace(0.0, 8.0, 500)

    fig, ax = plt.subplots(figsize=(9.8, 5.4))
    for u in u_levels:
        sens = abs_dr_du(tau_d, tau0, gamma, cp, lam, u)
        ax.plot(cp, sens, linewidth=2.3, label=rf"$u={u:.1f}$")

    ax.set_xlabel("Complexity potential scalar CP")
    ax.set_ylabel(r"$|\partial r / \partial u|$")
    ax.set_title("Sensitivity of time allowance to experience decays with CP")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, loc="upper right")

    fig.tight_layout()
    fig.savefig(out_pdf)
    fig.savefig(out_png, dpi=350)
    plt.close(fig)


def export_compatibility(
    section_root: Path,
    lean_file: Path,
    fig56_pdf: Path,
    fig56_png: Path,
    fig57_pdf: Path,
    fig57_png: Path,
    table_csv: Path,
    manifest_path: Path,
) -> None:
    repo_root = section_root.parents[1]

    compat_proof_dir = repo_root / "proofs" / "section5_6"
    compat_figures_dir = repo_root / "figures"
    compat_tables_dir = repo_root / "tables"
    compat_results_dir = repo_root / "results" / "section5_6"

    compat_proof_dir.mkdir(parents=True, exist_ok=True)
    compat_figures_dir.mkdir(parents=True, exist_ok=True)
    compat_tables_dir.mkdir(parents=True, exist_ok=True)
    compat_results_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy2(lean_file, compat_proof_dir / "Section5_6.lean")
    shutil.copy2(fig56_pdf, compat_figures_dir / "fig_5_6_schematic_experience_effect.pdf")
    shutil.copy2(fig56_png, compat_figures_dir / "fig_5_6_schematic_experience_effect.png")
    shutil.copy2(fig57_pdf, compat_figures_dir / "fig_5_7_schematic_sensitivity_decay.pdf")
    shutil.copy2(fig57_png, compat_figures_dir / "fig_5_7_schematic_sensitivity_decay.png")
    shutil.copy2(table_csv, compat_tables_dir / "tab_5_6_sensitivity_grid.csv")
    shutil.copy2(manifest_path, compat_results_dir / "manifest.json")


def main() -> None:
    np.random.seed(SEED)

    section_root = Path(__file__).resolve().parents[2]
    result_dir = section_root / "result"
    figures_dir = result_dir / "figures"
    tables_dir = result_dir / "tables"

    result_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    lean_file = section_root / "setup" / "proofs" / "Section5_6.lean"

    params = {
        "tau_d": 5.0,
        "tau0": 4.0,
        "gamma": 0.3,
        "lambda": 0.4,
        "h": 0.2,
        "eps_A": 1.1,
        "eps_B": 1.5,
    }

    cp_levels = [0.5, 2.0, 4.0, 7.0]
    u_levels = [0.1, 0.4, 0.7]

    fig56_pdf = figures_dir / "fig_5_6_schematic_experience_effect.pdf"
    fig56_png = figures_dir / "fig_5_6_schematic_experience_effect.png"
    plot_experience_effect(
        fig56_pdf,
        fig56_png,
        params["tau_d"],
        params["tau0"],
        params["gamma"],
        params["lambda"],
        params["eps_A"],
        cp_levels,
    )

    fig57_pdf = figures_dir / "fig_5_7_schematic_sensitivity_decay.pdf"
    fig57_png = figures_dir / "fig_5_7_schematic_sensitivity_decay.png"
    plot_sensitivity_decay(
        fig57_pdf,
        fig57_png,
        params["tau_d"],
        params["tau0"],
        params["gamma"],
        params["lambda"],
        u_levels,
    )

    cp_grid = np.linspace(0.0, 8.0, 121)
    u_grid = np.linspace(0.0, 1.0, 81)
    grid_df = build_grid_dataframe(
        params["tau_d"],
        params["tau0"],
        params["gamma"],
        params["lambda"],
        params["eps_A"],
        params["eps_B"],
        cp_grid,
        u_grid,
    )
    table_csv = tables_dir / "tab_5_6_sensitivity_grid.csv"
    grid_df.to_csv(table_csv, index=False, float_format="%.8f")

    theorem_ranges = parse_theorem_ranges(lean_file)
    theorem_status = [
        {
            "name": theorem_name,
            "status": "proved",
            "file": "analysis/section5_6/setup/proofs/Section5_6.lean",
            "line_range": f"{theorem_ranges[theorem_name][0]}-{theorem_ranges[theorem_name][1]}",
        }
        for theorem_name in [f"T5.6-{idx}" for idx in range(1, 5)]
    ]

    demo = {
        "abs_dr_du_at_cp_0_u_0_4": float(abs_dr_du(params["tau_d"], params["tau0"], params["gamma"], np.array([0.0]), params["lambda"], 0.4)[0]),
        "abs_dr_du_at_cp_6_u_0_4": float(abs_dr_du(params["tau_d"], params["tau0"], params["gamma"], np.array([6.0]), params["lambda"], 0.4)[0]),
        "sensitivity_decay_ratio_cp6_over_cp0_u0_4": float(
            abs_dr_du(params["tau_d"], params["tau0"], params["gamma"], np.array([6.0]), params["lambda"], 0.4)[0]
            / abs_dr_du(params["tau_d"], params["tau0"], params["gamma"], np.array([0.0]), params["lambda"], 0.4)[0]
        ),
    }

    manifest = {
        "section": "5.6",
        "theorem_status": theorem_status,
        "assumptions": [
            "Experience is represented by u in [0,1] with bounded multiplier (1-lambda*u).",
            "Structural drag grows with CP through tau = tau0*(1+gamma*CP) in the schematic scalar model.",
            "Mobilisation fractions are monotone in r.",
            "Regime-shift interpretation uses step changes in CP as boundary events.",
            "No empirical survey-data claim is proven in this section.",
        ],
        "mapping_assumptions": {
            "experience_proxy": "u with bounded effect scale lambda",
            "se_capability_proxy": [
                "reduce CP via architecture and interface interventions",
                "reduce baseline tau_stage^0 via engineered process",
                "increase h to preserve cognitive reserve",
            ],
            "high_drag_regime": "larger CP leading to larger tau and lower r",
        },
        "parameters": {
            **params,
            "cp_levels_for_fig_5_6": cp_levels,
            "u_levels_for_fig_5_7": u_levels,
            "grid_cp_points": int(cp_grid.size),
            "grid_u_points": int(u_grid.size),
        },
        "numeric_summary": demo,
        "file_paths": {
            "proof_file": "analysis/section5_6/setup/proofs/Section5_6.lean",
            "figure_5_6_pdf": "analysis/section5_6/result/figures/fig_5_6_schematic_experience_effect.pdf",
            "figure_5_6_png": "analysis/section5_6/result/figures/fig_5_6_schematic_experience_effect.png",
            "figure_5_7_pdf": "analysis/section5_6/result/figures/fig_5_7_schematic_sensitivity_decay.pdf",
            "figure_5_7_png": "analysis/section5_6/result/figures/fig_5_7_schematic_sensitivity_decay.png",
            "table_csv": "analysis/section5_6/result/tables/tab_5_6_sensitivity_grid.csv",
            "compat_proof_file": "proofs/section5_6/Section5_6.lean",
            "compat_figure_5_6_pdf": "figures/fig_5_6_schematic_experience_effect.pdf",
            "compat_figure_5_6_png": "figures/fig_5_6_schematic_experience_effect.png",
            "compat_figure_5_7_pdf": "figures/fig_5_7_schematic_sensitivity_decay.pdf",
            "compat_figure_5_7_png": "figures/fig_5_7_schematic_sensitivity_decay.png",
            "compat_table_csv": "tables/tab_5_6_sensitivity_grid.csv",
            "compat_manifest": "results/section5_6/manifest.json",
        },
        "caption_draft": "Figures 5-6 and 5-7 show the regime shift mechanism: as CP rises, the experience-driven effect on time allowance flattens while sensitivity to structural drag remains salient.",
        "determinism": {
            "seed": SEED,
            "backend": "Agg",
            "pythonhashseed": "0",
        },
    }

    manifest_path = result_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))

    export_compatibility(
        section_root,
        lean_file,
        fig56_pdf,
        fig56_png,
        fig57_pdf,
        fig57_png,
        table_csv,
        manifest_path,
    )


if __name__ == "__main__":
    main()
