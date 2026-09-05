# AI-Augmented and AI-Native Research

Use this reference when AI, language models, automated agents, synthetic data, synthetic participants, automated coding, or model-mediated decisions are part of the research method or object.

## Contents

1. Role and consequence ladder
2. Validation-by-role
3. AI as assistant
4. AI as analytic instrument
5. Synthetic participants and silicon sampling
6. AI-mediated qualitative research
7. AI-assisted evidence synthesis
8. Agents and autonomous actions
9. Provenance and reproducibility
10. Cultural and distributional validity
11. Reporting and disclosure
12. Stop and downgrade rules

## 1. Role and Consequence Ladder

Classify every AI use:

| Level | Role | Examples | Default treatment |
| --- | --- | --- | --- |
| 1 | Clerical transformation | Format conversion, deduplication, transcription draft | Verify samples and preserve originals |
| 2 | Research assistance | Query expansion, coding suggestions, drafting instruments | Human reviews all consequential decisions |
| 3 | Analytic instrument | Classification, extraction, scoring, prediction | Validate against target-task reference data |
| 4 | Proxy or synthetic subject | Simulated respondents, personas, agents standing for people | Exploratory or pretest use unless externally validated |
| 5 | Autonomous research action | Agent chooses sources, methods, experiments, or writes to systems | Stage gates, sandboxing, audit logs, independent review |

Do not infer reliability at one level from success at another. Fluent output is not validation.

## 2. Validation-by-Role

For each AI-mediated step, specify:

- task and intended use;
- consequence of error;
- target population, corpus, or environment;
- reference standard and who created it;
- sample and subgroup coverage;
- metrics tied to error costs;
- uncertainty and abstention rule;
- human review and escalation;
- model, version/date, parameters, prompt, context, tools, and data access;
- rerun, drift, and change-control policy;
- residual limitations.

Use holdout data or independently adjudicated examples. Avoid validating on the same examples used to construct prompts or rules.

High accuracy alone may be insufficient. Inspect false-positive and false-negative costs, calibration, subgroup performance, agreement on ambiguous cases, and downstream decision impact.

## 3. AI as Assistant

Appropriate uses may include:

- brainstorming alternative questions;
- expanding search vocabulary;
- transforming formats;
- drafting structured fields;
- generating counterarguments;
- proposing code or tests;
- summarizing inspected sources with locators.

Controls:

- provide source-bounded context;
- require provenance for extracted claims;
- compare against originals;
- separate suggestions from accepted decisions;
- preserve researcher edits and rationale;
- sample for omissions, not only false additions;
- avoid anchoring by generating an independent human view first when stakes are high.

Do not ask AI to supply missing facts from memory when an evidence source is required.

## 4. AI as Analytic Instrument

For classification, extraction, coding, prediction, or scoring:

1. define the construct operationally;
2. create or obtain a target-task reference set;
3. include ambiguous, negative, rare, subgroup, multilingual, and adversarial cases;
4. predefine metrics and acceptable error;
5. compare simple, non-AI, and human baselines;
6. calibrate prompts or models without contaminating the test set;
7. estimate uncertainty and define abstention;
8. inspect systematic failure patterns;
9. validate transfer to the target setting;
10. monitor drift and rerun after material model or pipeline changes.

A proprietary or changing model creates a dependency risk. Record an alternative or migration test.

## 5. Synthetic Participants and Silicon Sampling

Synthetic respondents may help with:

- instrument pretesting;
- scenario exploration;
- hypothesis generation;
- method debugging;
- sensitivity analysis;
- training or simulation where no claim about real population behaviour is made.

They must not substitute for human evidence merely because recruitment is expensive or slow.

Before using them for any population claim, require:

- a clearly defined target population and context;
- human benchmark data independent of model training and prompt construction;
- marginal-distribution comparison;
- correlation, covariance, ranking, and conditional-relationship preservation;
- subgroup and intersectional performance;
- variance and extremity checks;
- test-retest and prompt/model sensitivity;
- cultural and language validation;
- contamination and stereotype analysis;
- explicit domain-of-validity and failure boundaries.

Aggregate similarity does not prove individual, relational, causal, or subgroup fidelity. When validation is absent or weak, label outputs as simulations of model behaviour, not observations of people.

## 6. AI-Mediated Qualitative Research

Potential roles include transcription support, corpus navigation, deductive coding assistance, theme suggestions, contradiction surfacing, and audit-trail organization.

Protect interpretive integrity:

- retain raw data and contextual units;
- specify epistemological stance;
- do not treat generated codes or themes as findings before human analytic engagement;
- document prompts, iterations, accepted and rejected suggestions;
- inspect omissions, flattening, stereotype reproduction, and loss of minority voices;
- use culturally and linguistically competent review;
- test deductive coding on an adjudicated set when consistency is claimed;
- do not impose inter-rater agreement as the sole criterion for reflexive approaches;
- preserve negative cases and researcher reflexivity.

AI cannot supply participant meaning or field presence it did not observe.

## 7. AI-Assisted Evidence Synthesis

Automation may support search expansion, prioritization, screening, extraction, citation checking, and update monitoring.

Controls:

- preserve exact queries and retrieved universe;
- distinguish ranking from exclusion;
- calibrate screening on diverse examples;
- target high recall when missing evidence is costly;
- independently verify exclusions or a risk-based sample;
- verify every extracted claim against source locators;
- inspect inaccessible and non-English evidence;
- appraise risk of bias separately from extraction;
- document model and workflow changes during living updates.

Do not claim systematic completeness from an opaque recommender or top-k retrieval alone.

## 8. Agents and Autonomous Actions

For tool-using or multi-agent workflows:

- give each role a narrow objective and evidence contract;
- separate execution from grading;
- limit permissions and write scope;
- log prompts, tool calls, inputs, outputs, errors, and overrides;
- require approvals before external communication, data mutation, spending, participant contact, or experiment execution;
- use independent review for high-consequence outputs;
- prevent agents from treating another agent’s unsupported statement as evidence;
- define retry, rollback, and termination rules;
- test on safe fixtures before real systems.

Multi-agent debate can generate useful alternatives but does not create independent empirical evidence. Repeated agreement among models sharing training data or context is not a substitute for source verification.

## 9. Provenance and Reproducibility

Capture:

- provider or local model identifier;
- model version, snapshot, or access date;
- system and developer instructions;
- user prompt and templates;
- context files and retrieval method;
- tool definitions and calls;
- sampling parameters and seeds where available;
- output parser and validation;
- safety filters and post-processing;
- human edits, decisions, and reasons;
- data sent to third parties;
- costs, latency, and failure logs when operationally relevant;
- rerun policy after model updates.

When exact reproduction is impossible, aim for traceability, bounded replication, and robustness across reasonable model or prompt variations.

## 10. Cultural and Distributional Validity

Evaluate:

- language coverage and translation quality;
- representation in training and reference data;
- digital-access and literacy assumptions;
- cultural concepts that do not map to model categories;
- stereotype and norm imposition;
- subgroup sample size and uncertainty;
- local expert or community interpretation;
- differences in response style, context, and institutional meaning.

A model validated in one country, language, discipline, platform, or demographic group should be treated as unvalidated elsewhere until transfer evidence exists.

## 11. Reporting and Disclosure

Report AI use where it materially affected:

- question framing or search;
- source selection;
- instrument construction;
- data generation or collection;
- coding, extraction, analysis, or interpretation;
- figures, text, code, or decisions;
- autonomous actions.

Include purpose, model or tool, version/date, inputs, prompts or procedure, human oversight, validation, material errors, changes, and limitations. Verify current funder, institutional, journal, and jurisdictional requirements at task time.

Do not list AI as a human author or accountable investigator. Assign responsibility to named humans and institutions according to current policy.

## 12. Stop and Downgrade Rules

Stop or downgrade when:

- target-task validation is absent for a consequential role;
- reference data is too small, biased, or contaminated;
- subgroup errors exceed acceptable harm;
- outputs cannot be traced to sources;
- model or vendor changes invalidate prior testing;
- sensitive data cannot be processed lawfully or ethically;
- human reviewers lack the expertise to detect errors;
- autonomous permissions exceed the tested safety envelope;
- synthetic behaviour is being mistaken for human evidence.

Repairs include human-only processing, bounded assistance, dual review, abstention, narrower population claims, exploratory labeling, local models, safer data, external validation, or removing the AI component.
