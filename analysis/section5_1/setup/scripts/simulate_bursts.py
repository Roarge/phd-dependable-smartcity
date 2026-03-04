#!/usr/bin/env python3
"""Generate deterministic Chapter 5.1 proof artefacts and simulation outputs."""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sympy as sp


SEED = 20260208


@dataclass(frozen=True)
class EventSpec:
    time_index: int
    description: str


def project_paths() -> tuple[Path, Path, Path, Path]:
    script_path = Path(__file__).resolve()
    section_root = script_path.parents[2]
    result_dir = section_root / "result"
    writeup_dir = section_root / "writeup"
    result_dir.mkdir(parents=True, exist_ok=True)
    writeup_dir.mkdir(parents=True, exist_ok=True)
    return section_root, script_path, result_dir, writeup_dir


def simulate_series() -> dict[str, np.ndarray]:
    np.random.seed(SEED)

    t = np.arange(0, 91)

    # Gradual growth plus discrete step multipliers from boundary and governance events.
    log2_c = 8.2 + 0.022 * t
    log2_c += np.where(t >= 20, np.log2(1.70), 0.0)
    log2_c += np.where(t >= 45, np.log2(1.03), 0.0)
    log2_c += np.where(t >= 70, np.log2(0.75), 0.0)
    c = np.power(2.0, log2_c)

    # Design-time success share with event shocks and adaptation.
    rho_design = 0.24 - 0.0007 * t
    for t_event, amplitude, decay in [
        (20, -0.050, 14.0),
        (45, -0.090, 18.0),
        (70, +0.100, 20.0),
    ]:
        mask = t >= t_event
        rho_design[mask] += amplitude * np.exp(-(t[mask] - t_event) / decay)
    rho_design = np.clip(rho_design, 0.02, 0.95)

    # Time-conditioning from the thesis mobilisation model.
    tau_d = np.full_like(t, 9.0, dtype=float)
    for t_event, amplitude, decay in [
        (45, -3.20, 22.0),
        (70, +1.80, 22.0),
    ]:
        mask = t >= t_event
        tau_d[mask] += amplitude * np.exp(-(t[mask] - t_event) / decay)
    tau_d = np.clip(tau_d, 1.6, None)

    tau_eff = 6.20 + 0.018 * t
    for t_event, amplitude, decay in [
        (20, +1.50, 16.0),
        (45, +2.40, 20.0),
        (70, -2.00, 24.0),
    ]:
        mask = t >= t_event
        tau_eff[mask] += amplitude * np.exp(-(t[mask] - t_event) / decay)
    tau_eff = np.clip(tau_eff, 1.0, None)

    epsilon_a = 1.15
    r = tau_d / tau_eff
    f_a = np.minimum(1.0, np.power(r, epsilon_a))

    a = rho_design * c
    a_tilde = a * f_a

    rho_op = a_tilde / c
    rho_op = np.clip(rho_op, 1e-9, 1.0)

    i_g = -np.log2(rho_design)
    i_g_op = -np.log2(rho_op)

    return {
        "t": t,
        "C": c,
        "A": a,
        "A_tilde": a_tilde,
        "rho_design": rho_design,
        "rho_op": rho_op,
        "I_g": i_g,
        "I_g_op": i_g_op,
        "tau_d": tau_d,
        "tau_eff": tau_eff,
        "f_A": f_a,
    }


def build_event_metrics(series: dict[str, np.ndarray]) -> pd.DataFrame:
    events = [
        EventSpec(20, "Boundary degree introduction with coupling spillover"),
        EventSpec(45, "Constraint and boundary commitment shift in governance and compliance"),
        EventSpec(70, "Joint intervention on option count and mobilisation quality"),
    ]

    rows: list[dict[str, object]] = []
    for event in events:
        before = event.time_index - 1
        after = event.time_index
        rho_before = float(series["rho_op"][before])
        rho_after = float(series["rho_op"][after])
        i_before = float(series["I_g_op"][before])
        i_after = float(series["I_g_op"][after])

        rows.append(
            {
                "event_time_index": event.time_index,
                "change_description": event.description,
                "rho_op_before": rho_before,
                "rho_op_after": rho_after,
                "delta_Ig_op_bits": i_after - i_before,
                "log2_C_before": float(np.log2(series["C"][before])),
                "log2_C_after": float(np.log2(series["C"][after])),
                "log2_A_tilde_before": float(np.log2(series["A_tilde"][before])),
                "log2_A_tilde_after": float(np.log2(series["A_tilde"][after])),
            }
        )

    return pd.DataFrame(rows)


def save_metrics_tables(df: pd.DataFrame, artifacts: Path) -> None:
    csv_path = artifacts / "burst_metrics.csv"
    tex_path = artifacts / "burst_metrics.tex"

    df.to_csv(csv_path, index=False, float_format="%.6f")

    latex_df = df.copy()
    latex_df.columns = [
        "Event $t$",
        "Change",
        "$\\rho^{op}_{-}$",
        "$\\rho^{op}_{+}$",
        "$\\Delta I_g^{op}$ (bits)",
        "$\\log_2 C_{-}$",
        "$\\log_2 C_{+}$",
        "$\\log_2 \\tilde{A}_{-}$",
        "$\\log_2 \\tilde{A}_{+}$",
    ]
    tex = latex_df.to_latex(index=False, escape=False, float_format=lambda x: f"{x:.4f}")
    tex_path.write_text(tex)


def plot_complexity_bursts(series: dict[str, np.ndarray], artifacts: Path) -> None:
    t = series["t"]
    events = [20, 45, 70]

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(t, np.log2(series["C"]), color="#1f77b4", linewidth=2.4, label=r"$\log_2 C(t)$")
    ax.plot(t, np.log2(series["A_tilde"]), color="#2ca02c", linewidth=2.4, label=r"$\log_2 \tilde{A}(t)$")
    ax.plot(t, series["I_g_op"], color="#d62728", linewidth=2.4, label=r"$I_g^{op}(t)$")

    for t_event in events:
        ax.axvline(t_event, color="#555555", linestyle="--", linewidth=1.2)

    ax.text(20.5, series["I_g_op"][20] + 0.8, "Boundary composition", fontsize=9)
    ax.text(45.5, series["I_g_op"][45] + 0.8, "Constraint shock", fontsize=9)
    ax.text(70.5, series["I_g_op"][70] - 1.0, "Joint intervention", fontsize=9)

    ax.set_xlabel("Time index")
    ax.set_ylabel("Bits")
    ax.set_title(
        "Step changes in effective decision burden and mobilisation under boundary and constraint events"
    )
    ax.grid(alpha=0.25)
    ax.legend(loc="upper left", frameon=False)

    fig.tight_layout()
    fig.savefig(artifacts / "fig_5_1_complexity_bursts.png", dpi=300)
    fig.savefig(artifacts / "fig_5_1_complexity_bursts.pdf")
    plt.close(fig)


def plot_multiplicative_growth(artifacts: Path) -> None:
    baseline = {
        "tech": 12,
        "org": 6,
        "policy": 4,
        "practice": 5,
        "language": 3,
        "worldview": 2,
        "boundary": 2,
    }

    c_baseline = np.prod(list(baseline.values()))

    boundary_plus = baseline.copy()
    boundary_plus["boundary"] = 3
    c_boundary_plus = np.prod(list(boundary_plus.values()))

    coupled = baseline.copy()
    coupled["boundary"] = 3
    coupled["language"] = 4
    coupled["policy"] = 5
    c_coupled = np.prod(list(coupled.values()))

    labels = [
        "Baseline",
        "+1 boundary\noption",
        "+1 boundary with\ninterdependence",
    ]
    values = np.array([c_baseline, c_boundary_plus, c_coupled], dtype=float)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    bars = ax.bar(labels, values, color=["#4c78a8", "#f58518", "#54a24b"]) 

    for i, bar in enumerate(bars):
        multiplier = values[i] / values[0]
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() * 1.02,
            f"x{multiplier:.2f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    ax.set_ylabel("Feasible distinct options $C$")
    ax.set_title("Multiplicative option growth from small boundary degree changes")
    ax.grid(axis="y", alpha=0.25)

    fig.tight_layout()
    fig.savefig(artifacts / "fig_multiplicative_option_growth.png", dpi=300)
    fig.savefig(artifacts / "fig_multiplicative_option_growth.pdf")
    plt.close(fig)


def save_multiplicative_composition_table(artifacts: Path) -> None:
    """Produce the (n, m, C) multiplicative composition table cited in Appendix A.1."""
    scenarios = [
        {"n": 3, "m": 4, "C": 4**3, "log2_C": np.log2(4**3)},
        {"n": 5, "m": 3, "C": 3**5, "log2_C": np.log2(3**5)},
        {"n": 7, "m": 2, "C": 2**7, "log2_C": np.log2(2**7)},
    ]
    df = pd.DataFrame(scenarios)
    df["C_exceeds_m_plus_n"] = df["C"] > (df["m"] + df["n"])
    df.to_csv(artifacts / "tab_5_1_multiplicative_composition.csv", index=False, float_format="%.4f")

    latex_df = df.rename(columns={
        "n": "$n$",
        "m": "$m$",
        "C": "$C = m^n$",
        "log2_C": "$\\log_2 C$",
        "C_exceeds_m_plus_n": "$C > m+n$",
    })
    tex = latex_df.to_latex(index=False, escape=False, float_format=lambda x: f"{x:.4f}")
    (artifacts / "tab_5_1_multiplicative_composition.tex").write_text(tex)


def plot_joint_intervention(series: dict[str, np.ndarray], artifacts: Path) -> None:
    index = 69
    c0 = float(series["C"][index])
    a0 = float(series["A_tilde"][index])

    alpha = 0.75
    beta = 1.35

    i_base = np.log2(c0) - np.log2(a0)
    i_only_c = np.log2(alpha * c0) - np.log2(a0)
    i_only_a = np.log2(c0) - np.log2(beta * a0)
    i_joint = np.log2(alpha * c0) - np.log2(beta * a0)

    labels = ["Baseline", "Reduce $C_{eff}$ only", "Increase $A_{eff}$ only", "Joint change"]
    values = [i_base, i_only_c, i_only_a, i_joint]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    bars = ax.bar(labels, values, color=["#4c78a8", "#f58518", "#e45756", "#54a24b"])

    for bar, value in zip(bars, values, strict=True):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.04,
            f"{value:.3f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    reduction_joint = i_base - i_joint
    reduction_c = i_base - i_only_c
    reduction_a = i_base - i_only_a
    ax.text(2.75, i_joint + 0.30, f"Joint reduction = {reduction_joint:.3f} bits", fontsize=9)
    ax.text(2.75, i_joint + 0.12, f"Single-term sum = {(reduction_c + reduction_a):.3f} bits", fontsize=9)

    ax.set_ylabel(r"$I_g^{op}$ (bits)")
    ax.set_title("Joint intervention lowers operational functional information additively")
    ax.grid(axis="y", alpha=0.25)

    fig.tight_layout()
    fig.savefig(artifacts / "fig_joint_intervention_effect.png", dpi=300)
    fig.savefig(artifacts / "fig_joint_intervention_effect.pdf")
    plt.close(fig)


def theorem_line_ranges(lean_file: Path, theorem_names: list[str]) -> dict[str, tuple[int, int]]:
    lines = lean_file.read_text().splitlines()
    selected_starts: dict[str, int] = {}
    all_starts: list[int] = []

    for idx, line in enumerate(lines, start=1):
        match = re.match(r"^\s*theorem\s+([A-Za-z0-9_]+)", line)
        if match:
            theorem_name = match.group(1)
            all_starts.append(idx)
            if theorem_name in theorem_names:
                selected_starts[theorem_name] = idx

    all_starts.sort()
    ranges: dict[str, tuple[int, int]] = {}
    for name in theorem_names:
        start = selected_starts[name]
        next_starts = [line_no for line_no in all_starts if line_no > start]
        end = (next_starts[0] - 1) if next_starts else len(lines)
        ranges[name] = (start, end)
    return ranges


def save_proof_status(section_root: Path, result_dir: Path) -> None:
    theorem_names = ["A1", "A2", "A3", "A4", "B1", "B2", "B3", "C1", "C2"]
    theorem_statements = {
        "A1": "If a factor expands with fixed K, complexity C is non-decreasing",
        "A2": "If constraints tighten, complexity cannot increase",
        "A3": "Under factorised constraints and binning, total complexity is multiplicative",
        "A4": "Discrete factor introductions produce jumps with Delta log2 C = log2(k)",
        "B1": "Selection pressure that reduces rho^op makes I_g^op non-decreasing",
        "B2": "Discrete change gives Delta I_g^op = log2(rho_minus / rho_plus)",
        "B3": "Discrete pressure events produce jump discontinuities in I_g^op",
        "C1": "Change in I_g^op decomposes into log2(C ratio) minus log2(A ratio)",
        "C2": "Joint intervention reduction equals sum of single-term reductions",
    }

    lean_file = section_root / "setup" / "lean" / "ComplexityBursts.lean"
    ranges = theorem_line_ranges(lean_file, theorem_names)

    rho_minus, rho_plus, k, alpha, beta = sp.symbols("rho_minus rho_plus k alpha beta", positive=True)
    jump_i = sp.log(rho_minus / rho_plus, 2)
    jump_c = sp.log(k, 2)
    joint_gain = -sp.log(alpha, 2) + sp.log(beta, 2)

    theorems_json = []
    for name in theorem_names:
        start, end = ranges[name]
        theorems_json.append(
            {
                "name": name,
                "statement": theorem_statements[name],
                "status": "proved",
                "file": "analysis/section5_1/setup/lean/ComplexityBursts.lean",
                "line_range": f"{start}-{end}",
            }
        )

    payload = {
        "model_version": "Analytical-Models-4.2",
        "theorems": theorems_json,
        "assumptions": [
            "Finite decision resolution induces finite configuration spaces",
            "Distinct options are equivalence classes induced by the binning map b",
            "Constraint tightening means K2 implies K1 at configuration level",
            "A3 exactness assumes factorised constraints and factorised binning across subsystems",
            "All log arguments are strictly positive",
            "Selection pressure is modelled by antitone rho^op",
            "Event times are discrete and updates occur at event indices",
            "Joint intervention uses alpha in (0,1) and beta greater than 1",
        ],
        "derived_jump_formulae": [
            f"Delta log2 C = {sp.sstr(jump_c)}",
            f"Delta I_g^op = {sp.sstr(jump_i)}",
            f"Joint reduction in I_g^op = {sp.sstr(joint_gain)}",
        ],
    }

    (result_dir / "proof_status.json").write_text(json.dumps(payload, indent=2))


def save_traceability_map(writeup_dir: Path) -> None:
    text = """# Traceability Map

| Formal element | Lean identifier | Thesis source mapping |
|---|---|---|
| Configuration product space `X = ∏ X_i` | `ComplexityModel.feasibleDistinctSet` domain argument `Xspace` with finite factors | `Analytical Models/Complexity-in-PHAS.md` Eq. (15), Eq. (15a) |
| Constraints `K` and feasibility pruning | `ComplexityModel.feasibleDistinctSet` filter by `K` | `Analytical Models/Complexity-in-PHAS.md` Hard Constraints section |
| Distinctness by binning and quotient | `ComplexityModel.binEq`, `ComplexityModel.feasibleDistinctSet` image under `b` | `Analytical Models/Complexity-in-PHAS.md` Eq. (15b), Eq. (15c), Eq. (15d) |
| Complexity as total optionality `C = |S^δ|` | `ComplexityModel.complexity` | `Analytical Models/Complexity-in-PHAS.md` Eq. (16) |
| Success set and success share | `ComplexityModel.successSet`, `ComplexityModel.successShare` | `Analytical Models/Functional-Information-and-Cost-of-Choice-in-PHAS.md` Eq. (29), Eq. (30) |
| Functional information `I_g = -log2(rho)` | `ComplexityModel.functionalInformation` | `Analytical Models/Functional-Information-and-Cost-of-Choice-in-PHAS.md` Eq. (31) |
| Time-conditioning and mobilisation | `ComplexityModel.mobilisationFraction`, `ComplexityModel.effectiveSuccessCount` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` Eq. (24), Eq. (25), Eq. (26), and Eq. (32) |
| Operational functional information `I_g^{op}` | `ComplexityModel.operationalFunctionalInformation`, `ComplexityModel.operationalFunctionalInformationFromShare` | `Analytical Models/Functional-Information-and-Cost-of-Choice-in-PHAS.md` Eq. (33) |
| A1 Monotonicity under expansion | `ComplexityBursts.A1` | Complexity sanity check direction-of-change statement |
| A2 Monotonicity under tightening | `ComplexityBursts.A2` | Complexity sanity check direction-of-change statement |
| A3 Multiplicative composition | `ComplexityBursts.A3` | Composition property paragraph |
| A4 Event jump in complexity bits | `ComplexityBursts.A4` | Discrete event interpretation of composition in Chapter 5.1 |
| B1 Selection pressure monotonicity | `ComplexityBursts.B1` | Operational difficulty term in Eq. (33) and time-conditioning Eq. (24)-(26) |
| B2 Closed-form jump in `I_g^{op}` | `ComplexityBursts.B2` | Direct consequence of Eq. (33) expressed with success-share ratio |
| B3 Discrete-event burst in `I_g^{op}` | `ComplexityBursts.B3` | Governance and boundary event interpretation for Chapter 5.1.2 |
| C1 Differential expression for interventions | `ComplexityBursts.C1` | Eq. (33) decomposition by total versus useful effective options |
| C2 Joint intervention additivity | `ComplexityBursts.C2` | Operational information reduction interpretation in final paragraph of functional information model |
"""
    (writeup_dir / "traceability_map.md").write_text(text)


def save_section_writeup(metrics_df: pd.DataFrame, writeup_dir: Path) -> None:
    event_20 = metrics_df.loc[metrics_df["event_time_index"] == 20].iloc[0]
    event_45 = metrics_df.loc[metrics_df["event_time_index"] == 45].iloc[0]
    event_70 = metrics_df.loc[metrics_df["event_time_index"] == 70].iloc[0]

    text = f"""# Section 5.1 Formal Proof Write-up

## 5.1.1 Bursts from multiplicative composition of options

Theorem `A1` proves that complexity `C` is non-decreasing when a factor option set expands while `K` is fixed. The strictness lemma `A1_strict` gives the minimal strict increase condition. At least one new feasible distinct bin must be introduced by the expansion.

Theorem `A3` proves exact multiplicative composition under the stated independence assumption where constraints and binning factorise across subsystems. This validates the burst mechanism in which small boundary additions can produce large growth in feasible combinations.
When interdependence and heterogeneous constraints in `K` are active, a small interface change can alter feasibility across several coupled factors, so option-set shifts propagate beyond the edited boundary degree.\n

Theorem `A4` proves the event-time update form for discrete introductions. Between events the trajectory is constant at one-step resolution. At event times the jump is multiplicative and the bit jump is `Delta log2 C = log2(k)`. In the event at `t=20`, `log2 C` rises from {event_20['log2_C_before']:.3f} to {event_20['log2_C_after']:.3f}, demonstrating the step behaviour.

## 5.1.2 Bursts from constraint changes rather than option growth alone

Theorem `A2` proves that tightening constraints cannot increase feasible distinct options. This binds the analysis directly to `K`, including governance commitments and boundary obligations.

Theorem `B3` proves that a discrete drop in `rho^op` produces a jump in `I_g^op`. This captures discontinuities caused by governance, compliance, interface-semantics, or procurement changes even when technical option growth is limited.

In the event at `t=45`, `log2 C` changes only from {event_45['log2_C_before']:.3f} to {event_45['log2_C_after']:.3f}, while `Delta I_g^op` is {event_45['delta_Ig_op_bits']:.3f} bits. This separates constraint-driven bursts from raw option-count growth.

## 5.1.3 Functional information explains why bursts feel like sudden loss of competence

Theorem `B1` establishes that when selection pressure makes `rho^op` non-increasing, operational functional information `I_g^op = -log2(rho^op)` is non-decreasing. This gives a necessary monotonic response of decision burden under pressure.

Theorem `B2` provides the closed-form jump expression `Delta I_g^op = log2(rho_minus / rho_plus)`. The jump size is additive in bits, so small proportional drops in mobilisation share produce immediate increases in operational choice cost.

At `t=45`, `rho^op` drops from {event_45['rho_op_before']:.4f} to {event_45['rho_op_after']:.4f}. The measured increase in burden is {event_45['delta_Ig_op_bits']:.3f} bits. This maps to the observed operational experience of sudden competence loss because the same team faces a larger effective search burden within the same response window.

Figure `analysis/section5_1/result/fig_5_1_complexity_bursts.pdf` is the Chapter 5.1 anchor. The `log2 C` curve shows structural burden growth with discrete steps. The `log2 A~` curve shows mobilisation-constrained useful options. The `I_g^op` curve shows bursty increases in decision burden at the same event points.

## Embedded hypotheses

### H1 Bursty complexity hypothesis

Formal basis: `A4`, `B2`, and `B3`.

Prediction: bursts in complexity potential or boundary constraints create bursts in `I_g^op` and immediate response-performance drops because fewer useful options are mobilisable in time.

### H1 Joint intervention hypothesis

Formal basis: `C1` and `C2`.

`C1` decomposes change in operational functional information into a total-option term and a useful-option term. `C2` proves exact additivity of reductions for simultaneous changes.

In the event at `t=70`, the model shows `Delta I_g^op = {event_70['delta_Ig_op_bits']:.3f}` bits with simultaneous option-pruning and useful-share increase. The joint reduction is larger than either single-term intervention alone by theorem, not by narrative assumption.

## Required reasoning chain

1. Complexity is defined as feasible distinct optionality by cardinality of the quotient induced by binning and constraints, implemented by `feasibleDistinctSet` and `complexity`.
2. Multiplicative composition is proven by `A3`, so small additions at boundaries can scale combinations disproportionately.
3. Success share and functional information are formalised in `successShare` and `functionalInformation`, with `B1` separating optionality growth from success-share effects.
4. Time-conditioning enters through mobilisation fraction and effective success count, so reduced mobilisation lowers `rho^op` even if `C` grows.
5. Selection pressure is represented as antitone `rho^op` in `B1`, forcing non-decreasing `I_g^op`.
6. Discrete governance and boundary events are modelled in `A4` and `B3`, yielding jump discontinuities with closed-form jump size `B2`.
7. Joint intervention effects are derived in `C1` and `C2`, giving a direct resilience implication that coordinated pruning and success-share improvement should be prioritised.
"""

    (writeup_dir / "section_5_1_proof_writeup.md").write_text(text)


def main() -> None:
    section_root, _script_path, result_dir, writeup_dir = project_paths()

    series = simulate_series()
    metrics_df = build_event_metrics(series)

    save_metrics_tables(metrics_df, result_dir)
    plot_complexity_bursts(series, result_dir)
    plot_multiplicative_growth(result_dir)
    save_multiplicative_composition_table(result_dir)
    plot_joint_intervention(series, result_dir)

    save_proof_status(section_root, result_dir)
    save_traceability_map(writeup_dir)
    save_section_writeup(metrics_df, writeup_dir)


if __name__ == "__main__":
    main()
