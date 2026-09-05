# Decision Tree: Research Tool and Model Capability Selection

> **Runtime use condition:** Read when selecting software or model capabilities under privacy, reproducibility, cost, access, and validation constraints.
> **Evidence status:** Retained project-derived playbook, revised to be runtime-neutral. Verify implementation-critical capabilities, prices, limits, licenses, and API behaviour from first-party sources at task time.

**Version:** 2.0.0  
**Focus:** Match research tasks to required capabilities and validation evidence rather than to a fixed product name.

## 1. Selection order

Choose tools in this order:

1. **Inferential requirement:** What claim, transformation, computation, or decision must the tool support?
2. **Evidence and data boundary:** What data may leave the environment, and what provenance must be retained?
3. **Determinism and auditability:** Does the step require exact repeatability, executable tests, or only exploratory assistance?
4. **Capability:** Structured output, long-context reading, code execution, retrieval, speech recognition, vision, statistics, simulation, or domain-specific parsing.
5. **Validation burden:** What gold set, human review, error analysis, calibration, or cross-check is required?
6. **Operational constraints:** Cost, latency, rate limits, local hardware, license, accessibility, and maintenance.
7. **Fallback:** What happens when the preferred tool, model, API, or dataset is unavailable or changes?

## 2. Capability matrix

| Research task | Preferred capability | Minimum validation | Typical fallback |
| --- | --- | --- | --- |
| Transcription | Local or approved speech-to-text with timestamps and language support | Stratified word/error review, speaker and domain checks | Human transcription or targeted correction |
| Literature retrieval | Search API/database access with exportable queries and identifiers | Query log, source coverage, deduplication, screening audit | Manual database search and citation chaining |
| Structured extraction | Schema-constrained output plus source locators | Gold-set precision/recall and field-level grounding | Rules, double extraction, or manual adjudication |
| Qualitative coding | Context handling, stable instructions, evidence-linked labels | Calibration sample, negative cases, reflexive review | Human coding with software assistance |
| Statistical analysis | Deterministic language/runtime and tested libraries | Unit tests, diagnostics, reproducible environment | Independent implementation or manual calculation |
| Simulation or optimization | Executable solver with seed and environment control | Baselines, convergence checks, sensitivity analysis | Simpler analytical model |
| Repository analysis | AST/static analysis and sandboxed execution | Parse/error log, targeted runtime tests | Manual code tracing |
| Publication synthesis | Document toolchain with citation and compile support | Citation audit and successful build log | Plain Markdown report |

## 3. Model-use decision tree

```text
Start
├─ Can a deterministic parser, calculator, query, or script do the task?
│  ├─ Yes → use it and retain command evidence.
│  └─ No
├─ Does the input contain restricted or sensitive data?
│  ├─ Yes → use an approved local or governed environment.
│  └─ No
├─ Is the output consequential, inferential, or participant-facing?
│  ├─ Yes → require a target-task validation set and human review.
│  └─ No → exploratory use may be acceptable with provenance.
└─ Is the selected capability unavailable or unstable?
   ├─ Yes → invoke the declared fallback and downgrade the claim.
   └─ No → record version/date, parameters, prompt, inputs, and outputs.
```

## 4. Release checks

Before recommending a tool:

- verify current availability, documentation, context or payload limits, privacy terms, license, and pricing when material;
- avoid hard-coded model labels unless the user's environment guarantees them;
- distinguish a proposed tool from one actually installed or tested;
- prefer standard-library or local deterministic scripts for repeated checks;
- define task-specific acceptance criteria and a fallback;
- record what the tool cannot establish.
