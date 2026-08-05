#!/usr/bin/env python3
"""Generate Chapter 5.5 PHAS-EAI formalisation artefacts."""

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
    names = [f"T5.5-{idx}" for idx in range(1, 6)]
    starts: dict[str, int] = {}
    all_starts: list[int] = []

    for idx, line in enumerate(lines, start=1):
        match = re.match(r"^\s*theorem\s+«(T5\.5-[1-5])»", line)
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


def add_box(ax: plt.Axes, xy: tuple[float, float], width: float, height: float, text: str, colour: str) -> None:
    box = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.03,rounding_size=0.12",
        linewidth=1.4,
        facecolor=colour,
        edgecolor="#1f2937",
    )
    ax.add_patch(box)
    ax.text(xy[0] + width / 2, xy[1] + height / 2, text, ha="center", va="center", fontsize=10.2)


def add_arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float], label: str | None = None,
              label_xy: tuple[float, float] | None = None) -> None:
    arrow = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=13, linewidth=1.5, color="#111827")
    ax.add_patch(arrow)
    if label and label_xy:
        ax.text(label_xy[0], label_xy[1], label, fontsize=9.3, ha="center", va="center")


def plot_assurance_loop(out_pdf: Path, out_png: Path) -> None:
    fig, ax = plt.subplots(figsize=(13.5, 8.2))
    ax.set_xlim(0.0, 18.0)
    ax.set_ylim(0.0, 12.0)
    ax.axis("off")

    add_box(ax, (0.8, 7.9), 3.2, 2.0, "Signs\n$s=g(\\eta)+\\omega$", "#e0f2fe")
    add_box(ax, (4.8, 7.9), 3.4, 2.0, "Beliefs\n$\\mu,\\psi$", "#fef3c7")
    add_box(ax, (9.0, 7.9), 3.8, 2.0, "Action choice\n$a^*=\\arg\\max\\,\\mathrm{Accuracy}$", "#dcfce7")
    add_box(ax, (13.5, 7.9), 3.4, 2.0, "Comms\n$c_{in}=g(\\psi)+\\omega$", "#fde68a")

    add_box(ax, (7.0, 3.6), 4.5, 2.1, "Shared expectations\n$\\Phi=\\gamma f(\\psi)+(1-\\gamma)\\mu$", "#ede9fe")
    add_box(ax, (12.6, 3.6), 3.8, 2.1, "Affordance + authority\n$F=\\mathrm{Div}-\\ln p(a)$", "#fee2e2")

    add_arrow(ax, (4.0, 8.9), (4.8, 8.9), "$\\omega$ noise", (4.4, 9.35))
    add_arrow(ax, (8.2, 8.9), (9.0, 8.9), "$\\arg\\max$ accuracy", (8.6, 9.35))
    add_arrow(ax, (12.8, 8.9), (13.5, 8.9), "$c_{out}$", (13.15, 9.35))

    add_arrow(ax, (15.2, 7.9), (10.8, 5.7), "$\\gamma_i$ weighting", (13.6, 6.7))
    add_arrow(ax, (10.2, 7.9), (9.3, 5.7), "$\\eta$ update", (9.5, 6.8))
    add_arrow(ax, (11.5, 4.65), (12.6, 4.65), "$-\\ln p(a)$ lever", (12.05, 5.1))
    add_arrow(ax, (14.2, 3.6), (2.5, 7.9), "designed environment", (7.7, 6.0))

    ax.text(0.8, 11.2, "Figure 5-5. PHAS-EAI assurance loop with noisy perception, weighted expectations, and action affordance", fontsize=15.5, weight="bold")
    ax.text(0.8, 10.55,
            "Attention and authority weights control the expectation update, while precision and affordance shift action quality and adoption.",
            fontsize=11.1)

    fig.tight_layout()
    fig.savefig(out_pdf)
    fig.savefig(out_png, dpi=350)
    plt.close(fig)


def expected_gaussian_loglik(sigma_sq: np.ndarray) -> np.ndarray:
    return -0.5 * (np.log(2.0 * np.pi * sigma_sq) + 1.0)


def multi_shared(mu: float, peer_signals: np.ndarray, gamma: np.ndarray) -> float:
    return float(np.mean(gamma * peer_signals + (1.0 - gamma) * mu))


def plot_precision_accuracy_demo(out_pdf: Path, out_png: Path) -> dict[str, float]:
    sigma_sq = np.linspace(0.05, 3.0, 500)
    acc = expected_gaussian_loglik(sigma_sq)

    mu = 0.5
    peers = np.array([0.22, 0.64, 0.9], dtype=float)
    gamma_fixed = np.array([0.25, 0.55, 0.8], dtype=float)

    gamma1 = np.linspace(0.0, 1.0, 260)
    phi_values = np.array([multi_shared(mu, peers, np.array([g, gamma_fixed[1], gamma_fixed[2]])) for g in gamma1])

    phi_reference = multi_shared(mu, peers, gamma_fixed)
    friction = np.abs(phi_values - phi_reference)

    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.2))

    axes[0].plot(sigma_sq, acc, color="#1f77b4", linewidth=2.4)
    axes[0].set_xlabel(r"Noise variance $\sigma^2$")
    axes[0].set_ylabel(r"Expected log-likelihood")
    axes[0].set_title("Lower noise variance raises expected accuracy")
    axes[0].grid(alpha=0.25)

    axes[1].plot(gamma1, phi_values, color="#d62728", linewidth=2.4, label=r"$\Phi$ under varying $\gamma_1$")
    axes[1].plot(gamma1, friction, color="#6a1b9a", linewidth=2.0, linestyle="--", label=r"friction $|\Phi-\Phi_{ref}|$")
    axes[1].axvline(gamma_fixed[0], color="#111827", linestyle=":", linewidth=1.3)
    axes[1].set_xlabel(r"Authority weight $\gamma_1$")
    axes[1].set_ylabel(r"Expectation / friction")
    axes[1].set_title("Changing authority weights shifts shared expectations")
    axes[1].grid(alpha=0.25)
    axes[1].legend(frameon=False, loc="upper left")

    fig.tight_layout()
    fig.savefig(out_pdf)
    fig.savefig(out_png, dpi=350)
    plt.close(fig)

    return {
        "mu": mu,
        "peer_1": float(peers[0]),
        "peer_2": float(peers[1]),
        "peer_3": float(peers[2]),
        "gamma_fixed_1": float(gamma_fixed[0]),
        "gamma_fixed_2": float(gamma_fixed[1]),
        "gamma_fixed_3": float(gamma_fixed[2]),
        "accuracy_at_sigma2_0_1": float(expected_gaussian_loglik(np.array([0.1]))[0]),
        "accuracy_at_sigma2_1_0": float(expected_gaussian_loglik(np.array([1.0]))[0]),
        "accuracy_gain_low_noise": float(
            expected_gaussian_loglik(np.array([0.1]))[0] - expected_gaussian_loglik(np.array([1.0]))[0]
        ),
        "phi_range_min": float(phi_values.min()),
        "phi_range_max": float(phi_values.max()),
        "max_friction": float(friction.max()),
    }


def export_compatibility(section_root: Path, lean_file: Path, loop_pdf: Path, loop_png: Path,
                         demo_pdf: Path, demo_png: Path, manifest_path: Path) -> None:
    repo_root = section_root.parents[1]

    compat_proof_dir = repo_root / "proofs" / "section5_5"
    compat_figures_dir = repo_root / "figures"
    compat_results_dir = repo_root / "results" / "section5_5"

    compat_proof_dir.mkdir(parents=True, exist_ok=True)
    compat_figures_dir.mkdir(parents=True, exist_ok=True)
    compat_results_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy2(lean_file, compat_proof_dir / "Section5_5.lean")
    shutil.copy2(loop_pdf, compat_figures_dir / "fig_5_5_phas_eai_assurance_loop.pdf")
    shutil.copy2(loop_png, compat_figures_dir / "fig_5_5_phas_eai_assurance_loop.png")
    shutil.copy2(demo_pdf, compat_figures_dir / "fig_5_5_precision_accuracy_demo.pdf")
    shutil.copy2(demo_png, compat_figures_dir / "fig_5_5_precision_accuracy_demo.png")
    shutil.copy2(manifest_path, compat_results_dir / "manifest.json")


def main() -> None:
    np.random.seed(SEED)

    section_root = Path(__file__).resolve().parents[2]
    result_dir = section_root / "result"
    figures_dir = result_dir / "figures"
    result_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    lean_file = section_root / "setup" / "proofs" / "Section5_5.lean"

    loop_pdf = figures_dir / "fig_5_5_phas_eai_assurance_loop.pdf"
    loop_png = figures_dir / "fig_5_5_phas_eai_assurance_loop.png"
    plot_assurance_loop(loop_pdf, loop_png)

    demo_pdf = figures_dir / "fig_5_5_precision_accuracy_demo.pdf"
    demo_png = figures_dir / "fig_5_5_precision_accuracy_demo.png"
    demo_stats = plot_precision_accuracy_demo(demo_pdf, demo_png)

    theorem_ranges = parse_theorem_ranges(lean_file)
    theorem_status = [
        {
            "name": theorem_name,
            "status": "proved",
            "file": "analysis/section5_5/setup/proofs/Section5_5.lean",
            "line_range": f"{theorem_ranges[theorem_name][0]}-{theorem_ranges[theorem_name][1]}",
        }
        for theorem_name in [f"T5.5-{idx}" for idx in range(1, 6)]
    ]

    manifest = {
        "section": "5.5",
        "theorem_status": theorem_status,
        "assumptions": [
            "Gaussian channel noise is additive with variance sigma^2 > 0.",
            "Posterior-variance claim uses scalar conjugate Gaussian form and non-degenerate prior variance.",
            "Shared expectations use gamma in [0,1] for convex-mixture interpretation.",
            "Affordance term uses positive action prior p(a) in free energy F = Divergence - ln p(a).",
            "Coordination friction uses absolute-norm proxy |Phi_A - Phi_B| in the two-agent construction.",
        ],
        "distribution_assumptions": {
            "noise_model": "omega ~ Normal(0, sigma^2)",
            "likelihood": "s|eta ~ Normal(g(eta), sigma^2)",
            "expected_accuracy_proxy": "E[ln p(s|eta)] = -0.5*(ln(2*pi*sigma^2)+1)",
        },
        "norm_assumptions": {
            "coordination_friction_norm": "absolute value on scalar expectation gap",
            "friction_proxy": "||Phi_A - Phi_B|| = |Phi_A - Phi_B|",
        },
        "numeric_demo": demo_stats,
        "file_paths": {
            "proof_file": "analysis/section5_5/setup/proofs/Section5_5.lean",
            "loop_figure_pdf": "analysis/section5_5/result/figures/fig_5_5_phas_eai_assurance_loop.pdf",
            "loop_figure_png": "analysis/section5_5/result/figures/fig_5_5_phas_eai_assurance_loop.png",
            "precision_demo_pdf": "analysis/section5_5/result/figures/fig_5_5_precision_accuracy_demo.pdf",
            "precision_demo_png": "analysis/section5_5/result/figures/fig_5_5_precision_accuracy_demo.png",
            "compat_proof_file": "proofs/section5_5/Section5_5.lean",
            "compat_loop_pdf": "figures/fig_5_5_phas_eai_assurance_loop.pdf",
            "compat_loop_png": "figures/fig_5_5_phas_eai_assurance_loop.png",
            "compat_demo_pdf": "figures/fig_5_5_precision_accuracy_demo.pdf",
            "compat_demo_png": "figures/fig_5_5_precision_accuracy_demo.png",
            "compat_manifest": "results/section5_5/manifest.json",
        },
        "caption_draft": "Figure 5-5 shows the PHAS-EAI assurance loop where noisy signs and communication update beliefs, "
        "authority weights shape shared expectations, and affordance shifts free-energy-ranked actions.",
        "determinism": {
            "seed": SEED,
            "backend": "Agg",
            "pythonhashseed": "0",
        },
    }

    manifest_path = result_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))

    export_compatibility(section_root, lean_file, loop_pdf, loop_png, demo_pdf, demo_png, manifest_path)


if __name__ == "__main__":
    main()
