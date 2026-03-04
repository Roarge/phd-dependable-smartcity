# Section 5.1 Formal Proof Write-up

## 5.1.1 Bursts from multiplicative composition of options

Theorem `A1` proves that complexity `C` is non-decreasing when a factor option set expands while `K` is fixed. The strictness lemma `A1_strict` gives the minimal strict increase condition. At least one new feasible distinct bin must be introduced by the expansion.

Theorem `A3` proves exact multiplicative composition under the stated independence assumption where constraints and binning factorise across subsystems. This validates the burst mechanism in which small boundary additions can produce large growth in feasible combinations.
When interdependence and heterogeneous constraints in `K` are active, a small interface change can alter feasibility across several coupled factors, so option-set shifts propagate beyond the edited boundary degree.


Theorem `A4` proves the event-time update form for discrete introductions. Between events the trajectory is constant at one-step resolution. At event times the jump is multiplicative and the bit jump is `Delta log2 C = log2(k)`. In the event at `t=20`, `log2 C` rises from 8.618 to 9.406, demonstrating the step behaviour.

## 5.1.2 Bursts from constraint changes rather than option growth alone

Theorem `A2` proves that tightening constraints cannot increase feasible distinct options. This binds the analysis directly to `K`, including governance commitments and boundary obligations.

Theorem `B3` proves that a discrete drop in `rho^op` produces a jump in `I_g^op`. This captures discontinuities caused by governance, compliance, interface-semantics, or procurement changes even when technical option growth is limited.

In the event at `t=45`, `log2 C` changes only from 9.934 to 9.998, while `Delta I_g^op` is 1.720 bits. This separates constraint-driven bursts from raw option-count growth.

## 5.1.3 Functional information explains why bursts feel like sudden loss of competence

Theorem `B1` establishes that when selection pressure makes `rho^op` non-increasing, operational functional information `I_g^op = -log2(rho^op)` is non-decreasing. This gives a necessary monotonic response of decision burden under pressure.

Theorem `B2` provides the closed-form jump expression `Delta I_g^op = log2(rho_minus / rho_plus)`. The jump size is additive in bits, so small proportional drops in mobilisation share produce immediate increases in operational choice cost.

At `t=45`, `rho^op` drops from 0.2002 to 0.0608. The measured increase in burden is 1.720 bits. This maps to the observed operational experience of sudden competence loss because the same team faces a larger effective search burden within the same response window.

Figure `analysis/section5_1/result/fig_5_1_complexity_bursts.pdf` is the Chapter 5.1 anchor. The `log2 C` curve shows structural burden growth with discrete steps. The `log2 A~` curve shows mobilisation-constrained useful options. The `I_g^op` curve shows bursty increases in decision burden at the same event points.

## Embedded hypotheses

### H1 Bursty complexity hypothesis

Formal basis: `A4`, `B2`, and `B3`.

Prediction: bursts in complexity potential or boundary constraints create bursts in `I_g^op` and immediate response-performance drops because fewer useful options are mobilisable in time.

### H1 Joint intervention hypothesis

Formal basis: `C1` and `C2`.

`C1` decomposes change in operational functional information into a total-option term and a useful-option term. `C2` proves exact additivity of reductions for simultaneous changes.

In the event at `t=70`, the model shows `Delta I_g^op = -0.746` bits with simultaneous option-pruning and useful-share increase. The joint reduction is larger than either single-term intervention alone by theorem, not by narrative assumption.

## Required reasoning chain

1. Complexity is defined as feasible distinct optionality by cardinality of the quotient induced by binning and constraints, implemented by `feasibleDistinctSet` and `complexity`.
2. Multiplicative composition is proven by `A3`, so small additions at boundaries can scale combinations disproportionately.
3. Success share and functional information are formalised in `successShare` and `functionalInformation`, with `B1` separating optionality growth from success-share effects.
4. Time-conditioning enters through mobilisation fraction and effective success count, so reduced mobilisation lowers `rho^op` even if `C` grows.
5. Selection pressure is represented as antitone `rho^op` in `B1`, forcing non-decreasing `I_g^op`.
6. Discrete governance and boundary events are modelled in `A4` and `B3`, yielding jump discontinuities with closed-form jump size `B2`.
7. Joint intervention effects are derived in `C1` and `C2`, giving a direct resilience implication that coordinated pruning and success-share improvement should be prioritised.
