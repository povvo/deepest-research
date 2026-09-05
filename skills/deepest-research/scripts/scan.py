#!/usr/bin/env python3
"""Source-grounded local corpus curation and deduplication.

Scientific grounding:
  * The Pile data-curation pipeline.
  * Lee et al., "Deduplicating Training Data Makes Language Models Better."
  * C4 corpus documentation.

The script loads local JSON/JSONL/TXT/Markdown records, records source hashes,
applies explicit content filters, and clusters exact or near duplicates. It
never equates engagement metadata with credibility: ``--min-karma`` is an
optional corpus-inclusion rule and is named in the output configuration.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence

METHOD = {
    "name": "local corpus curation and deduplication",
    "sources": [
        "The Pile: An 800GB Dataset of Diverse Text for Language Modeling",
        "Deduplicating Training Data Makes Language Models Better",
        "Documenting the English Colossal Clean Crawled Corpus",
    ],
    "runtime_class": "corpus curation implementation",
}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_text(text: str, mode: str) -> str:
    if mode == "none":
        return text
    normalized = unicodedata.normalize("NFKC", text)
    if mode == "nfkc":
        return normalized
    if mode == "casefold-space":
        return " ".join(normalized.casefold().split())
    raise ValueError(f"Unknown normalization mode: {mode}")


def words(text: str) -> list[str]:
    return re.findall(r"\b[\w'-]+\b", text.casefold(), flags=re.UNICODE)


def shingles(text: str, n: int) -> set[tuple[str, ...]]:
    tokens = words(text)
    if not tokens:
        return set()
    if len(tokens) < n:
        return {tuple(tokens)}
    return {tuple(tokens[index : index + n]) for index in range(len(tokens) - n + 1)}


def jaccard(first: set[Any], second: set[Any]) -> float:
    union = first | second
    return len(first & second) / len(union) if union else 1.0


def repeated_line_fraction(text: str) -> float:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return 0.0 if not lines else 1.0 - len(set(lines)) / len(lines)


def repeated_token_fraction(text: str) -> float:
    tokens = words(text)
    if not tokens:
        return 0.0
    counts = Counter(tokens)
    return max(counts.values()) / len(tokens)


def canonicalize(
    data: Any,
    *,
    source: str,
    text_field: str,
    id_field: str,
) -> list[dict[str, Any]]:
    if isinstance(data, dict) and "documents" in data:
        data = data["documents"]
    elif isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise ValueError(f"{source}: expected a JSON list/object.")
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(data):
        if isinstance(item, str):
            record: dict[str, Any] = {
                "id": f"{source}:{index}",
                "text": item,
                "source": source,
            }
        elif isinstance(item, dict):
            record = dict(item)
            record["id"] = str(item.get(id_field, item.get("id", f"{source}:{index}")))
            value = item.get(text_field, item.get("text", item.get("content", "")))
            record["text"] = "" if value is None else str(value)
            record["source"] = str(item.get("source", source))
        else:
            raise ValueError(f"{source}: unsupported record at index {index}.")
        rows.append(record)
    return rows


def load_paths(
    path: Path,
    *,
    text_field: str,
    id_field: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    files = sorted(candidate for candidate in path.rglob("*") if candidate.is_file()) if path.is_dir() else [path]
    records: list[dict[str, Any]] = []
    inventory: list[dict[str, Any]] = []
    for file in files:
        suffix = file.suffix.casefold()
        if suffix not in {".json", ".jsonl", ".txt", ".md"}:
            continue
        inventory.append(
            {
                "path": str(file),
                "bytes": file.stat().st_size,
                "sha256": file_sha256(file),
                "format": suffix.lstrip("."),
            }
        )
        if suffix == ".json":
            payload = json.loads(file.read_text(encoding="utf-8"))
            records.extend(
                canonicalize(
                    payload,
                    source=str(file),
                    text_field=text_field,
                    id_field=id_field,
                )
            )
        elif suffix == ".jsonl":
            payload = [
                json.loads(line)
                for line in file.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            records.extend(
                canonicalize(
                    payload,
                    source=str(file),
                    text_field=text_field,
                    id_field=id_field,
                )
            )
        else:
            records.append(
                {
                    "id": str(file),
                    "text": file.read_text(encoding="utf-8", errors="replace"),
                    "source": str(file),
                }
            )
    if not inventory:
        raise ValueError("No supported JSON, JSONL, TXT, or Markdown files found.")
    return records, inventory


def filter_record(
    record: dict[str, Any],
    *,
    min_tokens: int,
    max_repeated_line_fraction: float,
    max_repeated_token_fraction: float,
    min_karma: float | None,
) -> tuple[bool, list[str], dict[str, Any]]:
    text = str(record.get("text", ""))
    token_count = len(words(text))
    line_repeat = repeated_line_fraction(text)
    token_repeat = repeated_token_fraction(text)
    reasons: list[str] = []
    if token_count < min_tokens:
        reasons.append("below_min_tokens")
    if line_repeat > max_repeated_line_fraction:
        reasons.append("excessive_repeated_lines")
    if token_repeat > max_repeated_token_fraction:
        reasons.append("excessive_single_token_repetition")
    karma = None
    if min_karma is not None:
        try:
            karma = float(record.get("karma", 0) or 0)
        except (TypeError, ValueError):
            reasons.append("invalid_karma")
        else:
            if karma < min_karma:
                reasons.append("below_min_karma")
    diagnostics = {
        "token_count": token_count,
        "repeated_line_fraction": line_repeat,
        "maximum_token_fraction": token_repeat,
        "karma": karma,
    }
    return not reasons, reasons, diagnostics


def representative_key(record: dict[str, Any], policy: str, input_index: int) -> tuple[Any, ...]:
    text = str(record.get("text", ""))
    if policy == "first":
        return (-input_index,)
    if policy == "longest":
        return (len(words(text)), -input_index)
    if policy == "highest-karma":
        try:
            karma = float(record.get("karma", 0) or 0)
        except (TypeError, ValueError):
            karma = float("-inf")
        return (karma, len(words(text)), -input_index)
    raise ValueError(f"Unknown representative policy: {policy}")


def signatures(
    records: list[dict[str, Any]],
    *,
    normalization: str,
    method: str,
    ngram_size: int,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for record in records:
        raw = str(record.get("text", ""))
        normalized = normalize_text(raw, normalization)
        if method == "exact":
            signature: Any = text_sha256(normalized)
        elif method == "token-set":
            signature = set(words(normalized))
        elif method == "word-ngram":
            signature = shingles(normalized, ngram_size)
        else:
            raise ValueError(f"Unknown deduplication method: {method}")
        output.append(
            {
                "raw_sha256": text_sha256(raw),
                "normalized_sha256": text_sha256(normalized),
                "signature": signature,
                "normalized_characters": len(normalized),
            }
        )
    return output


def similarity(first: Any, second: Any, method: str) -> float:
    if method == "exact":
        return 1.0 if first == second else 0.0
    return jaccard(first, second)


def connected_duplicate_components(
    sigs: list[dict[str, Any]],
    *,
    method: str,
    threshold: float,
) -> list[list[int]]:
    count = len(sigs)
    parent = list(range(count))

    def find(value: int) -> int:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(first: int, second: int) -> None:
        left, right = find(first), find(second)
        if left != right:
            parent[right] = left

    exact_buckets: defaultdict[str, list[int]] = defaultdict(list)
    for index, sig in enumerate(sigs):
        exact_buckets[str(sig["normalized_sha256"])].append(index)
    for bucket in exact_buckets.values():
        for index in bucket[1:]:
            union(bucket[0], index)

    if method != "exact":
        for first in range(count):
            for second in range(first + 1, count):
                if find(first) == find(second):
                    continue
                score = similarity(sigs[first]["signature"], sigs[second]["signature"], method)
                if score >= threshold:
                    union(first, second)

    groups: defaultdict[int, list[int]] = defaultdict(list)
    for index in range(count):
        groups[find(index)].append(index)
    return sorted(groups.values(), key=lambda group: min(group))


def curate(
    records: list[dict[str, Any]],
    *,
    min_tokens: int,
    max_repeated_line_fraction: float,
    max_repeated_token_fraction: float,
    min_karma: float | None,
    normalization: str,
    method: str,
    ngram_size: int,
    threshold: float,
    representative: str,
) -> dict[str, Any]:
    accepted: list[dict[str, Any]] = []
    accepted_original_indices: list[int] = []
    rejected: list[dict[str, Any]] = []
    diagnostics_by_id: dict[str, Any] = {}
    seen_ids: set[str] = set()

    for input_index, record in enumerate(records):
        record_id = str(record.get("id", input_index))
        if record_id in seen_ids:
            rejected.append(
                {
                    "id": record_id,
                    "input_index": input_index,
                    "reasons": ["duplicate_record_id"],
                }
            )
            continue
        seen_ids.add(record_id)
        ok, reasons, diagnostics = filter_record(
            record,
            min_tokens=min_tokens,
            max_repeated_line_fraction=max_repeated_line_fraction,
            max_repeated_token_fraction=max_repeated_token_fraction,
            min_karma=min_karma,
        )
        diagnostics_by_id[record_id] = diagnostics
        if ok:
            normalized_record = dict(record)
            normalized_record["id"] = record_id
            accepted.append(normalized_record)
            accepted_original_indices.append(input_index)
        else:
            rejected.append(
                {
                    "id": record_id,
                    "input_index": input_index,
                    "reasons": reasons,
                    "diagnostics": diagnostics,
                }
            )

    sigs = signatures(
        accepted,
        normalization=normalization,
        method=method,
        ngram_size=ngram_size,
    )
    components = connected_duplicate_components(sigs, method=method, threshold=threshold)
    kept_indices: list[int] = []
    duplicate_clusters: list[dict[str, Any]] = []
    for cluster_number, component in enumerate(components, start=1):
        keep = max(
            component,
            key=lambda index: representative_key(
                accepted[index], representative, accepted_original_indices[index]
            ),
        )
        kept_indices.append(keep)
        if len(component) > 1:
            members: list[dict[str, Any]] = []
            for index in component:
                score = similarity(
                    sigs[keep]["signature"],
                    sigs[index]["signature"],
                    method,
                )
                members.append(
                    {
                        "id": accepted[index]["id"],
                        "input_index": accepted_original_indices[index],
                        "similarity_to_representative": score,
                        "raw_sha256": sigs[index]["raw_sha256"],
                        "normalized_sha256": sigs[index]["normalized_sha256"],
                        "retained": index == keep,
                    }
                )
            duplicate_clusters.append(
                {
                    "cluster_id": cluster_number,
                    "representative_id": accepted[keep]["id"],
                    "members": members,
                }
            )

    kept_indices.sort(key=lambda index: accepted_original_indices[index])
    retained = []
    for index in kept_indices:
        row = dict(accepted[index])
        row["_curation"] = {
            **diagnostics_by_id[row["id"]],
            "raw_sha256": sigs[index]["raw_sha256"],
            "normalized_sha256": sigs[index]["normalized_sha256"],
        }
        retained.append(row)

    return {
        "input_count": len(records),
        "accepted_before_deduplication": len(accepted),
        "retained_count": len(retained),
        "rejected_count": len(rejected),
        "duplicate_cluster_count": len(duplicate_clusters),
        "rejected": rejected,
        "duplicate_clusters": duplicate_clusters,
        "documents": retained,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Curate and exact/near-deduplicate a local text collection."
    )
    parser.add_argument("--input", "--input-dir", dest="input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--text-field", default="text")
    parser.add_argument("--id-field", default="id")
    parser.add_argument("--min-tokens", type=int, default=1)
    parser.add_argument("--max-repeated-line-fraction", type=float, default=0.75)
    parser.add_argument("--max-repeated-token-fraction", type=float, default=0.50)
    parser.add_argument(
        "--min-karma",
        type=float,
        default=None,
        help="Optional metadata inclusion rule; not a credibility score.",
    )
    parser.add_argument(
        "--normalization",
        choices=["none", "nfkc", "casefold-space"],
        default="casefold-space",
    )
    parser.add_argument(
        "--dedup-method",
        choices=["exact", "token-set", "word-ngram"],
        default="word-ngram",
    )
    parser.add_argument("--ngram-size", type=int, default=5)
    parser.add_argument("--dedup-threshold", type=float, default=0.80)
    parser.add_argument(
        "--representative",
        choices=["first", "longest", "highest-karma"],
        default="longest",
    )
    parser.add_argument("--fail-empty", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.min_tokens < 0:
            raise ValueError("--min-tokens must be non-negative.")
        for name, value in (
            ("--max-repeated-line-fraction", args.max_repeated_line_fraction),
            ("--max-repeated-token-fraction", args.max_repeated_token_fraction),
            ("--dedup-threshold", args.dedup_threshold),
        ):
            if not 0 <= value <= 1:
                raise ValueError(f"{name} must be between 0 and 1.")
        if args.ngram_size < 1:
            raise ValueError("--ngram-size must be >= 1.")

        records, inventory = load_paths(
            args.input,
            text_field=args.text_field,
            id_field=args.id_field,
        )
        result = curate(
            records,
            min_tokens=args.min_tokens,
            max_repeated_line_fraction=args.max_repeated_line_fraction,
            max_repeated_token_fraction=args.max_repeated_token_fraction,
            min_karma=args.min_karma,
            normalization=args.normalization,
            method=args.dedup_method,
            ngram_size=args.ngram_size,
            threshold=args.dedup_threshold,
            representative=args.representative,
        )
        report = {
            "tool": "scan",
            "method": METHOD,
            "source_inventory": inventory,
            "configuration": {
                "text_field": args.text_field,
                "id_field": args.id_field,
                "min_tokens": args.min_tokens,
                "max_repeated_line_fraction": args.max_repeated_line_fraction,
                "max_repeated_token_fraction": args.max_repeated_token_fraction,
                "min_karma": args.min_karma,
                "normalization": args.normalization,
                "deduplication_method": args.dedup_method,
                "ngram_size": args.ngram_size,
                "deduplication_threshold": args.dedup_threshold,
                "representative_policy": args.representative,
            },
            **result,
            "interpretation": (
                "Curation and deduplication decisions are recorded corpus operations; "
                "they are not source-credibility or evidentiary-quality judgements."
            ),
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(
            json.dumps(
                {
                    "status": "PASS",
                    "output": str(args.output),
                    "input_count": report["input_count"],
                    "retained_count": report["retained_count"],
                    "duplicate_clusters": report["duplicate_cluster_count"],
                },
                sort_keys=True,
            )
        )
        if args.fail_empty and report["retained_count"] == 0:
            return 1
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"scan: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
