# Section 5.4 Formal Proof Write-up

## 5.4.1 Threshold sensitivity and set nesting

Theorem `T5.4-1` proves three properties jointly. Raising the performance threshold from `rho1` to `rho2 > rho1` produces set nesting (`successSetFinset Perf rho2 ⊆ successSetFinset Perf rho1`), antitone cardinality (`successCount Perf rho2 ≤ successCount Perf rho1`), and non-decreasing functional information (`IStar Perf rho1 ≤ IStar Perf rho2`). The positivity precondition `0 < successCount Perf rho2` ensures the `log2` term is well defined at the higher threshold.

The supporting lemma `successSetFinset_mono_threshold` establishes the subset relation by showing that any element satisfying `rho2 ≤ Perf x` also satisfies `rho1 ≤ Perf x` by transitivity. The cardinality bound `successCount_antitone` follows from `Finset.card_le_card` applied to that subset. The `IStar` inequality follows by `linarith` on the `log2` ordering of the success counts.

The practical implication is that raising performance requirements can only make the search harder, never easier. In the synthetic distribution (`tab_5_4_synthetic_perf.csv`, `C = 1024`, six performance levels), the success count drops from 1024 at `rho < 0.18` to 32 at `rho = 0.91`, producing a corresponding rise in `I_g^*` from 0 to `log2(1024) - log2(32) = 5` bits.

## 5.4.2 Piecewise-constant counts and step behaviour

Theorem `T5.4-2` proves a four-part result. First, the range of `Perf` over a finite type is finite (`Set.finite_range`). Second, between any two thresholds `rho1 ≤ rho2` where no element has performance in `[rho1, rho2)`, the success count is constant (`successCount_eq_of_no_crossing`). Third, whenever the success count does change between two thresholds, at least one realised performance value from `perfImage Perf` lies in that interval (`successCount_change_implies_crossing`). Fourth, a strict count drop with both counts positive implies a strict increase in `IStar` (`IStar_strict_of_count_drop`).

Together these properties establish that `I_g^*` is a step function over the threshold axis, with jumps occurring only at realised performance levels. The synthetic distribution has six such levels (0.18, 0.31, 0.46, 0.62, 0.77, 0.91), producing five jump points. The figure at `analysis/section5_4/result/figures/fig_5_4_threshold_shrinkage.pdf` displays the staircase pattern in `|A_{g,rho}|` and the matching step increases in `I_g^*`.

This result explains why small increases in required performance can produce disproportionate increases in operational difficulty. A threshold that coincides with a cluster of performance values eliminates many configurations at once.

## 5.4.3 Time pressure raises operational functional information

Theorem `T5.4-3` proves that reducing the time allowance ratio `r = tau_d / tau_eff` (by faster disturbance evolution or slower mobilisation) increases `I_g^op`. The proof requires that the mobilisation fraction `fA` is monotone and strictly positive. Under these conditions, a reduced ratio yields a smaller `fA` value, producing a smaller `log2(fA)` term, and therefore a larger `IOp`.

The auxiliary lemma `ratio_nonincrease_of_tauEff_increase` shows that increasing `tau_eff` while holding `tau_d` fixed reduces the ratio, connecting the physical parameter (response latency) to the abstract ratio ordering.

The figure at `analysis/section5_4/result/figures/fig_5_4_iop_time_pressure.pdf` shows the inset panel where `I_g^op` rises above `I_g^*` as `r` decreases. At `r = 0.5` the time-pressure charge is 1 bit. At `r = 0.25` the charge is 2 bits. At `r = 0.1` the charge is approximately 3.3 bits.

## 5.4.4 Three-part sensitivity and the limitation of raw complexity

Theorem `T5.4-4` proves three claims simultaneously using the count-based forms `IStarCounts` and `IOpCounts`. First, increasing total complexity `C` (with `0 < C1 < C2`) strictly increases `IStarCounts`, confirming that a larger option space raises design-time difficulty. Second, increasing `tau_eff` (with `0 < tau_eff1 ≤ tau_eff2`) raises `IOpCounts`, confirming that slower mobilisation increases operational difficulty. Third, the complexity-only indicator `complexityOnly C tau_eff = log2 C` is invariant to `tau_eff`, proved by `rfl`.

This last point is the formal anchor for hypothesis H8. The raw complexity measure `log2 C` cannot distinguish between situations where mobilisation is adequate and situations where time pressure makes most options unreachable. The operational functional information `I_g^op` captures this dimension of difficulty by incorporating the mobilisation fraction, while `log2 C` does not.

## Embedded hypotheses

### H8 Operational functional information predicts outcomes better than raw complexity

Formal basis: `T5.4-3` and `T5.4-4`.

Prediction: incidents where measured `I_g^op` is high (few usable options under time pressure) should show worse outcomes than incidents where `C` is equally high but `I_g^op` is lower (many options pass the threshold and mobilisation is adequate). Theorem `T5.4-4` proves that `log2 C` alone is invariant to `tau_eff`, so it cannot capture this distinction. Theorem `T5.4-3` proves that `I_g^op` strictly responds to mobilisation changes that `log2 C` ignores.

## Required reasoning chain

1. The success set `A_{g,rho}` is defined as the threshold-qualified subset of a finite option space, implemented by `successSetFinset` with filter `rho ≤ Perf x`.
2. Set nesting under threshold increase is proven by `T5.4-1`, so raising the bar can only shrink the set of satisfactory configurations.
3. The finite image of the performance map (`perfImage`) determines the jump points, proven by `T5.4-2`. Between adjacent performance levels, the success count is constant.
4. Design-time functional information `IStar` is `log2 C - log2 |A_{g,rho}|`, with monotonicity in the threshold established by `T5.4-1` and strict increases at jump points by `T5.4-2`.
5. Time conditioning enters through the ratio `r = tau_d / tau_eff` and the mobilisation fraction `fA(r)`. The `IOp` definition subtracts `log2(fA(r))` from `IStar`, adding a difficulty charge that grows as mobilisation drops.
6. Theorem `T5.4-3` proves that reduced `r` increases `IOp`, connecting physical response latency to information-theoretic difficulty.
7. Theorem `T5.4-4` separates the three dimensions: option-space size (affects `IStar`), mobilisation speed (affects `IOp` but not `IStar`), and raw complexity (affects neither `IOp` nor `IStar` beyond `log2 C`, which is time-invariant). This separation grounds H8.
