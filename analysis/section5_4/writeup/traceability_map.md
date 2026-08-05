# Traceability Map

| Formal element | Lean identifier | Thesis source mapping |
|---|---|---|
| Success set `A_{g,ρ}` as threshold-qualified subset | `Section5_4.successSet`, `Section5_4.successSetFinset` | `Analytical Models/Functional-Information-and-Cost-of-Choice-in-PHAS.md` Eq. (29) |
| Success count `|A_{g,ρ}|` | `Section5_4.successCount` | `Analytical Models/Functional-Information-and-Cost-of-Choice-in-PHAS.md` Eq. (29) cardinality |
| Total configuration count `C = |O^Δ|` | `Section5_4.configCount` | `Analytical Models/Complexity-in-PHAS.md` Eq. (16) |
| Success share `p_g(ρ) = |A_{g,ρ}| / C` | `Section5_4.successShare` | `Analytical Models/Functional-Information-and-Cost-of-Choice-in-PHAS.md` Eq. (30) |
| Design-time functional information `I_g^*(ρ) = log2 C - log2 |A_{g,ρ}|` | `Section5_4.IStar` | `Analytical Models/Functional-Information-and-Cost-of-Choice-in-PHAS.md` Eq. (31) |
| Time allowance ratio `r = τ_d / τ_eff` | `Section5_4.ratio` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` Eq. (24), Eq. (25) |
| Time-conditioned usable success count `Ã_{g,ρ}(τ_d, τ_eff)` | `Section5_4.usableSuccessCount` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` Eq. (26), Eq. (32) |
| Operational functional information `I_g^{op}(ρ, τ_d)` | `Section5_4.IOp` | `Analytical Models/Functional-Information-and-Cost-of-Choice-in-PHAS.md` Eq. (33) |
| Finite image of performance map | `Section5_4.perfImage` | Finite option space assumption in thesis Section 5.4 |
| Count-based `I_g^*` form for sensitivity | `Section5_4.IStarCounts` | `Analytical Models/Functional-Information-and-Cost-of-Choice-in-PHAS.md` Eq. (31) count form |
| Count-and-time `I_g^{op}` form for sensitivity | `Section5_4.IOpCounts` | `Analytical Models/Functional-Information-and-Cost-of-Choice-in-PHAS.md` Eq. (33) count form |
| Complexity-only indicator `log2 C` (time-invariant) | `Section5_4.complexityOnly` | `Analytical Models/Complexity-in-PHAS.md` Eq. (16) in bits |
| T5.4-1 Threshold shrinkage: set nesting, antitone count, non-decreasing `I_g^*` | `Section5_4.«T5.4-1»` | Thesis Section 5.4 "Threshold Sensitivity and Step Behaviour" paragraph 1 |
| T5.4-2 Finite-image step behaviour: piecewise-constant counts and jump points | `Section5_4.«T5.4-2»` | Thesis Section 5.4 "Threshold Sensitivity and Step Behaviour" paragraph 2 |
| T5.4-3 Time pressure raises `I_g^{op}` through reduced `f_A` | `Section5_4.«T5.4-3»` | Thesis Section 5.4 "Operational Functional Information Under Time Pressure" paragraph 3 |
| T5.4-4 Three-part sensitivity: `C` raises `I_g^*`, `τ_eff` raises `I_g^{op}`, `log2 C` ignores `τ_eff` | `Section5_4.«T5.4-4»` | Thesis Section 5.4 "Operational Functional Information Under Time Pressure" paragraph 4 |
| Subset monotonicity under threshold increase | `Section5_4.successSetFinset_mono_threshold` | Supporting lemma for T5.4-1 set nesting |
| Antitone success count under threshold increase | `Section5_4.successCount_antitone` | Supporting lemma for T5.4-1 cardinality bound |
| Constant count between non-crossing thresholds | `Section5_4.successCount_eq_of_no_crossing` | Supporting lemma for T5.4-2 piecewise-constant property |
| Count change implies crossing performance value | `Section5_4.successCount_change_implies_crossing` | Supporting lemma for T5.4-2 jump-point location |
| Strict `IStar` increase on strict count drop | `Section5_4.IStar_strict_of_count_drop` | Supporting lemma for T5.4-2 strict monotonicity at jumps |
| Ratio non-increase under `τ_eff` increase | `Section5_4.ratio_nonincrease_of_tauEff_increase` | Supporting lemma for T5.4-3 and T5.4-4 time-pressure direction |
| Synthetic performance distribution (`C = 1024`, six levels) | `analysis/section5_4/result/tables/tab_5_4_synthetic_perf.csv` | Thesis Section 5.4 Figure 5-4 caption and Appendix A.4 |
| Threshold shrinkage figure | `analysis/section5_4/result/figures/fig_5_4_threshold_shrinkage.pdf` | Thesis Figure 5-4 main panel |
| Time-pressure inset figure | `analysis/section5_4/result/figures/fig_5_4_iop_time_pressure.pdf` | Thesis Figure 5-4 optional inset |
