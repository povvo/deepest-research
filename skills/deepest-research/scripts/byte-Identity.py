#!/usr/bin/env python3
"""DIGESTables-style cell grounding with exact or normalized source offsets.

The tool checks whether every rendered table cell occurs in one or more source
texts, records provenance offsets and excerpts, and can prune cells that fail
the declared matching contract. It implements source grounding; interpretation
and source quality remain separate review dimensions.

``exact`` compares Unicode text literally and also reports UTF-8 byte offsets.
``normalized`` performs case-folded whitespace-normalized matching while mapping
the match back to raw character and byte offsets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence


METHOD = {
    "name": "cell-level source grounding",
    "sources": [
        "ArxivDIGESTables: Synthesizing Scientific Literature into Tables using Language Models",
        "Schema-Driven Information Extraction from Heterogeneous Tables",
    ],
}
NULL_MARKERS = {"", "n/a", "na", "nan", "none", "null", "not applicable"}


@dataclass(frozen=True)
class SourceDocument:
    source_id: str
    path: str
    text: str

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()

    @property
    def utf8_bytes(self) -> int:
        return len(self.text.encode("utf-8"))


def normalize_with_map(text: str) -> tuple[str, list[int]]:
    """Return case-folded, collapsed-whitespace text and raw-char index map."""

    output: list[str] = []
    mapping: list[int] = []
    in_space = False
    for raw_index, char in enumerate(text):
        folded = char.casefold()
        if char.isspace():
            if output and not in_space:
                output.append(" ")
                mapping.append(raw_index)
            in_space = True
            continue
        in_space = False
        for folded_char in folded:
            output.append(folded_char)
            mapping.append(raw_index)
    while output and output[-1] == " ":
        output.pop()
        mapping.pop()
    return "".join(output), mapping


def utf8_offset(text: str, char_offset: int) -> int:
    return len(text[:char_offset].encode("utf-8"))


def locate(value: str, source: SourceDocument, mode: str) -> dict[str, Any] | None:
    if mode == "exact":
        start = source.text.find(value)
        if start < 0:
            return None
        end = start + len(value)
    else:
        normalized_source, index_map = normalize_with_map(source.text)
        normalized_value, _ = normalize_with_map(value)
        if not normalized_value:
            return None
        normalized_start = normalized_source.find(normalized_value)
        if normalized_start < 0:
            return None
        normalized_end = normalized_start + len(normalized_value)
        start = index_map[normalized_start]
        end = index_map[normalized_end - 1] + 1
    return {
        "source_id": source.source_id,
        "source_path": source.path,
        "match_mode": mode,
        "raw_char_offsets": [start, end],
        "utf8_byte_offsets": [utf8_offset(source.text, start), utf8_offset(source.text, end)],
        "matched_text": source.text[start:end],
        "excerpt": source.text[max(0, start - 60): min(len(source.text), end + 60)].replace("\n", " "),
    }


def iter_cells(table: Any) -> Iterable[tuple[list[Any], Any]]:
    """Yield JSON paths and scalar cells from an object or row array."""

    def walk(value: Any, path: list[Any]) -> Iterable[tuple[list[Any], Any]]:
        if isinstance(value, dict):
            for key, child in value.items():
                yield from walk(child, [*path, key])
        elif isinstance(value, list):
            for index, child in enumerate(value):
                yield from walk(child, [*path, index])
        else:
            yield path, value

    yield from walk(table, [])


def set_path(root: Any, path: Sequence[Any], value: Any) -> None:
    cursor = root
    for part in path[:-1]:
        cursor = cursor[part]
    cursor[path[-1]] = value


def json_path(parts: Sequence[Any]) -> str:
    rendered = "$"
    for part in parts:
        if isinstance(part, int):
            rendered += f"[{part}]"
        elif re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", str(part)):
            rendered += f".{part}"
        else:
            rendered += f"[{json.dumps(str(part))}]"
    return rendered


def verify_table(
    table: Any,
    sources: Sequence[SourceDocument],
    *,
    mode: str,
    unsupported: str,
    all_occurrences: bool,
) -> dict[str, Any]:
    if not isinstance(table, (dict, list)):
        raise ValueError("Extraction JSON must be an object or array.")
    if not sources:
        raise ValueError("At least one source is required.")

    # JSON round trip gives a safe mutable deep copy for JSON-compatible input.
    verified = json.loads(json.dumps(table))
    audit: list[dict[str, Any]] = []
    grounded = ungrounded = null_count = 0

    for path, raw_value in iter_cells(table):
        rendered = "" if raw_value is None else str(raw_value).strip()
        if rendered.casefold() in NULL_MARKERS:
            null_count += 1
            audit.append(
                {
                    "path": json_path(path),
                    "value": raw_value,
                    "status": "not_applicable",
                    "matches": [],
                }
            )
            continue
        matches: list[dict[str, Any]] = []
        for source in sources:
            match = locate(rendered, source, mode)
            if match is not None:
                matches.append(match)
                if not all_occurrences:
                    break
        if matches:
            grounded += 1
            status = "grounded"
        else:
            ungrounded += 1
            status = "ungrounded"
            if unsupported == "na":
                set_path(verified, path, "N/A")
            elif unsupported == "null":
                set_path(verified, path, None)
        audit.append(
            {
                "path": json_path(path),
                "value": raw_value,
                "rendered_value": rendered,
                "status": status,
                "matches": matches,
            }
        )

    assessed = grounded + ungrounded
    return {
        "tool": "byte-identity",
        "method": METHOD,
        "source_inventory": [
            {
                "source_id": source.source_id,
                "path": source.path,
                "sha256": source.sha256,
                "utf8_bytes": source.utf8_bytes,
            }
            for source in sources
        ],
        "matching_contract": {
            "mode": mode,
            "unsupported_action": unsupported,
            "all_source_matches": all_occurrences,
        },
        "statistics": {
            "cells_assessed": assessed,
            "grounded_cells": grounded,
            "ungrounded_cells": ungrounded,
            "null_or_not_applicable": null_count,
            "grounding_coverage": grounded / assessed if assessed else None,
        },
        "verified_table": verified,
        "audit_trail": audit,
    }


class ByteIdentityVerifier:
    """Compatibility wrapper for programmatic callers of the original class."""

    def __init__(self, case_sensitive: bool = False, ignore_whitespace: bool = True):
        self.mode = "exact" if case_sensitive and not ignore_whitespace else "normalized"

    def verify_cell(self, value: Any, source_text: str) -> dict[str, Any]:
        rendered = "" if value is None else str(value).strip()
        if rendered.casefold() in NULL_MARKERS:
            return {"status": "not_applicable", "grounded": True, "matches": []}
        source = SourceDocument("source-1", "<memory>", source_text)
        match = locate(rendered, source, self.mode)
        return {
            "status": "grounded" if match else "ungrounded",
            "grounded": match is not None,
            "matches": [match] if match else [],
        }

    def verify_table(self, table_data: Any, source_text: str, unsupported: str = "na") -> dict[str, Any]:
        return verify_table(
            table_data,
            [SourceDocument("source-1", "<memory>", source_text)],
            mode=self.mode,
            unsupported=unsupported,
            all_occurrences=False,
        )


def load_sources(paths: Sequence[str]) -> list[SourceDocument]:
    result = []
    for index, raw_path in enumerate(paths, start=1):
        path = Path(raw_path)
        result.append(
            SourceDocument(
                source_id=f"source-{index}",
                path=str(path),
                text=path.read_text(encoding="utf-8", errors="replace"),
            )
        )
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify extracted table cells against source text with auditable offsets."
    )
    parser.add_argument("--source", action="append", help="UTF-8 source text; repeat for multiple sources.")
    parser.add_argument("--extraction", help="JSON object or array containing extracted cells.")
    parser.add_argument("--output", "--output_verified", dest="output")
    parser.add_argument("--mode", choices=("exact", "normalized"), default="exact")
    parser.add_argument("--unsupported", choices=("na", "null", "keep"), default="na")
    parser.add_argument("--all-occurrences", action="store_true")
    parser.add_argument("--fail-on-ungrounded", action="store_true")
    parser.add_argument("--demo", action="store_true", help="Run a deterministic source-grounding fixture.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.demo:
            sources = [
                SourceDocument(
                    "source-1",
                    "<demo>",
                    "SciCode-ML reached 89.05% using AdamW with a learning rate of 2e-5.",
                )
            ]
            extraction = [{"model": "SciCode-ML", "accuracy": "89.05%", "batch_size": "128"}]
        else:
            if not args.source or not args.extraction:
                raise ValueError("--source and --extraction are required unless --demo is used.")
            sources = load_sources(args.source)
            extraction = json.loads(Path(args.extraction).read_text(encoding="utf-8"))
        report = verify_table(
            extraction,
            sources,
            mode=args.mode,
            unsupported=args.unsupported,
            all_occurrences=args.all_occurrences,
        )
        payload = json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        if args.output:
            path = Path(args.output)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(payload, encoding="utf-8")
        print(payload, end="")
        if args.fail_on_ungrounded and report["statistics"]["ungrounded_cells"]:
            return 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
