# Section 5.7 Formal Proof Write-up

## 5.7.1 Patterns as operators on the feasible set

Theorem `T5.7-1` proves that all three pattern operations are complexity-non-increasing. The Lean proof establishes three conjuncts in a single statement:

1. **Constraint addition.** `constraintOperator O kP` filters the option set `O` by an additional predicate `kP`, so its cardinality cannot exceed that of `O`. The proof appeals to `Finset.card_filter_le`.
2. **Choice restriction.** A restricted option set `Orestricted` satisfying `hChoice : Orestricted ⊆ O` has cardinality bounded by `Finset.card_le_card`.
3. **Distinctness coarsening.** A coarser binning map `φ'` that factors through the original map as `φ' = h ∘ φ` produces no more distinct bins. The helper lemma `distinctCount_coarsen` shows that the image of `φ'` is contained in the image of `h` applied to the image of `φ`, and `Finset.card_image_le` bounds the latter.

These three operations correspond directly to the three pattern mechanisms described in the thesis text: adding constraints $K$, restricting choice sets $X_i$, and coarsening the distinctness map $\varphi$.

## 5.7.2 The conditional success-share theorem

Theorem `T5.7-2` proves that if the success share improves (weakly or strictly) after a pattern intervention, then functional information $I_g^*$ cannot increase (and strictly decreases when the share strictly improves). The proof structure is:

- The weak case follows from monotonicity of `log2` applied to the success-share ordering, then negation reversal in the `IStarShare` definition.
- The strict case uses `log2_lt_log2` for the strict share improvement and `linarith` to propagate the strict inequality through the negation.

This theorem provides the formal backing for the claim that patterns reduce the cost of choice by increasing the proportion of satisfactory configurations.

## 5.7.3 Joint intervention dominance

Theorem `T5.7-3` proves two properties of joint interventions on operational functional information:

1. **Additivity.** The joint reduction decomposes exactly into three single-channel reductions. Four helper lemmas (`delta_choice_only`, `delta_success_only`, `delta_mobilisation_only`, `delta_joint`) establish the individual and combined reduction expressions using the `log2_mul` identity. The joint form yields $\Delta I_g^{\text{op}} = (-\log_2 \alpha) + \log_2 \beta + \log_2 \gamma$.
2. **Dominance.** The joint reduction is at least as large as any single-channel reduction alone. This follows because $\alpha \in (0,1)$ makes $-\log_2 \alpha \geq 0$, while $\beta \geq 1$ and $\gamma \geq 1$ make $\log_2 \beta \geq 0$ and $\log_2 \gamma \geq 0$ respectively. Each single-channel reduction is therefore strictly less than the joint reduction whenever the other two channels contribute non-trivially.

The numeric demonstration in `analysis/section5_7/result/tables/tab_5_7_joint_intervention_demo.json` uses baseline parameters ($C = 4096$, $A = 512$, $f_A = 0.35$) with intervention factors ($\alpha = 0.62$, $\beta = 1.4$, $\gamma = 1.25$). The individual reductions are 0.690 bits (choice), 0.485 bits (success), and 0.322 bits (mobilisation). The joint reduction is 1.497 bits, and the additivity residual is $\approx 4.4 \times 10^{-16}$ bits, confirming exact decomposition at machine precision.

## 5.7.4 The inference-to-mobilisation bridge

Theorem `T5.7-4` proves three linked results under explicit bridge assumptions:

1. **Accuracy improvement.** Lower inference variance ($\sigma^2_{\text{low}} \leq \sigma^2_{\text{high}}$) produces higher expected Gaussian log-likelihood accuracy. The proof uses monotonicity of `Real.log` applied to scaled variance terms.
2. **Time-allowance ratio improvement.** Reduced detection latency ($\tau_{\text{detect,new}} \leq \tau_{\text{detect,old}}$) and reduced complexity-potential drag ($cp_{\text{new}} \leq cp_{\text{old}}$) lower effective response time $\tau_{\text{eff}}$, raising the ratio $r = \tau_d / \tau_{\text{eff}}$. Helper lemmas `tauTotal_mono_cp`, `tauTotal_mono_detect`, and `tauTotal_pos` establish the monotonicity chain through the response-time decomposition.
3. **Mobilisation improvement.** For any monotone mobilisation function $f_A$, the improved ratio entails improved mobilisation: $f_A(r_{\text{old}}) \leq f_A(r_{\text{new}})$.

The bridge assumptions connecting inference variance to detection latency and complexity-potential are stated as hypotheses in the proof, explicitly marking them as loans of intelligence. The mechanism is directionally supported but the precise coupling between posterior variance reduction and stage-time reduction is not derived from first principles.

## Embedded hypotheses

### H13 Patterns reduce functional information without reducing resilience

Formal basis: `T5.7-1` and `T5.7-2`.

Prediction: modelling patterns that encode constraints and substitutability reduce total optionality $C$ while increasing the proportion of successful configurations $|A_{g,\rho}|/C$, lowering functional information burden without reducing resilience, provided that useful and survivable variety are preserved. `T5.7-1` proves the non-increasing property on $C$ for all three pattern operations. `T5.7-2` proves that improved success share translates to reduced $I_g^*$.

### H14 Machine-readable traceability reduces noise and improves coordination

Formal basis: `T5.7-4`.

Prediction: machine-readable traceability and evidence chains reduce effective noise and improve the observation mapping, reducing surprise and improving coordination by stabilising shared expectations and shortening detection, decision, and execution cycles. `T5.7-4` proves that lower inference variance improves accuracy, raises the time-allowance ratio, and increases mobilisation fractions under monotone $f_A$.

## Required reasoning chain

1. Patterns are formalised as operators on three elements of the feasible set: constraints (`constraintOperator`), choice sets (subset restriction), and binning maps (`distinctCount` with coarsened `φ`).
2. All three operators are complexity-non-increasing by `T5.7-1`, so pattern adoption cannot increase $C$.
3. The success-share mechanism is formalised in `successShare` and `IStarShare`, with `T5.7-2` proving that improved success share reduces functional information.
4. Joint interventions acting on all three channels (complexity reduction $\alpha$, success expansion $\beta$, mobilisation improvement $\gamma$) decompose additively in the log domain by `T5.7-3`, and the joint reduction dominates each single-channel reduction.
5. The numeric demonstration confirms exact additivity at machine precision with representative parameters.
6. The inference-to-mobilisation bridge in `T5.7-4` connects lower inference variance to higher accuracy, shorter effective response time, and improved mobilisation, linking the PHAS-EAI inference model to the resilience machinery.
7. Bridge assumptions are explicitly marked as loans of intelligence, preserving the proof's epistemic transparency.

Figure `analysis/section5_7/result/figures/fig_5_8_patterns_as_operators.pdf` is the Chapter 5.7 anchor, mapping pattern and DE intervention channels to shared model quantities.
