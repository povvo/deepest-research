# Method Selection and Design Coherence

Use this reference to choose, compare, or audit a research design. Select methods from the intended conclusion and evidence conditions, not from superficial question words, fashionable tools, or arbitrary sample thresholds.

## Contents

1. Coherence chain
2. Inferential targets
3. Design families
4. Causal identification
5. Qualitative design
6. Evidence synthesis
7. Computational and engineering design
8. Mixed-methods integration
9. Sampling and sample-size logic
10. Decision matrix
11. Downgrade and fallback rules
12. Common selection failures

## 1. Coherence Chain

A defensible plan makes this chain explicit:

> decision need → contribution → research question → inferential target → design → sampling or cases → measures or evidence → analysis → validity checks → allowable conclusion

Audit every arrow. A method can be competently executed yet still be wrong for the intended claim.

Before naming a method, write:

- **Decision:** what action or knowledge choice will the result inform?
- **Target:** what quantity, mechanism, meaning, pattern, artefact, or evidence state is being learned?
- **Claim:** what sentence should the study be able to defend?
- **Counterclaim:** what plausible rival should the design distinguish?
- **Evidence condition:** what observations would change the conclusion?

## 2. Inferential Targets

| Intended target | Typical question | Suitable evidence | Common overclaim |
| --- | --- | --- | --- |
| Description | What exists, how often, for whom, and where? | Representative or clearly bounded observations | Generalising beyond frame or period |
| Interpretation | How do participants understand or experience X? | Context-rich cases and reflexive analysis | Treating themes as population prevalence |
| Association | How do X and Y covary? | Measured variables with confounding analysis | Calling association an effect |
| Prediction | How accurately can Y be predicted in target use? | Deployment-relevant train/test evidence | Treating predictive importance as causality |
| Causation | What is the effect of intervening on X? | Randomisation or credible identification | Ignoring counterfactual and interference |
| Mechanism | Through what process might X produce Y? | Process evidence, mediation, tracing, experiments | Inferring mechanism from end-state correlation |
| Evaluation | Did a programme work, for whom, how, and at what cost? | Outcome, implementation, context, comparison | Equating activity with impact |
| Construction | Can an artefact meet specified requirements? | Design rationale plus verification and validation | Treating a prototype demo as real-world effectiveness |
| Synthesis | What does the evidence base support and where is it uncertain? | Transparent retrieval, appraisal, and synthesis | Calling search absence evidence of absence |
| Theory development | What conceptual model explains observed patterns? | Iterative cases, comparison, negative evidence | Presenting a plausible story as tested theory |

A study may have multiple targets, but name the primary one and prevent secondary aims from silently changing the design.

## 3. Design Families

### Descriptive and prevalence designs

Use cross-sectional surveys, censuses, registries, observation, structured content analysis, or administrative data when the target is distribution or frequency.

Require:

- a defined population and sampling frame;
- inclusion period and coverage;
- nonresponse and missingness analysis;
- weights or calibration when used;
- precision intervals, not only point estimates;
- limits on temporal and geographic generalisation.

### Associational and explanatory observational designs

Use cohort, panel, case-control, longitudinal, naturalistic, comparative-case, or observational modelling when randomisation is unavailable.

Require:

- temporal ordering where relevant;
- a causal or explanatory diagram even if the claim remains associational;
- confounder, collider, mediator, and selection reasoning;
- measurement-error and missing-data plans;
- sensitivity analysis and alternative specifications;
- cautious language tied to assumptions.

### Experimental and quasi-experimental designs

Use randomized, factorial, crossover, cluster, single-case, interrupted time-series, regression-discontinuity, difference-in-differences, instrumental-variable, matching, or synthetic-control designs only when their assumptions fit the setting.

Require:

- intervention, comparator, outcome, timing, and estimand;
- assignment or identification mechanism;
- contamination, spillover, attrition, and noncompliance plan;
- treatment fidelity and manipulation checks;
- pre-specified primary analysis;
- diagnostic or falsification checks for identifying assumptions.

### Qualitative and interpretive designs

Choose by the kind of understanding sought:

| Need | Candidate approach | Design emphasis |
| --- | --- | --- |
| Lived experience | Phenomenological approaches | Experience, positionality, depth |
| Social process or theory generation | Grounded-theory family | Iteration, theoretical sampling, constant comparison |
| Meaning patterns across a corpus | Reflexive thematic analysis | Interpretive engagement, reflexivity, coherent themes |
| Predefined framework application | Framework or directed content analysis | Transparent codebook, fit and exception handling |
| Language, power, or construction | Discourse or conversation analysis | Context, interaction, rhetorical function |
| Culture and practice in setting | Ethnography | Prolonged engagement, field relations, situated observation |
| Bounded complex instance | Case study | Multiple evidence sources and case boundaries |
| Change over time or life course | Narrative approaches | Sequence, identity, plot, context |
| Mechanism in a case | Process tracing | Competing explanations and diagnostic evidence |

Do not select a qualitative method solely because the question starts with “how” or “why.” Do not claim saturation as a universal numeric threshold. Justify stopping through information power, theoretical sufficiency, code meaning, corpus coverage, or explicit operational criteria appropriate to the approach.

### Predictive and machine-learning designs

Use when prospective performance in a target environment is the primary claim.

Require:

- target use, decision threshold, and cost of errors;
- time-, site-, person-, or group-safe splitting;
- leakage prevention;
- simple and domain-relevant baselines;
- calibration, discrimination, uncertainty, and subgroup evaluation;
- external or temporal validation when deployment is claimed;
- drift, retraining, monitoring, and model-update policy;
- distinction between explanation of predictions and causal explanation.

## 4. Causal Identification

A causal plan is incomplete until it defines:

1. treatment or exposure;
2. outcome;
3. target population and unit;
4. time zero, follow-up, and treatment versions;
5. counterfactual contrast and estimand;
6. interference and consistency assumptions;
7. assignment or identification strategy;
8. pre-treatment confounders and prohibited controls;
9. missingness, attrition, and noncompliance;
10. sensitivity and falsification analyses.

Use a directed acyclic graph or equivalent causal model when it clarifies adjustment and timing. A diagram does not prove causality; it exposes assumptions.

Downgrade to associational language when:

- temporal order is unknown;
- key common causes are unmeasured with no credible strategy;
- selection into observation is unexplained;
- the comparator is undefined;
- the method estimates prediction rather than intervention;
- assumptions cannot be defended or tested indirectly.

## 5. Qualitative Design

Specify:

- epistemological and theoretical orientation where it affects interpretation;
- researcher role, positionality, and relationship to participants;
- case or participant selection logic;
- setting, access, language, translation, and power relations;
- data-generation method and why it fits;
- iterative memoing, code or theme development, and analytic decisions;
- negative cases, contradictions, rival interpretations, and boundary cases;
- credibility practices suited to the approach;
- audit trail and evidence excerpts;
- participant, peer, or community validation only when methodologically appropriate.

Inter-rater agreement may support a stable deductive codebook, but it is not a universal quality criterion for reflexive or constructivist analysis.

## 6. Evidence Synthesis

Choose the synthesis family by purpose:

| Purpose | Candidate design |
| --- | --- |
| Exhaustive answer to a focused effectiveness or association question | Systematic review, with meta-analysis if defensible |
| Map concepts, methods, populations, or gaps | Scoping review or evidence map |
| Rapid decision under deadline | Rapid review with explicit shortcuts |
| Integrate qualitative findings | Qualitative evidence synthesis or meta-ethnography |
| Examine theory and context-mechanism-outcome patterns | Realist review |
| Survey broad mixed literature | Integrative review |
| Maintain a changing evidence base | Living review with update triggers |
| Locate prior work for a proposal | Structured literature or competitive-landscape search, not automatically a systematic review |

Do not label a review “systematic” unless protocol, comprehensive search, selection, appraisal, synthesis, and reporting are sufficiently transparent to reproduce.

## 7. Computational and Engineering Design

### Computational or simulation studies

Specify:

- model purpose and abstraction boundary;
- source and calibration data;
- assumptions, parameter ranges, and initial conditions;
- verification of implementation versus validation against reality;
- uncertainty and sensitivity analysis;
- benchmark and stress scenarios;
- reproducible environment and compute;
- domain-of-validity statement.

### Engineering and design-science studies

Separate:

- **requirements** — what the artefact must do;
- **design rationale** — why this approach may satisfy them;
- **verification** — whether it was built to specification;
- **validation** — whether it solves the stakeholder problem in context.

Use acceptance criteria, test matrices, safety margins, failure-mode analysis, usability or field evaluation, and traceability from requirements to evidence.

## 8. Mixed-Methods Integration

Use mixed methods only when one evidence form cannot answer the decision need alone.

Define:

- integration purpose: triangulation, complementarity, explanation, development, expansion, or contradiction;
- sequence: concurrent, exploratory sequential, explanatory sequential, embedded, or multiphase;
- priority of components;
- where integration occurs: design, sampling, data collection, analysis, or interpretation;
- joint display or explicit meta-inference;
- response when components disagree.

Two methods run side by side without integration are parallel studies, not a coherent mixed-methods design.

## 9. Sampling and Sample-Size Logic

Match justification to the claim:

- **Prevalence or mean:** target precision, confidence, design effect, expected response, finite population.
- **Comparative or causal:** minimally important effect, variance, allocation, clustering, attrition, multiplicity, power or decision value.
- **Prediction:** events or cases relative to model complexity, prevalence, validation size, calibration precision, expected shift.
- **Qualitative:** information power, case heterogeneity, theoretical sampling, analytic depth, corpus coverage.
- **Evidence synthesis:** expected yield, source diversity, date/language coverage, screening reliability.
- **Engineering:** requirement and failure-mode coverage, operating envelope, reliability target.
- **Simulation:** Monte Carlo error, parameter-space coverage, rare-event frequency, convergence.

Do not infer method quality from sample size alone. A large biased sample can estimate the wrong target precisely.

## 10. Decision Matrix

At Standard or Protocol depth, score viable designs from 0 to 3:

- 0 — incompatible or unavailable;
- 1 — serious weakness;
- 2 — workable with mitigation;
- 3 — strong fit.

Use criteria and disclose weights:

| Criterion | Default weight |
| --- | ---: |
| Claim and inferential fit | 3 |
| Construct and measurement validity | 2 |
| Internal or interpretive validity | 3 |
| External and contextual fit | 2 |
| Ethics and stakeholder burden | 3 |
| Data or participant access | 3 |
| Analysis transparency and reproducibility | 2 |
| Time, cost, skills, and infrastructure | 2 |
| Robustness and contingency options | 2 |

Change weights for the user’s decision. Record disqualifying constraints separately; a weighted total must not override an ethical or identification failure.

## 11. Downgrade and Fallback Rules

Use these repairs:

- causal → associational when identification fails;
- population claim → bounded sample or case claim when representativeness fails;
- effectiveness claim → feasibility or implementation claim when outcomes are unavailable;
- automated classification → human-assisted coding when validation fails;
- systematic review → structured or rapid review when coverage cannot be achieved;
- deployment claim → prototype or internal-validation claim when external testing is absent;
- novelty claim → candidate contribution when search coverage is incomplete;
- comprehensive scope → staged pilot when access, budget, or time is insufficient.

State what evidence would permit the stronger claim later.

## 12. Common Selection Failures

Reject or repair:

- choosing qualitative versus quantitative from question wording alone;
- treating mixed methods as a compromise rather than an integration design;
- using synthetic participants because human access is difficult;
- equating a tool’s availability with methodological validity;
- using a predictive model to support an intervention claim;
- relying on a single metric without decision thresholds or error costs;
- selecting a fashionable method before defining the target;
- forcing hypotheses into exploratory or interpretive work;
- importing sample-size folklore across designs;
- hiding infeasibility behind an overcomplicated multi-stage plan.

## Retained Quick Selector from the Original Bundle

> This compact selector is retained for compatibility. Treat numeric thresholds and tool recommendations as prompts for method-specific justification, not universal rules. The coherence and identification rules above take precedence.

## Decision Tree: Method Selection for Scientific Research
**Version**: 1.0.0  
**Focus**: Guiding researchers between Qualitative, Quantitative, and Mixed-Methods paths  

This decision tree helps scientific and social science researchers select the optimal research design based on their research questions, sample sizes, and resource constraints.

---

### 1. Visual Overview
```
                     [ Start: Research Goal ]
                                |
             Is the goal to explore/understand OR verify/predict?
                               / \
               (Explore / Latent)   (Verify / Predict)
                             /         \
                [ Qualitative Path ]    [ Quantitative Path ]
                         |                        |
             Is text data unstructured?    Are variables measurable?
                       /   \                      /   \
                    (Yes)  (No)                 (Yes)  (No)
                     /       \                   /       \
         [Thematic Analysis] [Content]    [Statistical] [Silicon Sampling]
                             [Analysis]    [Modeling]   [AI Simulation]
```

---

### 2. Logical Decision Rules

#### Rule 1: Exploratory vs. Explanatory Framing
- If your research question starts with **"How..."**, **"Why..."**, or **"What is the meaning of..."**, proceed to the **Qualitative Path** (Section 3).
- If your research question starts with **"Does..."**, **"To what extent..."**, or **"What is the effect of $X$ on $Y$..."**, proceed to the **Quantitative Path** (Section 4).

#### Rule 2: Sample Size & Representation (N)
- If your sample size is small ($N < 50$ depth interviews or focus groups) but rich in contextual narrative, select **Reflexive Thematic Analysis** or **Phenomenological Analysis** [414, 557].
- If your sample size is moderate ($50 < N < 500$) and you need to generalize patterns, select **Deductive Content Analysis** or **Structured Survey Research**.
- If your sample size is massive ($N > 10,000$ social media posts, comments, or literature abstracts), select **Automated Text Classification & Secondary Data Analysis** [1, 203].

---

### 3. Qualitative Method Selector

```markdown
1. Are you analyzing lived human experiences?
   ├── YES ──> Interpretive Phenomenological Analysis (IPA)
   └── NO  ──> Proceed to Question 2

2. Is your objective to generate a new conceptual framework from raw data?
   ├── YES ──> Grounded Theory (using open and axial coding) [557]
   └── NO  ──> Proceed to Question 3

3. Do you have a pre-existing theoretical framework or codebook?
   ├── YES ──> Deductive Coding / Directed Qualitative Content Analysis
   └── NO  ──> Reflexive Thematic Analysis (inductive-focused)
```

---

### 4. Quantitative & Automated Method Selector

```markdown
1. Do you have structured, tabular, or numerical variables?
   ├── YES ──> Statistical Modeling (OLS Regression, GLM, ANOVA) [251, 439]
   └── NO  ──> Proceed to Question 2

2. Do you have massive volumes of unstructured text data?
   ├── YES ──> Automated Text Mining (Sentiment Analysis, Opinion Mining) [1, 29]
   └── NO  ──> Proceed to Question 3

3. Are you evaluating human behavioral responses but have extreme cost/logistical constraints?
   ├── YES ──> Silicon Sampling (Multi-agent AI survey simulation) [248]
   └── NO  ──> Traditional Human Survey Research (CASM-appraised) [148]
```
