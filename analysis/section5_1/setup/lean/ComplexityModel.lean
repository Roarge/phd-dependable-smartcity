import Mathlib

open scoped BigOperators

namespace ComplexityModel

noncomputable section

/-! ## Core definitions aligned with Equations (15)-(20), (40)-(44) -/

/-- Base-2 logarithm used for information measures (bits). -/
def log2 (x : Real) : Real := Real.log x / Real.log 2

/-- Distinctness relation induced by the binning map `b : X -> B` (Eq. 18). -/
def binEq {X B : Type*} (b : X -> B) (x y : X) : Prop := b x = b y

/-- Feasible distinct set `S^δ` as image of feasible configurations under the binning map (Eq. 19). -/
def feasibleDistinctSet {X B : Type*} [DecidableEq X] [DecidableEq B]
    (Xspace : Finset X) (K : X -> Prop) [DecidablePred K] (b : X -> B) : Finset B :=
  (Xspace.filter K).image b

/-- Complexity as total feasible distinct optionality `C = |S^δ|` (Eq. 20). -/
def complexity {X B : Type*} [DecidableEq X] [DecidableEq B]
    (Xspace : Finset X) (K : X -> Prop) [DecidablePred K] (b : X -> B) : Nat :=
  (feasibleDistinctSet Xspace K b).card

/-- Success set `A_{g,p}` for function `g` and threshold `p` (Eq. 40). -/
def successSet {X : Type*} [DecidableEq X]
    (Sdelta : Finset X) (g : X -> Real) (p : Real) : Finset X :=
  Sdelta.filter (fun x => p <= g x)

/-- Success share `rho = |A| / |S|` (Eq. 41 with thesis naming). -/
def successShare (A S : Real) : Real := A / S

/-- Design-time functional information `I_g = -log2(rho)` (Eq. 42). -/
def functionalInformation (rho : Real) : Real := -log2 rho

/-- Time-conditioned mobilisation fraction `f_A(r) = min(1, r^epsilon_A)` (Eq. 35). -/
def mobilisationFraction (tau_d tau_eff epsilonA : Real) : Real :=
  min 1 ((tau_d / tau_eff) ^ epsilonA)

/-- Effective successful option count `A~ = |A| * f_A` (Eq. 43). -/
def effectiveSuccessCount (A fA : Real) : Real := A * fA

/-- Operational success share `rho^op = A_eff / C_eff`. -/
def operationalSuccessShare (Aeff Ceff : Real) : Real := Aeff / Ceff

/-- Operational functional information from share `I_g^op = -log2(rho^op)`. -/
def operationalFunctionalInformationFromShare (rhoOp : Real) : Real :=
  functionalInformation rhoOp

/-- Operational functional information from counts `I_g^op = log2(C_eff) - log2(A_eff)` (Eq. 44 form). -/
def operationalFunctionalInformation (Ceff Aeff : Real) : Real :=
  log2 Ceff - log2 Aeff

/-- Discrete-time event-driven complexity process. Event steps multiply complexity by `k(t)`. -/
def eventDrivenComplexity (C0 : Real) (k : Nat -> Real) (event : Nat -> Prop)
    [DecidablePred event] : Nat -> Real
  | 0 => C0
  | t + 1 =>
      if event t then
        eventDrivenComplexity C0 k event t * k t
      else
        eventDrivenComplexity C0 k event t

/-- Jump predicate for discrete-time trajectories. -/
def JumpAt (f : Nat -> Real) (t : Nat) : Prop := f (t + 1) ≠ f t

lemma log2_mul {x y : Real} (hx : 0 < x) (hy : 0 < y) :
    log2 (x * y) = log2 x + log2 y := by
  unfold log2
  rw [Real.log_mul hx.ne' hy.ne']
  ring

lemma log2_div {x y : Real} (hx : 0 < x) (hy : 0 < y) :
    log2 (x / y) = log2 x - log2 y := by
  unfold log2
  rw [Real.log_div hx.ne' hy.ne']
  ring

lemma log2_jump_bits {Cminus k : Real} (hC : 0 < Cminus) (hk : 0 < k) :
    log2 (Cminus * k) - log2 Cminus = log2 k := by
  rw [log2_mul hC hk]
  ring

lemma operational_information_count_share_equiv {Ceff Aeff : Real}
    (hC : 0 < Ceff) (hA : 0 < Aeff) :
    operationalFunctionalInformation Ceff Aeff =
      operationalFunctionalInformationFromShare (operationalSuccessShare Aeff Ceff) := by
  unfold operationalFunctionalInformation operationalFunctionalInformationFromShare
  unfold operationalSuccessShare functionalInformation
  calc
    log2 Ceff - log2 Aeff = -(log2 Aeff - log2 Ceff) := by ring
    _ = -log2 (Aeff / Ceff) := by rw [<- log2_div hA hC]

end

end ComplexityModel
