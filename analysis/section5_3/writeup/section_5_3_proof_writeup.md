# Section 5.3 Formal Proof Write-up

## 5.3.1 Stage-specific sensitivity and structural drag

Theorem `T5.3-1` proves that the total response time `tauTotal` is strictly monotone in each stage baseline (`tauDetect0`, `tauDecide0`, `tauExecute0`) and monotone in the complexity-potential vector `cp`. The proof decomposes the three-stage sum and applies `stageTime_strict_mono_tau0` for each baseline independently, establishing that reducing one stage baseline reduces total response time regardless of the other two stages. The CP monotonicity result uses `stageTime_mono_cp` across all three stages and `dot_mono` for the inner product of sensitivity vectors with the CP vector.

The theorem also chains through to `tauEff`: because `sigmaTau` is non-negative (via `sigmaTau_bounds`), `tauEff` inherits the CP monotonicity of `tauTotal` through `tauEff_mono_tau`. The final conjunct proves the lower bound `(1 - lambdaTau) * tau <= tauEff`, establishing that even maximal skill cannot compress effective time below the floor set by the structural drag term and the skill ceiling.

This result validates the thesis claim that interventions must be targeted to specific stages and specific complexity factors. An investment in telemetry reduces `tauDetect0` but cannot affect `tauDecide0` or `tauExecute0`, and the formal separation of the three stages makes this distinction machine-checked.

## 5.3.2 Mobilisation monotonicity under time pressure

Theorem `T5.3-2` proves that when the disturbance timescale `tauD` shrinks or the effective response time `tauEff` grows, the time allowance ratio `r = tauD / tauEff` does not increase, and therefore the mobilisation fractions `fA`, `fB`, `fC` do not increase. The proof applies `ratio_nonincrease` for the ratio ordering, then uses the monotonicity of each mobilisation function (`hMonA`, `hMonB`, `hMonC`) to propagate the ordering. The saturation clause confirms that when `r >= 1`, all three mobilisation fractions equal 1.

The monotonicity assumption on `fA`, `fB`, `fC` is parametric: the theorem holds for any family of monotone, saturating mobilisation functions. The computational figure `analysis/section5_3/result/figures/fig_5_3_inset_mobilisation.png` illustrates two specific instances from the `min(1, r^epsilon)` family with `epsilon_a = 0.8` and `epsilon_b = 1.4`, showing the power-law region below `r = 1` and saturation above.

## 5.3.3 Skill is bounded

Theorem `T5.3-3` proves that `sigmaTau` lies in `[1 - lambdaTau, 1]` and that `tauEff` lies in `[(1 - lambdaTau) * tau, tau]`. The proof applies `sigmaTau_bounds` directly for the multiplier interval and `tauEff_interval` for the effective time interval. Both results rely on `lambdaTau` being in `[0, 1)` and `u` being in `[0, 1]`.

The formal consequence is that no amount of expertise can reduce effective mobilisation time below `(1 - lambdaTau) * tau`. When structural drag inflates `tau` through the CP-sensitive stage times, the floor `(1 - lambdaTau) * tau` rises proportionally. Skill compresses the time by at most a factor of `lambdaTau`, but the compressed time remains anchored to the structurally determined total. This provides the formal basis for the thesis claim that in high-drag environments, expertise produces diminishing returns on response outcomes.

## 5.3.4 Cognitive headroom floor from designed reserve

Theorem `T5.3-4` proves two properties of the cognitive headroom function `Hcog`. First, `Hcog h u q >= h` for all valid skill and task-demand values (`Hcog_lower_bound`). Second, `Hcog` is monotone in the designed reserve parameter `h` (`Hcog_mono_h`).

The lower bound holds because the term `(1 - h) * u * q` is non-negative whenever `h <= 1`, `u >= 0`, and `q >= 0`. Monotonicity in `h` uses the algebraic identity that increasing `h` raises the floor term by more than it reduces the variable term, provided `u * q <= 1`.

The worst-case witness is `u = 0` (no skill, or maximum task demand), which yields `Hcog = h` exactly. This confirms that the designed reserve is the only cognitive headroom available when personnel are inexperienced, inflexible, or overwhelmed. The thesis case material connects this to concrete investments: automated vulnerability monitoring (Paper V), collaborative threat modelling (Paper III), and AI-assisted requirements review (Paper IV).

## 5.3.5 Resilience threshold with mobilisation

Theorem `T5.3-5` unifies the three hypothesis schemas `H5Prop`, `H6Prop`, and `H7Prop` under a single set of explicit assumptions. The proof proceeds in three branches.

For H5 (time pressure reduces realised resilience): the theorem proves that reduced `r` lowers mobilisation fractions and, through `M0Thresh_mono_Aeff` and `MmaxThresh_mono_Beff`, lowers both the useful-variety threshold `M_0` and the survivable-variety threshold `M_max`. The chain from ratio ordering through mobilisation monotonicity to threshold monotonicity is fully formal.

For H6 (diminishing returns from expertise): the theorem proves that `tauEff` is bounded in the interval `[(1 - lambdaTau) * tau, tau]` for all skill values in `[0, 1]`. This reuses `tauEff_interval` and confirms that the skill speed-up saturates at `lambdaTau`.

For H7 (designed reserve outperforms experience investment): the theorem proves monotonicity of `Hcog` in `h` for all skill levels, proves the lower bound `h <= Hcog` for each reserve value, and exhibits the worst-case witness `u = 0` where `Hcog h 0 q = h` by direct computation (`ring`). The existential witness establishes that the designed reserve guarantee is tight, not merely a loose bound.

## Embedded hypotheses

### H5 Time pressure reduces realised resilience

Formal basis: `T5.3-2` and `T5.3-5` (H5 branch).

Prediction: faster-evolving disturbances (shorter `tauD`) reduce mobilisation fractions and threshold scores even when the feasible option set and team are unchanged. The formal chain runs from ratio ordering (`ratio_nonincrease`) through mobilisation monotonicity to `M0Thresh` and `MmaxThresh` monotonicity.

### H6 Diminishing returns from expertise

Formal basis: `T5.3-3` and `T5.3-5` (H6 branch).

Prediction: in high-complexity settings, the correlation between team experience and response performance should be weaker than in low-complexity settings, because `tauEff` converges towards `(1 - lambdaTau) * tau` as `u` increases, and the structural drag term `tau` dominates.

### H7 Designed reserve outperforms experience investment

Formal basis: `T5.3-4` and `T5.3-5` (H7 branch).

Prediction: teams with strong automation and pre-authorised actions should show more consistent incident-response performance across personnel changes, because `Hcog >= h` holds independently of `u`. The worst-case witness at `u = 0` confirms the guarantee is binding, not slack.

## Required reasoning chain

1. Response time decomposes into three stages (detect, decide, execute), each inflated by a CP-sensitive structural drag term, formalised in `stageTime` and `tauTotal`.
2. Each stage baseline and the CP vector contribute independently to total response time, with strict monotonicity in baselines and monotonicity in CP (T5.3-1).
3. Skill compresses effective time through `sigmaTau`, but the compression is bounded in `[1 - lambdaTau, 1]` (T5.3-3). The floor rises with structural drag.
4. The time allowance ratio `r = tauD / tauEff` determines mobilisation fractions. Reduced `tauD` or increased `tauEff` lowers `r` and thereby lowers all mobilisation fractions (T5.3-2).
5. Designed cognitive reserve `h` provides a floor on cognitive headroom that holds at all skill levels and all task demands (T5.3-4). The guarantee is tight (worst-case witness at `u = 0`).
6. The unified theorem T5.3-5 connects time pressure (H5), skill saturation (H6), and designed reserve (H7) into a single formal result with explicit assumptions and machine-checked proofs.

## Figures

Figure `analysis/section5_3/result/figures/fig_5_3_response_time_drag.pdf` is the Chapter 5.3 anchor. The diagram shows the three-stage decomposition, CP-sensitive drag entering each stage through sensitivity vectors, skill compression through `sigmaTau`, and the resulting `tauEff` feeding into the time allowance ratio and mobilisation fractions.

Figure `analysis/section5_3/result/figures/fig_5_3_inset_mobilisation.pdf` shows two mobilisation curves from the `min(1, r^epsilon)` family. The power-law region below `r = 1` demonstrates the sensitivity of mobilisation to time pressure. Above `r = 1`, both curves saturate at 1, confirming the formal saturation property used in T5.3-2 and T5.3-5.
