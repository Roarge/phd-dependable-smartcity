# Traceability Map

| Formal element | Lean identifier | Thesis source mapping |
|---|---|---|
| Dot product for structural drag sensitivities and CP vector | `Section5_3.dot` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` stage drag equation, sensitivity vectors |
| Stage response time with structural drag `tau_stage = tau0 * (1 + gamma^T CP)` | `Section5_3.stageTime` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` Eq. for stage-specific response time |
| Total response time decomposition `tau = tau_detect + tau_decide + tau_execute` | `Section5_3.tauTotal` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` three-stage decomposition |
| Skill multiplier `sigma_tau = 1 - lambda_tau * u(E, MF)` | `Section5_3.sigmaTau` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` effective time multiplier |
| Effective mobilisation time `tau_eff = sigma_tau * tau` | `Section5_3.tauEff` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` Eq. for effective response time |
| Time allowance ratio `r = tau_d / tau_eff` | `Section5_3.ratio` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` Eq. for time allowance ratio |
| Generic mobilisation fraction `min(1, r^epsilon)` | `Section5_3.mobilisationFraction` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` mobilisation fraction family |
| Cognitive headroom `H_cog = h + (1 - h) * u * q` | `Section5_3.Hcog` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` cognitive headroom with designed reserve |
| Total headroom `H_tot = H_phys * H_cog` | `Section5_3.Htot` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` combined headroom |
| Useful-variety threshold `M_0 = k * A_eff^alpha_A * H^beta_H` | `Section5_3.M0Thresh` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` magnitude threshold for useful variety |
| Survivable-variety threshold `M_max = k * B_eff^beta_B * H^beta_H` | `Section5_3.MmaxThresh` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` magnitude threshold for survivable variety |
| T5.3-1 Stage CP sensitivity: monotonicity of tau and tau_eff | `Section5_3.«T5.3-1»` (lines 272-333) | Chapter 5.3 "Response Time Decomposition and Structural Drag" paragraph on intervention design |
| T5.3-2 Mobilisation monotonicity: reduced r lowers all mobilisation fractions | `Section5_3.«T5.3-2»` (lines 334-359) | Chapter 5.3 "Nested Option Sets and Time Conditioning" paragraph on time allowance ratio |
| T5.3-3 Skill bound: sigma_tau in [1 - lambda_tau, 1], tau_eff bounded | `Section5_3.«T5.3-3»` (lines 360-371) | Chapter 5.3 "Skill Is Bounded" paragraph and formal result |
| T5.3-4 Cognitive headroom floor: h <= H_cog and monotonicity in h | `Section5_3.«T5.3-4»` (lines 372-411) | Chapter 5.3 "Designed Cognitive Reserve" paragraph and formal result |
| T5.3-5 Resilience threshold with mobilisation: unified H5, H6, H7 | `Section5_3.«T5.3-5»` (lines 412-471) | Chapter 5.3 "Hypotheses" section, H5/H6/H7 statements |
| H5 proposition schema: time pressure reduces realised resilience | `Section5_3.H5Prop` | Chapter 5.3 hypothesis H5 |
| H6 proposition schema: diminishing returns from expertise | `Section5_3.H6Prop` | Chapter 5.3 hypothesis H6 |
| H7 proposition schema with worst-case witness | `Section5_3.H7Prop` | Chapter 5.3 hypothesis H7 |
| Dot product non-negativity | `Section5_3.dot_nonneg` | Supporting lemma for T5.3-1 |
| Dot product monotonicity in CP | `Section5_3.dot_mono` | Supporting lemma for T5.3-1 |
| Stage time non-negativity | `Section5_3.stageTime_nonneg` | Supporting lemma for T5.3-1 |
| Stage time strict monotonicity in baseline | `Section5_3.stageTime_strict_mono_tau0` | Supporting lemma for T5.3-1, stage independence |
| Stage time monotonicity in CP | `Section5_3.stageTime_mono_cp` | Supporting lemma for T5.3-1, CP sensitivity |
| Total response time non-negativity | `Section5_3.tauTotal_nonneg` | Supporting lemma for T5.3-1 |
| Total time strict in detect baseline | `Section5_3.tauTotal_strict_tauDetect0` | Supporting lemma for T5.3-1, detect stage |
| Total time strict in decide baseline | `Section5_3.tauTotal_strict_tauDecide0` | Supporting lemma for T5.3-1, decide stage |
| Total time strict in execute baseline | `Section5_3.tauTotal_strict_tauExecute0` | Supporting lemma for T5.3-1, execute stage |
| Total time monotone in CP | `Section5_3.tauTotal_mono_cp` | Supporting lemma for T5.3-1, CP channel |
| Skill multiplier bounds | `Section5_3.sigmaTau_bounds` | Supporting lemma for T5.3-1 and T5.3-3 |
| Effective time monotone in tau | `Section5_3.tauEff_mono_tau` | Supporting lemma for T5.3-1, CP propagation to tau_eff |
| Effective time interval | `Section5_3.tauEff_interval` | Supporting lemma for T5.3-3 and T5.3-5 |
| Ratio non-increase | `Section5_3.ratio_nonincrease` | Supporting lemma for T5.3-2 and T5.3-5 |
| Cognitive headroom lower bound | `Section5_3.Hcog_lower_bound` | Supporting lemma for T5.3-4 |
| Cognitive headroom monotone in h | `Section5_3.Hcog_mono_h` | Supporting lemma for T5.3-4 |
| Useful-variety threshold monotone in A_eff | `Section5_3.M0Thresh_mono_Aeff` | Supporting lemma for T5.3-5 (H5 branch) |
| Survivable-variety threshold monotone in B_eff | `Section5_3.MmaxThresh_mono_Beff` | Supporting lemma for T5.3-5 (H5 branch) |
