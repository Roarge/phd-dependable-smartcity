"""
Active Inference Model of Collective Intelligence
==================================================

Reproduction of Kaufmann, R., Gupta, P. and Taylor, J. (2021).
"An Active Inference Model of Collective Intelligence."
Entropy, 23(7), 830. https://doi.org/10.3390/e23070830

Original code: Google Colab notebook by the authors.
Ported to standalone Python by Claude for the PhD project of Roar Georgsen.

The simulation models two active inference agents in a 1D circular environment
with food sources (targets). Four models explore a 2x2 matrix of cognitive
capabilities:
  Model 1: Baseline (no ToM, no Goal Alignment)
  Model 2: Theory of Mind only
  Model 3: Goal Alignment only
  Model 4: Theory of Mind + Goal Alignment
"""

import numpy as np
import pandas as pd
from datetime import datetime


# ---------------------------------------------------------------------------
# Environmental constants
# ---------------------------------------------------------------------------
ENV_SIZE = 60                              # Circular environment size (divisible by 6)
SHORTEST_PATH = ENV_SIZE // 3              # Distance from shared target to initial position
TARGET_DELTA = ENV_SIZE // 3               # Distance from shared to unshared target

# ---------------------------------------------------------------------------
# Agent constants
# ---------------------------------------------------------------------------
ACTIONS = (0, -1, 1)                       # Stay, left, right
ACTIONS_SQUARED = (                        # Combined action space for 2 agents
    (0, 0), (0, -1), (0, 1),
    (-1, 0), (-1, -1), (-1, 1),
    (1, 0), (1, -1), (1, 1),
)
MAX_SENSE_PROBABILITY = [0.99, 0.05]       # (strong, weak) agent perceptiveness
SENSE_DECAY_RATE = np.log(4) / ENV_SIZE    # omega: ensures p=0.5 at ENV_SIZE/2

# ---------------------------------------------------------------------------
# Simulation parameters
# ---------------------------------------------------------------------------
EPOCHS = 200                # Number of simulation steps per run
N_STEPS = 50                # Gradient descent steps per epoch for belief update
LEARNING_RATE = 0.7         # SGD learning rate

# ---------------------------------------------------------------------------
# Experimental conditions (2x2 matrix: ToM x Goal Alignment)
# ---------------------------------------------------------------------------
CONDITIONS = {
    1: {'model': 1, 'tom': [0, 0],   'alignment': 0},    # Baseline
    2: {'model': 2, 'tom': [0, 0.5], 'alignment': 0},    # Theory of Mind
    3: {'model': 3, 'tom': [0, 0],   'alignment': 1},    # Goal Alignment
    4: {'model': 4, 'tom': [0, 0.5], 'alignment': 1},    # ToM + Goal Alignment
}


# ═══════════════════════════════════════════════════════════════════════════
# Helper functions
# ═══════════════════════════════════════════════════════════════════════════

def softmax(b):
    """Softmax function with numerical stability shift."""
    e = np.exp(b - b.max())
    return e / np.sum(e)


def D_softmax(q):
    """Jacobian (gradient) of the softmax function."""
    return np.diag(q) - np.outer(q, q)


def model_encoding(b):
    """Probability of occupying specific position as encoded in internal state."""
    return softmax(b)


def model_encoding_derivative(b):
    """Derivative of the model encoding for free energy gradient calculation."""
    return D_softmax(model_encoding(b))


def variational_density(b):
    """
    P(psi | b)
    Agent's belief about external states (current or desired position)
    as encoded in the internal state.
    """
    return model_encoding(b)


def logdiff(p1, p2):
    """Element-wise log difference."""
    return np.log(p1) - np.log(p2)


def KLv(p1, p2):
    """Element-wise KL divergence contributions."""
    return np.multiply(p1, logdiff(p1, p2))


def KL(p1, p2):
    """Kullback-Leibler divergence between two distributions."""
    return np.sum(KLv(p1, p2))


def rerange(q, a):
    """
    Re-range a probability distribution, squishing its range from [0,1]
    to [(1-a)/N, a + (1-a)/N]. Controls the influence of partner model.
    """
    return a * q + (1 - a) / ENV_SIZE


def dynamic_rerange(q):
    """
    Constrain beliefs to the range [e^-10, 1] to prevent overconfidence.
    Implemented as a simple maximum on the log-beliefs.
    """
    B_MIN = -10
    b = np.log(q)
    b -= np.max(b)
    b_hat = np.maximum(b, B_MIN)
    return softmax(b_hat)


def p_action(q):
    """
    Probability of partner action given desired belief distribution q*.
    See Equation (4) in the paper.
    """
    p = []
    q_hat = 0.9 * q / np.max(q)
    p.append(q_hat)                              # a_partner = 0 (stay)
    A = (1 - q_hat) / (np.roll(q, 1) + np.roll(q, -1))
    p.append(np.roll(q, -1) * A)                 # a_partner = -1
    p.append(np.roll(q, +1) * A)                 # a_partner = +1
    return np.array(p)


def initialize_b_star(targets, sharpness=6):
    """
    Create desired belief distributions (Gaussian bumps) centred on targets.
    Returns a list of distributions, one per target.
    """
    b_star = []
    B_STANDARD = np.array([
        np.exp(-((i - ENV_SIZE / 2) / (ENV_SIZE / sharpness)) ** 2)
        for i in range(ENV_SIZE)
    ])
    for target in targets:
        b_star.append(np.roll(B_STANDARD, target - ENV_SIZE // 2))
    return b_star


# ═══════════════════════════════════════════════════════════════════════════
# Agent class
# ═══════════════════════════════════════════════════════════════════════════

class Agent:
    """
    An active inference agent in a 1D circular environment.

    Each agent has:
      - Physical perceptiveness (k): reliability of chemical sensors
      - Alterity (alpha): degree of Theory of Mind
      - Goal Alignment (gamma): degree to which goals are shared

    The agent maintains beliefs about its own position and its partner's
    position, and selects actions to minimise variational free energy.
    """

    def __init__(self, psi, b_star, perceptiveness, alterity, alignment):
        self.psi = psi
        self.alterity = alterity

        # Sensory dynamics: probability of detecting food as a function of
        # distance from the food source
        env = np.array(range(ENV_SIZE))
        self.sensory_dynamics = perceptiveness * np.exp(
            -SENSE_DECAY_RATE * np.minimum(
                np.abs(env - int(ENV_SIZE / 2)),
                np.abs(env - int(ENV_SIZE / 2) - ENV_SIZE)
            )
        )

        # Internal beliefs: (own position, partner position)
        self.b = (np.zeros(ENV_SIZE), np.zeros(ENV_SIZE))

        # Desired beliefs: combine shared and private targets based on alignment
        # b_star[0] = shared target, b_star[1] = own private, b_star[2] = partner private
        self.b_star = (
            b_star[0] + (1 - alignment) * b_star[1],
            b_star[0] + (1 - alignment) * b_star[2],
        )

        self.q = (variational_density(self.b[0]), variational_density(self.b[1]))
        self.q_star = (variational_density(self.b_star[0]), variational_density(self.b_star[1]))
        self.p_ap = p_action(self.q_star[1])

        self.a = (0, 0)
        self.a_pp = 0       # Partner's previous action
        self.delta = 0       # Perceived position difference

        # Traces for logging and plotting
        self.psi_trace = [psi]
        self.psi_partner_trace = []
        self.b_own_trace = [self.sensory_dynamics]
        self.b_partner_trace = [self.sensory_dynamics]
        self.s_trace = []
        self.a_trace = []

    def free_energy_own(self, a, p_own, p_partner):
        """Free energy for own position beliefs (first term of Eq. 5)."""
        p_partner_reranged = rerange(p_partner, self.alterity)
        p_partner_shifted = np.roll(p_partner_reranged, self.delta + a[0] - a[1])
        return KL(self.q_star[0], dynamic_rerange(p_own * p_partner_shifted))

    def free_energy_partner(self, a, p_own, p_partner):
        """Free energy for partner position beliefs (second term of Eq. 5)."""
        p_own_reranged = rerange(p_own, self.alterity ** 2)
        p_own_shifted = np.roll(p_own_reranged, -(self.delta + a[0] - a[1]))
        return KL(self.q_star[1], dynamic_rerange(p_partner * p_own_shifted))

    def fe_gradient(self, b_prime, p_own, p_partner, delta_prime):
        """
        Partial derivatives of the free energy with respect to belief.
        FE = KL(q_own || p_own * q_partner[-delta])
           + KL(q_partner || p_partner * q_own[+delta])
        """
        q_own = variational_density(b_prime[0])
        q_partner = variational_density(b_prime[1])

        p_own_reranged = rerange(p_own, self.alterity ** 2)
        p_partner_reranged = rerange(p_partner, self.alterity)

        p_own_shifted = np.roll(p_own_reranged, -delta_prime)
        p_partner_shifted = np.roll(p_partner_reranged, delta_prime)

        Dq_own = D_softmax(q_own)
        Dq_partner = D_softmax(q_partner)

        v = (
            1 + logdiff(q_own, dynamic_rerange(p_own * p_partner_shifted)),
            1 + logdiff(q_partner, dynamic_rerange(p_partner * p_own_shifted)),
        )

        return np.array([np.dot(Dq_own, v[0]), np.dot(Dq_partner, v[1])])

    def generative_density_own(self, a=(0, 0)):
        """Generative density for own position (sensory model, Section 2.6)."""
        q_own = self.q[0]
        sd = self.sensory_dynamics if self.s == 1 else 1 - self.sensory_dynamics
        return np.roll(sd * q_own, a[0])

    def generative_density_partner(self, a=(0, 0)):
        """Generative density for partner position (partner model, Section 2.7)."""
        q_own = self.q[0]
        q_partner = self.q[1]
        p_delta = np.roll(q_own, -self.delta)
        p_app = np.roll(self.p_ap[ACTIONS.index(self.a_pp)], -self.a_pp)
        p_j_prior = q_partner
        p_j_posterior = p_delta * p_app * p_j_prior
        return np.roll(p_j_posterior, a[1])

    def step(self):
        """Execute one simulation step: sense, decide, act, update beliefs."""
        # Sense: sample sensory state s in {0, 1}
        s = int(np.random.random() < self.sensory_dynamics[self.psi])
        self.s = s

        # Decide: evaluate free energy for all action pairs, pick minimum
        fes = []
        epsilon = 0.999 + np.random.random(3) * 0.002  # break ties randomly
        for a in ACTIONS_SQUARED:
            p_own = self.generative_density_own(a)
            p_partner = self.generative_density_partner(a)
            fes.append([
                self.free_energy_own(a, p_own, p_partner) * epsilon[a[0] + 1],
                self.free_energy_partner(a, p_own, p_partner),
            ])
        fes_t = np.transpose(fes)
        actions_index = [np.argmin(fes_t[0]), np.argmin(fes_t[1])]
        a = (ACTIONS_SQUARED[actions_index[0]][0],
             ACTIONS_SQUARED[actions_index[1]][1])
        self.a = a

        delta_prime = self.delta + a[0] - a[1]

        # Act: update own position (partner action is hypothetical only)
        psi = (self.psi + a[0]) % ENV_SIZE
        self.psi = psi

        p_own = self.generative_density_own()
        p_partner = self.generative_density_partner()
        b_prime = np.array([np.roll(self.b[0], a[0]), np.roll(self.b[1], a[1])])

        # Update beliefs: gradient descent on free energy
        for _step in range(N_STEPS):
            b_prime -= LEARNING_RATE * self.fe_gradient(
                b_prime,
                np.roll(p_own, a[0]),
                np.roll(p_partner, a[1]),
                delta_prime,
            )

        # Store updated state
        self.b = b_prime
        self.q = (variational_density(b_prime[0]), variational_density(b_prime[1]))

        # Log traces
        self.s_trace.append(s)
        self.a_trace.append(a[0])
        self.psi_trace.append(psi)
        self.psi_partner_trace.append(psi - self.delta)
        self.b_own_trace.append(model_encoding(b_prime[0]))
        self.b_partner_trace.append(model_encoding(b_prime[1]))

    def log_convergence(self, targets):
        """
        Calculate absolute distance from closest target at each epoch.
        Returns (target_label, distance_trace).
        """
        psi = np.array(self.psi_trace)
        c0 = np.minimum(
            np.abs(psi - targets[0]),
            np.minimum(
                np.abs(psi - targets[0] - ENV_SIZE),
                np.abs(psi - targets[0] + ENV_SIZE),
            ),
        )
        if len(targets) == 1:
            return 'shared target', c0

        c1 = np.minimum(
            np.abs(psi - targets[1]),
            np.minimum(
                np.abs(psi - targets[1] - ENV_SIZE),
                np.abs(psi - targets[1] + ENV_SIZE),
            ),
        )
        # Return convergence distance from the target the agent ended up nearest
        if c0[-1] <= c1[-1]:
            return 'shared target', c0
        else:
            return 'unshared target', c1


# ═══════════════════════════════════════════════════════════════════════════
# Simulation functions
# ═══════════════════════════════════════════════════════════════════════════

def simulate_agents(agents):
    """Run the simulation for EPOCHS steps with two interacting agents."""
    for epoch in range(EPOCHS):
        # Update each agent's perceived delta (position difference)
        delta_0 = agents[0].psi - agents[1].psi
        agents[0].delta = delta_0
        agents[1].delta = -delta_0

        # Update each agent's perceived partner action
        agents[0].a_pp = agents[1].a[0]
        agents[1].a_pp = agents[0].a[0]

        for agent in agents:
            agent.step()

    # Append final target distribution for plotting
    for agent in agents:
        tgt = model_encoding(agent.b_star[0])
        agent.b_own_trace.append(tgt / tgt.max())
        agent.s_trace.append(
            int(np.random.random() < agent.sensory_dynamics[agent.psi])
        )

    return agents


def single_run(shared_target, perceptiveness, alterity, alignment, plot=False):
    """
    Run a single simulation with two agents.

    Returns convergence data for both agents:
      (target_label_0, convergence_0, belief_end_0, psi_trace_0,
       target_label_1, convergence_1, belief_end_1, psi_trace_1)
    """
    initial_positions = [
        (shared_target + SHORTEST_PATH) % ENV_SIZE,
        (shared_target - SHORTEST_PATH) % ENV_SIZE,
    ]
    target_0 = (shared_target - TARGET_DELTA) % ENV_SIZE
    target_1 = (shared_target + TARGET_DELTA) % ENV_SIZE

    b_star_0 = initialize_b_star([shared_target, target_0, target_1])
    b_star_1 = initialize_b_star([shared_target, target_1, target_0])

    agents = (
        Agent(initial_positions[0], b_star_0,
              perceptiveness[0], alterity[0], alignment),
        Agent(initial_positions[1], b_star_1,
              perceptiveness[1], alterity[1], alignment),
    )
    agents = simulate_agents(agents)

    if plot:
        return agents

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

    return (tgt_0, log_0, b_end_0, agents[0].psi_trace,
            tgt_1, log_1, b_end_1, agents[1].psi_trace)


def simulate_runs(model=1, no_of_cycles=3, verbose=True):
    """
    Run the full simulation for a given model condition.

    Each cycle iterates over all ENV_SIZE possible shared target positions,
    giving no_of_cycles * ENV_SIZE total runs (default: 3 * 60 = 180).

    Returns (model_number, target_df, convergence_df, belief_df, fe_df).
    """
    alterity = CONDITIONS[model]['tom']
    alignment = CONDITIONS[model]['alignment']

    # Accumulators for results
    target_rows_0 = []
    target_rows_1 = []
    convergence_rows_0 = []
    convergence_rows_1 = []
    belief_rows_0 = []
    belief_rows_1 = []
    q_empirical = np.zeros([EPOCHS, ENV_SIZE])

    if verbose:
        print(f"Running Model {model}")
        print(f"  Env Size: {ENV_SIZE}")
        print(f"  Perceptiveness: {MAX_SENSE_PROBABILITY}")
        print(f"  ToM (alterity): {alterity}")
        print(f"  Alignment: {alignment}")
        total_runs = no_of_cycles * ENV_SIZE
        print(f"  Total runs: {total_runs}")
        print(f"  Start: {datetime.now().strftime('%H:%M:%S')}")

    for i in range(no_of_cycles):
        for shared_target in range(ENV_SIZE):
            run_num = i * ENV_SIZE + shared_target
            if verbose and (run_num % 30 == 0):
                print(f"    run {run_num}/{no_of_cycles * ENV_SIZE}")

            t1, c1, b1, psi1, t2, c2, b2, psi2 = single_run(
                shared_target, MAX_SENSE_PROBABILITY, alterity, alignment
            )

            target_rows_0.append(t1)
            target_rows_1.append(t2)
            convergence_rows_0.append(c1)
            convergence_rows_1.append(c2)
            belief_rows_0.append(b1)
            belief_rows_1.append(b2)

            for t in range(EPOCHS):
                q_empirical[t, psi1[t] - shared_target] += 1
                q_empirical[t, psi2[t] - shared_target] += 1

    if verbose:
        print(f"  End: {datetime.now().strftime('%H:%M:%S')}")
        print(f"  Model {model} complete.")

    # Assemble result DataFrames
    t_composite = _target_data(target_rows_0, target_rows_1)
    c_composite = _convergence_data(convergence_rows_0, convergence_rows_1)
    b_composite = _belief_data(belief_rows_0, belief_rows_1)
    fe_df = _system_free_energy_data(q_empirical)

    return model, t_composite, c_composite, b_composite, fe_df


# ═══════════════════════════════════════════════════════════════════════════
# Data assembly helpers
# ═══════════════════════════════════════════════════════════════════════════

def _target_data(rows_0, rows_1):
    """Collate which target each agent converged to."""
    dft1 = pd.DataFrame({'Target': rows_0, 'Agent': 'strong'})
    dft2 = pd.DataFrame({'Target': rows_1, 'Agent': 'weak'})
    return pd.concat([dft1, dft2], ignore_index=True)


def _convergence_data(rows_0, rows_1):
    """Collate distance-from-target traces over time."""
    dfc1 = pd.DataFrame(rows_0)
    dfc1 = dfc1.melt()
    dfc1.columns = ["Time", "Distance from Target"]
    dfc1['Agent'] = 'strong'

    dfc2 = pd.DataFrame(rows_1)
    dfc2 = dfc2.melt()
    dfc2.columns = ["Time", "Distance from Target"]
    dfc2['Agent'] = 'weak'

    return pd.concat([dfc1, dfc2], ignore_index=True)


def _belief_data(rows_0, rows_1):
    """Collate end-state belief distributions."""
    dfb1 = pd.DataFrame(rows_0)
    dfb1 = dfb1.melt()
    dfb1.columns = ["Relative Location", "Belief"]
    dfb1['Agent'] = 'strong'

    dfb2 = pd.DataFrame(rows_1)
    dfb2 = dfb2.melt()
    dfb2.columns = ["Relative Location", "Belief"]
    dfb2['Agent'] = 'weak'

    return pd.concat([dfb1, dfb2], ignore_index=True)


def _system_free_energy_data(q_empirical):
    """
    Calculate system-level free energy from the empirical distribution
    of agent positions across all runs (Eq. 8 in the paper).
    """
    global_p = initialize_b_star([0], 30)
    global_p = global_p[0]  # single target distribution
    global_p = global_p / np.sum(global_p)

    fe = np.zeros(EPOCHS)
    for t in range(EPOCHS):
        q = (q_empirical[t] + 0.01) / (np.sum(q_empirical[t]) + 0.01 * ENV_SIZE)
        fe[t] = KL(q, global_p)

    return pd.DataFrame(fe, columns=['FE'])
