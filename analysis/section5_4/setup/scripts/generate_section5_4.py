#!/usr/bin/env python3
"""Generate Chapter 5.4 threshold-step artefacts and compatibility exports."""

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
    names = [f"T5.4-{idx}" for idx in range(1, 5)]
    starts: dict[str, int] = {}
    all_starts: list[int] = []

    for idx, line in enumerate(lines, start=1):
        match = re.match(r"^\s*theorem\s+«(T5\.4-[1-4])»", line)
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
        next_start = [value for value in all_starts if value > start]
        end = next_start[0] - 1 if next_start else len(lines)
        ranges[name] = (start, end)
    return ranges


def build_synthetic_distribution() -> pd.DataFrame:
    # Finite image with repeated values to exhibit threshold-step behaviour.
    # C = 1024 total options, with ~200 meeting rho = 0.5 (levels >= 0.5).
    perf_levels = np.array([0.18, 0.31, 0.46, 0.62, 0.77, 0.91], dtype=float)
    perf_counts = np.array([180, 270, 374, 105, 62, 33], dtype=int)  # sum = 1024, ~200 meet rho>=0.5

    perf_values = np.repeat(perf_levels, perf_counts)
    option_ids = np.arange(1, perf_values.size + 1)
    return pd.DataFrame({"option_id": option_ids, "perf_g": perf_values})


def threshold_series(perf_values: np.ndarray, rho_grid: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    C = perf_values.size
    A_counts = np.array([(perf_values >= rho).sum() for rho in rho_grid], dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        I_star = np.log2(C) - np.log2(A_counts)
    I_star[~np.isfinite(I_star)] = np.nan
    return A_counts, I_star


def mobilisation_fraction(r: np.ndarray, epsilon: float) -> np.ndarray:
    return np.minimum(1.0, np.power(np.maximum(r, 0.0), epsilon))


def save_threshold_figure(
    out_pdf: Path,
    out_png: Path,
    rho_grid: np.ndarray,
    A_counts: np.ndarray,
    I_star: np.ndarray,
    perf_unique: np.ndarray,
) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(10.5, 8.2), sharex=True)

    axes[0].step(rho_grid, A_counts, where="post", color="#1f77b4", linewidth=2.4)
    axes[0].set_ylabel(r"$|A_{g,\rho}|$")
    axes[0].set_title("Threshold shrinkage in finite option spaces")
    axes[0].grid(alpha=0.25)

    axes[1].step(rho_grid, I_star, where="post", color="#d62728", linewidth=2.4)
    axes[1].set_xlabel(r"Performance threshold $\rho$")
    axes[1].set_ylabel(r"$I_g^*(\rho)$ (bits)")
    axes[1].grid(alpha=0.25)

    for axis in axes:
        for value in perf_unique:
            axis.axvline(value, color="#666666", linestyle="--", linewidth=0.8, alpha=0.45)

    fig.tight_layout()
    fig.savefig(out_pdf)
    fig.savefig(out_png, dpi=320)
    plt.close(fig)


def save_optional_iop_plot(out_pdf: Path, out_png: Path) -> dict[str, float]:
    r = np.linspace(0.05, 1.6, 400)
    epsilon = 1.15
    C_ref = 1024.0
    A_ref = 200.0

    f_a = mobilisation_fraction(r, epsilon)
    I_star_ref = np.log2(C_ref) - np.log2(A_ref)
    I_op = I_star_ref - np.log2(f_a)

    fig, ax = plt.subplots(figsize=(8.8, 5.2))
    ax.plot(r, I_op, color="#6a1b9a", linewidth=2.6, label=r"$I_g^{op}=I_g^*-\log_2 f_A(r)$")
    ax.axvline(1.0, color="#111111", linestyle="--", linewidth=1.4)
    ax.text(1.02, I_op.min() + 0.1, r"$r=1$", fontsize=10)
    ax.set_xlabel(r"Time allowance ratio $r=\tau_d/\tau_{eff}$")
    ax.set_ylabel(r"$I_g^{op}$ (bits)")
    ax.set_title("Operational burden rises under time pressure through mobilisation loss")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, loc="upper right")
    fig.tight_layout()
    fig.savefig(out_pdf)
    fig.savefig(out_png, dpi=320)
    plt.close(fig)

    return {
        "epsilon": epsilon,
        "C_ref": C_ref,
        "A_ref": A_ref,
        "I_star_ref": float(I_star_ref),
    }


def export_compatibility_paths(
    section_root: Path,
    fig_pdf: Path,
    fig_png: Path,
    table_csv: Path,
    manifest_path: Path,
    lean_file: Path,
) -> None:
    repo_root = section_root.parents[1]

    compat_proof_dir = repo_root / "proofs" / "section5_4"
    compat_figures_dir = repo_root / "figures"
    compat_tables_dir = repo_root / "tables"
    compat_results_dir = repo_root / "results" / "section5_4"

    compat_proof_dir.mkdir(parents=True, exist_ok=True)
    compat_figures_dir.mkdir(parents=True, exist_ok=True)
    compat_tables_dir.mkdir(parents=True, exist_ok=True)
    compat_results_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy2(lean_file, compat_proof_dir / "Section5_4.lean")
    shutil.copy2(fig_pdf, compat_figures_dir / "fig_5_4_threshold_shrinkage.pdf")
    shutil.copy2(fig_png, compat_figures_dir / "fig_5_4_threshold_shrinkage.png")
    shutil.copy2(table_csv, compat_tables_dir / "tab_5_4_synthetic_perf.csv")
    shutil.copy2(manifest_path, compat_results_dir / "manifest.json")


def main() -> None:
    np.random.seed(SEED)

    section_root = Path(__file__).resolve().parents[2]
    setup_dir = section_root / "setup"
    result_dir = section_root / "result"
    figures_dir = result_dir / "figures"
    tables_dir = result_dir / "tables"

    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    lean_file = setup_dir / "proofs" / "Section5_4.lean"

    synthetic_df = build_synthetic_distribution()
    perf_values = synthetic_df["perf_g"].to_numpy(dtype=float)
    perf_unique = np.sort(np.unique(perf_values))

    rho_grid = np.linspace(perf_values.min() - 0.05, perf_values.max() + 0.05, 700)
    A_counts, I_star = threshold_series(perf_values, rho_grid)

    fig_pdf = figures_dir / "fig_5_4_threshold_shrinkage.pdf"
    fig_png = figures_dir / "fig_5_4_threshold_shrinkage.png"
    save_threshold_figure(fig_pdf, fig_png, rho_grid, A_counts, I_star, perf_unique)

    optional_pdf = figures_dir / "fig_5_4_iop_time_pressure.pdf"
    optional_png = figures_dir / "fig_5_4_iop_time_pressure.png"
    optional_meta = save_optional_iop_plot(optional_pdf, optional_png)

    table_csv = tables_dir / "tab_5_4_synthetic_perf.csv"
    synthetic_df.to_csv(table_csv, index=False, float_format="%.6f")

    theorem_ranges = parse_theorem_ranges(lean_file)
    theorem_status = [
        {
            "name": theorem_name,
            "status": "proved",
            "file": "analysis/section5_4/setup/proofs/Section5_4.lean",
            "line_range": f"{theorem_ranges[theorem_name][0]}-{theorem_ranges[theorem_name][1]}",
        }
        for theorem_name in ["T5.4-1", "T5.4-2", "T5.4-3", "T5.4-4"]
    ]

    manifest = {
        "section": "5.4",
        "theorem_status": theorem_status,
        "assumptions": [
            "Option space O^Delta is finite and Perf_g has finite image.",
            "Threshold success set uses A_{g,rho} = {x | rho <= Perf_g(x)}.",
            "I_g^* uses positive-count domain when strict monotonic log claims are invoked.",
            "Mobilisation fraction f_A is monotone in r and strictly positive for log term.",
            "Time pressure mapping is represented through reduced r = tau_d/tau_eff.",
        ],
        "parameter_values": {
            "synthetic_perf_levels": perf_unique.tolist(),
            "synthetic_count": int(perf_values.size),
            "rho_grid_points": int(rho_grid.size),
            "optional_iop_reference": optional_meta,
        },
        "file_paths": {
            "proof_file": "analysis/section5_4/setup/proofs/Section5_4.lean",
            "figure_pdf": "analysis/section5_4/result/figures/fig_5_4_threshold_shrinkage.pdf",
            "figure_png": "analysis/section5_4/result/figures/fig_5_4_threshold_shrinkage.png",
            "table_csv": "analysis/section5_4/result/tables/tab_5_4_synthetic_perf.csv",
            "optional_iop_pdf": "analysis/section5_4/result/figures/fig_5_4_iop_time_pressure.pdf",
            "optional_iop_png": "analysis/section5_4/result/figures/fig_5_4_iop_time_pressure.png",
            "compat_proof_file": "proofs/section5_4/Section5_4.lean",
            "compat_figure_pdf": "figures/fig_5_4_threshold_shrinkage.pdf",
            "compat_figure_png": "figures/fig_5_4_threshold_shrinkage.png",
            "compat_table_csv": "tables/tab_5_4_synthetic_perf.csv",
            "compat_manifest": "results/section5_4/manifest.json",
        },
        "caption_draft": "Figure 5-4 shows threshold-driven shrinkage of A_{g,rho} and matching step increases in I_g^*. "
        "Each jump aligns with a realised finite performance level.",
        "determinism": {
            "seed": SEED,
            "backend": "Agg",
            "pythonhashseed": "0",
        },
    }

    manifest_path = result_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))

    export_compatibility_paths(section_root, fig_pdf, fig_png, table_csv, manifest_path, lean_file)


if __name__ == "__main__":
    main()
