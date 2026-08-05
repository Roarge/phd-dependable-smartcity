import Mathlib

namespace Section5_5

noncomputable section

open scoped BigOperators

set_option linter.unusedSectionVars false

/-- PHAS-EAI sign channel: `s = g(η) + ω`. -/
def sensorySignal (g : Real → Real) (eta omega : Real) : Real :=
  g eta + omega

/-- PHAS-EAI peer input channel: `c_in = g(ψ) + ω`. -/
def peerInput (g : Real → Real) (psi omega : Real) : Real :=
  g psi + omega

/-- Accuracy-minus-complexity objective used for action ranking. -/
def accuracyObjective (accuracy complexityCost : Real) : Real :=
  accuracy - complexityCost

/-- Shared expectation update for one peer: `Φ = γ f(ψ) + (1-γ) μ`. -/
def sharedExpectation (mu peerSignal gamma : Real) : Real :=
  gamma * peerSignal + (1 - gamma) * mu

/-- Multi-peer extension with per-peer authority and attention weights `γ_i`. -/
def multiSharedExpectation {n : Nat}
    (mu : Real) (peerSignals gammaVec : Fin n → Real) : Real :=
  (1 / (n : Real)) * ∑ i, sharedExpectation mu (peerSignals i) (gammaVec i)

/-- Gaussian conjugate posterior variance for scalar linear channel with noise variance `σ²`. -/
def posteriorVariance (priorVar noiseVar : Real) : Real :=
  (priorVar * noiseVar) / (priorVar + noiseVar)

/-- Affordance-augmented free-energy form: `F = Divergence - ln p(a)`. -/
def freeEnergyWithAffordance (divergence affordanceProb : Real) : Real :=
  divergence - Real.log affordanceProb

/-- Expected Gaussian log-likelihood term used as an accuracy proxy. -/
def expectedGaussianLogLikelihood (sigmaSq : Real) : Real :=
  -((Real.log (2 * Real.pi * sigmaSq) + 1) / 2)

/-- Closed-form derivative with respect to noise variance `σ²`. -/
def expectedGaussianLogLikelihoodDerivative (sigmaSq : Real) : Real :=
  -(1 / (2 * sigmaSq))

/-- Coordination-friction proxy induced by expectation divergence between two agents. -/
def coordinationFriction (mu peerSignal gammaA gammaB : Real) : Real :=
  |sharedExpectation mu peerSignal gammaA - sharedExpectation mu peerSignal gammaB|

lemma sharedExpectation_diff (mu peerSignal gammaA gammaB : Real) :
    sharedExpectation mu peerSignal gammaA - sharedExpectation mu peerSignal gammaB =
      (gammaA - gammaB) * (peerSignal - mu) := by
  unfold sharedExpectation
  ring

lemma sharedExpectation_as_mu (mu peerSignal gamma : Real) :
    sharedExpectation mu peerSignal gamma = mu + gamma * (peerSignal - mu) := by
  unfold sharedExpectation
  ring

lemma sharedExpectation_as_peer (mu peerSignal gamma : Real) :
    sharedExpectation mu peerSignal gamma = peerSignal + (1 - gamma) * (mu - peerSignal) := by
  unfold sharedExpectation
  ring

lemma coordinationFriction_factorised (mu peerSignal gammaA gammaB : Real) :
    coordinationFriction mu peerSignal gammaA gammaB =
      |gammaA - gammaB| * |peerSignal - mu| := by
  unfold coordinationFriction
  rw [sharedExpectation_diff, abs_mul]

/-- T5.5-1: non-degenerate noise implies non-zero posterior uncertainty unless prior is degenerate. -/
theorem «T5.5-1» (priorVar noiseVar : Real)
    (hNoise : 0 < noiseVar) :
    (0 < priorVar → 0 < posteriorVariance priorVar noiseVar) ∧
      (priorVar = 0 → posteriorVariance priorVar noiseVar = 0) := by
  constructor
  · intro hPrior
    unfold posteriorVariance
    apply div_pos
    · exact mul_pos hPrior hNoise
    · linarith
  · intro hPriorZero
    unfold posteriorVariance
    simp [hPriorZero]

/-- T5.5-2: shared expectations are convex mixtures, and multi-peer form is a weighted sum of such terms. -/
theorem «T5.5-2» (mu peerSignal gamma : Real)
    (hGamma0 : 0 ≤ gamma) (hGamma1 : gamma ≤ 1) :
    sharedExpectation mu peerSignal gamma ∈ Set.Icc (min mu peerSignal) (max mu peerSignal) ∧
      (∀ {n : Nat} (peerSignals gammaVec : Fin n → Real),
        multiSharedExpectation mu peerSignals gammaVec =
          (1 / (n : Real)) * ∑ i, sharedExpectation mu (peerSignals i) (gammaVec i)) := by
  constructor
  · cases le_total mu peerSignal with
    | inl hMuLePeer =>
      have hDeltaNonneg : 0 ≤ peerSignal - mu := by linarith
      have hScaledNonneg : 0 ≤ gamma * (peerSignal - mu) := by
        exact mul_nonneg hGamma0 hDeltaNonneg
      have hScaledLe : gamma * (peerSignal - mu) ≤ (peerSignal - mu) := by
        have hTmp : gamma * (peerSignal - mu) ≤ 1 * (peerSignal - mu) :=
          mul_le_mul_of_nonneg_right hGamma1 hDeltaNonneg
        simpa using hTmp
      have hLower : mu ≤ sharedExpectation mu peerSignal gamma := by
        rw [sharedExpectation_as_mu]
        linarith
      have hUpper : sharedExpectation mu peerSignal gamma ≤ peerSignal := by
        rw [sharedExpectation_as_mu]
        linarith
      simpa [min_eq_left hMuLePeer, max_eq_right hMuLePeer] using And.intro hLower hUpper
    | inr hPeerLeMu =>
      have hDeltaNonneg : 0 ≤ mu - peerSignal := by linarith
      have hOneGammaNonneg : 0 ≤ 1 - gamma := by linarith
      have hScaledNonneg : 0 ≤ (1 - gamma) * (mu - peerSignal) := by
        exact mul_nonneg hOneGammaNonneg hDeltaNonneg
      have hScaledLe : (1 - gamma) * (mu - peerSignal) ≤ (mu - peerSignal) := by
        have hTmp : (1 - gamma) * (mu - peerSignal) ≤ 1 * (mu - peerSignal) :=
          mul_le_mul_of_nonneg_right (by linarith) hDeltaNonneg
        simpa using hTmp
      have hLower : peerSignal ≤ sharedExpectation mu peerSignal gamma := by
        rw [sharedExpectation_as_peer]
        linarith
      have hUpper : sharedExpectation mu peerSignal gamma ≤ mu := by
        rw [sharedExpectation_as_peer]
        linarith
      simpa [min_eq_right hPeerLeMu, max_eq_left hPeerLeMu] using And.intro hLower hUpper
  · intro n peerSignals gammaVec
    rfl

/-- T5.5-3: increasing affordance probability lowers free energy and favours the action under argmin. -/
theorem «T5.5-3» (divergence p1 p2 : Real)
    (hP1 : 0 < p1) (hPInc : p1 < p2) :
    freeEnergyWithAffordance divergence p2 < freeEnergyWithAffordance divergence p1 := by
  unfold freeEnergyWithAffordance
  have hLog : Real.log p1 < Real.log p2 := Real.log_lt_log hP1 hPInc
  linarith

/-- T5.5-4: higher precision (lower noise variance) improves expected Gaussian log-likelihood. -/
theorem «T5.5-4» (sigmaSq1 sigmaSq2 : Real)
    (hSigma1 : 0 < sigmaSq1) (hSigma2 : 0 < sigmaSq2)
    (hOrder : sigmaSq1 ≤ sigmaSq2) :
    expectedGaussianLogLikelihoodDerivative sigmaSq1 < 0 ∧
      expectedGaussianLogLikelihoodDerivative sigmaSq2 < 0 ∧
      expectedGaussianLogLikelihood sigmaSq2 ≤ expectedGaussianLogLikelihood sigmaSq1 := by
  have hDeriv1 : expectedGaussianLogLikelihoodDerivative sigmaSq1 < 0 := by
    unfold expectedGaussianLogLikelihoodDerivative
    have hFracPos : 0 < 1 / (2 * sigmaSq1) := by positivity
    linarith
  have hDeriv2 : expectedGaussianLogLikelihoodDerivative sigmaSq2 < 0 := by
    unfold expectedGaussianLogLikelihoodDerivative
    have hFracPos : 0 < 1 / (2 * sigmaSq2) := by positivity
    linarith
  have hScaleNonneg : 0 ≤ 2 * Real.pi := by positivity
  have hArgOrder : (2 * Real.pi) * sigmaSq1 ≤ (2 * Real.pi) * sigmaSq2 :=
    mul_le_mul_of_nonneg_left hOrder hScaleNonneg
  have hArgPos1 : 0 < (2 * Real.pi) * sigmaSq1 := by positivity
  have hLog :
      Real.log ((2 * Real.pi) * sigmaSq1) ≤ Real.log ((2 * Real.pi) * sigmaSq2) :=
    Real.log_le_log hArgPos1 hArgOrder
  have hAcc : expectedGaussianLogLikelihood sigmaSq2 ≤ expectedGaussianLogLikelihood sigmaSq1 := by
    unfold expectedGaussianLogLikelihood
    linarith
  exact ⟨hDeriv1, hDeriv2, hAcc⟩

/-- T5.5-5: authority-weight asymmetry yields expectation divergence and increasing coordination friction. -/
theorem «T5.5-5»
    (mu peerSignal gammaA gammaB gammaA' gammaB' : Real)
    (hGammaNe : gammaA ≠ gammaB)
    (hPeerNe : peerSignal ≠ mu)
    (hAsym : |gammaA - gammaB| ≤ |gammaA' - gammaB'|) :
    sharedExpectation mu peerSignal gammaA ≠ sharedExpectation mu peerSignal gammaB ∧
      0 < coordinationFriction mu peerSignal gammaA gammaB ∧
      coordinationFriction mu peerSignal gammaA gammaB
        ≤ coordinationFriction mu peerSignal gammaA' gammaB' := by
  have hProdNe : (gammaA - gammaB) * (peerSignal - mu) ≠ 0 := by
    apply mul_ne_zero
    · exact sub_ne_zero.mpr hGammaNe
    · exact sub_ne_zero.mpr hPeerNe
  have hExpectNe :
      sharedExpectation mu peerSignal gammaA ≠ sharedExpectation mu peerSignal gammaB := by
    intro hEq
    have hZero :
        sharedExpectation mu peerSignal gammaA - sharedExpectation mu peerSignal gammaB = 0 := by
      exact sub_eq_zero.mpr hEq
    rw [sharedExpectation_diff] at hZero
    exact hProdNe hZero
  have hFrictionPos : 0 < coordinationFriction mu peerSignal gammaA gammaB := by
    unfold coordinationFriction
    rw [sharedExpectation_diff]
    exact abs_pos.mpr hProdNe
  have hFrictionLe :
      coordinationFriction mu peerSignal gammaA gammaB
        ≤ coordinationFriction mu peerSignal gammaA' gammaB' := by
    rw [coordinationFriction_factorised, coordinationFriction_factorised]
    have hPeerAbsNonneg : 0 ≤ |peerSignal - mu| := abs_nonneg _
    exact mul_le_mul_of_nonneg_right hAsym hPeerAbsNonneg
  exact ⟨hExpectNe, hFrictionPos, hFrictionLe⟩

end

end Section5_5
