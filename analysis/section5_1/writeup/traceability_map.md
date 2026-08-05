# Traceability Map

| Formal element | Lean identifier | Thesis source mapping |
|---|---|---|
| Configuration product space `X = ∏ X_i` | `ComplexityModel.feasibleDistinctSet` domain argument `Xspace` with finite factors | `Analytical Models/Complexity-in-PHAS.md` Eq. (15), Eq. (15a) |
| Constraints `K` and feasibility pruning | `ComplexityModel.feasibleDistinctSet` filter by `K` | `Analytical Models/Complexity-in-PHAS.md` Hard Constraints section |
| Distinctness by binning and quotient | `ComplexityModel.binEq`, `ComplexityModel.feasibleDistinctSet` image under `b` | `Analytical Models/Complexity-in-PHAS.md` Eq. (15b), Eq. (15c), Eq. (15d) |
| Complexity as total optionality `C = |S^δ|` | `ComplexityModel.complexity` | `Analytical Models/Complexity-in-PHAS.md` Eq. (16) |
| Success set and success share | `ComplexityModel.successSet`, `ComplexityModel.successShare` | `Analytical Models/Functional-Information-and-Cost-of-Choice-in-PHAS.md` Eq. (29), Eq. (30) |
| Functional information `I_g = -log2(rho)` | `ComplexityModel.functionalInformation` | `Analytical Models/Functional-Information-and-Cost-of-Choice-in-PHAS.md` Eq. (31) |
| Time-conditioning and mobilisation | `ComplexityModel.mobilisationFraction`, `ComplexityModel.effectiveSuccessCount` | `Analytical Models/Model-of-Resiliency-in-PHAS.md` Eq. (24), Eq. (25), Eq. (26), and Eq. (32) |
| Operational functional information `I_g^{op}` | `ComplexityModel.operationalFunctionalInformation`, `ComplexityModel.operationalFunctionalInformationFromShare` | `Analytical Models/Functional-Information-and-Cost-of-Choice-in-PHAS.md` Eq. (33) |
| A1 Monotonicity under expansion | `ComplexityBursts.A1` | Complexity sanity check direction-of-change statement |
| A2 Monotonicity under tightening | `ComplexityBursts.A2` | Complexity sanity check direction-of-change statement |
| A3 Multiplicative composition | `ComplexityBursts.A3` | Composition property paragraph |
| A4 Event jump in complexity bits | `ComplexityBursts.A4` | Discrete event interpretation of composition in Chapter 5.1 |
| B1 Selection pressure monotonicity | `ComplexityBursts.B1` | Operational difficulty term in Eq. (33) and time-conditioning Eq. (24)-(26) |
| B2 Closed-form jump in `I_g^{op}` | `ComplexityBursts.B2` | Direct consequence of Eq. (33) expressed with success-share ratio |
| B3 Discrete-event burst in `I_g^{op}` | `ComplexityBursts.B3` | Governance and boundary event interpretation for Chapter 5.1.2 |
| C1 Differential expression for interventions | `ComplexityBursts.C1` | Eq. (33) decomposition by total versus useful effective options |
| C2 Joint intervention additivity | `ComplexityBursts.C2` | Operational information reduction interpretation in final paragraph of functional information model |
