"""
Visualisation functions for the Active Inference Collective Intelligence model.

Reproduces the key figures from Kaufmann et al. (2021):
  - Figure 7: Single-run belief evolution heatmaps (Model 4)
  - Figure 8: Aggregate simulation results across all 4 models
  - Figure 9: System-level free energy over time
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from aif_collective import (
    EPOCHS, ENV_SIZE, model_encoding, CONDITIONS,
)


# Consistent styling
sns.set_style("whitegrid")
MODEL_LABELS = {
    1: "Model 1\n(Baseline)",
    2: "Model 2\n(Theory of Mind)",
    3: "Model 3\n(Goal Alignment)",
    4: "Model 4\n(ToM x Goal Alignment)",
}
MODEL_LABELS_SHORT = {
    1: "M1: Baseline",
    2: "M2: Theory of Mind",
    3: "M3: Goal Alignment",
    4: "M4: ToM x Goal Alignment",
}
AGENT_COLORS = {"strong": "#1f77b4", "weak": "#ff7f0e"}


def plot_figure7(agents, shared_target, save_path=None):
    """
    Reproduce Figure 7: Single-run belief evolution for Model 4.

    Shows four heatmaps:
      - Row 1: Strong agent's position and own-belief distribution
      - Row 2: Strong agent's beliefs about weak agent's location
      - Row 3: Weak agent's position and own-belief distribution
      - Row 4: Weak agent's beliefs about strong agent's location

    Parameters
    ----------
    agents : tuple of Agent
        Two agents from a completed single_run with plot=True.
    shared_target : int
        Position of the shared target (food source).
    save_path : str, optional
        Path to save the figure.
    """
    fig, axes = plt.subplots(4, 1, figsize=(14, 12), sharex=True)

    labels = [
        "Strong Agent's Locations\n& their belief distribution",
        "Strong Agent's Beliefs about\nWeak Agent's Locations",
        "Weak Agent's Locations\n& their belief distribution",
        "Weak Agent's Beliefs about\nStrong Agent's Locations",
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
            data,
            interpolation="nearest",
            aspect="auto",
            vmin=0, vmax=1,
            cmap="viridis",
            origin="lower",
        )
        ax.set_ylabel(labels[idx], fontsize=9)
        ax.set_ylim(0, ENV_SIZE - 1)

        if agent is not None:
            # Overlay actual agent positions
            psi = np.array(agent.psi_trace)
            epochs = np.arange(len(psi))
            s_arr = np.array(agent.s_trace)
            colours = np.where(s_arr == 1, "white", "grey")
            ax.scatter(epochs, psi, c=colours, s=8, zorder=5, edgecolors="none")

        fig.colorbar(im, ax=ax, fraction=0.02, pad=0.01)

    axes[-1].set_xlabel("Epoch")
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Saved: {save_path}")

    plt.close(fig)
    return fig


def plot_figure8(results, save_path=None):
    """
    Reproduce Figure 8: Aggregate simulation results for all 4 models.

    Three rows:
      - Row 1: Individual performance (distance from target over time)
      - Row 2: End-state belief distribution (shared target at centre)
      - Row 3: Distribution of targets pursued (shared vs unshared)

    Parameters
    ----------
    results : dict
        {model_num: (model, target_df, convergence_df, belief_df, fe_df)}
    save_path : str, optional
        Path to save the figure.
    """
    fig, axes = plt.subplots(3, 4, figsize=(18, 10))

    for col, model_num in enumerate([1, 2, 3, 4]):
        _, t_df, c_df, b_df, _ = results[model_num]

        # ── Row 1: Individual performance (distance from target) ──
        ax = axes[0, col]
        sns.lineplot(
            data=c_df, x="Time", y="Distance from Target",
            hue="Agent", linewidth=2, ax=ax,
            palette=AGENT_COLORS, errorbar="sd",
        )
        ax.set_xlim(0, EPOCHS)
        ax.set_ylim(0, 20)
        ax.set_title(MODEL_LABELS[model_num], fontsize=10)
        if col == 0:
            ax.set_ylabel("Individual Performance\n(Distance from Target)")
        else:
            ax.set_ylabel("")
        ax.get_legend().remove() if ax.get_legend() else None

        # ── Row 2: End-state belief distribution ──
        ax = axes[1, col]
        sns.lineplot(
            data=b_df, x="Relative Location", y="Belief",
            hue="Agent", linewidth=2, ax=ax,
            palette=AGENT_COLORS, errorbar="sd",
        )
        ax.set_xlim(0, ENV_SIZE - 1)
        ax.set_ylim(0, 0.45)
        if col == 0:
            ax.set_ylabel("Belief Distribution\n(End-state)")
        else:
            ax.set_ylabel("")
        ax.get_legend().remove() if ax.get_legend() else None

        # ── Row 3: Target pursued (shared vs unshared) ──
        ax = axes[2, col]
        target_counts = t_df.groupby(["Agent", "Target"]).size().unstack(
            fill_value=0
        )
        # Reorder columns
        for target_type in ["shared target", "unshared target"]:
            if target_type not in target_counts.columns:
                target_counts[target_type] = 0
        target_counts = target_counts[["shared target", "unshared target"]]

        x = np.arange(2)
        width = 0.35
        agents_list = ["strong", "weak"]
        for i, agent_name in enumerate(agents_list):
            if agent_name in target_counts.index:
                vals = target_counts.loc[agent_name].values
            else:
                vals = [0, 0]
            ax.bar(x + i * width, vals, width,
                   label=agent_name, color=AGENT_COLORS[agent_name])

        ax.set_xticks(x + width / 2)
        ax.set_xticklabels(["shared\ntarget", "unshared\ntarget"], fontsize=8)
        ax.set_ylim(0, 180)
        if col == 0:
            ax.set_ylabel("Target Pursued\n(max count 180)")
        else:
            ax.set_ylabel("")
        ax.get_legend().remove() if ax.get_legend() else None

    # Add a single legend for the whole figure
    handles = [
        plt.Line2D([0], [0], color=AGENT_COLORS["strong"], lw=2, label="strong"),
        plt.Line2D([0], [0], color=AGENT_COLORS["weak"], lw=2, label="weak"),
    ]
    fig.legend(handles=handles, loc="upper right", fontsize=10,
               title="Agent", bbox_to_anchor=(0.98, 0.98))

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Saved: {save_path}")

    plt.close(fig)
    return fig


def plot_figure9(results, save_path=None):
    """
    Reproduce Figure 9: System-level free energy F^Sigma over time.

    Shows how each model reduces system free energy over the simulation,
    with lower free energy indicating higher collective performance.

    Parameters
    ----------
    results : dict
        {model_num: (model, target_df, convergence_df, belief_df, fe_df)}
    save_path : str, optional
        Path to save the figure.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    colours = {
        1: "grey",
        2: "#d62728",   # red
        3: "#bcbd22",   # yellow-green
        4: "#2ca02c",   # green
    }
    linewidths = {1: 2, 2: 2, 3: 2, 4: 2.5}

    for model_num in [1, 2, 3, 4]:
        _, _, _, _, fe_df = results[model_num]
        ax.plot(
            fe_df.index, fe_df['FE'],
            color=colours[model_num],
            linewidth=linewidths[model_num],
            label=MODEL_LABELS_SHORT[model_num],
        )

    ax.set_xlabel("Time", fontsize=12)
    ax.set_ylabel("System Free Energy", fontsize=12)
    ax.set_title("")
    ax.set_xlim(0, EPOCHS)
    ax.set_ylim(0, None)
    ax.legend(fontsize=10, loc="upper right")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Saved: {save_path}")

    plt.close(fig)
    return fig
