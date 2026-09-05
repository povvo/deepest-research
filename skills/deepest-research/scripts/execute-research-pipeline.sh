#!/usr/bin/env bash
# Source-grounded research-planner orchestration harness.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
OUTPUT_DIR=""
DRY_RUN=0

SOURCE=""
EXTRACTIONS=""
EXTRACTOR_COMMAND=""
CANDIDATES=""
CODE=""
EXPERIMENT_SPEC=""
CURIE_PLAN=""
RUN_MANIFEST=""
RESEARCH_PLAN=""
PAPERS=""
CONCEPTS=""
CONCEPT_ADAPTER=""
REPOSITORY=""
CORPUS=""
CONTEXT_TEXT=""
CONTEXT_LIMIT=""
CURVATURE_LOGITS=""
CURVATURE_PROFILE=""
CURVATURE_THRESHOLD=""
HEADLINE_DATA=""
HEADLINE_MODEL=""

usage() {
  cat <<'EOF'
usage: execute-research-pipeline.sh --output-dir DIR [explicit stages]

Run selected research-planner tools with real inputs and write a command/evidence
manifest. No stage is inferred from a query and no dummy scientific result is
generated.

Core options:
  --output-dir DIR          Required isolated output directory.
  --dry-run                 Print commands without executing them.
  -h, --help                Show this help.

Extraction and grounding:
  --source FILE             Preprocess source text with mixed-ie-parser.
  --extractor-command CMD   With --source, run the JSON extractor adapter.
  --extractions FILE        With --source, verify structured values in source.

Aggregation and rigor:
  --candidates FILE         Aggregate independent paths by self-consistency.
  --code FILE               Run Curie Intra-ARM static setup audit.
  --experiment-spec FILE    Optional experiment specification for --code.
  --curie-plan FILE         Run Curie Inter-ARM plan audit.
  --run-manifest FILE       Verify Curie Experiment Knowledge/run evidence.
  --research-plan FILE      Lint a saved research plan.

Mapping, code, and corpus:
  --papers FILE             Build the deterministic hierarchy baseline.
  --concepts FILE           With --papers, integrate induced concepts.
  --concept-adapter CMD     With --papers, invoke concept induction adapter.
  --repository DIR          Build a static Python repository index.
  --corpus PATH             Curate and deduplicate a local corpus.
  --context-text FILE       Build a context budget/window report.
  --context-limit TOKENS    Required with --context-text.

Model/statistical components:
  --curvature-logits FILE   Compute Fast-DetectGPT criterion from logits JSON.
  --curvature-profile NAME  Optional built-in/profile JSON.
  --curvature-threshold X   Optional declared epsilon.
  --headline-data CSV       Train a within-experiment engagement model.
  --headline-model FILE     Required output model path with --headline-data.

Environment:
  PYTHON_BIN                Python interpreter, default python3.

Each stage writes its own report beneath --output-dir. The final
pipeline_status.json contains the exact command, return code, stdout/stderr log
paths, and PASS/FAIL state for every requested stage.
EOF
}

die() {
  printf 'execute-research-pipeline: %s\n' "$*" >&2
  exit 2
}

require_value() {
  [[ $# -ge 2 ]] || die "missing value for $1"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-dir) require_value "$@"; OUTPUT_DIR="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    --source) require_value "$@"; SOURCE="$2"; shift 2 ;;
    --extractions) require_value "$@"; EXTRACTIONS="$2"; shift 2 ;;
    --extractor-command) require_value "$@"; EXTRACTOR_COMMAND="$2"; shift 2 ;;
    --candidates) require_value "$@"; CANDIDATES="$2"; shift 2 ;;
    --code) require_value "$@"; CODE="$2"; shift 2 ;;
    --experiment-spec) require_value "$@"; EXPERIMENT_SPEC="$2"; shift 2 ;;
    --curie-plan) require_value "$@"; CURIE_PLAN="$2"; shift 2 ;;
    --run-manifest) require_value "$@"; RUN_MANIFEST="$2"; shift 2 ;;
    --research-plan|--plan) require_value "$@"; RESEARCH_PLAN="$2"; shift 2 ;;
    --papers) require_value "$@"; PAPERS="$2"; shift 2 ;;
    --concepts) require_value "$@"; CONCEPTS="$2"; shift 2 ;;
    --concept-adapter) require_value "$@"; CONCEPT_ADAPTER="$2"; shift 2 ;;
    --repository) require_value "$@"; REPOSITORY="$2"; shift 2 ;;
    --corpus) require_value "$@"; CORPUS="$2"; shift 2 ;;
    --context-text) require_value "$@"; CONTEXT_TEXT="$2"; shift 2 ;;
    --context-limit) require_value "$@"; CONTEXT_LIMIT="$2"; shift 2 ;;
    --curvature-logits) require_value "$@"; CURVATURE_LOGITS="$2"; shift 2 ;;
    --curvature-profile) require_value "$@"; CURVATURE_PROFILE="$2"; shift 2 ;;
    --curvature-threshold) require_value "$@"; CURVATURE_THRESHOLD="$2"; shift 2 ;;
    --headline-data) require_value "$@"; HEADLINE_DATA="$2"; shift 2 ;;
    --headline-model) require_value "$@"; HEADLINE_MODEL="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[[ -n "$OUTPUT_DIR" ]] || die "--output-dir is required"
[[ -z "$EXTRACTIONS" || -n "$SOURCE" ]] || die "--extractions requires --source"
[[ -z "$EXTRACTOR_COMMAND" || -n "$SOURCE" ]] || die "--extractor-command requires --source"
[[ -z "$EXPERIMENT_SPEC" || -n "$CODE" ]] || die "--experiment-spec requires --code"
[[ -z "$CONCEPTS" || -n "$PAPERS" ]] || die "--concepts requires --papers"
[[ -z "$CONCEPT_ADAPTER" || -n "$PAPERS" ]] || die "--concept-adapter requires --papers"
[[ -z "$CONCEPTS" || -z "$CONCEPT_ADAPTER" ]] || die "choose --concepts or --concept-adapter, not both"
[[ -z "$CONTEXT_TEXT" || -n "$CONTEXT_LIMIT" ]] || die "--context-text requires --context-limit"
[[ -z "$CONTEXT_LIMIT" || -n "$CONTEXT_TEXT" ]] || die "--context-limit requires --context-text"
[[ -z "$HEADLINE_DATA" || -n "$HEADLINE_MODEL" ]] || die "--headline-data requires --headline-model"

REQUESTED="$SOURCE$EXTRACTIONS$CANDIDATES$CODE$CURIE_PLAN$RUN_MANIFEST$RESEARCH_PLAN$PAPERS$REPOSITORY$CORPUS$CONTEXT_TEXT$CURVATURE_LOGITS$HEADLINE_DATA"
[[ -n "$REQUESTED" ]] || die "request at least one explicit stage"

mkdir -p "$OUTPUT_DIR"
STEP_LOG="$OUTPUT_DIR/pipeline_steps.tsv"
: > "$STEP_LOG"
PIPELINE_FAILED=0

command_string() {
  printf '%q ' "$@"
}

run_step() {
  local name="$1"
  shift
  local stdout_log="$OUTPUT_DIR/${name}.stdout.log"
  local stderr_log="$OUTPUT_DIR/${name}.stderr.log"
  local command
  command="$(command_string "$@")"
  printf '[%s] %s\n' "$name" "$command"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf '%s\t%s\t%s\t%s\t%s\n' "$name" "NOT_RUN" "$stdout_log" "$stderr_log" "$command" >> "$STEP_LOG"
    return 0
  fi
  "$@" >"$stdout_log" 2>"$stderr_log"
  local rc=$?
  printf '%s\t%s\t%s\t%s\t%s\n' "$name" "$rc" "$stdout_log" "$stderr_log" "$command" >> "$STEP_LOG"
  if [[ "$rc" -ne 0 ]]; then
    PIPELINE_FAILED=1
    printf '[%s] FAIL (return code %s)\n' "$name" "$rc" >&2
  else
    printf '[%s] PASS\n' "$name"
  fi
  return 0
}

if [[ -n "$SOURCE" ]]; then
  if [[ -n "$EXTRACTOR_COMMAND" ]]; then
    run_step "mixed_ie_adapter" "$PYTHON_BIN" "$SCRIPT_DIR/mixed-ie-parser.py" run-adapter \
      --file "$SOURCE" --extractor-command "$EXTRACTOR_COMMAND" \
      --output "$OUTPUT_DIR/mixed_ie.json" --raw-output "$OUTPUT_DIR/mixed_ie_raw.json" || true
  else
    run_step "mixed_ie_preprocess" "$PYTHON_BIN" "$SCRIPT_DIR/mixed-ie-parser.py" preprocess \
      --file "$SOURCE" --output "$OUTPUT_DIR/mixed_ie_preprocess.json" || true
  fi
fi

if [[ -n "$SOURCE" && -n "$EXTRACTIONS" ]]; then
  run_step "grounding" "$PYTHON_BIN" "$SCRIPT_DIR/hybrid-rag-verifier.py" \
    --source "$SOURCE" --target "$EXTRACTIONS" --mode normalized \
    --output "$OUTPUT_DIR/grounding_report.json" || true
fi

if [[ -n "$CANDIDATES" ]]; then
  run_step "self_consistency" "$PYTHON_BIN" "$SCRIPT_DIR/self-consistency-voting.py" \
    --candidates "$CANDIDATES" --output "$OUTPUT_DIR/self_consistency.json" || true
fi

if [[ -n "$CODE" ]]; then
  cmd=("$PYTHON_BIN" "$SCRIPT_DIR/curie-rigor-monitor.py" audit --code "$CODE" --output "$OUTPUT_DIR/curie_intra_arm.json")
  [[ -z "$EXPERIMENT_SPEC" ]] || cmd+=(--spec "$EXPERIMENT_SPEC")
  run_step "curie_intra_arm" "${cmd[@]}" || true
fi

if [[ -n "$CURIE_PLAN" ]]; then
  run_step "curie_inter_arm" "$PYTHON_BIN" "$SCRIPT_DIR/curie-rigor-monitor.py" audit-plan \
    --plan "$CURIE_PLAN" --output "$OUTPUT_DIR/curie_inter_arm.json" || true
fi

if [[ -n "$RUN_MANIFEST" ]]; then
  run_step "curie_experiment_knowledge" "$PYTHON_BIN" "$SCRIPT_DIR/curie-rigor-monitor.py" verify-run \
    --manifest "$RUN_MANIFEST" --output "$OUTPUT_DIR/curie_experiment_knowledge.json" || true
fi

if [[ -n "$RESEARCH_PLAN" ]]; then
  run_step "plan_lint" "$PYTHON_BIN" "$SCRIPT_DIR/plan_lint.py" "$RESEARCH_PLAN" \
    --format auto --strict --json-output "$OUTPUT_DIR/plan_lint.json" || true
fi

if [[ -n "$PAPERS" ]]; then
  if [[ -n "$CONCEPTS" ]]; then
    run_step "concept_integration" "$PYTHON_BIN" "$SCRIPT_DIR/hierarchography.py" integrate \
      --documents "$PAPERS" --concepts "$CONCEPTS" \
      --output "$OUTPUT_DIR/concepts.json" --markdown "$OUTPUT_DIR/concepts.md" || true
  elif [[ -n "$CONCEPT_ADAPTER" ]]; then
    run_step "concept_induction" "$PYTHON_BIN" "$SCRIPT_DIR/hierarchography.py" run-adapter \
      --documents "$PAPERS" --adapter-command "$CONCEPT_ADAPTER" \
      --output "$OUTPUT_DIR/concepts.json" --markdown "$OUTPUT_DIR/concepts.md" \
      --save-adapter-input "$OUTPUT_DIR/concept_adapter_input.json" \
      --save-adapter-output "$OUTPUT_DIR/concept_adapter_output.json" || true
  else
    run_step "hierarchy_baseline" "$PYTHON_BIN" "$SCRIPT_DIR/hierarchography.py" cluster \
      --documents "$PAPERS" --output "$OUTPUT_DIR/hierarchy_baseline.json" \
      --markdown "$OUTPUT_DIR/hierarchy_baseline.md" || true
  fi
fi

if [[ -n "$REPOSITORY" ]]; then
  run_step "repository_index" "$PYTHON_BIN" "$SCRIPT_DIR/repo_parser.py" "$REPOSITORY" \
    --output "$OUTPUT_DIR/repository_index.json" || true
fi

if [[ -n "$CORPUS" ]]; then
  run_step "corpus_curation" "$PYTHON_BIN" "$SCRIPT_DIR/scan.py" \
    --input "$CORPUS" --output "$OUTPUT_DIR/curated_corpus.json" || true
fi

if [[ -n "$CONTEXT_TEXT" ]]; then
  run_step "context_budget" "$PYTHON_BIN" "$SCRIPT_DIR/context_window.py" \
    --text-file "$CONTEXT_TEXT" --context-limit "$CONTEXT_LIMIT" \
    --output "$OUTPUT_DIR/context_budget.json" || true
fi

if [[ -n "$CURVATURE_LOGITS" ]]; then
  cmd=("$PYTHON_BIN" "$SCRIPT_DIR/probability_curvature.py" criterion --input "$CURVATURE_LOGITS" --output "$OUTPUT_DIR/curvature.json")
  [[ -z "$CURVATURE_PROFILE" ]] || cmd+=(--profile "$CURVATURE_PROFILE")
  [[ -z "$CURVATURE_THRESHOLD" ]] || cmd+=(--threshold "$CURVATURE_THRESHOLD")
  run_step "fast_detectgpt_criterion" "${cmd[@]}" || true
fi

if [[ -n "$HEADLINE_DATA" ]]; then
  run_step "headline_model_train" "$PYTHON_BIN" "$SCRIPT_DIR/hypothetically_popular.py" train \
    --input "$HEADLINE_DATA" --output "$HEADLINE_MODEL" || true
fi

"$PYTHON_BIN" - "$STEP_LOG" "$OUTPUT_DIR/pipeline_status.json" "$DRY_RUN" <<'PY'
import json
import sys
from pathlib import Path

step_log = Path(sys.argv[1])
output = Path(sys.argv[2])
dry_run = bool(int(sys.argv[3]))
steps = []
for line in step_log.read_text(encoding="utf-8").splitlines():
    if not line:
        continue
    name, rc_raw, stdout, stderr, command = line.split("\t", 4)
    if rc_raw == "NOT_RUN":
        status = "NOT_RUN"
        rc = None
    else:
        rc = int(rc_raw)
        status = "PASS" if rc == 0 else "FAIL"
    steps.append({
        "name": name,
        "status": status,
        "return_code": rc,
        "command": command,
        "stdout_log": stdout,
        "stderr_log": stderr,
    })
overall = "NOT_RUN" if dry_run else ("PASS" if all(s["status"] == "PASS" for s in steps) else "FAIL")
report = {
    "tool": "execute-research-pipeline",
    "runtime_class": "orchestrator",
    "status": overall,
    "dry_run": dry_run,
    "steps": steps,
    "interpretation": (
        "Pipeline status reports command execution only. Interpret each scientific "
        "result under the producing script's method and operating contract."
    ),
}
output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({"status": overall, "manifest": str(output), "steps": len(steps)}))
raise SystemExit(0 if overall in {"PASS", "NOT_RUN"} else 1)
PY
exit $?
