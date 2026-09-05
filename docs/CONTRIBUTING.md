# Contributing to Deepest Research

This guide is for maintainers and contributors changing the skill contract, host metadata, assets, references, templates, scripts, workflows, or project documentation.

## Reader outcome

After reading this guide, a contributor can identify the canonical source for a change, run the checks that match the changed path, inspect the exact diff, and release a revision with its remote and workflow state verified.

## Contribution boundary

Keep implementation-significant claims tied to the current source or a reproduced observation. Preserve the distinction between a method’s scientific source, a local implementation, a command execution, and a research conclusion. Do not add fabricated citations, benchmark numbers, provider availability, or claims of novelty.

The repository currently has no `LICENSE` file. Do not add a licensing claim to a new document until the owner provides the applicable terms. Keep internal ledgers, local author paths, and generated reports outside the repository.

## Source map

| Area | Canonical source | Change together when |
| --- | --- | --- |
| Agent behavior and evidence boundary | `skills/deepest-research/SKILL.md` | Method stages, constraints, output contract, or resource routing change |
| Host discovery metadata | `skills/deepest-research/agents/openai.yaml` | Display name, description, default prompt, or implicit invocation changes |
| Read-only proposer role | `skills/deepest-research/agents/research-proposer.toml` | Input contract, reasoning effort, sandbox, or output behavior changes |
| Reusable prompt assets | `skills/deepest-research/assets/` | A prompt’s task, schema, method boundary, or evidence requirement changes |
| Method/evidence references | `skills/deepest-research/references/` | A script’s scientific grounding, compatibility, or interpretation boundary changes |
| Executable utilities | `skills/deepest-research/scripts/` | CLI flags, report schemas, dependencies, or runtime behavior changes |
| Plan/evidence templates | `skills/deepest-research/templates/` | Supported saved-plan or ledger shape changes |
| Public orientation and procedures | `README.md`, `docs/USER_GUIDE.md` | Reader entry path, command examples, limitations, or recovery changes |

The `references/script-method-map.md` file is the canonical crosswalk for bundled scripts. Read it before modifying or interpreting a script. When a script changes its interface or method boundary, update the map, relevant user-guide section, examples, and checks together.

## Local setup

The local utilities target Python 3 and use standard-library modules unless a selected path requires optional packages or external providers. No project dependency installation is required for the structural checks below. The Bash orchestrator requires Bash and defaults to `python3`.

Create reports outside the source tree:

```bash
mkdir -p /tmp/deepest-research-checks
```

On Windows, use a directory such as `research-output/` and remove it after inspection if it is not part of the change. Do not write generated indexes, model caches, credentials, or provider output into `skills/deepest-research/`.

## Validation workflow

Run the checks that match the changed surface.

### Python syntax and static structure

```bash
python -m compileall -q skills/deepest-research/scripts
python skills/deepest-research/scripts/repo_parser.py \
  skills/deepest-research/scripts \
  --fail-on-parse-error \
  --output /tmp/deepest-research-checks/repository-index.json
```

Expected result: compileall exits zero and the report has `parse_error_count: 0`. This proves syntax and static parsing for the selected files; it does not prove runtime behavior.

### CLI surface

Run `--help` on the changed utility and its subcommands. For example:

```bash
python skills/deepest-research/scripts/literature-explorer.py --help
python skills/deepest-research/scripts/probability_curvature.py --help
python skills/deepest-research/scripts/mixed-ie-parser.py --help
bash skills/deepest-research/scripts/execute-research-pipeline.sh --help
```

The last command requires Bash.

### Meaningful local fixtures

Use small explicit fixtures to exercise the changed contract:

```bash
python skills/deepest-research/scripts/context_window.py \
  --chars 2400 --context-limit 8192 --chunk-chars 1000 \
  --overlap-chars 100 --output /tmp/deepest-research-checks/context.json
python skills/deepest-research/scripts/sample_size.py \
  --margin 0.05 --confidence 0.95 --proportion 0.5 \
  --output /tmp/deepest-research-checks/sample-size.json
python skills/deepest-research/scripts/intercoder.py \
  --demo --output /tmp/deepest-research-checks/kappa.json
```

For grounding changes, use a source text containing one known value and one absent value, then verify exact/normalized offsets and the selected unsupported policy. For extraction, run preprocessing and integration with a small tuple fixture. For plan lint, run a valid fixture and a deliberate invalid fixture and inspect the exit status and JSON report.

### Pipeline checks

Preview first, then run one real local stage:

```bash
bash skills/deepest-research/scripts/execute-research-pipeline.sh \
  --output-dir /tmp/deepest-research-checks/pipeline-preview \
  --repository skills/deepest-research/scripts --dry-run
bash skills/deepest-research/scripts/execute-research-pipeline.sh \
  --output-dir /tmp/deepest-research-checks/pipeline \
  --repository skills/deepest-research/scripts
```

Inspect `pipeline_steps.tsv`, stage logs, and `pipeline_status.json`. A pipeline `PASS` means command completion. It does not establish scientific validity or external model/provider availability.

### Documentation checks

Run the public documentation audits after editing the manuals. They are heuristics, so follow them with a literal walkthrough of every command example.

```bash
python "$TASKS_SKILL/scripts/cli.py" audit README.md --format json
python "$TASKS_SKILL/scripts/cli.py" audit docs/USER_GUIDE.md --format json
python "$TASKS_SKILL/scripts/cli.py" audit docs/CONTRIBUTING.md --format json
```

Set `TASKS_SKILL` to the installed Agent Documentation Skills Tasks directory in your environment. Keep generated audit output outside the repository.

## Add or change a utility

1. State the research or engineering job and why an existing utility cannot support it.
2. Choose a method source and record what it establishes, what it does not establish, assumptions, baselines, and failure modes.
3. Define explicit input/output schemas, provenance fields, status behavior, and an independent verification path.
4. Implement a standard-library path when practical. Make optional model/provider dependencies explicit and fail or warn without fabricating fallback evidence.
5. Add `--help`, deterministic small fixtures, meaningful error paths, and a method-map entry.
6. Add or update the relevant user-guide procedure and contributor validation command.
7. Run syntax, CLI, fixture, and documentation checks. Inspect the exact diff and preserve unrelated user changes.

Keep filenames stable when possible. If a rename is necessary, update source routing, links, method map, workflows, and release notes together.

## Add or change a reference, asset, or template

Write the reader job and evidence boundary at the top. Distinguish framework guidance from a project observation or measured result. For prompt assets, define the input fields, expected schema, failure behavior, and provenance requirements. For templates, keep placeholders explicit until a real example or generated output validates the shape.

Do not turn repeated citations, a ranking result, or a deterministic fixture into proof that a method works in every context. If the asset changes a script’s expected input or interpretation, update the script method map and a runnable fixture.

## Documentation rules

- Put the concrete product behavior before abstract positioning.
- Use exact commands, paths, flags, output names, and observable success signals.
- Keep preconditions before actions and recovery next to the relevant failure.
- State when a procedure does not apply.
- Preserve `PASS`, `WARN`, `FAIL`, and `NOT RUN` boundaries.
- Keep unknown host/provider/model behavior conditional.
- Link to the canonical source instead of duplicating mutable interface details without a reason.
- Do not publish internal metadata, local author paths, validation ledgers, or process reports.

## Pull request or release checklist

> **Warning:** Do not commit credentials, model caches, generated indexes, or provider output. Do not rewrite history or force-push. Preserve existing user changes, keep reports outside the source tree, and record external model/provider gates as `NOT RUN` when they were not executed.

- [ ] Existing user changes and the pre-change status were inspected and preserved.
- [ ] The source contract and method map were read for every changed implementation path.
- [ ] Documentation states the task boundary, prerequisites, action, expected result, decision branches, recovery, and verification.
- [ ] Python syntax and static repository parsing pass.
- [ ] Changed CLIs report `--help` successfully.
- [ ] Meaningful local fixtures pass, including a failure or unsupported-value path where relevant.
- [ ] Pipeline output and logs were inspected when the orchestrator changed.
- [ ] External model/provider gates are marked `NOT RUN` when unavailable.
- [ ] Markdown links, code paths, and examples resolve from the repository root.
- [ ] Exact diff and `git diff --check` were reviewed.
- [ ] Commit was created without rewriting history and pushed to the intended branch.
- [ ] Remote commit and relevant workflow status were read back at the pushed SHA.
- [ ] License status is stated accurately; this repository currently has no `LICENSE` file.

## Release and maintenance

After a release, record the exact commit SHA, branch, clean/dirty state, checks run, first-use result, and any unrun external gates in the release handoff outside the repository. Verify the remote branch points to the same SHA. Confirm workflow runs refer to that SHA; a green run on another revision is not release evidence.

Refresh the user guide when CLI flags, output schemas, source layout, supported model/provider paths, or host metadata change. Refresh the method map whenever scientific grounding, runtime class, or interpretation requirements change. Re-run the repository index and meaningful fixtures after source edits.
