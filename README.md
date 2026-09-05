# Deepest Research

Deepest Research is an agent skill for turning an underspecified research goal into a defensible, executable path. It helps an agent frame the real question, search across evidence and implementation lanes, inspect methods, compare designs, challenge competing explanations, and define the next research action with explicit provenance.

It is useful when the work involves a research plan, literature or evidence search, interdisciplinary mapping, systematic or scoping review strategy, empirical study, experiment, benchmark, prior-art or implementation study, novelty investigation, or paper-to-code workflow. It is not the right entry point for a simple paper summary or an ordinary factual answer with no research-design component.

## Start here

Read the [user guide](docs/USER_GUIDE.md) for installation, invocation, task procedures, utility reference, troubleshooting, and worked examples. Contributors should start with the [contributor guide](docs/CONTRIBUTING.md).

### First use

1. Place or install `skills/deepest-research/` using the skill host’s documented installation mechanism. The repository does not require `pip install` for the local utilities and does not provide a host-independent installer.
2. Invoke the skill from your host with a question such as:

   ```text
   Use $deepest-research to turn this research question into a source-grounded plan. Inspect the supplied papers and code first. Separate evidence from inference, search for competing explanations, compare at least two viable approaches, and finish with an executable next step and explicit limitations.
   ```

3. For a local first success, run the static repository indexer:

   ```bash
   python skills/deepest-research/scripts/repo_parser.py \
     skills/deepest-research/scripts \
     --output research-output/repository-index.json
   ```

The command writes a JSON index containing Python modules, symbols, signatures, imports, parse errors, and any local import edges. It parses source without importing or executing the indexed project. A successful local run is structural evidence; it does not prove runtime behavior or scientific validity.

## Verification

The repository includes a local quality workflow for Python syntax, static indexing, context/sample-size/agreement smoke fixtures, and the pipeline’s dry-run contract. The shipped utilities have also been exercised against explicit source, extraction, document, and candidate fixtures: the repository index reported 15 modules with zero parse errors, grounding retained one matched and one unmatched value, and the pipeline produced both an intentional `NOT_RUN` dry-run and a live local `PASS`. These checks cover local interfaces and report behavior; external model, provider, network, and host-discovery paths require their own environment evidence.

### Walkthrough and source inspection

- Source inspection covered `SKILL.md`, host metadata, references, assets, templates, scripts, and the Bash pipeline.
- Execution test covered the static repository index, local calculators, source grounding, extraction preprocessing, hierarchy baseline, self-consistency aggregation, pipeline dry-run, and one live local pipeline stage.
- Walkthrough used the documented first-use commands and checked the reported files, statuses, and parse counts.
- Target-user edit and provider/model execution were not run in this repository check; validate those paths in the target host and research environment.

## What the skill does

The core workflow is deliberately evidence-first:

1. Frame the decision or knowledge gap, question type, population/system, unit, context, timeframe, and what observation would change the answer.
2. Build complementary search lanes for direct evidence, mechanisms, comparisons, failure cases, implementations, citation graphs, and adjacent domains.
3. Inspect methods and implementation details rather than inferring a method from metadata or an abstract alone.
4. Synthesize mechanisms across sources and preserve conditional branches when evidence conflicts.
5. Compare materially different research approaches on inferential fit, information gain, measurement, validity, feasibility, reuse, failure recovery, and decision usefulness.
6. Design the smallest study or computational experiment that can support the intended conclusion.
7. Search mature implementations, datasets, models, APIs, and MCP servers before proposing custom engineering.
8. Run a disconfirmation pass for competing hypotheses, negative evidence, boundary conditions, leakage, provider dependence, and cheaper explanations.
9. Convert the selected path into explicit inputs, actions, tools, outputs, decision rules, branches, and stop conditions.
10. Stop when additional credible evidence is unlikely to change the method set, leading explanation, design, important failure boundary, reuse decision, or next action.

The package also includes independent local utilities for source grounding, literature retrieval and ranking, context-window planning, corpus curation, agreement and sample-size calculations, self-consistency aggregation, hierarchy and concept integration, Fast-DetectGPT criterion/calibration/detection, headline-model training/prediction/features, Curie-style rigor checks, repository indexing, plan linting, and an explicit-stage Bash pipeline.

## Choose a utility

| Need | Entry point | Output or boundary |
| --- | --- | --- |
| Inspect a Python repository | `scripts/repo_parser.py` | Static AST index; no project imports or execution |
| Curate and deduplicate text/JSON | `scripts/scan.py` | Retained/rejected records and provenance; configure normalization and duplicate policy |
| Ground extracted values in source text | `scripts/hybrid-rag-verifier.py`, `scripts/byte-Identity.py` | Exact or normalized offsets and unsupported-value handling; occurrence is not semantic proof |
| Preprocess or integrate structured extraction | `scripts/mixed-ie-parser.py` | Segments, extractor contracts, tuple integration, conflicts, and provenance |
| Retrieve and rank literature | `scripts/literature-explorer.py` | arXiv/frozen-feed records and lexical/BM25/optional dense ranking; one query is not a systematic search |
| Plan context windows | `scripts/context_window.py` | Exact tokenizer or explicit character/token estimate and chunk manifest |
| Build a hierarchy or integrate concepts | `scripts/hierarchography.py` | Offline TF-IDF baseline or explicit concept-adapter integration |
| Aggregate sampled answers | `scripts/self-consistency-voting.py` | Majority, weighted, or resonance aggregation with dissent retained |
| Compute formal planning statistics | `scripts/sample_size.py`, `scripts/intercoder.py` | Sample-size or Cohen/Fleiss agreement reports under declared assumptions |
| Compute Fast-DetectGPT curvature | `scripts/probability_curvature.py` | Analytic criterion, calibration profile, or model-backed detection |
| Train or apply headline model | `scripts/hypothetically_popular.py` | Within-experiment train/predict/features path over explicit CSV/model artifacts |
| Audit experiment rigor | `scripts/curie-rigor-monitor.py` | Static setup, plan partition, or execution-manifest verification |
| Validate a saved research plan | `scripts/plan_lint.py` | Structural and epistemic checks; not domain or ethics approval |
| Run selected stages together | `scripts/execute-research-pipeline.sh` | Isolated logs plus `pipeline_status.json`; command completion is not research validity |

Read each command’s `--help` before preparing inputs. The [user guide](docs/USER_GUIDE.md) contains the full task reference and examples.

## Package layout

```text
skills/deepest-research/
├── SKILL.md                    # canonical agent behavior and evidence contract
├── agents/                     # host and proposer metadata
├── assets/                     # reusable prompt and workflow assets
├── references/                 # method, evidence, and implementation references
├── scripts/                    # explicit local utilities and pipeline
└── templates/                  # research-plan and evidence templates
```

The skill metadata allows implicit invocation on compatible hosts. `agents/research-proposer.toml` describes a read-only proposal role; it does not edit files or select a winner without explicit criteria.

## Evidence boundary

Deepest Research requires supplied papers, datasets, code, notes, and prototypes to be inspected before judgment or replacement. Source-specific claims must come from inspected evidence. The skill does not invent citations, searches, results, access, executions, metrics, or novelty. For consequential work, actively seek competing explanations, negative evidence, boundary conditions, and failure cases.

Every executable gate is reported as `PASS`, `WARN`, `FAIL`, or `NOT RUN`. A script or pipeline can prove that a command ran and produced a report; it cannot, by itself, prove that the research conclusion is correct. Record the source revision, inputs, model/tokenizer and dependency settings where relevant, thresholds, domain, policy, and unmatched or unsupported values before interpreting output.

## Runtime requirements and limits

The local utilities target Python 3 and use standard-library paths unless a selected method requires an optional model or provider. The Bash pipeline requires Bash and defaults to `python3`. Literature retrieval, dense ranking, rerankers, model-backed detection, and adapter commands depend on network, model, command, and dependency availability. Run those paths in the target environment and report `NOT RUN` when their prerequisites are absent.

This repository currently contains no `LICENSE` file. Treat reuse and redistribution terms as unresolved until the project owner adds or communicates an applicable license. See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for source ownership, validation, and release checks.

## Project status

The source package is maintained as a collection of agent instructions, references, templates, and executable utilities. Structural and local fixture checks are appropriate for every change. External model/provider behavior, scholarly coverage, and empirical research conclusions require their own evidence and are outside the claims made by this repository’s local checks.
