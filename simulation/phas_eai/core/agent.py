"""
Extended Active Inference Agent for the PHAS-EAI model.
=======================================================

Reproduces the Kaufmann et al. (2021) agent logic and adds:
  - Designed cognitive reserve (h): minimum sensory floor
  - Niche construction: agents mark detections in the shared environment
  - Dynamic shared expectations (Phi): per-agent evolving gamma
  - Patterned Practices: accept periodic belief synchronisation

All extensions are toggled by constructor parameters so that experiments
can compose features freely.
"""

import numpy as np

from .environment import ENV_SIZE


# ---------------------------------------------------------------------------
# Constants (matching Kaufmann)
# ---------------------------------------------------------------------------
ACTIONS = (0, -1, 1)
ACTIONS_SQUARED = (
    (0, 0), (0, -1), (0, 1),
    (-1, 0), (-1, -1), (-1, 1),
    (1, 0), (1, -1), (1, 1),
)
SENSE_DECAY_RATE = np.log(4) / ENV_SIZE
N_STEPS = 50
LEARNING_RATE = 0.7


# ---------------------------------------------------------------------------
# Helper functions (matching Kaufmann)
# ---------------------------------------------------------------------------

def softmax(b):
    e = np.exp(b - b.max())
    return e / np.sum(e)


def D_softmax(q):
    return np.diag(q) - np.outer(q, q)


def model_encoding(b):
    return softmax(b)


def variational_density(b):
    return model_encoding(b)


def logdiff(p1, p2):
    return np.log(p1) - np.log(p2)


def KLv(p1, p2):
    return np.multiply(p1, logdiff(p1, p2))


def KL(p1, p2):
    return np.sum(KLv(p1, p2))


def rerange(q, a):
    return a * q + (1 - a) / ENV_SIZE


def dynamic_rerange(q):
    B_MIN = -10
    b = np.log(q)
    b -= np.max(b)
    b_hat = np.maximum(b, B_MIN)
    return softmax(b_hat)


def p_action(q):
    p = []
    q_hat = 0.9 * q / np.max(q)
    p.append(q_hat)
    A = (1 - q_hat) / (np.roll(q, 1) + np.roll(q, -1))
    p.append(np.roll(q, -1) * A)
    p.append(np.roll(q, +1) * A)
    return np.array(p)


def initialize_b_star(targets, sharpness=6, env_size=ENV_SIZE):
    b_star = []
    B_STANDARD = np.array([
        np.exp(-((i - env_size / 2) / (env_size / sharpness)) ** 2)
        for i in range(env_size)
    ])
    for target in targets:
        b_star.append(np.roll(B_STANDARD, target - env_size // 2))
    return b_star


# ---------------------------------------------------------------------------
# Extended Agent
# ---------------------------------------------------------------------------

class PHASAgent:
    """
    An active inference agent extended with PHAS-EAI constructs.

    Parameters
    ----------
    agent_id : int
        Unique identifier (0 or 1 in 2-agent case).
    psi : int
        Initial position in the circular environment.
    b_star : list of ndarray
        Desired belief distributions [shared, own_private, partner_private].
    perceptiveness : float
        Maximum sensory probability (physical capability).
    alterity : float
        Degree of Theory of Mind (alpha in Kaufmann).
    alignment : float
        Degree of goal alignment (gamma in Kaufmann).  Used as the initial
        value when dynamic_gamma is enabled.
    h : float
        Designed cognitive reserve in (0, 1].  h=0 reproduces Kaufmann.
        h>0 provides a sensory floor: effective detection probability is
        at least h * (1/ENV_SIZE) everywhere.
    environment : Environment or None
        Shared environment for niche construction.  If None, niche
        construction is disabled.
    dynamic_gamma : bool
        If True, gamma evolves based on interaction success.
    gamma_lr : float
        Learning rate for dynamic gamma updates.
    """

    def __init__(
        self,
        agent_id,
        psi,
        b_star,
        perceptiveness,
        alterity,
        alignment,
        h=0.0,
        environment=None,
        dynamic_gamma=False,
        gamma_lr=0.01,
    ):
        self.agent_id = agent_id
        self.psi = psi
        self.alterity = alterity
        self.alignment = alignment
        self.h = h
        self.environment = environment
        self.dynamic_gamma = dynamic_gamma
        self.gamma_lr = gamma_lr

        # Base sensory dynamics (Kaufmann original)
        env = np.array(range(ENV_SIZE))
        self._base_sensory = perceptiveness * np.exp(
            -SENSE_DECAY_RATE * np.minimum(
                np.abs(env - int(ENV_SIZE / 2)),
                np.abs(env - int(ENV_SIZE / 2) - ENV_SIZE),
            )
        )

        # Designed cognitive reserve: max-floor guarantee (Theorem T5.3-4)
        # H_cog >= h: the floor holds regardless of skill, without degrading peak.
        if h > 0:
            h_floor = h * (1.0 / ENV_SIZE)
            self.sensory_dynamics = np.maximum(h_floor, self._base_sensory)
        else:
            self.sensory_dynamics = self._base_sensory.copy()

        # Internal beliefs
        self.b = (np.zeros(ENV_SIZE), np.zeros(ENV_SIZE))

        # Desired beliefs (goal alignment applied)
        self.b_star = (
            b_star[0] + (1 - alignment) * b_star[1],
            b_star[0] + (1 - alignment) * b_star[2],
        )

        self.q = (variational_density(self.b[0]), variational_density(self.b[1]))
        self.q_star = (
            variational_density(self.b_star[0]),
            variational_density(self.b_star[1]),
        )
        self.p_ap = p_action(self.q_star[1])

        self.a = (0, 0)
        self.a_pp = 0
        self.delta = 0

        # Free energy from previous epoch (for dynamic gamma)
        self._prev_fe = None

        # Traces
        self.psi_trace = [psi]
        self.psi_partner_trace = []
        self.b_own_trace = [self.sensory_dynamics]
        self.b_partner_trace = [self.sensory_dynamics]
        self.s_trace = []
        self.a_trace = []
        self.gamma_trace = [alignment]
        self.fe_trace = []

    # ------------------------------------------------------------------
    # Effective sensory dynamics (with environment salience)
    # ------------------------------------------------------------------

    def _effective_sensory(self):
        """Sensory dynamics modulated by environment salience."""
        if self.environment is not None and self.environment.niche_construction:
            return np.clip(
                self.sensory_dynamics * self.environment.get_salience(),
                0.0, 0.99,
            )
        return self.sensory_dynamics

    # ------------------------------------------------------------------
    # Free energy computations (matching Kaufmann)
    # ------------------------------------------------------------------

    def free_energy_own(self, a, p_own, p_partner):
        p_partner_reranged = rerange(p_partner, self.alterity)
        p_partner_shifted = np.roll(p_partner_reranged, self.delta + a[0] - a[1])
        return KL(self.q_star[0], dynamic_rerange(p_own * p_partner_shifted))

    def free_energy_partner(self, a, p_own, p_partner):
        p_own_reranged = rerange(p_own, self.alterity ** 2)
        p_own_shifted = np.roll(p_own_reranged, -(self.delta + a[0] - a[1]))
        return KL(self.q_star[1], dynamic_rerange(p_partner * p_own_shifted))

    def fe_gradient(self, b_prime, p_own, p_partner, delta_prime):
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

    # ------------------------------------------------------------------
    # Generative densities
    # ------------------------------------------------------------------

    def generative_density_own(self, a=(0, 0)):
        q_own = self.q[0]
        sd = self._effective_sensory()
        sd_s = sd if self.s == 1 else 1 - sd
        return np.roll(sd_s * q_own, a[0])

    def generative_density_partner(self, a=(0, 0)):
        q_own = self.q[0]
        q_partner = self.q[1]
        p_delta = np.roll(q_own, -self.delta)
        p_app = np.roll(self.p_ap[ACTIONS.index(self.a_pp)], -self.a_pp)
        p_j_prior = q_partner
        p_j_posterior = p_delta * p_app * p_j_prior
        return np.roll(p_j_posterior, a[1])

    # ------------------------------------------------------------------
    # Step
    # ------------------------------------------------------------------

    def step(self):
        """Execute one simulation step: sense, decide, act, update beliefs."""
        sd = self._effective_sensory()

        # Sense
        s = int(np.random.random() < sd[self.psi])
        self.s = s

        # Niche construction: mark successful detections
        if s == 1 and self.environment is not None:
            self.environment.mark_detection(self.psi)

        # Decide: evaluate free energy for all action pairs
        fes = []
        epsilon = 0.999 + np.random.random(3) * 0.002
        for a in ACTIONS_SQUARED:
            p_own = self.generative_density_own(a)
            p_partner = self.generative_density_partner(a)
            fes.append([
                self.free_energy_own(a, p_own, p_partner) * epsilon[a[0] + 1],
                self.free_energy_partner(a, p_own, p_partner),
            ])
        fes_t = np.transpose(fes)
        actions_index = [np.argmin(fes_t[0]), np.argmin(fes_t[1])]
        a = (
            ACTIONS_SQUARED[actions_index[0]][0],
            ACTIONS_SQUARED[actions_index[1]][1],
        )
        self.a = a

        # Track total free energy for this step (for dynamic gamma)
        current_fe = fes_t[0][actions_index[0]] + fes_t[1][actions_index[1]]
        self.fe_trace.append(current_fe)

        delta_prime = self.delta + a[0] - a[1]

        # Act
        psi = (self.psi + a[0]) % ENV_SIZE
        self.psi = psi

        p_own = self.generative_density_own()
        p_partner = self.generative_density_partner()
        b_prime = np.array([np.roll(self.b[0], a[0]), np.roll(self.b[1], a[1])])

        # Update beliefs via gradient descent
        for _step in range(N_STEPS):
            b_prime -= LEARNING_RATE * self.fe_gradient(
                b_prime,
                np.roll(p_own, a[0]),
                np.roll(p_partner, a[1]),
                delta_prime,
            )

        self.b = b_prime
        self.q = (variational_density(b_prime[0]), variational_density(b_prime[1]))

        # Dynamic gamma update (Extension 3)
        if self.dynamic_gamma and self._prev_fe is not None:
            delta_fe = self._prev_fe - current_fe  # positive = improvement
            self.alignment = np.clip(
                self.alignment + self.gamma_lr * delta_fe,
                0.0, 1.0,
            )
        self._prev_fe = current_fe
        self.gamma_trace.append(self.alignment)

        # Log traces
        self.s_trace.append(s)
        self.a_trace.append(a[0])
        self.psi_trace.append(psi)
        self.psi_partner_trace.append(psi - self.delta)
        self.b_own_trace.append(model_encoding(b_prime[0]))
        self.b_partner_trace.append(model_encoding(b_prime[1]))

    # ------------------------------------------------------------------
    # Patterned Practices: belief synchronisation (Extension 4)
    # ------------------------------------------------------------------

    def sync_partner_belief(self, partner_own_belief, fidelity=0.5):
        """
        Synchronise this agent's partner model with the partner's actual
        self-belief.  Models a structured interaction event (stand-up,
        threat-modelling session, retrospective).

        Parameters
        ----------
        partner_own_belief : ndarray
            The partner's belief about its own position (b[0]).
        fidelity : float
            Blending weight in [0, 1].  0 = no update, 1 = full replacement.
        """
        self.b = (
            self.b[0],
            fidelity * partner_own_belief + (1 - fidelity) * self.b[1],
        )
        self.q = (self.q[0], variational_density(self.b[1]))

    # ------------------------------------------------------------------
    # Convergence logging (matching Kaufmann)
    # ------------------------------------------------------------------

    def log_convergence(self, targets):
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
        if c0[-1] <= c1[-1]:
            return 'shared target', c0
        else:
            return 'unshared target', c1
