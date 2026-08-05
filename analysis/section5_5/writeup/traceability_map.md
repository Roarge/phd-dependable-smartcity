# Traceability Map

| Formal element | Lean identifier | Thesis source mapping |
|---|---|---|
| Sensory signal channel `s = g(eta) + omega` | `Section5_5.sensorySignal` | Section 5.5 "Perception and Communication Are Noisy Channels", Eq. `s = g(eta) + omega` |
| Peer input channel `c_in = g(psi) + omega` | `Section5_5.peerInput` | Section 5.5 "Perception and Communication Are Noisy Channels", Eq. `c_in = g(psi) + omega` |
| Accuracy-minus-complexity objective | `Section5_5.accuracyObjective` | Action ranking criterion in PHAS-EAI model |
| Shared expectation `Phi = gamma f(psi) + (1-gamma) mu` | `Section5_5.sharedExpectation` | Section 5.5 "Shared Expectations and Authority Weights", Eq. `Phi = gamma f(psi) + (1-gamma) mu` |
| Multi-peer shared expectation with per-peer `gamma_i` | `Section5_5.multiSharedExpectation` | Section 5.5 "Shared Expectations and Authority Weights", Eq. `Phi = (1/n) sum [gamma_i f(psi_i) + (1-gamma_i) mu]` |
| Gaussian conjugate posterior variance | `Section5_5.posteriorVariance` | Scalar conjugate Gaussian form, precision = `1/sigma^2` |
| Affordance-augmented free energy `F = D - ln p(a)` | `Section5_5.freeEnergyWithAffordance` | Section 5.5 "Affordance and Drift", affordance term `-ln p(a)` |
| Expected Gaussian log-likelihood (accuracy proxy) | `Section5_5.expectedGaussianLogLikelihood` | Section 5.5 precision discussion, `E[ln p(s\|eta)] = -0.5*(ln(2*pi*sigma^2)+1)` |
| Derivative of accuracy w.r.t. noise variance | `Section5_5.expectedGaussianLogLikelihoodDerivative` | Closed-form derivative confirming monotonic precision-accuracy relationship |
| Coordination friction `\|Phi_A - Phi_B\|` | `Section5_5.coordinationFriction` | Section 5.5 "Shared Expectations and Authority Weights", authority-weight asymmetry |
| Shared expectation difference factorisation | `Section5_5.sharedExpectation_diff` | Algebraic identity `Phi_A - Phi_B = (gamma_A - gamma_B)(f(psi) - mu)` |
| Shared expectation as displacement from own model | `Section5_5.sharedExpectation_as_mu` | Rewriting `Phi = mu + gamma(f(psi) - mu)` for convexity proof |
| Shared expectation as displacement from peer | `Section5_5.sharedExpectation_as_peer` | Rewriting `Phi = f(psi) + (1-gamma)(mu - f(psi))` for convexity proof |
| Coordination friction factorisation | `Section5_5.coordinationFriction_factorised` | Product form `\|gamma_A - gamma_B\| * \|f(psi) - mu\|` |
| T5.5-1 Non-degenerate noise implies positive posterior variance | `Section5_5.«T5.5-1»` | Section 5.5 "Perception and Communication Are Noisy Channels", misinterpretation as normal operating condition |
| T5.5-2 Shared expectations are convex mixtures | `Section5_5.«T5.5-2»` | Section 5.5 "Shared Expectations and Authority Weights", convex hull property and multi-peer averaging |
| T5.5-3 Increasing affordance lowers free energy | `Section5_5.«T5.5-3»` | Section 5.5 "Affordance and Drift", affordance intervention mechanism |
| T5.5-4 Higher precision improves expected accuracy | `Section5_5.«T5.5-4»` | Section 5.5 "Perception and Communication Are Noisy Channels", precision monotonicity |
| T5.5-5 Authority-weight asymmetry yields coordination friction | `Section5_5.«T5.5-5»` | Section 5.5 "Shared Expectations and Authority Weights", friction monotone in weight gap |
