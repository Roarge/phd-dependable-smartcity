"""
Visualisation functions for PHAS-EAI extended models.
=====================================================

Extends Kaufmann plotting with:
  - Variable model count (not hardcoded to 4)
  - Gamma evolution panel
  - Salience heatmap panel
  - Comparison overlays between Kaufmann and PHAS-EAI conditions
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from ..core.agent import ENV_SIZE, model_encoding
from ..core.simulation import EPOCHS


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
sns.set_style("whitegrid")
AGENT_COLORS = {"strong": "#1f77b4", "weak": "#ff7f0e"}


# ---------------------------------------------------------------------------
# Figure: Single-run belief heatmaps (Kaufmann Figure 7 equivalent)
# ---------------------------------------------------------------------------

def plot_belief_heatmaps(agents, title="Single Run", save_path=None):
    """
    Four-panel heatmap: each agent's self-belief and partner-belief over time.

    Parameters
    ----------
    agents : tuple of PHASAgent
        Two agents from a completed simulation with traces.
    title : str
        Figure title.
    save_path : str, optional
        Path to save the figure.
    """
    fig, axes = plt.subplots(4, 1, figsize=(14, 12), sharex=True)

    labels = [
        "Strong Agent: own belief",
        "Strong Agent: partner belief",
        "Weak Agent: own belief",
        "Weak Agent: partner belief",
    ]

    traces = [
        (agents[0].b_own_trace, agents[0]),
        (agents[0].b_partner_trace, None),
        (agents[1].b_own_trace, agents[1]),
        (agents[1].b_partner_trace, None),
    ]

    for idx, (ax, (btrace, agent)) in enumerate(zip(axes, traces)):
        data = np.array(btrace).T
        im = ax.imshow(
            data, interpolation="nearest", aspect="auto",
            vmin=0, vmax=1, cmap="viridis", origin="lower",
        )
        ax.set_ylabel(labels[idx], fontsize=9)
        ax.set_ylim(0, ENV_SIZE - 1)

        if agent is not None:
            psi = np.array(agent.psi_trace)
            epochs_arr = np.arange(len(psi))
            s_arr = np.array(agent.s_trace)
            colours = np.where(s_arr == 1, "white", "grey")
            ax.scatter(
                epochs_arr, psi, c=colours, s=8,
                zorder=5, edgecolors="none",
            )

        fig.colorbar(im, ax=ax, fraction=0.02, pad=0.01)

    axes[-1].set_xlabel("Epoch")
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Saved: {save_path}")

    plt.close(fig)
    return fig


# ---------------------------------------------------------------------------
# Figure: Aggregate comparison (Kaufmann Figure 8 equivalent)
# ---------------------------------------------------------------------------

def plot_aggregate_comparison(results, model_labels=None, save_path=None,
                              title="Aggregate Simulation Results"):
    """
    Three-row comparison across multiple model conditions.

    Row 1: Individual performance (distance from target over time).
    Row 2: End-state belief distribution.
    Row 3: Target pursued (shared vs unshared).

    Parameters
    ----------
    results : dict
        {model_key: (label, target_df, convergence_df, belief_df, fe_df, gamma_df)}
    model_labels : dict, optional
        {model_key: display_label}. Derived from result labels if None.
    save_path : str, optional
        Path to save the figure.
    title : str
        Figure title.
    """
    keys = list(results.keys())
    n_models = len(keys)

    if model_labels is None:
        model_labels = {}
        for k in keys:
            model_labels[k] = results[k][0]

    fig, axes = plt.subplots(3, n_models, figsize=(4.5 * n_models, 10))

    # Handle single-model case (axes would be 1D)
    if n_models == 1:
        axes = axes.reshape(3, 1)

    for col, key in enumerate(keys):
        label, t_df, c_df, b_df, fe_df, g_df = results[key]

        # Row 1: Distance from target
        ax = axes[0, col]
        sns.lineplot(
            data=c_df, x="Time", y="Distance from Target",
            hue="Agent", linewidth=2, ax=ax,
            palette=AGENT_COLORS, errorbar="sd",
        )
        ax.set_xlim(0, EPOCHS)
        ax.set_ylim(0, 20)
        ax.set_title(model_labels.get(key, str(key)), fontsize=10)
        if col == 0:
            ax.set_ylabel("Distance from Target")
        else:
            ax.set_ylabel("")
        if ax.get_legend():
            ax.get_legend().remove()

        # Row 2: End-state belief
        ax = axes[1, col]
        sns.lineplot(
            data=b_df, x="Relative Location", y="Belief",
            hue="Agent", linewidth=2, ax=ax,
            palette=AGENT_COLORS, errorbar="sd",
        )
        ax.set_xlim(0, ENV_SIZE - 1)
        ax.set_ylim(0, 0.45)
        if col == 0:
            ax.set_ylabel("Belief Distribution")
        else:
            ax.set_ylabel("")
        if ax.get_legend():
            ax.get_legend().remove()

        # Row 3: Target pursued
        ax = axes[2, col]
        target_counts = t_df.groupby(
            ["Agent", "Target"]
        ).size().unstack(fill_value=0)
        for target_type in ["shared target", "unshared target"]:
            if target_type not in target_counts.columns:
                target_counts[target_type] = 0
        target_counts = target_counts[["shared target", "unshared target"]]

        x = np.arange(2)
        width = 0.35
        for i, agent_name in enumerate(["strong", "weak"]):
            if agent_name in target_counts.index:
                vals = target_counts.loc[agent_name].values
            else:
                vals = [0, 0]
            ax.bar(
                x + i * width, vals, width,
                label=agent_name, color=AGENT_COLORS[agent_name],
            )
        ax.set_xticks(x + width / 2)
        ax.set_xticklabels(["shared\ntarget", "unshared\ntarget"], fontsize=8)
        ax.set_ylim(0, 180)
        if col == 0:
            ax.set_ylabel("Target Pursued")
        else:
            ax.set_ylabel("")
        if ax.get_legend():
            ax.get_legend().remove()

    # Shared legend
    handles = [
        plt.Line2D([0], [0], color=AGENT_COLORS["strong"], lw=2, label="strong"),
        plt.Line2D([0], [0], color=AGENT_COLORS["weak"], lw=2, label="weak"),
    ]
    fig.legend(
        handles=handles, loc="upper right", fontsize=10,
        title="Agent", bbox_to_anchor=(0.98, 0.98),
    )
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Saved: {save_path}")

    plt.close(fig)
    return fig


# ---------------------------------------------------------------------------
# Figure: System free energy (Kaufmann Figure 9 equivalent)
# ---------------------------------------------------------------------------

def plot_system_free_energy(results, save_path=None,
                             title="System-Level Free Energy"):
    """
    Overlay system free energy trajectories for multiple model conditions.

    Parameters
    ----------
    results : dict
        {model_key: (label, target_df, convergence_df, belief_df, fe_df, gamma_df)}
    save_path : str, optional
        Path to save the figure.
    title : str
        Figure title.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    cmap = plt.cm.viridis
    keys = list(results.keys())
    n = len(keys)

    for i, key in enumerate(keys):
        label, _, _, _, fe_df, _ = results[key]
        colour = cmap(i / max(n - 1, 1))
        ax.plot(
            fe_df.index, fe_df["FE"],
            color=colour, linewidth=2, label=label,
        )

    ax.set_xlabel("Time", fontsize=12)
    ax.set_ylabel("System Free Energy", fontsize=12)
    ax.set_xlim(0, EPOCHS)
    ax.set_ylim(0, None)
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Saved: {save_path}")

    plt.close(fig)
    return fig


# ---------------------------------------------------------------------------
# Figure: Gamma evolution over time (Extension 3 diagnostic)
# ---------------------------------------------------------------------------

def plot_gamma_evolution(results, save_path=None,
                          title="Shared Expectation Weight Evolution"):
    """
    Plot gamma (alignment weight) evolution for each model condition.

    Parameters
    ----------
    results : dict
        {model_key: (label, target_df, convergence_df, belief_df, fe_df, gamma_df)}
    save_path : str, optional
        Path to save the figure.
    title : str
        Figure title.
    """
    keys = [k for k in results if not results[k][5].empty]
    if not keys:
        print("  No gamma data to plot.")
        return None

    n = len(keys)
    max_cols = min(n, 4)
    nrows = (n + max_cols - 1) // max_cols
    fig, axes = plt.subplots(
        nrows, max_cols,
        figsize=(4.5 * max_cols, 4 * nrows),
        squeeze=False,
    )

    for idx, key in enumerate(keys):
        row, col = divmod(idx, max_cols)
        label, _, _, _, _, g_df = results[key]
        ax = axes[row, col]
        sns.lineplot(
            data=g_df, x="Epoch", y="Gamma",
            hue="Agent", linewidth=2, ax=ax,
            palette=AGENT_COLORS,
        )
        ax.set_title(label, fontsize=10)
        ax.set_ylim(-0.05, 1.05)
        if idx > 0 and ax.get_legend():
            ax.get_legend().remove()

    # Hide unused subplots
    for idx in range(n, nrows * max_cols):
        row, col = divmod(idx, max_cols)
        axes[row, col].set_visible(False)

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Saved: {save_path}")

    plt.close(fig)
    return fig


# ---------------------------------------------------------------------------
# Figure: Convergence comparison (multi-model overlay)
# ---------------------------------------------------------------------------

def plot_convergence_overlay(results, agent="weak", save_path=None,
                              title="Convergence Comparison"):
    """
    Overlay mean convergence curves for one agent across model conditions.

    Parameters
    ----------
    results : dict
        Same format as other plotting functions.
    agent : str
        Which agent to plot ("strong" or "weak").
    save_path : str, optional
        Path to save the figure.
    title : str
        Figure title.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    cmap = plt.cm.tab10
    keys = list(results.keys())

    for i, key in enumerate(keys):
        label, _, c_df, _, _, _ = results[key]
        subset = c_df[c_df["Agent"] == agent]
        mean_dist = subset.groupby("Time")["Distance from Target"].mean()
        ax.plot(
            mean_dist.index, mean_dist.values,
            color=cmap(i / 10), linewidth=2, label=label,
        )

    ax.set_xlabel("Time", fontsize=12)
    ax.set_ylabel("Mean Distance from Target", fontsize=12)
    ax.set_title("")
    ax.set_xlim(0, EPOCHS)
    ax.set_ylim(0, 20)
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Saved: {save_path}")

    plt.close(fig)
    return fig


# ---------------------------------------------------------------------------
# Figure: 2x2 alignment interaction summary
# ---------------------------------------------------------------------------

def plot_2x2_alignment(results, core_keys, save_path=None,
                       title="Alignment x ToM Interaction"):
    """
    2x2 bar chart showing the interaction between ToM and alignment,
    with a full comparison panel alongside.

    Parameters
    ----------
    results : dict
        Same format as other plotting functions.
    core_keys : dict
        Mapping of 2x2 cell labels to result keys:
        {"no_tom_no_align": key, "tom_no_align": key,
         "no_tom_align": key, "tom_align": key}
    save_path : str, optional
        Path to save the figure.
    title : str
        Figure title.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # --- Left panel: 2x2 interaction for weak agent ---
    ax = axes[0]
    cell_labels = [
        ("no_tom_no_align", "No ToM\nNo Align"),
        ("tom_no_align", "ToM\nNo Align"),
        ("no_tom_align", "No ToM\nAlign"),
        ("tom_align", "ToM\nAlign"),
    ]
    x_pos = np.arange(4)
    means = []
    for cell_key, _ in cell_labels:
        rkey = core_keys[cell_key]
        _, _, c_df, _, _, _ = results[rkey]
        subset = c_df[c_df["Agent"] == "weak"]
        final_dist = subset.groupby("Time")["Distance from Target"].mean()
        means.append(final_dist.iloc[-1])

    colours = ["#7fcdbb", "#fc8d59", "#7fcdbb", "#2c7fb8"]
    bars = ax.bar(x_pos, means, color=colours, edgecolor="black", linewidth=0.8)
    ax.set_xticks(x_pos)
    ax.set_xticklabels([lbl for _, lbl in cell_labels], fontsize=10)
    ax.set_ylabel("Mean Final Distance (weak agent)", fontsize=11)
    ax.set_title("Core 2x2: ToM x Alignment", fontsize=12, fontweight="bold")
    ax.set_ylim(0, max(means) * 1.3)
    for bar, val in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f"{val:.1f}", ha="center", va="bottom", fontsize=10,
                fontweight="bold")

    # Highlight the worst (ToM, no align) with a red border
    bars[1].set_edgecolor("#d7191c")
    bars[1].set_linewidth(2.5)

    # --- Right panel: full comparison including scaffold ---
    ax = axes[1]
    all_keys = list(results.keys())
    x_pos = np.arange(len(all_keys))
    means = []
    labels = []
    for rkey in all_keys:
        label, _, c_df, _, _, _ = results[rkey]
        subset = c_df[c_df["Agent"] == "weak"]
        final_dist = subset.groupby("Time")["Distance from Target"].mean()
        means.append(final_dist.iloc[-1])
        labels.append(label.split(": ", 1)[-1] if ": " in label else label)

    cmap_full = plt.cm.tab10
    colours = [cmap_full(i / 10) for i in range(len(all_keys))]
    bars = ax.bar(x_pos, means, color=colours, edgecolor="black", linewidth=0.8)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, fontsize=8, rotation=30, ha="right")
    ax.set_ylabel("Mean Final Distance (weak agent)", fontsize=11)
    ax.set_title("All Conditions", fontsize=12, fontweight="bold")
    ax.set_ylim(0, max(means) * 1.3)
    for bar, val in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f"{val:.1f}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Saved: {save_path}")

    plt.close(fig)
    return fig
