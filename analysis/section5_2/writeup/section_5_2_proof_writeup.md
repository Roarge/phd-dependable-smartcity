# Section 5.2 Formal Proof Write-up

## 5.2.1 Boundedness of the resilience score

Theorem `T5.2-1` proves that the piecewise-linear resilience score `resilienceScore` is bounded in [0, 1] and attains its boundary values at the magnitude limits. Specifically, given the gap condition `M0Val < MmaxVal`, the theorem establishes four properties: non-negativity, the upper bound of one, saturation to one when `M <= M0Val`, and collapse to zero when `MmaxVal <= M`. The supporting lemmas `resilience_nonneg`, `resilience_le_one`, `resilience_eq_one_of_le_M0`, and `resilience_eq_zero_of_Mmax_le` decompose the proof into independent steps. The linear interpolation lemma `resilience_eq_linear_of_between` confirms the degradation formula `(MmaxVal - M) / (MmaxVal - M0Val)` in the intermediate band.

This formalises the piecewise resilience expression in the thesis text. Full absorption holds when disturbance magnitude falls below the useful-option threshold `M_0`. Total collapse holds when magnitude exceeds the survivable-option threshold `M_max`. Between these limits, resilience degrades linearly with increasing magnitude.

## 5.2.2 Sufficient condition for fast-regime VSE advantage

Theorem `T5.2-2` proves a sufficient condition under which the smaller organisation (VSE) achieves higher magnitude limits than the larger organisation in the scarce-time branch. The proof decomposes each magnitude limit into a product of the corresponding large-organisation limit and a dimensionless factor. `factorM0` captures the ratio for the useful-option threshold and `factorMmax` captures the ratio for the survivable-option threshold. When both factors exceed one, the VSE magnitude limits exceed those of the larger organisation.

The factor expressions encode the competition between three terms: static variety ratio (smaller for the VSE), mobilisation-speed ratio (larger for the VSE due to lower `tauEff`), and headroom ratio. The speed ratio enters as `(tauEff_L / tauEff_S) ^ (alpha * epsilon)`, so the mobilisation advantage grows with the exponent product. This captures the thesis claim that faster mobilisation can overcome smaller static variety in the fast-disturbance regime.

The preconditions `A_S < A_L`, `B_S < B_L`, and `tauEff_S < tauEff_L` encode the structural asymmetry: the VSE has less variety but responds faster. The theorem does not require specific parameter values, providing a general algebraic condition for the advantage.

## 5.2.3 Slow-regime reversal to static dominance

Theorem `T5.2-3` proves that when `tauD` is large enough to saturate mobilisation for both organisations (`tauEff <= tauD`), the time-conditioned magnitude limits reduce to their static forms `M0Static` and `MmaxStatic`. The key lemma `mobilisation_eq_one_of_saturated` shows that the mobilisation fraction reaches its ceiling of one when the time-allowance ratio `tauD / tauEff` is at least one. Once mobilisation saturates, the speed advantage disappears entirely.

The theorem further proves that under saturation, if the VSE has smaller useful variety (`orgS.A < orgL.A`) and no greater headroom (`orgS.H <= orgL.H`), then the VSE useful-option threshold is weakly dominated: `M0 orgS <= M0 orgL`. The proof uses monotonicity of power functions (`pow_le_pow_left0`) and multiplication by the non-negative scale factor `k`.

This formalises the thesis claim that the VSE advantage reverses in slow disturbances. When both organisations have ample time to mobilise their full variety, the larger organisation's greater static resources dominate.

## 5.2.4 Existence of a parity boundary

Theorem `T5.2-4` proves the existence of a disturbance timescale `tauStar` in the interval `[1/2, 10]` at which `deltaRExample tauStar (11/5) = 0`, given continuity of the advantage function on that interval. The proof applies the intermediate value theorem (`intermediate_value_Icc'`) to a function that is positive at `tauD = 1/2` and negative at `tauD = 10`.

The sign witnesses come from two constructive lemmas. `deltaR_fast_positive_on_interval` proves that at `tauD = 1/2`, the VSE resilience score is strictly positive while the large-organisation score is zero (magnitude exceeds its `Mmax`), giving `deltaR > 0` for magnitudes in `[21/10, 23/10]`. `deltaR_slow_negative_on_interval` proves that at `tauD = 10`, the large organisation absorbs the same magnitudes fully (`R = 1`) while the VSE degrades, giving `deltaR < 0`.

The constructive parameter witness uses `orgVSE` (A=2, B=6, H=0.9, tauEff=1) and `orgLarge` (A=4, B=8, H=1.0, tauEff=5) with unit scaling exponents. The manifest reports a numerical parity estimate of `tauStar ~ 2.475` at reference magnitude `M = 2.2`.

Figure `analysis/section5_2/result/figures/fig_5_2_resilience_advantage_heatmap.pdf` visualises the `deltaR` field over the `(tauD, M)` plane. The zero contour corresponds to the parity boundary proved to exist by `T5.2-4`. Warm colours mark the positive-advantage region (fast disturbances, moderate magnitudes) and cool colours mark the reversal region (slow disturbances or extreme magnitudes). The manifest records a maximum advantage of 1.0 at `(tauD=0.06, M=0.1)` and a positive-advantage area of 9.8828 in the sampled plane.

Table `analysis/section5_2/result/tables/tab_5_2_parameter_set.csv` documents the constructive parameter values for both organisations and the shared scaling constants.

## Embedded hypotheses

### H3 VSE advantage is regime-dependent

Formal basis: `T5.2-1`, `T5.2-2`, `T5.2-3`, and `T5.2-4`.

Prediction: the VSE resilience advantage is positive for fast disturbances and moderate magnitudes when the mobilisation-speed ratio overcomes the variety deficit, but becomes negative beyond a bounded magnitude band as `M` approaches the VSE `Mmax` due to limited headroom and survivable variety. `T5.2-2` gives the algebraic sufficient condition for the fast regime. `T5.2-3` proves reversal under saturation. `T5.2-4` proves the parity boundary exists between the two regimes.

### H4 Burst-induced regime shift

Formal basis: `T5.2-4` combined with Section 5.1 burst results (`A4`, `B3`).

Prediction: a burst increase in complexity potential or coordination drag increases `tauEff`, shifting the parity boundary leftward and shrinking the positive-advantage region. An organisation that was in the positive-advantage region before the burst may find itself in the negative region afterwards, without any change in team composition or individual expertise. The constructive witness parameters allow numerical estimation of the shift magnitude.

## Required reasoning chain

1. The resilience score is defined as a clamped piecewise-linear function of disturbance magnitude, bounded by `M_0` (useful-option threshold) and `M_max` (survivable-option threshold), implemented by `resilienceScore`.
2. Both thresholds depend on time-conditioned effective counts, which are products of static variety and mobilisation fraction, implemented by `Atilde`, `Btilde`, and `mobilisation`.
3. The VSE has lower static variety (`A`, `B`) and lower headroom (`H`) but lower effective mobilisation time (`tauEff`), encoded in `orgVSE` and `orgLarge`.
4. In the fast regime, the mobilisation fraction differentiates the two organisations because the VSE saturates its mobilisation sooner. `T5.2-2` gives the sufficient condition for this to produce higher VSE magnitude limits.
5. In the slow regime, both organisations saturate mobilisation, eliminating the speed advantage. `T5.2-3` proves the limits reduce to static forms where larger variety dominates.
6. The transition between regimes is continuous. `T5.2-4` applies the intermediate value theorem to a constructive sign reversal, proving the parity boundary exists.
7. The comparative advantage field `deltaR` maps the full `(tauD, M)` plane, with the zero contour marking the regime boundary that separates VSE advantage from reversal.
