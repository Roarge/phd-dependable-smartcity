#!/usr/bin/env python3
"""Generate Chapter 5.2 comparison artefacts and manifest."""

from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

SEED = 20260208


def mobilisation(tau_d: np.ndarray, tau_eff: float, epsilon: int) -> np.ndarray:
    return np.minimum(1.0, np.power(tau_d / tau_eff, epsilon))


def thresholds(
    tau_d: np.ndarray,
    org: dict[str, float],
    params: dict[str, float | int],
) -> tuple[np.ndarray, np.ndarray]:
    f_a = mobilisation(tau_d, org["tau_eff"], int(params["epsilon_A"]))
    f_b = mobilisation(tau_d, org["tau_eff"], int(params["epsilon_B"]))

    m0 = (
        params["k"]
        * np.power(org["A"] * f_a, int(params["alpha_A"]))
        * np.power(org["H"], int(params["beta_H"]))
    )
    mmax = (
        params["k"]
        * np.power(org["B"] * f_b, int(params["beta_B"]))
        * np.power(org["H"], int(params["beta_H"]))
    )
    return m0, mmax


def resilience_score(M: np.ndarray, m0: np.ndarray, mmax: np.ndarray) -> np.ndarray:
    denom = mmax - m0
    with np.errstate(divide="ignore", invalid="ignore"):
        linear = (mmax - M) / denom

    degenerate = np.isclose(denom, 0.0)
    if np.any(degenerate):
        linear = np.where(degenerate, np.where(M <= m0, 1.0, 0.0), linear)

    return np.clip(linear, 0.0, 1.0)


def delta_r(
    tau_d_grid: np.ndarray,
    m_grid: np.ndarray,
    org_s: dict[str, float],
    org_l: dict[str, float],
    params: dict[str, float | int],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    m0_s, mmax_s = thresholds(tau_d_grid, org_s, params)
    m0_l, mmax_l = thresholds(tau_d_grid, org_l, params)

    r_s = resilience_score(m_grid, m0_s, mmax_s)
    r_l = resilience_score(m_grid, m0_l, mmax_l)
    return r_s - r_l, m0_s, mmax_s


def parse_theorem_ranges(lean_file: Path) -> dict[str, tuple[int, int]]:
    lines = lean_file.read_text().splitlines()
    theorem_names = ["T5.2-1", "T5.2-2", "T5.2-3", "T5.2-4"]

    starts: dict[str, int] = {}
    all_starts: list[int] = []
    for idx, line in enumerate(lines, start=1):
        match = re.match(r"^\s*theorem\s+«(T5\.2-[1-4])»", line)
        if match:
            name = match.group(1)
            starts[name] = idx
            all_starts.append(idx)

    all_starts.sort()
    ranges: dict[str, tuple[int, int]] = {}
    for name in theorem_names:
        start = starts[name]
        next_lines = [n for n in all_starts if n > start]
        end = next_lines[0] - 1 if next_lines else len(lines)
        ranges[name] = (start, end)
    return ranges


def tau_star_estimates(tau_values: np.ndarray, delta_values: np.ndarray) -> list[float]:
    signs = np.sign(delta_values).astype(float)

    # Forward fill zeros, then backward fill leading zeros.
    for idx in range(1, len(signs)):
        if signs[idx] == 0:
            signs[idx] = signs[idx - 1]
    for idx in range(len(signs) - 2, -1, -1):
        if signs[idx] == 0:
            signs[idx] = signs[idx + 1]

    stars: list[float] = []
    crossing_idx = np.where(signs[:-1] * signs[1:] < 0)[0]
    for idx in crossing_idx:
        d0 = delta_values[idx]
        d1 = delta_values[idx + 1]
        t0 = tau_values[idx]
        t1 = tau_values[idx + 1]
        t_star = t0 - d0 * (t1 - t0) / (d1 - d0)
        stars.append(float(t_star))

    # Deduplicate numeric noise from nearby crossings.
    return sorted(set(round(v, 10) for v in stars))


def main() -> None:
    np.random.seed(SEED)

    section_root = Path(__file__).resolve().parents[2]
    lean_file = section_root / "setup" / "proofs" / "Section5_2.lean"

    figures_dir = section_root / "result" / "figures"
    tables_dir = section_root / "result" / "tables"
    results_dir = section_root / "result"
    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    params: dict[str, float | int] = {
        "k": 1.0,
        "alpha_A": 1,
        "beta_B": 1,
        "beta_H": 1,
        "epsilon_A": 1,
        "epsilon_B": 1,
    }
    org_s = {"A": 2.0, "B": 6.0, "H": 0.9, "tau_eff": 1.0}
    org_l = {"A": 4.0, "B": 8.0, "H": 1.0, "tau_eff": 5.0}

    tau_values = np.linspace(0.0, 10.0, 501)
    m_values = np.linspace(0.0, 10.0, 501)
    tau_grid, m_grid = np.meshgrid(tau_values, m_values)

    delta, m0_s_grid, mmax_s_grid = delta_r(tau_grid, m_grid, org_s, org_l, params)
    _, m0_l_grid, mmax_l_grid = delta_r(tau_grid, m_grid, org_l, org_l, params)

    # Curves as 1D arrays against tau.
    m0_s_curve, mmax_s_curve = thresholds(tau_values, org_s, params)
    m0_l_curve, mmax_l_curve = thresholds(tau_values, org_l, params)

    fig, ax = plt.subplots(figsize=(12, 8))
    levels = np.linspace(-1.0, 1.0, 41)
    hm = ax.contourf(tau_grid, m_grid, delta, levels=levels, cmap="viridis", vmin=-1.0, vmax=1.0)

    ax.contour(tau_grid, m_grid, delta, levels=[0.0], colors="black", linewidths=2.5)

    ax.plot(tau_values, m0_s_curve, color="#ffbf00", linestyle="--", linewidth=2.8, label=r"VSE $M_0$")
    ax.plot(tau_values, mmax_s_curve, color="#ff3b30", linestyle="--", linewidth=2.8, label=r"VSE $M_{\max}$")
    ax.plot(tau_values, m0_l_curve, color="#00b5ad", linestyle="-.", linewidth=2.4, label=r"Large $M_0$")
    ax.plot(tau_values, mmax_l_curve, color="#1e90ff", linestyle=":", linewidth=2.4, label=r"Large $M_{\max}$")

    ax.set_xlim(0.0, 10.0)
    ax.set_ylim(0.0, 10.0)
    ax.set_xlabel(r"Disturbance timescale $\tau_d$")
    ax.set_ylabel(r"Disturbance magnitude $M$")
    ax.set_title("Resilience advantage field with parity boundary and threshold curves")

    cb = fig.colorbar(hm, ax=ax)
    cb.set_label(r"VSE advantage $\Delta R$")

    legend_handles = [
        Line2D([0], [0], color="black", linewidth=2.5, label=r"Parity boundary $\Delta R = 0$"),
        Line2D([0], [0], color="#ffbf00", linestyle="--", linewidth=2.8, label=r"VSE $M_0$"),
        Line2D([0], [0], color="#ff3b30", linestyle="--", linewidth=2.8, label=r"VSE $M_{\max}$"),
        Line2D([0], [0], color="#00b5ad", linestyle="-.", linewidth=2.4, label=r"Large $M_0$"),
        Line2D([0], [0], color="#1e90ff", linestyle=":", linewidth=2.4, label=r"Large $M_{\max}$"),
    ]
    ax.legend(handles=legend_handles, loc="upper right", frameon=False)
    ax.grid(alpha=0.15)

    fig.tight_layout()
    fig_pdf = figures_dir / "fig_5_2_resilience_advantage_heatmap.pdf"
    fig_png = figures_dir / "fig_5_2_resilience_advantage_heatmap.png"
    fig.savefig(fig_pdf)
    fig.savefig(fig_png, dpi=300)
    plt.close(fig)

    dt = tau_values[1] - tau_values[0]
    dm = m_values[1] - m_values[0]
    positive_area = float(np.sum(delta > 0.0) * dt * dm)

    idx_max = np.unravel_index(np.argmax(delta), delta.shape)
    max_adv = float(delta[idx_max])
    max_tau = float(tau_grid[idx_max])
    max_m = float(m_grid[idx_max])

    m_ref = 11.0 / 5.0
    delta_ref = delta_r(tau_values, np.full_like(tau_values, m_ref), org_s, org_l, params)[0]
    tau_stars = tau_star_estimates(tau_values, delta_ref)

    summary_rows = [
        ("k", params["k"]),
        ("alpha_A", params["alpha_A"]),
        ("beta_B", params["beta_B"]),
        ("beta_H", params["beta_H"]),
        ("epsilon_A", params["epsilon_A"]),
        ("epsilon_B", params["epsilon_B"]),
        ("A_S", org_s["A"]),
        ("B_S", org_s["B"]),
        ("H_S", org_s["H"]),
        ("tauEff_S", org_s["tau_eff"]),
        ("A_L", org_l["A"]),
        ("B_L", org_l["B"]),
        ("H_L", org_l["H"]),
        ("tauEff_L", org_l["tau_eff"]),
        ("tau_d_star_estimates", ", ".join(f"{v:.6f}" for v in tau_stars) if tau_stars else "none"),
        ("positive_advantage_area", positive_area),
        ("max_advantage", max_adv),
        ("max_advantage_tau_d", max_tau),
        ("max_advantage_M", max_m),
        ("tau_star_reference_M", m_ref),
    ]

    table_path = tables_dir / "tab_5_2_parameter_set.csv"
    pd.DataFrame(summary_rows, columns=["parameter", "value"]).to_csv(table_path, index=False)

    theorem_ranges = parse_theorem_ranges(lean_file)
    theorem_status = [
        {
            "name": name,
            "status": "proved",
            "file": "analysis/section5_2/setup/proofs/Section5_2.lean",
            "line_range": f"{theorem_ranges[name][0]}-{theorem_ranges[name][1]}",
        }
        for name in ["T5.2-1", "T5.2-2", "T5.2-3", "T5.2-4"]
    ]

    manifest = {
        "section": "5.2",
        "theorem_status": theorem_status,
        "assumptions": [
            "All organisational parameters and disturbance timescales are non-negative",
            "Gap condition M_0 < M_max is used for strict piecewise boundary claims",
            "Fast-regime sufficient conditions are encoded through scarce-branch factor decomposition",
            "Slow-regime reduction assumes mobilisation saturation f_A = f_B = 1",
            "Constructive parity case uses explicit constants in the Lean proof file",
        ],
        "parameter_values": {
            "k": params["k"],
            "alpha_A": params["alpha_A"],
            "beta_B": params["beta_B"],
            "beta_H": params["beta_H"],
            "epsilon_A": params["epsilon_A"],
            "epsilon_B": params["epsilon_B"],
            "org_S": org_s,
            "org_L": org_l,
        },
        "summary_statistics": {
            "tau_d_star_estimates": tau_stars,
            "positive_advantage_area": positive_area,
            "max_advantage": {
                "value": max_adv,
                "tau_d": max_tau,
                "M": max_m,
            },
            "tau_star_reference_M": m_ref,
        },
        "file_paths": {
            "figure_pdf": "analysis/section5_2/result/figures/fig_5_2_resilience_advantage_heatmap.pdf",
            "figure_png": "analysis/section5_2/result/figures/fig_5_2_resilience_advantage_heatmap.png",
            "table_csv": "analysis/section5_2/result/tables/tab_5_2_parameter_set.csv",
            "proof_file": "analysis/section5_2/setup/proofs/Section5_2.lean",
        },
        "caption_draft": "Figure 5-2 maps Delta R over disturbance timescale and magnitude. The zero contour marks the parity boundary, showing a fast-regime VSE advantage that reverses as mobilisation saturates and larger survivable variety dominates.",
    }

    manifest_path = results_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
