import Mathlib

namespace Section5_4

noncomputable section

open scoped BigOperators

set_option linter.unusedSectionVars false

variable {α : Type} [Fintype α] [DecidableEq α]

/-- Base-2 logarithm as used in the thesis equations. -/
def log2 (x : Real) : Real :=
  Real.log x * (1 / Real.log 2)

/-- Threshold-qualified success set `A_{g,ρ}` over a finite option space. -/
def successSet (Perf : α → Real) (rho : Real) : Set α :=
  {x | rho ≤ Perf x}

/-- Finset realisation of `A_{g,ρ}` for cardinality arguments. -/
def successSetFinset (Perf : α → Real) (rho : Real) : Finset α :=
  Finset.univ.filter (fun x => rho ≤ Perf x)

/-- Cardinality `|A_{g,ρ}|`. -/
def successCount (Perf : α → Real) (rho : Real) : Nat :=
  (successSetFinset Perf rho).card

/-- Total configuration count `C = |O^Δ|`. -/
def configCount : Nat :=
  Fintype.card α

/-- Success share `p_g(ρ) = |A_{g,ρ}| / C`. -/
def successShare (Perf : α → Real) (rho : Real) : Real :=
  (successCount Perf rho : Real) / (configCount (α := α) : Real)

/-- Functional information `I_g^*(ρ) = log2 C - log2 |A_{g,ρ}|`. -/
def IStar (Perf : α → Real) (rho : Real) : Real :=
  log2 (configCount (α := α)) - log2 (successCount Perf rho)

/-- Time allowance ratio `r = τ_d / τ_eff`. -/
def ratio (tauD tauEff : Real) : Real :=
  tauD / tauEff

/-- Time-conditioned usable success count `Ã_{g,ρ}(τ_d,τ_eff)`. -/
def usableSuccessCount (Perf : α → Real) (rho : Real)
    (fA : Real → Real) (tauD tauEff : Real) : Real :=
  (successCount Perf rho : Real) * fA (ratio tauD tauEff)

/-- Operational functional information `I_g^op(ρ,τ_d)`. -/
def IOp (Perf : α → Real) (rho : Real)
    (fA : Real → Real) (tauD tauEff : Real) : Real :=
  IStar Perf rho - log2 (fA (ratio tauD tauEff))

/-- Finite image of the performance map. -/
def perfImage (Perf : α → Real) : Finset Real :=
  Finset.univ.image Perf

/-- Count-based form used for H8 sensitivity statements. -/
def IStarCounts (C A : Real) : Real :=
  log2 C - log2 A

/-- Count-and-time form used for H8 sensitivity statements. -/
def IOpCounts (C A : Real) (fA : Real → Real)
    (tauD tauEff : Real) : Real :=
  IStarCounts C A - log2 (fA (ratio tauD tauEff))

/-- Complexity-only indicator that does not depend on `τ_eff`. -/
def complexityOnly (C _tauEff : Real) : Real :=
  log2 C

lemma log2_den_pos : 0 < Real.log 2 := by
  have hTwo : (1 : Real) < 2 := by norm_num
  exact Real.log_pos hTwo

lemma log2_le_log2 {x y : Real} (hx : 0 < x) (hxy : x ≤ y) :
    log2 x ≤ log2 y := by
  unfold log2
  have hLog : Real.log x ≤ Real.log y := Real.log_le_log hx hxy
  have hInvNonneg : 0 ≤ 1 / Real.log 2 := by
    positivity
  exact mul_le_mul_of_nonneg_right hLog hInvNonneg

lemma log2_lt_log2 {x y : Real} (hx : 0 < x) (hxy : x < y) :
    log2 x < log2 y := by
  unfold log2
  have hLog : Real.log x < Real.log y := Real.log_lt_log hx hxy
  have hInvPos : 0 < 1 / Real.log 2 := by
    positivity
  exact mul_lt_mul_of_pos_right hLog hInvPos

lemma successSetFinset_mono_threshold
    (Perf : α → Real) {rho1 rho2 : Real} (hRho : rho1 ≤ rho2) :
    successSetFinset Perf rho2 ⊆ successSetFinset Perf rho1 := by
  intro x hx
  simp [successSetFinset] at hx ⊢
  exact le_trans hRho hx

lemma successCount_antitone
    (Perf : α → Real) {rho1 rho2 : Real} (hRho : rho1 ≤ rho2) :
    successCount Perf rho2 ≤ successCount Perf rho1 := by
  exact Finset.card_le_card (successSetFinset_mono_threshold (Perf := Perf) hRho)

lemma successCount_eq_of_no_crossing
    (Perf : α → Real) {rho1 rho2 : Real}
    (hOrder : rho1 ≤ rho2)
    (hNo : ∀ x, ¬ (rho1 ≤ Perf x ∧ Perf x < rho2)) :
    successCount Perf rho1 = successCount Perf rho2 := by
  have hEq : successSetFinset Perf rho1 = successSetFinset Perf rho2 := by
    apply Finset.ext
    intro x
    constructor
    · intro hx
      simp [successSetFinset] at hx ⊢
      by_contra hNot
      exact hNo x ⟨hx, lt_of_not_ge hNot⟩
    · intro hx
      exact successSetFinset_mono_threshold (Perf := Perf) hOrder hx
  simpa [successCount] using congrArg Finset.card hEq

lemma successCount_change_implies_crossing
    (Perf : α → Real) {rho1 rho2 : Real}
    (hOrder : rho1 ≤ rho2)
    (hNe : successCount Perf rho1 ≠ successCount Perf rho2) :
    ∃ x, rho1 ≤ Perf x ∧ Perf x < rho2 := by
  by_contra hNo
  have hNo' : ∀ x, ¬ (rho1 ≤ Perf x ∧ Perf x < rho2) := by
    intro x hx
    exact hNo ⟨x, hx⟩
  have hEq := successCount_eq_of_no_crossing (Perf := Perf) hOrder hNo'
  exact hNe hEq

lemma IStar_strict_of_count_drop
    (Perf : α → Real) {rho1 rho2 : Real}
    (hDrop : successCount Perf rho2 < successCount Perf rho1)
    (hPos2 : 0 < successCount Perf rho2) :
    IStar Perf rho1 < IStar Perf rho2 := by
  have hCastDrop : (successCount Perf rho2 : Real) < (successCount Perf rho1 : Real) := by
    exact_mod_cast hDrop
  have hLog :
      Real.log (successCount Perf rho2 : Real) <
      Real.log (successCount Perf rho1 : Real) :=
    Real.log_lt_log (Nat.cast_pos.mpr hPos2) hCastDrop
  have hLog2 :
      log2 (successCount Perf rho2) <
      log2 (successCount Perf rho1) :=
    log2_lt_log2 (Nat.cast_pos.mpr hPos2) hCastDrop
  unfold IStar
  linarith

lemma ratio_nonincrease_of_tauEff_increase
    (tauD tauEff1 tauEff2 : Real)
    (hTauD : 0 ≤ tauD) (hTauEff1 : 0 < tauEff1) (hTauEff : tauEff1 ≤ tauEff2) :
    ratio tauD tauEff2 ≤ ratio tauD tauEff1 := by
  unfold ratio
  exact div_le_div_of_nonneg_left hTauD hTauEff1 hTauEff

/-- T5.4-1: raising the threshold shrinks the success set and raises `I_g^*`. -/
theorem «T5.4-1»
    (Perf : α → Real) (rho1 rho2 : Real)
    (hRho : rho2 > rho1)
    (hPos2 : 0 < successCount Perf rho2) :
    successSetFinset Perf rho2 ⊆ successSetFinset Perf rho1 ∧
      successCount Perf rho2 ≤ successCount Perf rho1 ∧
      IStar Perf rho1 ≤ IStar Perf rho2 := by
  have hOrder : rho1 ≤ rho2 := le_of_lt hRho
  have hSubset := successSetFinset_mono_threshold (Perf := Perf) hOrder
  have hCount := successCount_antitone (Perf := Perf) hOrder
  have hCastCount : (successCount Perf rho2 : Real) ≤ (successCount Perf rho1 : Real) := by
    exact_mod_cast hCount
  have hLog :
      Real.log (successCount Perf rho2 : Real) ≤
      Real.log (successCount Perf rho1 : Real) :=
    Real.log_le_log (Nat.cast_pos.mpr hPos2) hCastCount
  have hLog2 :
      log2 (successCount Perf rho2) ≤
      log2 (successCount Perf rho1) :=
    log2_le_log2 (Nat.cast_pos.mpr hPos2) hCastCount
  have hI : IStar Perf rho1 ≤ IStar Perf rho2 := by
    unfold IStar
    linarith
  exact ⟨hSubset, hCount, hI⟩

/-- T5.4-2: finite-image thresholds induce piecewise-constant counts and jump points. -/
theorem «T5.4-2»
    (Perf : α → Real) :
    (Set.range Perf).Finite ∧
      (∀ rho1 rho2, rho1 ≤ rho2 →
        (∀ x, ¬ (rho1 ≤ Perf x ∧ Perf x < rho2)) →
        successCount Perf rho1 = successCount Perf rho2) ∧
      (∀ rho1 rho2, rho1 ≤ rho2 →
        successCount Perf rho1 ≠ successCount Perf rho2 →
        ∃ v ∈ perfImage Perf, rho1 ≤ v ∧ v < rho2) ∧
      (∀ rho1 rho2, rho1 < rho2 →
        successCount Perf rho1 ≠ successCount Perf rho2 →
        0 < successCount Perf rho1 →
        0 < successCount Perf rho2 →
        IStar Perf rho1 < IStar Perf rho2) := by
  constructor
  · simpa using Set.finite_range Perf
  · constructor
    · intro rho1 rho2 hOrder hNo
      exact successCount_eq_of_no_crossing (Perf := Perf) hOrder hNo
    · constructor
      · intro rho1 rho2 hOrder hNe
        have hCross := successCount_change_implies_crossing (Perf := Perf) hOrder hNe
        rcases hCross with ⟨x, hx1, hx2⟩
        refine ⟨Perf x, ?_, hx1, hx2⟩
        simp [perfImage]
      · intro rho1 rho2 hLt hNe _hPos1 hPos2
        have hLe : successCount Perf rho2 ≤ successCount Perf rho1 :=
          successCount_antitone (Perf := Perf) (le_of_lt hLt)
        have hNe' : successCount Perf rho2 ≠ successCount Perf rho1 := Ne.symm hNe
        have hDrop : successCount Perf rho2 < successCount Perf rho1 :=
          lt_of_le_of_ne hLe hNe'
        exact IStar_strict_of_count_drop (Perf := Perf) hDrop hPos2

/-- T5.4-3: time pressure raises operational functional information through `f_A`. -/
theorem «T5.4-3»
    (Perf : α → Real) (rho tauD1 tauEff1 tauD2 tauEff2 : Real)
    (fA : Real → Real)
    (hMonF : Monotone fA)
    (hFPos : ∀ r, 0 < fA r)
    (hRatio : ratio tauD2 tauEff2 ≤ ratio tauD1 tauEff1) :
    IOp Perf rho fA tauD1 tauEff1 ≤ IOp Perf rho fA tauD2 tauEff2 := by
  have hF : fA (ratio tauD2 tauEff2) ≤ fA (ratio tauD1 tauEff1) := hMonF hRatio
  have hLog :
      log2 (fA (ratio tauD2 tauEff2)) ≤
      log2 (fA (ratio tauD1 tauEff1)) :=
    log2_le_log2 (hFPos _) hF
  unfold IOp
  linarith

/-- T5.4-4: `I_g^op` depends on both size and time pressure, while `C` alone ignores `τ_eff`. -/
theorem «T5.4-4»
    (C1 C2 A tauD tauEff1 tauEff2 : Real)
    (fA : Real → Real)
    (hCPos : 0 < C1) (hCInc : C1 < C2)
    (hMonF : Monotone fA)
    (hFPos : ∀ r, 0 < fA r)
    (hTauD : 0 ≤ tauD)
    (hTauEff1 : 0 < tauEff1) (hTauEff : tauEff1 ≤ tauEff2) :
    IStarCounts C1 A < IStarCounts C2 A ∧
      IOpCounts C2 A fA tauD tauEff1 ≤ IOpCounts C2 A fA tauD tauEff2 ∧
      complexityOnly C2 tauEff1 = complexityOnly C2 tauEff2 := by
  have hLogC : log2 C1 < log2 C2 := log2_lt_log2 hCPos hCInc
  have hRatio : ratio tauD tauEff2 ≤ ratio tauD tauEff1 :=
    ratio_nonincrease_of_tauEff_increase tauD tauEff1 tauEff2 hTauD hTauEff1 hTauEff
  have hF : fA (ratio tauD tauEff2) ≤ fA (ratio tauD tauEff1) := hMonF hRatio
  have hLogF : log2 (fA (ratio tauD tauEff2)) ≤ log2 (fA (ratio tauD tauEff1)) :=
    log2_le_log2 (hFPos _) hF
  constructor
  · unfold IStarCounts
    linarith
  · constructor
    · unfold IOpCounts IStarCounts
      linarith
    · unfold complexityOnly
      rfl

end

end Section5_4
