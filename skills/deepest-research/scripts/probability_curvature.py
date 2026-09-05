#!/usr/bin/env python3
"""Fast-DetectGPT conditional-probability-curvature detector.

This implementation follows Bao et al., "Fast-DetectGPT: Efficient Zero-Shot
Detection of Machine-Generated Text via Conditional Probability Curvature"
(ICLR 2024). It provides three production paths:

* ``criterion`` computes the analytic Fast-DetectGPT statistic from supplied
  reference/scoring logits and next-token labels.
* ``detect`` runs named Hugging Face causal language models, computes the
  statistic, and applies either a declared curvature threshold or a calibrated
  Gaussian profile.
* ``calibrate`` derives a threshold and distribution profile from labelled
  in-domain criterion values.

Model inference imports ``torch`` and ``transformers`` lazily. The deterministic
``criterion`` and ``calibrate`` paths use only the Python standard library.

A detector result is valid only for its recorded model pair, tokenization,
language/domain, text-length range, and calibration/threshold. Do not invent
confidence scores or silently transfer thresholds between operating conditions.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence


METHOD = {
    "name": "Fast-DetectGPT",
    "paper": "Fast-DetectGPT: Efficient Zero-Shot Detection of Machine-Generated Text via Conditional Probability Curvature",
    "arxiv": "2310.05130",
    "criterion": "analytic conditional probability curvature",
}

# Parameters published in the authors' local inference implementation.
# Names are compatibility keys used by that implementation, not universal
# calibration claims.
BUILTIN_PROFILES: dict[str, dict[str, Any]] = {
    "gpt-j-6B__gpt-neo-2.7B": {
        "sampling_model": "gpt-j-6B",
        "scoring_model": "gpt-neo-2.7B",
        "mu_human": 0.2713,
        "sigma_human": 0.9366,
        "mu_llm": 2.2334,
        "sigma_llm": 1.8731,
        "source": "Fast-DetectGPT authors' local_infer.py",
    },
    "gpt-neo-2.7B__gpt-neo-2.7B": {
        "sampling_model": "gpt-neo-2.7B",
        "scoring_model": "gpt-neo-2.7B",
        "mu_human": -0.2489,
        "sigma_human": 0.9968,
        "mu_llm": 1.8983,
        "sigma_llm": 1.9935,
        "source": "Fast-DetectGPT authors' local_infer.py",
    },
    "falcon-7b__falcon-7b-instruct": {
        "sampling_model": "falcon-7b",
        "scoring_model": "falcon-7b-instruct",
        "mu_human": -0.0707,
        "sigma_human": 0.9520,
        "mu_llm": 2.9306,
        "sigma_llm": 1.9039,
        "source": "Fast-DetectGPT authors' local_infer.py",
    },
    "llama3-8b__llama3-8b-instruct": {
        "sampling_model": "meta-llama/Meta-Llama-3-8B",
        "scoring_model": "meta-llama/Meta-Llama-3-8B-Instruct",
        "mu_human": 0.1603,
        "sigma_human": 1.0791,
        "mu_llm": 2.4686,
        "sigma_llm": 2.1582,
        "source": "Fast-DetectGPT authors' local_infer.py",
    },
}


@dataclass(frozen=True)
class CalibrationProfile:
    name: str
    sampling_model: str
    scoring_model: str
    mu_human: float
    sigma_human: float
    mu_llm: float
    sigma_llm: float
    threshold: float | None = None
    threshold_objective: str | None = None
    calibration_n_human: int | None = None
    calibration_n_llm: int | None = None
    domain: str | None = None
    language: str | None = None
    min_tokens: int | None = None
    max_tokens: int | None = None
    source: str | None = None


def _ensure_finite(values: Iterable[float], label: str) -> None:
    if not all(math.isfinite(float(value)) for value in values):
        raise ValueError(f"{label} contains a non-finite value.")


def _log_softmax(row: Sequence[float]) -> list[float]:
    if not row:
        raise ValueError("Logit rows must not be empty.")
    _ensure_finite(row, "logits")
    maximum = max(float(value) for value in row)
    log_denom = maximum + math.log(sum(math.exp(float(value) - maximum) for value in row))
    return [float(value) - log_denom for value in row]


def _softmax(row: Sequence[float]) -> list[float]:
    if not row:
        raise ValueError("Logit rows must not be empty.")
    _ensure_finite(row, "logits")
    maximum = max(float(value) for value in row)
    exps = [math.exp(float(value) - maximum) for value in row]
    total = sum(exps)
    return [value / total for value in exps]


def conditional_probability_curvature(
    reference_logits: Sequence[Sequence[float]],
    scoring_logits: Sequence[Sequence[float]],
    labels: Sequence[int],
    *,
    allow_vocab_truncation: bool = False,
) -> dict[str, Any]:
    """Compute the analytic Fast-DetectGPT discrepancy for one sequence.

    For each token position, the observed next-token log-likelihood under the
    scoring model is compared with the expectation and variance induced by
    conditional samples from the reference model. The sequence statistic is

        (sum(observed) - sum(expected)) / sqrt(sum(variance)).
    """

    if not reference_logits or not scoring_logits or not labels:
        raise ValueError("Reference logits, scoring logits, and labels must be non-empty.")
    if len(reference_logits) != len(scoring_logits) or len(labels) != len(scoring_logits):
        raise ValueError("Token dimensions of reference logits, scoring logits, and labels must match.")

    observed_sum = 0.0
    expected_sum = 0.0
    variance_sum = 0.0
    token_rows: list[dict[str, float | int]] = []
    vocab_truncated = False

    for position, (ref_row_raw, score_row_raw, label_raw) in enumerate(
        zip(reference_logits, scoring_logits, labels)
    ):
        ref_row = [float(value) for value in ref_row_raw]
        score_row = [float(value) for value in score_row_raw]
        if len(ref_row) != len(score_row):
            if not allow_vocab_truncation:
                raise ValueError(
                    f"Vocabulary mismatch at token {position}: "
                    f"{len(ref_row)} reference versus {len(score_row)} scoring."
                )
            width = min(len(ref_row), len(score_row))
            ref_row = ref_row[:width]
            score_row = score_row[:width]
            vocab_truncated = True
        if not ref_row:
            raise ValueError(f"Empty vocabulary at token {position}.")
        label = int(label_raw)
        if label < 0 or label >= len(score_row):
            raise ValueError(f"Label {label} at token {position} is outside vocabulary size {len(score_row)}.")

        score_log_probs = _log_softmax(score_row)
        reference_probs = _softmax(ref_row)
        observed = score_log_probs[label]
        expected = sum(prob * log_prob for prob, log_prob in zip(reference_probs, score_log_probs))
        second_moment = sum(
            prob * (log_prob * log_prob)
            for prob, log_prob in zip(reference_probs, score_log_probs)
        )
        variance = max(0.0, second_moment - expected * expected)

        observed_sum += observed
        expected_sum += expected
        variance_sum += variance
        token_rows.append(
            {
                "position": position,
                "label": label,
                "observed_log_probability": observed,
                "expected_log_probability": expected,
                "conditional_variance": variance,
            }
        )

    if variance_sum <= 0.0:
        raise ValueError("Summed conditional variance is zero; curvature is undefined.")
    criterion = (observed_sum - expected_sum) / math.sqrt(variance_sum)
    return {
        "method": METHOD,
        "criterion": criterion,
        "token_count": len(labels),
        "observed_log_probability_sum": observed_sum,
        "expected_log_probability_sum": expected_sum,
        "conditional_variance_sum": variance_sum,
        "vocabulary_truncated": vocab_truncated,
        "token_statistics": token_rows,
    }


def normal_pdf(value: float, mean: float, sigma: float) -> float:
    if sigma <= 0 or not math.isfinite(sigma):
        raise ValueError("Distribution sigma must be positive and finite.")
    z = (value - mean) / sigma
    return math.exp(-0.5 * z * z) / (sigma * math.sqrt(2.0 * math.pi))


def gaussian_llm_probability(criterion: float, profile: CalibrationProfile) -> float:
    """Return equal-prior posterior probability under the profile's Gaussians."""

    human_density = normal_pdf(criterion, profile.mu_human, profile.sigma_human)
    llm_density = normal_pdf(criterion, profile.mu_llm, profile.sigma_llm)
    denominator = human_density + llm_density
    if denominator == 0:
        # Both densities underflow only extremely far into the tails. Compare
        # log densities to retain the equal-prior decision.
        log_human = -math.log(profile.sigma_human) - 0.5 * (
            (criterion - profile.mu_human) / profile.sigma_human
        ) ** 2
        log_llm = -math.log(profile.sigma_llm) - 0.5 * (
            (criterion - profile.mu_llm) / profile.sigma_llm
        ) ** 2
        delta = max(-700.0, min(700.0, log_human - log_llm))
        return 1.0 / (1.0 + math.exp(delta))
    return llm_density / denominator


def profile_from_mapping(name: str, data: dict[str, Any]) -> CalibrationProfile:
    aliases = {
        "mu0": "mu_human",
        "sigma0": "sigma_human",
        "mu1": "mu_llm",
        "sigma1": "sigma_llm",
        "sampling_model_name": "sampling_model",
        "scoring_model_name": "scoring_model",
    }
    normalized = dict(data)
    for old, new in aliases.items():
        if new not in normalized and old in normalized:
            normalized[new] = normalized[old]
    required = [
        "sampling_model",
        "scoring_model",
        "mu_human",
        "sigma_human",
        "mu_llm",
        "sigma_llm",
    ]
    missing = [key for key in required if key not in normalized]
    if missing:
        raise ValueError(f"Calibration profile is missing: {', '.join(missing)}")
    return CalibrationProfile(
        name=name,
        sampling_model=str(normalized["sampling_model"]),
        scoring_model=str(normalized["scoring_model"]),
        mu_human=float(normalized["mu_human"]),
        sigma_human=float(normalized["sigma_human"]),
        mu_llm=float(normalized["mu_llm"]),
        sigma_llm=float(normalized["sigma_llm"]),
        threshold=(None if normalized.get("threshold") is None else float(normalized["threshold"])),
        threshold_objective=normalized.get("threshold_objective"),
        calibration_n_human=normalized.get("calibration_n_human"),
        calibration_n_llm=normalized.get("calibration_n_llm"),
        domain=normalized.get("domain"),
        language=normalized.get("language"),
        min_tokens=normalized.get("min_tokens"),
        max_tokens=normalized.get("max_tokens"),
        source=normalized.get("source"),
    )


def load_profile(value: str | None) -> CalibrationProfile | None:
    if value is None:
        return None
    if value in BUILTIN_PROFILES:
        return profile_from_mapping(value, BUILTIN_PROFILES[value])
    path = Path(value)
    if not path.is_file():
        available = ", ".join(sorted(BUILTIN_PROFILES))
        raise ValueError(f"Unknown profile {value!r}. Built-ins: {available}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Calibration profile must be a JSON object.")
    return profile_from_mapping(str(data.get("name") or path.stem), data)


def classify(
    criterion: float,
    *,
    threshold: float | None,
    profile: CalibrationProfile | None,
    probability_cutoff: float,
) -> dict[str, Any]:
    if threshold is not None:
        return {
            "classification": "LLM-generated" if criterion > threshold else "human-written",
            "decision_rule": "criterion > threshold",
            "threshold": threshold,
            "llm_probability": (
                gaussian_llm_probability(criterion, profile) if profile is not None else None
            ),
        }
    if profile is None:
        return {
            "classification": None,
            "decision_rule": None,
            "threshold": None,
            "llm_probability": None,
            "status": "criterion_only",
        }
    probability = gaussian_llm_probability(criterion, profile)
    return {
        "classification": "LLM-generated" if probability >= probability_cutoff else "human-written",
        "decision_rule": "equal-prior Gaussian profile probability >= cutoff",
        "threshold": profile.threshold,
        "probability_cutoff": probability_cutoff,
        "llm_probability": probability,
    }


def load_logits_payload(path: Path) -> tuple[list[list[float]], list[list[float]], list[int]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Criterion input must be a JSON object.")
    reference = data.get("reference_logits", data.get("logits_ref"))
    scoring = data.get("scoring_logits", data.get("logits_score"))
    labels = data.get("labels")
    if not isinstance(reference, list) or not isinstance(scoring, list) or not isinstance(labels, list):
        raise ValueError("Input requires reference_logits, scoring_logits, and labels arrays.")
    # Accept a leading batch dimension of one for compatibility with tensor dumps.
    if reference and isinstance(reference[0], list) and reference[0] and isinstance(reference[0][0], list):
        if len(reference) != 1 or len(scoring) != 1 or (
            labels and isinstance(labels[0], list) and len(labels) != 1
        ):
            raise ValueError("JSON criterion mode supports exactly one sequence.")
        reference = reference[0]
        scoring = scoring[0]
        if labels and isinstance(labels[0], list):
            labels = labels[0]
    return reference, scoring, [int(value) for value in labels]


def iter_calibration_rows(path: Path) -> Iterable[tuple[float, str]]:
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            criterion = float(row["criterion"])
            label = str(row["label"]).strip().casefold()
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid calibration row {line_number}: {exc}") from exc
        if label in {"human", "human-written", "real", "0"}:
            canonical = "human"
        elif label in {"llm", "llm-generated", "machine", "synthetic", "fake", "1"}:
            canonical = "llm"
        else:
            raise ValueError(f"Unknown label {label!r} on row {line_number}.")
        if not math.isfinite(criterion):
            raise ValueError(f"Non-finite criterion on row {line_number}.")
        yield criterion, canonical


def confusion_at_threshold(
    human: Sequence[float], llm: Sequence[float], threshold: float
) -> dict[str, float | int]:
    true_negative = sum(value <= threshold for value in human)
    false_positive = len(human) - true_negative
    true_positive = sum(value > threshold for value in llm)
    false_negative = len(llm) - true_positive
    tpr = true_positive / len(llm)
    fpr = false_positive / len(human)
    tnr = true_negative / len(human)
    return {
        "threshold": threshold,
        "true_positive": true_positive,
        "false_positive": false_positive,
        "true_negative": true_negative,
        "false_negative": false_negative,
        "true_positive_rate": tpr,
        "false_positive_rate": fpr,
        "true_negative_rate": tnr,
        "balanced_accuracy": (tpr + tnr) / 2.0,
        "youden_j": tpr - fpr,
    }


def choose_threshold(
    human: Sequence[float],
    llm: Sequence[float],
    *,
    target_fpr: float | None,
) -> tuple[float, dict[str, float | int], str]:
    unique = sorted(set(float(value) for value in [*human, *llm]))
    if not unique:
        raise ValueError("Calibration data are empty.")
    candidates = [unique[0] - 1e-12]
    candidates.extend((left + right) / 2.0 for left, right in zip(unique, unique[1:]))
    candidates.append(unique[-1] + 1e-12)
    metrics = [confusion_at_threshold(human, llm, value) for value in candidates]
    if target_fpr is not None:
        feasible = [row for row in metrics if float(row["false_positive_rate"]) <= target_fpr]
        if not feasible:
            best = min(metrics, key=lambda row: float(row["false_positive_rate"]))
        else:
            best = max(
                feasible,
                key=lambda row: (
                    float(row["true_positive_rate"]),
                    float(row["balanced_accuracy"]),
                    -float(row["threshold"]),
                ),
            )
        objective = f"maximize TPR subject to FPR <= {target_fpr:g}"
    else:
        best = max(
            metrics,
            key=lambda row: (
                float(row["balanced_accuracy"]),
                float(row["youden_j"]),
                -abs(float(row["threshold"])),
            ),
        )
        objective = "maximize balanced accuracy"
    return float(best["threshold"]), best, objective


def sample_sigma(values: Sequence[float]) -> float:
    if len(values) < 2:
        raise ValueError("Each calibration class needs at least two observations.")
    sigma = statistics.stdev(values)
    if sigma <= 0:
        raise ValueError("Calibration class has zero variance.")
    return sigma


def run_criterion(args: argparse.Namespace) -> dict[str, Any]:
    reference, scoring, labels = load_logits_payload(Path(args.input))
    result = conditional_probability_curvature(
        reference,
        scoring,
        labels,
        allow_vocab_truncation=args.allow_vocab_truncation,
    )
    profile = load_profile(args.profile)
    result["calibration_profile"] = asdict(profile) if profile else None
    result.update(
        classify(
            float(result["criterion"]),
            threshold=args.threshold,
            profile=profile,
            probability_cutoff=args.probability_cutoff,
        )
    )
    return result


def _dtype_from_name(torch_module: Any, name: str, device: str) -> Any:
    if name == "auto":
        return torch_module.float16 if str(device).startswith("cuda") else torch_module.float32
    return {
        "float32": torch_module.float32,
        "float16": torch_module.float16,
        "bfloat16": torch_module.bfloat16,
    }[name]


def run_model_detection(args: argparse.Namespace) -> dict[str, Any]:
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise RuntimeError(
            "Model-backed detection requires torch and transformers. "
            "Install them in the execution environment or use criterion mode."
        ) from exc

    profile = load_profile(args.profile)
    sampling_model_name = args.sampling_model or (profile.sampling_model if profile else None)
    scoring_model_name = args.scoring_model or (profile.scoring_model if profile else None)
    if not sampling_model_name or not scoring_model_name:
        raise ValueError(
            "Provide --sampling-model and --scoring-model, or select a profile that names both."
        )

    text = Path(args.input).read_text(encoding="utf-8", errors="replace") if args.input else args.text
    if not text or not text.strip():
        raise ValueError("Detection text is empty.")

    if args.device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device = args.device
    dtype = _dtype_from_name(torch, args.dtype, device)

    tokenizer_kwargs: dict[str, Any] = {"cache_dir": args.cache_dir}
    model_kwargs: dict[str, Any] = {"cache_dir": args.cache_dir, "torch_dtype": dtype}
    if args.trust_remote_code:
        tokenizer_kwargs["trust_remote_code"] = True
        model_kwargs["trust_remote_code"] = True

    scoring_tokenizer = AutoTokenizer.from_pretrained(scoring_model_name, **tokenizer_kwargs)
    scoring_model = AutoModelForCausalLM.from_pretrained(scoring_model_name, **model_kwargs).to(device)
    scoring_model.eval()

    scoring_tokens = scoring_tokenizer(
        text,
        truncation=True,
        max_length=args.max_length,
        return_tensors="pt",
        return_token_type_ids=False,
    ).to(device)
    if scoring_tokens.input_ids.shape[1] < 2:
        raise ValueError("Text must yield at least two tokens.")
    labels = scoring_tokens.input_ids[:, 1:]
    with torch.no_grad():
        scoring_logits = scoring_model(**scoring_tokens).logits[:, :-1, :]

    if sampling_model_name == scoring_model_name:
        reference_logits = scoring_logits
    else:
        sampling_tokenizer = AutoTokenizer.from_pretrained(sampling_model_name, **tokenizer_kwargs)
        sampling_model = AutoModelForCausalLM.from_pretrained(sampling_model_name, **model_kwargs).to(device)
        sampling_model.eval()
        sampling_tokens = sampling_tokenizer(
            text,
            truncation=True,
            max_length=args.max_length,
            return_tensors="pt",
            return_token_type_ids=False,
        ).to(device)
        if sampling_tokens.input_ids.shape != scoring_tokens.input_ids.shape or not torch.equal(
            sampling_tokens.input_ids[:, 1:], labels
        ):
            raise ValueError(
                "Sampling and scoring tokenizers produced different next-token labels; "
                "Fast-DetectGPT requires compatible tokenization for this model pair."
            )
        with torch.no_grad():
            reference_logits = sampling_model(**sampling_tokens).logits[:, :-1, :]

    # Use the same tensor expression as the Fast-DetectGPT analytic criterion.
    vocab_size = min(reference_logits.shape[-1], scoring_logits.shape[-1])
    if reference_logits.shape[-1] != scoring_logits.shape[-1] and not args.allow_vocab_truncation:
        raise ValueError(
            f"Vocabulary mismatch: {reference_logits.shape[-1]} reference versus "
            f"{scoring_logits.shape[-1]} scoring. Re-run with --allow-vocab-truncation "
            "only when the model pair is known to share aligned token IDs."
        )
    reference_logits = reference_logits[..., :vocab_size]
    scoring_logits = scoring_logits[..., :vocab_size]
    if int(labels.max()) >= vocab_size:
        raise ValueError("A next-token label lies outside the aligned vocabulary.")

    log_probs_score = torch.log_softmax(scoring_logits, dim=-1)
    probs_reference = torch.softmax(reference_logits, dim=-1)
    observed = log_probs_score.gather(dim=-1, index=labels.unsqueeze(-1)).squeeze(-1)
    expected = (probs_reference * log_probs_score).sum(dim=-1)
    variance = (probs_reference * torch.square(log_probs_score)).sum(dim=-1) - torch.square(expected)
    variance_sum = variance.sum(dim=-1)
    if bool(torch.any(variance_sum <= 0)):
        raise ValueError("Summed conditional variance is zero; curvature is undefined.")
    criterion_value = ((observed.sum(dim=-1) - expected.sum(dim=-1)) / variance_sum.sqrt()).mean().item()

    result: dict[str, Any] = {
        "method": METHOD,
        "criterion": float(criterion_value),
        "token_count": int(labels.shape[1]),
        "sampling_model": sampling_model_name,
        "scoring_model": scoring_model_name,
        "device": str(device),
        "dtype": args.dtype,
        "max_length": args.max_length,
        "text_truncated": int(scoring_tokens.input_ids.shape[1]) >= args.max_length,
        "calibration_profile": asdict(profile) if profile else None,
    }
    result.update(
        classify(
            float(criterion_value),
            threshold=args.threshold,
            profile=profile,
            probability_cutoff=args.probability_cutoff,
        )
    )
    result["operating_scope"] = {
        "domain": args.domain,
        "language": args.language,
        "threshold_source": args.threshold_source,
        "note": (
            "Interpret only within the declared model-pair, tokenizer, language/domain, "
            "length, and calibration conditions. Record review and appeal procedures "
            "when the result informs an academic-integrity decision."
        ),
    }
    return result


def run_calibrate(args: argparse.Namespace) -> dict[str, Any]:
    rows = list(iter_calibration_rows(Path(args.input)))
    human = [value for value, label in rows if label == "human"]
    llm = [value for value, label in rows if label == "llm"]
    if len(human) < 2 or len(llm) < 2:
        raise ValueError("Calibration requires at least two human and two LLM criterion values.")
    threshold, metrics, objective = choose_threshold(human, llm, target_fpr=args.target_fpr)
    profile = CalibrationProfile(
        name=args.name,
        sampling_model=args.sampling_model,
        scoring_model=args.scoring_model,
        mu_human=statistics.fmean(human),
        sigma_human=sample_sigma(human),
        mu_llm=statistics.fmean(llm),
        sigma_llm=sample_sigma(llm),
        threshold=threshold,
        threshold_objective=objective,
        calibration_n_human=len(human),
        calibration_n_llm=len(llm),
        domain=args.domain,
        language=args.language,
        min_tokens=args.min_tokens,
        max_tokens=args.max_tokens,
        source=args.source,
    )
    return {
        **asdict(profile),
        "method": METHOD,
        "calibration_metrics": metrics,
        "label_rule": "criterion > threshold => LLM-generated",
    }


def write_result(result: dict[str, Any], output: str | None) -> None:
    payload = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload + "\n", encoding="utf-8")
    print(payload)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compute, calibrate, or run Fast-DetectGPT conditional probability curvature."
    )
    parser.add_argument(
        "--list-profiles",
        action="store_true",
        help="Print bundled calibration-profile metadata and exit.",
    )
    subparsers = parser.add_subparsers(dest="command")

    criterion_parser = subparsers.add_parser(
        "criterion",
        help="Compute the analytic criterion from JSON logits and labels.",
    )
    criterion_parser.add_argument("--input", required=True, help="JSON logits fixture.")
    criterion_parser.add_argument("--output", help="Optional JSON report path.")
    criterion_parser.add_argument("--profile", help="Built-in profile name or profile JSON path.")
    criterion_parser.add_argument("--threshold", type=float, help="Declared curvature threshold epsilon.")
    criterion_parser.add_argument("--probability-cutoff", type=float, default=0.5)
    criterion_parser.add_argument(
        "--allow-vocab-truncation",
        action="store_true",
        help="Align logits by the smaller vocabulary; use only for compatible token IDs.",
    )

    detect_parser = subparsers.add_parser(
        "detect",
        help="Run model-backed Fast-DetectGPT detection.",
    )
    text_group = detect_parser.add_mutually_exclusive_group(required=True)
    text_group.add_argument("--input", help="UTF-8 text file.")
    text_group.add_argument("--text", help="Literal text.")
    detect_parser.add_argument("--output", help="Optional JSON report path.")
    detect_parser.add_argument("--sampling-model", help="Reference/sampling causal LM identifier.")
    detect_parser.add_argument("--scoring-model", help="Scoring causal LM identifier.")
    detect_parser.add_argument("--profile", help="Built-in profile name or profile JSON path.")
    detect_parser.add_argument("--threshold", type=float, help="Declared curvature threshold epsilon.")
    detect_parser.add_argument("--probability-cutoff", type=float, default=0.5)
    detect_parser.add_argument("--threshold-source", help="Citation, calibration report, or protocol locator.")
    detect_parser.add_argument("--domain", help="Declared operating domain.")
    detect_parser.add_argument("--language", help="Declared language.")
    detect_parser.add_argument("--max-length", type=int, default=512)
    detect_parser.add_argument("--device", default="auto", help="auto, cpu, cuda, or a torch device.")
    detect_parser.add_argument(
        "--dtype",
        choices=["auto", "float32", "float16", "bfloat16"],
        default="auto",
    )
    detect_parser.add_argument("--cache-dir")
    detect_parser.add_argument("--trust-remote-code", action="store_true")
    detect_parser.add_argument("--allow-vocab-truncation", action="store_true")

    calibrate_parser = subparsers.add_parser(
        "calibrate",
        help="Fit a threshold and Gaussian profile from labelled criterion JSONL.",
    )
    calibrate_parser.add_argument("--input", required=True, help="JSONL with criterion and label.")
    calibrate_parser.add_argument("--output", required=True, help="Profile JSON report path.")
    calibrate_parser.add_argument("--name", required=True)
    calibrate_parser.add_argument("--sampling-model", required=True)
    calibrate_parser.add_argument("--scoring-model", required=True)
    calibrate_parser.add_argument("--target-fpr", type=float)
    calibrate_parser.add_argument("--domain")
    calibrate_parser.add_argument("--language")
    calibrate_parser.add_argument("--min-tokens", type=int)
    calibrate_parser.add_argument("--max-tokens", type=int)
    calibrate_parser.add_argument("--source", help="Dataset/protocol provenance locator.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.list_profiles:
        print(json.dumps(BUILTIN_PROFILES, indent=2, sort_keys=True))
        return 0
    if not args.command:
        parser.print_help()
        return 0
    try:
        if args.command == "criterion":
            result = run_criterion(args)
            write_result(result, args.output)
        elif args.command == "detect":
            result = run_model_detection(args)
            write_result(result, args.output)
        elif args.command == "calibrate":
            if args.target_fpr is not None and not 0 <= args.target_fpr <= 1:
                raise ValueError("--target-fpr must be between 0 and 1.")
            result = run_calibrate(args)
            write_result(result, args.output)
        else:
            raise ValueError(f"Unknown command: {args.command}")
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
