# Research Engine

## Purpose
Use whenever the task requires discovering, mapping, comparing, or synthesizing evidence rather than merely formatting a plan. This is the capability core: it turns a research question into a high-recall/high-precision search graph, traverses scholarly and implementation evidence, extracts mechanisms, and stops at decision sufficiency.

## 1. Build the research graph
Represent the question through complementary vocabularies:
- domain/user terms;
- formal constructs and synonyms;
- mechanism/method names;
- population/context;
- outcome/measurement terms;
- implementation terms;
- benchmark/evaluation terms;
- limitation/failure terms;
- adjacent-domain analogues;
- canonical identifiers (DOI, PMID, arXiv, repository/model/dataset IDs).

Decompose into 3–8 answerable subquestions. For each state what evidence would change the design or conclusion.

## 2. Search in lanes, not one query
Run complementary lanes when relevant:
1. **Direct:** phenomenon + outcome/context.
2. **Mechanism:** method/algorithm/theory + phenomenon.
3. **Comparison:** method + alternative/baseline/benchmark.
4. **Failure:** method + limitation/bias/robustness/negative result.
5. **Implementation:** method + code/package/dataset/model/system.
6. **Citation:** backward references for foundations; forward citations for replication, refinements and criticism.
7. **Adjacent-domain:** same mechanism in a field where it is more mature.

Prefer structured scholarly/repository providers over generic web search when available. Use OpenAlex/Crossref/arXiv for identity and discovery, OpenCitations for graph expansion, GitHub for implementations, Hugging Face for models/datasets/Spaces, and the MCP Registry for reusable live integrations. Generic web search fills gaps and retrieves official documentation.

## 3. Candidate-set strategy
Use a funnel:
- **Seed:** 3–8 high-relevance canonical works/components spanning distinct method families.
- **Expand:** citation chaining, related-work queries, author/project search, alternative terminology.
- **Diversify:** deliberately add contradictory, newer, lower-citation but method-rich, and adjacent-domain candidates.
- **Converge:** stop expanding a lane when consecutive credible additions no longer change the method set, failure boundaries, reuse options, or planned experiment.

Citation count is a discovery signal, never a quality score.

## 4. Acquire enough primary evidence
Metadata is not method evidence. For every source that materially determines a procedure, acquire enough primary content to inspect:
- problem and operating context;
- data/sample;
- method/procedure/equations;
- parameter selection;
- baselines;
- evaluation;
- limitations/failure modes;
- implementation artefacts.

If primary content is unavailable, retain the item as a discovery lead and do not invent procedure.

## 5. Extract mechanism cards
For each material source/component capture:
- problem solved;
- inputs and grain;
- transformation/algorithm;
- output;
- assumptions;
- parameters and how selected;
- evidence/evaluation;
- failure modes and boundary conditions;
- reusable code/data/model/API;
- transfer conditions.

Synthesize mechanism cards, not source-by-source prose.

## 6. Cross-source synthesis
Normalize equivalent concepts only when inputs, outputs, and assumptions match. Compose complementary stages when interfaces align:
`acquisition → normalization → candidate generation → analysis → validation → synthesis`.

When sources conflict, diagnose whether the cause is population, measurement, version, objective, study quality, or genuine uncertainty. Preserve conditional branches instead of averaging incompatible claims.

Classify new architecture that no source states verbatim as engineering synthesis. Transfer methods across domains only after checking shared invariant structure, changed assumptions, recalibration needs, falsifiers, and target-context test.

## 7. Choose research design by inferential job
- Map a field → scoping review/evidence map/taxonomy.
- Estimate prevalence → representative survey/registry/population data.
- Estimate causal effect → randomized experiment or justified quasi-experimental/causal design.
- Predict → leakage-safe train/validation/test or temporal validation.
- Understand mechanism → experiment/process tracing/formal model/mechanistic study.
- Understand meaning/workflow → interviews/contextual inquiry/observation/qualitative analysis.
- Compare implementations → fixed-fixture benchmark + ablation + failure tests.
- Build a system → design science/prototype-and-evaluate + prior-art reuse.
- Synthesize heterogeneous evidence → integrative/realist/mixed-method synthesis.
- Monitor a fast field → living review/repeated reconnaissance.

Use the smallest design that can answer the decision, and triangulate only when different designs contribute distinct evidence.

## 8. Quantitative reasoning
Before calculation define unit, denominator, baseline, time window, target, comparator, and uncertainty. Inspect missingness, duplicates, leakage, subgroup behavior, and data-generating process.

Match metrics to the decision:
- classification: precision/recall/F1, PR-AUC/ROC-AUC, calibration as appropriate;
- ranking/retrieval: recall@k, precision@k, MRR/NDCG, review budget;
- regression: absolute/squared/relative error plus distribution;
- probabilistic: log loss/Brier/calibration;
- forecasting: rolling temporal validation and horizon-specific error.

Prefer estimates with uncertainty and effect sizes over binary significance. Test sensitivity to plausible inclusion rules, thresholds, missingness policies, model specifications, and time windows.

## 9. Prior-art and implementation reconnaissance
Before proposing custom engineering, search products, repositories, packages, MCP servers, models, datasets, APIs, and relevant standards. For serious candidates compare capability coverage, licence, maintenance, API stability, dependencies, tests, runtime fit, auth/data requirements, extensibility, adaptation cost, and lock-in.

Choose explicitly among reuse, configure, adapt, compose, reimplement, or research further. Popularity alone is not fitness.

## 10. Ideation and hypothesis generation
After establishing the evidence baseline, generate alternatives by varying:
- mechanism;
- unit/population;
- data source;
- measurement;
- intervention;
- comparison/baseline;
- evaluation;
- deployment context.

For each promising idea identify nearest overlap, differentiating contribution, strongest rival explanation, falsifier, and cheapest discriminating test. Optimize importance and validity before novelty.

## 11. Research loop
Repeat:
`frame → search → inspect → extract → synthesize → challenge → update question/design → search again`.

At each checkpoint ask: what is the highest-value missing evidence? Run that next, rather than mechanically completing a checklist.

Stop when additional credible evidence is unlikely to change the method set, design choice, failure boundary, reuse decision, or next experiment. Residual uncertainty can remain.

## 12. Research outputs
Depending on the request, produce one or more:
- ranked source map with canonical identifiers and why each source matters;
- evidence/method matrix;
- mechanism cards;
- competing-hypothesis table;
- prior-art reuse matrix;
- research design comparison;
- executable search protocol;
- experiment/benchmark specification;
- decision-ready synthesis with next discriminating research actions.

The primary output should help the user do better research, not merely document that research was governed.
