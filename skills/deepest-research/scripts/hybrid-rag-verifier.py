#!/usr/bin/env python3
"""Hybrid-RAG verifier for nested extractions and multi-source provenance.

Grounded in ArxivDIGESTables and attributed-generation workflows. The verifier
flattens nested JSON values, finds exact or whitespace/case-normalized matches,
maps normalized matches back to raw character and UTF-8 byte offsets, and can
emit a pruned extraction where unmatched values become ``N/A`` or ``null``.

The reported metric is grounding coverage: the fraction of assessed rendered
values with source support under the declared matching contract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence


METHOD = {
    "name": "Hybrid-RAG source verifier",
    "sources": [
        "ArxivDIGESTables: Synthesizing Scientific Literature into Tables using Language Models",
        "Attributed Text Generation via Post-Hoc Research and Revision",
    ],
}
NULL_MARKERS = {"", "n/a", "na", "none", "null", "nan", "not applicable"}


@dataclass(frozen=True)
class Source:
    source_id: str
    path: str
    text: str

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()

    @property
    def utf8_bytes(self) -> int:
        return len(self.text.encode("utf-8"))


def flatten(value: Any, path: tuple[Any, ...] = ()) -> Iterator[tuple[tuple[Any, ...], Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield from flatten(child, (*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from flatten(child, (*path, index))
    else:
        yield path, value


def path_text(path: Sequence[Any]) -> str:
    result = "$"
    for part in path:
        if isinstance(part, int):
            result += f"[{part}]"
        elif re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", str(part)):
            result += f".{part}"
        else:
            result += f"[{json.dumps(str(part))}]"
    return result


def set_value(root: Any, path: Sequence[Any], value: Any) -> None:
    cursor = root
    for part in path[:-1]:
        cursor = cursor[part]
    cursor[path[-1]] = value


def normalized_map(text: str) -> tuple[str, list[int]]:
    output: list[str] = []
    mapping: list[int] = []
    pending_space = False
    for raw_index, char in enumerate(text):
        if char.isspace():
            if output:
                pending_space = True
            continue
        if pending_space:
            output.append(" ")
            mapping.append(raw_index)
            pending_space = False
        for folded in char.casefold():
            output.append(folded)
            mapping.append(raw_index)
    return "".join(output), mapping


def byte_offset(text: str, character_offset: int) -> int:
    return len(text[:character_offset].encode("utf-8"))


def find_all(haystack: str, needle: str) -> Iterable[int]:
    start = 0
    while True:
        index = haystack.find(needle, start)
        if index < 0:
            return
        yield index
        start = index + max(1, len(needle))


def matches_in_source(
    rendered: str,
    source: Source,
    *,
    mode: str,
    max_matches: int,
) -> list[dict[str, Any]]:
    if mode == "exact":
        search_text = source.text
        needle = rendered
        mapping = None
    else:
        search_text, mapping = normalized_map(source.text)
        needle, _ = normalized_map(rendered)
    if not needle:
        return []

    results: list[dict[str, Any]] = []
    for index in find_all(search_text, needle):
        if mapping is None:
            raw_start, raw_end = index, index + len(needle)
        else:
            raw_start = mapping[index]
            raw_end = mapping[index + len(needle) - 1] + 1
        results.append(
            {
                "source_id": source.source_id,
                "source_path": source.path,
                "match_mode": mode,
                "raw_character_offsets": [raw_start, raw_end],
                "utf8_byte_offsets": [
                    byte_offset(source.text, raw_start),
                    byte_offset(source.text, raw_end),
                ],
                "matched_text": source.text[raw_start:raw_end],
                "excerpt": source.text[
                    max(0, raw_start - 80): min(len(source.text), raw_end + 80)
                ].replace("\n", " "),
            }
        )
        if max_matches > 0 and len(results) >= max_matches:
            break
    return results


def verify_grounding(
    sources: Sequence[Source],
    target_values: Any,
    *,
    mode: str = "exact",
    max_matches: int = 1,
    unsupported: str = "keep",
) -> dict[str, Any]:
    if not isinstance(target_values, (dict, list)):
        raise ValueError("Target JSON must be an object or array.")
    if not sources:
        raise ValueError("At least one source is required.")
    verified = deepcopy(target_values)
    rows: list[dict[str, Any]] = []
    grounded = ungrounded = excluded = 0

    for path, value in flatten(target_values):
        rendered = "" if value is None else str(value).strip()
        if rendered.casefold() in NULL_MARKERS:
            excluded += 1
            rows.append(
                {
                    "path": path_text(path),
                    "value": value,
                    "status": "not_applicable",
                    "matches": [],
                }
            )
            continue
        matches: list[dict[str, Any]] = []
        for source in sources:
            matches.extend(
                matches_in_source(
                    rendered,
                    source,
                    mode=mode,
                    max_matches=(max_matches - len(matches) if max_matches > 0 else 0),
                )
            )
            if max_matches > 0 and len(matches) >= max_matches:
                break
        status = "grounded" if matches else "not_grounded"
        if matches:
            grounded += 1
        else:
            ungrounded += 1
            if unsupported == "na":
                set_value(verified, path, "N/A")
            elif unsupported == "null":
                set_value(verified, path, None)
        rows.append(
            {
                "path": path_text(path),
                "value": value,
                "rendered_value": rendered,
                "status": status,
                "matches": matches,
            }
        )

    denominator = grounded + ungrounded
    return {
        "tool": "hybrid-rag-verifier",
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
            "max_matches_per_value": max_matches,
            "unsupported_action": unsupported,
        },
        "statistics": {
            "assessed_values": denominator,
            "grounded_values": grounded,
            "ungrounded_values": ungrounded,
            "null_or_not_applicable": excluded,
            "grounding_coverage": grounded / denominator if denominator else None,
        },
        "verified_extraction": verified,
        "verifications": rows,
    }


def load_sources(paths: Sequence[str]) -> list[Source]:
    sources = []
    for index, raw in enumerate(paths, start=1):
        path = Path(raw)
        sources.append(
            Source(
                source_id=f"source-{index}",
                path=str(path),
                text=path.read_text(encoding="utf-8", errors="replace"),
            )
        )
    return sources


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify nested JSON values against one or more source texts."
    )
    parser.add_argument("--source", action="append", required=True, help="Source text; repeatable.")
    parser.add_argument("--target", required=True, help="Extraction JSON.")
    parser.add_argument("--output", default="rag_grounding_report.json")
    parser.add_argument("--mode", choices=("exact", "normalized"), default="exact")
    parser.add_argument("--max-matches", type=int, default=1, help="0 retains all matches.")
    parser.add_argument("--unsupported", choices=("keep", "na", "null"), default="keep")
    parser.add_argument("--fail-on-ungrounded", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.max_matches < 0:
            raise ValueError("--max-matches cannot be negative.")
        sources = load_sources(args.source)
        target = json.loads(Path(args.target).read_text(encoding="utf-8"))
        report = verify_grounding(
            sources,
            target,
            mode=args.mode,
            max_matches=args.max_matches,
            unsupported=args.unsupported,
        )
        payload = json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
        print(payload, end="")
        if args.fail_on_ungrounded and report["statistics"]["ungrounded_values"]:
            return 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
