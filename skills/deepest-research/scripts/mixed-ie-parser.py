#!/usr/bin/env python3
"""Mixed information extraction: code AST, text preprocessing, and T³ integration.

The text pipeline is grounded in Text-to-Table and Text-Tuple-Table. It keeps
model generation and deterministic integration separate:

1. ``preprocess`` segments documents and emits corpus statistics/keyword
   candidates for a schema-free or schema-guided extractor.
2. ``integrate`` validates globally extracted tuples, deduplicates them, and
   materializes a JSON table with source locators.
3. ``run-adapter`` invokes a caller-supplied non-interactive extractor command
   over the preprocessed payload and then applies the same integration checks.

``code`` retains the original AST ontology function for repository inputs.
No regex co-occurrence graph is silently represented as a learned Text-to-Table
model.
"""

from __future__ import annotations

import argparse
import ast
import collections
import json
import math
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence


METHOD = {
    "sources": [
        "Text-to-Table: A New Way of Information Extraction",
        "Text-Tuple-Table: Towards Information Integration in Text-to-Table Generation via Global Tuple Extraction",
    ],
    "pipeline": ["text", "global tuples", "integrated table"],
}
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "by", "for", "from",
    "has", "have", "in", "into", "is", "it", "of", "on", "or", "that", "the",
    "their", "this", "to", "was", "were", "will", "with",
}


def expression_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = expression_name(node.value)
        return f"{prefix}.{node.attr}".lstrip(".")
    try:
        return ast.unparse(node)
    except Exception:
        return type(node).__name__


class CodebaseOntologyExtractor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.classes: list[dict[str, Any]] = []
        self.functions: list[dict[str, Any]] = []
        self.imports: list[dict[str, Any]] = []
        self.globals: list[dict[str, Any]] = []
        self.calls: list[dict[str, Any]] = []
        self._class_stack: list[str] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append(
                {"module": alias.name, "alias": alias.asname, "line": node.lineno}
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            self.imports.append(
                {
                    "module": node.module,
                    "name": alias.name,
                    "alias": alias.asname,
                    "level": node.level,
                    "line": node.lineno,
                }
            )
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        info = {
            "name": node.name,
            "line": node.lineno,
            "bases": [expression_name(base) for base in node.bases],
            "methods": [
                {
                    "name": child.name,
                    "line": child.lineno,
                    "args": [argument.arg for argument in child.args.args],
                }
                for child in node.body
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
            ],
        }
        self.classes.append(info)
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if not self._class_stack:
            self.functions.append(
                {
                    "name": node.name,
                    "line": node.lineno,
                    "args": [argument.arg for argument in node.args.args],
                    "returns": expression_name(node.returns) if node.returns else None,
                }
            )
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.visit_FunctionDef(node)  # type: ignore[arg-type]

    def visit_Assign(self, node: ast.Assign) -> None:
        if not self._class_stack and isinstance(getattr(node, "col_offset", 1), int) and node.col_offset == 0:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.globals.append({"name": target.id, "line": node.lineno})
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        self.calls.append({"callee": expression_name(node.func), "line": node.lineno})
        self.generic_visit(node)

    def result(self) -> dict[str, Any]:
        return {
            "classes": self.classes,
            "functions": self.functions,
            "imports": self.imports,
            "globals": self.globals,
            "calls": self.calls,
        }


def parse_code(path: Path) -> dict[str, Any]:
    source = path.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(source, filename=str(path))
    extractor = CodebaseOntologyExtractor()
    extractor.visit(tree)
    return {
        "type": "code_ast",
        "method": METHOD,
        "source": str(path),
        "ontology": extractor.result(),
    }


def segment_text(text: str, max_chars: int, overlap_chars: int) -> list[dict[str, Any]]:
    if max_chars <= 0 or overlap_chars < 0 or overlap_chars >= max_chars:
        raise ValueError("Require max_chars > overlap_chars >= 0.")
    paragraphs = [
        (match.start(), match.group().strip())
        for match in re.finditer(r"(?:^|\n\s*\n)(.*?)(?=\n\s*\n|\Z)", text, flags=re.DOTALL)
        if match.group().strip()
    ]
    segments: list[dict[str, Any]] = []
    current_parts: list[str] = []
    current_start: int | None = None
    current_end = 0

    def flush() -> None:
        nonlocal current_parts, current_start, current_end
        if not current_parts or current_start is None:
            return
        content = "\n\n".join(current_parts)
        segments.append(
            {
                "segment_id": f"segment-{len(segments)+1}",
                "char_start": current_start,
                "char_end": current_end,
                "text": content,
            }
        )
        if overlap_chars:
            tail = content[-overlap_chars:]
            current_parts = [tail]
            current_start = max(current_start, current_end - len(tail))
        else:
            current_parts = []
            current_start = None

    for start, paragraph in paragraphs:
        end = start + len(paragraph)
        if len(paragraph) > max_chars:
            flush()
            step = max_chars - overlap_chars
            for local_start in range(0, len(paragraph), step):
                chunk = paragraph[local_start: local_start + max_chars]
                segments.append(
                    {
                        "segment_id": f"segment-{len(segments)+1}",
                        "char_start": start + local_start,
                        "char_end": start + local_start + len(chunk),
                        "text": chunk,
                    }
                )
                if local_start + max_chars >= len(paragraph):
                    break
            continue
        projected = sum(len(part) for part in current_parts) + 2 * len(current_parts) + len(paragraph)
        if current_parts and projected > max_chars:
            flush()
        if current_start is None:
            current_start = start
        current_parts.append(paragraph)
        current_end = end
    flush()
    if not segments and text:
        segments.append(
            {
                "segment_id": "segment-1",
                "char_start": 0,
                "char_end": len(text),
                "text": text,
            }
        )
    return segments


def tokens(text: str) -> list[str]:
    return [
        token.casefold()
        for token in re.findall(r"\b[\w-]{2,}\b", text, flags=re.UNICODE)
        if token.casefold() not in STOPWORDS
    ]


def corpus_keywords(segments: Sequence[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
    term_frequency: collections.Counter[str] = collections.Counter()
    document_frequency: collections.Counter[str] = collections.Counter()
    for segment in segments:
        segment_tokens = tokens(segment["text"])
        term_frequency.update(segment_tokens)
        document_frequency.update(set(segment_tokens))
    total_docs = max(1, len(segments))
    scored = []
    for term, tf in term_frequency.items():
        idf = math.log((1 + total_docs) / (1 + document_frequency[term])) + 1.0
        scored.append(
            {
                "term": term,
                "term_frequency": tf,
                "document_frequency": document_frequency[term],
                "tf_idf": tf * idf,
            }
        )
    return sorted(scored, key=lambda row: (-row["tf_idf"], row["term"]))[:top_k]


def preprocess_text(path: Path, max_chars: int, overlap_chars: int, top_k: int) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    segments = segment_text(text, max_chars, overlap_chars)
    return {
        "type": "text_preprocessing",
        "method": METHOD,
        "source": str(path),
        "character_count": len(text),
        "segments": segments,
        "keyword_candidates": corpus_keywords(segments, top_k),
        "extractor_contract": {
            "input": "each segment text plus optional schema",
            "output": {
                "tuples": [
                    {
                        "subject": "string",
                        "relation": "string",
                        "object": "JSON scalar or object",
                        "attributes": "object, optional",
                        "segment_id": "string",
                        "evidence_quote": "literal source span",
                    }
                ]
            },
        },
    }


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).casefold()


def load_tuple_payload(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, dict) and isinstance(data.get("tuples"), list):
        data = data["tuples"]
    if not isinstance(data, list):
        raise ValueError("Tuple payload must be an array or an object containing a tuples array.")
    result = []
    for index, row in enumerate(data):
        if not isinstance(row, dict):
            raise ValueError(f"Tuple {index} is not an object.")
        missing = [key for key in ("subject", "relation", "object") if key not in row]
        if missing:
            raise ValueError(f"Tuple {index} is missing: {', '.join(missing)}.")
        result.append(row)
    return result


def integrate_tuples(
    tuples: Sequence[dict[str, Any]],
    *,
    key_fields: Sequence[str],
) -> dict[str, Any]:
    deduplicated: list[dict[str, Any]] = []
    seen: set[tuple[str, ...]] = set()
    duplicates: list[int] = []
    for index, row in enumerate(tuples):
        key = tuple(canonical(row.get(field)) for field in key_fields)
        if key in seen:
            duplicates.append(index)
            continue
        seen.add(key)
        deduplicated.append(dict(row))

    # Wide materialization: one row per subject, relation names become columns.
    by_subject: dict[str, dict[str, Any]] = {}
    conflicts: list[dict[str, Any]] = []
    for row in deduplicated:
        subject = str(row["subject"])
        relation = str(row["relation"])
        table_row = by_subject.setdefault(subject, {"subject": row["subject"], "_provenance": {}})
        if relation in table_row and canonical(table_row[relation]) != canonical(row["object"]):
            conflicts.append(
                {
                    "subject": subject,
                    "relation": relation,
                    "existing": table_row[relation],
                    "candidate": row["object"],
                    "candidate_segment_id": row.get("segment_id"),
                }
            )
            existing = table_row[relation]
            if not isinstance(existing, list):
                table_row[relation] = [existing]
            if row["object"] not in table_row[relation]:
                table_row[relation].append(row["object"])
        else:
            table_row[relation] = row["object"]
        table_row["_provenance"].setdefault(relation, []).append(
            {
                "segment_id": row.get("segment_id"),
                "evidence_quote": row.get("evidence_quote"),
                "attributes": row.get("attributes"),
            }
        )
    return {
        "type": "text_tuple_table",
        "method": METHOD,
        "statistics": {
            "input_tuples": len(tuples),
            "deduplicated_tuples": len(deduplicated),
            "duplicates_removed": len(duplicates),
            "subjects": len(by_subject),
            "integration_conflicts": len(conflicts),
        },
        "global_tuples": deduplicated,
        "table": [by_subject[key] for key in sorted(by_subject)],
        "conflicts": conflicts,
        "duplicate_input_indices": duplicates,
    }


def run_adapter(command: str, payload: dict[str, Any], timeout: float) -> Any:
    argv = shlex.split(command)
    if not argv:
        raise ValueError("Extractor command is empty.")
    completed = subprocess.run(
        argv,
        input=json.dumps(payload, ensure_ascii=False),
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"Extractor command exited {completed.returncode}: {completed.stderr.strip()}"
        )
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Extractor command did not return JSON on stdout.") from exc


def write(data: dict[str, Any], output: str) -> None:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    path.write_text(payload, encoding="utf-8")
    print(payload, end="")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preprocess text, integrate global tuples, or inventory Python AST symbols."
    )
    subparsers = parser.add_subparsers(dest="command")

    code = subparsers.add_parser("code", help="Create an AST ontology from one Python file.")
    code.add_argument("--file", required=True)
    code.add_argument("--output", default="ie_code_ontology.json")

    preprocess = subparsers.add_parser("preprocess", help="Segment text and emit extraction candidates.")
    preprocess.add_argument("--file", required=True)
    preprocess.add_argument("--output", default="ie_preprocessed.json")
    preprocess.add_argument("--max-chars", type=int, default=6000)
    preprocess.add_argument("--overlap-chars", type=int, default=400)
    preprocess.add_argument("--top-keywords", type=int, default=100)

    integrate = subparsers.add_parser("integrate", help="Validate and integrate extracted global tuples.")
    integrate.add_argument("--tuples", required=True)
    integrate.add_argument("--output", default="ie_table.json")
    integrate.add_argument(
        "--key-field",
        action="append",
        default=["subject", "relation", "object"],
        help="Tuple deduplication field; repeatable.",
    )

    adapter = subparsers.add_parser(
        "run-adapter",
        help="Preprocess text, invoke a JSON-in/JSON-out extractor, and integrate tuples.",
    )
    adapter.add_argument("--file", required=True)
    adapter.add_argument("--extractor-command", required=True)
    adapter.add_argument("--schema", help="Optional JSON schema passed to the extractor.")
    adapter.add_argument("--output", default="ie_table.json")
    adapter.add_argument("--raw-output", help="Optional path for raw extractor JSON.")
    adapter.add_argument("--timeout", type=float, default=600.0)
    adapter.add_argument("--max-chars", type=int, default=6000)
    adapter.add_argument("--overlap-chars", type=int, default=400)
    adapter.add_argument("--top-keywords", type=int, default=100)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0
    try:
        if args.command == "code":
            result = parse_code(Path(args.file))
            write(result, args.output)
        elif args.command == "preprocess":
            result = preprocess_text(
                Path(args.file), args.max_chars, args.overlap_chars, args.top_keywords
            )
            write(result, args.output)
        elif args.command == "integrate":
            payload = json.loads(Path(args.tuples).read_text(encoding="utf-8"))
            result = integrate_tuples(load_tuple_payload(payload), key_fields=args.key_field)
            write(result, args.output)
        elif args.command == "run-adapter":
            payload = preprocess_text(
                Path(args.file), args.max_chars, args.overlap_chars, args.top_keywords
            )
            if args.schema:
                payload["schema"] = json.loads(Path(args.schema).read_text(encoding="utf-8"))
            raw = run_adapter(args.extractor_command, payload, args.timeout)
            if args.raw_output:
                Path(args.raw_output).write_text(
                    json.dumps(raw, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )
            result = integrate_tuples(load_tuple_payload(raw), key_fields=["subject", "relation", "object"])
            result["adapter_command"] = shlex.split(args.extractor_command)
            write(result, args.output)
        else:
            raise ValueError(f"Unknown command {args.command}")
    except (
        OSError,
        ValueError,
        RuntimeError,
        subprocess.TimeoutExpired,
        json.JSONDecodeError,
        SyntaxError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
