# Traceability Map

| Formal element | Lean identifier | Thesis source mapping |
|---|---|---|
| Organisation parameters (A, B, H, tauEff) | `Section5_2.Organisation` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` Eq. (24)-(26), Eq. (32) |
| Mobilisation fraction `f(r) = min(1, r^epsilon)` | `Section5_2.mobilisation` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` Eq. (24) mobilisation share |
| Time-conditioned useful count `A~ = A f_A` | `Section5_2.Atilde` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` Eq. (25) effective useful count |
| Time-conditioned survivable count `B~ = B f_B` | `Section5_2.Btilde` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` Eq. (26) effective survivable count |
| Magnitude limit `M_0` (useful-option threshold) | `Section5_2.M0` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` absorbable magnitude lower bound |
| Magnitude limit `M_max` (survivable-option threshold) | `Section5_2.Mmax` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` absorbable magnitude upper bound |
| Static forms `M0Static`, `MmaxStatic` | `Section5_2.M0Static`, `Section5_2.MmaxStatic` | Slow-regime reduction when mobilisation saturates |
| Resilience score (piecewise-linear) | `Section5_2.resilienceScore` | Section 5.2 thesis text, piecewise `R(M, tau_d)` expression |
| Comparative advantage `Delta R = R_S - R_L` | `Section5_2.deltaR` | Section 5.2 thesis text, advantage field definition |
| T5.2-1 Boundedness and boundary values | `Section5_2.«T5.2-1»` | Resilience score bounded in [0, 1] with saturation and collapse |
| T5.2-2 Fast-regime sufficient condition | `Section5_2.«T5.2-2»` | Sufficient condition for VSE advantage via factor decomposition |
| T5.2-3 Slow-regime static reduction | `Section5_2.«T5.2-3»` | Mobilisation saturation eliminates speed advantage |
| T5.2-4 Parity boundary existence | `Section5_2.«T5.2-4»` | Intermediate value theorem applied to constructive sign reversal |
| Fast-regime positive witness | `Section5_2.deltaR_fast_positive_on_interval` | Constructive proof that `Delta R > 0` at `tau_d = 1/2` for M in [2.1, 2.3] |
| Slow-regime negative witness | `Section5_2.deltaR_slow_negative_on_interval` | Constructive proof that `Delta R < 0` at `tau_d = 10` for M in [2.1, 2.3] |
| Constructive sign reversal | `Section5_2.t5_2_4_sign_interval` | Existence of non-empty magnitude band with sign change across regimes |
| Mobilisation saturation lemma | `Section5_2.mobilisation_eq_one_of_saturated` | `f = 1` when `tauEff <= tauD` |
| M0 static reduction | `Section5_2.M0_eq_static_of_saturated` | `M_0` equals static form under saturation |
| Mmax static reduction | `Section5_2.Mmax_eq_static_of_saturated` | `M_max` equals static form under saturation |
| Resilience linear interpolation | `Section5_2.resilience_eq_linear_of_between` | Degradation formula in the intermediate band |
| VSE constructive parameters | `Section5_2.orgVSE` (A=2, B=6, H=0.9, tauEff=1) | `analysis/section5_2/result/tables/tab_5_2_parameter_set.csv` |
| Large-org constructive parameters | `Section5_2.orgLarge` (A=4, B=8, H=1.0, tauEff=5) | `analysis/section5_2/result/tables/tab_5_2_parameter_set.csv` |
| Heatmap figure | `fig_5_2_resilience_advantage_heatmap` | `analysis/section5_2/result/figures/fig_5_2_resilience_advantage_heatmap.pdf` |
