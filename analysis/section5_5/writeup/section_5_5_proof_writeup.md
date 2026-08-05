# Section 5.5 Formal Proof Write-up

## 5.5.1 Perception and communication are noisy channels

Theorem `T5.5-1` proves that non-degenerate noise implies non-zero posterior uncertainty. Given a scalar linear Gaussian channel with noise variance $\sigma^2 > 0$ and prior variance $\sigma_{\text{prior}}^2$, the conjugate posterior variance $\sigma_{\text{post}}^2 = \sigma_{\text{prior}}^2 \sigma^2 / (\sigma_{\text{prior}}^2 + \sigma^2)$ is strictly positive when $\sigma_{\text{prior}}^2 > 0$, and collapses to zero only when the prior is degenerate ($\sigma_{\text{prior}}^2 = 0$). This validates the thesis claim that misinterpretation is a normal operating condition: any agent with non-trivial prior uncertainty retains residual uncertainty after observation.

Theorem `T5.5-4` proves that higher precision (lower $\sigma^2$) monotonically improves expected Gaussian log-likelihood. The proof establishes three results jointly: (1) the derivative `expectedGaussianLogLikelihoodDerivative` is strictly negative for all $\sigma^2 > 0$, confirming that accuracy improves continuously as noise decreases, (2) the derivative remains negative at both comparison points, and (3) for $\sigma_1^2 \le \sigma_2^2$, the expected accuracy at $\sigma_1^2$ is at least as large as at $\sigma_2^2$. The numeric demonstration in the manifest confirms the monotonicity: accuracy at $\sigma^2 = 0.1$ is $-0.268$, whereas accuracy at $\sigma^2 = 1.0$ is $-1.419$, yielding an accuracy gain of $1.151$ bits for the tenfold precision improvement.

Figure `analysis/section5_5/result/figures/fig_5_5_precision_accuracy_demo.pdf` visualises this relationship.

## 5.5.2 Shared expectations are convex mixtures

Theorem `T5.5-2` proves that the shared expectation $\Phi = \gamma f(\psi) + (1 - \gamma) \mu$ lies within the convex hull of $\mu$ and $f(\psi)$ when $\gamma \in [0, 1]$. The proof handles both orderings ($\mu \le f(\psi)$ and $f(\psi) \le \mu$) by rewriting the shared expectation in displacement form via the auxiliary lemmas `sharedExpectation_as_mu` and `sharedExpectation_as_peer`. The second conjunct confirms that the multi-peer extension `multiSharedExpectation` unfolds definitionally to the averaging sum $\frac{1}{n} \sum_i [\gamma_i f(\psi_i) + (1 - \gamma_i) \mu]$, matching the thesis equation.

The numeric demonstration uses three peers with signals $(0.22, 0.64, 0.9)$ and authority weights $(0.25, 0.55, 0.8)$ against $\mu = 0.5$. The resulting $\Phi$ range spans $[0.539, 0.632]$, confirming that the multi-peer aggregation stays within a bounded neighbourhood of the agent's own model.

## 5.5.3 Affordance reduces free energy

Theorem `T5.5-3` proves that increasing the affordance probability $p(a)$ strictly reduces the affordance-augmented free energy $F = D - \ln p(a)$ for any fixed divergence $D$. The proof relies on the strict monotonicity of $\ln$ for positive arguments: $p_1 < p_2$ implies $\ln p_1 < \ln p_2$, so $-\ln p_2 < -\ln p_1$, and the free energy at $p_2$ is strictly lower. This validates the thesis claim that actions with high affordance (pre-approved, tool-supported, default) are favoured under the free-energy minimisation objective, and that low-affordance actions are deprioritised under workload pressure even by competent teams.

## 5.5.4 Authority-weight asymmetry produces coordination friction

Theorem `T5.5-5` proves three results about authority-weight asymmetry in the two-agent case. Given $\gamma_A \ne \gamma_B$ and $f(\psi) \ne \mu$:

1. The shared expectations $\Phi_A$ and $\Phi_B$ are distinct (they cannot agree when the authority weights and the signal differ from the prior).
2. Coordination friction $|\Phi_A - \Phi_B|$ is strictly positive.
3. Friction is monotone in the weight gap: if $|\gamma_A - \gamma_B| \le |\gamma_A' - \gamma_B'|$, then $|\Phi_A - \Phi_B| \le |\Phi_{A'} - \Phi_{B'}|$.

The factorisation lemma `coordinationFriction_factorised` decomposes friction into $|\gamma_A - \gamma_B| \cdot |f(\psi) - \mu|$, showing that friction is the product of weight divergence and signal divergence. The numeric demonstration reports a maximum friction of $0.070$ across the tested configurations.

This validates the thesis claim that authority-weight asymmetry across stakeholders (for example, a regulator weighting safety signals heavily while a contractor weights cost signals) produces coordination friction proportional to both the weight difference and the signal difference.

## Embedded hypotheses

### H9 Regimes of attention reduce drift

Formal basis: `T5.5-4` and `T5.5-3`.

`T5.5-4` proves that reducing noise variance monotonically improves expected accuracy, supporting the claim that improving telemetry and data quality (reducing $\omega$) improves detection performance. `T5.5-3` proves that increasing affordance strictly reduces free energy for desired actions, supporting the claim that making dependability actions pre-approved and tool-supported counteracts drift.

Prediction: teams operating under a regime of attention (structured telemetry, pre-authorised escalation, machine-readable evidence chains) should show shorter detection times and more consistent escalation behaviour than teams with equivalent technical capability but weaker signal infrastructure.

### H10 Authority-weight asymmetry predicts friction

Formal basis: `T5.5-5` and `T5.5-2`.

`T5.5-5` proves that authority-weight asymmetry generates strictly positive coordination friction that is monotone in the weight gap. `T5.5-2` establishes that shared expectations remain bounded (convex mixture), so friction arises not from unbounded divergence but from proportional disagreement.

Prediction: incidents involving multiple stakeholders with documented authority-weight differences should show longer decision phases and higher rates of decision reversal than incidents handled by a single team with aligned authority weights.

## Required reasoning chain

1. Sensing and communication are modelled as noisy channels $s = g(\eta) + \omega$, implemented by `sensorySignal` and `peerInput`, with noise variance $\sigma^2 > 0$.
2. Posterior uncertainty is strictly positive for non-degenerate priors (`T5.5-1`), establishing that residual ambiguity is structural.
3. Precision monotonically improves expected accuracy (`T5.5-4`), so reducing noise is a direct lever on inference quality.
4. Shared expectations are convex mixtures of peer signals and own model (`T5.5-2`), bounded by the authority weight $\gamma \in [0, 1]$.
5. Authority-weight asymmetry factorises into weight divergence times signal divergence (`coordinationFriction_factorised`), producing monotone coordination friction (`T5.5-5`).
6. Affordance directly modulates free energy (`T5.5-3`), so making desired actions more affordable shifts action selection without changing beliefs.
7. A regime of attention combines noise reduction (point 3), affordance increase (point 6), and authority-weight alignment (point 5) into a single design pattern for dependability.

Figure `analysis/section5_5/result/figures/fig_5_5_phas_eai_assurance_loop.pdf` is the Chapter 5.5 anchor, showing the assurance loop where noisy signs and communication update beliefs, authority weights shape shared expectations, and affordance shifts free-energy-ranked actions.
