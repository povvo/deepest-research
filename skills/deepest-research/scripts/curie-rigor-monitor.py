#!/usr/bin/env python3
"""Curie-style rigor monitor for research code and execution evidence.

Grounded in "Curie: Toward Rigorous and Automated Scientific Experimentation
with AI Agents." The tool implements three bounded modules:

* Intra-ARM setup audit: alignment between an experiment specification and
  code, input/output handling, placeholders, randomness, literal parameters,
  and intermediate evidence.
* Inter-ARM plan audit: fine-grained partitions, dependencies, permissible
  state transitions, and scheduling metadata.
* Experiment Knowledge verification: immutable command/run records, artifact
  hashes, repeated-run consistency, and a structured change history.

Static analysis and execution verification are reported separately. The tool
does not claim a run occurred unless a supplied manifest contains inspectable
run evidence and referenced artefacts pass their declared checks.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import shlex
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence


METHOD = {
    "name": "Curie-style rigor monitor",
    "source": "Curie: Toward Rigorous and Automated Scientific Experimentation with AI Agents",
    "modules": ["Intra-ARM", "Inter-ARM", "Experiment Knowledge Module"],
}

PLACEHOLDER_PATTERNS = {
    "todo": re.compile(r"\b(?:TODO|FIXME|XXX)\b", re.IGNORECASE),
    "not_implemented": re.compile(r"\bNotImplemented(?:Error)?\b"),
    "mock_or_dummy": re.compile(
        r"\b(?:mock|dummy|fake|placeholder)[_-]?(?:data|result|metric|output|generator)?\b",
        re.IGNORECASE,
    ),
    "ellipsis_statement": re.compile(r"^\s*\.\.\.\s*(?:#.*)?$", re.MULTILINE),
}
SEED_CALLS = {
    "random.seed",
    "numpy.random.seed",
    "np.random.seed",
    "torch.manual_seed",
    "torch.cuda.manual_seed",
    "torch.cuda.manual_seed_all",
    "transformers.set_seed",
    "set_seed",
}
RANDOM_CALL_PREFIXES = (
    "random.",
    "numpy.random.",
    "np.random.",
    "torch.rand",
    "torch.randn",
    "torch.randint",
)
OUTPUT_CALLS = {
    "open",
    "Path.write_text",
    "Path.write_bytes",
    "json.dump",
    "json.dumps",
    "csv.writer",
    "csv.DictWriter",
    "torch.save",
}
CONTROL_WORDS = re.compile(
    r"\b(control|baseline|comparator|placebo|holdout|negative[_ -]?control|ablation)\b",
    re.IGNORECASE,
)


@dataclass
class CodeFacts:
    imports: set[str]
    functions: set[str]
    classes: set[str]
    assignments: dict[str, Any]
    call_names: list[str]
    argparse_options: set[str]
    files_read: list[str]
    files_written: list[str]
    random_calls: list[str]
    seed_calls: list[str]


def node_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = node_name(node.value)
        return f"{prefix}.{node.attr}".lstrip(".")
    try:
        return ast.unparse(node)
    except Exception:
        return type(node).__name__


def literal_value(node: ast.AST) -> Any:
    try:
        return ast.literal_eval(node)
    except Exception:
        return None


class FactVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.facts = CodeFacts(set(), set(), set(), {}, [], set(), [], [], [], [])

    def visit_Import(self, node: ast.Import) -> None:
        self.facts.imports.update(alias.name for alias in node.names)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            self.facts.imports.add(node.module)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.facts.functions.add(node.name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.facts.functions.add(node.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.facts.classes.add(node.name)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        value = literal_value(node.value)
        if value is not None:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.facts.assignments[target.id] = value
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if isinstance(node.target, ast.Name) and node.value is not None:
            value = literal_value(node.value)
            if value is not None:
                self.facts.assignments[node.target.id] = value
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        name = node_name(node.func)
        self.facts.call_names.append(name)
        if name.endswith(".add_argument") or name == "add_argument":
            for argument in node.args:
                value = literal_value(argument)
                if isinstance(value, str) and value.startswith("-"):
                    self.facts.argparse_options.add(value)
        if name in SEED_CALLS:
            self.facts.seed_calls.append(name)
        if any(name.startswith(prefix) for prefix in RANDOM_CALL_PREFIXES) and name not in SEED_CALLS:
            self.facts.random_calls.append(name)
        if name == "open" and node.args:
            path = literal_value(node.args[0])
            mode = literal_value(node.args[1]) if len(node.args) > 1 else "r"
            if isinstance(path, str):
                if isinstance(mode, str) and any(flag in mode for flag in ("w", "a", "x", "+")):
                    self.facts.files_written.append(path)
                else:
                    self.facts.files_read.append(path)
        if name.endswith(".read_text") or name.endswith(".read_bytes"):
            owner = node_name(node.func.value) if isinstance(node.func, ast.Attribute) else ""
            self.facts.files_read.append(owner)
        if name.endswith(".write_text") or name.endswith(".write_bytes"):
            owner = node_name(node.func.value) if isinstance(node.func, ast.Attribute) else ""
            self.facts.files_written.append(owner)
        self.generic_visit(node)


def check(check_id: str, status: str, message: str, evidence: Any = None) -> dict[str, Any]:
    row = {"id": check_id, "status": status, "message": message}
    if evidence is not None:
        row["evidence"] = evidence
    return row


def load_json_object(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return data


def summarize_checks(rows: Sequence[dict[str, Any]]) -> dict[str, int | str]:
    counts = {key: sum(row["status"] == key for row in rows) for key in ("PASS", "FAIL", "WARN", "NOT_RUN")}
    overall = "FAIL" if counts["FAIL"] else ("WARN" if counts["WARN"] else "PASS")
    return {**counts, "overall": overall}


def inspect_code(path: Path) -> tuple[str, ast.AST | None, CodeFacts | None, list[dict[str, Any]]]:
    source = path.read_text(encoding="utf-8", errors="replace")
    rows: list[dict[str, Any]] = []
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        rows.append(
            check(
                "intra.syntax",
                "FAIL",
                f"Python syntax error at line {exc.lineno}: {exc.msg}",
            )
        )
        return source, None, None, rows
    rows.append(check("intra.syntax", "PASS", "Python AST parsed successfully."))
    visitor = FactVisitor()
    visitor.visit(tree)
    return source, tree, visitor.facts, rows


def spec_names(spec: dict[str, Any] | None, key: str) -> list[str]:
    if not spec:
        return []
    value = spec.get(key, [])
    if isinstance(value, dict):
        return [str(name) for name in value]
    if isinstance(value, list):
        names = []
        for item in value:
            if isinstance(item, str):
                names.append(item)
            elif isinstance(item, dict) and item.get("name"):
                names.append(str(item["name"]))
        return names
    return []


def audit_setup(code_path: Path, spec: dict[str, Any] | None) -> dict[str, Any]:
    source, tree, facts, rows = inspect_code(code_path)
    if tree is None or facts is None:
        return {
            "module": "Intra-ARM",
            "target": str(code_path),
            "checks": rows,
            "summary": summarize_checks(rows),
        }

    placeholders: dict[str, list[int]] = {}
    for name, pattern in PLACEHOLDER_PATTERNS.items():
        positions = [source.count("\n", 0, match.start()) + 1 for match in pattern.finditer(source)]
        if positions:
            placeholders[name] = positions
    rows.append(
        check(
            "intra.placeholders",
            "FAIL" if placeholders else "PASS",
            "Placeholder or mock markers found." if placeholders else "No placeholder or mock markers found.",
            placeholders or None,
        )
    )

    if facts.random_calls:
        rows.append(
            check(
                "intra.randomness",
                "PASS" if facts.seed_calls else "FAIL",
                (
                    "Random operations and seed calls are both present."
                    if facts.seed_calls
                    else "Random operations are present without a recognized seed call."
                ),
                {"random_calls": sorted(set(facts.random_calls)), "seed_calls": sorted(set(facts.seed_calls))},
            )
        )
    else:
        rows.append(check("intra.randomness", "PASS", "No recognized stochastic operation is present."))

    rows.append(
        check(
            "intra.interface",
            "PASS" if facts.argparse_options or "argparse" not in facts.imports else "WARN",
            (
                f"Discovered {len(facts.argparse_options)} command-line options."
                if facts.argparse_options
                else "No argparse options discovered; confirm the script's invocation contract."
            ),
            sorted(facts.argparse_options),
        )
    )
    rows.append(
        check(
            "intra.io",
            "PASS" if facts.files_written or "--output" in facts.argparse_options else "WARN",
            (
                "Output-writing evidence was found."
                if facts.files_written or "--output" in facts.argparse_options
                else "No output path or write operation was discovered."
            ),
            {"reads": facts.files_read, "writes": facts.files_written},
        )
    )

    metric_literals = {
        name: value
        for name, value in facts.assignments.items()
        if re.search(r"(accuracy|auc|f1|precision|recall|success|metric|score)", name, re.IGNORECASE)
        and isinstance(value, (int, float))
    }
    rows.append(
        check(
            "intra.metric_literals",
            "WARN" if metric_literals else "PASS",
            (
                "Metric-like literal assignments require provenance review."
                if metric_literals
                else "No metric-like literal assignments were found."
            ),
            metric_literals or None,
        )
    )

    path_literals = {
        name: value
        for name, value in facts.assignments.items()
        if isinstance(value, str)
        and (value.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", value))
    }
    rows.append(
        check(
            "intra.absolute_paths",
            "FAIL" if path_literals else "PASS",
            (
                "Absolute path literals make the setup environment-dependent."
                if path_literals
                else "No assigned absolute path literals were found."
            ),
            path_literals or None,
        )
    )

    rows.append(
        check(
            "intra.comparator",
            "PASS" if CONTROL_WORDS.search(source) else "WARN",
            (
                "Comparator/control language is present."
                if CONTROL_WORDS.search(source)
                else "No comparator/control language was found; it may be in the experiment spec."
            ),
        )
    )

    if spec is None:
        rows.append(
            check(
                "intra.spec_alignment",
                "NOT_RUN",
                "No experiment specification was supplied; question/variable alignment was not checked.",
            )
        )
    else:
        required_top = ["research_question", "independent_variables", "dependent_variables", "constants"]
        missing_top = [key for key in required_top if not spec.get(key)]
        rows.append(
            check(
                "intra.spec_fields",
                "FAIL" if missing_top else "PASS",
                (
                    f"Experiment specification is missing: {', '.join(missing_top)}"
                    if missing_top
                    else "Research question and variable classes are declared."
                ),
            )
        )
        declared = {
            *spec_names(spec, "independent_variables"),
            *spec_names(spec, "dependent_variables"),
            *spec_names(spec, "constants"),
        }
        searchable = set(facts.assignments) | facts.functions | facts.classes
        unresolved = sorted(
            name for name in declared
            if name and not any(name.casefold() in candidate.casefold() for candidate in searchable)
        )
        rows.append(
            check(
                "intra.variable_alignment",
                "WARN" if unresolved else "PASS",
                (
                    "Some declared variables were not found as code symbols."
                    if unresolved
                    else "Declared variables have candidate code symbols."
                ),
                unresolved or None,
            )
        )
        expected_outputs = spec.get("expected_outputs", [])
        output_options = {"--output", "--output-dir", "--report"} & facts.argparse_options
        rows.append(
            check(
                "intra.expected_outputs",
                "PASS" if not expected_outputs or facts.files_written or output_options else "FAIL",
                (
                    "Expected outputs have an apparent write/output interface."
                    if expected_outputs
                    else "No expected outputs were declared in the specification."
                ),
                expected_outputs,
            )
        )

    return {
        "module": "Intra-ARM",
        "target": str(code_path),
        "method": METHOD,
        "facts": {
            "imports": sorted(facts.imports),
            "functions": sorted(facts.functions),
            "classes": sorted(facts.classes),
            "argparse_options": sorted(facts.argparse_options),
            "random_calls": sorted(set(facts.random_calls)),
            "seed_calls": sorted(set(facts.seed_calls)),
        },
        "checks": rows,
        "summary": summarize_checks(rows),
    }


def audit_partitions(plan: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    partitions = plan.get("partitions")
    if not isinstance(partitions, list) or not partitions:
        rows.append(check("inter.partitions", "FAIL", "Plan must contain a non-empty partitions array."))
        return {
            "module": "Inter-ARM",
            "method": METHOD,
            "checks": rows,
            "summary": summarize_checks(rows),
        }

    ids: list[str] = []
    by_id: dict[str, dict[str, Any]] = {}
    duplicates: list[str] = []
    for index, partition in enumerate(partitions):
        if not isinstance(partition, dict) or not partition.get("id"):
            rows.append(check(f"inter.partition.{index}", "FAIL", "Partition needs an id."))
            continue
        partition_id = str(partition["id"])
        if partition_id in by_id:
            duplicates.append(partition_id)
        ids.append(partition_id)
        by_id[partition_id] = partition
    rows.append(
        check(
            "inter.unique_ids",
            "FAIL" if duplicates else "PASS",
            "Partition IDs are unique." if not duplicates else "Duplicate partition IDs found.",
            sorted(set(duplicates)) or None,
        )
    )

    unknown_dependencies: dict[str, list[str]] = {}
    missing_fields: dict[str, list[str]] = {}
    for partition_id, partition in by_id.items():
        required = ["objective", "owner", "state", "dependencies", "completion_evidence"]
        absent = [key for key in required if key not in partition]
        if absent:
            missing_fields[partition_id] = absent
        dependencies = partition.get("dependencies", [])
        if not isinstance(dependencies, list):
            dependencies = []
            missing_fields.setdefault(partition_id, []).append("dependencies:list")
        unknown = [str(value) for value in dependencies if str(value) not in by_id]
        if unknown:
            unknown_dependencies[partition_id] = unknown
    rows.append(
        check(
            "inter.partition_fields",
            "FAIL" if missing_fields else "PASS",
            "All partitions contain required control fields." if not missing_fields else "Partition control fields are missing.",
            missing_fields or None,
        )
    )
    rows.append(
        check(
            "inter.dependencies",
            "FAIL" if unknown_dependencies else "PASS",
            "All dependencies refer to known partitions." if not unknown_dependencies else "Unknown dependencies found.",
            unknown_dependencies or None,
        )
    )

    visiting: set[str] = set()
    visited: set[str] = set()
    cycle: list[str] = []

    def visit(node: str, trail: list[str]) -> bool:
        nonlocal cycle
        if node in visiting:
            start = trail.index(node) if node in trail else 0
            cycle = trail[start:] + [node]
            return True
        if node in visited:
            return False
        visiting.add(node)
        for dependency in by_id[node].get("dependencies", []):
            dependency = str(dependency)
            if dependency in by_id and visit(dependency, trail + [node]):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    for partition_id in by_id:
        if visit(partition_id, []):
            break
    rows.append(
        check(
            "inter.acyclic",
            "FAIL" if cycle else "PASS",
            "Dependency graph is acyclic." if not cycle else "Dependency cycle found.",
            cycle or None,
        )
    )

    allowed_states = set(plan.get("allowed_states", ["planned", "setup_validated", "running", "executed", "verified", "failed", "blocked"]))
    invalid_states = {
        partition_id: partition.get("state")
        for partition_id, partition in by_id.items()
        if partition.get("state") not in allowed_states
    }
    rows.append(
        check(
            "inter.states",
            "FAIL" if invalid_states else "PASS",
            "Partition states are permitted." if not invalid_states else "Invalid partition states found.",
            invalid_states or None,
        )
    )

    scheduler_fields = ["priority", "resource_requirements"]
    scheduler_missing = {
        partition_id: [key for key in scheduler_fields if key not in partition]
        for partition_id, partition in by_id.items()
        if any(key not in partition for key in scheduler_fields)
    }
    rows.append(
        check(
            "inter.scheduling",
            "WARN" if scheduler_missing else "PASS",
            (
                "Scheduling metadata are complete."
                if not scheduler_missing
                else "Some partitions lack priority or resource requirements."
            ),
            scheduler_missing or None,
        )
    )
    return {
        "module": "Inter-ARM",
        "method": METHOD,
        "partition_count": len(by_id),
        "checks": rows,
        "summary": summarize_checks(rows),
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_execution_manifest(manifest: dict[str, Any], base_dir: Path) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    command = manifest.get("command")
    return_code = manifest.get("return_code")
    rows.append(
        check(
            "knowledge.command",
            "PASS" if isinstance(command, (str, list)) and command else "FAIL",
            "Command is recorded." if command else "Execution command is missing.",
            command,
        )
    )
    rows.append(
        check(
            "knowledge.return_code",
            "PASS" if isinstance(return_code, int) else "FAIL",
            (
                f"Return code is recorded as {return_code}."
                if isinstance(return_code, int)
                else "Integer return code is missing."
            ),
        )
    )
    environment = manifest.get("environment")
    rows.append(
        check(
            "knowledge.environment",
            "PASS" if isinstance(environment, dict) and environment else "WARN",
            (
                "Environment metadata are recorded."
                if isinstance(environment, dict) and environment
                else "Environment metadata are missing or empty."
            ),
        )
    )

    artifacts = manifest.get("artifacts", [])
    artifact_results: list[dict[str, Any]] = []
    if not isinstance(artifacts, list):
        rows.append(check("knowledge.artifacts", "FAIL", "Artifacts must be an array."))
        artifacts = []
    for index, item in enumerate(artifacts):
        if not isinstance(item, dict) or not item.get("path"):
            artifact_results.append({"index": index, "status": "FAIL", "reason": "missing path"})
            continue
        path = Path(str(item["path"]))
        if not path.is_absolute():
            path = base_dir / path
        if not path.is_file():
            artifact_results.append({"path": str(path), "status": "FAIL", "reason": "not found"})
            continue
        actual = sha256_file(path)
        expected = item.get("sha256")
        if expected and actual != expected:
            artifact_results.append(
                {"path": str(path), "status": "FAIL", "expected_sha256": expected, "actual_sha256": actual}
            )
        else:
            artifact_results.append(
                {"path": str(path), "status": "PASS", "sha256": actual, "bytes": path.stat().st_size}
            )
    if artifacts:
        rows.append(
            check(
                "knowledge.artifacts",
                "FAIL" if any(item["status"] == "FAIL" for item in artifact_results) else "PASS",
                "Artifact existence and hashes checked.",
                artifact_results,
            )
        )
    else:
        rows.append(check("knowledge.artifacts", "WARN", "No output artifacts were declared."))

    repeats = manifest.get("repeated_runs", [])
    if not isinstance(repeats, list) or len(repeats) < 2:
        rows.append(
            check(
                "knowledge.repeated_runs",
                "NOT_RUN",
                "At least two repeated-run records are required for consistency checking.",
            )
        )
    else:
        signatures = []
        invalid = []
        for index, run in enumerate(repeats):
            if not isinstance(run, dict) or "return_code" not in run:
                invalid.append(index)
                continue
            signatures.append(
                (
                    run.get("return_code"),
                    json.dumps(run.get("metrics"), sort_keys=True, separators=(",", ":")),
                    json.dumps(run.get("artifact_hashes"), sort_keys=True, separators=(",", ":")),
                )
            )
        if invalid:
            rows.append(
                check(
                    "knowledge.repeated_runs",
                    "FAIL",
                    "Repeated-run records are incomplete.",
                    invalid,
                )
            )
        else:
            all_equal = len(set(signatures)) == 1
            rows.append(
                check(
                    "knowledge.repeated_runs",
                    "PASS" if all_equal else "WARN",
                    (
                        "Repeated-run signatures are identical."
                        if all_equal
                        else "Repeated-run signatures differ; inspect stochastic tolerance or hidden dependencies."
                    ),
                    {"count": len(signatures), "unique_signatures": len(set(signatures))},
                )
            )

    history = manifest.get("history", [])
    rows.append(
        check(
            "knowledge.history",
            "PASS" if isinstance(history, list) and history else "WARN",
            (
                "Structured change history is present."
                if isinstance(history, list) and history
                else "No structured change history is recorded."
            ),
        )
    )

    success_claim = (
        isinstance(return_code, int)
        and return_code == 0
        and not any(row["status"] == "FAIL" for row in rows)
        and bool(artifacts)
    )
    return {
        "module": "Experiment Knowledge Module",
        "method": METHOD,
        "manifest_status": "verified_execution_record" if success_claim else "incomplete_or_failed_record",
        "checks": rows,
        "summary": summarize_checks(rows),
    }


def emit(data: dict[str, Any], output: str | None) -> None:
    payload = json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True)
    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload + "\n", encoding="utf-8")
    print(payload)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Curie-style setup, partition, and execution-evidence rigor checks."
    )
    subparsers = parser.add_subparsers(dest="command")

    audit = subparsers.add_parser("audit", help="Run Intra-ARM static setup validation.")
    audit.add_argument("--code", required=True, help="Python research script.")
    audit.add_argument("--spec", help="Optional experiment specification JSON.")
    audit.add_argument("--output")

    plan = subparsers.add_parser("audit-plan", help="Run Inter-ARM partition/control-flow validation.")
    plan.add_argument("--plan", required=True, help="Partition plan JSON.")
    plan.add_argument("--output")

    verify = subparsers.add_parser("verify-run", help="Verify an execution knowledge manifest.")
    verify.add_argument("--manifest", required=True)
    verify.add_argument(
        "--base-dir",
        help="Base directory for relative artifact paths; defaults to the manifest directory.",
    )
    verify.add_argument("--output")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0
    try:
        if args.command == "audit":
            spec = load_json_object(Path(args.spec)) if args.spec else None
            result = audit_setup(Path(args.code), spec)
            emit(result, args.output)
        elif args.command == "audit-plan":
            plan = load_json_object(Path(args.plan))
            assert plan is not None
            result = audit_partitions(plan)
            emit(result, args.output)
        elif args.command == "verify-run":
            manifest_path = Path(args.manifest)
            manifest = load_json_object(manifest_path)
            assert manifest is not None
            base_dir = Path(args.base_dir) if args.base_dir else manifest_path.parent
            result = verify_execution_manifest(manifest, base_dir)
            emit(result, args.output)
        else:
            raise ValueError(f"Unknown command {args.command}")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
