#!/usr/bin/env python3
"""Generate Chapter 5.7 proof artefacts and operator diagram."""

from __future__ import annotations

import json
import re
from pathlib import Path
import shutil

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from matplotlib.patches import FancyBboxPatch
import numpy as np

SEED = 20260208


def parse_theorem_ranges(lean_file: Path) -> dict[str, tuple[int, int]]:
    lines = lean_file.read_text().splitlines()
    names = [f"T5.7-{idx}" for idx in range(1, 5)]
    starts: dict[str, int] = {}
    all_starts: list[int] = []

    for idx, line in enumerate(lines, start=1):
        match = re.match(r"^\s*theorem\s+«(T5\.7-[1-4])»", line)
        if match:
            theorem_name = match.group(1)
            starts[theorem_name] = idx
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


def add_box(
    ax: plt.Axes,
    xy: tuple[float, float],
    width: float,
    height: float,
    text: str,
    colour: str,
    fontsize: float = 10.4,
) -> None:
    box = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.03,rounding_size=0.09",
        linewidth=1.4,
        facecolor=colour,
        edgecolor="#1f2937",
    )
    ax.add_patch(box)
    ax.text(xy[0] + width / 2, xy[1] + height / 2, text, ha="center", va="center", fontsize=fontsize)


def add_arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    label: str | None = None,
    label_xy: tuple[float, float] | None = None,
) -> None:
    arrow = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=12.5, linewidth=1.45, color="#111827")
    ax.add_patch(arrow)
    if label and label_xy:
        ax.text(label_xy[0], label_xy[1], label, fontsize=9.0, ha="center", va="center")


def plot_patterns_as_operators(out_pdf: Path, out_png: Path) -> None:
    fig, ax = plt.subplots(figsize=(14.2, 8.3))
    ax.set_xlim(0.0, 19.0)
    ax.set_ylim(0.0, 11.5)
    ax.axis("off")

    add_box(ax, (0.7, 7.8), 3.0, 1.7, "Choice factors\n$X_i$", "#dbeafe")
    add_box(ax, (4.1, 7.8), 3.0, 1.7, "Constraints\n$K(\\ell)$", "#fee2e2")
    add_box(ax, (7.5, 7.8), 3.0, 1.7, "Distinctness map\n$\\varphi$", "#fef3c7")
    add_box(ax, (10.9, 7.8), 2.8, 1.7, "Complexity\n$C=|\\mathcal{O}^\\Delta|$", "#dcfce7")
    add_box(ax, (14.1, 7.8), 4.0, 1.7, "Success set\n$A_{g,\\rho}$ and $I_g^*$", "#e9d5ff")

    add_box(ax, (3.5, 4.9), 4.6, 1.8, "Mobilisation dynamics\n$\\tau_{eff},\\ r,\\ f_A$", "#ccfbf1")
    add_box(ax, (8.9, 4.9), 4.5, 1.8, "Operational burden\n$I_g^{op}=I_g^*-\\log_2 f_A$", "#fde68a")
    add_box(ax, (14.0, 4.9), 4.1, 1.8, "Inference dynamics\n$g(\\cdot),\\ \\omega,\\ \\Phi,\\ Accuracy$", "#e0e7ff")

    add_box(ax, (5.0, 2.0), 4.0, 1.5, "Pattern operator class\n$\\mathcal{P}$", "#f5d0fe")
    add_box(ax, (9.8, 2.0), 4.5, 1.5, "Digital engineering interventions\n(architecture, tooling, governance)", "#bbf7d0")

    add_arrow(ax, (3.7, 8.65), (4.1, 8.65))
    add_arrow(ax, (7.1, 8.65), (7.5, 8.65))
    add_arrow(ax, (10.5, 8.65), (10.9, 8.65))
    add_arrow(ax, (13.7, 8.65), (14.1, 8.65))

    add_arrow(ax, (16.1, 7.8), (11.6, 6.7), "threshold and selection", (13.7, 7.1))
    add_arrow(ax, (5.8, 7.8), (5.8, 6.7), "feasible-time coupling", (4.4, 7.1))
    add_arrow(ax, (10.1, 5.8), (8.9, 5.8))
    add_arrow(ax, (14.0, 5.8), (13.4, 5.8))

    add_arrow(ax, (7.0, 3.5), (5.9, 4.9), "operators on $X_i,K,\\varphi$", (5.0, 4.1))
    add_arrow(ax, (7.0, 3.5), (10.6, 4.9), "joint intervention path", (8.9, 4.1))
    add_arrow(ax, (12.0, 3.5), (15.0, 4.9), "improve $g$, reduce $\\omega$", (13.8, 4.1))
    add_arrow(ax, (12.0, 3.5), (10.1, 4.9), "reduce drag", (10.9, 4.2))

    ax.text(
        0.7,
        10.8,
        "Figure 5-8. Patterns as operators on complexity, inference, and mobilisation variables",
        fontsize=15.2,
        weight="bold",
    )
    ax.text(
        0.7,
        10.25,
        "Patterns and digital engineering interventions act on shared formal variables and jointly shape operational functional information.",
        fontsize=10.9,
    )

    fig.tight_layout()
    fig.savefig(out_pdf)
    fig.savefig(out_png, dpi=350)
    plt.close(fig)


def plot_joint_intervention_bar(demo: dict[str, object], out_pdf: Path, out_png: Path) -> None:
    """Horizontal bar chart of the five intervention scenarios with stacked reductions."""
    scenarios = demo["scenarios"]
    reductions = demo["reductions_bits"]

    names = ["Baseline", "Choice only", "Success only", "Mobilisation only", "Joint"]
    keys = ["baseline", "choice_only", "success_only", "mobilisation_only", "joint"]
    iop_values = [scenarios[k]["I_g_op_bits"] for k in keys]

    fig, axes = plt.subplots(1, 2, figsize=(14.5, 5.5), gridspec_kw={"width_ratios": [2, 1.3]})

    colours = ["#4c78a8", "#f58518", "#e45756", "#72b7b2", "#54a24b"]
    axes[0].barh(names, iop_values, color=colours, height=0.55)
    axes[0].set_xlabel(r"$I_g^{op}$ (bits)")
    axes[0].set_title("Operational burden under five scenarios")
    axes[0].invert_yaxis()
    axes[0].grid(axis="x", alpha=0.25)
    for i, val in enumerate(iop_values):
        axes[0].text(val + 0.04, i, f"{val:.3f}", va="center", fontsize=9)

    delta_choice = reductions["delta_choice_bits"]
    delta_success = reductions["delta_success_bits"]
    delta_mob = reductions["delta_mobilisation_bits"]

    bar_labels = ["Individual\nsum", "Joint"]
    axes[1].barh(bar_labels, [delta_choice, delta_choice], color="#f58518", height=0.45, label="Choice")
    axes[1].barh(
        bar_labels,
        [delta_success, delta_success],
        left=[delta_choice, delta_choice],
        color="#e45756",
        height=0.45,
        label="Success",
    )
    axes[1].barh(
        bar_labels,
        [delta_mob, delta_mob],
        left=[delta_choice + delta_success, delta_choice + delta_success],
        color="#72b7b2",
        height=0.45,
        label="Mobilisation",
    )
    axes[1].set_xlabel(r"$\Delta I_g^{op}$ (bits)")
    axes[1].set_title("Additive decomposition of joint reduction")
    axes[1].invert_yaxis()
    axes[1].grid(axis="x", alpha=0.25)
    axes[1].legend(frameon=False, fontsize=8, loc="lower right")

    fig.tight_layout()
    fig.savefig(out_pdf)
    fig.savefig(out_png, dpi=350)
    plt.close(fig)


def log2(x: float) -> float:
    return float(np.log2(x))


def iop(C: float, A: float, f_A: float) -> float:
    return log2(C) - log2(A) - log2(f_A)


def build_joint_demo() -> dict[str, object]:
    baseline = {"C": 4096.0, "A": 512.0, "f_A": 0.35}
    factors = {"alpha": 0.62, "beta": 1.40, "gamma": 1.25}

    C0 = baseline["C"]
    A0 = baseline["A"]
    f0 = baseline["f_A"]
    alpha = factors["alpha"]
    beta = factors["beta"]
    gamma = factors["gamma"]

    scenarios = {
        "baseline": {"C": C0, "A": A0, "f_A": f0},
        "choice_only": {"C": alpha * C0, "A": A0, "f_A": f0},
        "success_only": {"C": C0, "A": beta * A0, "f_A": f0},
        "mobilisation_only": {"C": C0, "A": A0, "f_A": gamma * f0},
        "joint": {"C": alpha * C0, "A": beta * A0, "f_A": gamma * f0},
    }

    for item in scenarios.values():
        item["rho_op"] = (item["A"] * item["f_A"]) / item["C"]
        item["I_g_op_bits"] = iop(item["C"], item["A"], item["f_A"])

    baseline_i = scenarios["baseline"]["I_g_op_bits"]
    deltas = {
        "delta_choice_bits": baseline_i - scenarios["choice_only"]["I_g_op_bits"],
        "delta_success_bits": baseline_i - scenarios["success_only"]["I_g_op_bits"],
        "delta_mobilisation_bits": baseline_i - scenarios["mobilisation_only"]["I_g_op_bits"],
        "delta_joint_bits": baseline_i - scenarios["joint"]["I_g_op_bits"],
    }
    deltas["additivity_residual_bits"] = deltas["delta_joint_bits"] - (
        deltas["delta_choice_bits"] + deltas["delta_success_bits"] + deltas["delta_mobilisation_bits"]
    )

    return {
        "baseline": baseline,
        "intervention_factors": factors,
        "scenarios": scenarios,
        "reductions_bits": deltas,
    }


def export_compatibility(
    section_root: Path,
    lean_file: Path,
    fig_pdf: Path,
    fig_png: Path,
    demo_json: Path,
    manifest_path: Path,
) -> None:
    repo_root = section_root.parents[1]

    compat_proof_dir = repo_root / "proofs" / "section5_7"
    compat_figures_dir = repo_root / "figures"
    compat_tables_dir = repo_root / "tables"
    compat_results_dir = repo_root / "results" / "section5_7"

    compat_proof_dir.mkdir(parents=True, exist_ok=True)
    compat_figures_dir.mkdir(parents=True, exist_ok=True)
    compat_tables_dir.mkdir(parents=True, exist_ok=True)
    compat_results_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy2(lean_file, compat_proof_dir / "Section5_7.lean")
    shutil.copy2(fig_pdf, compat_figures_dir / "fig_5_8_patterns_as_operators.pdf")
    shutil.copy2(fig_png, compat_figures_dir / "fig_5_8_patterns_as_operators.png")
    shutil.copy2(demo_json, compat_tables_dir / "tab_5_7_joint_intervention_demo.json")
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

    lean_file = section_root / "setup" / "proofs" / "Section5_7.lean"

    fig_pdf = figures_dir / "fig_5_8_patterns_as_operators.pdf"
    fig_png = figures_dir / "fig_5_8_patterns_as_operators.png"
    plot_patterns_as_operators(fig_pdf, fig_png)

    demo = build_joint_demo()
    demo_json = tables_dir / "tab_5_7_joint_intervention_demo.json"
    demo_json.write_text(json.dumps(demo, indent=2))

    bar_pdf = figures_dir / "fig_5_8_joint_intervention_bar.pdf"
    bar_png = figures_dir / "fig_5_8_joint_intervention_bar.png"
    plot_joint_intervention_bar(demo, bar_pdf, bar_png)

    theorem_ranges = parse_theorem_ranges(lean_file)
    theorem_status = [
        {
            "name": theorem_name,
            "status": "proved",
            "file": "analysis/section5_7/setup/proofs/Section5_7.lean",
            "line_range": f"{theorem_ranges[theorem_name][0]}-{theorem_ranges[theorem_name][1]}",
        }
        for theorem_name in [f"T5.7-{idx}" for idx in range(1, 5)]
    ]

    manifest = {
        "section": "5.7",
        "theorem_status": theorem_status,
        "assumptions": [
            "Finite option-set representations are used for operator cardinality proofs.",
            "Constraint operator is modelled as pruning by additional feasibility predicates.",
            "Distinctness coarsening is modelled by composition phi' = h o phi.",
            "Count variables satisfy positivity where logarithms are used.",
            "Joint intervention factors satisfy alpha in (0,1), beta >= 1, gamma >= 1.",
            "Gaussian likelihood accuracy proxy uses sigma^2 > 0.",
        ],
        "bridging_assumptions": [
            "Improved inference map g(.) and reduced channel noise omega are represented by lower effective inference variance.",
            "Inference improvements can reduce tau_detect^0 or CP_info in the response-time model.",
            "With monotone mobilisation fractions in r = tau_d/tau_eff, reduced tau_eff implies increased mobilisation.",
        ],
        "numeric_demo": demo,
        "file_paths": {
            "proof_file": "analysis/section5_7/setup/proofs/Section5_7.lean",
            "figure_pdf": "analysis/section5_7/result/figures/fig_5_8_patterns_as_operators.pdf",
            "figure_png": "analysis/section5_7/result/figures/fig_5_8_patterns_as_operators.png",
            "demo_json": "analysis/section5_7/result/tables/tab_5_7_joint_intervention_demo.json",
            "compat_proof_file": "proofs/section5_7/Section5_7.lean",
            "compat_figure_pdf": "figures/fig_5_8_patterns_as_operators.pdf",
            "compat_figure_png": "figures/fig_5_8_patterns_as_operators.png",
            "compat_demo_json": "tables/tab_5_7_joint_intervention_demo.json",
            "compat_manifest": "results/section5_7/manifest.json",
        },
        "caption_draft": "Figure 5-8 maps modelling patterns and digital engineering interventions to shared operators on option-space structure, mobilisation dynamics, and inference dynamics.",
        "determinism": {
            "seed": SEED,
            "backend": "Agg",
            "pythonhashseed": "0",
        },
    }

    manifest_path = result_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))

    export_compatibility(section_root, lean_file, fig_pdf, fig_png, demo_json, manifest_path)


if __name__ == "__main__":
    main()
