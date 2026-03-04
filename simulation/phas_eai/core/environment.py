"""
Mutable environment for the PHAS-EAI extended model.
====================================================

Extends Kaufmann's static 1D circular environment with:
  - Mutable salience map (Regimes of Attention / niche construction)
  - Disturbance events (target relocation)

The environment is shared between all agents, so one agent's niche
construction benefits every agent (collective environmental shaping).
"""

import numpy as np


# ---------------------------------------------------------------------------
# Environmental constants (matching Kaufmann)
# ---------------------------------------------------------------------------
ENV_SIZE = 60
SHORTEST_PATH = ENV_SIZE // 3
TARGET_DELTA = ENV_SIZE // 3

# ---------------------------------------------------------------------------
# Niche construction defaults
# ---------------------------------------------------------------------------
DEFAULT_BOOST = 0.15          # salience boost per successful detection
DEFAULT_KERNEL_RADIUS = 3     # half-width of the Gaussian boost kernel
DEFAULT_SALIENCE_DECAY = 0.99 # per-epoch multiplicative decay


def _gaussian_kernel(radius):
    """Normalised Gaussian kernel for local salience boost."""
    x = np.arange(-radius, radius + 1, dtype=float)
    kernel = np.exp(-0.5 * (x / max(radius / 2, 1)) ** 2)
    return kernel / kernel.max()


class Environment:
    """
    Shared 1D circular environment with mutable salience.

    Parameters
    ----------
    env_size : int
        Number of discrete positions on the ring.
    niche_construction : bool
        If True, agents can boost local salience when they detect targets.
    boost : float
        Magnitude of the salience boost per detection event.
    kernel_radius : int
        Half-width of the Gaussian kernel applied around the detection site.
    salience_decay : float
        Per-epoch multiplicative decay of accumulated salience (prevents
        unbounded growth and models information staleness).
    """

    def __init__(
        self,
        env_size=ENV_SIZE,
        niche_construction=False,
        boost=DEFAULT_BOOST,
        kernel_radius=DEFAULT_KERNEL_RADIUS,
        salience_decay=DEFAULT_SALIENCE_DECAY,
    ):
        self.env_size = env_size
        self.niche_construction = niche_construction
        self.boost = boost
        self.kernel_radius = kernel_radius
        self.salience_decay = salience_decay

        # Salience map: multiplier on sensory dynamics.  1.0 = no change.
        self.salience = np.ones(env_size)
        self._kernel = _gaussian_kernel(kernel_radius)

        # Target positions (set by experiment)
        self.shared_target = None
        self.targets = {}  # agent_id -> [shared, private]

        # Disturbance state
        self._original_shared_target = None
        self._original_targets = {}
        self.disturbed = False

    # ------------------------------------------------------------------
    # Target management
    # ------------------------------------------------------------------

    def set_targets(self, shared_target, private_targets):
        """
        Configure target positions.

        Parameters
        ----------
        shared_target : int
            Position of the shared target (food source).
        private_targets : dict
            {agent_id: private_target_position}
        """
        self.shared_target = shared_target
        for agent_id, priv in private_targets.items():
            self.targets[agent_id] = [shared_target, priv]
        self._original_shared_target = shared_target
        self._original_targets = {k: list(v) for k, v in self.targets.items()}

    # ------------------------------------------------------------------
    # Niche construction (Regimes of Attention)
    # ------------------------------------------------------------------

    def mark_detection(self, position):
        """
        Boost salience around a position where an agent detected a signal.

        This models niche construction: the agent modifies its shared
        environment by leaving a trace (deploying monitoring, adding a
        dashboard, marking a location).
        """
        if not self.niche_construction:
            return

        k = self._kernel
        r = self.kernel_radius
        for i, weight in enumerate(k):
            idx = (position - r + i) % self.env_size
            self.salience[idx] += self.boost * weight

    def decay_salience(self):
        """Apply per-epoch decay to salience (information staleness)."""
        if not self.niche_construction:
            return
        # Decay toward 1.0 (baseline), not toward 0
        self.salience = 1.0 + (self.salience - 1.0) * self.salience_decay

    def get_salience(self):
        """Return the current salience map."""
        return self.salience.copy()

    # ------------------------------------------------------------------
    # Disturbance events (Extension 5)
    # ------------------------------------------------------------------

    def apply_disturbance(self, rng=None):
        """
        Relocate all targets to new random positions, preserving relative
        geometry (shared target moves, private targets follow).

        Parameters
        ----------
        rng : np.random.RandomState, optional
            Random state for reproducibility.
        """
        if rng is None:
            rng = np.random
        new_shared = rng.randint(0, self.env_size)
        offset = new_shared - self.shared_target
        self.shared_target = new_shared
        for agent_id in self.targets:
            self.targets[agent_id] = [
                new_shared,
                (self._original_targets[agent_id][1] + offset) % self.env_size,
            ]
        self.disturbed = True

    def reset_disturbance(self):
        """Restore original target positions."""
        self.shared_target = self._original_shared_target
        self.targets = {k: list(v) for k, v in self._original_targets.items()}
        self.disturbed = False
