#!/usr/bin/env python3
"""Lint Markdown or JSON research plans produced by the research-planner skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

REQUIRED_MARKDOWN_HEADINGS = [
    "Plan Snapshot",
    "Decision, Contribution, and Scope",
    "Assumptions and Unknowns",
    "Research Questions and Inferential Targets",
    "Conceptual, Causal, or Logic Model",
    "Evidence Baseline and Search Strategy",
    "Design Options and Selection",
    "Sampling, Cases, or Corpus",
    "Constructs, Measures, and Data Collection",
    "Analysis and Interpretation Plan",
    "Validity, Robustness, and Boundary Tests",
    "Ethics, Bias, Governance, and Stakeholders",
    "Reproducibility and Provenance",
    "Feasibility, Risks, and Contingencies",
    "Execution Roadmap and Decision Gates",
    "Unresolved Items",
]

ALLOWED_EPISTEMIC_STATUS = {
    "Verified",
    "Inference",
    "Assumption",
    "Proposal",
    "Unknown",
}

PLACEHOLDER_PATTERNS = [
    re.compile(r"\{\{[^{}\n]+\}\}"),
    re.compile(r"\b(?:TBD|TODO|CHANGEME)\b", re.IGNORECASE),
    re.compile(r"\[(?:INSERT|PLACEHOLDER)[^\]]*\]", re.IGNORECASE),
]


def check(name: str, status: str, message: str, evidence: Any | None = None) -> dict[str, Any]:
    item: dict[str, Any] = {"check": name, "status": status, "message": message}
    if evidence is not None:
        item["evidence"] = evidence
    return item


def detect_format(path: Path, requested: str) -> str:
    if requested != "auto":
        return requested
    if path.suffix.lower() == ".json":
        return "json"
    if path.suffix.lower() in {".md", ".markdown"}:
        return "markdown"
    text = path.read_text(encoding="utf-8", errors="replace").lstrip()
    return "json" if text.startswith(("{", "[")) else "markdown"


def find_placeholders(text: str) -> list[str]:
    found: list[str] = []
    for pattern in PLACEHOLDER_PATTERNS:
        found.extend(match.group(0) for match in pattern.finditer(text))
    return sorted(set(found))


def section_content(body: str, heading: str) -> str:
    pattern = re.compile(
        rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(body)
    return match.group(1).strip() if match else ""


def lint_markdown(path: Path, strict: bool) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    checks: list[dict[str, Any]] = []

    if text.strip():
        checks.append(check("file.nonempty", "PASS", "Plan file is non-empty"))
    else:
        return [check("file.nonempty", "FAIL", "Plan file is empty")]

    headings = re.findall(r"^## (.+?)\s*$", text, re.MULTILINE)
    missing = [heading for heading in REQUIRED_MARKDOWN_HEADINGS if heading not in headings]
    if missing:
        checks.append(check("markdown.required-headings", "FAIL", "Required headings are missing", missing))
    else:
        checks.append(check("markdown.required-headings", "PASS", "All required headings are present"))

    positions = [headings.index(heading) for heading in REQUIRED_MARKDOWN_HEADINGS if heading in headings]
    if len(positions) == len(REQUIRED_MARKDOWN_HEADINGS) and positions == sorted(positions):
        checks.append(check("markdown.heading-order", "PASS", "Required headings appear in contract order"))
    elif len(positions) == len(REQUIRED_MARKDOWN_HEADINGS):
        checks.append(check("markdown.heading-order", "FAIL", "Required headings are out of order", headings))

    duplicates = sorted({heading for heading in headings if headings.count(heading) > 1})
    if duplicates:
        checks.append(check("markdown.duplicate-headings", "FAIL", "Duplicate level-two headings found", duplicates))
    else:
        checks.append(check("markdown.duplicate-headings", "PASS", "No duplicate level-two headings"))

    empty_sections = [
        heading for heading in REQUIRED_MARKDOWN_HEADINGS
        if heading in headings and not section_content(text, heading)
    ]
    if empty_sections:
        checks.append(check("markdown.section-content", "FAIL", "Required sections contain no content", empty_sections))
    else:
        checks.append(check("markdown.section-content", "PASS", "Required sections contain content"))

    if strict and "Completion Record" not in headings:
        checks.append(check("markdown.completion-record", "FAIL", "Strict saved plans require a Completion Record section"))
    elif "Completion Record" in headings:
        content = section_content(text, "Completion Record")
        status = "PASS" if content else "FAIL"
        checks.append(check("markdown.completion-record", status, "Completion Record is present" if content else "Completion Record is empty"))
    else:
        checks.append(check("markdown.completion-record", "WARN", "Completion Record is recommended for saved plans"))

    placeholders = find_placeholders(text)
    if placeholders:
        status = "FAIL" if strict else "WARN"
        checks.append(check("content.placeholders", status, "Unresolved placeholders found", placeholders[:25]))
    else:
        checks.append(check("content.placeholders", "PASS", "No unresolved placeholders found"))

    statuses = sorted(status for status in ALLOWED_EPISTEMIC_STATUS if re.search(rf"\b{status}\b", text))
    if "Proposal" not in statuses:
        checks.append(check("epistemic.proposal", "FAIL" if strict else "WARN", "No Proposal label found; future work may be confused with completed work"))
    else:
        checks.append(check("epistemic.proposal", "PASS", "Future work is explicitly labelled Proposal"))
    if len(statuses) < 2:
        checks.append(check("epistemic.variety", "FAIL" if strict else "WARN", "Fewer than two epistemic status labels are used", statuses))
    else:
        checks.append(check("epistemic.variety", "PASS", "Multiple epistemic states are visible", statuses))

    unsupported_statuses = sorted(set(
        match.group(1)
        for match in re.finditer(
            r"(?:\[|\*\*)(Fact|Certain|Confirmed|Completed)(?:\]|\*\*)",
            text,
            re.IGNORECASE,
        )
    ))
    if unsupported_statuses:
        checks.append(check("epistemic.unsupported-labels", "WARN", "Potentially ambiguous status labels found; use the five allowed labels", unsupported_statuses))
    else:
        checks.append(check("epistemic.unsupported-labels", "PASS", "No ambiguous status labels detected"))

    overclaim_patterns = {
        "execution": r"\b(?:we ran|was executed|experiment (?:was )?run|search (?:was )?completed|analysis (?:was )?completed)\b",
        "observed_result": r"\b(?:results? (?:show|showed|demonstrate|demonstrated)|we found|achieved an? .*?(?:accuracy|effect|improvement))\b",
        "novelty": r"\b(?:first[- ]ever|unprecedented|entirely novel|proven novel)\b",
    }
    overclaims: dict[str, list[str]] = {}
    for category, pattern in overclaim_patterns.items():
        matches = [m.group(0) for m in re.finditer(pattern, text, re.IGNORECASE)]
        if matches:
            overclaims[category] = sorted(set(matches))
    if overclaims:
        checks.append(check(
            "content.overclaim-review",
            "WARN",
            "Language that may claim execution, observations, or novelty requires source or command evidence",
            overclaims,
        ))
    else:
        checks.append(check("content.overclaim-review", "PASS", "No obvious execution, result, or novelty overclaim phrases detected"))

    causal_language = bool(re.search(r"\b(?:causes?|causal effect|effect of .+ on)\b", text, re.IGNORECASE))
    causal_support = bool(re.search(
        r"\b(?:identification|counterfactual|confounder|randomi[sz]|difference-in-differences|"
        r"instrumental variable|regression discontinuity|causal diagram|DAG|associational)\b|"
        r"\b(?:not|no|without|avoid|downgrade\w*)\b[^.\n]{0,50}\bcausal\b",
        text,
        re.IGNORECASE,
    ))
    if causal_language and not causal_support:
        checks.append(check("content.causal-support", "WARN", "Causal language found without an obvious identification or downgrade term"))
    else:
        checks.append(check("content.causal-support", "PASS", "Causal language is absent, identified, or explicitly bounded"))

    return checks


def resolve_ref(schema_root: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise ValueError(f"Only local JSON Schema references are supported: {ref}")
    node: Any = schema_root
    for token in ref[2:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or token not in node:
            raise ValueError(f"Unresolvable JSON Schema reference: {ref}")
        node = node[token]
    if not isinstance(node, dict):
        raise ValueError(f"JSON Schema reference is not an object: {ref}")
    return node


def type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def validate_schema(
    value: Any,
    schema: dict[str, Any],
    schema_root: dict[str, Any],
    path: str = "$",
) -> list[str]:
    errors: list[str] = []

    if "$ref" in schema:
        try:
            target = resolve_ref(schema_root, str(schema["$ref"]))
        except ValueError as exc:
            return [f"{path}: {exc}"]
        return validate_schema(value, target, schema_root, path)

    expected_type = schema.get("type")
    if isinstance(expected_type, str) and not type_matches(value, expected_type):
        return [f"{path}: expected {expected_type}, got {type(value).__name__}"]

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value {value!r} is not one of {schema['enum']!r}")

    if isinstance(value, str):
        minimum = schema.get("minLength")
        if isinstance(minimum, int) and len(value) < minimum:
            errors.append(f"{path}: string length {len(value)} is below {minimum}")
        if schema.get("format") == "date":
            try:
                date.fromisoformat(value)
            except ValueError:
                errors.append(f"{path}: expected ISO date YYYY-MM-DD")

    if isinstance(value, list):
        minimum = schema.get("minItems")
        if isinstance(minimum, int) and len(value) < minimum:
            errors.append(f"{path}: array length {len(value)} is below {minimum}")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(validate_schema(item, item_schema, schema_root, f"{path}[{index}]"))

    if isinstance(value, dict):
        minimum = schema.get("minProperties")
        if isinstance(minimum, int) and len(value) < minimum:
            errors.append(f"{path}: object has {len(value)} properties; minimum is {minimum}")

        required = schema.get("required", [])
        if isinstance(required, list):
            for key in required:
                if key not in value:
                    errors.append(f"{path}: missing required property {key!r}")

        properties = schema.get("properties", {})
        if not isinstance(properties, dict):
            properties = {}
        for key, child_schema in properties.items():
            if key in value and isinstance(child_schema, dict):
                errors.extend(validate_schema(value[key], child_schema, schema_root, f"{path}.{key}"))

        additional = schema.get("additionalProperties", True)
        extra = sorted(set(value) - set(properties))
        if additional is False and extra:
            errors.append(f"{path}: unexpected properties {extra!r}")
        elif isinstance(additional, dict):
            for key in extra:
                errors.extend(validate_schema(value[key], additional, schema_root, f"{path}.{key}"))

    return errors


def walk_objects(value: Any, path: str = "$"):
    if isinstance(value, dict):
        yield path, value
        for key, child in value.items():
            yield from walk_objects(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_objects(child, f"{path}[{index}]")


def lint_json(path: Path, schema_path: Path, strict: bool) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [check("json.parse", "FAIL", "Plan is not valid JSON", {"line": exc.lineno, "column": exc.colno, "error": exc.msg})]
    checks.append(check("json.parse", "PASS", "Plan parses as JSON"))

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return checks + [check("json.schema-load", "FAIL", "Schema could not be loaded", str(exc))]
    checks.append(check("json.schema-load", "PASS", "Schema loaded", str(schema_path)))

    errors = validate_schema(data, schema, schema)
    if errors:
        checks.append(check("json.schema", "FAIL", "Plan violates the bundled schema", errors[:100]))
    else:
        checks.append(check("json.schema", "PASS", "Plan satisfies the supported schema constraints"))

    placeholders = find_placeholders(json.dumps(data, ensure_ascii=False))
    if placeholders:
        checks.append(check("content.placeholders", "FAIL" if strict else "WARN", "Unresolved placeholders found", placeholders[:25]))
    else:
        checks.append(check("content.placeholders", "PASS", "No unresolved placeholders found"))

    verified_without_locator: list[str] = []
    completed_without_evidence: list[str] = []
    statuses: set[str] = set()
    for object_path, obj in walk_objects(data):
        status = obj.get("status")
        if isinstance(status, str) and status in ALLOWED_EPISTEMIC_STATUS:
            statuses.add(status)
            if status == "Verified" and not str(obj.get("evidence_locator", "")).strip():
                verified_without_locator.append(object_path)
        if obj.get("status") == "COMPLETE":
            evidence = str(obj.get("completion_evidence", "")).strip()
            if not evidence or evidence.lower() in {"none", "n/a", "not applicable", "proposed"}:
                completed_without_evidence.append(object_path)

    if verified_without_locator:
        checks.append(check(
            "epistemic.verified-locator",
            "FAIL" if strict else "WARN",
            "Verified objects lack evidence_locator",
            verified_without_locator,
        ))
    else:
        checks.append(check("epistemic.verified-locator", "PASS", "Verified objects include locators or no Verified object is present"))

    if completed_without_evidence:
        checks.append(check(
            "execution.complete-evidence",
            "FAIL",
            "COMPLETE roadmap stages lack objective completion evidence",
            completed_without_evidence,
        ))
    else:
        checks.append(check("execution.complete-evidence", "PASS", "No unsupported COMPLETE roadmap stage found"))

    if "Proposal" not in statuses:
        checks.append(check("epistemic.proposal", "FAIL" if strict else "WARN", "No Proposal status object found"))
    else:
        checks.append(check("epistemic.proposal", "PASS", "Future work is explicitly labelled Proposal"))

    return checks


def build_report(path: Path, plan_format: str, strict: bool, checks: list[dict[str, Any]]) -> dict[str, Any]:
    failed = sum(item["status"] == "FAIL" for item in checks)
    warnings = sum(item["status"] == "WARN" for item in checks)
    passed = sum(item["status"] == "PASS" for item in checks)
    return {
        "status": "PASS" if failed == 0 else "FAIL",
        "path": str(path.resolve()),
        "format": plan_format,
        "strict": strict,
        "checks": checks,
        "summary": {
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "total": len(checks),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lint a research plan against the research-planner Markdown or JSON output contract."
    )
    parser.add_argument("path", help="Path to a Markdown or JSON research plan")
    parser.add_argument(
        "--format",
        choices=("auto", "markdown", "json"),
        default="auto",
        help="Input format; auto uses the extension and content",
    )
    parser.add_argument(
        "--schema",
        help="JSON Schema path; defaults to templates/research-plan.schema.json beside the skill",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on unresolved placeholders and missing saved-plan completion metadata",
    )
    parser.add_argument(
        "--json-output",
        help="Write the full lint report to this JSON file",
    )
    args = parser.parse_args()

    path = Path(args.path).expanduser()
    if not path.is_file():
        parser.error(f"Plan file not found: {path}")

    plan_format = detect_format(path, args.format)
    schema_path = (
        Path(args.schema).expanduser()
        if args.schema
        else Path(__file__).resolve().parent.parent / "templates" / "research-plan.schema.json"
    )

    try:
        checks = (
            lint_markdown(path, args.strict)
            if plan_format == "markdown"
            else lint_json(path, schema_path, args.strict)
        )
    except OSError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2

    report = build_report(path, plan_format, args.strict, checks)

    if args.json_output:
        output = Path(args.json_output).expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(
        f"{report['status']}: {path} "
        f"({report['summary']['passed']} passed, "
        f"{report['summary']['failed']} failed, "
        f"{report['summary']['warnings']} warnings)"
    )
    for item in checks:
        if item["status"] != "PASS":
            print(f"{item['status']}: {item['check']}: {item['message']}")
            if "evidence" in item:
                print(json.dumps(item["evidence"], ensure_ascii=False, indent=2))

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
