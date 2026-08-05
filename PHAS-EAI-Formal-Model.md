---
title: "The PHAS-EAI Formal Model"
subtitle: "A Complete Reference"
---

# The PHAS-EAI Formal Model

This document presents the complete formal model for Purposeful Human Activity Systems with Extended Active Inference (PHAS-EAI). The model provides a unified analytical framework that connects four components:

1. an active inference account of how agents in socio-technical systems perceive, decide, act, and communicate under uncertainty,
2. a complexity model that defines and measures the option space available to such systems,
3. a resilience model that quantifies the ability to mobilise useful responses under time pressure, and
4. a functional information model that measures the difficulty of finding satisfactory configurations.

The intended audience is anyone working with the `analysis/` or `simulation/` folders in this repository who needs to understand what the equations mean, how the model components connect, and what predictions the model generates.

## Sources

The model is published in two places, and this document reproduces both. The primary source is the doctoral dissertation *Building Smarter Environments for Small Teams: A Model-Based Approach to Dependable Smart City Infrastructure in Very Small Entities* by Roar Elias Georgsen (University of South-Eastern Norway, 2026), included in this repository as `Georgsen dissertation 060326.pdf`. The active inference model (Equations 1 to 14) was developed in the journal article "Navigating Uncertainty: Guiding Attention in Purposeful Human Activity Systems" (*Systems Engineering*, 2026, doi 10.1002/sys.70041). The dissertation is article-based, and this article is bundled in the dissertation PDF as the fifth of its five papers. Following the dissertation's convention, this document refers to it as Paper V.

The active inference model is restated in Section 4.2.2 of the dissertation. The complexity, resilience, and functional information models (Equations 15 to 44) are Sections 4.2.3 through 4.2.5 of the dissertation. Equation numbers match the dissertation throughout, and the dissertation numbering coincides with Paper V for Equations 1 to 14. The Foundations part below condenses Chapter 3 of the dissertation and Section 2 of Paper V. The Key Findings part condenses Chapter 5. Tables 2 through 5 in this document correspond to dissertation Tables 12 through 15.

## Repository orientation

The `analysis/` folder contains formal proofs written in Lean 4, computational verification scripts, and the detailed model analysis (hypotheses H1 through H14, theorems, and sensitivity analyses). Each `analysis/section5_*` subfolder covers one major topic, with `setup/lean/` for proofs, `result/` for computed outputs and figures, and `writeup/` for prose.

The `simulation/` folder contains an agent-based implementation of the model. The `simulation/phas_eai/` package implements the PHAS-EAI extensions (designed cognitive reserve, Regimes of Attention, dynamic shared expectations, Patterned Practices, and disturbance episodes). The `simulation/kaufmann/` folder contains a read-only reproduction of the Kaufmann et al. (2021) baseline active inference simulation used for comparison.

This document defines the model that those folders implement and analyse. All 44 equations are presented with full notation, plain-language explanations, and the principles that follow from them.

## Master notation

| Symbol | Meaning |
|--------|---------|
| $s$ | Sensory input (observed signs) |
| $g(\cdot)$ | Observation mapping from external states to the sensed signal (distinct from the function name $g$ in $I_g^{\star}$) |
| $\eta$ | External states of the world |
| $\mu$ | Internal model or beliefs of the agent |
| $a$ | Action |
| $\omega$ | Noise and uncertainty in perception or communication |
| $\psi$ | Peer internal states |
| $c_{\text{in}}$, $c_{\text{out}}$ | Incoming and outgoing communication |
| $F$ | Variational free energy |
| $D[\cdot\|\cdot]$ | Kullback-Leibler divergence between two distributions |
| $q_{\mu}(\eta)$ | Approximate posterior over external states (the active inference literature also calls this the variational density, and the two terms are equivalent) |
| $\mathbb{E}$ | Expectation operator |
| $\Phi$ | Shared norms, conventions, and expectations |
| $\gamma$, $\gamma_i$ | Authority weight(s) for peer influence |
| $\gamma_{\text{det}}, \gamma_{\text{dec}}, \gamma_{\text{exe}}$ | Stage-specific sensitivity vectors for structural drag (unrelated to the authority weights) |
| $X_i$ | Set of alternatives for configuration-space factor $i$ |
| $K$ | Hard constraint set |
| $\Delta$ | Decision resolution (smallest meaningful difference) |
| $\varphi$ | Binning map for collapsing near-duplicates |
| $\mathcal{O}^{\Delta}$ | Feasible set of distinct options at resolution $\Delta$ |
| $C$ | Complexity (= $\lvert\mathcal{O}^{\Delta}\rvert$, the count of distinct feasible options) |
| $CP_i$ | Per-factor complexity potential for factor $i$ |
| $A_d$, $B_d$ | Useful variety and survivable variety under disturbance $d$ |
| $H$ | Total headroom ($H_{\text{phys}} \times H_{\text{cog}}$) |
| $h$ | Designed cognitive reserve (minimum cognitive floor) |
| $u(E, MF)$ | Normalised skill factor from experience $E$ and mental flexibility $MF$ |
| $\tau$ | Response time |
| $\tau_{\text{eff}}$ | Effective mobilisation time |
| $\tau_d$ | Disturbance timescale |
| $r$ | Time allowance ratio ($\tau_d / \tau_{\text{eff}}$) |
| $f_A, f_B, f_C$ | Response functions (mobilisation fractions) |
| $\sigma_{\tau}$ | Skill-based time multiplier |
| $M_0$, $M_{\max}$ | No-penalty and collapse magnitude limits |
| $R$ | Resilience score (0 to 1) |
| $I_g^{\star}(\rho)$ | Design-time functional information for function $g$ at threshold $\rho$ |
| $I_g^{\text{op}}$ | Operational functional information (under time pressure) |
| $S$ | Surprise, $-\ln p(x \mid \mu)$ |
| $IT$ | Interaction type (task demand rating, 1 to 10) |
| $E$, $MF$ | Experience and mental flexibility ratings (1 to 5) |
| $q(IT)$ | Task-demand function, in $[0,1]$ (unrelated to the approximate posterior $q_{\mu}$) |
| $\lambda_{\tau}$ | Maximum fractional time reduction attributable to skill |
| $\varepsilon_A, \varepsilon_B, \varepsilon_C$ | Mobilisation elasticities for useful, survivable, and total options |
| $k$, $\alpha$, $\beta$ | Scale constant and elasticities in the magnitude limits (Equation 38) |
| $M$, $M_d$ | Disturbance magnitude |
| $1/\sigma^2$ | Precision of a noisy channel (inverse of the noise variance) |

Three typographic notes prevent confusion later. The double-struck $\mathbb{E}$ is the expectation operator and is distinct from the italic $E$, which denotes experience. Square brackets in a range include the endpoint and round brackets exclude it: $h \in (0,1]$ means $h$ is greater than zero and at most one, and $\lambda_{\tau} \in [0,1)$ means $\lambda_{\tau}$ is at least zero and strictly below one, with the symbol $\in$ itself reading "lies in". A centred dot inside brackets, as in $p(\cdot)$, is a placeholder marking where the function's argument goes.

---

# Part I: Active Inference Model of PHAS

## 1 Foundations

### 1.1 Systems, boundaries, and the Markov blanket

A system is a thing that exhibits organised persistence over time, understood as constrained patterns of state and state transition. It can be treated as a coherent object of analysis because interactions with its environment are mediated by a boundary. In engineering contexts, the system definition also includes purpose and accountability, because these determine what counts as feasible action under stress.

A boundary is the subset of states, interfaces, and constraints that mediates exchange between system and environment. Boundary choice constrains what can be observed and influenced at the chosen level of description, and therefore constrains what can be predicted, assured, and governed.

In statistical physics, a system's identity is determined by its ability to maintain a consistent set of internal states and state transitions despite external influences. Statistically, this separation means that internal and external states are conditionally independent: once the states of the boundary are known, the outside world provides no further information about the inside. The minimal structure necessary to maintain such conditional independence is a Markov blanket. A Markov blanket creates a separation between internal (systemic) and external (environmental) states. Input states receive information from the external environment, and internal states receive information only from input states, not directly from external states. Active states represent the system's influence on the environment, driven by its internal goals, preferences, and biases. Through this interplay, external conditions provide necessary input but do not directly influence the system's internal states.

The Markov blanket demonstrates that internal and external states are "hidden" from each other. No system can ever directly observe the world beyond its own boundaries, and this boundary mediates all knowledge about the external world. The causes of sensations cannot be directly accessed, nor is there a one-to-one correspondence between specific causes and the sensations they produce. Solving such ill-posed inference problems requires relying on prior beliefs or experiences to navigate ambiguity and uncertainty, which is why a strategy such as variational inference is required.

### 1.2 Scientific systems principles

Three general systems principles provide the scientific foundation for the formal model.

The **principle of conservation of properties (SP1)** holds that emergent properties in system formation are balanced by the submergence of properties in the parts. The capacity gained at the system level is paid for by capacity lost at the component level.

The **principle of universal interdependence (SP2)** holds that system properties reflect a balance between bottom-up emergence from parts and outside-in submergence from the supersystemic context, so that neither internal structure nor external environment alone determines system behaviour.

The **principle of complexity dominance (SP3)** holds that in interactions between subsystems of unequal complexity, the simpler subsystem undergoes proportionally greater submergence, meaning that complex systems buffer their autonomy more effectively than simple ones. A direct corollary is Ashby's (1956) law of requisite variety: effective regulation requires internal diversity at least equal to the diversity of disturbances. SP3 and Ashby's corollary together establish that a small engineering team confronting a complex cyber-physical system-of-systems is, by structural necessity, the simpler partner in the interaction. The autonomy cost falls disproportionately on the team, not because it lacks skill but because the variety asymmetry is built into the relationship.

### 1.3 Loans of intelligence and the intentional stance

A *loan of intelligence* is the provisional use of assumptions in scientific models. These assumptions allow scientists to proceed by treating certain structures or relationships as functionally coherent, even when the details are not fully understood or justified. Referring to "command" and "control" in an engineering context, for instance, presumes a sender, a receiver, and a reliable process for interpreting and executing instructions. This is a loan of intelligence: a practical tool that makes a complex system tractable, not a claim about the underlying mechanisms.

The intentional stance is the most powerful and most common loan of intelligence. It is a pragmatic strategy for predicting and explaining the behaviour of complex systems by treating any system, whether human, animal, or machine, as if it were a rational agent with beliefs and desires. A system qualifies as an intentional system only if this approach leads to accurate and useful predictions. The intentional stance does not require the system to possess subjective mental states. It is a methodological tool, not a claim about internal experience.

All assumptions in the model that follows are provisional, and three caveats govern how the formalism should be read. First, the generative model is not something internal to the components of a PHAS. It is a mathematical construct that describes an observable phenomenon. Second, intentional systems can be wrong. They act rationally in the context of their own beliefs, and those beliefs may be false, so "choosing" and "optimising" in the model denote local optima in a specific context. Third, a sentient engineer and the layout of a workshop can be described using the same formalism, but this does not confer sentience on the environment, nor does it entail any form of group consciousness. Some models are more useful than others, but even the most precise and predictive models remain wrong.

### 1.4 The extended mind and the cognitive niche

The extended mind thesis asserts that cognitive processes can be "uploaded" to the external environment, expanding the cognitive system beyond the agent's internal states. The implication is that the cognitive unit is not confined to the individual, but extends into the environment and across individuals.

When knowledge is uploaded to the external environment, it becomes part of a shared system that multiple agents and technical systems can access, refine, and build upon. In engineering workplaces, automated workflow and process documentation represent uploaded knowledge. These systems store the detailed steps of complex processes, allowing them to be followed and improved over time. This knowledge is distributed across individuals and systems that understand how to interpret, use, and modify these processes.

In biology, niche construction refers to how individuals actively shape their surroundings to enhance their abilities. The cognitive niche expands on this by treating the environment as a space where agents create and maintain cause-effect models to guide their actions. Consider a shared workspace where employees gradually develop efficient shortcuts for accessing frequently used tools or resources. Over time, as more people adopt a particular shortcut, it becomes established and reliable, signalling to others that this is the most effective way to accomplish a task. The cognitive niche thus becomes a collective memory and problem-solving resource, enabling agents to perform cognitive tasks that would be impossible without the integration and collaboration of multiple minds and tools.

### 1.5 Purposeful Human Activity Systems

A purposeful human activity system (PHAS) is a socio-technical system grounded in people and their behaviour. These systems use highly specialised technical knowledge to design, model, and realise complex solution systems. The term refers specifically to engineered systems whose performance and effectiveness depend significantly on the integrated interactions between their social (human, organisational) and technical elements.

The PHAS model focuses on four core elements, subsequently expanded to five with the addition of Worldview:

- **System:** PHAS consist of conceptual and concrete parts. These parts interrelate to create persistent structures, processes, and meanings.
- **Purpose:** PHAS are designed to fulfil specific purposes. They possess inherent causal powers to achieve these purposes, are designed to align with their objectives, and are aware of and intentionally pursue their goals.
- **Boundary:** PHAS interact with their environment through their boundary. This boundary allows the system to both submerge into and influence its environment.
- **Relationships:** The nature and strength of the relationships between parts, purpose, and boundary depend on the context and are influenced by the language used.
- **Worldview:** PHAS are intentional systems with a worldview. Adding worldview as a first-class component reflects the formal model's treatment of PHAS as intentional systems whose behaviour is driven by beliefs, shared expectations, and cultural norms.

![PHAS model expanded to include worldview as a fifth component.](<Analytical Models/figures/figure-8-phas-with-worldview.png>)

Table 1 lists the PHAS principles, including the worldview principles derived from the formal model.

**Table 1. PHAS principles and sub-principles.**

| Component | Principle |
|-----------|-----------|
| System | 1. PHAS have parts: (a) parts are conceptual and concrete, (b) parts interrelate to produce persistent structures, processes, behaviours, and meanings, (c) interrelations are conditioned by kind, capability, and structure. |
| Purpose | 2. PHAS exist to fulfil a purpose: (a) possess inherent causal powers to fulfil purpose, (b) design is commensurate with purpose, (c) are aware of and intentionally pursue their purposes. |
| Boundary | 3. PHAS mediate interactions through boundary: (a) system submerges to its environment, (b) system influences its environment. |
| Relationships | 4. Context and language modulate relationships: (a) magnitude and kind vary according to context, (b) magnitude and kind are conditioned by the language used. |
| Worldview | 5. PHAS are intentional systems with a worldview: (5.1) perceive environment through noisy, mediated inputs, (5.2) maintain and optimise a generative model to minimise uncertainty, (5.3) shape environment through action, (5.4) the intentional stance applies both by and to them, (5.5) operate within a multi-scale hierarchy preserving free energy across scales. |

Free energy, the generative model, and the worldview sub-principles are defined formally in sections 1.6 through 6 below. Sub-principle 5.1 corresponds to Equation (2), 5.2 to Equations (3) and (4), 5.3 to Equations (5) through (8), 5.4 to Equations (9) through (12) and (14), and 5.5 to Equation (13).

### 1.6 The Free-Energy Principle and active inference

The Free-Energy Principle (FEP), as articulated by Karl Friston, is a theoretical framework that unifies various aspects of biology under the single concept of minimising variational free energy. Rooted in earlier ideas in thermodynamics and Helmholtz's notion of unconscious inference, FEP posits that biological systems maintain their low-entropy, organised states by reducing the discrepancy between predicted and actual sensory inputs, thereby minimising surprise and uncertainty about their environment. Reducing uncertainty involves minimising variational free energy, which pushes the system to explain or predict its sensations more accurately. This process is typically modelled as active inference, a widely used mathematical model of updating beliefs in perception and learning.

In active inference, the agent relies on an internal probabilistic generative model to represent a mapping between unobserved causes and observed effects, reflecting the agent's predictive and causal understanding of the world. FEP is highly generalisable and has demonstrated strong predictive power across perception, attention, learning, emotions, action, cultural processes, niche construction, and natural selection.

The formal model presented below applies the FEP to purposeful human activity systems. Each equation represents an aspect of PHAS or their environment, and key properties that follow from the formal description are proposed as new PHAS principles.

## 2 The generative model and perception

### 2.1 Generative model

A generative model is typically expressed in terms of a likelihood and a prior term:

$$p(s,\eta) = p(s \mid \eta)\,p(\eta) \tag{1}$$

In Equation (1), $p(\cdot)$ denotes probability, $s$ denotes observed signs, and $\eta$ denotes external world states. The left side $p(s,\eta)$ is the joint probability of signs and states. The term $p(s \mid \eta)$ is the likelihood: the probability of experiencing certain sensations $s$ (such as "sour" or "sweet") if the world is in a given state $\eta$ (such as "eating lemon" or "eating honey"). The term $p(\eta)$ is the prior over states: what the agent believes about the state of the world before receiving any sensory evidence.

### 2.2 Perceptual uncertainty

Sensory perception is always mediated by a randomly fluctuating and noisy external world. This can be stated formally as follows:

$$s = g(\eta) + \omega \tag{2}$$

In Equation (2), $g(\cdot)$ is the observation mapping from external states to the sensed signal, and $\omega$ is a noise term. Equation (2) states that sensory input $s$ received from the environment does not directly reflect the actual states of the world $\eta$, but rather some function $g$ of those states filtered through a layer of noise and uncertainty $\omega$. This can be expressed as a new PHAS principle:

> **Principle of Perceptual Uncertainty:** A PHAS perceives its environment mediated through a boundary, with internal states shaped by noisy, uncertain inputs that obscure direct observation of the world.

## 3 Free energy, alignment, and action

### 3.1 Free energy and surprise

In the model, surprise $S$ is a measure of how unlikely it is for a random variable $X$ to take a specific value $x$, given a model $\mu$ of how $X$ was generated. This is expressed algebraically as $S = -\ln p(x \mid \mu)$. Taking the negative logarithm turns small probabilities into large surprise values: an event judged nearly certain carries almost no surprise, while an event judged nearly impossible carries a great deal. Entropy is the expected or weighted average of surprise over time. Sensory inputs, or signs, $s$ are the specific observed or experienced outcomes. When $x$ is replaced by $s$, and assuming that the model $\mu$ is implicit in how sensations $s$ are generated, the expression becomes $-\ln p(s)$, representing the surprise or unlikeliness of experiencing sensations $s$ given the underlying model. Equation (3) shows how surprise directly influences free energy, with higher surprise leading to increased free energy:

$$F(s,\mu) = D\!\left[q_{\mu}(\eta)\,\|\,p(\eta \mid s)\right] - \ln p(s) \tag{3}$$

Equation (3) states that free energy is the sum of two parts: how far the agent's working beliefs are from the ideal beliefs given the evidence, plus how surprising the sensation itself is. Here $p(\eta \mid s)$ is the true posterior, the ideal updated belief about world states after observing $s$, and $q_{\mu}(\eta)$ is the approximate posterior, the agent's practical approximation to it. The Kullback-Leibler divergence $D$ in Equation (3) is a measure of how a probability distribution, here the approximate posterior, diverges from a reference distribution, here the true posterior. The double bar in $D[\cdot\,\|\,\cdot]$ separates the two distributions, and the order matters: swapping them gives a different number, so the divergence is not a symmetric distance. The divergence can never be negative. Free energy is therefore always at least as large as surprise, and a system that reduces its free energy is guaranteed to be reducing an upper limit on its own surprise. This is why free energy is minimised in place of surprise, which cannot be computed directly.

Minimising $D$ between the approximate and true posteriors means the system's internal model is more aligned with reality. This allows the agent to reverse the likelihood from the generative model in Equation (1) and to infer beliefs about the causes of sensations (for example, "was it a lemon or honey, given the sensation of sourness or sweetness"). If $D$ becomes zero, the approximate and true posteriors become identical, signifying that the system has developed a perfect model of the world, capable of inferring the causes of its sensations without error. However, the nature of sensation as described in Equation (2) means that such a state can never be reached.

### 3.2 Optimisation as alignment

Formulating the generative model from Equation (1) in terms of minimising free energy in Equation (3) transforms the generative model into an optimisation problem. Equation (4) makes this explicit by adding an optimisation process that shows the system actively working to minimise the divergence:

$$F(s,\mu) = \underbrace{D\!\left[q_{\mu}(\eta)\,\|\,p(\eta \mid s)\right]}_{\text{Divergence}} - \underbrace{\ln p(s)}_{\text{Surprise}},\qquad \mu^{*} = \arg\min_{\mu}\,\text{Divergence} \tag{4}$$

Here, $\mu^{*}$ is the optimised internal model and $\arg\min$ returns the argument that minimises the target term. Equation (4) states that belief update is represented as divergence minimisation. This can be restated as a new PHAS principle:

> **Principle of Alignment:** A PHAS actively works to minimise the divergence between its internal model and the external world. By reducing uncertainty and aligning its model with reality, the PHAS improves its ability to infer the causes of its input, moving towards a perfect representation of its environment.

### 3.3 Action selection

Agents in the model act based on prior beliefs about expected or preferred outcomes, and actions are selected to reduce surprise by bringing about anticipated results. The next action is chosen by minimising free energy as a function of the agent's internal model and the current input caused by the previous action:

$$a^{*} = \arg\min_{a}\,F\!\left(s(a),\mu\right) \tag{5}$$

In Equation (5), $a$ is a candidate action, $s(a)$ is the sign stream expected under action $a$, and $a^{*}$ is the selected action. Equation (5) selects the action that minimises free energy under the sign stream expected to follow from that action.

### 3.4 Complexity-accuracy form

Action minimises surprise by increasing the accuracy of sensory inputs. The prior $p(\eta)$ appears in place of the posterior $p(\eta \mid s)$ used in Equation (4) because actions cannot alter internal beliefs directly. Actions influence free energy only by changing the sensory input the system receives. Preferred actions are therefore those that reduce the expected ambiguity of future input, selecting outcomes that maximise expected accuracy rather than revising the model itself. This asymmetry between perception and action is central to active inference: perception updates the internal model to fit the world, while action changes the world to fit the internal model.

$$F(s,\mu) = \underbrace{D\!\left[q_{\mu}(\eta)\,\|\,p(\eta)\right]}_{\text{Complexity}} - \underbrace{\mathbb{E}_{q_{\mu}(\eta)}\!\left[\ln p(s \mid \eta)\right]}_{\text{Accuracy}},\qquad a^{*} = \arg\max_{a}\,\text{Accuracy} \tag{6}$$

Equation (6) introduces $\mathbb{E}_{q_{\mu}(\eta)}[\cdot]$ as expectation under the approximate posterior, and $\arg\max$ as the operator that returns the argument that maximises the target term. Equation (6) rewrites free energy as complexity minus accuracy and expresses action choice as expected-accuracy maximisation. The label *Complexity* here is the standard active inference name for the divergence penalty, the cost of moving beliefs away from the prior. It is unrelated to the complexity measure $C$ defined in Part II, which counts feasible options. Both labels are retained because each is standard in its own literature. Expressed as a PHAS principle:

> **Principle of Epistemic Foraging:** A PHAS selects actions that maximise the expected accuracy of future input, not by altering internal beliefs but by reducing the ambiguity of external input. Driving the system towards outcomes that align with its expectations enhances perceptual clarity, thus minimising free energy.

## 4 Niche construction

The simplest way for an agent to perform the optimisation described in Equation (6) is to selectively sample only input it expects, thus reducing the probability of unexpected outcomes (surprise). A more sophisticated strategy is to modify the environment and assert more direct control over future input. The formal symmetry of the Markov blanket is exploited to model cognitive niche construction as minimising free energy from the perspective of the niche:

$$F(a,\eta) = D\!\left[q_{\eta}(\mu)\,\|\,p(\mu \mid a)\right] - \ln p(a) \tag{7}$$

Equation (7) introduces $q_{\eta}(\mu)$ as a distribution over agent internal states from the environment side, $p(\mu \mid a)$ as the conditional model of internal states given action, and $p(a)$ as the action probability term. The term $-\ln p(a)$, labelled *Affordance* in Equation (8), captures how likely or natural a given action is within the current environment.

$$F(a,\eta) = \underbrace{D\!\left[q_{\eta}(\mu)\,\|\,p(\mu \mid a)\right]}_{\text{Divergence}} - \underbrace{\ln p(a)}_{\text{Affordance}},\qquad \eta^{*} = \arg\min_{\eta}\,\text{Divergence} \tag{8}$$

Equations (7) and (8) show how the environment works to minimise environmental surprise. The environment "learns" which actions are more likely to occur based on the states of the environment and the agent. From this perspective, the surprise term can be interpreted as a mathematical model of affordance.

The symmetry between Equations (3)/(4) and Equations (7)/(8) demonstrates that the niche and its inhabitants can become mutually predictable, forming a joint system in which environment and agents influence each other through mutual self-evidencing. Self-evidencing means that each side behaves in ways that generate the very evidence its model of the other predicts. Mutual predictability arises because the coupling through the Markov blanket makes the mapping between external signals and internal states statistically regular. As these regularities stabilise, each side can forecast the other's effects via the interface without violating conditional independence. The environment predicts and influences the actions an agent is most likely to take, making certain behaviours more probable and thus more "afforded" by the environment. This can be stated as a new PHAS principle:

> **Principle of Coupled Adaptation:** A PHAS co-evolves with its environment, wherein the environment minimises environmental surprise by affording specific actions, thus influencing agents to adopt some behaviours over others within a given context, guiding the system towards mutually predictable interactions.

## 5 Peer interaction and communication

While the original PHAS model recognises PHAS as a composite socio-technical system, the model presented here makes this explicit by adding a peer model. Agent-based simulations, in which agents interact with each other and their environment through active inference, support the modelling process. The model does not formally distinguish between an agent's peers and other external systems, viewing them as equally opaque. However, because the intention is to incorporate the intentional stance and intentional systems into the model, it is helpful to adopt different notations. Equation (2) can then be re-purposed to describe the nature of incoming communication:

$$c_{\text{in}} = g(\psi) + \omega \tag{9}$$

Equation (9) states that incoming communication $c_{\text{in}}$ is a function of the peer's internal states $\psi$ perceived through a layer of noise and uncertainty $\omega$. Re-purposing Equation (5), an agent chooses what to communicate by minimising free energy as a function of what it perceives about its peer's response to the previous communication:

$$c_{\text{out}}^{*} = \arg\min_{c_{\text{out}}} F\!\left(c_{\text{in}}(c_{\text{out}}),\mu\right) \tag{10}$$

In Equation (10), $c_{\text{out}}$ is outgoing communication choice, $c_{\text{out}}^{*}$ is the selected outgoing communication, and $c_{\text{in}}(c_{\text{out}})$ indicates that the incoming signal depends on the outgoing choice. As with Equation (6), this can be stated as maximising accuracy:

$$F(c_{\text{in}},\mu) = \underbrace{D\!\left[q_{\mu}(\psi)\,\|\,p(\psi)\right]}_{\text{Complexity}} - \underbrace{\mathbb{E}_{q_{\mu}(\psi)}\!\left[\ln p(c_{\text{in}}(c_{\text{out}}) \mid \psi)\right]}_{\text{Accuracy}},\qquad c_{\text{out}}^{*} = \arg\max_{c_{\text{out}}}\,\text{Accuracy} \tag{11}$$

Equation (11) introduces $q_{\mu}(\psi)$ as the approximate belief over peer states, $p(\psi)$ as the peer-state prior, and $p(c_{\text{in}}(c_{\text{out}}) \mid \psi)$ as the communication likelihood term. It gives the complexity-accuracy form for communication: the agent selects outgoing messages that maximise the expected accuracy of its peer model and incoming communication.

## 6 Shared expectations and hierarchical composition

### 6.1 Shared norms, conventions, and expectations

$\Phi$ denotes a set of shared norms, conventions, and expectations:

$$\Phi = f(\psi)\gamma + (1 - \gamma)\mu \tag{12}$$

Equation (12) introduces $\Phi$ as the agent's representation of shared norms, conventions, and expectations, expressed in the same belief space as the internal model $\mu$ so that the two can be blended numerically. The function $f$ translates the peer's internal states $\psi$ into that same space. The weight $\gamma$ lies between 0 and 1, so $\Phi$ is $\gamma$ parts peer-derived and $(1 - \gamma)$ parts self-derived. The parameter $\gamma$ functions as an authority weight that determines how much the agent trusts its peer's perspective relative to its own beliefs. When $\gamma$ is high, the peer's views dominate the shared expectation. When $\gamma$ is low, the agent's own model prevails. This weighting captures a structural feature of organisational life that becomes consequential in the formal model: hypothesis H10, stated in the Key Findings part below, predicts that asymmetry in authority weights between interacting agents is a source of coordination friction.

### 6.2 Subsystems and supersystems

Because free energy is an additive and conserved property, the model applies equally to subsystems and supersystems:

$$F_{\text{super}} = \sum_{i=1}^{N} F_{i}\!\left(c_{\text{in},i},\,s_{i},\,\mu_{i}\right) \tag{13}$$

Equation (13) introduces $F_{\text{super}}$ as supersystem free energy, $N$ as the number of subsystems, and $F_{i}$ as subsystem-level free energy. The subscript $i$ indexes local terms $(c_{\text{in},i}, s_{i}, \mu_{i})$, and the summation sign $\sum$ adds up the free-energy contributions of each of the $N$ subsystems in turn. The equation expresses multiscale additivity: a supersystem's free energy equals the sum of its subsystems' free energies, with contributions from the parts summing to the whole. Complex systems can therefore be simplified by modelling them at a higher level, and a PHAS can be modelled independently at multiple scales of the component hierarchy.

### 6.3 Multi-peer extension

Equation (14) extends shared expectations to many peers with heterogeneous influence:

$$\Phi = \sum_{i=1}^{N}\left(f(\psi_{i})\gamma_{i} + (1 - \gamma_{i})\mu\right) \tag{14}$$

Each peer $i$ carries a distinct authority weight $\gamma_i$, allowing the model to represent organisational structures in which different roles, ranks, or external actors exert different degrees of influence over shared norms. The heterogeneity of the $\gamma_i$ values makes the model sensitive to how influence is distributed, not only to group size. As printed, the sum grows with the number of peers because the self-derived term $(1 - \gamma_i)\mu$ is counted once per peer. The formal analysis in Chapter 5 of the dissertation therefore works with the averaged form $\Phi = \frac{1}{N}\sum_{i=1}^{N}\left(f(\psi_{i})\gamma_{i} + (1 - \gamma_{i})\mu\right)$, which keeps $\Phi$ within the range of the blended beliefs. The two forms differ only by the constant factor $1/N$.

![Active inference model of PHAS.](<Analytical Models/figures/figure-4-active-inference-model-of-phas.jpg>)

The first figure expresses the model in the language of active inference. The system is organised around a Markov blanket that separates external states ($\eta$) from internal states ($\mu$), while still allowing coupling through sensation and action. Sensation is modelled as noisy input, $s = g(\eta) + \omega$. Peer states ($\psi$) are not directly observable, but are inferred through noisy incoming communication, $c_{\text{in}} = g(\psi) + \omega$. The lower panels make the formal decomposition explicit by expressing free energy in terms of divergence and surprise for perception and niche construction, and in terms of complexity and accuracy for action and communication.

![Expanded PHAS framework mapping the formal active inference model into a representation aligned with the original PHAS visualisation.](<Analytical Models/figures/figure-6-expanded-phas-framework.jpg>)

The expanded framework figure maps the same formal model back into a representation aligned with the original PHAS framework. The upper part distinguishes concrete systems from conceptual systems and illustrates how uncertainty reduces over time as the conceptual model becomes better aligned with the operational environment. Action selection is placed outside the agent's boundary to emphasise that action is a coupling to the environment, not an internal cognitive event. Expectations, norms, and conventions ($\Phi$) are shown as contextual priors that shape both agents' interpretations and choices, representing how shared meanings and social constraints guide attention and stabilise coordination.

---

# Part II: Complexity as Feasible Distinct Optionality

## 7 Configuration space

### 7.1 The product space

The model treats the controllable degrees of freedom as $X_{1},\ldots,X_{n}$ and defines the configuration space:

$$X = \prod_{i = 1}^{n}X_{i} \tag{15}$$

A controllable degree of freedom is any aspect of the socio-technical system that can be set, selected, or governed, either by the system itself or an external force acting on it. The term includes technical design choices, such as component selection or topology, and organisational choices, such as decision rights, escalation paths, and approval rules. Treating these as degrees of freedom enables a single configuration space to represent both engineering and governance commitments.

Each $X_{i}$ is a set of alternatives for a design lever or policy choice, and $n$ is the number of such levers. The product sign $\prod$ combines the sets: the configuration space $X$ lists every possible combination of one alternative from each lever, just as the product of the set sizes gives the number of combinations. Because the system under study is a PHAS, these degrees of freedom are grouped as:

$$X = X_{\text{tech}} \times X_{\text{org}} \times X_{\text{policy}} \times X_{\text{practice}} \times X_{\text{language}} \times X_{\text{worldview}} \times X_{\text{boundary}} \tag{16}$$

Where:

- $X_{\text{tech}} \rightarrow$ technical artefacts and architectural choices
- $X_{\text{org}} \rightarrow$ roles, decision rights and escalation paths
- $X_{\text{policy}} \rightarrow$ rules that authorise or forbid actions
- $X_{\text{practice}} \rightarrow$ codified routines and patterned practices
- $X_{\text{language}} \rightarrow$ shared semantics and data definitions
- $X_{\text{worldview}} \rightarrow$ the ensemble of beliefs, expectations, norms, and conventions that render options legitimate or illegitimate, including shared worldviews (organisation-wide or group-specific) and individual beliefs
- $X_{\text{boundary}} \rightarrow$ the system boundary and its external interfaces. Each PHAS may include multiple sub-PHAS within this boundary, each with its own configuration space and constraints.

The product construction and grouping do not assume that the dimensions are independent in practice. However, they do provide a neutral starting point that makes potentially relevant choices explicit. Several factors are intangible, particularly language and worldview. These are included because they constrain action and coordination as directly as technical interfaces. Shared operational vocabulary can enable cross-team workflows that are otherwise unavailable. Incompatible assumptions about acceptable risk can exclude configurations that are technically possible but socially illegitimate.

**Table 2. Configuration space factors, their constituent elements, typical interfaces, and illustrative rating sources.**

| Factor $i$ | Elements | Interfaces | Typical sources for ratings |
|---|---|---|---|
| $X_{\text{tech}}$ | devices, services, components | APIs, network links, buses, protocols | CMDB, architecture repository |
| $X_{\text{org}}$ | roles, teams | handoffs, reporting lines, RACI links | organisation charts, SOPs |
| $X_{\text{policy}}$ | policies, regulations, standards | cross-references, compliance bindings | policy register |
| $X_{\text{practice}}$ | procedures, routines | workflow handoffs, checklists | QMS, playbooks |
| $X_{\text{language}}$ | ontologies, controlled terms | mappings, synonym bridges | data dictionary |
| $X_{\text{worldview}}$ | norms, commitments | alignment mechanisms, forums | charters, retrospectives |
| $X_{\text{boundary}}$ | counterpart systems, vendors | SLAs, contracts, network/APIs | contract store, interface catalogue |

## 8 Constraints, distinctness, and the feasible set

### 8.1 Decision resolution

Some levers are continuous or very fine-grained. A decision resolution $\Delta = \{\Delta_{i}\}$ is fixed to render each domain finite, producing $X^{\Delta} = \prod_{i} X_{i}^{\Delta}$, where $\Delta$ is the smallest difference treated as a distinct option and $X_{i}^{\Delta}$ denotes the finite set of alternatives that remains for lever $i$ once differences smaller than $\Delta_{i}$ are ignored. The decision resolution $\Delta$ acts as a modelling granularity. For discrete levers, it is usually implicit. For continuous levers, such as thresholds, tuning parameters, or resource allocations, $\Delta$ specifies the smallest change that is treated as meaningfully different for the purposes of design and operation. The resolution should reflect the precision at which decisions can be made and validated, and the precision at which outcomes can be distinguished in monitoring and assurance.

### 8.2 Hard constraints

Not every combination in $X^{\Delta}$ is feasible or permitted. A constraint set $K$ captures hard constraints that hold regardless of the current staff, budget, or time. $K$ includes interface and compatibility rules, architectural invariants, safety segregation, required cybersecurity controls, regulatory and certification limits, licensing and data-residency terms, platform commitments, site and environmental limits, semantic preconditions for coordination, normative commitments arising from worldview, and explicit boundary commitments. Applying $K$ prunes impossible or disallowed combinations and enforces coupling where it exists, including across internal sub-PHAS interfaces. The constraint set $K$ captures structural feasibility rather than effort. A configuration that violates $K$ is prohibited, even with unlimited time and staffing. $K$ therefore represents commitments that cannot be negotiated during a response, such as safety segregation rules, interface contracts, licensing conditions, and hard budget ceilings set by governance.

### 8.3 Distinct optionality

If every micro-variation is treated as distinct, the option count can be inflated by near-duplicates. Near-duplicates arise when two configurations differ in low-level settings but yield outcomes that are indistinguishable at the level relevant to decision-making. Counting such micro-variations can make complexity appear higher than the practical choice space faced by engineers and operators. To define "distinct option" explicitly, the model introduces a binning map:

$$\varphi: X^{\Delta} \rightarrow \mathcal{B} \tag{17}$$

where $\mathcal{B}$ is a finite space of bins induced by rounding or categorising outcomes and socio-technical attributes. The map $\varphi$ assigns each fine-grained configuration to a bin that represents the attributes by which options are considered distinct. A bin can be defined in terms of performance outcomes, such as latency bands, or in terms of socio-technical attributes, such as auditability class or coordination overhead class.

Binning is intentionally coarse. It reflects that many decisions are made using categories rather than exact values, and that monitoring and assurance often rely on thresholds and bands. Changing the binning scheme changes the number of options, which is appropriate because distinctness is defined relative to what can be noticed and acted upon. The bins are part of the modelling assumptions and should be selected to align with the questions being asked. The model states this as an equivalence relation:

$$x \sim y \Leftrightarrow \varphi(x) = \varphi(y) \tag{18}$$

The double arrow $\Leftrightarrow$ reads "exactly when", and the tilde $\sim$ reads "counts as the same option as". In words, two configurations are treated as the same option when, and only when, they fall into the same bin under $\varphi$. The groups of configurations that share a bin, called equivalence classes, are therefore sets of near-duplicates that are indistinguishable with respect to the chosen bins.

### 8.4 The feasible set

The feasible set at resolution $\Delta$ is then the quotient:

$$\mathcal{O}^{\Delta} = \{\, x \in X^{\Delta} : x\text{ satisfies }K\,\}/ \sim \tag{19}$$

The set-builder expression $\{\, x \in X^{\Delta} : x\text{ satisfies }K\,\}$ reads "the set of all configurations $x$ for which the stated condition holds", so the braces collect every configuration that respects the hard constraints. The trailing $/\sim$ is the quotient operation: it merges each group of equivalent configurations into a single entry, keeping one representative per group. The set $\mathcal{O}^{\Delta}$ can be read as the feasible option set after both structural feasibility and distinctness are applied. It contains one representative for each distinct feasible option, rather than every micro-configuration. For example, if $\varphi$ rounds cost to budget tiers, then two configurations that differ by a small cost delta within the same tier are treated as a single option. Under this definition, the option count reflects what can realistically be compared, selected, and justified.

The factor $X_{\text{worldview}}$ operates as both a state within the configuration space and the primary logic of the internal generative model described in Part I. It represents the set of norms and beliefs that an organisation can intentionally shift or align, yet it also acts as a fundamental source of constraints within $K$. By defining what is considered legitimate or possible, $X_{\text{worldview}}$ prunes the wider configuration space. It is the system's meta-logic: any chosen configuration of technical or policy levers must remain consistent with the shared expectations and normative commitments of the agents involved.

Treating worldview as both a variable and a constraint reflects that norms can change, but only within limits set by identity, regulation, and external expectations. An organisation can adopt a stronger security posture and new escalation norms, but it cannot simultaneously maintain mutually incompatible commitments. Encoding these commitments inside $K$ prevents the model from counting options that are organisationally unreachable.

### 8.5 Complexity as total optionality

**Complexity** is defined as the size of this feasible set:

$$C = |\mathcal{O}^{\Delta}| \tag{20}$$

Equation (20) defines complexity as the count of distinct feasible options available at the chosen resolution. The vertical bars denote the number of elements in a set. Later in the document the same bars around a number, such as $|\gamma_A - \gamma_B|$, denote its absolute value instead. The units of $C$ are an option count rather than a physical quantity, and $C$ is finite because the choice sets have been discretised and near-duplicates have been collapsed. This treats complexity as total optionality: $C$ counts all distinct socio-technical configurations that the PHAS can, in principle, realise once structural commitments are respected. This complexity measure is unrelated to the *Complexity* label in the free-energy decompositions of Part I, which names a divergence penalty on beliefs.

$C$ counts both desirable configurations and *failure modes* (unsafe, brittle, non-compliant, or otherwise unacceptable configurations). This is intentional. As the option set grows, so does the number of alternatives that must be evaluated, ruled out, constrained, or monitored. Each additional configuration increases both choice and error surface. Because a PHAS often comprises constituent sub-PHAS, $C$ can also be computed at the subsystem level when useful, and then related to the whole via the composition property below, with cross-subsystem coupling captured in $K$.

Where feasibility depends on the lifecycle or operating state $\ell$ (commissioning, steady operation, incident response), constraints are indexed as $K(\ell)$, yielding $\mathcal{O}^{\Delta}(\ell)$ and $C(\ell) = |\mathcal{O}^{\Delta}(\ell)|$. Indexing constraints by lifecycle state $\ell$ makes explicit that feasibility is mode-dependent. A configuration that is feasible during commissioning may be infeasible during incident response because approvals, maintenance windows, or tooling are not available. Representing this through $K(\ell)$ allows the model to compare the option space across operational modes without changing the underlying definition of complexity.

Two simple sanity checks are used in the analysis:

- **Direction of change.** Adding another lever (expanding some $X_{i}^{\Delta}$) or relaxing a hard constraint in $K$ cannot decrease $C$. Adding a hard constraint to $K$ cannot increase $C$. This remains true even though near-duplicates are collapsed via $\varphi$.
- **Composition.** If two subsystems $A$ and $B$ are mostly independent (few coupling constraints), the combined option count is approximately multiplicative: $C_{A \| B} \approx C_{A} \cdot C_{B}$, where $A \| B$ denotes the two subsystems operated side by side (here $A$ and $B$ name subsystems, not the variety counts defined in Part III). Coupling constraints reduce this by ruling out combinations.

The composition property is approximate because socio-technical subsystems are rarely fully independent. Coupling enters through cross-subsystem constraints in $K$, such as shared resources, shared interfaces, or shared governance. The multiplicative calculation is therefore most useful as an order-of-magnitude argument that highlights how quickly option counts grow when additional levers are introduced without corresponding constraints.

A worked example shows the growth. Two PLC families, three network topologies, and two database engines yield $2 \times 3 \times 2 = 12$ raw combinations. If a safety invariant in $K$ forbids one topology with one PLC at high-criticality sites, this leaves 10 feasible combinations, so $C = 10$. Introducing a standard incident-response playbook enables two additional coordination patterns across roles. If all are compatible, $C$ becomes $10 \times 3 = 30$. Adopting a shared threat taxonomy unlocks one further cross-team workflow, and $C$ becomes $30 \times 2 = 60$. Adding a quality-of-service target counted at $\Delta = 5\%$ from 0 to 100 per cent yields 21 levels. If independent of the other choices, $C = 60 \times 21 = 1{,}260$.

The numerical illustration shows how options can multiply across technical, organisational, and informational changes. Even when each individual change appears modest, the combined option count can grow rapidly. This provides a quantitative rationale for design practices that deliberately reduce option space through standardisation, architectural invariants, and shared vocabularies.

## 9 Linking optionality to entropy and surprise

In the PHAS-EAI model, surprise is defined as $S = -\ln p(x \mid \mu)$, and entropy is the expected or weighted average of surprise over time. Here, $x$ denotes a configuration, so the PHAS definition is read as the surprise of selecting or observing configuration $x$ under the internal model $\mu$. When $\mathcal{O}^{\Delta}$ is interpreted as a discrete hypothesis space of configurations, $C$ sets the scale of how uncertain selection can be before usefulness and time constraints are applied.

Surprise and entropy connect option counts to the uncertainty experienced by decision-makers. The probability term $p(x \mid \mu)$ denotes the plausibility of configuration $x$ under an internal model $\mu$. A low-probability configuration is surprising and typically requires either explanation or corrective action. Under an uninformative (uniform) distribution over $\mathcal{O}^{\Delta}$, the maximum Shannon entropy over configurations is $\ln C$ (or $\log_{2} C$ in bits). More generally, if the PHAS internal model $\mu$ induces a non-uniform distribution over configurations or outcomes, then expected surprise is reduced by concentrating probability mass on a smaller subset of typical configurations. This is the discrete counterpart to the observation that stronger priors reduce uncertainty in active inference. In active inference, complexity appears as a divergence term between posterior and prior beliefs, while accuracy rewards explanations that predict sensations. The cardinality $C$ is not that KL divergence, but it bounds it by determining how large the discrete hypothesis space can be. When there are equiprobable configurations, selecting the realised configuration requires $\log_{2} C$ bits of information.

Worldview, policy, and technical commitments act as priors that concentrate probability mass and prune options, thereby reducing entropy and the informational work required to disambiguate configurations during design and operation. Increasing $C$ increases the informational work required to identify, justify, and stabilise a configuration, unless parallel investment narrows the effective hypothesis space through stronger constraints, sharper priors, or better tooling.

## 10 Model parameters and subjective complexity

### 10.1 Rating vector and complexity potential

Each factor $X_{i} \in \{\text{tech}, \text{org}, \text{policy}, \text{practice}, \text{language}, \text{worldview}, \text{boundary}\}$ can be further described using the parameter set adopted from Schöttl and Lindemann (2015) summarised in Table 3. Option counts provide a structural upper bound, but response time is also influenced by the complexity of each factor and its rate of change. The weighted parameters in Table 3 are used to model this by assigning ratings to each factor. For each factor $i$, the rating vector is:

$$\mathbf{p}_{i} = \left( NE_{i},VE_{i},DI_{i},NI_{i},VI_{i},\,\Delta NE_{i},\Delta VE_{i},\Delta DI_{i},\Delta NI_{i},\Delta VI_{i},\Delta E_{i} \right) \tag{21}$$

The rating vector $\mathbf{p}_{i}$ groups five structural properties and six rates of change. In these abbreviations the prefix $\Delta$ reads "change in" and is unrelated to the decision resolution $\Delta$ of section 8.1, and the E in $\Delta E$ abbreviates "elements", not the experience rating $E$ used from section 10.2 onwards. The structural properties describe the number of distinct elements in the factor, their variability, and the number of interfaces that connect them. The change terms describe how quickly those properties evolve. Ratings are on an ordinal 1-10 scale, which supports comparative analysis even when absolute measurement is impractical.

**Table 3. Complexity model system parameters and weights.**

| Group | Group weight | Parameter | Abbr. | Scale | Parameter weight |
|---|---|---|---|---|---|
| System properties | 0.4 | Number of elements (processes and resources) | NE | 1-10 | 0.08 |
| | | Variety of elements (processes and resources) | VE | 1-10 | 0.09 |
| | | Degree of interconnectedness | DI | 1-10 | 0.02 |
| | | Number of interfaces to neighbouring system parts | NI | 1-10 | 0.25 |
| | | Variety of interfaces to neighbouring system parts | VI | 1-10 | 0.07 |
| System changes | 0.6 | Change in number of elements | $\Delta$NE | 1-10 | 0.06 |
| | | Change in variety of elements | $\Delta$VE | 1-10 | 0.01 |
| | | Change in degree of interconnectedness | $\Delta$DI | 1-10 | 0.20 |
| | | Change in number of interfaces | $\Delta$NI | 1-10 | 0.03 |
| | | Change in variety of interfaces | $\Delta$VI | 1-10 | 0.06 |
| | | Change of elements (processes and resources) | $\Delta$E | 1-10 | 0.13 |

The per-factor complexity potential $CP_{i}$ is:

$$\begin{aligned}
CP_{i} &= 0.4(0.08\, NE_{i} + 0.09\, VE_{i} + 0.02\, DI_{i} + 0.25\, NI_{i} + 0.07\, VI_{i}) \\
&\quad + 0.6(0.06\,\Delta NE_{i} + 0.01\,\Delta VE_{i} + 0.20\,\Delta DI_{i} + 0.03\,\Delta NI_{i} + 0.06\,\Delta VI_{i} + 0.13\,\Delta E_{i})
\end{aligned} \tag{22}$$

Equation (22) aggregates the five structural attributes and six rates of change into a single complexity potential. A factor with many varied parts, numerous interfaces, and rapidly shifting connections scores high, while a small, uniform, loosely coupled, stable factor scores low. With every rating at its minimum of 1, $CP_{i}$ is approximately 0.5, and with every rating at 10 it is approximately 5.0, so the complexity potential of a factor ranges between roughly 0.5 and 5. The group weights in $CP_{i}$ give greater emphasis to system change than to static structure. This aligns with the view that volatility and churn can create more operational drag than complexity that is well understood and stable. Schöttl and Lindemann emphasise that both the 1-10 scales and the weights are system-dependent and should be recalibrated for the domain under study.

### 10.2 Subjective complexity

Schöttl and Lindemann (2015) combine interaction difficulty with a person's experience and mental flexibility, recognising that interaction difficulty is experienced differently by people with different levels of expertise. Interaction type $IT \in \{1,\ldots,10\}$ captures the intrinsic demand of the task, while experience $E \in \{1,\ldots,5\}$ and mental flexibility $MF \in \{1,\ldots,5\}$ capture capability. Table 4 shows example scorings of interaction types, and Table 5 the scoring scheme used for experience and mental flexibility.

**Table 4. Example scoring of interaction types.**

| IT | Description |
|---|---|
| 1 | Easy, low-demand job with clear instructions and no time pressure, with marginal interfaces |
| 5 | Ordinary, well-structured job with diversified content and medium responsibility |
| 10 | Highly demanding job with high time pressure, responsibility for subordinates and many external interfaces |

**Table 5. Scoring scheme for experience and mental flexibility.**

| Value | Label |
|---|---|
| 1 | Very low |
| 2 | Low |
| 3 | Medium |
| 4 | High |
| 5 | Very high |

Perception demand decreases as experience and flexibility increase. A linear map that preserves this direction is:

$$\theta(E,MF) = 12.25 - 1.125\,(E + MF) \in [1,10],\qquad u(E,MF) = \frac{10 - \theta(E,MF)}{9} \in [0,1] \tag{23}$$

The linear map $\theta(E,MF)$ in Equation (23) is the (inverse) perception score, and assigns a higher numerical demand to lower experience and flexibility. The constants follow from the endpoints of the rating scales: the combined rating $E + MF$ runs from 2 (both very low) to 10 (both very high), and the coefficients 12.25 and 1.125 are chosen so that this range maps linearly onto the demand scale, with $\theta = 10$ at the low end and $\theta = 1$ at the high end. The normalised skill factor $u(E,MF)$ rescales this to the unit interval, where 0 represents no effective skill benefit and 1 represents the maximum skill benefit available under the scoring scheme. The skill factor $u(E,MF)$ rises with experience and flexibility, and is used to scale both cognitive headroom and mobilisation time.

---

# Part III: Resilience as Mobilisable Variety

## 11 Useful and survivable variety

A disturbance $d$ has a **magnitude** $M_{d}$ and **timescale** $\tau_{d}$. The disturbance represents a situation to which the system must respond, such as a component failure, a cyber incident, an extreme weather event, or a supplier outage. The magnitude $M_{d}$ represents severity, for example the scale of service degradation or the level of damage. The timescale represents the time available to address the disturbance before unacceptable outcomes occur.

For a disturbance $d$ with a characteristic timescale $\tau_{d}$, the feasible set $\mathcal{O}^{\Delta}$ yields two nested sets:

**Useful variety** (required service maintained):

$$A_{d} = \{\, x \in \mathcal{O}^{\Delta} : x\text{ would deliver required service under }d\text{ with acceptable risk}\,\} \tag{24}$$

with $A = |A_{d}|$.

**Survivable variety** (safety and non-collapse maintained, service may degrade):

$$B_{d} = \{\, x \in \mathcal{O}^{\Delta} : \text{system remains safe and non-collapsed under }d\,\} \tag{25}$$

with $B = |B_{d}|$.

By construction, $A_{d} \subseteq B_{d} \subseteq \mathcal{O}^{\Delta}$, hence $A \leq B \leq C$. The symbol $\subseteq$ reads "is contained in": every useful option is also survivable, and every survivable option is in the feasible set.

The sets $A_{d}$ and $B_{d}$ separate service adequacy from mere survival. In infrastructure contexts, safe degradation may be acceptable for a limited period, whereas unsafe operation is not.

## 12 Headroom

Headroom $H$ is the mobilisable slack available during the response. It comprises a physical component and a cognitive component. The normalised physical headroom $H_{\text{phys}} \in [0,1]$ aggregates slack in capacity, inventory, budget, and authority. The model treats $H_{\text{phys}}$ as an assessed input on a 0 to 1 scale rather than deriving it from a formula. The cognitive component $H_{\text{cog}}$ reflects skill and task demand:

$$H_{\text{cog}} = h + (1 - h)\, u(E,MF)\, q(IT) \tag{26}$$

Equation (26) combines three ideas. First, $h \in (0,1]$ denotes the minimum cognitive reserve that is preserved by design, for example through automation, checklists, or pre-authorised actions. Second, the normalised skill factor $u(E,MF) \in [0,1]$ denotes capability as a function of experience and mental flexibility. Third, $q(IT)$ denotes the task's demand level and is modelled as a decreasing function of interaction type, mapping the 1 to 10 interaction-type scale into $[0,1]$. The symbol $q$ here names the task-demand function and is unrelated to the approximate posterior $q_{\mu}(\eta)$ of Part I. The formal analysis treats $q(IT)$ as a bounded input in $[0,1]$ (assumption S5.3-A2 in the theorem inventory) rather than fixing one functional form. Multiplying $u(E,MF)$ and $q(IT)$ captures that skill is most valuable when tasks are demanding, and that limited skill reduces usable headroom under stress. The algebra guarantees a floor: however low the skill or however demanding the task, $H_{\text{cog}}$ never falls below $h$, and it rises towards 1 as skill meets demand.

Total headroom is:

$$H = H_{\text{phys}} \times H_{\text{cog}} \in [0,1] \tag{27}$$

Total headroom $H$ is modelled as the product of physical and cognitive components, indicating that both types of slack must be available simultaneously. The multiplicative form keeps $H$ within $[0,1]$ and penalises bottlenecks in either component. A team can possess strong cognitive capabilities yet remain constrained by a lack of authority or capacity. Surplus capacity is ineffective if decision-making is blocked.

## 13 Response time and structural drag

Response time decomposes as:

$$\tau = \tau_{\text{detect}} + \tau_{\text{decide}} + \tau_{\text{execute}} \tag{28}$$

*Detect* encompasses sensing and triage and is hindered by low observability and ambiguous signals. *Decide* encompasses delays due to coordination and authorisation. *Execute* covers deployment and change procedures. Keeping the stages separate supports analysis of interventions that shorten one stage without necessarily affecting the others. Each stage has a baseline time under a stable configuration:

$$\tau_{\text{detect}}^{0},\quad\tau_{\text{decide}}^{0},\quad\tau_{\text{execute}}^{0} \tag{29}$$

The baseline times represent typical stage durations under stable operating conditions with clear procedures and no unusual friction. They can be estimated from historical incident records or from rehearsal exercises. They do not represent best-case times, but rather typical times under normal operating assumptions.

*Structural drag* from complexity potential increases these baselines. The complexity potential vector aggregates all seven factors:

$$CP = \left( CP_{\text{tech}},CP_{\text{org}},CP_{\text{policy}},CP_{\text{practice}},CP_{\text{language}},CP_{\text{worldview}},CP_{\text{boundary}} \right)^{\top} \tag{30}$$

Equation (30) expands Equation (22) by combining the per-factor complexity potentials into a single vector, with the superscript $\top$ marking it as a column of seven numbers, one per factor. Stage times then become:

$$\begin{aligned}
\tau_{\text{detect}} &= \tau_{\text{detect}}^{0}\,\left[ 1 + \gamma_{\text{det}}^{\top}CP \right], \\
\tau_{\text{decide}} &= \tau_{\text{decide}}^{0}\,\left[ 1 + \gamma_{\text{dec}}^{\top}CP \right], \\
\tau_{\text{execute}} &= \tau_{\text{execute}}^{0}\,\left[ 1 + \gamma_{\text{exe}}^{\top}CP \right].
\end{aligned} \tag{31}$$

where $\gamma_{\text{det}},\gamma_{\text{dec}},\gamma_{\text{exe}} \in \mathbb{R}_{\geq 0}^{7}$ denote stage-specific sensitivity vectors, each a list of seven non-negative numbers, one per factor. The expression $\gamma_{\text{det}}^{\top}CP$ is a weighted sum: each factor's complexity potential is multiplied by that stage's sensitivity to the factor, and the products are added up. The vector component $\gamma_{\text{det},i}$ measures how factor $i$ slows detection, $\gamma_{\text{dec},i}$ measures decision-making drag, and $\gamma_{\text{exe},i}$ measures execution drag. A factor can therefore slow one stage more than another. For example, policy complexity may primarily affect decision-making through approval and compliance checks, while technical complexity may primarily affect detection through observability challenges. The stage sensitivities reuse the letter $\gamma$ with distinguishing subscripts and are unrelated to the authority weights $\gamma_{i}$ of Part I.

Structural drag can be interpreted through the PHAS active-inference lens as a noise and coupling penalty at the Markov blanket. A high complexity potential $CP$ corresponds to an operational landscape with a lower signal-to-noise ratio and a more ambiguous mapping between external signals and internal states. Resolving uncertainty then takes longer, which is reflected in the scaling of response times $\tau$ by $CP$ in (31).

## 14 Skill and effective mobilisation time

Human skill shortens the inflated time. With $\lambda_{\tau} \in [0,1)$ as the maximum fractional reduction attributable to skill, the effective time multiplier is:

$$\sigma_{\tau} = 1 - \lambda_{\tau}\, u(E,MF) \in (0,1] \tag{32}$$

The multiplier $\sigma_{\tau}$ reduces response time as skill increases, with $\lambda_{\tau}$ setting the maximum achievable speed-up. No amount of skill can reduce the time below $1 - \lambda_{\tau}$ of the structurally determined time. This reflects that some delays are imposed by physical realities and governance rather than by individual proficiency.

The effective mobilisation time is:

$$\tau_{\text{eff}} = \sigma_{\tau}\,\tau \tag{33}$$

The effective mobilisation time $\tau_{\text{eff}}$ is the response time used in the time-conditioned option counts. It is the quantity compared with the disturbance timescale $\tau_{d}$. At the limits, $\sigma_{\tau} = 1$ when $u = 0$, so skill offers no speed-up (inexperienced, inflexible). As $u \to 1$ (experienced, flexible), $\sigma_{\tau} \to 1 - \lambda_{\tau}$, corresponding to a maximum fractional time reduction of $\lambda_{\tau}$ and a speed-up factor of $1/(1 - \lambda_{\tau})$.

The model uses $u(E,MF)$ in both $H_{\text{cog}}$ and $\tau_{\text{eff}}$ deliberately. Skill both frees cognitive reserve (more usable attention under stress) and increases execution speed (faster, more reliable action sequences). These are distinct mechanisms, so this is not double-counting.

## 15 Time-conditioned option counts

### 15.1 Time allowance ratio and response functions

Only a share of options can be mobilised within the shock window. The time-allowance ratio is:

$$r = \frac{\tau_{d}}{\tau_{\text{eff}}} \tag{34}$$

The ratio $r$ in Equation (34) compares the time available, $\tau_{d}$, with the effective time $\tau_{\text{eff}}$. Values below 1 indicate that the response is time-constrained, so only a subset of options is realistically selectable. Values above 1 indicate that time is sufficient, so mobilisation is not limited by speed. Three response functions represent the share of options that can be mobilised within the available time window:

$$f_{A}(r) = \min\left( 1,\, r^{\varepsilon_{A}} \right),\quad f_{B}(r) = \min\left( 1,\, r^{\varepsilon_{B}} \right),\quad f_{C}(r) = \min\left( 1,\, r^{\varepsilon_{C}} \right) \tag{35}$$

where $\varepsilon_{A},\varepsilon_{B},\varepsilon_{C} > 0$ are elasticities for useful, survivable, and total option mobilisation. The response functions $f_{A}, f_{B}, f_{C}$ are unrelated to the belief-translation function $f$ of Equations (12) and (14). The minimum operator caps each fraction at 1, so the functions saturate once there is sufficient time to mobilise the full option set, and each fraction shrinks as the time window tightens. The elasticities control how sharply option accessibility falls as time becomes scarce. Separate elasticities are used because useful options may require more coordination than survivable options, and total optionality may include options that are costly to mobilise. For notational convenience:

$$f_{A}\left( \tau_{d},\tau_{\text{eff}} \right) := f_{A}\left( \frac{\tau_{d}}{\tau_{\text{eff}}} \right),\quad f_{B}\left( \tau_{d},\tau_{\text{eff}} \right) := f_{B}\left( \frac{\tau_{d}}{\tau_{\text{eff}}} \right),\quad f_{C}\left( \tau_{d},\tau_{\text{eff}} \right) := f_{C}\left( \frac{\tau_{d}}{\tau_{\text{eff}}} \right) \tag{36}$$

The symbol $:=$ reads "is defined as". Writing the response functions with two arguments makes it explicit that the same time allowance ratio can arise from the disturbance evolving quickly, mobilisation being slow, or both. This supports analysis of whether resilience could be improved by faster detection and execution, or by designing for greater tolerance to disturbances.

### 15.2 Time-conditioned effective counts

The time-conditioned effective option counts are:

$$\widetilde{A}\left( \tau_{d},\tau_{\text{eff}} \right) := A\, f_{A}\left( \tau_{d},\tau_{\text{eff}} \right),\quad \widetilde{B}\left( \tau_{d},\tau_{\text{eff}} \right) := B\, f_{B}\left( \tau_{d},\tau_{\text{eff}} \right),\quad \widetilde{C}\left( \tau_{d},\tau_{\text{eff}} \right) := C\, f_{C}\left( \tau_{d},\tau_{\text{eff}} \right) \tag{37}$$

The effective counts $\widetilde{A}$, $\widetilde{B}$, and $\widetilde{C}$ represent the sets of useful, survivable, and total options that are practically mobilisable within the available time.

## 16 Magnitude limits and resilience score

The absorbable magnitude is expressed as a function of time-conditioned option counts and headroom:

$$M_{0}\left( \tau_{d},\tau_{\text{eff}} \right) = k\,\widetilde{A}\left( \tau_{d},\tau_{\text{eff}} \right)^{\alpha}H^{\beta},\qquad M_{\max}\left( \tau_{d},\tau_{\text{eff}} \right) = k\,\widetilde{B}\left( \tau_{d},\tau_{\text{eff}} \right)^{\alpha}H^{\beta} \tag{38}$$

The magnitude limits in (38) connect options and headroom to the severity that can be absorbed. $M_{0}$ denotes the no-penalty limit and $M_{\max}$ denotes the collapse threshold. Since $A \leq B$ by construction, $M_{0} \leq M_{\max}$. The constant $k > 0$ fixes the overall scale so that the limits share the units of disturbance magnitude. The exponents $\alpha > 0$ and $\beta > 0$ are elasticities that control how the limits grow with the option counts and with headroom. An elasticity expresses how strongly one quantity responds to another: here $\alpha$ governs how quickly the absorbable magnitude grows as more options become mobilisable, and $\beta$ governs how quickly it grows with headroom. These parameters can be calibrated from domain-specific incident histories or from stress testing and simulation.

The model defines a resilience score $R(M, \tau_{d})$ in two cases, where $M$ denotes the magnitude of the disturbance under assessment (the subscript $d$ is dropped for brevity). If $M_{0}\left( \tau_{d},\tau_{\text{eff}} \right) < M_{\max}\left( \tau_{d},\tau_{\text{eff}} \right)$:

$$R\left( M,\tau_{d} \right) = \begin{cases} 1, & M \leq M_{0}\left( \tau_{d},\tau_{\text{eff}} \right)\ \text{(no penalty)} \\ \max\left\{ 0,\ 1 - \frac{M - M_{0}\left( \tau_{d},\tau_{\text{eff}} \right)}{M_{\max}\left( \tau_{d},\tau_{\text{eff}} \right) - M_{0}\left( \tau_{d},\tau_{\text{eff}} \right)} \right\}, & M_{0}\left( \tau_{d},\tau_{\text{eff}} \right) < M \leq M_{\max}\left( \tau_{d},\tau_{\text{eff}} \right)\ \text{(survival band)} \\ 0, & M > M_{\max}\left( \tau_{d},\tau_{\text{eff}} \right)\ \text{(collapse)} \end{cases} \tag{39}$$

If $M_{0}\left( \tau_{d},\tau_{\text{eff}} \right) = M_{\max}\left( \tau_{d},\tau_{\text{eff}} \right)$:

$$R\left( M,\tau_{d} \right) = \begin{cases} 1, & M \leq M_{0}\left( \tau_{d},\tau_{\text{eff}} \right) \\ 0, & M > M_{0}\left( \tau_{d},\tau_{\text{eff}} \right) \end{cases}$$

Equation (39) gives $R = 1$ for $M \leq M_{0}$, a gradual taper for $M_{0} < M \leq M_{\max}$, and $R = 0$ beyond $M_{\max}$. In words: disturbances up to $M_{0}$ cost nothing and score 1. Beyond $M_{\max}$ the system collapses and scores 0. Between the two limits, $R$ falls in a straight line from 1 to 0 as the magnitude $M$ moves from $M_{0}$ to $M_{\max}$. The $\max\{0, \cdot\}$ wrapper prevents the score from going below zero.

The resilience score $R$ is defined on a 0-1 scale. It rewards configurations and organisational arrangements that can handle larger disturbance magnitudes without penalty, and penalises cases where survival requires degradation. A linear taper is a modelling choice that supports comparison and sensitivity analysis when detailed loss functions are unavailable.

---

# Part IV: Functional Information and Cost of Choice

## 17 Design-time functional information

Szostak (2003) introduced functional information to shift analysis from structural description to the rarity of configurations that achieve a specified function at a stated level in a defined context. Hazen et al. (2007) provided a system-agnostic formulation that makes the concept precise for any domain in which both function and degree of function can be scored.

Functional information, denoted by $I$, connects structural optionality to performance requirements. Option counts alone do not indicate whether many options are good enough. $I$ quantifies the sparsity of success once a performance threshold is set for a given function, supporting discussions of resilience requirements expressed as service levels, safety integrity targets, or recovery time objectives. It depends on the function-threshold pair, as well as on context, and not on structural intricacy alone.

If almost every feasible configuration meets the threshold, then $I$ is small. If only a small share succeeds, $I$ is large. If a light switch is acceptable in either state for the function "valid state", every configuration succeeds, and $I = 0$. If a throughput target is at least 10 Mb/s and all available ports exceed that, every configuration succeeds and $I = 0$. Raise the target to 800 Mb/s and only some configurations succeed, so $I > 0$. If the requirement is at least one successful backup per week, and all schedules meet that, $I = 0$. Require hourly recovery points and only a subset succeeds, so $I > 0$.

A named function $g$ specifies the capability of interest, and a performance threshold $\rho$ marks "good enough" in context, for example a safety integrity target or a service level under a named disturbance. The symbol $g$ here names the system function under assessment (for example, maintain pump control during network loss) and is unrelated to the observation mapping $g(\cdot)$ of Equation (2). The subset of feasible configurations that meet or exceed the threshold for the named function $g$ is then:

$$A_{g,\rho} = \{\, x \in \mathcal{O}^{\Delta} : x\text{ achieves performance } \geq \rho\text{ for function }g\,\} \tag{40}$$

The threshold $\rho$ can encode a required service level under disturbance, or an assurance target that must be maintained. Defining success as a set supports consistent comparison across different functions and contexts.

The share of the option set that succeeds is:

$$p_{g}(\rho) = \frac{|A_{g,\rho}|}{C} \in [0,1] \tag{41}$$

When $p_{g}(\rho)$ is small, success is rare among the feasible options, implying that search and selection are more difficult.

The **design-time** functional information for $g$ at level $\rho$ is:

$$I_{g}^{\star}(\rho) = - \log_{2}p_{g}(\rho) = \log_{2}C - \log_{2}|A_{g,\rho}| \tag{42}$$

Design-time functional information $I_{g}^{\star}(\rho)$ is measured in bits because it uses a base-2 logarithm. It can be interpreted as the number of binary decisions required to isolate a successful configuration under an uninformative search. The definition depends on the context-specific choice of $g$ and $\rho$ rather than on structural intricacy alone. Two edge cases follow directly. If every feasible configuration passes at $\rho$, then $p_{g}(\rho) = 1$ and $I_{g}^{\star}(\rho) = 0$. If exactly one feasible configuration passes, then $p_{g}(\rho) = 1/C$ and $I_{g}^{\star}(\rho) = \log_{2}C$.

## 18 Operational functional information

When time pressure is considered, the model includes a time-conditioned *effective* count:

$$\widetilde{A}_{g,\rho}\left( \tau_{d},\tau_{\text{eff}} \right) := |A_{g,\rho}|\, f_{A}\left( \tau_{d},\tau_{\text{eff}} \right) \tag{43}$$

Time pressure reduces the number of viable options available. The set $A_{g,\rho}$ plays the same role for function $g$ that the useful-variety set $A_{d}$ plays for disturbance $d$, so the effective success count $\widetilde{A}_{g,\rho}$ uses the same mobilisation fraction $f_{A}$ as the useful variety calculation. This aligns functional information with the operational assumption that only a share of options can be enacted within the shock window.

The corresponding **operational functional information** becomes:

$$I_{g}^{\text{op}}\left( \rho,\tau_{d} \right) = \log_{2}C - \log_{2}\widetilde{A}_{g,\rho}\left( \tau_{d},\tau_{\text{eff}} \right) = I_{g}^{\star}(\rho) - \log_{2}f_{A}\left( \tau_{d},\tau_{\text{eff}} \right) \tag{44}$$

Operational functional information $I_{g}^{\text{op}}$ adds an extra difficulty term that depends on time pressure. The $-\log_{2}f_{A}$ term increases as the time allowance ratio falls. This makes it explicit that a system can have many structurally feasible, successful configurations while still being hard to operate if they cannot be mobilised quickly.

In practical terms, time pressure shrinks the set of options one can actually use, adding $-\log_{2}f_{A}$ bits of difficulty. Faster effective response (higher $u$, lower structural $CP$, hence smaller $\tau_{\text{eff}}$) raises $f_{A}$ and reduces $I_{g}^{\text{op}}$. For instance, consider a water utility when a main bursts. On a normal day there are eight good ways to keep pressure up, but with only thirty minutes available only two are feasible, so choosing one that works is now harder. Detecting sooner, clear playbooks, and automation allow more options to fit any given time window, which lowers operational functional information and raises resilience.

The expression $I_{g}^{\star}(\rho) = -\log_{2}p_{g}(\rho)$ mirrors the negative-log form used for surprise in the PHAS-EAI model. Under the extended active inference regime, learning, redesign, and environment shaping can prune unhelpful configurations and lower $C$. At the same time, better sensing, decision support, automation, and headroom lift more configurations above the threshold and shorten $\tau_{\text{eff}}$, so $\widetilde{A}_{g,\rho}$ rises and $f_{A}$ rises. Both effects reduce $I_{g}^{\text{op}}$. Choices that retire dead-end architectures, strategies, tactics, tools and technologies reduce $C$, and upgrades increase $|A_{g,\rho}|$. Together these changes push $I_{g}^{\text{op}}$ down, which means fewer yes-or-no questions to find a plan that works in time.

---

# Derived Principles

Paper V derives four named principles from the formal model. Each principle follows directly from the equations and can be traced to specific formal results. The list below is condensed, and the full statements appear as block quotes beside their equations in Part I. Full proofs and formal verification are available in `analysis/appendix/`.

1. **Principle of Perceptual Uncertainty** (from Eq. 2): A PHAS perceives its environment mediated through a boundary, with internal states shaped by noisy, uncertain inputs that obscure direct observation of the world.

2. **Principle of Alignment** (from Eq. 4): A PHAS actively works to minimise the divergence between its internal model and the external world. By reducing uncertainty and aligning its model with reality, the PHAS improves its ability to infer the causes of its input.

3. **Principle of Epistemic Foraging** (from Eq. 6): A PHAS selects actions that maximise the expected accuracy of future input, not by altering internal beliefs but by reducing the ambiguity of external input.

4. **Principle of Coupled Adaptation** (from Eqs. 7-8): A PHAS co-evolves with its environment, wherein the environment minimises environmental surprise by affording specific actions, guiding the system towards mutually predictable interactions.

Equations (12) and (14) formalise shared expectations and authority weights without a named principle of their own. Their consequences appear as formal results and hypotheses in the Key Findings part below, in particular Theorem T5.5-5 and hypothesis H10 on authority-weight asymmetry.

---

# Key Findings from Model Analysis

The formal models developed above provide a common analytical vocabulary for complexity, resilience, functional information, and inference dynamics. The emphasis is on why performance often looks stable until it does not, why VSEs can be resilient in specific regimes, and why attention and authority behave like dependability variables. Formal proofs, parameter sensitivity analyses, and executable verification artefacts that substantiate each claim are in `analysis/appendix/` and `analysis/section5_*/setup/lean/`.

## Complexity rises, and it rises in bursts

Options combine multiplicatively across factors and subsystems. If two weakly coupled subsystems have option counts $C_A$ and $C_B$, the combined count is approximately $C_{A \| B} \approx C_A \cdot C_B$ (Theorem A3 in `analysis/section5_1/`, where appendix theorems carry letter-number labels, unlike the T5.x-y labels used for chapter theorems). This means that introducing a new lever with $k$ alternatives ($k$ here is simply the number of alternatives, not the scale constant of Equation 38) multiplies the option count by $k$, producing a jump of $\log_2 k$ bits in $\log_2 C$, the option count expressed in bits. Bursts also arise from constraint changes rather than option growth alone: shifting $K(\ell)$ changes $\mathcal{O}^{\Delta}(\ell)$ and therefore $C(\ell)$ without requiring any change in the underlying configuration space $X$.

Operationally, complexity bursts are experienced as a sudden loss of competence. Functional information provides the formal mechanism: when $C$ grows or $|A_{g,\rho}|$ shrinks, $I_g^*$ increases and search becomes harder. Operational functional information $I_g^{\text{op}}$ adds a time-pressure term $-\log_2 f_A$ that can produce sharp increases in effective difficulty even when the nominal capability of the team appears unchanged.

![Step changes in effective decision burden and mobilisation under boundary and constraint events. Each plateau represents a period of operational stability, and each jump corresponds to a structural change.](<Analytical Models/figures/fig-complexity-bursts.png>)

**H1 (Bursty complexity).** Complexity growth in interdependent socio-technical systems manifests as step changes in mobilisation difficulty rather than smooth degradation. Bursts in complexity potential $CP$ or boundary constraints cause bursts in operational functional information $I_g^{\text{op}}$ and observable drops in response performance.

**H2 (Joint intervention).** Interventions that jointly reduce total option count $C$ and increase the successful option share $|A_{g,\rho}|/C$ produce larger resilience gains than interventions that affect only one term. The appendix provides a formal proof of the additivity of intervention effects in the log domain (Theorem C2).

## The relative resilience advantage of VSEs is real and bounded

VSEs can mobilise a larger fraction of their option set under fast disturbances because their effective mobilisation time $\tau_{\text{eff}}$ is often shorter (fewer handoffs, simpler governance). This advantage is real but bounded: limited headroom $H$ and survivable variety $B$ mean that VSEs collapse earlier as disturbance magnitude increases. Theorem T5.2-4 proves, under continuity conditions, the existence of a parity boundary: a disturbance timescale $\tau_d^*$ at which the advantage difference $\Delta R$ equals zero for a given magnitude, beyond which the advantage reverses.

![Resilience advantage field with parity boundary and threshold curves. Warm colours indicate faster mobilisation dominates, cool colours indicate larger reserves dominate. The zero contour marks the parity boundary $\Delta R = 0$.](<Analytical Models/figures/fig-resilience-advantage.png>)

**H3 (VSE advantage is regime-dependent).** The VSE resilience advantage is positive for fast disturbances and moderate magnitudes when $r = \tau_d / \tau_{\text{eff}}$ favours rapid mobilisation, but becomes negative beyond a bounded magnitude band as $M$ approaches or exceeds the VSE $M_{\max}$ due to limited headroom and survivable variety.

**H4 (Burst-induced regime shift).** A burst increase in complexity potential or coordination drag can shift an organisation abruptly from an apparently resilient regime into degradation or collapse by increasing $\tau_{\text{eff}}$ and operational functional information, even when the nominal capability of individuals appears unchanged.

## Resilience is mobilisable variety under time pressure

Under time pressure, only a fraction of options can be mobilised. The time allowance ratio $r = \tau_d / \tau_{\text{eff}}$ determines this fraction. Structural drag from complexity potential inflates response time through stage-specific sensitivities (Theorem T5.3-1). Human skill shortens the inflated time, but the speed-up is bounded by $\lambda_\tau$ (Theorem T5.3-3). Designed cognitive reserve $h$ provides a floor on cognitive headroom that holds even when skill varies (Theorem T5.3-4).

**H5 (Time pressure reduces realised resilience).** For disturbances of equal magnitude, shorter timescale $\tau_d$ reduces realised resilience by lowering mobilisation fractions even if the feasible option set is unchanged.

**H6 (Diminishing returns from expertise).** In high-drag environments, increased expertise produces diminishing returns on response outcomes because the skill speed-up is bounded by $\lambda_\tau$ and cannot remove governance and interface-imposed delays embedded in structural drag.

**H7 (Designed reserve outperforms experience investment).** Interventions that increase design-preserved cognitive reserve $h$ yield more reliable improvements in time-bounded mobilisation and resilience than interventions that attempt to increase experience alone, because $h$ protects cognitive headroom even under high interaction demand.

## Functional information is the cost of choice

Design-time functional information $I_g^*(\rho)$ measures how many binary decisions are required to identify a satisfactory configuration. Raising the performance threshold $\rho$ can only shrink $A_{g,\rho}$ (Theorem T5.4-1), and the count $|A_{g,\rho}|$ is piecewise constant between adjacent performance levels, so $I_g^*$ increases in discrete jumps at thresholds (Theorem T5.4-2). Reducing the time allowance ratio increases $I_g^{\text{op}}$ (Theorem T5.4-3).

**H8 (Operational functional information predicts outcomes better than raw complexity).** Operational functional information $I_g^{\text{op}}(\rho, \tau_d)$ predicts resilience outcomes better than raw complexity $C$ alone, particularly when disturbances are fast or when performance thresholds are raised, because it incorporates both the sparsity of success and time-bounded mobilisation.

## Attention, authority, and shared expectations are dependability variables

Perception and communication are noisy channels (Equations 2 and 9). The precision of these channels, defined as $1/\sigma^2$ where $\sigma^2$ is the variance of the noise $\omega$ in Equations (2) and (9) (unrelated to the time multiplier $\sigma_{\tau}$), determines how strongly signals drive belief update: low-noise channels are high-precision channels and are trusted more. Higher precision improves expected accuracy monotonically, that is, always in the same direction, so more precision never makes accuracy worse (Theorem T5.5-4). Shared expectations $\Phi$ for a single peer lie within the convex hull of $\mu$ and $f(\psi)$ when $\gamma \in [0,1]$, meaning $\Phi$ always lands between the agent's own belief and the peer contribution and never outside them (Theorem T5.5-2). Increasing affordance for a desired action strictly reduces free energy, making the action more likely (Theorem T5.5-3). Authority-weight asymmetry between agents generates coordination friction that grows steadily with the weight gap $|\gamma_A - \gamma_B|$ (Theorem T5.5-5).

Two practical constructs follow, defined in Paper V and re-purposed there from Ramstead et al. (2016) as prescriptive tools. *Regimes of Attention* are the environmental features, such as social cues, architectural designs, and digital interfaces, that naturally steer focus towards the information most pertinent for reducing uncertainty. They function as a guiding scaffold, keeping salient signals readily detectable within a complex operational landscape. *Patterned Practices* are the regular, often ritualised, interactions with these environmental cues. By engaging in Patterned Practices, agents repeatedly interface with systems that embed crucial knowledge, and internalise these patterns. When the practices are shared among team members, they foster joint attention and synchronisation of internal models, promoting shared intention. Over time, this internalisation prompts agents to act in accordance with collective expectations, even in the absence of direct cues.

**H9 (Regimes of attention reduce drift).** Regimes of attention that increase the salience and precision of dependability signals reduce drift away from resilience-improving actions under workload pressure, leading to faster detection and more consistent escalation.

**H10 (Authority-weight asymmetry predicts friction).** Authority-weight asymmetry across stakeholders, expressed as heterogeneous $\gamma_i$ values in the construction of $\Phi$, predicts coordination friction and decision reversals across organisational boundaries, which manifests as disproportionate growth in decision latency during complex incidents.

## Empirical alignment and threshold behaviour

Systems engineering capability reduces complexity potential and baseline stage times and preserves cognitive reserve $h$. The experience effect on $\tau_{\text{eff}}$ is bounded by $\lambda_{\tau} \cdot \tau$ (Theorem T5.6-1). As $CP$ grows, the sensitivity of the time allowance ratio to skill, written $|\partial r / \partial u|$ (how much $r$ improves for a small increase in $u$), decreases, meaning additional expertise produces smaller improvements in the time allowance ratio (Theorem T5.6-2). A structural dominance threshold exists: when aggregate complexity potential $CP$ reaches a threshold $CP^*$, structural interventions that reduce $CP$ produce larger gains than the full experience effect (Theorem T5.6-3). Step changes in $CP$ produce step drops in $r$, connecting burst dynamics to abrupt performance regime shifts (Theorem T5.6-4).

**H11 (SE capability dominates in high complexity).** In high-complexity work, systems engineering capability has a stronger association with performance than prior experience because it reduces complexity potential and baseline stage times and preserves cognitive reserve $h$, while skill-driven speed-up is bounded.

**H12 (Experience effect weakens after bursts).** Prior experience is associated with performance in low-complexity work through improved $u(E, MF)$ and faster effective mobilisation, but this association weakens after bursts in complexity potential and interface churn that increase structural drag and decision latency.

## Patterns and digital engineering interventions change the same underlying quantities

Modelling patterns (proven architectural templates, standard interface contracts, codified response playbooks) act as operators on the feasible set. Adding constraints, restricting choices, and coarsening $\varphi$ are complexity-non-increasing (Theorem T5.7-1). The conditional success-share theorem (Theorem T5.7-2) formalises that if an intervention increases the share of successful configurations, then $I_g^{*\prime} \leq I_g^*$, where the prime marks the value of $I_g^*$ after the intervention: functional information can only fall or stay the same.

Joint interventions produce larger reductions in operational functional information than any single-channel intervention alone (Theorem T5.7-3). The reduction decomposes additively in the log domain:

$$\Delta I_g^{\text{op}} = (-\log_2 \alpha) + \log_2 \beta + \log_2 \gamma$$

where $\alpha \in (0,1)$ is the complexity reduction factor ($C \mapsto \alpha C$), $\beta \geq 1$ is the success expansion factor ($A \mapsto \beta A$), and $\gamma \geq 1$ is the mobilisation improvement factor ($f_A \mapsto \gamma f_A$). In this decomposition $\alpha$, $\beta$, and $\gamma$ are intervention factors defined here, distinct from the elasticity exponents of Equation (38) and the authority weights of Equations (12) and (14). The arrow notation $C \mapsto \alpha C$ reads "$C$ is replaced by $\alpha C$".

Theorem T5.7-4 provides the formal bridge between the PHAS-EAI inference model and the resilience model: under stated assumptions, improving inference precision raises the time allowance ratio $r$ and mobilisation fractions.

**H13 (Patterns reduce functional information without reducing resilience).** Modelling patterns that encode constraints and substitutability reduce total optionality $C$ while increasing the proportion of successful configurations $|A_{g,\rho}|/C$, lowering functional information burden without reducing resilience, provided that useful and survivable variety are preserved.

**H14 (Machine-readable traceability reduces noise and improves coordination).** Machine-readable traceability and evidence chains reduce effective noise $\omega$ and improve observation mapping $g(\cdot)$, reducing surprise and improving coordination by stabilising shared expectations and shortening detection, decision, and execution cycles.

## Leverage points for intervention design

The table below maps each model lever to its directional effects and gives illustrative examples of interventions that would manipulate that lever. Every directional effect listed corresponds to a proved monotonicity result or a stated assumption. The table is organised into four groups.

### Configuration-space levers

| Lever | If moved up | If moved down | Intervention examples |
|---|---|---|---|
| **Hard constraints $K$** | Prunes infeasible and unsafe configurations. Reduces $C$ and failure surface if constraints target failure modes. If overly restrictive, can also reduce useful variety. | Expands $C$, increases search space and failure surface, increases coordination burden, can increase brittleness if unsafe modes re-enter feasibility. | Contract tests, policy-as-code gates, codified safety and security invariants, interface compliance checks |
| **Decision resolution $\Delta$ and distinctness map $\varphi$** | Coarser resolution collapses near-duplicates, reduces counted $C$, reduces cognitive burden. Risk of hiding materially important distinctions if bins are too coarse. | Finer resolution increases counted $C$, increases modelling and decision burden, increases apparent complexity and coordination load. | Standardise categories and acceptance bands, define equivalence classes for options, adopt shared binned KPIs |
| **Boundary degrees of freedom $X_{\text{boundary}}$** | Wider boundary increases coordination scope and multiplies option space through interdependence. Can increase adaptability, tends to increase drag without parallel observability and pattern investments. | Narrower boundary reduces modelling and coordination burden but increases risk of unmanaged externalities and surprise. | Scope discipline for interfaces, explicit responsibility boundaries, interface ownership, dependency caps |

### Mobilisation-time levers

| Lever | If moved up | If moved down | Intervention examples |
|---|---|---|---|
| **Complexity potential $CP_i$** | Increases stage times through drag, reduces $r$, collapses $\widetilde{A}$, $\widetilde{B}$, increases brittleness under fast disturbances. | Reduces drag, increases mobilisation, improves resilience margins. | Interface standardisation, change-rate governance, supplier interface control, stabilise vocabularies and data definitions |
| **Baseline detection time $\tau_{\text{detect}}^0$** | Slower detection reduces effective window and collapses mobilisation fraction. | Faster detection expands effective window and improves mobilisation. | Instrumentation, alert quality improvements, telemetry with clear semantics, automated triage |
| **Baseline decision time $\tau_{\text{decide}}^0$** | Longer decision baselines increase collapse risk in fast disturbances, especially in multi-actor governance. | Faster decisions increase mobilisation and reduce degradation time. | Pre-authorised actions, clarified decision rights, incident decision playbooks, escalation simplification |
| **Baseline execution time $\tau_{\text{execute}}^0$** | Slow execution reduces ability to recover inside $\tau_d$, increases degradation and collapse probability. | Faster execution increases recovery likelihood and reduces outage duration. | Automated deployment, rollback capability, rehearsed recovery routines, standard operating procedures |
| **Stage sensitivities $\gamma_{\text{det}}, \gamma_{\text{dec}}, \gamma_{\text{exe}}$** | Higher sensitivity makes $CP$ more damaging, raising drag and slowing response. | Lower sensitivity reduces how strongly complexity harms response, improving stability. | Reduce cross-team handoffs, stabilise interfaces, reduce exception handling, standardise response steps |
| **Skill factor $u(E,MF)$** | Increases cognitive headroom and reduces effective mobilisation time, but only up to the bound set by $\lambda_\tau$. | Reduces headroom and slows mobilisation, increasing brittleness under time pressure. | Training, rehearsal, peer learning, targeted capability building for high-demand tasks |
| **Designed cognitive reserve $h$** | Protects attention and decision capacity under stress even when skill varies, improving resilience in thin teams. | Increases vulnerability to cognitive overload and drift, increases decision errors under pressure. | Automation, checklists, pre-authorised actions, tooling that removes routine cognitive load |
| **Physical headroom $H_{\text{phys}}$** | Raises disturbance magnitude limits $M_0$ and $M_{\max}$, improves survivability. | Lowers magnitude limits, causes earlier degradation and collapse. | Spare capacity, buffer budgets, delegated authority, redundancy, surge staffing agreements |

### Information and inference levers

| Lever | If moved up | If moved down | Intervention examples |
|---|---|---|---|
| **Performance threshold $\rho$** | Higher $\rho$ shrinks $\lvert A_{g,\rho}\rvert$, increases functional information, increases brittleness if not paired with pattern investments. | Lower $\rho$ increases $\lvert A_{g,\rho}\rvert$, reduces functional information, but relaxes required performance and assurance. | Mode-dependent service levels, staged degradation policies, explicit function prioritisation |
| **Observation mapping $g(\cdot)$** | More informative sensing reduces ambiguity, reduces detection delays, improves belief update and coordination. | Less informative sensing increases ambiguity, increases reliance on priors and heuristics, increases drift and delay. | Better telemetry, consistent semantic definitions, traceability from model elements to monitored signals |
| **Noise $\omega$** | Higher noise increases uncertainty, increases divergence in inference, increases miscoordination. | Lower noise increases confidence, improves coordination and response speed. | Reduce conflicting metrics, improve data quality, standard incident reporting formats |
| **Traceability and machine-readable evidence chains** | Improves observation mapping, reduces noise, stabilises shared expectations, reduces decision rework and integration surprises. | Weak traceability increases ambiguity, increases reliance on informal memory, increases drift and rework. | Model-to-test-to-deploy-to-telemetry linking, automated evidence capture, auditable pipelines, shared artefact repositories |

### Coordination and governance levers

| Lever | If moved up | If moved down | Intervention examples |
|---|---|---|---|
| **Affordance $p(a)$** | Higher affordance for desired actions makes them more likely under pressure. | Lower affordance makes desired actions harder or less legitimate, encouraging drift. | Make resilience actions default and pre-approved, tool support that reduces bureaucratic friction |
| **Communication $c_{\text{in}}, c_{\text{out}}$** | More structured, evidence-backed communication improves peer inference and mutual predictability. | Ambiguous communication increases misinterpretation and coordination delay. | Structured escalation templates, shared vocabularies, evidence attachments, time-boxed communication loops |
| **Authority weights $\gamma$, $\gamma_i$ in $\Phi$** | Higher weight drives faster convergence to peer expectations if peers are reliable. Can propagate peer error if not. | Lower weight preserves autonomy and diversity, can reduce coordination efficiency and increase divergence. | Governance design, decision rights, regulator or integrator authority calibration |
| **External state scope $\eta$** | Broader scope increases potential accuracy but increases hypothesis space and cognitive burden unless observability scales. | Narrower scope reduces burden but increases risk of unmodelled disturbances and surprise. | Explicit "known unknowns", boundary monitoring commitments, scoped assurance cases |
| **Action set (the agent's repertoire of available actions)** | Larger action set increases adaptability but increases choice burden and inconsistency risk without constraints. | Smaller action set reduces choice burden and increases consistency but can reduce useful variety under diverse disturbances. | Standard response playbooks, controlled automation, limiting response paths to tested safe operations |

The intervention tables serve two functions. The first is *intervention candidate specification*: which levers are relevant, with predicted directional effects grounded in formal monotonicity results. The second is *evidence design*: directional effects define what counts as "movement" on the intended lever, shifting the evidentiary burden from outcome measurement to lever measurement, which is observable in routine operational data. The non-monotone levers (boundary degrees of freedom, authority weights, action set scope) are identified explicitly and require case-specific calibration rather than blanket directional recommendations.

---

# Connections to Analysis and Simulation

## Hypotheses

The formal model generates fourteen testable hypotheses (H1 through H14), covering bursty complexity growth, the bounded resilience advantage of VSEs, time-pressure effects on mobilisation, the predictive power of operational functional information, the role of attention and authority weights as dependability variables, empirical alignment with systems engineering capability data, and the mechanism by which modelling patterns and digital engineering interventions change the same underlying quantities.

Full hypothesis statements, predictions, and supporting theorems are in `analysis/chapter5/section5_1.md` through `analysis/chapter5/section5_8.md`.

## Formal proofs

Theorems T5.2-4, T5.3-1, T5.3-3, T5.3-4, T5.4-1 through T5.4-4, T5.5-2 through T5.5-5, T5.6-1 through T5.6-4, and T5.7-1 through T5.7-4 establish formal properties of the model. These include monotonicity of complexity under constraint changes, boundedness of skill effects, floor guarantees from designed cognitive reserve, threshold sensitivity of functional information, convexity of shared expectations, affordance reduction of free energy, precision-accuracy monotonicity, authority-weight friction, diminishing returns from expertise under structural drag, structural dominance thresholds, and joint intervention additivity.

Lean 4 proofs are in `analysis/section5_*/setup/lean/`. Proof writeups are in `analysis/section5_*/writeup/`. A theorem inventory is in `analysis/appendix/`.

## Simulation

The agent-based simulation in `simulation/phas_eai/` implements the model with five extensions, ordered by implementation priority:

1. **Designed cognitive reserve** ($h$): minimum sensory floor per agent.
2. **Regimes of Attention**: mutable environment salience (niche construction).
3. **Dynamic shared expectations** ($\Phi$): per-agent, evolving authority weights.
4. **Patterned Practices**: periodic belief synchronisation at interval $P$.
5. **Disturbance episodes**: target relocation at $T_{\text{shock}}$, resilience scoring.

The baseline active inference simulation from Kaufmann et al. (2021) is in `simulation/kaufmann/` for direct comparison. The mapping between Kaufmann simulation constructs and PHAS-EAI model quantities is documented in Table 26 of the dissertation.

## Figures

Computational figures illustrating model behaviour are generated by the analysis scripts and stored in `analysis/section5_*/result/`. Key figures include complexity burst trajectories, resilience advantage heatmaps, response time drag curves, mobilisation fraction plots, threshold shrinkage diagrams, operational functional information under varying time pressure, the PHAS-EAI assurance loop schematic, precision-accuracy demonstrations, experience effect schematics, sensitivity decay curves, patterns-as-operators diagrams, and joint intervention bar charts.
