# Building Smarter Environments for Small Teams

## A Model-Based Approach to Dependable Smart City Infrastructure in Very Small Entities

Doctoral thesis | Roar Elias Georgsen | University of South-Eastern Norway (USN) | 2026

---

## Abstract

The thesis investigates how Very Small Entities (VSEs), organisations with fewer than 25 employees, can deliver dependable smart city infrastructure despite severe constraints in capacity, tooling, and expertise. VSEs constitute over 92% of European enterprises and dominate the infrastructure supply chain, yet they are structurally mismatched with the security, reliability, and integration demands of modern cyber-physical systems.

The work develops a formal model of complexity and resilience, defining complexity as feasible distinct optionality and resilience as mobilisable variety under time pressure. An extended Purposeful Human Activity Systems (PHAS) model integrates the Free-Energy Principle from computational biology, introducing two constructs: *Regimes of Attention*, which channel collective focus towards critical signals, and *Patterned Practices*, which sustain engagement through regular, structured interaction. Fourteen testable hypotheses and a leverage points framework for intervention design are derived from the formal analysis.

Four industrial case studies conducted over six years with a Norwegian VSE evaluate complementary digital engineering interventions: model-based reliability and security validation, gamified threat modelling, LLM-assisted requirements review, and environmentally designed cybersecurity practices. Cross-case analysis finds convergent support for four claims: designed cognitive reserve outperforms experience investment, modelling patterns reduce decision burden without reducing resilience, machine-readable traceability reduces cross-boundary noise, and environmental salience sustains improvement more effectively than compliance mandates.

**Keywords:** Very Small Entities, smart city, digital engineering, model-based engineering, resilience, systems security, Free-Energy Principle, active inference, Purposeful Human Activity Systems

---

## Repository Contents

The full dissertation is available as
[Georgsen dissertation 060326.pdf](Georgsen%20dissertation%20060326.pdf).
This repository also contains the reproducible analysis and simulation
artefacts.

### Analysis (`analysis/`)

Seven self-contained sections correspond to Chapter 5 of the thesis. Each
section folder follows the same structure:

| Subfolder | Contents |
| --- | --- |
| `setup/lean/` or `setup/proofs/` | Lean 4 formal proofs |
| `setup/scripts/` | Python scripts that generate figures and tables |
| `result/` | Generated figures (PDF/PNG), tables (CSV/TeX), and manifests |
| `writeup/` | Proof narrative and traceability maps |

**Sections:**

| Section | Topic |
| --- | --- |
| `section5_1/` | Complexity as feasible distinct optionality (multiplicative composition, burst dynamics) |
| `section5_2/` | Resilience advantage under designed cognitive reserve |
| `section5_3/` | Response time drag and mobilisation insets |
| `section5_4/` | Operational functional information under time pressure |
| `section5_5/` | PHAS-EAI assurance loop (precision and accuracy) |
| `section5_6/` | Experience effects and sensitivity decay |
| `section5_7/` | Joint intervention analysis (patterns as operators) |

Runner scripts at the top level execute one or all sections:

```bash
./analysis/run_all.sh            # all sections
./analysis/run_section5_3.sh     # single section
```

### Simulation (`simulation/`)

Agent-based models built on the active inference framework from Kaufmann et
al. (2021), extended with five PHAS-EAI constructs.

| Folder | Contents |
| --- | --- |
| `kaufmann/` | Baseline reproduction of Kaufmann et al. (2021) collective intelligence model (read-only reference) |
| `phas_eai/core/` | Extended agent, environment, and simulation modules |
| `phas_eai/experiments/` | Experiment scripts (one per extension plus combinations) |
| `phas_eai/plotting/` | Visualisation functions |
| `phas_eai/results/` | Generated figures organised by experiment |

**Extensions (cumulative):**

| Extension | Construct | Hypothesis |
| --- | --- | --- |
| 1 | Designed cognitive reserve (*h*) | H3 |
| 2 | Regimes of Attention (niche construction) | H5 |
| 3 | Dynamic shared expectations (*Phi*) | H7 |
| 4 | Patterned Practices (periodic synchronisation) | H9 |
| 5 | Disturbance episodes (resilience testing) | H11 |

```bash
cd simulation
source .venv/bin/activate
python kaufmann/run_simulation.py --quick          # baseline
python -m phas_eai.experiments.run_extension1 --quick  # single extension
./run_all_full.sh                                  # all experiments
```

## Thesis Context

The thesis is article-based. Papers I through V are included as appendices
in the submitted thesis. Four industrial case studies were conducted with a
Norwegian VSE (Aiwell AS):

- **Case A**: SysML-based reliability and security validation
- **Case B**: Gamified threat modelling
- **Case C**: LLM-assisted requirements review
- **Case D**: Environmentally designed cybersecurity practices (PHAS-EAI)

## Toolchain

- **Lean 4.27.0** for formal proofs (one per analysis section)
- **Python 3.12** for analysis scripts and agent-based simulation
- Deterministic execution: fixed random seeds, `PYTHONHASHSEED=0`

## Case Company

[Aiwell AS](https://aiwell.no) — Norwegian VSE operating smart building infrastructure.

---

*Submitted in partial fulfilment of the requirements for the degree of Philosophiae Doctor (PhD) at the University of South-Eastern Norway.*
