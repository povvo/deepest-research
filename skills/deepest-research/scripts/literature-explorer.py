#!/usr/bin/env python3
"""Scientific literature retrieval and reranking with reproducible provenance.

Grounded in LitSearch and S2ORC. The script can retrieve arXiv Atom records or
parse a saved feed, then rank with a transparent lexical/BM25 baseline, an
optional SentenceTransformers dense retriever, and an optional JSON-in/JSON-out
listwise reranker command. Every stage preserves the original records, query,
ranker configuration, and component scores.

A successful query is a documented search operation, not a completeness or
novelty verdict.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import re
import shlex
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence


METHOD = {
    "sources": [
        "LitSearch: A Retrieval Benchmark for Scientific Literature Search",
        "S2ORC: The Semantic Scholar Open Research Corpus",
    ],
    "stages": ["retrieval", "first-stage ranking", "optional listwise reranking"],
}
ATOM = {"atom": "http://www.w3.org/2005/Atom"}
ARXIV_API = "https://export.arxiv.org/api/query"


def compact(text: str | None) -> str:
    return " ".join((text or "").split())


def parse_atom(xml_data: bytes) -> list[dict[str, Any]]:
    root = ET.fromstring(xml_data)
    records: list[dict[str, Any]] = []
    for entry in root.findall("atom:entry", ATOM):
        def field(tag: str) -> str:
            node = entry.find(f"atom:{tag}", ATOM)
            return compact(node.text if node is not None else "")

        links = [
            {
                "href": link.attrib.get("href"),
                "rel": link.attrib.get("rel"),
                "type": link.attrib.get("type"),
                "title": link.attrib.get("title"),
            }
            for link in entry.findall("atom:link", ATOM)
        ]
        records.append(
            {
                "id": field("id"),
                "title": field("title"),
                "abstract": field("summary"),
                "published": field("published"),
                "updated": field("updated"),
                "authors": [
                    compact(node.text)
                    for node in entry.findall("atom:author/atom:name", ATOM)
                ],
                "categories": [
                    node.attrib.get("term")
                    for node in entry.findall("atom:category", ATOM)
                    if node.attrib.get("term")
                ],
                "links": links,
            }
        )
    return records


def build_arxiv_url(query: str, start: int, max_results: int, sort_by: str, sort_order: str) -> str:
    parameters = urllib.parse.urlencode(
        {
            "search_query": query,
            "start": start,
            "max_results": max_results,
            "sortBy": sort_by,
            "sortOrder": sort_order,
        }
    )
    return f"{ARXIV_API}?{parameters}"


def fetch(url: str, timeout: float, retries: int, user_agent: str) -> bytes:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": user_agent})
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(min(8.0, 0.5 * (2**attempt)))
    raise RuntimeError(f"arXiv request failed after {retries + 1} attempts: {last_error}")


def tokenize(text: str) -> list[str]:
    return re.findall(r"\b[\w-]{2,}\b", text.casefold(), flags=re.UNICODE)


def record_text(record: dict[str, Any]) -> str:
    return f"{record.get('title', '')}\n{record.get('abstract', '')}"


def lexical_scores(records: Sequence[dict[str, Any]], query: str) -> list[float]:
    query_terms = tokenize(query)
    scores = []
    for record in records:
        counts = Counter(tokenize(record_text(record)))
        title_counts = Counter(tokenize(str(record.get("title", ""))))
        score = sum(counts[term] + 2 * title_counts[term] for term in query_terms)
        scores.append(float(score))
    return scores


def bm25_scores(
    records: Sequence[dict[str, Any]],
    query: str,
    *,
    k1: float,
    b: float,
) -> list[float]:
    documents = [tokenize(record_text(record)) for record in records]
    if not documents:
        return []
    average_length = sum(len(document) for document in documents) / len(documents)
    document_frequency: Counter[str] = Counter()
    for document in documents:
        document_frequency.update(set(document))
    query_terms = tokenize(query)
    scores: list[float] = []
    total_documents = len(documents)
    for document in documents:
        counts = Counter(document)
        length = len(document)
        score = 0.0
        for term in query_terms:
            df = document_frequency.get(term, 0)
            idf = math.log(1.0 + (total_documents - df + 0.5) / (df + 0.5))
            tf = counts.get(term, 0)
            denominator = tf + k1 * (1.0 - b + b * length / max(1.0, average_length))
            if denominator:
                score += idf * (tf * (k1 + 1.0)) / denominator
        scores.append(score)
    return scores


def dense_scores(records: Sequence[dict[str, Any]], query: str, model_name: str) -> list[float]:
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError(
            "Dense ranking requires sentence-transformers; use --ranker bm25 or install it."
        ) from exc
    model = SentenceTransformer(model_name)
    embeddings = model.encode(
        [query, *[record_text(record) for record in records]],
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    query_embedding = embeddings[0]
    return [float(query_embedding @ vector) for vector in embeddings[1:]]


def first_stage_rank(
    records: Sequence[dict[str, Any]],
    query: str,
    *,
    ranker: str,
    model_name: str,
    k1: float,
    b: float,
) -> list[dict[str, Any]]:
    if ranker == "lexical":
        scores = lexical_scores(records, query)
    elif ranker == "bm25":
        scores = bm25_scores(records, query, k1=k1, b=b)
    elif ranker == "dense":
        scores = dense_scores(records, query, model_name)
    else:
        raise ValueError(f"Unknown ranker {ranker}.")
    ranked = []
    for index, (record, score) in enumerate(zip(records, scores)):
        item = dict(record)
        item["retrieval_index"] = index
        item["first_stage_score"] = score
        item["first_stage_ranker"] = ranker
        ranked.append(item)
    ranked.sort(
        key=lambda item: (
            -float(item["first_stage_score"]),
            str(item.get("published", "")),
            str(item.get("id", "")),
        )
    )
    for rank, item in enumerate(ranked, start=1):
        item["first_stage_rank"] = rank
    return ranked


def run_reranker(
    command: str,
    query: str,
    candidates: Sequence[dict[str, Any]],
    *,
    timeout: float,
) -> list[dict[str, Any]]:
    argv = shlex.split(command)
    if not argv:
        raise ValueError("Reranker command is empty.")
    request = {
        "query": query,
        "candidates": [
            {
                "candidate_id": str(index),
                "title": item.get("title"),
                "abstract": item.get("abstract"),
                "first_stage_rank": item.get("first_stage_rank"),
                "first_stage_score": item.get("first_stage_score"),
            }
            for index, item in enumerate(candidates)
        ],
        "response_contract": {
            "ranking": ["candidate_id"],
            "optional_scores": {"candidate_id": "number"},
        },
    }
    completed = subprocess.run(
        argv,
        input=json.dumps(request, ensure_ascii=False),
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"Reranker exited {completed.returncode}: {completed.stderr.strip()}"
        )
    try:
        response = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Reranker did not return JSON on stdout.") from exc
    ranking = response.get("ranking") if isinstance(response, dict) else None
    if not isinstance(ranking, list):
        raise RuntimeError("Reranker response requires a ranking array.")
    order = [str(value) for value in ranking]
    expected = {str(index) for index in range(len(candidates))}
    if set(order) != expected or len(order) != len(expected):
        raise RuntimeError("Reranker ranking must contain every candidate_id exactly once.")
    scores = response.get("scores", {}) if isinstance(response, dict) else {}
    reranked = []
    for rank, candidate_id in enumerate(order, start=1):
        item = dict(candidates[int(candidate_id)])
        item["rerank_rank"] = rank
        item["rerank_score"] = scores.get(candidate_id) if isinstance(scores, dict) else None
        reranked.append(item)
    return reranked


def load_records(path: Path) -> list[dict[str, Any]]:
    if path.suffix.casefold() in {".xml", ".atom"}:
        return parse_atom(path.read_bytes())
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("records"), list):
        data = data["records"]
    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise ValueError("Input must contain a JSON record array or an Atom feed.")
    return data


def build_report(
    records: Sequence[dict[str, Any]],
    *,
    query: str,
    source: dict[str, Any],
    ranker: str,
    dense_model: str,
    k1: float,
    b: float,
    top_k: int,
    rerank_command: str | None,
    rerank_timeout: float,
) -> dict[str, Any]:
    ranked = first_stage_rank(
        records,
        query,
        ranker=ranker,
        model_name=dense_model,
        k1=k1,
        b=b,
    )
    selected = ranked[:top_k] if top_k > 0 else ranked
    reranker_record = None
    if rerank_command:
        selected = run_reranker(rerank_command, query, selected, timeout=rerank_timeout)
        reranker_record = {"argv": shlex.split(rerank_command), "candidate_count": len(selected)}
    return {
        "tool": "literature-explorer",
        "method": METHOD,
        "query": query,
        "retrieval": source,
        "ranking": {
            "first_stage": {
                "ranker": ranker,
                "dense_model": dense_model if ranker == "dense" else None,
                "bm25_k1": k1 if ranker == "bm25" else None,
                "bm25_b": b if ranker == "bm25" else None,
            },
            "reranker": reranker_record,
        },
        "record_count": len(records),
        "returned_count": len(selected),
        "records": selected,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Retrieve or parse scientific records and rank them reproducibly."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--query", help="arXiv API search query.")
    source.add_argument("--input-feed", help="Saved Atom XML.")
    source.add_argument("--input-json", help="Saved JSON records.")
    parser.add_argument(
        "--ranking-query",
        help="Natural-language ranking query; defaults to --query or an empty string.",
    )
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--max-results", type=int, default=100)
    parser.add_argument(
        "--sort-by",
        choices=("relevance", "lastUpdatedDate", "submittedDate"),
        default="relevance",
    )
    parser.add_argument("--sort-order", choices=("ascending", "descending"), default="descending")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--user-agent", default="research-planner/1.0 (literature-search)")
    parser.add_argument("--save-feed", help="Save raw Atom response.")
    parser.add_argument("--ranker", choices=("lexical", "bm25", "dense"), default="bm25")
    parser.add_argument("--dense-model", default="allenai/specter2_base")
    parser.add_argument("--bm25-k1", type=float, default=1.2)
    parser.add_argument("--bm25-b", type=float, default=0.75)
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--rerank-command", help="JSON-in/JSON-out listwise reranker command.")
    parser.add_argument("--rerank-timeout", type=float, default=600.0)
    parser.add_argument("--output", default="arxiv_results.json")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.query:
            url = build_arxiv_url(
                args.query, args.start, args.max_results, args.sort_by, args.sort_order
            )
            raw = fetch(url, args.timeout, args.retries, args.user_agent)
            if args.save_feed:
                feed_path = Path(args.save_feed)
                feed_path.parent.mkdir(parents=True, exist_ok=True)
                feed_path.write_bytes(raw)
            records = parse_atom(raw)
            source = {
                "source": "arXiv API",
                "url": url,
                "retrieved_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                "raw_feed_saved": args.save_feed,
            }
            ranking_query = args.ranking_query or args.query
        else:
            path = Path(args.input_feed or args.input_json)
            records = load_records(path)
            source = {
                "source": "saved file",
                "path": str(path),
                "retrieved_at_utc": None,
            }
            ranking_query = args.ranking_query or ""
        report = build_report(
            records,
            query=ranking_query,
            source=source,
            ranker=args.ranker,
            dense_model=args.dense_model,
            k1=args.bm25_k1,
            b=args.bm25_b,
            top_k=args.top_k,
            rerank_command=args.rerank_command,
            rerank_timeout=args.rerank_timeout,
        )
        payload = json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
        print(payload, end="")
    except (
        OSError,
        ValueError,
        RuntimeError,
        subprocess.TimeoutExpired,
        urllib.error.URLError,
        ET.ParseError,
        json.JSONDecodeError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
