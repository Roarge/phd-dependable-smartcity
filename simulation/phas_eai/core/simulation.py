"""
Simulation runner for the PHAS-EAI extended model.
===================================================

Provides the same interface as Kaufmann's simulate_agents / single_run /
simulate_runs, but using PHASAgent and the shared Environment.
"""

import numpy as np
import pandas as pd
from datetime import datetime

from .agent import (
    PHASAgent, initialize_b_star, model_encoding, ENV_SIZE,
    ACTIONS, KL,
)
from .environment import (
    Environment, SHORTEST_PATH, TARGET_DELTA,
)


# ---------------------------------------------------------------------------
# Simulation parameters (matching Kaufmann defaults)
# ---------------------------------------------------------------------------
EPOCHS = 200
MAX_SENSE_PROBABILITY = [0.99, 0.05]


def simulate_pair(agents, environment, epochs=EPOCHS,
                  practice_interval=0, practice_fidelity=0.5,
                  disturbance_epoch=None, rng=None):
    """
    Run the simulation for a pair of interacting agents.

    Parameters
    ----------
    agents : tuple of PHASAgent
        Two agents to simulate.
    environment : Environment
        Shared environment instance.
    epochs : int
        Number of simulation steps.
    practice_interval : int
        If > 0, perform Patterned Practices sync every this many epochs.
        0 disables sync.
    practice_fidelity : float
        Blending weight for Patterned Practices sync.
    disturbance_epoch : int or None
        If set, apply a disturbance at this epoch.
    rng : np.random.RandomState, optional
        Random state for disturbance reproducibility.

    Returns
    -------
    agents : tuple of PHASAgent
        The agents after simulation (with traces populated).
    """
    for epoch in range(epochs):
        # Disturbance event (Extension 5)
        if disturbance_epoch is not None and epoch == disturbance_epoch:
            environment.apply_disturbance(rng=rng)
            # Update desired beliefs to reflect new targets
            for agent in agents:
                aid = agent.agent_id
                targets = environment.targets[aid]
                new_b_star = initialize_b_star(
                    [targets[0], targets[1],
                     environment.targets[1 - aid][1]]
                )
                agent.b_star = (
                    new_b_star[0] + (1 - agent.alignment) * new_b_star[1],
                    new_b_star[0] + (1 - agent.alignment) * new_b_star[2],
                )
                from .agent import variational_density, p_action
                agent.q_star = (
                    variational_density(agent.b_star[0]),
                    variational_density(agent.b_star[1]),
                )
                agent.p_ap = p_action(agent.q_star[1])

        # Update perceived delta (position difference)
        delta_0 = agents[0].psi - agents[1].psi
        agents[0].delta = delta_0
        agents[1].delta = -delta_0

        # Update perceived partner action
        agents[0].a_pp = agents[1].a[0]
        agents[1].a_pp = agents[0].a[0]

        # Each agent steps
        for agent in agents:
            agent.step()

        # Environment salience decay
        environment.decay_salience()

        # Patterned Practices: periodic sync (Extension 4)
        if practice_interval > 0 and (epoch + 1) % practice_interval == 0:
            # Bidirectional sync: each agent gets the other's self-belief
            b0_own = agents[0].b[0].copy()
            b1_own = agents[1].b[0].copy()
            agents[0].sync_partner_belief(b1_own, practice_fidelity)
            agents[1].sync_partner_belief(b0_own, practice_fidelity)

    # Append final target distribution for plotting (matching Kaufmann)
    for agent in agents:
        tgt = model_encoding(agent.b_star[0])
        agent.b_own_trace.append(tgt / tgt.max())
        sd = agent._effective_sensory()
        agent.s_trace.append(int(np.random.random() < sd[agent.psi]))

    return agents


def single_run(
    shared_target,
    perceptiveness,
    alterity,
    alignment,
    h=(0.0, 0.0),
    niche_construction=False,
    niche_boost=0.15,
    niche_radius=3,
    niche_decay=0.99,
    dynamic_gamma=False,
    gamma_lr=0.01,
    practice_interval=0,
    practice_fidelity=0.5,
    disturbance_epoch=None,
    rng=None,
    plot=False,
    epochs=EPOCHS,
):
    """
    Run a single simulation with two agents.

    Parameters match Kaufmann's single_run plus PHAS-EAI extensions.
    h is a tuple (h_agent0, h_agent1) for per-agent cognitive reserve.

    Returns convergence data or agents (if plot=True).
    """
    env = Environment(
        niche_construction=niche_construction,
        boost=niche_boost,
        kernel_radius=niche_radius,
        salience_decay=niche_decay,
    )

    initial_positions = [
        (shared_target + SHORTEST_PATH) % ENV_SIZE,
        (shared_target - SHORTEST_PATH) % ENV_SIZE,
    ]
    target_0 = (shared_target - TARGET_DELTA) % ENV_SIZE
    target_1 = (shared_target + TARGET_DELTA) % ENV_SIZE

    env.set_targets(shared_target, {0: target_0, 1: target_1})

    b_star_0 = initialize_b_star([shared_target, target_0, target_1])
    b_star_1 = initialize_b_star([shared_target, target_1, target_0])

    agents = (
        PHASAgent(
            agent_id=0,
            psi=initial_positions[0],
            b_star=b_star_0,
            perceptiveness=perceptiveness[0],
            alterity=alterity[0],
            alignment=alignment,
            h=h[0],
            environment=env,
            dynamic_gamma=dynamic_gamma,
            gamma_lr=gamma_lr,
        ),
        PHASAgent(
            agent_id=1,
            psi=initial_positions[1],
            b_star=b_star_1,
            perceptiveness=perceptiveness[1],
            alterity=alterity[1],
            alignment=alignment,
            h=h[1],
            environment=env,
            dynamic_gamma=dynamic_gamma,
            gamma_lr=gamma_lr,
        ),
    )

    agents = simulate_pair(
        agents, env, epochs=epochs,
        practice_interval=practice_interval,
        practice_fidelity=practice_fidelity,
        disturbance_epoch=disturbance_epoch,
        rng=rng,
    )

    if plot:
        return agents, env

    tgt_0, log_0 = agents[0].log_convergence([shared_target, target_0])
    tgt_1, log_1 = agents[1].log_convergence([shared_target, target_1])

    b_end_0 = np.roll(
        agents[0].b_own_trace[-2],
        (int(ENV_SIZE / 2) - shared_target) % ENV_SIZE,
    )
    b_end_1 = np.roll(
        agents[1].b_own_trace[-2],
        (int(ENV_SIZE / 2) - shared_target) % ENV_SIZE,
    )

    return (
        tgt_0, log_0, b_end_0, agents[0].psi_trace,
        tgt_1, log_1, b_end_1, agents[1].psi_trace,
        agents[0].gamma_trace, agents[1].gamma_trace,
    )


def simulate_runs(
    model_label,
    perceptiveness=None,
    alterity=(0, 0),
    alignment=0,
    h=(0.0, 0.0),
    niche_construction=False,
    niche_boost=0.15,
    niche_radius=3,
    niche_decay=0.99,
    dynamic_gamma=False,
    gamma_lr=0.01,
    practice_interval=0,
    practice_fidelity=0.5,
    disturbance_epoch=None,
    no_of_cycles=3,
    verbose=True,
    epochs=EPOCHS,
):
    """
    Run the full simulation for a given model configuration.

    Returns (model_label, target_df, convergence_df, belief_df, fe_df, gamma_df).
    """
    if perceptiveness is None:
        perceptiveness = MAX_SENSE_PROBABILITY

    target_rows_0, target_rows_1 = [], []
    convergence_rows_0, convergence_rows_1 = [], []
    belief_rows_0, belief_rows_1 = [], []
    gamma_rows_0, gamma_rows_1 = [], []
    q_empirical = np.zeros([epochs, ENV_SIZE])

    total_runs = no_of_cycles * ENV_SIZE
    if verbose:
        print(f"Running {model_label}")
        print(f"  h={h}, niche={niche_construction}, "
              f"dyn_gamma={dynamic_gamma}, practice_P={practice_interval}")
        print(f"  Total runs: {total_runs}")
        print(f"  Start: {datetime.now().strftime('%H:%M:%S')}")

    for i in range(no_of_cycles):
        for shared_target in range(ENV_SIZE):
            run_num = i * ENV_SIZE + shared_target
            if verbose and (run_num % 30 == 0):
                print(f"    run {run_num}/{total_runs}")

            result = single_run(
                shared_target, perceptiveness, alterity, alignment,
                h=h,
                niche_construction=niche_construction,
                niche_boost=niche_boost,
                niche_radius=niche_radius,
                niche_decay=niche_decay,
                dynamic_gamma=dynamic_gamma,
                gamma_lr=gamma_lr,
                practice_interval=practice_interval,
                practice_fidelity=practice_fidelity,
                disturbance_epoch=disturbance_epoch,
                epochs=epochs,
            )
            t1, c1, b1, psi1, t2, c2, b2, psi2, g1, g2 = result

            target_rows_0.append(t1)
            target_rows_1.append(t2)
            convergence_rows_0.append(c1)
            convergence_rows_1.append(c2)
            belief_rows_0.append(b1)
            belief_rows_1.append(b2)
            gamma_rows_0.append(g1)
            gamma_rows_1.append(g2)

            for t in range(epochs):
                q_empirical[t, psi1[t] - shared_target] += 1
                q_empirical[t, psi2[t] - shared_target] += 1

    if verbose:
        print(f"  End: {datetime.now().strftime('%H:%M:%S')}")

    # Assemble DataFrames
    t_composite = _target_data(target_rows_0, target_rows_1)
    c_composite = _convergence_data(convergence_rows_0, convergence_rows_1)
    b_composite = _belief_data(belief_rows_0, belief_rows_1)
    fe_df = _system_free_energy_data(q_empirical, epochs)
    g_composite = _gamma_data(gamma_rows_0, gamma_rows_1, epochs)

    return model_label, t_composite, c_composite, b_composite, fe_df, g_composite


# ---------------------------------------------------------------------------
# Data assembly helpers
# ---------------------------------------------------------------------------

def _target_data(rows_0, rows_1):
    dft1 = pd.DataFrame({'Target': rows_0, 'Agent': 'strong'})
    dft2 = pd.DataFrame({'Target': rows_1, 'Agent': 'weak'})
    return pd.concat([dft1, dft2], ignore_index=True)


def _convergence_data(rows_0, rows_1):
    dfc1 = pd.DataFrame(rows_0).melt()
    dfc1.columns = ["Time", "Distance from Target"]
    dfc1['Agent'] = 'strong'
    dfc2 = pd.DataFrame(rows_1).melt()
    dfc2.columns = ["Time", "Distance from Target"]
    dfc2['Agent'] = 'weak'
    return pd.concat([dfc1, dfc2], ignore_index=True)


def _belief_data(rows_0, rows_1):
    dfb1 = pd.DataFrame(rows_0).melt()
    dfb1.columns = ["Relative Location", "Belief"]
    dfb1['Agent'] = 'strong'
    dfb2 = pd.DataFrame(rows_1).melt()
    dfb2.columns = ["Relative Location", "Belief"]
    dfb2['Agent'] = 'weak'
    return pd.concat([dfb1, dfb2], ignore_index=True)


def _system_free_energy_data(q_empirical, epochs):
    global_p = initialize_b_star([0], 30)
    global_p = global_p[0]
    global_p = global_p / np.sum(global_p)
    fe = np.zeros(epochs)
    for t in range(epochs):
        q = (q_empirical[t] + 0.01) / (np.sum(q_empirical[t]) + 0.01 * ENV_SIZE)
        fe[t] = KL(q, global_p)
    return pd.DataFrame(fe, columns=['FE'])


def _gamma_data(rows_0, rows_1, epochs):
    """Average gamma evolution across all runs."""
    g0 = np.array([g[:epochs + 1] for g in rows_0 if len(g) >= epochs + 1])
    g1 = np.array([g[:epochs + 1] for g in rows_1 if len(g) >= epochs + 1])
    if len(g0) == 0 or len(g1) == 0:
        return pd.DataFrame()
    mean_g0 = g0.mean(axis=0)
    mean_g1 = g1.mean(axis=0)
    df = pd.DataFrame({
        'Epoch': list(range(epochs + 1)) * 2,
        'Gamma': np.concatenate([mean_g0, mean_g1]),
        'Agent': ['strong'] * (epochs + 1) + ['weak'] * (epochs + 1),
    })
    return df
