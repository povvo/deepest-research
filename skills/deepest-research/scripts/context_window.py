#!/usr/bin/env python3
"""Context-budget and position-aware chunking calculator.

Scientific grounding: Liu et al., "Lost in the Middle: How Language Models Use
Long Contexts." The tool separates exact tokenizer-backed counts from explicit
character/token estimates and emits auditable token or character window
manifests. It does not hard-code a vendor model's current context limit.

Optional tokenizer backends are imported lazily:
  * Hugging Face ``transformers`` for a named tokenizer/model repository.
  * ``tiktoken`` for a named encoding.

Without a tokenizer, every token result is marked ``estimated`` and records the
declared characters-per-token assumption.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any, Callable, Sequence

METHOD = {
    "name": "position-aware context planning",
    "source": "Lost in the Middle: How Language Models Use Long Contexts",
    "runtime_class": "formal calculator + tokenizer adapter",
}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def window_ranges(total: int, size: int, overlap: int) -> list[tuple[int, int]]:
    if total < 0:
        raise ValueError("Total length must be non-negative.")
    if size <= 0:
        raise ValueError("Window size must be positive.")
    if overlap < 0 or overlap >= size:
        raise ValueError("Overlap must be non-negative and smaller than window size.")
    if total == 0:
        return []
    starts: list[int] = []
    step = size - overlap
    start = 0
    while start < total:
        starts.append(start)
        if start + size >= total:
            break
        start += step
    return [(start, min(total, start + size)) for start in starts]


def position_band(index: int, count: int) -> str:
    if count <= 1:
        return "whole"
    relative = index / (count - 1)
    if relative <= 1 / 3:
        return "leading"
    if relative >= 2 / 3:
        return "trailing"
    return "middle"


def edge_first_order(count: int) -> list[int]:
    """Return 0,n-1,1,n-2,... for an explicit edge-first scheduling policy."""
    order: list[int] = []
    left, right = 0, count - 1
    while left <= right:
        order.append(left)
        if right != left:
            order.append(right)
        left += 1
        right -= 1
    return order


def estimate_tokens(characters: int, chars_per_token: float) -> int:
    if characters < 0:
        raise ValueError("Character count must be non-negative.")
    if chars_per_token <= 0 or not math.isfinite(chars_per_token):
        raise ValueError("Characters per token must be a positive finite value.")
    return math.ceil(characters / chars_per_token)


def load_huggingface_tokenizer(identifier: str, cache_dir: str | None, trust_remote_code: bool) -> tuple[
    Callable[[str], list[int]], Callable[[Sequence[int]], str], dict[str, Any]
]:
    try:
        from transformers import AutoTokenizer
    except ImportError as exc:
        raise RuntimeError(
            "Hugging Face tokenization requires the optional 'transformers' package."
        ) from exc
    kwargs: dict[str, Any] = {"cache_dir": cache_dir}
    if trust_remote_code:
        kwargs["trust_remote_code"] = True
    tokenizer = AutoTokenizer.from_pretrained(identifier, **kwargs)

    def encode(text: str) -> list[int]:
        return list(tokenizer.encode(text, add_special_tokens=False))

    def decode(ids: Sequence[int]) -> str:
        return tokenizer.decode(list(ids), skip_special_tokens=False)

    return encode, decode, {
        "backend": "huggingface",
        "identifier": identifier,
        "tokenizer_class": type(tokenizer).__name__,
        "vocabulary_size": getattr(tokenizer, "vocab_size", None),
    }


def load_tiktoken_encoding(identifier: str) -> tuple[
    Callable[[str], list[int]], Callable[[Sequence[int]], str], dict[str, Any]
]:
    try:
        import tiktoken
    except ImportError as exc:
        raise RuntimeError("tiktoken tokenization requires the optional 'tiktoken' package.") from exc
    try:
        encoding = tiktoken.get_encoding(identifier)
    except Exception:
        # Permit a model name when the installed version knows it.
        encoding = tiktoken.encoding_for_model(identifier)

    def encode(text: str) -> list[int]:
        return list(encoding.encode(text))

    def decode(ids: Sequence[int]) -> str:
        return encoding.decode(list(ids))

    return encode, decode, {
        "backend": "tiktoken",
        "identifier": identifier,
        "encoding_name": encoding.name,
        "vocabulary_size": getattr(encoding, "n_vocab", None),
    }


def tokenizer_adapter(
    identifier: str,
    backend: str,
    cache_dir: str | None,
    trust_remote_code: bool,
) -> tuple[Callable[[str], list[int]], Callable[[Sequence[int]], str], dict[str, Any]]:
    if backend == "huggingface":
        return load_huggingface_tokenizer(identifier, cache_dir, trust_remote_code)
    if backend == "tiktoken":
        return load_tiktoken_encoding(identifier)
    errors: list[str] = []
    for candidate in ("huggingface", "tiktoken"):
        try:
            return tokenizer_adapter(identifier, candidate, cache_dir, trust_remote_code)
        except (RuntimeError, OSError, ValueError) as exc:
            errors.append(f"{candidate}: {exc}")
    raise RuntimeError("Unable to load tokenizer in auto mode. " + " | ".join(errors))


def budget_report(
    document_tokens: int,
    *,
    token_count_status: str,
    context_limit: int,
    prompt_overhead: int,
    reserved_output: int,
) -> dict[str, Any]:
    if context_limit <= 0:
        raise ValueError("Context limit must be positive.")
    if prompt_overhead < 0 or reserved_output < 0:
        raise ValueError("Prompt overhead and reserved output must be non-negative.")
    usable = context_limit - reserved_output
    if usable < 0:
        raise ValueError("Reserved output exceeds the context limit.")
    total_input = document_tokens + prompt_overhead
    remaining = usable - total_input
    return {
        "document_tokens": document_tokens,
        "token_count_status": token_count_status,
        "prompt_overhead_tokens": prompt_overhead,
        "reserved_output_tokens": reserved_output,
        "context_limit_tokens": context_limit,
        "usable_input_limit_tokens": usable,
        "total_input_tokens": total_input,
        "remaining_input_tokens": remaining,
        "utilization_of_usable_input": total_input / usable if usable else None,
        "fits": remaining >= 0,
    }


def exact_window_manifest(
    token_ids: list[int],
    decoder: Callable[[Sequence[int]], str],
    *,
    size: int,
    overlap: int,
    order_policy: str,
    emit_text: bool,
) -> dict[str, Any]:
    ranges = window_ranges(len(token_ids), size, overlap)
    order = list(range(len(ranges))) if order_policy == "sequential" else edge_first_order(len(ranges))
    scheduled = {original: position for position, original in enumerate(order)}
    windows: list[dict[str, Any]] = []
    for index, (start, end) in enumerate(ranges):
        row: dict[str, Any] = {
            "window_id": index,
            "token_start": start,
            "token_end": end,
            "token_count": end - start,
            "source_position_band": position_band(index, len(ranges)),
            "scheduled_position": scheduled[index],
        }
        if emit_text:
            decoded = decoder(token_ids[start:end])
            row["text"] = decoded
            row["text_sha256"] = sha256_text(decoded)
        windows.append(row)
    return {
        "unit": "tokens",
        "window_size": size,
        "overlap": overlap,
        "step": size - overlap,
        "window_count": len(windows),
        "order_policy": order_policy,
        "scheduled_window_ids": order,
        "windows": windows,
    }


def estimated_window_manifest(
    text: str,
    *,
    size: int,
    overlap: int,
    order_policy: str,
    emit_text: bool,
) -> dict[str, Any]:
    ranges = window_ranges(len(text), size, overlap)
    order = list(range(len(ranges))) if order_policy == "sequential" else edge_first_order(len(ranges))
    scheduled = {original: position for position, original in enumerate(order)}
    windows: list[dict[str, Any]] = []
    for index, (start, end) in enumerate(ranges):
        row: dict[str, Any] = {
            "window_id": index,
            "character_start": start,
            "character_end": end,
            "character_count": end - start,
            "source_position_band": position_band(index, len(ranges)),
            "scheduled_position": scheduled[index],
        }
        if emit_text:
            chunk = text[start:end]
            row["text"] = chunk
            row["text_sha256"] = sha256_text(chunk)
        windows.append(row)
    return {
        "unit": "characters",
        "window_size": size,
        "overlap": overlap,
        "step": size - overlap,
        "window_count": len(windows),
        "order_policy": order_policy,
        "scheduled_window_ids": order,
        "windows": windows,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Count or estimate tokens and build a position-aware chunk manifest."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--text-file", type=Path, help="UTF-8 source text.")
    source.add_argument("--chars", type=int, help="Character count when source text is unavailable.")

    parser.add_argument("--tokenizer", help="Named tokenizer/model or tiktoken encoding.")
    parser.add_argument(
        "--tokenizer-backend",
        choices=["auto", "huggingface", "tiktoken"],
        default="auto",
    )
    parser.add_argument("--cache-dir")
    parser.add_argument("--trust-remote-code", action="store_true")
    parser.add_argument("--chars-per-token", type=float, default=4.0)
    parser.add_argument("--context-limit", type=int, required=True)
    parser.add_argument("--prompt-overhead", type=int, default=1_500)
    parser.add_argument("--reserved-output", type=int, default=4_000)

    token_window = parser.add_argument_group("exact token windows")
    token_window.add_argument("--chunk-tokens", type=int)
    token_window.add_argument("--overlap-tokens", type=int, default=0)

    char_window = parser.add_argument_group("estimated character windows")
    char_window.add_argument("--chunk-chars", type=int)
    char_window.add_argument("--overlap-chars", type=int, default=0)

    parser.add_argument(
        "--order-policy",
        choices=["sequential", "edge-first"],
        default="sequential",
        help="Scheduling metadata only; it does not infer which chunk is relevant.",
    )
    parser.add_argument("--emit-text", action="store_true", help="Include decoded/raw chunk text.")
    parser.add_argument("--output", type=Path, help="Optional JSON report; stdout is always emitted.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.text_file:
            text = args.text_file.read_text(encoding="utf-8", errors="replace")
            characters = len(text)
            source = {
                "path": str(args.text_file),
                "characters": characters,
                "utf8_bytes": len(text.encode("utf-8")),
                "sha256": sha256_text(text),
            }
        else:
            if args.chars is None or args.chars < 0:
                raise ValueError("--chars must be non-negative.")
            text = None
            characters = args.chars
            source = {"path": None, "characters": characters, "sha256": None}

        adapter_meta: dict[str, Any] | None = None
        token_ids: list[int] | None = None
        decoder: Callable[[Sequence[int]], str] | None = None
        if args.tokenizer:
            if text is None:
                raise ValueError("Exact tokenization requires --text-file.")
            encoder, decoder, adapter_meta = tokenizer_adapter(
                args.tokenizer,
                args.tokenizer_backend,
                args.cache_dir,
                args.trust_remote_code,
            )
            token_ids = encoder(text)
            document_tokens = len(token_ids)
            token_status = "exact_tokenizer"
        else:
            document_tokens = estimate_tokens(characters, args.chars_per_token)
            token_status = "estimated_from_characters"

        report: dict[str, Any] = {
            "tool": "context_window",
            "method": METHOD,
            "source": source,
            "tokenizer": adapter_meta,
            "estimation": (
                None
                if token_ids is not None
                else {"characters_per_token": args.chars_per_token}
            ),
            "budget": budget_report(
                document_tokens,
                token_count_status=token_status,
                context_limit=args.context_limit,
                prompt_overhead=args.prompt_overhead,
                reserved_output=args.reserved_output,
            ),
            "position_note": (
                "Window fit and scheduling do not establish uniform model use of evidence; "
                "validate task performance across relevant-information positions."
            ),
        }

        if args.chunk_tokens is not None:
            if token_ids is None or decoder is None:
                raise ValueError("--chunk-tokens requires --tokenizer and --text-file.")
            report["windows"] = exact_window_manifest(
                token_ids,
                decoder,
                size=args.chunk_tokens,
                overlap=args.overlap_tokens,
                order_policy=args.order_policy,
                emit_text=args.emit_text,
            )
        elif args.chunk_chars is not None:
            if text is None:
                # A count-only manifest can still expose spans without text.
                text = " " * characters if args.emit_text else ""
                ranges = window_ranges(characters, args.chunk_chars, args.overlap_chars)
                order = (
                    list(range(len(ranges)))
                    if args.order_policy == "sequential"
                    else edge_first_order(len(ranges))
                )
                scheduled = {original: position for position, original in enumerate(order)}
                report["windows"] = {
                    "unit": "characters",
                    "window_size": args.chunk_chars,
                    "overlap": args.overlap_chars,
                    "step": args.chunk_chars - args.overlap_chars,
                    "window_count": len(ranges),
                    "order_policy": args.order_policy,
                    "scheduled_window_ids": order,
                    "windows": [
                        {
                            "window_id": i,
                            "character_start": start,
                            "character_end": end,
                            "character_count": end - start,
                            "source_position_band": position_band(i, len(ranges)),
                            "scheduled_position": scheduled[i],
                        }
                        for i, (start, end) in enumerate(ranges)
                    ],
                }
            else:
                report["windows"] = estimated_window_manifest(
                    text,
                    size=args.chunk_chars,
                    overlap=args.overlap_chars,
                    order_policy=args.order_policy,
                    emit_text=args.emit_text,
                )

        payload = json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(payload, encoding="utf-8")
        sys.stdout.write(payload)
        return 0
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"context_window: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
