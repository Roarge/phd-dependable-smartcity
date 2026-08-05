# Traceability Map

| Formal element | Lean identifier | Thesis source mapping |
|---|---|---|
| Option count `C = \|O^Δ\|` | `Section5_7.optionCount` | `Analytical Models/Complexity-in-PHAS.md` Eq. (16) |
| Constraint operator `K' = K ∪ K_p` as feasibility filter | `Section5_7.constraintOperator` | `Analytical Models/Complexity-in-PHAS.md` Hard Constraints section |
| Distinct option count under binning map `φ` | `Section5_7.distinctCount` | `Analytical Models/Complexity-in-PHAS.md` Eq. (15b), Eq. (15c), Eq. (15d) |
| Success share `ρ = A/C` | `Section5_7.successShare` | `Analytical Models/Functional-Information-and-Cost-of-Choice-in-PHAS.md` Eq. (30) |
| Functional information in share form `I_g^* = -log2(A/C)` | `Section5_7.IStarShare` | `Analytical Models/Functional-Information-and-Cost-of-Choice-in-PHAS.md` Eq. (31) |
| Operational functional information `I_g^op = log2 C - log2 A - log2 f_A` | `Section5_7.IOpCounts` | `Analytical Models/Functional-Information-and-Cost-of-Choice-in-PHAS.md` Eq. (33) |
| Expected Gaussian log-likelihood accuracy | `Section5_7.expectedAccuracy` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` inference precision term |
| Response-time decomposition with CP-sensitive detection drag | `Section5_7.tauTotal` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` Eq. (24), Eq. (25) |
| Effective response time under expertise multiplier | `Section5_7.tauEff` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` Eq. (26) |
| Time allowance ratio `r = τ_d / τ_eff` | `Section5_7.ratio` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` Eq. (32) |
| Distinctness coarsening lemma | `Section5_7.distinctCount_coarsen` | Composition property for coarsened binning in Chapter 5.7 |
| T5.7-1 Pattern operators are complexity-non-increasing | `Section5_7.«T5.7-1»` | Constraint addition, choice restriction, and distinctness coarsening paragraph in Section 5.7 |
| T5.7-2 Conditional success-share reduction of `I_g^*` | `Section5_7.«T5.7-2»` | Conditional Success-Share Theorem paragraph in Section 5.7 |
| Single-channel reduction: choice only `Δ = -log2 α` | `Section5_7.delta_choice_only` | Joint Intervention Dominance decomposition in Section 5.7 |
| Single-channel reduction: success only `Δ = log2 β` | `Section5_7.delta_success_only` | Joint Intervention Dominance decomposition in Section 5.7 |
| Single-channel reduction: mobilisation only `Δ = log2 γ` | `Section5_7.delta_mobilisation_only` | Joint Intervention Dominance decomposition in Section 5.7 |
| Joint reduction `Δ = -log2 α + log2 β + log2 γ` | `Section5_7.delta_joint` | Joint Intervention Dominance decomposition in Section 5.7 |
| T5.7-3 Joint intervention dominance and additivity | `Section5_7.«T5.7-3»` | Joint Intervention Dominance paragraph in Section 5.7 |
| Response-time monotonicity in CP | `Section5_7.tauTotal_mono_cp` | Bridge from Inference to Mobilisation in Section 5.7 |
| Response-time monotonicity in detection latency | `Section5_7.tauTotal_mono_detect` | Bridge from Inference to Mobilisation in Section 5.7 |
| Response-time positivity | `Section5_7.tauTotal_pos` | Bridge from Inference to Mobilisation in Section 5.7 |
| T5.7-4 Inference-to-mobilisation bridge | `Section5_7.«T5.7-4»` | Bridge from Inference to Mobilisation paragraph in Section 5.7 |
