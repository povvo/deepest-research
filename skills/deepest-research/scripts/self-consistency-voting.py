#!/usr/bin/env python3
"""Aggregate independently sampled reasoning paths by self-consistency.

The default ``majority`` mode follows Wang et al.: extract a final answer from
each sampled path and select the empirical mode, marginalizing over the diverse
reasoning paths. ``weighted`` accepts externally supplied non-negative sample
weights. ``resonance`` retains the original demo's Jaccard-centrality extension
for free-form candidates where no stable answer extractor is available.

Agreement is reported with the full vote distribution and dissent retained.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable, Sequence


METHOD = {
    "name": "self-consistency decoding",
    "source": "Self-Consistency Improves Chain of Thought Reasoning in Language Models",
}


def get_path(value: Any, dotted: str) -> Any:
    cursor = value
    for part in dotted.split("."):
        if isinstance(cursor, dict) and part in cursor:
            cursor = cursor[part]
        else:
            raise KeyError(dotted)
    return cursor


def normalize_answer(value: Any, mode: str) -> str:
    if mode == "json":
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    text = str(value)
    if mode == "exact":
        return text
    if mode == "casefold":
        return text.strip().casefold()
    if mode == "numeric":
        match = re.search(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?", text.replace(",", ""))
        if not match:
            raise ValueError(f"No numeric answer found in {text!r}.")
        return format(float(match.group(0)), ".15g")
    # compact
    return re.sub(r"\s+", " ", text).strip().casefold()


def token_set(value: Any) -> set[str]:
    rendered = json.dumps(value, sort_keys=True, ensure_ascii=False)
    return set(re.findall(r"\b[\w'-]+\b", rendered.casefold()))


def jaccard(first: Any, second: Any) -> float:
    left, right = token_set(first), token_set(second)
    union = left | right
    return len(left & right) / len(union) if union else 1.0


def extract_candidate_answer(candidate: Any, answer_field: str | None) -> Any:
    if answer_field:
        return get_path(candidate, answer_field)
    if isinstance(candidate, dict):
        for common in ("final_answer", "answer", "result", "selected_value"):
            if common in candidate:
                return candidate[common]
        raise ValueError(
            "Object candidates need --answer-field or one of final_answer, answer, result, selected_value."
        )
    return candidate


def majority_vote(
    candidates: Sequence[Any],
    *,
    answer_field: str | None,
    normalization: str,
    weight_field: str | None,
) -> dict[str, Any]:
    if not candidates:
        raise ValueError("Candidate list must not be empty.")

    totals: defaultdict[str, float] = defaultdict(float)
    counts: Counter[str] = Counter()
    examples: dict[str, Any] = {}
    members: defaultdict[str, list[int]] = defaultdict(list)
    total_weight = 0.0

    for index, candidate in enumerate(candidates):
        answer = extract_candidate_answer(candidate, answer_field)
        normalized = normalize_answer(answer, normalization)
        if weight_field:
            if not isinstance(candidate, dict):
                raise ValueError("--weight-field requires object candidates.")
            weight = float(get_path(candidate, weight_field))
            if not math.isfinite(weight) or weight < 0:
                raise ValueError(f"Candidate {index} has an invalid weight.")
        else:
            weight = 1.0
        totals[normalized] += weight
        counts[normalized] += 1
        total_weight += weight
        examples.setdefault(normalized, answer)
        members[normalized].append(index)

    if total_weight <= 0:
        raise ValueError("Total vote weight must be positive.")
    winner = sorted(
        totals,
        key=lambda key: (-totals[key], -counts[key], key),
    )[0]
    distribution = [
        {
            "normalized_answer": key,
            "representative_answer": examples[key],
            "votes": counts[key],
            "weight": totals[key],
            "vote_share": totals[key] / total_weight,
            "candidate_indices": members[key],
        }
        for key in sorted(totals, key=lambda key: (-totals[key], key))
    ]
    top_share = totals[winner] / total_weight
    runner_share = distribution[1]["vote_share"] if len(distribution) > 1 else 0.0
    return {
        "method": METHOD,
        "aggregation": "weighted_empirical_mode" if weight_field else "empirical_mode",
        "candidate_count": len(candidates),
        "selected_answer": examples[winner],
        "normalized_selected_answer": winner,
        "vote_share": top_share,
        "margin_over_runner_up": top_share - runner_share,
        "unanimous": counts[winner] == len(candidates),
        "distribution": distribution,
        "dissenting_candidate_indices": [
            index for key, indices in members.items() if key != winner for index in indices
        ],
    }


def resonance_vote(candidates: Sequence[Any]) -> dict[str, Any]:
    if not candidates:
        raise ValueError("Candidate list must not be empty.")
    matrix = [[0.0 for _ in candidates] for _ in candidates]
    scores = [0.0 for _ in candidates]
    for i, first in enumerate(candidates):
        matrix[i][i] = 1.0
        for j in range(i + 1, len(candidates)):
            similarity = jaccard(first, candidates[j])
            matrix[i][j] = matrix[j][i] = similarity
            scores[i] += similarity
            scores[j] += similarity
    denominator = max(1, len(candidates) - 1)
    centrality = [score / denominator for score in scores]
    winner = sorted(range(len(candidates)), key=lambda index: (-centrality[index], index))[0]
    return {
        "method": METHOD,
        "aggregation": "jaccard_resonance_extension",
        "candidate_count": len(candidates),
        "winning_index": winner,
        "resonance_strength": centrality[winner],
        "consensus_candidate": candidates[winner],
        "centrality": centrality,
        "similarity_matrix": matrix,
    }


def vote_on_paths(
    candidates: list[Any],
    *,
    mode: str = "majority",
    answer_field: str | None = None,
    normalization: str = "compact",
    weight_field: str | None = None,
) -> dict[str, Any]:
    if mode == "resonance":
        return resonance_vote(candidates)
    return majority_vote(
        candidates,
        answer_field=answer_field,
        normalization=normalization,
        weight_field=(weight_field if mode == "weighted" else None),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Aggregate independent reasoning samples by answer self-consistency."
    )
    parser.add_argument("--candidates", required=True, help="JSON array of sampled paths.")
    parser.add_argument("--output", default="consensus_choice.json")
    parser.add_argument("--mode", choices=("majority", "weighted", "resonance"), default="majority")
    parser.add_argument("--answer-field", help="Dotted object path containing the final answer.")
    parser.add_argument(
        "--normalization",
        choices=("exact", "casefold", "compact", "numeric", "json"),
        default="compact",
    )
    parser.add_argument("--weight-field", help="Dotted field containing an external non-negative weight.")
    parser.add_argument("--minimum-share", type=float, help="Exit 1 if the winning vote share is below this value.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        data = json.loads(Path(args.candidates).read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("Candidates JSON must contain an array.")
        if args.mode == "weighted" and not args.weight_field:
            raise ValueError("--weight-field is required in weighted mode.")
        if args.minimum_share is not None and not 0 <= args.minimum_share <= 1:
            raise ValueError("--minimum-share must be between 0 and 1.")
        report = vote_on_paths(
            data,
            mode=args.mode,
            answer_field=args.answer_field,
            normalization=args.normalization,
            weight_field=args.weight_field,
        )
        payload = json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
        print(payload, end="")
        if args.minimum_share is not None and report.get("vote_share", 1.0) < args.minimum_share:
            return 1
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
