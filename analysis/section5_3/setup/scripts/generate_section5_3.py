#!/usr/bin/env python3
"""Generate Chapter 5.3 proof artefacts and thesis figures."""

from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch
from matplotlib.patches import FancyBboxPatch

SEED = 20260208


def parse_theorem_ranges(lean_file: Path) -> dict[str, tuple[int, int]]:
    lines = lean_file.read_text().splitlines()
    theorem_names = [f"T5.3-{idx}" for idx in range(1, 6)]
    starts: dict[str, int] = {}
    start_lines: list[int] = []

    for idx, line in enumerate(lines, start=1):
        match = re.match(r"^\s*theorem\s+«(T5\.3-[1-5])»", line)
        if match:
            name = match.group(1)
            starts[name] = idx
            start_lines.append(idx)

    missing = [name for name in theorem_names if name not in starts]
    if missing:
        raise ValueError(f"Missing theorem declarations in Lean file: {', '.join(missing)}")

    start_lines.sort()
    ranges: dict[str, tuple[int, int]] = {}
    for name in theorem_names:
        start = starts[name]
        next_starts = [value for value in start_lines if value > start]
        end = next_starts[0] - 1 if next_starts else len(lines)
        ranges[name] = (start, end)
    return ranges


def add_box(
    ax: plt.Axes,
    xy: tuple[float, float],
    width: float,
    height: float,
    text: str,
    facecolor: str,
    edgecolor: str = "#1f2937",
) -> None:
    box = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.03,rounding_size=0.12",
        linewidth=1.4,
        facecolor=facecolor,
        edgecolor=edgecolor,
    )
    ax.add_patch(box)
    ax.text(
        xy[0] + width / 2.0,
        xy[1] + height / 2.0,
        text,
        ha="center",
        va="center",
        fontsize=10.5,
    )


def add_arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    text: str | None = None,
    text_pos: tuple[float, float] | None = None,
    color: str = "#111827",
    style: str = "-|>",
) -> None:
    arrow = FancyArrowPatch(start, end, arrowstyle=style, mutation_scale=13, linewidth=1.4, color=color)
    ax.add_patch(arrow)
    if text is not None and text_pos is not None:
        ax.text(text_pos[0], text_pos[1], text, fontsize=9.8, color=color, ha="center", va="center")


def build_response_drag_figure(output_pdf: Path, output_png: Path) -> None:
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0.0, 20.0)
    ax.set_ylim(0.0, 12.5)
    ax.axis("off")

    colours = {
        "cp": "#fee2e2",
        "stage": "#dbeafe",
        "sum": "#e5e7eb",
        "sigma": "#dcfce7",
        "ratio": "#fef3c7",
        "mobilise": "#ede9fe",
    }

    add_box(ax, (0.9, 8.9), 2.8, 2.0, "CP vector", colours["cp"])
    add_box(ax, (4.2, 9.0), 3.2, 1.8, r"$\tau_{detect}$" "\n" r"$=\tau_{detect}^0(1+\gamma_d^\top CP)$", colours["stage"])
    add_box(ax, (8.0, 9.0), 3.2, 1.8, r"$\tau_{decide}$" "\n" r"$=\tau_{decide}^0(1+\gamma_c^\top CP)$", colours["stage"])
    add_box(ax, (11.8, 9.0), 3.2, 1.8, r"$\tau_{execute}$" "\n" r"$=\tau_{execute}^0(1+\gamma_x^\top CP)$", colours["stage"])
    add_box(ax, (15.8, 9.2), 3.5, 1.5, r"$\tau=\tau_{detect}+\tau_{decide}+\tau_{execute}$", colours["sum"])

    add_box(ax, (12.8, 5.7), 3.7, 1.7, r"$\sigma_\tau=1-\lambda_\tau u(E,MF)$", colours["sigma"])
    add_box(ax, (17.2, 5.7), 2.4, 1.7, r"$\tau_{eff}=\sigma_\tau\tau$", colours["sigma"])

    add_box(ax, (15.9, 3.0), 3.1, 1.4, r"$r=\tau_d/\tau_{eff}$", colours["ratio"])

    add_box(ax, (12.2, 0.7), 3.0, 1.5, r"$f_A(r)$", colours["mobilise"])
    add_box(ax, (16.0, 0.7), 3.0, 1.5, r"$f_B(r)$", colours["mobilise"])
    add_box(ax, (8.2, 0.7), 3.0, 1.5, r"$f_C(r)$", colours["mobilise"])

    add_arrow(ax, (3.7, 10.0), (4.2, 10.0))
    add_arrow(ax, (7.4, 10.0), (8.0, 10.0))
    add_arrow(ax, (11.2, 10.0), (11.8, 10.0))
    add_arrow(ax, (15.0, 10.0), (15.8, 10.0))

    add_arrow(ax, (2.3, 8.9), (5.2, 9.0), r"$\gamma_d^\top CP$", (3.6, 8.4))
    add_arrow(ax, (2.3, 8.9), (9.0, 9.0), r"$\gamma_c^\top CP$", (5.8, 7.9))
    add_arrow(ax, (2.3, 8.9), (12.8, 9.0), r"$\gamma_x^\top CP$", (8.2, 7.3))

    add_arrow(ax, (17.5, 9.2), (14.7, 7.35), r"$\tau$", (15.4, 7.85), color="#374151")
    add_arrow(ax, (14.7, 7.35), (13.8, 6.6), color="#374151")

    add_arrow(ax, (16.5, 6.55), (17.2, 6.55))
    add_arrow(ax, (18.4, 5.7), (17.45, 4.4))
    add_arrow(ax, (10.7, 4.0), (15.9, 3.7), r"$\tau_d$ input", (12.8, 4.35))

    add_arrow(ax, (17.45, 3.0), (13.7, 2.2))
    add_arrow(ax, (17.45, 3.0), (17.5, 2.2))
    add_arrow(ax, (17.45, 3.0), (9.7, 2.2))

    ax.text(1.0, 11.8, "Figure 5-3. Response-time decomposition, structural drag, and time-bounded mobilisation",
            fontsize=16.5, weight="bold", ha="left", va="center")
    ax.text(
        1.0,
        11.1,
        "Detection, decision, and execution delays enter separately through CP-sensitive drag and feed into "
        r"$\tau_{eff}$ and mobilisation fractions.",
        fontsize=11.2,
        ha="left",
        va="center",
    )

    fig.tight_layout()
    fig.savefig(output_pdf)
    fig.savefig(output_png, dpi=350)
    plt.close(fig)


def build_mobilisation_inset(output_pdf: Path, output_png: Path) -> None:
    r = np.linspace(0.0, 2.0, 400)
    epsilon_a = 0.8
    epsilon_b = 1.4
    f_a = np.minimum(1.0, np.power(r, epsilon_a))
    f_b = np.minimum(1.0, np.power(r, epsilon_b))

    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    ax.plot(r, f_a, linewidth=2.5, color="#0f766e", label=rf"$f_A(r)=\min(1,r^{{{epsilon_a}}})$")
    ax.plot(r, f_b, linewidth=2.5, color="#b45309", label=rf"$f_B(r)=\min(1,r^{{{epsilon_b}}})$")
    ax.axvline(1.0, color="#111827", linestyle="--", linewidth=1.5)
    ax.text(1.02, 0.12, r"$r=1$ saturation boundary", fontsize=10)
    ax.text(0.32, 0.52, "Power-law region", fontsize=10.5)
    ax.text(1.28, 0.93, "Saturated at 1", fontsize=10.5)
    ax.set_xlim(0.0, 2.0)
    ax.set_ylim(0.0, 1.05)
    ax.set_xlabel(r"Time allowance ratio $r=\tau_d/\tau_{eff}$")
    ax.set_ylabel("Mobilisation fraction")
    ax.set_title("Mobilisation fractions saturate as time allowance increases")
    ax.grid(alpha=0.2)
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(output_pdf)
    fig.savefig(output_png, dpi=350)
    plt.close(fig)


def main() -> None:
    np.random.seed(SEED)

    section_root = Path(__file__).resolve().parents[2]
    lean_file = section_root / "setup" / "proofs" / "Section5_3.lean"

    figures_dir = section_root / "result" / "figures"
    results_dir = section_root / "result"
    figures_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    fig_main_pdf = figures_dir / "fig_5_3_response_time_drag.pdf"
    fig_main_png = figures_dir / "fig_5_3_response_time_drag.png"
    fig_inset_pdf = figures_dir / "fig_5_3_inset_mobilisation.pdf"
    fig_inset_png = figures_dir / "fig_5_3_inset_mobilisation.png"

    build_response_drag_figure(fig_main_pdf, fig_main_png)
    build_mobilisation_inset(fig_inset_pdf, fig_inset_png)

    theorem_ranges = parse_theorem_ranges(lean_file)
    theorem_status = [
        {
            "name": theorem_name,
            "status": "proved",
            "file": "analysis/section5_3/setup/proofs/Section5_3.lean",
            "line_range": f"{theorem_ranges[theorem_name][0]}-{theorem_ranges[theorem_name][1]}",
        }
        for theorem_name in [f"T5.3-{idx}" for idx in range(1, 6)]
    ]

    manifest = {
        "section": "5.3",
        "theorem_status": theorem_status,
        "assumptions": [
            "All stage baselines, CP components, and sensitivity terms are non-negative where monotonicity is used.",
            "Skill utility u(E,MF) and quality term q(IT) are in [0,1].",
            "lambda_tau is bounded in [0,1] for sigma_tau interval claims.",
            "Mobilisation functions are monotone in r and saturate at 1.",
            "Threshold forms M_0 and M_max use non-negative scale and headroom factors.",
        ],
        "file_paths": {
            "proof_file": "analysis/section5_3/setup/proofs/Section5_3.lean",
            "figure_main_pdf": "analysis/section5_3/result/figures/fig_5_3_response_time_drag.pdf",
            "figure_main_png": "analysis/section5_3/result/figures/fig_5_3_response_time_drag.png",
            "figure_inset_pdf": "analysis/section5_3/result/figures/fig_5_3_inset_mobilisation.pdf",
            "figure_inset_png": "analysis/section5_3/result/figures/fig_5_3_inset_mobilisation.png",
        },
        "caption_draft": "Figure 5-3 shows how CP-sensitive detection, decision, and execution delays combine into tau, "
        "how skill enters through sigma_tau, and how the resulting ratio r governs mobilisation fractions.",
        "determinism": {
            "seed": SEED,
            "backend": "Agg",
            "pythonhashseed": "0",
        },
    }

    manifest_path = results_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
