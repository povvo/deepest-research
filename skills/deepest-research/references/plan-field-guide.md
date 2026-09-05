# Research Plan Field Guide

Use this reference before Protocol-depth output, saved files, machine-readable plans, or comprehensive plan audits.

## Contents

1. Depth profiles
2. Epistemic status grammar
3. Required plan sections
4. Research-family extensions
5. Roadmap and decision gates
6. Audit evidence
7. Completion tests

## 1. Depth Profiles

### Rapid

Use when the user needs direction rather than a protocol. Include:

- decision and scoped question;
- key assumptions and unknowns;
- recommended design and why;
- data or evidence needed;
- critical validity, ethics, and feasibility risks;
- next decision gate.

Do not hide uncertainty to stay brief.

### Standard

Use by default. Include all 16 Output Contract sections in `SKILL.md`, compare viable designs, specify the protocol enough to expose missing access or assumptions, and provide a staged roadmap.

### Protocol

Use for preregistration, funding, review, delegation, or implementation handoff. Include:

- stable identifiers and version/date;
- complete eligibility, sampling, measurement, data, and analysis rules;
- current-rule checks;
- amendments and deviations policy;
- machine-readable JSON when requested;
- evidence ledger where search or sourcing is in scope;
- lint report and explicit `NOT RUN` checks.

## 2. Epistemic Status Grammar

Use labels consistently:

| Status | Meaning | Required support |
| --- | --- | --- |
| `Verified` | Inspected source or objective run evidence supports the statement | Source or command plus exact locator |
| `Inference` | Reasoned conclusion from verified inputs | Supporting inputs and reasoning |
| `Assumption` | Temporary design choice made to proceed | Consequence and verification step |
| `Proposal` | Future action, method, criterion, or expected artefact | Owner, dependency, and gate where useful |
| `Unknown` | Missing or unresolved information | Why it matters and resolution path |

Do not use `Verified` for model memory, an uninspected citation, a search snippet, or another agent’s assertion.

For tables, place status in its own column. For prose, prefix consequential statements such as `**Assumption:**`.

## 3. Required Plan Sections

### 1. Plan Snapshot

Include:

- title;
- version and date;
- mode and depth;
- research family;
- primary question;
- intended decision or contribution;
- primary design;
- target population, system, or corpus;
- key feasibility constraint;
- next gate.

Quality test: a reviewer can understand the plan’s purpose and boundary in one minute.

### 2. Decision, Contribution, and Scope

State:

- problem and stakeholder;
- decision or use;
- contribution type;
- unit of analysis;
- population, context, place, and time;
- in-scope and out-of-scope claims.

Quality test: success is defined by knowledge or decision value, not by completing activities.

### 3. Assumptions and Unknowns

For each item include:

- status;
- statement;
- consequence if wrong;
- resolution step;
- owner or gate.

Quality test: no design-critical default remains hidden.

### 4. Research Questions and Inferential Targets

For each question include:

- ID;
- wording;
- claim type;
- estimand, phenomenon, mechanism, pattern, or construct;
- target population or cases;
- evidence needed;
- allowable conclusion.

Quality test: subquestions are necessary, nonduplicative, and collectively answer the primary question.

### 5. Conceptual, Causal, or Logic Model

Choose a representation suited to the study:

- construct map;
- theory of change;
- causal diagram;
- context-mechanism-outcome configuration;
- system architecture;
- requirements traceability;
- evidence-to-claim map.

Include competing explanations and boundary conditions.

Quality test: the representation changes at least one design, measurement, or analysis decision.

### 6. Evidence Baseline and Search Strategy

Separate:

- inspected sources;
- named but uninspected sources;
- searches run;
- searches proposed;
- evidence gaps.

Include claim-evidence needs, source classes, queries, limits, screening, appraisal, synthesis, and update policy as applicable.

Quality test: no novelty or current-fact claim exceeds documented search evidence.

### 7. Design Options and Selection

For each viable option include:

- design;
- supported claim;
- strengths;
- threats;
- ethical and access burden;
- resources;
- score and disqualifiers.

Then state primary design, fallback, and trigger for switching.

Quality test: the recommendation is conditional on the user’s decision and constraints.

### 8. Sampling, Cases, or Corpus

Include:

- target and frame;
- inclusion and exclusion;
- selection or recruitment;
- sample-size or case sufficiency rationale;
- subgroup and boundary coverage;
- attrition, nonresponse, yield, or replacement;
- access evidence.

Quality test: the achieved sample can be compared with the target and selection mechanisms can be assessed.

### 9. Constructs, Measures, and Data Collection

For each key construct or artefact include:

- conceptual definition;
- operational measure or evidence;
- provenance;
- reliability, validity, calibration, or quality check;
- timing and collection procedure;
- data type and metadata;
- pilot and failure rule.

Quality test: each inferential target has observable evidence and a quality control.

### 10. Analysis and Interpretation Plan

Include:

- primary analysis tied to each question;
- assumptions and diagnostics;
- preprocessing, exclusions, missingness, and outliers;
- uncertainty;
- multiplicity and flexibility;
- qualitative or synthesis decision rules;
- robustness and sensitivity;
- null, contradictory, and inconclusive interpretation;
- software, code, and review.

Quality test: another qualified analyst could implement the intended analysis without inventing core choices.

### 11. Validity, Robustness, and Boundary Tests

Use a table with:

- threat;
- affected claim;
- prevention;
- detection;
- sensitivity or falsification test;
- residual limitation.

Cover temporal, population, cultural, geographic, scale, environmental, and adversarial boundaries when relevant.

Quality test: the plan states how it might be wrong.

### 12. Ethics, Bias, Governance, and Stakeholders

Include:

- stakeholder map;
- benefits, burdens, power, and group harms;
- consent, privacy, confidentiality, data rights, and accessibility;
- cultural and language fit;
- approvals and current-rule checks;
- conflicts, dual use, and accountability;
- unresolved ethics gates.

Quality test: this section changes procedures, access, sampling, analysis, or dissemination where risk exists.

### 13. Reproducibility and Provenance

Include:

- protocol and amendment log;
- source, data, and instrument versions;
- code, environment, hardware, seeds, and dependencies;
- prompts, context, model, tools, and human overrides where AI is used;
- archival and access plan;
- deviation reporting.

Quality test: a reviewer can trace every conclusion to source, data, transformation, and decision.

### 14. Feasibility, Risks, and Contingencies

Include:

- timeline and critical path;
- people, skills, facilities, compute, budget, and permissions;
- dependency and risk register;
- fallback and scope reduction;
- stop or redesign thresholds.

Quality test: inaccessible data or approvals cannot remain implicit.

### 15. Execution Roadmap and Decision Gates

For each stage include:

- stage ID;
- inputs;
- actions;
- owner or role;
- dependency;
- deliverable;
- completion evidence;
- gate and rule;
- status.

Quality test: progress can be verified without converting activity into evidence of a research result.

### 16. Unresolved Items

List only design-relevant items. Include:

- priority;
- question;
- affected section;
- consequence;
- resolution method;
- deadline or gate.

Quality test: the plan remains usable while making limitations visible.

## 4. Research-Family Extensions

### Evidence synthesis

Add protocol registration, search exports, deduplication, screening calibration, extraction schema, risk-of-bias, heterogeneity, certainty, and update trigger.

### Qualitative

Add orientation, researcher position, field relationship, sampling evolution, reflexivity, analytic memos, negative cases, contextual evidence, translation, and participant/community engagement.

### Causal or experimental

Add estimand, assignment or identification, timing, interference, compliance, manipulation, confounders, power/precision, treatment fidelity, and falsification.

### Prediction or machine learning

Add target use, error costs, split strategy, leakage controls, baselines, calibration, subgroup evaluation, external validation, monitoring, and drift.

### Engineering or design science

Add requirements, alternatives, architecture, acceptance criteria, verification matrix, validation setting, hazards, reliability, and maintenance.

### AI-augmented

Add role level, target-task validation, reference standard, subgroup and cultural checks, model/prompt/tool provenance, human review, abstention, and model-change policy.

## 5. Roadmap and Decision Gates

Recommended stage pattern:

1. scope and stakeholder gate;
2. evidence and feasibility reconnaissance;
3. ethics, governance, and access gate;
4. pilot or calibration;
5. design freeze or preregistration;
6. acquisition or data collection;
7. quality gate;
8. analysis freeze and execution;
9. robustness and independent review;
10. reporting, disclosure, archive, and update.

A gate result is `GO`, `REVISE`, `STOP`, or `UNKNOWN`, supported by evidence.

## 6. Audit Evidence

Every audit finding should contain:

- `severity`;
- `section`;
- exact quote or missing field;
- `failure_mechanism`;
- affected claim or decision;
- `repair`;
- `verification`.

Severity:

- **Critical:** invalidates the central claim, creates serious ethical/safety risk, fabricates evidence, or makes execution impossible.
- **High:** likely changes design or conclusion.
- **Medium:** weakens interpretation, transfer, or reproducibility.
- **Low:** clarity, organization, or efficiency issue with limited inferential effect.

Do not rewrite before showing Critical and High findings.

## 7. Completion Tests

A plan is decision-ready only when:

1. primary question and allowable conclusion match;
2. every question maps to evidence and analysis;
3. method choice is justified against alternatives;
4. sampling or cases support the target;
5. constructs and measures are operational;
6. analysis choices and uncertainty are explicit;
7. validity, contradiction, and boundary tests exist;
8. ethics, stakeholders, culture, language, and governance are addressed;
9. provenance and reproducibility are specified;
10. access, resources, dependencies, and gates are feasible;
11. novelty and current claims are evidence-bounded;
12. proposed work is not presented as completed work;
13. saved files pass `scripts/plan_lint.py`;
14. blocked checks are marked `Unknown` or `NOT RUN`.
