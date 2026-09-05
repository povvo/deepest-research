# Source-Grounded Prototype Engineering

## Contents

- [Read This Reference When](#read-this-reference-when)
- [Governing Presumption](#governing-presumption)
- [Fidelity Classes](#fidelity-classes)
- [Paper-to-Production Procedure](#paper-to-production-procedure)
- [Claim and Evidence Discipline](#claim-and-evidence-discipline)
- [Release Evidence](#release-evidence)

## Read This Reference When

Read this file before changing, replacing, auditing, or operationalizing any supplied research script, prompt, calculator, decision tree, or orchestration asset. Also read it when a method's scientific basis and the current code's completeness must be distinguished.

## Governing Presumption

Treat a supplied research component as an intentional, source-grounded prototype unless direct inspection establishes otherwise. Do not infer that a compact implementation, fixed fixture, simplified scorer, or demo entry point means that the underlying method is unsupported.

The correct audit unit is the **paper-to-implementation contract**:

1. the cited scientific claim or method;
2. the algorithmic or procedural core needed to instantiate it;
3. the prototype's current implementation of that core;
4. deliberate simplifications, unresolved parameters, external dependencies, and missing evidence;
5. the production implementation and its operating envelope;
6. tests showing that the implementation behaves as specified.

Respect the researcher's supplied rationale and terminology. Challenge a component only with exact evidence such as a syntax failure, unreachable file, mismatched equation, missing dependency declaration, unimplemented model call, invalid calibration transfer, or a result field not produced by the cited procedure.

## Fidelity Classes

Assign one class before editing:

- **Paper-backed implementation** — the executable path implements the cited algorithmic core and exposes the parameters required by the source.
- **Calibrated model implementation** — the method requires learned parameters, thresholds, or a model artefact; training or calibration and inference are separate, reproducible commands.
- **Model/tool adapter** — the local script implements preprocessing, contracts, validation, provenance, and integration while a named external model or tool performs the learned operation.
- **Deterministic reference baseline** — a transparent, reproducible baseline used for fixtures, ablation, or offline operation; it must not be represented as the paper's strongest learned system.
- **Formal calculator** — a cited statistic or formula with declared assumptions and machine-checkable inputs.
- **Evidence verifier** — a deterministic grounding, provenance, schema, or execution-evidence check.
- **Orchestrator** — invokes independently testable tools without manufacturing successful outputs.

A component may expose more than one class through separate subcommands. Name the class in output metadata.

## Paper-to-Production Procedure

### 1. Resolve the source

Use `references/source-provenance-map.md` to identify the supplied rationale and papers. For implementation-critical details, inspect the paper and, where available, the authors' official code. Record title, version/date, section, equation or algorithm, repository revision, and any dataset or model card.

### 2. Write the executable contract

State:

- required inputs and their schema;
- model, tokenizer, dataset, corpus, or instrument identifiers;
- algorithm, statistic, or decision rule;
- parameters and whether they are published, calibrated, trained, or user supplied;
- outputs, units, provenance, and uncertainty;
- supported domains, languages, lengths, and hardware;
- expected failure modes and non-zero exit behavior.

Do not silently replace a learned method with lexical scoring, a calibrated detector with fixed percentages, a model call with random values, or executed evidence with static inspection.

### 3. Preserve useful prototype behavior

Retain stable input aliases, output fields, deterministic fixtures, and extension points when they remain coherent. When a production interface must change, document migration in `references/script-method-map.md` and keep a compatibility path where practical.

### 4. Separate algorithm from calibration and policy

A scientifically supported algorithm can still require local calibration, external validity checks, or institutional review. Express those as operating conditions, not as a denial of the method.

Examples:

- Fast-DetectGPT can classify under a declared model pair and threshold; threshold transfer, language/domain shift, and consequential review are separate questions.
- A headline engagement model can predict within the population represented by randomized experiments after training and held-out evaluation; transparent features alone are not a trained prediction.
- Curie-style static validation, partition validation, and execution-knowledge verification are distinct evidence layers.
- LLooM-style concept induction requires model-generated concepts and explicit criteria; TF-IDF clustering may remain a baseline, not a substitute presented under the same name.

### 5. Validate at the right layer

Every executable script must pass:

1. `--help`;
2. syntax or shell parsing;
3. a task-specific smoke test;
4. an expected-failure test;
5. output-schema and provenance assertions.

Add method-specific checks where applicable:

- equation-level numeric fixtures against an independent implementation;
- calibration split integrity and leakage checks;
- tokenizer/model compatibility;
- deterministic seeds and repeatability;
- source offsets and byte spans;
- DAG validity and artefact hashes;
- adapter JSON contract and timeout behavior.

A smoke test proves the executable contract, not empirical parity with a paper. Mark paper-level reproduction or benchmark comparison `NOT RUN` unless it was actually executed.

## Claim Language

Use precise findings:

- “The prototype cites Fast-DetectGPT, but its current scorer does not implement the paper's analytic conditional-probability criterion.”
- “The method is source-grounded; model-backed inference is blocked in this environment because `transformers` and weights are unavailable.”
- “The deterministic clustering path is an offline baseline; LLooM concept induction is available through the model adapter.”
- “The archive experiment model has not been trained on the supplied dataset, so prediction is `NOT RUN`.”

Do not use blanket labels such as “unsupported,” “random,” “toy,” or “unverified” when the issue is implementation completeness, calibration, dependency availability, or external validity.

## Runtime Packaging

Ship production code, contracts, templates, and focused on-demand references. Keep source PDFs, benchmark corpora, model weights, training runs, eval outputs, and build notes outside the runtime package unless the skill explicitly needs a redistributable runtime artefact. Never remove a supplied component merely because it is not required by one narrow execution path; either route it directly or document a deliberate, evidence-backed supersession.
