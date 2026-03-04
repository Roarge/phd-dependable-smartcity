import Mathlib

namespace Section5_3

open scoped BigOperators

noncomputable section

/-- Dot product for structural drag sensitivities and complexity-potential vector. -/
def dot {n : Nat} (gamma cp : Fin n → Real) : Real :=
  ∑ i, gamma i * cp i

/-- Stage response time with structural drag. -/
def stageTime {n : Nat} (tau0 : Real) (gamma cp : Fin n → Real) : Real :=
  tau0 * (1 + dot gamma cp)

/-- Total response time decomposition. -/
def tauTotal {n : Nat}
    (tauDetect0 tauDecide0 tauExecute0 : Real)
    (gammaDetect gammaDecide gammaExecute cp : Fin n → Real) : Real :=
  stageTime tauDetect0 gammaDetect cp
    + stageTime tauDecide0 gammaDecide cp
    + stageTime tauExecute0 gammaExecute cp

/-- Skill multiplier for effective mobilisation time. -/
def sigmaTau (lambdaTau u : Real) : Real :=
  1 - lambdaTau * u

/-- Effective mobilisation time. -/
def tauEff (lambdaTau u tau : Real) : Real :=
  sigmaTau lambdaTau u * tau

/-- Time allowance ratio. -/
def ratio (tauD tauEffVal : Real) : Real :=
  tauD / tauEffVal

/-- Generic mobilisation fraction shape from the model family. -/
def mobilisationFraction (r eps : Real) : Real :=
  min 1 (r ^ eps)

/-- Cognitive headroom component. -/
def Hcog (h u q : Real) : Real :=
  h + (1 - h) * u * q

/-- Total headroom. -/
def Htot (Hphys h u q : Real) : Real :=
  Hphys * Hcog h u q

/-- Magnitude threshold form for useful variety. -/
def M0Thresh (k Aeff H : Real) (alphaA betaH : Nat) : Real :=
  k * Aeff ^ alphaA * H ^ betaH

/-- Magnitude threshold form for survivable variety. -/
def MmaxThresh (k Beff H : Real) (betaB betaH : Nat) : Real :=
  k * Beff ^ betaB * H ^ betaH

lemma dot_nonneg {n : Nat} (gamma cp : Fin n → Real)
    (hGamma : ∀ i, 0 ≤ gamma i) (hCP : ∀ i, 0 ≤ cp i) :
    0 ≤ dot gamma cp := by
  unfold dot
  exact Finset.sum_nonneg (fun i _ => mul_nonneg (hGamma i) (hCP i))

lemma dot_mono {n : Nat} (gamma cp1 cp2 : Fin n → Real)
    (hGamma : ∀ i, 0 ≤ gamma i) (hCP : ∀ i, cp1 i ≤ cp2 i) :
    dot gamma cp1 ≤ dot gamma cp2 := by
  unfold dot
  refine Finset.sum_le_sum ?_
  intro i _
  exact mul_le_mul_of_nonneg_left (hCP i) (hGamma i)

lemma stageTime_nonneg {n : Nat}
    (tau0 : Real) (gamma cp : Fin n → Real)
    (hTau0 : 0 ≤ tau0)
    (hGamma : ∀ i, 0 ≤ gamma i)
    (hCP : ∀ i, 0 ≤ cp i) :
    0 ≤ stageTime tau0 gamma cp := by
  unfold stageTime
  have hDot : 0 ≤ dot gamma cp := dot_nonneg gamma cp hGamma hCP
  have hMul : 0 ≤ 1 + dot gamma cp := by linarith
  exact mul_nonneg hTau0 hMul

lemma stageTime_strict_mono_tau0 {n : Nat}
    (tau0 tau0' : Real) (gamma cp : Fin n → Real)
    (hTau : tau0 < tau0')
    (hGamma : ∀ i, 0 ≤ gamma i)
    (hCP : ∀ i, 0 ≤ cp i) :
    stageTime tau0 gamma cp < stageTime tau0' gamma cp := by
  unfold stageTime
  have hDot : 0 ≤ dot gamma cp := dot_nonneg gamma cp hGamma hCP
  have hFactor : 0 < 1 + dot gamma cp := by linarith
  exact mul_lt_mul_of_pos_right hTau hFactor

lemma stageTime_mono_cp {n : Nat}
    (tau0 : Real) (gamma cp1 cp2 : Fin n → Real)
    (hTau0 : 0 ≤ tau0)
    (hGamma : ∀ i, 0 ≤ gamma i)
    (hCP : ∀ i, cp1 i ≤ cp2 i) :
    stageTime tau0 gamma cp1 ≤ stageTime tau0 gamma cp2 := by
  unfold stageTime
  have hDot : dot gamma cp1 ≤ dot gamma cp2 := dot_mono gamma cp1 cp2 hGamma hCP
  have hFactor : 1 + dot gamma cp1 ≤ 1 + dot gamma cp2 := by linarith
  exact mul_le_mul_of_nonneg_left hFactor hTau0

lemma tauTotal_nonneg {n : Nat}
    (tauDetect0 tauDecide0 tauExecute0 : Real)
    (gammaDetect gammaDecide gammaExecute cp : Fin n → Real)
    (hTauDetect0 : 0 ≤ tauDetect0)
    (hTauDecide0 : 0 ≤ tauDecide0)
    (hTauExecute0 : 0 ≤ tauExecute0)
    (hGammaDetect : ∀ i, 0 ≤ gammaDetect i)
    (hGammaDecide : ∀ i, 0 ≤ gammaDecide i)
    (hGammaExecute : ∀ i, 0 ≤ gammaExecute i)
    (hCP : ∀ i, 0 ≤ cp i) :
    0 ≤ tauTotal tauDetect0 tauDecide0 tauExecute0 gammaDetect gammaDecide gammaExecute cp := by
  unfold tauTotal
  have h1 := stageTime_nonneg tauDetect0 gammaDetect cp hTauDetect0 hGammaDetect hCP
  have h2 := stageTime_nonneg tauDecide0 gammaDecide cp hTauDecide0 hGammaDecide hCP
  have h3 := stageTime_nonneg tauExecute0 gammaExecute cp hTauExecute0 hGammaExecute hCP
  linarith

lemma tauTotal_strict_tauDetect0 {n : Nat}
    (tauDetect0 tauDetect0' tauDecide0 tauExecute0 : Real)
    (gammaDetect gammaDecide gammaExecute cp : Fin n → Real)
    (hTau : tauDetect0 < tauDetect0')
    (hGammaDetect : ∀ i, 0 ≤ gammaDetect i)
    (hCP : ∀ i, 0 ≤ cp i) :
    tauTotal tauDetect0 tauDecide0 tauExecute0 gammaDetect gammaDecide gammaExecute cp
      < tauTotal tauDetect0' tauDecide0 tauExecute0 gammaDetect gammaDecide gammaExecute cp := by
  unfold tauTotal
  have hDet := stageTime_strict_mono_tau0 tauDetect0 tauDetect0' gammaDetect cp hTau hGammaDetect hCP
  linarith

lemma tauTotal_strict_tauDecide0 {n : Nat}
    (tauDetect0 tauDecide0 tauDecide0' tauExecute0 : Real)
    (gammaDetect gammaDecide gammaExecute cp : Fin n → Real)
    (hTau : tauDecide0 < tauDecide0')
    (hGammaDecide : ∀ i, 0 ≤ gammaDecide i)
    (hCP : ∀ i, 0 ≤ cp i) :
    tauTotal tauDetect0 tauDecide0 tauExecute0 gammaDetect gammaDecide gammaExecute cp
      < tauTotal tauDetect0 tauDecide0' tauExecute0 gammaDetect gammaDecide gammaExecute cp := by
  unfold tauTotal
  have hDec := stageTime_strict_mono_tau0 tauDecide0 tauDecide0' gammaDecide cp hTau hGammaDecide hCP
  linarith

lemma tauTotal_strict_tauExecute0 {n : Nat}
    (tauDetect0 tauDecide0 tauExecute0 tauExecute0' : Real)
    (gammaDetect gammaDecide gammaExecute cp : Fin n → Real)
    (hTau : tauExecute0 < tauExecute0')
    (hGammaExecute : ∀ i, 0 ≤ gammaExecute i)
    (hCP : ∀ i, 0 ≤ cp i) :
    tauTotal tauDetect0 tauDecide0 tauExecute0 gammaDetect gammaDecide gammaExecute cp
      < tauTotal tauDetect0 tauDecide0 tauExecute0' gammaDetect gammaDecide gammaExecute cp := by
  unfold tauTotal
  have hExe := stageTime_strict_mono_tau0 tauExecute0 tauExecute0' gammaExecute cp hTau hGammaExecute hCP
  linarith

lemma tauTotal_mono_cp {n : Nat}
    (tauDetect0 tauDecide0 tauExecute0 : Real)
    (gammaDetect gammaDecide gammaExecute cp1 cp2 : Fin n → Real)
    (hTauDetect0 : 0 ≤ tauDetect0)
    (hTauDecide0 : 0 ≤ tauDecide0)
    (hTauExecute0 : 0 ≤ tauExecute0)
    (hGammaDetect : ∀ i, 0 ≤ gammaDetect i)
    (hGammaDecide : ∀ i, 0 ≤ gammaDecide i)
    (hGammaExecute : ∀ i, 0 ≤ gammaExecute i)
    (hCP : ∀ i, cp1 i ≤ cp2 i) :
    tauTotal tauDetect0 tauDecide0 tauExecute0 gammaDetect gammaDecide gammaExecute cp1
      ≤ tauTotal tauDetect0 tauDecide0 tauExecute0 gammaDetect gammaDecide gammaExecute cp2 := by
  unfold tauTotal
  have h1 := stageTime_mono_cp tauDetect0 gammaDetect cp1 cp2 hTauDetect0 hGammaDetect hCP
  have h2 := stageTime_mono_cp tauDecide0 gammaDecide cp1 cp2 hTauDecide0 hGammaDecide hCP
  have h3 := stageTime_mono_cp tauExecute0 gammaExecute cp1 cp2 hTauExecute0 hGammaExecute hCP
  linarith

lemma sigmaTau_bounds (lambdaTau u : Real)
    (hLambda0 : 0 ≤ lambdaTau) (_hLambda1 : lambdaTau ≤ 1)
    (hU0 : 0 ≤ u) (hU1 : u ≤ 1) :
    1 - lambdaTau ≤ sigmaTau lambdaTau u ∧ sigmaTau lambdaTau u ≤ 1 := by
  unfold sigmaTau
  have hMulLe : lambdaTau * u ≤ lambdaTau := by
    have hMul : lambdaTau * u ≤ lambdaTau * 1 :=
      mul_le_mul_of_nonneg_left hU1 hLambda0
    simpa using hMul
  have hMulNonneg : 0 ≤ lambdaTau * u := mul_nonneg hLambda0 hU0
  constructor
  · linarith
  · linarith

lemma tauEff_mono_tau (lambdaTau u tau1 tau2 : Real)
    (hSigma : 0 ≤ sigmaTau lambdaTau u) (hTau : tau1 ≤ tau2) :
    tauEff lambdaTau u tau1 ≤ tauEff lambdaTau u tau2 := by
  unfold tauEff
  exact mul_le_mul_of_nonneg_left hTau hSigma

lemma tauEff_interval (lambdaTau u tau : Real)
    (hLambda0 : 0 ≤ lambdaTau) (hLambda1 : lambdaTau ≤ 1)
    (hU0 : 0 ≤ u) (hU1 : u ≤ 1)
    (hTau0 : 0 ≤ tau) :
    (1 - lambdaTau) * tau ≤ tauEff lambdaTau u tau ∧ tauEff lambdaTau u tau ≤ tau := by
  have hSigma := sigmaTau_bounds lambdaTau u hLambda0 hLambda1 hU0 hU1
  constructor
  · unfold tauEff
    exact mul_le_mul_of_nonneg_right hSigma.1 hTau0
  · unfold tauEff
    simpa using mul_le_mul_of_nonneg_right hSigma.2 hTau0

lemma ratio_nonincrease
    (tauD0 tauD1 tauEff0 tauEff1 : Real)
    (hTauD1Nonneg : 0 ≤ tauD1)
    (hTauDDecrease : tauD1 ≤ tauD0)
    (hTauEff0Pos : 0 < tauEff0)
    (hTauEffIncrease : tauEff0 ≤ tauEff1) :
    ratio tauD1 tauEff1 ≤ ratio tauD0 tauEff0 := by
  have hTauEff1Pos : 0 < tauEff1 := lt_of_lt_of_le hTauEff0Pos hTauEffIncrease
  unfold ratio
  have hStep1 : tauD1 / tauEff1 ≤ tauD0 / tauEff1 :=
    div_le_div_of_nonneg_right hTauDDecrease (le_of_lt hTauEff1Pos)
  have hTauD0Nonneg : 0 ≤ tauD0 := le_trans hTauD1Nonneg hTauDDecrease
  have hStep2 : tauD0 / tauEff1 ≤ tauD0 / tauEff0 :=
    div_le_div_of_nonneg_left hTauD0Nonneg hTauEff0Pos hTauEffIncrease
  exact le_trans hStep1 hStep2

lemma Hcog_lower_bound (h u q : Real)
    (_hH0 : 0 ≤ h) (hH1 : h ≤ 1)
    (hU0 : 0 ≤ u) (hQ0 : 0 ≤ q) :
    h ≤ Hcog h u q := by
  unfold Hcog
  have hOneMinusH : 0 ≤ 1 - h := by linarith
  have hUQ : 0 ≤ u * q := mul_nonneg hU0 hQ0
  have hTerm : 0 ≤ (1 - h) * u * q := mul_nonneg (mul_nonneg hOneMinusH hU0) hQ0
  linarith

lemma Hcog_mono_h (h1 h2 u q : Real)
    (hH : h1 ≤ h2)
    (hU0 : 0 ≤ u) (hU1 : u ≤ 1)
    (hQ0 : 0 ≤ q) (hQ1 : q ≤ 1) :
    Hcog h1 u q ≤ Hcog h2 u q := by
  unfold Hcog
  have hUQNonneg : 0 ≤ u * q := mul_nonneg hU0 hQ0
  have hUQLeOne : u * q ≤ 1 := by
    nlinarith [hU1, hQ1]
  have hOneMinusUQ : 0 ≤ 1 - u * q := by linarith
  have hDiffNonneg : 0 ≤ (h2 - h1) * (1 - u * q) :=
    mul_nonneg (by linarith) hOneMinusUQ
  nlinarith [hUQNonneg, hDiffNonneg]

lemma M0Thresh_mono_Aeff (k Aeff1 Aeff2 H : Real) (alphaA betaH : Nat)
    (hK : 0 ≤ k) (hH : 0 ≤ H)
    (hAeff1 : 0 ≤ Aeff1) (hAeff : Aeff1 ≤ Aeff2) :
    M0Thresh k Aeff1 H alphaA betaH ≤ M0Thresh k Aeff2 H alphaA betaH := by
  unfold M0Thresh
  have hPow : Aeff1 ^ alphaA ≤ Aeff2 ^ alphaA :=
    pow_le_pow_left₀ hAeff1 hAeff alphaA
  have hScaled : k * Aeff1 ^ alphaA ≤ k * Aeff2 ^ alphaA :=
    mul_le_mul_of_nonneg_left hPow hK
  have hHpow : 0 ≤ H ^ betaH := pow_nonneg hH betaH
  exact mul_le_mul_of_nonneg_right hScaled hHpow

lemma MmaxThresh_mono_Beff (k Beff1 Beff2 H : Real) (betaB betaH : Nat)
    (hK : 0 ≤ k) (hH : 0 ≤ H)
    (hBeff1 : 0 ≤ Beff1) (hBeff : Beff1 ≤ Beff2) :
    MmaxThresh k Beff1 H betaB betaH ≤ MmaxThresh k Beff2 H betaB betaH := by
  unfold MmaxThresh
  have hPow : Beff1 ^ betaB ≤ Beff2 ^ betaB :=
    pow_le_pow_left₀ hBeff1 hBeff betaB
  have hScaled : k * Beff1 ^ betaB ≤ k * Beff2 ^ betaB :=
    mul_le_mul_of_nonneg_left hPow hK
  have hHpow : 0 ≤ H ^ betaH := pow_nonneg hH betaH
  exact mul_le_mul_of_nonneg_right hScaled hHpow

/-- T5.3-1: monotonicity of `tau` and `tau_eff` with lower bound. -/
theorem «T5.3-1» {n : Nat}
    (tauDetect0 tauDetect0' tauDecide0 tauDecide0' tauExecute0 tauExecute0' : Real)
    (gammaDetect gammaDecide gammaExecute cp cp' : Fin n → Real)
    (lambdaTau u : Real)
    (hTauDetectInc : tauDetect0 < tauDetect0')
    (hTauDecideInc : tauDecide0 < tauDecide0')
    (hTauExecuteInc : tauExecute0 < tauExecute0')
    (hTauDetect0 : 0 ≤ tauDetect0)
    (hTauDecide0 : 0 ≤ tauDecide0)
    (hTauExecute0 : 0 ≤ tauExecute0)
    (hGammaDetect : ∀ i, 0 ≤ gammaDetect i)
    (hGammaDecide : ∀ i, 0 ≤ gammaDecide i)
    (hGammaExecute : ∀ i, 0 ≤ gammaExecute i)
    (hCPNonneg : ∀ i, 0 ≤ cp i)
    (hCPMono : ∀ i, cp i ≤ cp' i)
    (hLambda0 : 0 ≤ lambdaTau) (hLambda1 : lambdaTau ≤ 1)
    (hU0 : 0 ≤ u) (hU1 : u ≤ 1) :
    (tauTotal tauDetect0 tauDecide0 tauExecute0 gammaDetect gammaDecide gammaExecute cp
      < tauTotal tauDetect0' tauDecide0 tauExecute0 gammaDetect gammaDecide gammaExecute cp) ∧
    (tauTotal tauDetect0 tauDecide0 tauExecute0 gammaDetect gammaDecide gammaExecute cp
      < tauTotal tauDetect0 tauDecide0' tauExecute0 gammaDetect gammaDecide gammaExecute cp) ∧
    (tauTotal tauDetect0 tauDecide0 tauExecute0 gammaDetect gammaDecide gammaExecute cp
      < tauTotal tauDetect0 tauDecide0 tauExecute0' gammaDetect gammaDecide gammaExecute cp) ∧
    (tauTotal tauDetect0 tauDecide0 tauExecute0 gammaDetect gammaDecide gammaExecute cp
      ≤ tauTotal tauDetect0 tauDecide0 tauExecute0 gammaDetect gammaDecide gammaExecute cp') ∧
    (tauEff lambdaTau u
        (tauTotal tauDetect0 tauDecide0 tauExecute0 gammaDetect gammaDecide gammaExecute cp)
      ≤ tauEff lambdaTau u
        (tauTotal tauDetect0 tauDecide0 tauExecute0 gammaDetect gammaDecide gammaExecute cp')) ∧
    ((1 - lambdaTau)
      * (tauTotal tauDetect0 tauDecide0 tauExecute0 gammaDetect gammaDecide gammaExecute cp)
      ≤ tauEff lambdaTau u
        (tauTotal tauDetect0 tauDecide0 tauExecute0 gammaDetect gammaDecide gammaExecute cp)) := by
  have hTauDetect := tauTotal_strict_tauDetect0 tauDetect0 tauDetect0' tauDecide0 tauExecute0
    gammaDetect gammaDecide gammaExecute cp hTauDetectInc hGammaDetect hCPNonneg
  have hTauDecide := tauTotal_strict_tauDecide0 tauDetect0 tauDecide0 tauDecide0' tauExecute0
    gammaDetect gammaDecide gammaExecute cp hTauDecideInc hGammaDecide hCPNonneg
  have hTauExecute := tauTotal_strict_tauExecute0 tauDetect0 tauDecide0 tauExecute0 tauExecute0'
    gammaDetect gammaDecide gammaExecute cp hTauExecuteInc hGammaExecute hCPNonneg
  have hTauCP := tauTotal_mono_cp tauDetect0 tauDecide0 tauExecute0
    gammaDetect gammaDecide gammaExecute cp cp'
    hTauDetect0 hTauDecide0 hTauExecute0
    hGammaDetect hGammaDecide hGammaExecute hCPMono
  have hSigmaBounds := sigmaTau_bounds lambdaTau u hLambda0 hLambda1 hU0 hU1
  have hSigmaNonneg : 0 ≤ sigmaTau lambdaTau u := by
    have hOneMinusNonneg : 0 ≤ 1 - lambdaTau := by linarith
    exact le_trans hOneMinusNonneg hSigmaBounds.1
  have hTauEffCP := tauEff_mono_tau lambdaTau u
    (tauTotal tauDetect0 tauDecide0 tauExecute0 gammaDetect gammaDecide gammaExecute cp)
    (tauTotal tauDetect0 tauDecide0 tauExecute0 gammaDetect gammaDecide gammaExecute cp')
    hSigmaNonneg
    hTauCP
  have hTauNonneg := tauTotal_nonneg tauDetect0 tauDecide0 tauExecute0
    gammaDetect gammaDecide gammaExecute cp
    hTauDetect0 hTauDecide0 hTauExecute0
    hGammaDetect hGammaDecide hGammaExecute hCPNonneg
  have hTauEffLower := (tauEff_interval lambdaTau u
    (tauTotal tauDetect0 tauDecide0 tauExecute0 gammaDetect gammaDecide gammaExecute cp)
    hLambda0 hLambda1 hU0 hU1 hTauNonneg).1
  exact ⟨hTauDetect, hTauDecide, hTauExecute, hTauCP, hTauEffCP, hTauEffLower⟩

/-- T5.3-2: reduced time allowance ratio does not increase mobilisation fractions. -/
theorem «T5.3-2»
    (fA fB fC : Real → Real)
    (hMonA : Monotone fA) (hMonB : Monotone fB) (hMonC : Monotone fC)
    (hSatA : ∀ r, 1 ≤ r → fA r = 1)
    (hSatB : ∀ r, 1 ≤ r → fB r = 1)
    (hSatC : ∀ r, 1 ≤ r → fC r = 1)
    (tauD0 tauD1 tauEff0 tauEff1 : Real)
    (hTauD1Nonneg : 0 ≤ tauD1)
    (hTauDDecrease : tauD1 ≤ tauD0)
    (hTauEff0Pos : 0 < tauEff0)
    (hTauEffIncrease : tauEff0 ≤ tauEff1) :
    let r0 := ratio tauD0 tauEff0
    let r1 := ratio tauD1 tauEff1
    r1 ≤ r0 ∧
      fA r1 ≤ fA r0 ∧
      fB r1 ≤ fB r0 ∧
      fC r1 ≤ fC r0 ∧
      (1 ≤ r1 → fA r1 = 1 ∧ fB r1 = 1 ∧ fC r1 = 1) := by
  dsimp
  have hR : ratio tauD1 tauEff1 ≤ ratio tauD0 tauEff0 :=
    ratio_nonincrease tauD0 tauD1 tauEff0 tauEff1 hTauD1Nonneg hTauDDecrease hTauEff0Pos hTauEffIncrease
  refine ⟨hR, hMonA hR, hMonB hR, hMonC hR, ?_⟩
  intro hR1
  exact ⟨hSatA _ hR1, hSatB _ hR1, hSatC _ hR1⟩

/-- T5.3-3: bounded skill multiplier and bounded effective mobilisation time. -/
theorem «T5.3-3»
    (lambdaTau u tau : Real)
    (hLambda0 : 0 ≤ lambdaTau) (hLambda1 : lambdaTau ≤ 1)
    (hU0 : 0 ≤ u) (hU1 : u ≤ 1)
    (hTau0 : 0 ≤ tau) :
    sigmaTau lambdaTau u ∈ Set.Icc (1 - lambdaTau) 1 ∧
      tauEff lambdaTau u tau ∈ Set.Icc ((1 - lambdaTau) * tau) tau := by
  have hSigma := sigmaTau_bounds lambdaTau u hLambda0 hLambda1 hU0 hU1
  have hTau := tauEff_interval lambdaTau u tau hLambda0 hLambda1 hU0 hU1 hTau0
  exact ⟨⟨hSigma.1, hSigma.2⟩, ⟨hTau.1, hTau.2⟩⟩

/-- T5.3-4: designed reserve lower-bounds cognitive headroom and is distinct from skill changes. -/
theorem «T5.3-4»
    (h h1 h2 u q : Real)
    (hH0 : 0 ≤ h) (hH1 : h ≤ 1)
    (hU0 : 0 ≤ u) (hU1 : u ≤ 1)
    (hQ0 : 0 ≤ q) (hQ1 : q ≤ 1)
    (hHInc : h1 ≤ h2) :
    h ≤ Hcog h u q ∧ Hcog h1 u q ≤ Hcog h2 u q := by
  constructor
  · exact Hcog_lower_bound h u q hH0 hH1 hU0 hQ0
  · exact Hcog_mono_h h1 h2 u q hHInc hU0 hU1 hQ0 hQ1

/-- H5 proposition schema. -/
def H5Prop
    (fA fB fC : Real → Real)
    (k A B H : Real) (alphaA betaB betaH : Nat) : Prop :=
  ∀ tauD0 tauD1 tauEff0 tauEff1,
    0 ≤ tauD1 → tauD1 ≤ tauD0 → 0 < tauEff0 → tauEff0 ≤ tauEff1 →
    let r0 := ratio tauD0 tauEff0
    let r1 := ratio tauD1 tauEff1
    r1 ≤ r0 ∧
      fA r1 ≤ fA r0 ∧
      fB r1 ≤ fB r0 ∧
      fC r1 ≤ fC r0 ∧
      M0Thresh k (A * fA r1) H alphaA betaH ≤ M0Thresh k (A * fA r0) H alphaA betaH ∧
      MmaxThresh k (B * fB r1) H betaB betaH ≤ MmaxThresh k (B * fB r0) H betaB betaH

/-- H6 proposition schema. -/
def H6Prop (lambdaTau : Real) : Prop :=
  ∀ u tau, u ∈ Set.Icc 0 1 → 0 ≤ tau →
    tauEff lambdaTau u tau ∈ Set.Icc ((1 - lambdaTau) * tau) tau

/-- H7 proposition schema with worst-case skill guarantee. -/
def H7Prop : Prop :=
  ∀ h1 h2 q,
    h1 ≤ h2 → h1 ∈ Set.Icc 0 1 → h2 ∈ Set.Icc 0 1 → q ∈ Set.Icc 0 1 →
    (∀ u, u ∈ Set.Icc 0 1 → Hcog h1 u q ≤ Hcog h2 u q) ∧
    (∀ u, u ∈ Set.Icc 0 1 → h1 ≤ Hcog h1 u q ∧ h2 ≤ Hcog h2 u q) ∧
    (∃ u, u ∈ Set.Icc 0 1 ∧ Hcog h1 u q = h1 ∧ Hcog h2 u q = h2)

/-- T5.3-5: formalised H5, H6, H7 propositions under explicit assumptions. -/
theorem «T5.3-5»
    (fA fB fC : Real → Real)
    (k A B H lambdaTau : Real)
    (alphaA betaB betaH : Nat)
    (hMonA : Monotone fA) (hMonB : Monotone fB) (hMonC : Monotone fC)
    (hFANonneg : ∀ r, 0 ≤ fA r)
    (hFBNonneg : ∀ r, 0 ≤ fB r)
    (_hSatA : ∀ r, 1 ≤ r → fA r = 1)
    (_hSatB : ∀ r, 1 ≤ r → fB r = 1)
    (_hSatC : ∀ r, 1 ≤ r → fC r = 1)
    (hK : 0 ≤ k) (hA : 0 ≤ A) (hB : 0 ≤ B) (hH : 0 ≤ H)
    (hLambda0 : 0 ≤ lambdaTau) (hLambda1 : lambdaTau ≤ 1) :
    H5Prop fA fB fC k A B H alphaA betaB betaH ∧
      H6Prop lambdaTau ∧
      H7Prop := by
  refine ⟨?hH5, ?hH6, ?hH7⟩
  · intro tauD0 tauD1 tauEff0 tauEff1 hTauD1Nonneg hTauDDecrease hTauEff0Pos hTauEffIncrease
    dsimp
    have hR : ratio tauD1 tauEff1 ≤ ratio tauD0 tauEff0 :=
      ratio_nonincrease tauD0 tauD1 tauEff0 tauEff1 hTauD1Nonneg hTauDDecrease hTauEff0Pos hTauEffIncrease
    have hFA : fA (ratio tauD1 tauEff1) ≤ fA (ratio tauD0 tauEff0) := hMonA hR
    have hFB : fB (ratio tauD1 tauEff1) ≤ fB (ratio tauD0 tauEff0) := hMonB hR
    have hFC : fC (ratio tauD1 tauEff1) ≤ fC (ratio tauD0 tauEff0) := hMonC hR
    have hM0 :
        M0Thresh k (A * fA (ratio tauD1 tauEff1)) H alphaA betaH
          ≤ M0Thresh k (A * fA (ratio tauD0 tauEff0)) H alphaA betaH := by
      apply M0Thresh_mono_Aeff k (A * fA (ratio tauD1 tauEff1)) (A * fA (ratio tauD0 tauEff0)) H alphaA betaH
      · exact hK
      · exact hH
      · exact mul_nonneg hA (hFANonneg _)
      · exact mul_le_mul_of_nonneg_left hFA hA
    have hMmax :
        MmaxThresh k (B * fB (ratio tauD1 tauEff1)) H betaB betaH
          ≤ MmaxThresh k (B * fB (ratio tauD0 tauEff0)) H betaB betaH := by
      apply MmaxThresh_mono_Beff k (B * fB (ratio tauD1 tauEff1)) (B * fB (ratio tauD0 tauEff0)) H betaB betaH
      · exact hK
      · exact hH
      · exact mul_nonneg hB (hFBNonneg _)
      · exact mul_le_mul_of_nonneg_left hFB hB
    exact ⟨hR, hFA, hFB, hFC, hM0, hMmax⟩
  · intro u tau hU hTau0
    exact ⟨(tauEff_interval lambdaTau u tau hLambda0 hLambda1 hU.1 hU.2 hTau0).1,
      (tauEff_interval lambdaTau u tau hLambda0 hLambda1 hU.1 hU.2 hTau0).2⟩
  · intro h1 h2 q hHInc hH1 hH2 hQ
    refine ⟨?hMono, ?hLower, ?hWitness⟩
    · intro u hU
      exact Hcog_mono_h h1 h2 u q hHInc hU.1 hU.2 hQ.1 hQ.2
    · intro u hU
      refine ⟨?hL1, ?hL2⟩
      · exact Hcog_lower_bound h1 u q hH1.1 hH1.2 hU.1 hQ.1
      · exact Hcog_lower_bound h2 u q hH2.1 hH2.2 hU.1 hQ.1
    · refine ⟨0, ⟨by norm_num, by norm_num⟩, ?_, ?_⟩
      · unfold Hcog
        ring
      · unfold Hcog
        ring

end

end Section5_3
