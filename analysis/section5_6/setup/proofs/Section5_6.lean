import Mathlib

namespace Section5_6

noncomputable section

set_option linter.unusedSectionVars false

/-- Stage-time model with scalar complexity potential for sensitivity analysis. -/
def tauStage (tau0 gamma cp : Real) : Real :=
  tau0 * (1 + gamma * cp)

/-- Aggregate mobilisation time before skill multiplier. -/
def tauTotal (tau0 gamma cp : Real) : Real :=
  tauStage tau0 gamma cp

/-- Effective mobilisation time with bounded skill speed-up `u in [0,1]`. -/
def tauEff (tau0 gamma cp lambda u : Real) : Real :=
  (1 - lambda * u) * tauTotal tau0 gamma cp

/-- Reduced form with fixed `tau` used for bounded-multiplier proofs. -/
def tauEffBase (tau lambda u : Real) : Real :=
  (1 - lambda * u) * tau

/-- Time allowance ratio. -/
def ratio (tauD tau0 gamma cp lambda u : Real) : Real :=
  tauD / tauEff tau0 gamma cp lambda u

/-- Magnitude of sensitivity of `r` to `u` from the closed form derivative. -/
def rSensitivityU (tauD tau0 gamma cp lambda u : Real) : Real :=
  (tauD * lambda) /
    (((1 - lambda * u) ^ (2 : Nat)) * tauTotal tau0 gamma cp)

/-- Mobilisation fraction family. -/
def mobilisationFraction (r eps : Real) : Real :=
  min 1 (r ^ eps)

/-- Sensitivity proxies for Section 5.6 comparison statements. -/
def partialTauCP (tau0 gamma : Real) : Real :=
  tau0 * gamma

/-- Sensitivity of effective time to experience multiplier. -/
def partialTauEffU (tau0 gamma cp lambda : Real) : Real :=
  -(lambda * tauTotal tau0 gamma cp)

/-- Structural intervention by proportional CP reduction `k`. -/
def cpReductionGain (tau0 gamma cp k : Real) : Real :=
  tauTotal tau0 gamma cp - tauTotal tau0 gamma ((1 - k) * cp)

/-- Maximum experience-driven reduction between `u=0` and `u=1`. -/
def experienceMaxGain (tau0 gamma cp lambda : Real) : Real :=
  tauTotal tau0 gamma cp - tauEff tau0 gamma cp lambda 1

/-- Closed-form CP threshold where structural and experience gains are equal. -/
def dominanceThreshold (lambda gamma k : Real) : Real :=
  lambda / (gamma * (k - lambda))

lemma tauTotal_mono_cp (tau0 gamma cpLow cpHigh : Real)
    (hTau0 : 0 ≤ tau0) (hGamma : 0 ≤ gamma) (hCp : cpLow ≤ cpHigh) :
    tauTotal tau0 gamma cpLow ≤ tauTotal tau0 gamma cpHigh := by
  unfold tauTotal tauStage
  have hInner : 1 + gamma * cpLow ≤ 1 + gamma * cpHigh := by
    nlinarith [hGamma, hCp]
  exact mul_le_mul_of_nonneg_left hInner hTau0

lemma tauTotal_strict_cp (tau0 gamma cpLow cpHigh : Real)
    (hTau0 : 0 < tau0) (hGamma : 0 < gamma) (hCp : cpLow < cpHigh) :
    tauTotal tau0 gamma cpLow < tauTotal tau0 gamma cpHigh := by
  unfold tauTotal tauStage
  have hInner : 1 + gamma * cpLow < 1 + gamma * cpHigh := by
    nlinarith
  exact mul_lt_mul_of_pos_left hInner hTau0

lemma tauTotal_nonneg (tau0 gamma cp : Real)
    (hTau0 : 0 ≤ tau0) (hGamma : 0 ≤ gamma) (hCp0 : 0 ≤ cp) :
    0 ≤ tauTotal tau0 gamma cp := by
  unfold tauTotal tauStage
  have hFactor : 0 ≤ 1 + gamma * cp := by
    nlinarith [hGamma, hCp0]
  exact mul_nonneg hTau0 hFactor

lemma tauTotal_pos (tau0 gamma cp : Real)
    (hTau0 : 0 < tau0) (hGamma : 0 ≤ gamma) (hCp0 : 0 ≤ cp) :
    0 < tauTotal tau0 gamma cp := by
  unfold tauTotal tauStage
  have hFactor : 0 < 1 + gamma * cp := by
    nlinarith [hGamma, hCp0]
  exact mul_pos hTau0 hFactor

/-- T5.6-1: bounded experience effect on effective time. -/
theorem «T5.6-1» (tau lambda u : Real)
    (hTau : 0 < tau)
    (hLam0 : 0 ≤ lambda) (_hLam1 : lambda ≤ 1)
    (hU0 : 0 ≤ u) (hU1 : u ≤ 1) :
    tauEffBase tau lambda u = tau - (lambda * tau) * u ∧
      |-(lambda * tau)| ≤ lambda * tau ∧
      tauEffBase tau lambda u ∈ Set.Icc ((1 - lambda) * tau) tau ∧
      ((tauEffBase tau lambda 0 - tauEffBase tau lambda 1) / tau = lambda) := by
  have hLamTauNonneg : 0 ≤ lambda * tau := mul_nonneg hLam0 hTau.le
  have hFactorLower : 1 - lambda ≤ 1 - lambda * u := by
    nlinarith [hLam0, hU0, hU1]
  have hFactorUpper : 1 - lambda * u ≤ 1 := by
    nlinarith [hLam0, hU0]
  have hLower : (1 - lambda) * tau ≤ tauEffBase tau lambda u := by
    unfold tauEffBase
    exact mul_le_mul_of_nonneg_right hFactorLower hTau.le
  have hUpper : tauEffBase tau lambda u ≤ tau := by
    unfold tauEffBase
    have hTmp : (1 - lambda * u) * tau ≤ 1 * tau :=
      mul_le_mul_of_nonneg_right hFactorUpper hTau.le
    simpa using hTmp
  have hTauNe : tau ≠ 0 := ne_of_gt hTau
  constructor
  · unfold tauEffBase
    ring
  constructor
  · have hAbs : |-(lambda * tau)| = lambda * tau := by
      simp [abs_of_nonneg hLamTauNonneg]
    rw [hAbs]
  constructor
  · exact ⟨hLower, hUpper⟩
  · unfold tauEffBase
    field_simp [hTauNe]
    ring

/-- T5.6-2: diminishing sensitivity of mobilisation to experience as complexity potential grows. -/
theorem «T5.6-2»
    (tauD tau0 gamma cpLow cpHigh lambda u : Real)
    (fA fB : Real → Real)
    (hTauD0 : 0 ≤ tauD)
    (hTau0 : 0 < tau0)
    (hGamma0 : 0 ≤ gamma)
    (hCp0 : 0 ≤ cpLow)
    (hCp : cpLow ≤ cpHigh)
    (hLam0 : 0 ≤ lambda)
    (_hU0 : 0 ≤ u)
    (hStab : lambda * u < 1)
    (hMonA : Monotone fA)
    (hMonB : Monotone fB) :
    rSensitivityU tauD tau0 gamma cpHigh lambda u
      ≤ rSensitivityU tauD tau0 gamma cpLow lambda u ∧
    ratio tauD tau0 gamma cpHigh lambda u
      ≤ ratio tauD tau0 gamma cpLow lambda u ∧
    fA (ratio tauD tau0 gamma cpHigh lambda u)
      ≤ fA (ratio tauD tau0 gamma cpLow lambda u) ∧
    fB (ratio tauD tau0 gamma cpHigh lambda u)
      ≤ fB (ratio tauD tau0 gamma cpLow lambda u) := by
  have hCpHigh0 : 0 ≤ cpHigh := le_trans hCp0 hCp
  have hTauMon :
      tauTotal tau0 gamma cpLow ≤ tauTotal tau0 gamma cpHigh :=
    tauTotal_mono_cp tau0 gamma cpLow cpHigh hTau0.le hGamma0 hCp
  have hTauLowPos : 0 < tauTotal tau0 gamma cpLow :=
    tauTotal_pos tau0 gamma cpLow hTau0 hGamma0 hCp0
  have hOneMinusPos : 0 < 1 - lambda * u := by linarith
  have hNumNonneg : 0 ≤ tauD * lambda := mul_nonneg hTauD0 hLam0
  have hSqNonneg : 0 ≤ (1 - lambda * u) ^ (2 : Nat) := sq_nonneg _
  have hSqPos : 0 < (1 - lambda * u) ^ (2 : Nat) := by
    nlinarith [hOneMinusPos]

  have hDenMonSens :
      ((1 - lambda * u) ^ (2 : Nat)) * tauTotal tau0 gamma cpLow
        ≤ ((1 - lambda * u) ^ (2 : Nat)) * tauTotal tau0 gamma cpHigh :=
    mul_le_mul_of_nonneg_left hTauMon hSqNonneg
  have hDenSensPos :
      0 < ((1 - lambda * u) ^ (2 : Nat)) * tauTotal tau0 gamma cpLow :=
    mul_pos hSqPos hTauLowPos

  have hSens :
      rSensitivityU tauD tau0 gamma cpHigh lambda u
        ≤ rSensitivityU tauD tau0 gamma cpLow lambda u := by
    unfold rSensitivityU
    exact div_le_div_of_nonneg_left hNumNonneg hDenSensPos hDenMonSens

  have hDenMonRatio :
      (1 - lambda * u) * tauTotal tau0 gamma cpLow
        ≤ (1 - lambda * u) * tauTotal tau0 gamma cpHigh :=
    mul_le_mul_of_nonneg_left hTauMon hOneMinusPos.le
  have hDenRatioPos :
      0 < (1 - lambda * u) * tauTotal tau0 gamma cpLow :=
    mul_pos hOneMinusPos hTauLowPos

  have hRatio :
      ratio tauD tau0 gamma cpHigh lambda u
        ≤ ratio tauD tau0 gamma cpLow lambda u := by
    unfold ratio tauEff
    exact div_le_div_of_nonneg_left hTauD0 hDenRatioPos hDenMonRatio

  have hFA := hMonA hRatio
  have hFB := hMonB hRatio
  exact ⟨hSens, hRatio, hFA, hFB⟩

lemma cpReductionGain_closed_form (tau0 gamma cp k : Real) :
    cpReductionGain tau0 gamma cp k = tau0 * gamma * k * cp := by
  unfold cpReductionGain tauTotal tauStage
  ring

lemma experienceMaxGain_closed_form (tau0 gamma cp lambda : Real) :
    experienceMaxGain tau0 gamma cp lambda = lambda * tauTotal tau0 gamma cp := by
  unfold experienceMaxGain tauEff
  ring

/-- T5.6-3: structural interventions dominate in high-drag regimes under explicit threshold assumptions. -/
theorem «T5.6-3»
    (tau0 gamma cpLow cpHigh lambda u k : Real)
    (hTau0 : 0 < tau0)
    (hGamma : 0 < gamma)
    (hCp0 : 0 ≤ cpLow)
    (hCp : cpLow ≤ cpHigh)
    (hLam0 : 0 < lambda)
    (_hLam1 : lambda < 1)
    (_hU0 : 0 ≤ u)
    (_hU1 : u ≤ 1)
    (hKDom : lambda < k)
    (hCPStar : dominanceThreshold lambda gamma k ≤ cpHigh) :
    cpReductionGain tau0 gamma cpLow k ≤ cpReductionGain tau0 gamma cpHigh k ∧
      partialTauCP tau0 gamma = tau0 * gamma ∧
      |partialTauEffU tau0 gamma cpHigh lambda| = lambda * tauTotal tau0 gamma cpHigh ∧
      experienceMaxGain tau0 gamma cpHigh lambda ≤ cpReductionGain tau0 gamma cpHigh k := by
  have hCpHigh0 : 0 ≤ cpHigh := le_trans hCp0 hCp
  have hGainMono : cpReductionGain tau0 gamma cpLow k ≤ cpReductionGain tau0 gamma cpHigh k := by
    rw [cpReductionGain_closed_form, cpReductionGain_closed_form]
    have hKPos : 0 ≤ k := le_of_lt (lt_trans hLam0 hKDom)
    have hScaleNonneg : 0 ≤ tau0 * gamma * k := by
      exact mul_nonneg (mul_nonneg hTau0.le hGamma.le) hKPos
    exact mul_le_mul_of_nonneg_left hCp hScaleNonneg

  have hAbsEff : |partialTauEffU tau0 gamma cpHigh lambda| = lambda * tauTotal tau0 gamma cpHigh := by
    unfold partialTauEffU
    have hTauNonneg : 0 ≤ tauTotal tau0 gamma cpHigh :=
      tauTotal_nonneg tau0 gamma cpHigh hTau0.le hGamma.le hCpHigh0
    have hProdNonneg : 0 ≤ lambda * tauTotal tau0 gamma cpHigh := mul_nonneg hLam0.le hTauNonneg
    simp [abs_of_nonneg hProdNonneg]

  have hThresholdCore : lambda ≤ gamma * (k - lambda) * cpHigh := by
    unfold dominanceThreshold at hCPStar
    have hDenPos : 0 < gamma * (k - lambda) := by nlinarith [hGamma, hKDom]
    have hScaledMul :
        (lambda / (gamma * (k - lambda))) * (gamma * (k - lambda))
          ≤ cpHigh * (gamma * (k - lambda)) :=
      mul_le_mul_of_nonneg_right hCPStar hDenPos.le
    have hDenNe : gamma * (k - lambda) ≠ 0 := ne_of_gt hDenPos
    have hKNe : k - lambda ≠ 0 := sub_ne_zero.mpr (ne_of_gt hKDom)
    have hLeft : (lambda / (gamma * (k - lambda))) * (gamma * (k - lambda)) = lambda := by
      field_simp [hDenNe, hKNe]
    have hScaled : lambda ≤ cpHigh * (gamma * (k - lambda)) := by
      linarith [hScaledMul, hLeft]
    nlinarith [hScaled]

  have hCompareCore : lambda * (1 + gamma * cpHigh) ≤ gamma * k * cpHigh := by
    nlinarith [hThresholdCore]

  have hCompare :
      experienceMaxGain tau0 gamma cpHigh lambda ≤ cpReductionGain tau0 gamma cpHigh k := by
    rw [experienceMaxGain_closed_form, cpReductionGain_closed_form]
    unfold tauTotal tauStage
    have hTau0Nonneg : 0 ≤ tau0 := hTau0.le
    have hScaled := mul_le_mul_of_nonneg_left hCompareCore hTau0Nonneg
    nlinarith [hScaled]

  exact ⟨hGainMono, rfl, hAbsEff, hCompare⟩

/-- T5.6-4: step increases in CP produce downward jumps in time allowance ratio. -/
theorem «T5.6-4»
    (tauD tau0 gamma cpBefore cpAfter lambda u : Real)
    (hTauD : 0 < tauD)
    (hTau0 : 0 < tau0)
    (hGamma : 0 < gamma)
    (hCp0 : 0 ≤ cpBefore)
    (hCpJump : cpBefore < cpAfter)
    (_hLam0 : 0 ≤ lambda)
    (_hU0 : 0 ≤ u)
    (hStab : lambda * u < 1) :
    ratio tauD tau0 gamma cpAfter lambda u < ratio tauD tau0 gamma cpBefore lambda u ∧
      ratio tauD tau0 gamma cpAfter lambda u
        - ratio tauD tau0 gamma cpBefore lambda u < 0 := by
  have hTauBeforePos : 0 < tauTotal tau0 gamma cpBefore :=
    tauTotal_pos tau0 gamma cpBefore hTau0 hGamma.le hCp0
  have hTauBeforeLtAfter :
      tauTotal tau0 gamma cpBefore < tauTotal tau0 gamma cpAfter :=
    tauTotal_strict_cp tau0 gamma cpBefore cpAfter hTau0 hGamma hCpJump
  have hOneMinusPos : 0 < 1 - lambda * u := by linarith
  let denBefore := (1 - lambda * u) * tauTotal tau0 gamma cpBefore
  let denAfter := (1 - lambda * u) * tauTotal tau0 gamma cpAfter
  have hDenBeforePos : 0 < denBefore := by
    dsimp [denBefore]
    exact mul_pos hOneMinusPos hTauBeforePos
  have hDenBeforeLtAfter :
      denBefore < denAfter := by
    dsimp [denBefore, denAfter]
    exact mul_lt_mul_of_pos_left hTauBeforeLtAfter hOneMinusPos

  have hRatioDrop :
      ratio tauD tau0 gamma cpAfter lambda u < ratio tauD tau0 gamma cpBefore lambda u := by
    have hDenAfterPos : 0 < denAfter := lt_trans hDenBeforePos hDenBeforeLtAfter
    have hInv : 1 / denAfter < 1 / denBefore :=
      one_div_lt_one_div_of_lt hDenBeforePos hDenBeforeLtAfter
    have hMul : tauD * (1 / denAfter) < tauD * (1 / denBefore) :=
      mul_lt_mul_of_pos_left hInv hTauD
    unfold ratio tauEff
    dsimp [denBefore, denAfter] at hMul
    simpa [div_eq_mul_inv, mul_assoc, mul_left_comm, mul_comm] using hMul

  constructor
  · exact hRatioDrop
  · linarith

end

end Section5_6
