import Mathlib

namespace Section5_7

noncomputable section

set_option linter.unusedSectionVars false

/-- Base-2 logarithm used in the thesis equations. -/
def log2 (x : Real) : Real :=
  Real.log x * (1 / Real.log 2)

/-- Complexity count `C = |O^Δ|` for a finite option set. -/
def optionCount {α : Type} (O : Finset α) : Nat :=
  O.card

/-- Constraint operator `K' = K ∪ K_p` modelled as additional filtering of options. -/
def constraintOperator {α : Type} (O : Finset α) (kP : α → Prop) [DecidablePred kP] : Finset α :=
  O.filter kP

/-- Distinct option count induced by a binning map `φ`. -/
def distinctCount {α β : Type} [DecidableEq β] (O : Finset α) (φ : α → β) : Nat :=
  (O.image φ).card

/-- Success share written from counts. -/
def successShare (A C : Real) : Real :=
  A / C

/-- Functional information in share form `I_g^* = -log2(|A|/C)`. -/
def IStarShare (A C : Real) : Real :=
  -log2 (successShare A C)

/-- Operational functional information `I_g^op = I_g^* - log2 f_A`. -/
def IOpCounts (C A fA : Real) : Real :=
  log2 C - log2 A - log2 fA

/-- Expected Gaussian log-likelihood accuracy term. -/
def expectedAccuracy (sigmaSq : Real) : Real :=
  -((Real.log (2 * Real.pi * sigmaSq) + 1) / 2)

/-- Response-time decomposition with CP-sensitive detection drag in reduced form. -/
def tauTotal (tauDetect0 tauOther gamma cpInfo : Real) : Real :=
  tauDetect0 * (1 + gamma * cpInfo) + tauOther

/-- Effective response time under bounded expertise multiplier. -/
def tauEff (tauDetect0 tauOther gamma cpInfo lambda u : Real) : Real :=
  (1 - lambda * u) * tauTotal tauDetect0 tauOther gamma cpInfo

/-- Time allowance ratio. -/
def ratio (tauD tauDetect0 tauOther gamma cpInfo lambda u : Real) : Real :=
  tauD / tauEff tauDetect0 tauOther gamma cpInfo lambda u

lemma log2_le_log2 {x y : Real} (hx : 0 < x) (hxy : x ≤ y) :
    log2 x ≤ log2 y := by
  unfold log2
  have hLog : Real.log x ≤ Real.log y := Real.log_le_log hx hxy
  have hInvNonneg : 0 ≤ 1 / Real.log 2 := by positivity
  exact mul_le_mul_of_nonneg_right hLog hInvNonneg

lemma log2_lt_log2 {x y : Real} (hx : 0 < x) (hxy : x < y) :
    log2 x < log2 y := by
  unfold log2
  have hLog : Real.log x < Real.log y := Real.log_lt_log hx hxy
  have hInvPos : 0 < 1 / Real.log 2 := by positivity
  exact mul_lt_mul_of_pos_right hLog hInvPos

lemma log2_mul {x y : Real} (hx : 0 < x) (hy : 0 < y) :
    log2 (x * y) = log2 x + log2 y := by
  unfold log2
  rw [Real.log_mul (ne_of_gt hx) (ne_of_gt hy)]
  ring

lemma log2_nonneg {x : Real} (hx : 1 ≤ x) : 0 ≤ log2 x := by
  have hx0 : 0 < x := lt_of_lt_of_le zero_lt_one hx
  have h := log2_le_log2 (x := 1) (y := x) (by norm_num) hx
  simpa [log2] using h

lemma log2_nonpos {x : Real} (hx0 : 0 < x) (hx1 : x ≤ 1) : log2 x ≤ 0 := by
  have h := log2_le_log2 (x := x) (y := 1) hx0 hx1
  simpa [log2] using h

lemma distinctCount_coarsen
    {α β γ : Type} [DecidableEq β] [DecidableEq γ]
    (O : Finset α) (φ : α → β) (φ' : α → γ) (h : β → γ)
    (hCoarse : ∀ x, φ' x = h (φ x)) :
    distinctCount O φ' ≤ distinctCount O φ := by
  have hSubset : O.image φ' ⊆ (O.image φ).image h := by
    intro y hy
    rcases Finset.mem_image.mp hy with ⟨x, hx, rfl⟩
    have hMem : φ x ∈ O.image φ := Finset.mem_image.mpr ⟨x, hx, rfl⟩
    have hMem' : h (φ x) ∈ (O.image φ).image h := Finset.mem_image.mpr ⟨φ x, hMem, rfl⟩
    simpa [hCoarse x] using hMem'
  have hCard₁ : (O.image φ').card ≤ ((O.image φ).image h).card := Finset.card_le_card hSubset
  have hCard₂ : ((O.image φ).image h).card ≤ (O.image φ).card := Finset.card_image_le
  unfold distinctCount
  exact le_trans hCard₁ hCard₂

/-- T5.7-1: pattern operators on `K`, `X_i`, and `φ` are complexity non-increasing. -/
theorem «T5.7-1»
    {α β γ : Type} [DecidableEq β] [DecidableEq γ]
    (O : Finset α) (kP : α → Prop) [DecidablePred kP]
    (Orestricted : Finset α) (hChoice : Orestricted ⊆ O)
    (φ : α → β) (φ' : α → γ) (h : β → γ)
    (hCoarse : ∀ x, φ' x = h (φ x)) :
    optionCount (constraintOperator O kP) ≤ optionCount O ∧
      optionCount Orestricted ≤ optionCount O ∧
      distinctCount O φ' ≤ distinctCount O φ := by
  constructor
  · unfold optionCount constraintOperator
    exact Finset.card_filter_le _ _
  constructor
  · exact Finset.card_le_card hChoice
  · exact distinctCount_coarsen O φ φ' h hCoarse

/-- T5.7-2: if success share improves after a pattern intervention, `I_g^*` cannot increase. -/
theorem «T5.7-2»
    (A C A' C' : Real)
    (hA : 0 < A) (hC : 0 < C) (hA' : 0 < A') (hC' : 0 < C')
    (hShare : successShare A C ≤ successShare A' C') :
    IStarShare A' C' ≤ IStarShare A C ∧
      (successShare A C < successShare A' C' → IStarShare A' C' < IStarShare A C) := by
  have hSharePos : 0 < successShare A C := by
    unfold successShare
    exact div_pos hA hC
  have hSharePos' : 0 < successShare A' C' := by
    unfold successShare
    exact div_pos hA' hC'
  have hLog : log2 (successShare A C) ≤ log2 (successShare A' C') :=
    log2_le_log2 hSharePos hShare
  have hWeak : IStarShare A' C' ≤ IStarShare A C := by
    unfold IStarShare
    linarith
  constructor
  · exact hWeak
  · intro hStrictShare
    have hLogStrict : log2 (successShare A C) < log2 (successShare A' C') :=
      log2_lt_log2 hSharePos hStrictShare
    unfold IStarShare
    linarith

lemma delta_choice_only
    (C A fA alpha : Real)
    (hC : 0 < C) (hAlpha : 0 < alpha) :
    IOpCounts C A fA - IOpCounts (alpha * C) A fA = -log2 alpha := by
  unfold IOpCounts
  rw [log2_mul hAlpha hC]
  ring

lemma delta_success_only
    (C A fA beta : Real)
    (hA : 0 < A) (hBeta : 0 < beta) :
    IOpCounts C A fA - IOpCounts C (beta * A) fA = log2 beta := by
  unfold IOpCounts
  rw [log2_mul hBeta hA]
  ring

lemma delta_mobilisation_only
    (C A fA gamma : Real)
    (hF : 0 < fA) (hGamma : 0 < gamma) :
    IOpCounts C A fA - IOpCounts C A (gamma * fA) = log2 gamma := by
  unfold IOpCounts
  rw [log2_mul hGamma hF]
  ring

lemma delta_joint
    (C A fA alpha beta gamma : Real)
    (hC : 0 < C) (hA : 0 < A) (hF : 0 < fA)
    (hAlpha : 0 < alpha) (hBeta : 0 < beta) (hGamma : 0 < gamma) :
    IOpCounts C A fA - IOpCounts (alpha * C) (beta * A) (gamma * fA) =
      -log2 alpha + log2 beta + log2 gamma := by
  unfold IOpCounts
  rw [log2_mul hAlpha hC, log2_mul hBeta hA, log2_mul hGamma hF]
  ring

/-- T5.7-3: joint interventions reduce `I_g^op` more than single-term interventions. -/
theorem «T5.7-3»
    (C A fA alpha beta gamma : Real)
    (hC : 0 < C) (hA : 0 < A) (hF : 0 < fA)
    (hAlpha0 : 0 < alpha) (hAlpha1 : alpha < 1)
    (hBeta1 : 1 ≤ beta) (hGamma1 : 1 ≤ gamma) :
    (IOpCounts C A fA - IOpCounts (alpha * C) (beta * A) (gamma * fA) =
      (IOpCounts C A fA - IOpCounts (alpha * C) A fA) +
      (IOpCounts C A fA - IOpCounts C (beta * A) fA) +
      (IOpCounts C A fA - IOpCounts C A (gamma * fA))) ∧
    (IOpCounts C A fA - IOpCounts (alpha * C) (beta * A) (gamma * fA) ≥
      IOpCounts C A fA - IOpCounts (alpha * C) A fA) ∧
    (IOpCounts C A fA - IOpCounts (alpha * C) (beta * A) (gamma * fA) ≥
      IOpCounts C A fA - IOpCounts C (beta * A) fA) ∧
    (IOpCounts C A fA - IOpCounts (alpha * C) (beta * A) (gamma * fA) ≥
      IOpCounts C A fA - IOpCounts C A (gamma * fA)) := by
  have hBeta0 : 0 < beta := lt_of_lt_of_le zero_lt_one hBeta1
  have hGamma0 : 0 < gamma := lt_of_lt_of_le zero_lt_one hGamma1
  have hΔC : IOpCounts C A fA - IOpCounts (alpha * C) A fA = -log2 alpha :=
    delta_choice_only C A fA alpha hC hAlpha0
  have hΔA : IOpCounts C A fA - IOpCounts C (beta * A) fA = log2 beta :=
    delta_success_only C A fA beta hA hBeta0
  have hΔF : IOpCounts C A fA - IOpCounts C A (gamma * fA) = log2 gamma :=
    delta_mobilisation_only C A fA gamma hF hGamma0
  have hΔJ :
      IOpCounts C A fA - IOpCounts (alpha * C) (beta * A) (gamma * fA) =
        -log2 alpha + log2 beta + log2 gamma :=
    delta_joint C A fA alpha beta gamma hC hA hF hAlpha0 hBeta0 hGamma0

  have hLogBetaNonneg : 0 ≤ log2 beta := log2_nonneg hBeta1
  have hLogGammaNonneg : 0 ≤ log2 gamma := log2_nonneg hGamma1
  have hLogAlphaNonpos : log2 alpha ≤ 0 := log2_nonpos hAlpha0 (le_of_lt hAlpha1)
  have hAlphaTermNonneg : 0 ≤ -log2 alpha := by linarith

  constructor
  · linarith [hΔJ, hΔC, hΔA, hΔF]
  constructor
  · rw [hΔJ, hΔC]
    linarith
  constructor
  · rw [hΔJ, hΔA]
    linarith
  · rw [hΔJ, hΔF]
    linarith

lemma tauTotal_mono_cp
    (tauDetect0 tauOther gamma cp₁ cp₂ : Real)
    (hDetect0 : 0 ≤ tauDetect0) (hGamma : 0 ≤ gamma) (hCP : cp₁ ≤ cp₂) :
    tauTotal tauDetect0 tauOther gamma cp₁ ≤ tauTotal tauDetect0 tauOther gamma cp₂ := by
  unfold tauTotal
  have hInner : 1 + gamma * cp₁ ≤ 1 + gamma * cp₂ := by
    nlinarith [hGamma, hCP]
  have hMul : tauDetect0 * (1 + gamma * cp₁) ≤ tauDetect0 * (1 + gamma * cp₂) :=
    mul_le_mul_of_nonneg_left hInner hDetect0
  linarith

lemma tauTotal_mono_detect
    (tauDetect₁ tauDetect₂ tauOther gamma cp : Real)
    (hCP0 : 0 ≤ cp) (hGamma : 0 ≤ gamma) (hDetect : tauDetect₁ ≤ tauDetect₂) :
    tauTotal tauDetect₁ tauOther gamma cp ≤ tauTotal tauDetect₂ tauOther gamma cp := by
  unfold tauTotal
  have hFactor : 0 ≤ 1 + gamma * cp := by
    nlinarith [hGamma, hCP0]
  have hMul : tauDetect₁ * (1 + gamma * cp) ≤ tauDetect₂ * (1 + gamma * cp) :=
    mul_le_mul_of_nonneg_right hDetect hFactor
  linarith

lemma tauTotal_pos
    (tauDetect0 tauOther gamma cp : Real)
    (hDetect0 : 0 ≤ tauDetect0) (hOther : 0 < tauOther)
    (hGamma : 0 ≤ gamma) (hCP0 : 0 ≤ cp) :
    0 < tauTotal tauDetect0 tauOther gamma cp := by
  unfold tauTotal
  have hFactor : 0 ≤ 1 + gamma * cp := by
    nlinarith [hGamma, hCP0]
  have hTerm : 0 ≤ tauDetect0 * (1 + gamma * cp) := mul_nonneg hDetect0 hFactor
  linarith

/-- T5.7-4: reducing inference noise improves accuracy and, via bridge assumptions, raises mobilisation. -/
theorem «T5.7-4»
    (sigmaSqLow sigmaSqHigh : Real)
    (tauD tauDetectOld tauDetectNew tauOther gamma cpOld cpNew lambda u : Real)
    (fA : Real → Real)
    (hSigmaLow : 0 < sigmaSqLow) (_hSigmaHigh : 0 < sigmaSqHigh)
    (hSigmaOrder : sigmaSqLow ≤ sigmaSqHigh)
    (hTauD : 0 ≤ tauD)
    (hDetectNew0 : 0 ≤ tauDetectNew) (hDetectOrder : tauDetectNew ≤ tauDetectOld)
    (hTauOther : 0 < tauOther)
    (hGamma : 0 ≤ gamma)
    (hCPNew0 : 0 ≤ cpNew) (hCPOrder : cpNew ≤ cpOld)
    (_hLambda0 : 0 ≤ lambda) (hSpeedBound : lambda * u < 1)
    (hMonFA : Monotone fA) :
    expectedAccuracy sigmaSqHigh ≤ expectedAccuracy sigmaSqLow ∧
      ratio tauD tauDetectOld tauOther gamma cpOld lambda u ≤
        ratio tauD tauDetectNew tauOther gamma cpNew lambda u ∧
      fA (ratio tauD tauDetectOld tauOther gamma cpOld lambda u) ≤
        fA (ratio tauD tauDetectNew tauOther gamma cpNew lambda u) := by
  have hScaleNonneg : 0 ≤ 2 * Real.pi := by positivity
  have hArgOrder : (2 * Real.pi) * sigmaSqLow ≤ (2 * Real.pi) * sigmaSqHigh :=
    mul_le_mul_of_nonneg_left hSigmaOrder hScaleNonneg
  have hArgPos : 0 < (2 * Real.pi) * sigmaSqLow := by positivity
  have hLogOrder :
      Real.log ((2 * Real.pi) * sigmaSqLow) ≤ Real.log ((2 * Real.pi) * sigmaSqHigh) :=
    Real.log_le_log hArgPos hArgOrder
  have hAcc : expectedAccuracy sigmaSqHigh ≤ expectedAccuracy sigmaSqLow := by
    unfold expectedAccuracy
    linarith

  have hDetectOld0 : 0 ≤ tauDetectOld := le_trans hDetectNew0 hDetectOrder
  have hCPOld0 : 0 ≤ cpOld := le_trans hCPNew0 hCPOrder

  have hTauDetect :
      tauTotal tauDetectNew tauOther gamma cpNew ≤
        tauTotal tauDetectOld tauOther gamma cpNew :=
    tauTotal_mono_detect tauDetectNew tauDetectOld tauOther gamma cpNew hCPNew0 hGamma hDetectOrder
  have hTauCP :
      tauTotal tauDetectOld tauOther gamma cpNew ≤
        tauTotal tauDetectOld tauOther gamma cpOld :=
    tauTotal_mono_cp tauDetectOld tauOther gamma cpNew cpOld hDetectOld0 hGamma hCPOrder
  have hTauTotal :
      tauTotal tauDetectNew tauOther gamma cpNew ≤
        tauTotal tauDetectOld tauOther gamma cpOld := le_trans hTauDetect hTauCP

  have hOneMinusPos : 0 < 1 - lambda * u := by linarith
  have hTauEff :
      tauEff tauDetectNew tauOther gamma cpNew lambda u ≤
        tauEff tauDetectOld tauOther gamma cpOld lambda u := by
    unfold tauEff
    exact mul_le_mul_of_nonneg_left hTauTotal hOneMinusPos.le

  have hTauTotalNewPos : 0 < tauTotal tauDetectNew tauOther gamma cpNew :=
    tauTotal_pos tauDetectNew tauOther gamma cpNew hDetectNew0 hTauOther hGamma hCPNew0
  have hTauEffNewPos : 0 < tauEff tauDetectNew tauOther gamma cpNew lambda u := by
    unfold tauEff
    exact mul_pos hOneMinusPos hTauTotalNewPos

  have hRatio :
      ratio tauD tauDetectOld tauOther gamma cpOld lambda u ≤
        ratio tauD tauDetectNew tauOther gamma cpNew lambda u := by
    unfold ratio
    exact div_le_div_of_nonneg_left hTauD hTauEffNewPos hTauEff
  have hMobilisation :
      fA (ratio tauD tauDetectOld tauOther gamma cpOld lambda u) ≤
        fA (ratio tauD tauDetectNew tauOther gamma cpNew lambda u) := hMonFA hRatio

  exact ⟨hAcc, hRatio, hMobilisation⟩

end

end Section5_7
