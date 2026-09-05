# Deepest Research user guide

This guide helps a researcher or research engineer choose an entry point, run the package, verify outputs, and recover when the expected result does not occur.

## Contents

- [Task boundary](#task-boundary)
- [Install or place the skill](#install-or-place-the-skill)
- [Run the first local check](#run-the-first-local-check)
- [Turn a question into a research path](#turn-a-question-into-a-research-path)
- [Preserve evidence and provenance](#preserve-evidence-and-provenance)
- [Use the utilities](#use-the-utilities)
- [Run the explicit-stage pipeline](#run-the-explicit-stage-pipeline)
- [Interpret statuses and reports](#interpret-statuses-and-reports)
- [Troubleshoot by symptom](#troubleshoot-by-symptom)
- [Runtime limits](#runtime-limits)

## Task boundary

Use this guide to invoke the `deepest-research` skill, plan research, run its local utilities, interpret reports, and recover from common input or environment failures.

Do not use it as evidence that an external model, provider, scholarly endpoint, or research conclusion is available or valid. Inspect the canonical source and the report produced by the selected utility before making a substantive claim.

## Install or place the skill

### Preconditions

- Obtain the repository or a release archive.
- Identify the skill host’s documented skill directory or installation command.
- Use Python 3 for local utilities. Use Bash for `execute-research-pipeline.sh`.
- Decide where generated reports will live. Keep them outside the skill source tree.

### Procedure

1. Copy the directory `skills/deepest-research/` into the host’s skill directory, or use the host’s skill installer to place that directory.

   Expected result: the installed directory contains `SKILL.md`, `agents/`, `assets/`, `references/`, `scripts/`, and `templates/`.

2. Check the package metadata:

   ```bash
   python -c "from pathlib import Path; p=Path('skills/deepest-research'); required=['SKILL.md','agents/openai.yaml','scripts/repo_parser.py']; missing=[x for x in required if not (p/x).is_file()]; raise SystemExit(f'missing: {missing}' if missing else 'deepest-research layout: PASS')"
   ```

   Expected result: `deepest-research layout: PASS`.

3. Invoke the skill through the host. Give it a concrete question, supplied source paths or links, the desired conclusion type, and the decision the research will inform.

   Expected result: the agent frames the question and returns an evidence/search/design path instead of treating the request as an ordinary factual lookup.

### Verify

The local layout check proves that the package is present. It does not prove that a particular host discovers or invokes it. Verify host discovery through that host’s own interface and keep the host-specific result with the release evidence.

## Run the first local check

This is a portable first use of the shipped tooling. It indexes the Python utilities without importing or executing them.

### POSIX shell

```bash
set -eu
out="research-output"
mkdir -p "$out"
python3 skills/deepest-research/scripts/repo_parser.py \
  skills/deepest-research/scripts \
  --fail-on-parse-error \
  --output "$out/repository-index.json"
python3 -c "import json; p=json.load(open('$out/repository-index.json', encoding='utf-8')); assert p['parse_error_count'] == 0; print('repository index: PASS', p['module_count'], 'modules')"
```

### PowerShell

```powershell
$out = Join-Path $PWD 'research-output'
New-Item -ItemType Directory -Force $out | Out-Null
python skills/deepest-research/scripts/repo_parser.py `
  skills/deepest-research/scripts `
  --fail-on-parse-error `
  --output (Join-Path $out 'repository-index.json')
$report = Get-Content (Join-Path $out 'repository-index.json') -Raw | ConvertFrom-Json
if ($report.parse_error_count -ne 0) { throw 'repository index contains parse errors' }
"repository index: PASS $($report.module_count) modules"
```

Expected result: the JSON report records `runtime_class` as a static repository preprocessor, `parse_error_count` as zero for a healthy source tree, and a `repository_structure` for the Python files. The parser does not import project modules, resolve dynamic imports, or prove runtime behavior.

## Turn a question into a research path

Use the following procedure when the request is broader than a lookup.

### Before you start

- State the decision or knowledge gap.
- State the primary question and necessary subquestions.
- Classify the intended claim: descriptive, interpretive, associational, predictive, causal, evaluative, constructive, or synthetic.
- Name the population/system, unit or grain, context, and timeframe.
- List supplied papers, datasets, code, notes, prototypes, and access constraints.
- Define what observation would change the answer.

### Procedure

1. Frame the question before selecting a method.

   Expected result: the question has a target, claim type, context, and decision consequence.

2. Build complementary search lanes: direct evidence, mechanism, comparison, failure, implementation, citation graph, and adjacent domain when relevant.

   Expected result: search terms include domain vocabulary, formal constructs, synonyms, mechanisms, failure terms, and implementation identifiers.

3. Inspect the method, data grain, procedure, parameters, output, assumptions, evaluation, baselines, limitations, and code/data/model artefacts for sources that change the plan.

   Expected result: each material source has a method/mechanism card rather than a conclusion-only summary.

4. Compare at least two materially different approaches when the choice matters.

   Expected result: the comparison states which claim each approach supports, what data and measurement it needs, its threats, cost, reuse path, and fallback.

5. Design the smallest study or computational experiment that can support the intended conclusion.

   Expected result: sampling/cases, measures, acquisition, missingness, baseline, analysis, uncertainty, sensitivity, stopping, and failure recovery are explicit.

6. Search for prior art and reusable implementations before proposing custom engineering.

   Expected result: the plan names `reuse`, `configure`, `adapt`, `compose`, `reimplement`, or `research further`, with the reason and adaptation cost.

7. Run a disconfirmation pass.

   Expected result: the plan includes a strongest competing hypothesis, falsifier, alternative measure or denominator, boundary context, negative evidence, and a cheaper baseline where relevant.

8. Convert the selected approach into `input → action → method/tool → output → decision rule → next branch`.

   Expected result: another operator can identify the next command or evidence request without guessing.

### Verify

Stop when additional credible evidence is unlikely to change the method set, leading explanation, design choice, important failure boundary, reuse decision, or next action. Record residual uncertainty and the highest-value unresolved test.

## Preserve evidence and provenance

Every source-specific claim must be traceable to inspected evidence. Keep a source record with:

- relative path or canonical URL and revision/date;
- source hash where the utility emits one;
- the exact locator, excerpt, table cell, or line range used;
- the claim type and scope;
- assumptions, contradictions, and open questions;
- the action or decision changed by the evidence.

When a utility produces a result, record the query or input, source/feed hash, method/ranker/model, dependency version, domain/language, thresholds, normalization mode, unsupported-value policy, and complete candidate pool where applicable. Grounding an exact string establishes source occurrence and offsets; it does not establish that the source means the extracted value.

Do not present a smoke fixture, static parse, or successful command as empirical evidence. Use `NOT RUN` when the model, weights, endpoint, optional package, or shell required for a stage is unavailable.

## Use the utilities

Read `--help` for the exact interface before running a utility. The table below gives the supported path and the evidence boundary.

### Inspect Python repositories

```bash
python skills/deepest-research/scripts/repo_parser.py REPOSITORY \
  --output OUTPUT.json \
  --fail-on-parse-error
```

The parser covers `**/*.py`, records modules, classes, functions, signatures, imports, local import edges, and parse errors, and never imports or executes project code. Treat dynamic imports and runtime call paths as unresolved until separately tested.

### Curate and deduplicate a local corpus

```bash
python skills/deepest-research/scripts/scan.py \
  --input CORPUS_OR_DIRECTORY \
  --output curated-corpus.json \
  --text-field text \
  --id-field id \
  --normalization casefold-space \
  --dedup-method word-ngram \
  --dedup-threshold 0.80 \
  --representative longest
```

`scan.py` loads local JSON, JSONL, or text collections, applies declared quality filters, hashes records, and exact/near-deduplicates them. Record the input inventory, text field, normalization, method, threshold, representative policy, exclusions, and retained/rejected counts. `--min-karma` is an inclusion rule, not a credibility score.

### Ground extracted values against source text

For nested JSON values:

```bash
python skills/deepest-research/scripts/hybrid-rag-verifier.py \
  --source article.txt \
  --target extraction.json \
  --mode exact \
  --unsupported keep \
  --output grounding-report.json
```

Use `--mode normalized` only when the transformation is part of the evidence record. Use `--fail-on-ungrounded` when an unmatched value should fail the command. `byte-Identity.py` provides the corresponding table-cell path with exact or normalized UTF-8 offsets and optional all-occurrence reporting.

Expected result: the report contains source hashes, paths, offsets, coverage, and unmatched or unsupported cells. Review unmatched values and semantic meaning before accepting the extraction.

### Preprocess or integrate structured extraction

```bash
python skills/deepest-research/scripts/mixed-ie-parser.py preprocess \
  --file source.txt --output preprocessed.json
python skills/deepest-research/scripts/mixed-ie-parser.py integrate \
  --tuples extracted-tuples.json --output integrated.json
```

The adapter path accepts JSON on stdin and returns JSON on stdout. Preprocessing candidates are not model-extracted facts. Integration validates global tuples, records duplicates and conflicts, and preserves provenance.

### Retrieve and rank literature

Live arXiv retrieval:

```bash
python skills/deepest-research/scripts/literature-explorer.py \
  --query 'all:"research question"' \
  --max-results 20 \
  --ranker bm25 \
  --ranking-query 'mechanism implementation failure' \
  --save-feed raw-feed.xml \
  --output literature-report.json
```

For reproducible review, prefer a saved Atom feed or JSON record set with `--input-feed` or `--input-json`. Preserve the original query, retrieval date, endpoint/feed hash, complete candidate pool, ranker settings, and optional reranker command/version. A single query or ranked shortlist is a discovery result, not a complete systematic search.

### Plan context windows

When a tokenizer is available, use exact token windows:

```bash
python skills/deepest-research/scripts/context_window.py \
  --text-file source.txt \
  --tokenizer TOKENIZER_OR_ENCODING \
  --context-limit 32768 \
  --reserved-output 4000 \
  --chunk-tokens 8000 \
  --overlap-tokens 400 \
  --order-policy edge-first \
  --output context-budget.json
```

For a portable estimate, omit `--tokenizer` and use `--chars-per-token` with `--chunk-chars` and `--overlap-chars`. The `edge-first` value is scheduling metadata; it does not infer relevance. Record the tokenizer/model or estimation ratio, prompt overhead, reserved output, context limit, chunk policy, and ordering.

### Build a hierarchy or integrate concepts

```bash
python skills/deepest-research/scripts/hierarchography.py cluster \
  --documents documents.json \
  --output hierarchy.json \
  --markdown hierarchy.md
```

The `cluster` path is a deterministic standard-library TF-IDF baseline. `integrate` validates supplied concepts, and `run-adapter` invokes a JSON-in/JSON-out concept induction command. Label the baseline separately from model-induced concepts and inspect evidence-quote diagnostics.

### Aggregate independent reasoning paths

```bash
python skills/deepest-research/scripts/self-consistency-voting.py \
  --candidates sampled-paths.json \
  --mode majority \
  --normalization compact \
  --minimum-share 0.60 \
  --output consensus.json
```

Weighted mode requires `--weight-field`; resonance retains disagreement patterns. Record prompt/model/sampling conditions, path independence, answer normalization, vote distribution, and tie/minimum-share rules. Aggregation does not replace an external correctness check.

### Compute agreement or sample size

```bash
python skills/deepest-research/scripts/intercoder.py \
  --kind cohen --matrix coding-matrix.json --output kappa.json
python skills/deepest-research/scripts/sample_size.py \
  --margin 0.05 --confidence 0.95 --proportion 0.50 \
  --design-effect 1.0 --attrition 0.10 --output sample-size.json
```

Declare coding units, category set, missing-value handling, prevalence, and disagreement review for kappa. Declare the estimand, confidence, margin, anticipated proportion, design effect, population, attrition, and sampling assumptions for sample size. These calculators do not validate the target population or independence assumptions.

### Run Fast-DetectGPT paths

Analytic criterion:

```bash
python skills/deepest-research/scripts/probability_curvature.py criterion \
  --input logits.json --output curvature.json
```

Calibration consumes labelled criterion JSONL and requires sampling/scoring model names. Model-backed `detect` requires compatible Hugging Face model/tokenizer dependencies and weights. Record reference/scoring models, tokenizer compatibility, truncation, language/domain, threshold/profile source, and dependency versions. Bundled profiles are compatibility presets, not universal calibration.

### Train or apply the headline model

```bash
python skills/deepest-research/scripts/hypothetically_popular.py train \
  --input randomized-headline-tests.csv \
  --output headline-model.json
python skills/deepest-research/scripts/hypothetically_popular.py predict \
  --model headline-model.json \
  --first 'First headline' --second 'Second headline' \
  --output headline-comparison.json
```

Training uses within-experiment headline pairs and writes a model artifact. Prediction uses only a saved model; `features` exposes the transparent feature vector. Record archive version, exclusions and risk flags, outcome definition, group-level split, metrics, coefficients, date range, and target population.

### Audit rigor and lint a plan

```bash
python skills/deepest-research/scripts/curie-rigor-monitor.py audit \
  --code experiment.py --output intra-arm.json
python skills/deepest-research/scripts/curie-rigor-monitor.py audit-plan \
  --plan experiment-plan.json --output inter-arm.json
python skills/deepest-research/scripts/curie-rigor-monitor.py verify-run \
  --manifest execution-knowledge.json --output execution-report.json
python skills/deepest-research/scripts/plan_lint.py \
  research-plan.md --strict --json-output plan-lint.json
```

Static setup evidence is not execution evidence. A complete run claim requires a verified manifest and existing hashed artifacts. Plan lint checks the supported Markdown/JSON contract; it is not domain-expert or ethics approval.

## Run the explicit-stage pipeline

The pipeline is useful when several supported local stages belong in one isolated run.

### Preconditions

- Bash and a `python3`-compatible interpreter.
- An output directory outside the source tree.
- At least one explicit stage input such as `--source`, `--candidates`, `--repository`, `--corpus`, `--context-text`, or another documented input.
- Inputs for any dependent stage, such as `--source` with `--extractions` or `--context-text` with `--context-limit`.

### Procedure

1. Preview the interface:

   ```bash
   bash skills/deepest-research/scripts/execute-research-pipeline.sh --help
   ```

   Expected result: the explicit stage flags and output contract are displayed.

2. Run a dry-run with an isolated output directory:

   ```bash
   bash skills/deepest-research/scripts/execute-research-pipeline.sh \
     --output-dir research-output/pipeline-preview \
     --repository skills/deepest-research/scripts \
     --dry-run
   ```

   Expected result: `pipeline_status.json` reports `NOT_RUN` and records the planned command.

3. Run the requested stage without `--dry-run`:

   ```bash
   bash skills/deepest-research/scripts/execute-research-pipeline.sh \
     --output-dir research-output/pipeline \
     --repository skills/deepest-research/scripts
   ```

   Expected result: the stage writes its report and the final manifest records a return code and `PASS` or `FAIL` for the requested stage.

4. Inspect `pipeline_steps.tsv`, each stage’s stdout/stderr log, and `pipeline_status.json`.

   Expected result: every requested stage has an independently inspectable command, return code, log path, and output path.

### Verify

`PASS` means the requested command returned zero. Read the producing report under that script’s method contract before interpreting a research result. The pipeline does not infer omitted stages, repair invalid inputs, or manufacture dummy scientific outputs.

## Interpret statuses and reports

| Status | Meaning | Action |
| --- | --- | --- |
| `PASS` | The command completed with a zero return code or the deterministic check passed | Inspect the report and method evidence before using the result |
| `WARN` | The tool completed with a bounded issue or heuristic limitation | Resolve or explicitly carry the limitation |
| `FAIL` | The command or validation gate failed | Inspect stderr/report, fix the input or environment, then rerun |
| `NOT RUN` | A dry-run or unavailable gate did not execute | Do not present a result; record the missing prerequisite |

Keep lexical ranking, dense ranking, hybrid fusion, reranking, model-backed inference, source occurrence, structural parsing, and scientific validity as separate claims. A ranked result is a locator. Open the canonical source before using it as factual evidence.

## Troubleshoot by symptom

| Symptom | Check first | Recovery | Verify |
| --- | --- | --- | --- |
| `NOT_RUN` in pipeline report | `dry_run` and stage log | Remove `--dry-run` and rerun in a fresh output directory | Stage has return code and output |
| `pipeline ... requires` error | Flag dependency in `--help` | Supply required companion input, such as `--context-limit` | Re-run help and command |
| Parse error in repository index | `parse_error_count` and source path | Fix syntax or remove the path from the intended scope | Re-run with `--fail-on-parse-error` |
| Unsupported or unmatched grounding value | Grounding report mode/policy and source bytes | Inspect the source, choose exact/normalized mode deliberately, or retain `null`/`na`/value per policy | Report contains offsets or explicit unmatched state |
| Literature results too narrow | Query, endpoint/feed hash, ranker, and candidate pool | Expand search lanes and use a saved feed for reproducibility | Preserve all query reports and screening decisions |
| Dense/model adapter unavailable | Dependency, model, weights, endpoint, and auth | Use a local analytic/baseline path or record `NOT RUN` | Record exact runtime and evidence boundary |
| Static index has no runtime edges | Parser’s static runtime class and dynamic import limitation | Run the relevant project separately | Add direct runtime evidence if needed |
| Plan lint fails | Report check and line/field | Repair schema, placeholders, or evidence locator | Re-run `--strict` |

Do not repeat a failed destructive or high-consequence action without first capturing the symptom, input, report, and relevant source. For this package’s local utilities, fixes are usually input, dependency, or interpretation corrections; external provider/model failures need their own environment diagnostics.

## Runtime limits

- The repository does not include a host-independent installer or a Python package manifest for the skill itself.
- The local utilities are not a single importable API; use the documented command entry points and inspect source when embedding them.
- Optional dense retrieval, rerankers, model inference, adapters, and network retrieval are conditional on the target environment.
- `repo_parser.py` is static and cannot establish runtime call paths or dynamic imports.
- Grounding checks source occurrence and offsets; they do not prove semantic correctness.
- A pipeline, lint, parse, or smoke result is execution evidence, not proof that a research conclusion is correct.
- No `LICENSE` file is present in the current repository; clarify reuse terms before redistribution.
