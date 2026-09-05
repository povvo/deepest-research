#!/usr/bin/env python3
"""Hierarchical concept induction and deterministic taxonomy construction.

Scientific grounding:
  * Lam et al., "Concept Induction: Analyzing Unstructured Text with High-Level
    Concepts Using LLooM" (arXiv:2404.12259).
  * SurveyForge's outline/hierarchy rationale.

Three explicit paths are provided:
  * ``run-adapter`` invokes a JSON-in/JSON-out model adapter that induces
    high-level concepts with inclusion criteria and grounded matches.
  * ``integrate`` validates and organizes already induced concepts.
  * ``cluster`` produces a deterministic TF-IDF hierarchy for offline
    baseline/ablation use; it is never labelled as LLooM output.

Legacy flat ``--papers ...`` arguments are routed to ``cluster``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shlex
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence

METHOD = {
    "source": [
        "Concept Induction: Analyzing Unstructured Text with High-Level Concepts Using LLooM",
        "SurveyForge: On the Outline Heuristics, Memory-Driven Generation, and Multi-Dimensional Evaluation for Automated Survey Writing",
    ],
}

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has",
    "have", "in", "is", "it", "of", "on", "or", "that", "the", "their", "this",
    "to", "was", "were", "will", "with", "we", "our", "using", "use", "study",
    "research", "paper", "results", "method",
}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def tokenize(text: str) -> list[str]:
    return [
        word
        for word in re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", text.casefold())
        if word not in STOPWORDS
    ]


def canonical_docs(data: Any) -> list[dict[str, str]]:
    if isinstance(data, dict):
        data = data.get("documents", data.get("papers", data))
    if not isinstance(data, list):
        raise ValueError("Document input must be a JSON list or object with documents/papers.")
    docs: list[dict[str, str]] = []
    seen: set[str] = set()
    for index, item in enumerate(data):
        if isinstance(item, str):
            document_id = str(index)
            title = item[:120]
            text = item
        elif isinstance(item, dict):
            document_id = str(item.get("id", index))
            title = str(item.get("title") or item.get("name") or document_id)
            fields = ("title", "abstract", "summary", "text", "content")
            text = "\n".join(str(item.get(field, "")) for field in fields if item.get(field))
        else:
            raise ValueError(f"Unsupported document at index {index}.")
        if document_id in seen:
            raise ValueError(f"Duplicate document id: {document_id}")
        if not text.strip():
            raise ValueError(f"Document {document_id!r} has no text.")
        seen.add(document_id)
        docs.append(
            {
                "id": document_id,
                "title": title,
                "text": text,
                "sha256": sha256_text(text),
            }
        )
    if not docs:
        raise ValueError("At least one document is required.")
    return docs


def load_documents(path: Path) -> list[dict[str, str]]:
    return canonical_docs(json.loads(path.read_text(encoding="utf-8")))


# ----------------------------- baseline clustering ----------------------------

def tfidf_vectors(
    docs: list[dict[str, str]],
) -> tuple[list[dict[str, float]], list[list[str]]]:
    token_rows = [tokenize(doc["text"]) for doc in docs]
    document_frequency: Counter[str] = Counter()
    for row in token_rows:
        document_frequency.update(set(row))
    count = len(docs)
    vectors: list[dict[str, float]] = []
    for row in token_rows:
        term_frequency = Counter(row)
        vector = {
            term: frequency * (math.log((1 + count) / (1 + document_frequency[term])) + 1.0)
            for term, frequency in term_frequency.items()
        }
        norm = math.sqrt(sum(value * value for value in vector.values())) or 1.0
        vectors.append({term: value / norm for term, value in vector.items()})
    return vectors, token_rows


def cosine(first: dict[str, float], second: dict[str, float]) -> float:
    if len(first) > len(second):
        first, second = second, first
    return sum(value * second.get(term, 0.0) for term, value in first.items())


def choose_seeds(indices: list[int], vectors: list[dict[str, float]], k: int) -> list[int]:
    seeds = [min(indices)]
    while len(seeds) < min(k, len(indices)):
        candidate = max(
            (index for index in indices if index not in seeds),
            key=lambda index: (
                min(1.0 - cosine(vectors[index], vectors[seed]) for seed in seeds),
                -index,
            ),
        )
        seeds.append(candidate)
    return seeds


def partition(indices: list[int], vectors: list[dict[str, float]], k: int) -> list[list[int]]:
    seeds = choose_seeds(indices, vectors, k)
    groups = [[] for _ in seeds]
    for index in indices:
        best = max(
            range(len(seeds)),
            key=lambda group: (cosine(vectors[index], vectors[seeds[group]]), -group),
        )
        groups[best].append(index)
    return [group for group in groups if group]


def top_terms(indices: list[int], token_rows: list[list[str]], limit: int = 5) -> list[str]:
    counts = Counter(term for index in indices for term in token_rows[index])
    return [term for term, _ in counts.most_common(limit)]


def build_cluster_tree(
    docs: list[dict[str, str]],
    vectors: list[dict[str, float]],
    token_rows: list[list[str]],
    indices: list[int],
    depth: int,
    max_depth: int,
    branching_factor: int,
) -> dict[str, Any]:
    node: dict[str, Any] = {
        "label_terms": top_terms(indices, token_rows),
        "document_count": len(indices),
        "document_ids": [docs[index]["id"] for index in indices],
        "children": [],
    }
    if depth >= max_depth or len(indices) <= 1:
        node["documents"] = [
            {"id": docs[index]["id"], "title": docs[index]["title"]}
            for index in indices
        ]
        return node
    groups = partition(indices, vectors, min(branching_factor, len(indices)))
    if len(groups) <= 1:
        node["documents"] = [
            {"id": docs[index]["id"], "title": docs[index]["title"]}
            for index in indices
        ]
        return node
    node["children"] = [
        build_cluster_tree(
            docs, vectors, token_rows, group, depth + 1, max_depth, branching_factor
        )
        for group in groups
    ]
    return node


def render_cluster_markdown(node: dict[str, Any], level: int = 1) -> str:
    label = ", ".join(node.get("label_terms") or ["unlabelled"])
    lines = [f"{'#' * min(level, 6)} {label} ({node['document_count']})"]
    for document in node.get("documents", []):
        lines.append(f"- `{document['id']}` — {document['title']}")
    for child in node.get("children", []):
        lines.extend(["", render_cluster_markdown(child, level + 1)])
    return "\n".join(lines)


# ------------------------------- concept path --------------------------------

def canonical_concepts(data: Any, documents: list[dict[str, str]]) -> list[dict[str, Any]]:
    if isinstance(data, dict):
        data = data.get("concepts", data)
    if not isinstance(data, list):
        raise ValueError("Concept output must be a JSON list or object with a concepts list.")
    document_map = {doc["id"]: doc for doc in documents}
    concepts: list[dict[str, Any]] = []
    seen: set[str] = set()

    for index, raw in enumerate(data):
        if not isinstance(raw, dict):
            raise ValueError(f"Concept {index} must be an object.")
        concept_id = str(raw.get("id") or f"concept-{index + 1}")
        if concept_id in seen:
            raise ValueError(f"Duplicate concept id: {concept_id}")
        seen.add(concept_id)
        name = str(raw.get("name") or raw.get("label") or "").strip()
        criteria = str(
            raw.get("inclusion_criteria")
            or raw.get("criteria")
            or raw.get("definition")
            or ""
        ).strip()
        if not name or not criteria:
            raise ValueError(f"Concept {concept_id} requires name and inclusion criteria.")
        parent = raw.get("parent_id")
        parent_id = None if parent in (None, "") else str(parent)
        exclusions = raw.get("exclusion_criteria", [])
        if isinstance(exclusions, str):
            exclusions = [exclusions]
        if not isinstance(exclusions, list):
            raise ValueError(f"Concept {concept_id} exclusion_criteria must be a list/string.")

        raw_matches = raw.get("matches", [])
        if not raw_matches and isinstance(raw.get("document_ids"), list):
            raw_matches = [{"document_id": value} for value in raw["document_ids"]]
        if not isinstance(raw_matches, list):
            raise ValueError(f"Concept {concept_id} matches must be a list.")

        matches: list[dict[str, Any]] = []
        matched_ids: set[str] = set()
        for match_index, match in enumerate(raw_matches):
            if isinstance(match, str):
                match = {"document_id": match}
            if not isinstance(match, dict):
                raise ValueError(f"Concept {concept_id} match {match_index} must be an object.")
            document_id = str(match.get("document_id", match.get("id", "")))
            if document_id not in document_map:
                raise ValueError(
                    f"Concept {concept_id} references unknown document {document_id!r}."
                )
            if document_id in matched_ids:
                raise ValueError(
                    f"Concept {concept_id} repeats document {document_id!r}."
                )
            score = match.get("score")
            if score is not None:
                score = float(score)
                if not math.isfinite(score):
                    raise ValueError(f"Concept {concept_id} has non-finite score.")
            evidence = match.get("evidence", match.get("quote"))
            evidence_status = "not_supplied"
            if evidence not in (None, ""):
                evidence = str(evidence)
                evidence_status = (
                    "exact_source_match"
                    if evidence in document_map[document_id]["text"]
                    else "not_found_in_source"
                )
            matched_ids.add(document_id)
            matches.append(
                {
                    "document_id": document_id,
                    "score": score,
                    "evidence": evidence,
                    "evidence_status": evidence_status,
                }
            )
        concepts.append(
            {
                "id": concept_id,
                "name": name,
                "inclusion_criteria": criteria,
                "exclusion_criteria": [str(value) for value in exclusions],
                "parent_id": parent_id,
                "matches": matches,
                "source_metadata": raw.get("source_metadata"),
            }
        )

    ids = {concept["id"] for concept in concepts}
    for concept in concepts:
        if concept["parent_id"] is not None and concept["parent_id"] not in ids:
            raise ValueError(
                f"Concept {concept['id']} references unknown parent {concept['parent_id']}."
            )
    detect_parent_cycles(concepts)
    return concepts


def detect_parent_cycles(concepts: list[dict[str, Any]]) -> None:
    parent = {concept["id"]: concept["parent_id"] for concept in concepts}
    for concept_id in parent:
        path: set[str] = set()
        current: str | None = concept_id
        while current is not None:
            if current in path:
                raise ValueError(f"Concept parent cycle includes {current}.")
            path.add(current)
            current = parent[current]


def concept_tree(concepts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    children: dict[str | None, list[dict[str, Any]]] = defaultdict(list)
    for concept in concepts:
        children[concept["parent_id"]].append(concept)

    def build(concept: dict[str, Any]) -> dict[str, Any]:
        return {
            **concept,
            "children": [
                build(child)
                for child in sorted(children[concept["id"]], key=lambda item: item["id"])
            ],
        }

    return [build(root) for root in sorted(children[None], key=lambda item: item["id"])]


def concept_diagnostics(
    concepts: list[dict[str, Any]], documents: list[dict[str, str]]
) -> dict[str, Any]:
    matches_by_document: defaultdict[str, list[str]] = defaultdict(list)
    evidence_failures: list[dict[str, str]] = []
    for concept in concepts:
        for match in concept["matches"]:
            matches_by_document[match["document_id"]].append(concept["id"])
            if match["evidence_status"] == "not_found_in_source":
                evidence_failures.append(
                    {
                        "concept_id": concept["id"],
                        "document_id": match["document_id"],
                    }
                )
    matched = set(matches_by_document)
    all_ids = {doc["id"] for doc in documents}
    return {
        "document_count": len(documents),
        "concept_count": len(concepts),
        "matched_document_count": len(matched),
        "coverage": len(matched) / len(documents) if documents else 0.0,
        "unmatched_document_ids": sorted(all_ids - matched),
        "multiply_matched_document_ids": {
            document_id: concept_ids
            for document_id, concept_ids in sorted(matches_by_document.items())
            if len(concept_ids) > 1
        },
        "evidence_quote_failures": evidence_failures,
    }


def render_concept_markdown(nodes: list[dict[str, Any]], level: int = 1) -> str:
    lines: list[str] = []
    for node in nodes:
        lines.append(f"{'#' * min(level, 6)} {node['name']} (`{node['id']}`)")
        lines.append(node["inclusion_criteria"])
        if node["exclusion_criteria"]:
            lines.append(
                "**Excludes:** " + "; ".join(node["exclusion_criteria"])
            )
        for match in node["matches"]:
            suffix = (
                f" — {match['evidence']}"
                if match["evidence"] not in (None, "")
                else ""
            )
            lines.append(
                f"- `{match['document_id']}` [{match['evidence_status']}]{suffix}"
            )
        if node["children"]:
            lines.extend(["", render_concept_markdown(node["children"], level + 1)])
        lines.append("")
    return "\n".join(lines).rstrip()


def adapter_payload(documents: list[dict[str, str]], max_concepts: int) -> dict[str, Any]:
    return {
        "task": "induce_high_level_concepts",
        "method_contract": {
            "concept_fields": [
                "id",
                "name",
                "inclusion_criteria",
                "exclusion_criteria",
                "parent_id",
                "matches",
            ],
            "match_fields": ["document_id", "score", "evidence"],
            "requirements": [
                "Concepts must be high-level and human interpretable.",
                "Every concept requires explicit inclusion criteria.",
                "Each match must name a supplied document.",
                "Evidence quotes must be verbatim substrings when supplied.",
                "Parent relations must form an acyclic hierarchy.",
            ],
            "maximum_concepts": max_concepts,
        },
        "documents": [
            {
                "id": doc["id"],
                "title": doc["title"],
                "text": doc["text"],
                "sha256": doc["sha256"],
            }
            for doc in documents
        ],
    }


def run_adapter(
    command: str,
    payload: dict[str, Any],
    *,
    timeout: int,
) -> tuple[Any, dict[str, Any]]:
    argv = shlex.split(command)
    if not argv:
        raise ValueError("Adapter command is empty.")
    completed = subprocess.run(
        argv,
        input=json.dumps(payload, ensure_ascii=False),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    metadata = {
        "command": argv,
        "return_code": completed.returncode,
        "stderr": completed.stderr[-4000:],
    }
    if completed.returncode != 0:
        raise RuntimeError(
            f"Concept adapter failed with return code {completed.returncode}: "
            f"{completed.stderr[-1000:]}"
        )
    try:
        return json.loads(completed.stdout), metadata
    except json.JSONDecodeError as exc:
        raise RuntimeError("Concept adapter stdout is not valid JSON.") from exc


def write_report(report: dict[str, Any], output: Path | None, markdown: Path | None) -> None:
    payload = json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    if markdown:
        markdown.parent.mkdir(parents=True, exist_ok=True)
        if report["runtime_class"] == "model adapter / induced concept integration":
            rendered = render_concept_markdown(report["tree"])
        else:
            rendered = render_cluster_markdown(report["tree"])
        markdown.write_text(rendered + "\n", encoding="utf-8")


def add_common_output(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output-tree", "--output", dest="output", type=Path)
    parser.add_argument("--markdown", type=Path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Induce/integrate high-level concepts or build an offline hierarchy baseline."
    )
    subparsers = parser.add_subparsers(dest="command")

    cluster = subparsers.add_parser(
        "cluster",
        help="Build a deterministic TF-IDF hierarchy baseline.",
    )
    cluster.add_argument("--papers", "--documents", dest="documents", type=Path, required=True)
    cluster.add_argument("--levels", type=int, default=3)
    cluster.add_argument("--branching-factor", type=int, default=2)
    add_common_output(cluster)

    integrate = subparsers.add_parser(
        "integrate",
        help="Validate and organize supplied high-level concepts.",
    )
    integrate.add_argument("--documents", type=Path, required=True)
    integrate.add_argument("--concepts", type=Path, required=True)
    integrate.add_argument("--fail-on-ungrounded-evidence", action="store_true")
    add_common_output(integrate)

    adapter = subparsers.add_parser(
        "run-adapter",
        help="Invoke a JSON-in/JSON-out concept induction model adapter.",
    )
    adapter.add_argument("--documents", type=Path, required=True)
    adapter.add_argument("--adapter-command", required=True)
    adapter.add_argument("--timeout", type=int, default=300)
    adapter.add_argument("--max-concepts", type=int, default=20)
    adapter.add_argument("--save-adapter-input", type=Path)
    adapter.add_argument("--save-adapter-output", type=Path)
    adapter.add_argument("--fail-on-ungrounded-evidence", action="store_true")
    add_common_output(adapter)
    return parser


def normalize_legacy_argv(argv: Sequence[str]) -> list[str]:
    if not argv or argv[0] in {"-h", "--help", "cluster", "integrate", "run-adapter"}:
        return list(argv)
    if any(value in argv for value in ("--papers", "--levels", "--branching-factor", "--demo")):
        if "--demo" in argv:
            raise ValueError(
                "The legacy --demo fixture was removed from runtime use; supply --papers."
            )
        return ["cluster", *argv]
    return list(argv)


def main(argv: Sequence[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    try:
        normalized = normalize_legacy_argv(raw)
        args = parser.parse_args(normalized)
        if not args.command:
            parser.print_help()
            return 0

        documents = load_documents(args.documents)
        if args.command == "cluster":
            if args.levels < 1 or args.branching_factor < 2:
                raise ValueError("--levels must be >= 1 and --branching-factor >= 2.")
            vectors, token_rows = tfidf_vectors(documents)
            tree = build_cluster_tree(
                documents,
                vectors,
                token_rows,
                list(range(len(documents))),
                1,
                args.levels,
                args.branching_factor,
            )
            report = {
                "tool": "hierarchography",
                "method": METHOD,
                "runtime_class": "deterministic reference baseline",
                "implementation": "standard-library TF-IDF cosine partitioning",
                "documents": [
                    {"id": doc["id"], "title": doc["title"], "sha256": doc["sha256"]}
                    for doc in documents
                ],
                "tree": tree,
                "interpretation": (
                    "This is the explicit offline baseline/ablation path, not LLooM "
                    "concept induction."
                ),
            }
        else:
            adapter_metadata = None
            if args.command == "integrate":
                concept_payload = json.loads(args.concepts.read_text(encoding="utf-8"))
            else:
                payload = adapter_payload(documents, args.max_concepts)
                if args.save_adapter_input:
                    args.save_adapter_input.parent.mkdir(parents=True, exist_ok=True)
                    args.save_adapter_input.write_text(
                        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8",
                    )
                concept_payload, adapter_metadata = run_adapter(
                    args.adapter_command, payload, timeout=args.timeout
                )
                if args.save_adapter_output:
                    args.save_adapter_output.parent.mkdir(parents=True, exist_ok=True)
                    args.save_adapter_output.write_text(
                        json.dumps(concept_payload, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8",
                    )
            concepts = canonical_concepts(concept_payload, documents)
            diagnostics = concept_diagnostics(concepts, documents)
            report = {
                "tool": "hierarchography",
                "method": METHOD,
                "runtime_class": "model adapter / induced concept integration",
                "adapter": adapter_metadata,
                "documents": [
                    {"id": doc["id"], "title": doc["title"], "sha256": doc["sha256"]}
                    for doc in documents
                ],
                "concepts": concepts,
                "tree": concept_tree(concepts),
                "diagnostics": diagnostics,
            }
            if args.fail_on_ungrounded_evidence and diagnostics["evidence_quote_failures"]:
                write_report(report, args.output, args.markdown)
                print(
                    "hierarchography: ungrounded evidence quotes: "
                    f"{len(diagnostics['evidence_quote_failures'])}; "
                    f"inspect {args.output or 'stdout report'}",
                    file=sys.stderr,
                )
                return 1

        write_report(report, args.output, args.markdown)
        return 0
    except (
        OSError,
        ValueError,
        RuntimeError,
        json.JSONDecodeError,
        subprocess.TimeoutExpired,
    ) as exc:
        print(f"hierarchography: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
