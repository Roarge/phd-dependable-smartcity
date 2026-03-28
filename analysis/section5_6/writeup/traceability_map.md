# Traceability Map

| Formal element | Lean identifier | Thesis source mapping |
|---|---|---|
| Stage-time model `tau_stage = tau0 * (1 + gamma * CP)` | `Section5_6.tauStage` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` stage-time definition |
| Aggregate mobilisation time before skill | `Section5_6.tauTotal` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` total mobilisation time |
| Effective mobilisation time with bounded skill `(1 - lambda * u) * tau` | `Section5_6.tauEff` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` effective time with experience factor |
| Reduced-form effective time for bounded-multiplier proofs | `Section5_6.tauEffBase` | Helper for T5.6-1 proofs, derived from `tauEff` with fixed `tau` |
| Time allowance ratio `r = tauD / tauEff` | `Section5_6.ratio` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` time allowance ratio definition |
| Sensitivity of `r` to experience `\|dr/du\|` | `Section5_6.rSensitivityU` | Closed-form derivative used in Section 5.6 sensitivity analysis |
| Mobilisation fraction `min(1, r^eps)` | `Section5_6.mobilisationFraction` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` mobilisation fraction |
| Partial derivative of `tau` with respect to `CP` | `Section5_6.partialTauCP` | Sensitivity comparison in T5.6-3 derivation |
| Partial derivative of `tauEff` with respect to `u` | `Section5_6.partialTauEffU` | Experience sensitivity in T5.6-3 derivation |
| Structural CP reduction gain `tau(CP) - tau((1-k)*CP)` | `Section5_6.cpReductionGain` | SE capability proxy: proportional CP reduction by fraction `k` |
| Maximum experience-driven gain `tau(CP) - tauEff(CP, lambda, 1)` | `Section5_6.experienceMaxGain` | Full experience effect from `u=0` to `u=1` |
| Dominance threshold `CP* = lambda / (gamma * (k - lambda))` | `Section5_6.dominanceThreshold` | Crossover point where structural interventions exceed experience effect |
| Monotonicity of total time in `CP` | `Section5_6.tauTotal_mono_cp` | Supporting lemma: structural drag grows with complexity potential |
| Strict monotonicity of total time in `CP` | `Section5_6.tauTotal_strict_cp` | Supporting lemma for T5.6-4 strict inequality |
| Non-negativity of total time | `Section5_6.tauTotal_nonneg` | Well-formedness guard for division in ratio proofs |
| Positivity of total time | `Section5_6.tauTotal_pos` | Well-formedness guard for strict division in ratio proofs |
| T5.6-1 Bounded experience effect | `Section5_6.«T5.6-1»` | Section 5.6 formal derivation: experience bound, fractional improvement equals `lambda` |
| T5.6-2 Diminishing sensitivity under rising CP | `Section5_6.«T5.6-2»` | Section 5.6 formal derivation: sensitivity decay, ratio ordering, monotone function propagation |
| T5.6-3 Structural dominance threshold | `Section5_6.«T5.6-3»` | Section 5.6 formal derivation: SE capability dominates above `CP*`, H11 formal basis |
| T5.6-4 Step drop in ratio from CP burst | `Section5_6.«T5.6-4»` | Section 5.6 formal derivation: burst dynamics produce abrupt regime shift, H12 formal basis |
| Closed form of CP reduction gain | `Section5_6.cpReductionGain_closed_form` | Algebraic simplification: `tau0 * gamma * k * CP` |
| Closed form of experience max gain | `Section5_6.experienceMaxGain_closed_form` | Algebraic simplification: `lambda * tauTotal` |
| Figure 5-6: Experience effect at varying CP | `analysis/section5_6/result/figures/fig_5_6_schematic_experience_effect.pdf` | Chapter 5.6 anchor figure: `r` versus `u` at CP levels 0.5, 2.0, 4.0, 7.0 |
| Figure 5-7: Sensitivity decay | `analysis/section5_6/result/figures/fig_5_7_schematic_sensitivity_decay.pdf` | Chapter 5.6 anchor figure: `\|dr/du\|` versus CP at u levels 0.1, 0.4, 0.7 |
| Table 5-6: Sensitivity grid | `analysis/section5_6/result/tables/tab_5_6_sensitivity_grid.csv` | 121 x 81 grid of `\|dr/du\|` across CP and u values |
