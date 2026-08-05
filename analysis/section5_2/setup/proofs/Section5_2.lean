import Mathlib

namespace Section5_2

open Set

noncomputable section

/-- Organisation-level parameters used in the comparative resilience model. -/
structure Organisation where
  A : Real
  B : Real
  H : Real
  tauEff : Real

/-- Time-conditioned mobilisation share for an option class. -/
def mobilisation (tauD tauEff : Real) (epsilon : Nat) : Real :=
  min 1 ((tauD / tauEff) ^ epsilon)

/-- Time-conditioned useful count `Ã = A f_A`. -/
def Atilde (org : Organisation) (tauD : Real) (epsilonA : Nat) : Real :=
  org.A * mobilisation tauD org.tauEff epsilonA

/-- Time-conditioned survivable count `B̃ = B f_B`. -/
def Btilde (org : Organisation) (tauD : Real) (epsilonB : Nat) : Real :=
  org.B * mobilisation tauD org.tauEff epsilonB

/-- Magnitude limit `M_0` in the resilience model. -/
def M0 (k : Real) (alphaA betaH epsilonA : Nat) (tauD : Real) (org : Organisation) : Real :=
  k * (Atilde org tauD epsilonA) ^ alphaA * org.H ^ betaH

/-- Magnitude limit `M_max` in the resilience model. -/
def Mmax (k : Real) (betaB betaH epsilonB : Nat) (tauD : Real) (org : Organisation) : Real :=
  k * (Btilde org tauD epsilonB) ^ betaB * org.H ^ betaH

/-- Static form of `M_0` when mobilisation saturates. -/
def M0Static (k A H : Real) (alphaA betaH : Nat) : Real :=
  k * A ^ alphaA * H ^ betaH

/-- Static form of `M_max` when mobilisation saturates. -/
def MmaxStatic (k B H : Real) (betaB betaH : Nat) : Real :=
  k * B ^ betaB * H ^ betaH

/-- Resilience score in clamped piecewise-linear form. -/
def resilienceScore (M M0Val MmaxVal : Real) : Real :=
  max 0 (min 1 ((MmaxVal - M) / (MmaxVal - M0Val)))

/-- Comparative advantage field `ΔR = R_S - R_L`. -/
def deltaR (k : Real)
    (alphaA betaB betaH epsilonA epsilonB : Nat)
    (orgS orgL : Organisation) (tauD M : Real) : Real :=
  resilienceScore M (M0 k alphaA betaH epsilonA tauD orgS) (Mmax k betaB betaH epsilonB tauD orgS)
    - resilienceScore M (M0 k alphaA betaH epsilonA tauD orgL) (Mmax k betaB betaH epsilonB tauD orgL)

lemma resilience_nonneg (M M0Val MmaxVal : Real) :
    0 ≤ resilienceScore M M0Val MmaxVal := by
  unfold resilienceScore
  exact le_max_left 0 (min 1 ((MmaxVal - M) / (MmaxVal - M0Val)))

lemma resilience_le_one (M M0Val MmaxVal : Real) :
    resilienceScore M M0Val MmaxVal ≤ 1 := by
  unfold resilienceScore
  exact (max_le_iff.mpr ⟨by norm_num, min_le_left 1 ((MmaxVal - M) / (MmaxVal - M0Val))⟩)

lemma resilience_eq_one_of_le_M0
    (M M0Val MmaxVal : Real) (hGap : M0Val < MmaxVal) (hM : M ≤ M0Val) :
    resilienceScore M M0Val MmaxVal = 1 := by
  have hDen : 0 < MmaxVal - M0Val := sub_pos.mpr hGap
  have hNumGe : MmaxVal - M0Val ≤ MmaxVal - M := by linarith
  have hRatioGe' :
      (MmaxVal - M0Val) / (MmaxVal - M0Val) ≤ (MmaxVal - M) / (MmaxVal - M0Val) := by
    exact div_le_div_of_nonneg_right hNumGe (le_of_lt hDen)
  have hRatioGe : 1 ≤ (MmaxVal - M) / (MmaxVal - M0Val) := by
    simpa [hDen.ne'] using hRatioGe'
  unfold resilienceScore
  rw [min_eq_left hRatioGe]
  norm_num

lemma resilience_eq_zero_of_Mmax_le
    (M M0Val MmaxVal : Real) (hGap : M0Val < MmaxVal) (hM : MmaxVal ≤ M) :
    resilienceScore M M0Val MmaxVal = 0 := by
  have hDen : 0 < MmaxVal - M0Val := sub_pos.mpr hGap
  have hNumLe : MmaxVal - M ≤ 0 := by linarith
  have hRatioLe : (MmaxVal - M) / (MmaxVal - M0Val) ≤ 0 := by
    exact div_nonpos_of_nonpos_of_nonneg hNumLe (le_of_lt hDen)
  unfold resilienceScore
  have hMin : min 1 ((MmaxVal - M) / (MmaxVal - M0Val)) = (MmaxVal - M) / (MmaxVal - M0Val) := by
    exact min_eq_right (le_trans hRatioLe (by norm_num))
  rw [hMin]
  exact max_eq_left hRatioLe

lemma resilience_eq_linear_of_between
    (M M0Val MmaxVal : Real) (hGap : M0Val < MmaxVal)
    (hLow : M0Val ≤ M) (hHigh : M ≤ MmaxVal) :
    resilienceScore M M0Val MmaxVal = (MmaxVal - M) / (MmaxVal - M0Val) := by
  have hDen : 0 < MmaxVal - M0Val := sub_pos.mpr hGap
  have hNumNonneg : 0 ≤ MmaxVal - M := by linarith
  have hNumLeDen : MmaxVal - M ≤ MmaxVal - M0Val := by linarith
  have hRatioNonneg : 0 ≤ (MmaxVal - M) / (MmaxVal - M0Val) := by
    exact div_nonneg hNumNonneg (le_of_lt hDen)
  have hRatioLeOne' :
      (MmaxVal - M) / (MmaxVal - M0Val) ≤ (MmaxVal - M0Val) / (MmaxVal - M0Val) := by
    exact div_le_div_of_nonneg_right hNumLeDen (le_of_lt hDen)
  have hRatioLeOne : (MmaxVal - M) / (MmaxVal - M0Val) ≤ 1 := by
    simpa [hDen.ne'] using hRatioLeOne'
  unfold resilienceScore
  rw [min_eq_right hRatioLeOne]
  rw [max_eq_right hRatioNonneg]

lemma mobilisation_eq_one_of_saturated
    (tauD tauEff : Real) (epsilon : Nat)
    (hTauEffPos : 0 < tauEff) (hSat : tauEff ≤ tauD) :
    mobilisation tauD tauEff epsilon = 1 := by
  unfold mobilisation
  have hRatioGe : 1 ≤ tauD / tauEff := by
    have hDiv : tauEff / tauEff ≤ tauD / tauEff := by
      exact div_le_div_of_nonneg_right hSat (le_of_lt hTauEffPos)
    simpa [hTauEffPos.ne'] using hDiv
  have hPowGe : 1 ≤ (tauD / tauEff) ^ epsilon := by
    exact one_le_pow₀ hRatioGe
  exact min_eq_left hPowGe

lemma M0_eq_static_of_saturated
    (k : Real) (alphaA betaH epsilonA : Nat) (tauD : Real) (org : Organisation)
    (hTauEffPos : 0 < org.tauEff) (hSat : org.tauEff ≤ tauD) :
    M0 k alphaA betaH epsilonA tauD org = M0Static k org.A org.H alphaA betaH := by
  unfold M0 M0Static Atilde
  rw [mobilisation_eq_one_of_saturated tauD org.tauEff epsilonA hTauEffPos hSat]
  ring

lemma Mmax_eq_static_of_saturated
    (k : Real) (betaB betaH epsilonB : Nat) (tauD : Real) (org : Organisation)
    (hTauEffPos : 0 < org.tauEff) (hSat : org.tauEff ≤ tauD) :
    Mmax k betaB betaH epsilonB tauD org = MmaxStatic k org.B org.H betaB betaH := by
  unfold Mmax MmaxStatic Btilde
  rw [mobilisation_eq_one_of_saturated tauD org.tauEff epsilonB hTauEffPos hSat]
  ring

/-- T5.2-1: boundedness of resilience score and boundary values. -/
theorem «T5.2-1»
    (M M0Val MmaxVal : Real) (hGap : M0Val < MmaxVal) :
    0 ≤ resilienceScore M M0Val MmaxVal ∧
      resilienceScore M M0Val MmaxVal ≤ 1 ∧
      (M ≤ M0Val → resilienceScore M M0Val MmaxVal = 1) ∧
      (MmaxVal ≤ M → resilienceScore M M0Val MmaxVal = 0) := by
  refine ⟨resilience_nonneg M M0Val MmaxVal, resilience_le_one M M0Val MmaxVal, ?_, ?_⟩
  · intro hM
    exact resilience_eq_one_of_le_M0 M M0Val MmaxVal hGap hM
  · intro hM
    exact resilience_eq_zero_of_Mmax_le M M0Val MmaxVal hGap hM

/-- Sufficient-condition factor for `M_0` in the scarce-time branch. -/
def factorM0
    (A_S A_L tauEff_S tauEff_L H_S H_L : Real)
    (alphaA betaH epsilonA : Nat) : Real :=
  (A_S / A_L) ^ alphaA * (tauEff_L / tauEff_S) ^ (alphaA * epsilonA) * (H_S / H_L) ^ betaH

/-- Sufficient-condition factor for `M_max` in the scarce-time branch. -/
def factorMmax
    (B_S B_L tauEff_S tauEff_L H_S H_L : Real)
    (betaB betaH epsilonB : Nat) : Real :=
  (B_S / B_L) ^ betaB * (tauEff_L / tauEff_S) ^ (betaB * epsilonB) * (H_S / H_L) ^ betaH

/-- T5.2-2: sufficient condition for VSE advantage in fast disturbances.
    The decomposition equalities capture scarce-branch algebra. -/
theorem «T5.2-2»
    (A_S A_L B_S B_L tauEff_S tauEff_L H_S H_L : Real)
    (alphaA betaB betaH epsilonA epsilonB : Nat)
    (M0_S M0_L Mmax_S Mmax_L : Real)
    (_hA : A_S < A_L) (_hB : B_S < B_L) (_hTau : tauEff_S < tauEff_L)
    (hM0Decomp : M0_S = M0_L * factorM0 A_S A_L tauEff_S tauEff_L H_S H_L alphaA betaH epsilonA)
    (hMmaxDecomp :
      Mmax_S = Mmax_L * factorMmax B_S B_L tauEff_S tauEff_L H_S H_L betaB betaH epsilonB)
    (hM0Cond : factorM0 A_S A_L tauEff_S tauEff_L H_S H_L alphaA betaH epsilonA > 1)
    (hMmaxCond : factorMmax B_S B_L tauEff_S tauEff_L H_S H_L betaB betaH epsilonB > 1)
    (hM0LPos : 0 < M0_L) (hMmaxLPos : 0 < Mmax_L) :
    M0_S > M0_L ∧ Mmax_S > Mmax_L := by
  have hM0 : M0_L * 1 < M0_L * factorM0 A_S A_L tauEff_S tauEff_L H_S H_L alphaA betaH epsilonA := by
    exact mul_lt_mul_of_pos_left hM0Cond hM0LPos
  have hMmax :
      Mmax_L * 1 < Mmax_L * factorMmax B_S B_L tauEff_S tauEff_L H_S H_L betaB betaH epsilonB := by
    exact mul_lt_mul_of_pos_left hMmaxCond hMmaxLPos
  constructor
  · rw [hM0Decomp]
    simpa using hM0
  · rw [hMmaxDecomp]
    simpa using hMmax

/-- T5.2-3: in the slow regime the limits reduce to static forms,
    and if `A_S < A_L` and `H_S ≤ H_L` then `M0_S ≤ M0_L`. -/
theorem «T5.2-3»
    (k tauD : Real)
    (alphaA betaB betaH epsilonA epsilonB : Nat)
    (orgS orgL : Organisation)
    (hK : 0 ≤ k)
    (hTauSPos : 0 < orgS.tauEff) (hTauLPos : 0 < orgL.tauEff)
    (hSatS : orgS.tauEff ≤ tauD) (hSatL : orgL.tauEff ≤ tauD)
    (hA : orgS.A < orgL.A) (hH : orgS.H ≤ orgL.H)
    (hANonneg : 0 ≤ orgS.A) (hHNonneg : 0 ≤ orgS.H)
    (_hBNonneg : 0 ≤ orgS.B) :
    (M0 k alphaA betaH epsilonA tauD orgS = M0Static k orgS.A orgS.H alphaA betaH) ∧
      (M0 k alphaA betaH epsilonA tauD orgL = M0Static k orgL.A orgL.H alphaA betaH) ∧
      (Mmax k betaB betaH epsilonB tauD orgS = MmaxStatic k orgS.B orgS.H betaB betaH) ∧
      (Mmax k betaB betaH epsilonB tauD orgL = MmaxStatic k orgL.B orgL.H betaB betaH) ∧
      (M0 k alphaA betaH epsilonA tauD orgS ≤ M0 k alphaA betaH epsilonA tauD orgL) := by
  have hEqM0S : M0 k alphaA betaH epsilonA tauD orgS = M0Static k orgS.A orgS.H alphaA betaH :=
    M0_eq_static_of_saturated k alphaA betaH epsilonA tauD orgS hTauSPos hSatS
  have hEqM0L : M0 k alphaA betaH epsilonA tauD orgL = M0Static k orgL.A orgL.H alphaA betaH :=
    M0_eq_static_of_saturated k alphaA betaH epsilonA tauD orgL hTauLPos hSatL
  have hEqMmaxS : Mmax k betaB betaH epsilonB tauD orgS = MmaxStatic k orgS.B orgS.H betaB betaH :=
    Mmax_eq_static_of_saturated k betaB betaH epsilonB tauD orgS hTauSPos hSatS
  have hEqMmaxL : Mmax k betaB betaH epsilonB tauD orgL = MmaxStatic k orgL.B orgL.H betaB betaH :=
    Mmax_eq_static_of_saturated k betaB betaH epsilonB tauD orgL hTauLPos hSatL

  have hALNonneg : 0 ≤ orgL.A := by linarith
  have hHLNonneg : 0 ≤ orgL.H := by linarith
  have hApow : orgS.A ^ alphaA ≤ orgL.A ^ alphaA :=
    pow_le_pow_left₀ hANonneg hA.le alphaA
  have hHpow : orgS.H ^ betaH ≤ orgL.H ^ betaH :=
    pow_le_pow_left₀ hHNonneg hH betaH
  have hProd : orgS.A ^ alphaA * orgS.H ^ betaH ≤ orgL.A ^ alphaA * orgL.H ^ betaH := by
    exact mul_le_mul hApow hHpow (pow_nonneg hHNonneg betaH) (pow_nonneg hALNonneg alphaA)
  have hScaled :
      k * (orgS.A ^ alphaA * orgS.H ^ betaH) ≤ k * (orgL.A ^ alphaA * orgL.H ^ betaH) :=
    mul_le_mul_of_nonneg_left hProd hK
  have hM0Le : M0 k alphaA betaH epsilonA tauD orgS ≤ M0 k alphaA betaH epsilonA tauD orgL := by
    rw [hEqM0S, hEqM0L]
    unfold M0Static
    simpa [mul_assoc, mul_left_comm, mul_comm] using hScaled

  refine ⟨hEqM0S, hEqM0L, hEqMmaxS, hEqMmaxL, hM0Le⟩

/-- Explicit constructive parameter set for Section 5.2 parity analysis. -/
def orgVSE : Organisation :=
  { A := 2, B := 6, H := 9 / 10, tauEff := 1 }

/-- Explicit constructive parameter set for Section 5.2 parity analysis. -/
def orgLarge : Organisation :=
  { A := 4, B := 8, H := 1, tauEff := 5 }

abbrev kVal : Real := 1
abbrev alphaAVal : Nat := 1
abbrev betaBVal : Nat := 1
abbrev betaHVal : Nat := 1
abbrev epsilonAVal : Nat := 1
abbrev epsilonBVal : Nat := 1

/-- Comparative advantage for the constructive parameter set. -/
def deltaRExample (tauD M : Real) : Real :=
  deltaR kVal alphaAVal betaBVal betaHVal epsilonAVal epsilonBVal orgVSE orgLarge tauD M

lemma deltaR_fast_positive_on_interval
    (M : Real) (hLow : 21 / 10 ≤ M) (hHigh : M ≤ 23 / 10) :
    0 < deltaRExample (1 / 2) M := by
  have hRS : resilienceScore M (9 / 10) (27 / 10) = (27 / 10 - M) / (27 / 10 - 9 / 10) := by
    apply resilience_eq_linear_of_between
    · norm_num
    · linarith
    · linarith
  have hRL : resilienceScore M (2 / 5) (4 / 5) = 0 := by
    apply resilience_eq_zero_of_Mmax_le
    · norm_num
    · linarith
  have hTarget :
      deltaRExample (1 / 2) M = resilienceScore M (9 / 10) (27 / 10) - resilienceScore M (2 / 5) (4 / 5) := by
    unfold deltaRExample deltaR
    unfold kVal alphaAVal betaBVal betaHVal epsilonAVal epsilonBVal
    unfold orgVSE orgLarge
    unfold M0 Mmax Atilde Btilde mobilisation
    norm_num
  rw [hTarget]
  rw [hRS, hRL]
  have hNumPos : 0 < 27 / 10 - M := by linarith
  have hDenPos : 0 < (27 : Real) / 10 - (9 : Real) / 10 := by norm_num
  have hDivPos : 0 < (27 / 10 - M) / (27 / 10 - 9 / 10) := div_pos hNumPos hDenPos
  simpa using hDivPos

lemma deltaR_slow_negative_on_interval
    (M : Real) (hLow : 21 / 10 ≤ M) (hHigh : M ≤ 23 / 10) :
    deltaRExample 10 M < 0 := by
  have hRS : resilienceScore M (9 / 5) (27 / 5) = (27 / 5 - M) / (27 / 5 - 9 / 5) := by
    apply resilience_eq_linear_of_between
    · norm_num
    · linarith
    · linarith
  have hRL : resilienceScore M 4 8 = 1 := by
    apply resilience_eq_one_of_le_M0
    · norm_num
    · linarith
  have hTarget :
      deltaRExample 10 M = resilienceScore M (9 / 5) (27 / 5) - resilienceScore M 4 8 := by
    unfold deltaRExample deltaR
    unfold kVal alphaAVal betaBVal betaHVal epsilonAVal epsilonBVal
    unfold orgVSE orgLarge
    unfold M0 Mmax Atilde Btilde mobilisation
    norm_num
  rw [hTarget]
  rw [hRS, hRL]
  have hDenPos : 0 < (27 : Real) / 5 - (9 : Real) / 5 := by norm_num
  have hNumLt : 27 / 5 - M < 27 / 5 - 9 / 5 := by linarith
  have hRatioLtOne' :
      (27 / 5 - M) / (27 / 5 - 9 / 5) < (27 / 5 - 9 / 5) / (27 / 5 - 9 / 5) := by
    exact div_lt_div_of_pos_right hNumLt hDenPos
  have hRatioLtOne : (27 / 5 - M) / (27 / 5 - 9 / 5) < 1 := by
    have hEq : ((27 / 5 - 9 / 5) / (27 / 5 - 9 / 5) : Real) = 1 := by
      field_simp [hDenPos.ne']
    simpa [hEq] using hRatioLtOne'
  linarith

/-- Constructive sign reversal for `ΔR` on a non-empty disturbance-magnitude interval.
    This provides the witness regime used for T5.2-4. -/
theorem t5_2_4_sign_interval :
    ∃ Mlo Mhi tauFast tauSlow,
      Mlo < Mhi ∧
      tauFast < tauSlow ∧
      (∀ M, Mlo ≤ M → M ≤ Mhi → 0 < deltaRExample tauFast M) ∧
      (∀ M, Mlo ≤ M → M ≤ Mhi → deltaRExample tauSlow M < 0) := by
  refine ⟨21 / 10, 23 / 10, 1 / 2, 10, by norm_num, by norm_num, ?_, ?_⟩
  · intro M hLow hHigh
    simpa using deltaR_fast_positive_on_interval M hLow hHigh
  · intro M hLow hHigh
    simpa using deltaR_slow_negative_on_interval M hLow hHigh

/-- T5.2-4: existence of a parity boundary crossing time for a constructive parameter witness. -/
theorem «T5.2-4»
    (hCont : ContinuousOn (fun tau : Real => deltaRExample tau (11 / 5)) (Icc (1 / 2) 10)) :
    ∃ tauStar ∈ Icc (1 / 2) 10, deltaRExample tauStar (11 / 5) = 0 := by
  have hPos : 0 < deltaRExample (1 / 2) (11 / 5) := by
    exact deltaR_fast_positive_on_interval (11 / 5) (by norm_num) (by norm_num)
  have hNeg : deltaRExample 10 (11 / 5) < 0 := by
    exact deltaR_slow_negative_on_interval (11 / 5) (by norm_num) (by norm_num)
  have hZeroIn : (0 : Real) ∈ Icc (deltaRExample 10 (11 / 5)) (deltaRExample (1 / 2) (11 / 5)) := by
    exact ⟨le_of_lt hNeg, le_of_lt hPos⟩
  have hImage : (0 : Real) ∈ (fun tau : Real => deltaRExample tau (11 / 5)) '' Icc (1 / 2) 10 := by
    exact intermediate_value_Icc' (by norm_num : (1 / 2 : Real) ≤ 10) hCont hZeroIn
  rcases hImage with ⟨tauStar, hTauMem, hTauEq⟩
  exact ⟨tauStar, hTauMem, hTauEq⟩

end

end Section5_2
