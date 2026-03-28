# Section 5.6 Formal Proof Write-up

## 5.6.1 Bounded experience effect on effective mobilisation time

Theorem `T5.6-1` proves that the experience-driven reduction in effective mobilisation time is bounded. The Lean identifier `Section5_6.«T5.6-1»` establishes four results in a single conjunction. First, the effective time `tauEffBase` equals `tau - (lambda * tau) * u`, confirming the linear speed-up form. Second, the absolute slope is bounded by `lambda * tau`. Third, the effective time lies in the closed interval `[(1 - lambda) * tau, tau]` for all `u` in `[0, 1]`. Fourth, the fractional maximum improvement from full expertise (`u = 0` to `u = 1`) is exactly `lambda`.

This bound is structural, not empirical. No matter how skilled the agent, the speed-up factor `(1 - lambda * u)` cannot reduce effective time below `(1 - lambda) * tau`. The bounded multiplier maps directly to the thesis claim that experience produces meaningful but capped improvements in the time allowance ratio.

## 5.6.2 Diminishing sensitivity of mobilisation to experience under rising structural drag

Theorem `T5.6-2` proves that as complexity potential `CP` increases, three quantities decrease simultaneously: the sensitivity `|dr/du|` of the time allowance ratio to experience, the ratio `r` itself, and any monotone function of `r` (including mobilisation fraction and cognitive headroom). The Lean identifier `Section5_6.«T5.6-2»` takes two arbitrary monotone functions `fA` and `fB` as parameters and proves the ordering for both, generalising the result beyond any single mobilisation model.

The proof relies on `tauTotal_mono_cp`, which shows that total mobilisation time grows with `CP`. Since `r = tauD / tauEff` and `tauEff` grows with `CP`, the ratio `r` falls. The sensitivity `rSensitivityU`, defined as `(tauD * lambda) / ((1 - lambda * u)^2 * tauTotal)`, falls because its denominator grows with `CP` while its numerator is invariant.

At the computational level, the manifest records `|dr/du|` at `CP = 0` as 0.709 and at `CP = 6` as 0.253. The decay ratio is 0.357, meaning that roughly two thirds of the marginal value of experience has been lost by the time structural drag reaches `CP = 6`. Figure `analysis/section5_6/result/figures/fig_5_7_schematic_sensitivity_decay.pdf` plots this decay.

## 5.6.3 Structural dominance threshold

Theorem `T5.6-3` proves that above a critical complexity potential `CP*`, structural interventions that reduce `CP` by a fraction `k` produce larger gains than the full experience effect (from `u = 0` to `u = 1`). The Lean identifier `Section5_6.«T5.6-3»` proves four results. First, the structural reduction gain `cpReductionGain` is monotone in `CP`. Second, the partial derivative of total time with respect to `CP` equals `tau0 * gamma`. Third, the absolute sensitivity to experience equals `lambda * tauTotal`. Fourth, whenever `CP >= CP*` where `CP* = lambda / (gamma * (k - lambda))`, the structural gain exceeds the experience gain.

The helper lemmas `cpReductionGain_closed_form` and `experienceMaxGain_closed_form` provide the algebraic simplifications that make the threshold comparison tractable. The closed form for structural gain is `tau0 * gamma * k * CP`, which grows linearly with `CP`. The closed form for experience gain is `lambda * tauTotal`, which also grows with `CP` but at a slower rate when `k > lambda`. The crossover point `CP*` is the exact threshold at which the structural lever overtakes the experience lever.

This result provides the formal basis for the thesis claim that systems engineering capability (modelled as structural interventions on `CP`, `tau0`, and `h`) dominates experience in high-complexity regimes.

## 5.6.4 Step changes in complexity potential produce downward jumps in the time allowance ratio

Theorem `T5.6-4` proves that a discrete increase in `CP` from `cpBefore` to `cpAfter` produces a strict decrease in the time allowance ratio `r`, and that the difference `r(cpAfter) - r(cpBefore)` is negative. The Lean identifier `Section5_6.«T5.6-4»` uses `tauTotal_strict_cp` to establish the strict ordering of total mobilisation times, then propagates the strict inequality through the ratio definition.

This connects burst dynamics (Section 5.1) to regime shifts. When a boundary event introduces new interfaces or governance requirements, `CP` increases in a step. The ratio `r` drops immediately, potentially crossing a threshold below which mobilisation fraction collapses and performance degrades. The step-drop structure means that the system does not gradually transition between regimes but instead shifts abruptly.

Figure `analysis/section5_6/result/figures/fig_5_6_schematic_experience_effect.pdf` shows the experience effect at four `CP` levels (0.5, 2.0, 4.0, 7.0). As `CP` rises, the curves flatten, illustrating the diminishing returns proved in T5.6-2 and the dominance shift formalised in T5.6-3.

## Embedded hypotheses

### H11 SE capability dominates in high complexity

Formal basis: `T5.6-2` and `T5.6-3`.

Prediction: in high-`CP` regimes, interventions that reduce complexity potential, baseline stage times, and preserve cognitive reserve `h` (process maturity, interface standards, automation) produce stronger performance effects than training and experience programmes. The bounded multiplier `lambda` caps the experience effect, while structural interventions scale linearly with the drag they offset.

### H12 Experience effect weakens after bursts

Formal basis: `T5.6-1`, `T5.6-2`, and `T5.6-4`.

Prediction: teams with strong experience profiles perform well until a complexity burst shifts the operating regime. After the burst, the sensitivity of `r` to `u` has decayed (T5.6-2) and the ratio `r` has dropped in a step (T5.6-4), so unchanged experience levels produce visibly worse outcomes.

## Required reasoning chain

1. Effective mobilisation time is defined as `tauEff = (1 - lambda * u) * tau0 * (1 + gamma * CP)`, with `u` in `[0, 1]` and `lambda` in `[0, 1]` bounding the speed-up.
2. T5.6-1 establishes that the fractional improvement from experience is exactly `lambda`, independent of `CP`.
3. The time allowance ratio `r = tauD / tauEff` falls as `CP` rises because `tauEff` grows with `CP` while `tauD` (disturbance timescale) is fixed.
4. T5.6-2 proves that both `r` and `|dr/du|` decrease with `CP`, so the marginal value of experience diminishes under structural drag.
5. Structural interventions reduce `CP` by a fraction `k`, giving a gain that grows linearly with `CP`. T5.6-3 identifies the crossover `CP*` above which this gain exceeds the full experience effect.
6. T5.6-4 connects burst dynamics to regime shifts: step increases in `CP` produce step drops in `r`, meaning the transition is abrupt rather than gradual.
7. The sensitivity grid (`analysis/section5_6/result/tables/tab_5_6_sensitivity_grid.csv`) provides the numerical complement, showing `|dr/du|` across a 121 x 81 grid of `CP` and `u` values with parameters from the manifest.
