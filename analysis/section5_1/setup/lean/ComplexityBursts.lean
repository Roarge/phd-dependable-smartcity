import Mathlib
import ComplexityModel

namespace ComplexityBursts

open ComplexityModel

/-! ## Theorem group A: monotonicity and multiplicative growth -/

/-- A1. Monotonicity of complexity under option-set expansion. -/
theorem A1
    {X B : Type*} [DecidableEq X] [DecidableEq B]
    (X1 X2 : Finset X) (K : X -> Prop) [DecidablePred K] (b : X -> B)
    (hExpand : X1 ⊆ X2) :
    complexity X1 K b <= complexity X2 K b := by
  unfold complexity feasibleDistinctSet
  have hFilter : X1.filter K ⊆ X2.filter K := by
    intro x hx
    exact Finset.mem_filter.mpr
      ⟨hExpand (Finset.mem_filter.mp hx).1, (Finset.mem_filter.mp hx).2⟩
  exact Finset.card_le_card (Finset.image_subset_image hFilter)

/-- Minimal strictness condition for A1: strict increase occurs when expansion introduces
    at least one new feasible distinct bin. -/
theorem A1_strict
    {X B : Type*} [DecidableEq X] [DecidableEq B]
    (X1 X2 : Finset X) (K : X -> Prop) [DecidablePred K] (b : X -> B)
    (hExpand : X1 ⊆ X2)
    (hNew : ∃ y, y ∈ feasibleDistinctSet X2 K b ∧ y ∉ feasibleDistinctSet X1 K b) :
    complexity X1 K b < complexity X2 K b := by
  unfold complexity
  have hSubset : feasibleDistinctSet X1 K b ⊆ feasibleDistinctSet X2 K b := by
    intro y hy
    rcases Finset.mem_image.mp hy with ⟨x, hx, rfl⟩
    exact Finset.mem_image.mpr
      ⟨x, Finset.mem_filter.mpr
        ⟨hExpand (Finset.mem_filter.mp hx).1, (Finset.mem_filter.mp hx).2⟩, rfl⟩
  have hNotSubset : ¬ feasibleDistinctSet X2 K b ⊆ feasibleDistinctSet X1 K b := by
    intro h
    rcases hNew with ⟨y, hy2, hy1not⟩
    exact hy1not (h hy2)
  have hSSubset : feasibleDistinctSet X1 K b ⊂ feasibleDistinctSet X2 K b := by
    exact ⟨hSubset, hNotSubset⟩
  exact Finset.card_lt_card hSSubset

/-- A2. Monotonicity of complexity under constraint tightening. -/
theorem A2
    {X B : Type*} [DecidableEq X] [DecidableEq B]
    (Xspace : Finset X)
    (K1 K2 : X -> Prop) [DecidablePred K1] [DecidablePred K2] (b : X -> B)
    (hTighten : ∀ x, K2 x -> K1 x) :
    complexity Xspace K2 b <= complexity Xspace K1 b := by
  unfold complexity feasibleDistinctSet
  have hFilter : Xspace.filter K2 ⊆ Xspace.filter K1 := by
    intro x hx
    exact Finset.mem_filter.mpr
      ⟨(Finset.mem_filter.mp hx).1, hTighten x (Finset.mem_filter.mp hx).2⟩
  exact Finset.card_le_card (Finset.image_subset_image hFilter)

/-- A3. Multiplicative composition lemma under exact independence assumption:
    the feasible distinct total set factorises as a Cartesian product. -/
theorem A3
    {X1 X2 : Type*} [DecidableEq X1] [DecidableEq X2]
    (Stot : Finset (X1 × X2)) (S1 : Finset X1) (S2 : Finset X2)
    (hIndependent : Stot = S1.product S2) :
    Stot.card = S1.card * S2.card := by
  rw [hIndependent]
  exact Finset.card_product S1 S2

/-- Helper lemmas for event-driven updates. -/
lemma event_step_no_event
    (C0 : Real) (k : Nat -> Real) (event : Nat -> Prop)
    [DecidablePred event] (t : Nat) (hNoEvent : ¬ event t) :
    eventDrivenComplexity C0 k event (t + 1) = eventDrivenComplexity C0 k event t := by
  simp [eventDrivenComplexity, hNoEvent]

lemma event_step_event
    (C0 : Real) (k : Nat -> Real) (event : Nat -> Prop)
    [DecidablePred event] (t : Nat) (hEvent : event t) :
    eventDrivenComplexity C0 k event (t + 1) =
      eventDrivenComplexity C0 k event t * k t := by
  simp [eventDrivenComplexity, hEvent]

/-- A4. Bursts from discrete factor introductions.
    Complexity trajectory is piecewise constant between events and jumps at events,
    with bit jump size `Delta log2 C = log2(k)`. -/
theorem A4
    (C0 : Real) (k : Nat -> Real) (event : Nat -> Prop)
    [DecidablePred event] (t : Nat)
    (hC : 0 < eventDrivenComplexity C0 k event t)
    (hk : 0 < k t) :
    ((¬ event t ->
        eventDrivenComplexity C0 k event (t + 1) = eventDrivenComplexity C0 k event t) ∧
      (event t ->
        eventDrivenComplexity C0 k event (t + 1) =
          eventDrivenComplexity C0 k event t * k t) ∧
      (event t ->
        log2 (eventDrivenComplexity C0 k event (t + 1))
          - log2 (eventDrivenComplexity C0 k event t)
          = log2 (k t))) := by
  refine ⟨?hNoEvent, ?hRest⟩
  · intro hNoEvent
    exact event_step_no_event C0 k event t hNoEvent
  · refine ⟨?hEventStep, ?hJump⟩
    · intro hEvent
      exact event_step_event C0 k event t hEvent
    · intro hEvent
      rw [event_step_event C0 k event t hEvent]
      exact log2_jump_bits hC hk

/-! ## Theorem group B: selection pressure and operational complexity -/

/-- B1. Selection-pressure monotonicity.
    If operational success share `rho^op` is non-increasing, then `I_g^op` is non-decreasing. -/
theorem B1
    {S : Type*} [Preorder S]
    (rhoOp : S -> Real)
    (hRhoAntitone : Antitone rhoOp)
    (hRhoPos : ∀ s, 0 < rhoOp s) :
    (∀ {s t}, s <= t -> rhoOp t <= rhoOp s) ∧
      Monotone (fun s => operationalFunctionalInformationFromShare (rhoOp s)) := by
  refine ⟨?hRho, ?hI⟩
  · intro s t hst
    exact hRhoAntitone hst
  · intro s t hst
    have hRho : rhoOp t <= rhoOp s := hRhoAntitone hst
    have hLog : Real.log (rhoOp t) <= Real.log (rhoOp s) :=
      Real.log_le_log (hRhoPos t) hRho
    have hLog2Pos : 0 < Real.log 2 := by
      exact Real.log_pos (by norm_num : (1 : Real) < 2)
    have hDiv : Real.log (rhoOp t) / Real.log 2 <= Real.log (rhoOp s) / Real.log 2 := by
      exact div_le_div_of_nonneg_right hLog (le_of_lt hLog2Pos)
    unfold operationalFunctionalInformationFromShare functionalInformation log2
    linarith

/-- B2. Closed-form jump size in bits for a discrete change in `rho^op`. -/
theorem B2
    (rhoMinus rhoPlus : Real)
    (hMinus : 0 < rhoMinus)
    (hPlus : 0 < rhoPlus) :
    operationalFunctionalInformationFromShare rhoPlus
      - operationalFunctionalInformationFromShare rhoMinus
      = log2 (rhoMinus / rhoPlus) := by
  unfold operationalFunctionalInformationFromShare functionalInformation
  calc
    (-log2 rhoPlus) - (-log2 rhoMinus)
        = log2 rhoMinus - log2 rhoPlus := by ring
    _ = log2 (rhoMinus / rhoPlus) := by
      rw [<- log2_div hMinus hPlus]

/-- B3. If selection-pressure variables change discretely and reduce `rho^op`,
    then `I_g^op(t)` has a jump discontinuity at that event time. -/
theorem B3
    (rhoOp : Nat -> Real) (t : Nat)
    (_hMinus : 0 < rhoOp t)
    (hPlus : 0 < rhoOp (t + 1))
    (hDrop : rhoOp (t + 1) < rhoOp t) :
    JumpAt (fun n => operationalFunctionalInformationFromShare (rhoOp n)) t := by
  unfold JumpAt
  have hLog : Real.log (rhoOp (t + 1)) < Real.log (rhoOp t) :=
    Real.log_lt_log hPlus hDrop
  have hLog2Pos : 0 < Real.log 2 := by
    exact Real.log_pos (by norm_num : (1 : Real) < 2)
  have hDiv :
      Real.log (rhoOp (t + 1)) / Real.log 2 < Real.log (rhoOp t) / Real.log 2 := by
    exact div_lt_div_of_pos_right hLog hLog2Pos
  have hStrict :
      operationalFunctionalInformationFromShare (rhoOp (t + 1))
        > operationalFunctionalInformationFromShare (rhoOp t) := by
    unfold operationalFunctionalInformationFromShare functionalInformation log2
    linarith
  exact ne_of_gt hStrict

/-! ## Theorem group C: joint intervention effect -/

/-- C1. Symbolic expression for change in `I_g^op` from simultaneous count changes. -/
theorem C1
    (CeffBefore CeffAfter AeffBefore AeffAfter : Real)
    (hCbefore : 0 < CeffBefore) (hCafter : 0 < CeffAfter)
    (hAbefore : 0 < AeffBefore) (hAafter : 0 < AeffAfter) :
    operationalFunctionalInformation CeffAfter AeffAfter
      - operationalFunctionalInformation CeffBefore AeffBefore
      = log2 (CeffAfter / CeffBefore) - log2 (AeffAfter / AeffBefore) := by
  unfold operationalFunctionalInformation
  calc
    (log2 CeffAfter - log2 AeffAfter) - (log2 CeffBefore - log2 AeffBefore)
        = (log2 CeffAfter - log2 CeffBefore) - (log2 AeffAfter - log2 AeffBefore) := by ring
    _ = log2 (CeffAfter / CeffBefore) - log2 (AeffAfter / AeffBefore) := by
      rw [<- log2_div hCafter hCbefore, <- log2_div hAafter hAbefore]

/-- C2. Joint intervention hypothesis.
    If `C_eff` is reduced by `alpha in (0,1)` and `A_eff` is increased by `beta > 1`,
    the reduction in `I_g^op` equals the sum of reductions from each single-term change. -/
theorem C2
    (Ceff Aeff alpha beta : Real)
    (hC : 0 < Ceff) (hA : 0 < Aeff)
    (hAlphaLower : 0 < alpha) (_hAlphaUpper : alpha < 1)
    (hBeta : 1 < beta) :
    (operationalFunctionalInformation Ceff Aeff
      - operationalFunctionalInformation (alpha * Ceff) (beta * Aeff))
      =
      (operationalFunctionalInformation Ceff Aeff
        - operationalFunctionalInformation (alpha * Ceff) Aeff)
      +
      (operationalFunctionalInformation Ceff Aeff
        - operationalFunctionalInformation Ceff (beta * Aeff)) := by
  have hBetaPos : 0 < beta := lt_trans zero_lt_one hBeta
  have hJointBits :
      operationalFunctionalInformation Ceff Aeff
        - operationalFunctionalInformation (alpha * Ceff) (beta * Aeff)
        = (-log2 alpha) + log2 beta := by
    unfold operationalFunctionalInformation
    rw [log2_mul hAlphaLower hC, log2_mul hBetaPos hA]
    ring
  have hOnlyC :
      operationalFunctionalInformation Ceff Aeff
        - operationalFunctionalInformation (alpha * Ceff) Aeff
        = -log2 alpha := by
    unfold operationalFunctionalInformation
    rw [log2_mul hAlphaLower hC]
    ring
  have hOnlyA :
      operationalFunctionalInformation Ceff Aeff
        - operationalFunctionalInformation Ceff (beta * Aeff)
        = log2 beta := by
    unfold operationalFunctionalInformation
    rw [log2_mul hBetaPos hA]
    ring
  calc
    operationalFunctionalInformation Ceff Aeff
      - operationalFunctionalInformation (alpha * Ceff) (beta * Aeff)
        = (-log2 alpha) + log2 beta := hJointBits
    _ = (operationalFunctionalInformation Ceff Aeff
          - operationalFunctionalInformation (alpha * Ceff) Aeff)
        +
        (operationalFunctionalInformation Ceff Aeff
          - operationalFunctionalInformation Ceff (beta * Aeff)) := by
      rw [hOnlyC, hOnlyA]

end ComplexityBursts
