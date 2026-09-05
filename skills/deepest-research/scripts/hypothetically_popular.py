#!/usr/bin/env python3
"""Train and apply an Upworthy-style headline engagement model.

The implementation is grounded in randomized headline experiments and in
Banerjee & Urminsky's construct-based analysis of language and engagement.
Unlike the former demo, production predictions require a fitted model artifact;
no hand-written score is presented as predicted engagement.

Training constructs within-test headline pairs so that comparisons are made
inside the same randomized experiment. Tests flagged for randomization risk are
excluded by default. A deterministic group split keeps all packages from one
test in the same train or evaluation partition.

Training, evaluation, export, and prediction use only the Python standard
library. The optimizer is deterministic Adam over a weighted pairwise logistic
objective with L2 regularization controlled by ``C``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import statistics
import sys
from dataclasses import dataclass
from datetime import date
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable, Sequence


METHOD = {
    "name": "within-experiment headline engagement comparison",
    "sources": [
        "The Language That Drives Engagement: A Systematic Large-scale Analysis of Headline Experiments",
        "The Upworthy Research Archive, a Time Series of 32,487 Experiments in U.S. Media",
    ],
}

POSITIVE = {
    "amazing", "beautiful", "best", "brilliant", "delight", "good", "great",
    "happy", "hope", "incredible", "inspiring", "love", "powerful", "success",
}
NEGATIVE = {
    "awful", "bad", "crisis", "danger", "dead", "death", "fail", "fear",
    "hate", "horrible", "risk", "sad", "shocking", "terrible", "worst",
}
URGENCY = {
    "breaking", "immediately", "now", "today", "tonight", "urgent", "warning",
}
CERTAINTY = {
    "always", "certain", "clearly", "definitely", "must", "never", "proven",
}
UNCERTAINTY = {
    "could", "likely", "may", "might", "perhaps", "possibly", "suggests",
}
SECOND_PERSON = {"you", "your", "yours", "yourself", "yourselves"}
FIRST_PERSON = {"i", "me", "my", "mine", "we", "our", "ours", "us"}
NEGATIONS = {"no", "not", "never", "none", "nothing", "without"}
CTA = {"click", "discover", "find", "learn", "look", "read", "see", "share", "watch"}

FEATURE_NAMES = [
    "word_count",
    "character_count",
    "mean_word_length",
    "long_word_share",
    "unique_word_share",
    "number_count",
    "question_count",
    "exclamation_count",
    "colon_count",
    "dash_count",
    "quote_count",
    "all_caps_token_share",
    "positive_share",
    "negative_share",
    "urgency_share",
    "certainty_share",
    "uncertainty_share",
    "second_person_share",
    "first_person_share",
    "negation_share",
    "cta_share",
]


@dataclass(frozen=True)
class Package:
    test_id: str
    headline: str
    impressions: int
    clicks: int
    risk_flag: bool

    @property
    def ctr(self) -> float:
        return self.clicks / self.impressions


def words(text: str) -> list[str]:
    return re.findall(r"\b[\w'-]+\b", text, flags=re.UNICODE)


def text_features(text: str) -> dict[str, float]:
    tokens_original = words(text)
    tokens = [token.casefold() for token in tokens_original]
    count = max(1, len(tokens))
    alpha = [token for token in tokens if any(char.isalpha() for char in token)]
    alpha_count = max(1, len(alpha))

    def share(lexicon: set[str]) -> float:
        return sum(token in lexicon for token in tokens) / count

    return {
        "word_count": float(len(tokens)),
        "character_count": float(len(text)),
        "mean_word_length": (
            sum(len(token) for token in alpha) / alpha_count if alpha else 0.0
        ),
        "long_word_share": sum(len(token) >= 7 for token in alpha) / alpha_count if alpha else 0.0,
        "unique_word_share": len(set(tokens)) / count if tokens else 0.0,
        "number_count": float(len(re.findall(r"\b\d+(?:[.,]\d+)?%?\b", text))),
        "question_count": float(text.count("?")),
        "exclamation_count": float(text.count("!")),
        "colon_count": float(text.count(":")),
        "dash_count": float(len(re.findall(r"[-–—]", text))),
        "quote_count": float(len(re.findall(r"""["“”'‘’]""", text))),
        "all_caps_token_share": (
            sum(token.isupper() and any(char.isalpha() for char in token) for token in tokens_original)
            / count
        ),
        "positive_share": share(POSITIVE),
        "negative_share": share(NEGATIVE),
        "urgency_share": share(URGENCY),
        "certainty_share": share(CERTAINTY),
        "uncertainty_share": share(UNCERTAINTY),
        "second_person_share": share(SECOND_PERSON),
        "first_person_share": share(FIRST_PERSON),
        "negation_share": share(NEGATIONS),
        "cta_share": share(CTA),
    }


def vector(text: str) -> list[float]:
    features = text_features(text)
    return [float(features[name]) for name in FEATURE_NAMES]


def truthy(value: Any) -> bool:
    return str(value).strip().casefold() in {"1", "true", "yes", "y", "risk", "flagged"}


def load_packages(
    path: Path,
    *,
    test_column: str,
    headline_column: str,
    impressions_column: str,
    clicks_column: str,
    risk_columns: Sequence[str],
    include_flagged: bool,
) -> tuple[list[Package], dict[str, int]]:
    packages: list[Package] = []
    skipped = {"empty_headline": 0, "invalid_counts": 0, "flagged": 0}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("Training CSV has no header.")
        required = {test_column, headline_column, impressions_column, clicks_column}
        missing = sorted(required - set(reader.fieldnames))
        if missing:
            raise ValueError(f"Training CSV is missing columns: {', '.join(missing)}")
        available_risk = [column for column in risk_columns if column in reader.fieldnames]
        for row_number, row in enumerate(reader, start=2):
            headline = str(row.get(headline_column, "")).strip()
            if not headline:
                skipped["empty_headline"] += 1
                continue
            try:
                impressions = int(float(str(row[impressions_column]).replace(",", "")))
                clicks = int(float(str(row[clicks_column]).replace(",", "")))
            except (TypeError, ValueError):
                skipped["invalid_counts"] += 1
                continue
            if impressions <= 0 or clicks < 0 or clicks > impressions:
                skipped["invalid_counts"] += 1
                continue
            risk = any(truthy(row.get(column, "")) for column in available_risk)
            if risk and not include_flagged:
                skipped["flagged"] += 1
                continue
            test_id = str(row.get(test_column, "")).strip()
            if not test_id:
                skipped["invalid_counts"] += 1
                continue
            packages.append(Package(test_id, headline, impressions, clicks, risk))
    return packages, skipped


def stable_partition(test_id: str, evaluation_fraction: float) -> str:
    digest = hashlib.sha256(test_id.encode("utf-8")).digest()
    value = int.from_bytes(digest[:8], "big") / 2**64
    return "evaluation" if value < evaluation_fraction else "training"


def make_pairs(
    packages: Sequence[Package],
    *,
    evaluation_fraction: float,
    max_pairs_per_test: int,
) -> tuple[list[list[float]], list[int], list[float], list[str], list[dict[str, Any]]]:
    groups: dict[str, list[Package]] = {}
    for package in packages:
        groups.setdefault(package.test_id, []).append(package)

    differences: list[list[float]] = []
    labels: list[int] = []
    weights: list[float] = []
    partitions: list[str] = []
    provenance: list[dict[str, Any]] = []

    for test_id in sorted(groups):
        group = groups[test_id]
        candidate_pairs = list(combinations(group, 2))
        if max_pairs_per_test > 0:
            candidate_pairs = candidate_pairs[:max_pairs_per_test]
        for first, second in candidate_pairs:
            if math.isclose(first.ctr, second.ctr, rel_tol=0.0, abs_tol=1e-15):
                continue
            first_vector, second_vector = vector(first.headline), vector(second.headline)
            diff = [left - right for left, right in zip(first_vector, second_vector)]
            label = int(first.ctr > second.ctr)
            # Effective comparison weight: harmonic mean of randomized exposures,
            # square-rooted to stop very large tests dominating the fit.
            effective_n = 2.0 / (1.0 / first.impressions + 1.0 / second.impressions)
            weight = math.sqrt(effective_n)
            differences.append(diff)
            labels.append(label)
            weights.append(weight)
            partitions.append(stable_partition(test_id, evaluation_fraction))
            provenance.append(
                {
                    "test_id": test_id,
                    "first_ctr": first.ctr,
                    "second_ctr": second.ctr,
                    "first_impressions": first.impressions,
                    "second_impressions": second.impressions,
                }
            )
            # Add the symmetric ordering so the classifier is order-invariant.
            differences.append([-value for value in diff])
            labels.append(1 - label)
            weights.append(weight)
            partitions.append(stable_partition(test_id, evaluation_fraction))
            provenance.append(
                {
                    "test_id": test_id,
                    "first_ctr": second.ctr,
                    "second_ctr": first.ctr,
                    "first_impressions": second.impressions,
                    "second_impressions": first.impressions,
                }
            )
    return differences, labels, weights, partitions, provenance


def weighted_mean_std(rows: Sequence[Sequence[float]], weights: Sequence[float]) -> tuple[list[float], list[float]]:
    if not rows:
        raise ValueError("No training rows.")
    width = len(rows[0])
    total_weight = sum(weights)
    means = [
        sum(weight * row[index] for row, weight in zip(rows, weights)) / total_weight
        for index in range(width)
    ]
    variances = [
        sum(weight * (row[index] - means[index]) ** 2 for row, weight in zip(rows, weights))
        / total_weight
        for index in range(width)
    ]
    scales = [math.sqrt(value) if value > 1e-12 else 1.0 for value in variances]
    return means, scales


def standardize(row: Sequence[float], means: Sequence[float], scales: Sequence[float]) -> list[float]:
    return [(value - mean) / scale for value, mean, scale in zip(row, means, scales)]


def sigmoid(value: float) -> float:
    if value >= 0:
        exponent = math.exp(-value)
        return 1.0 / (1.0 + exponent)
    exponent = math.exp(value)
    return exponent / (1.0 + exponent)


def predict_probability(model: dict[str, Any], first: str, second: str) -> tuple[float, dict[str, float]]:
    if model.get("model_type") != "standardized_pairwise_logistic_regression":
        raise ValueError("Unsupported model type.")
    feature_names = model.get("feature_names")
    if feature_names != FEATURE_NAMES:
        raise ValueError("Model feature schema does not match this script version.")
    first_features, second_features = text_features(first), text_features(second)
    difference = [first_features[name] - second_features[name] for name in FEATURE_NAMES]
    normalized = standardize(difference, model["means"], model["scales"])
    logit = float(model["intercept"]) + sum(
        float(coefficient) * value for coefficient, value in zip(model["coefficients"], normalized)
    )
    return sigmoid(logit), {
        name: difference[index] for index, name in enumerate(FEATURE_NAMES)
    }


def evaluate_predictions(
    probabilities: Sequence[float],
    labels: Sequence[int],
    weights: Sequence[float],
) -> dict[str, float | int]:
    if not probabilities:
        return {"n": 0}
    total_weight = sum(weights)
    accuracy = sum(
        weight * int((probability >= 0.5) == bool(label))
        for probability, label, weight in zip(probabilities, labels, weights)
    ) / total_weight
    brier = sum(
        weight * (probability - label) ** 2
        for probability, label, weight in zip(probabilities, labels, weights)
    ) / total_weight
    epsilon = 1e-15
    log_loss = -sum(
        weight
        * (
            label * math.log(max(epsilon, probability))
            + (1 - label) * math.log(max(epsilon, 1 - probability))
        )
        for probability, label, weight in zip(probabilities, labels, weights)
    ) / total_weight
    return {
        "n": len(probabilities),
        "weighted_accuracy": accuracy,
        "weighted_brier_score": brier,
        "weighted_log_loss": log_loss,
    }


def weighted_logistic_objective(
    rows: Sequence[Sequence[float]],
    labels: Sequence[int],
    sample_weights: Sequence[float],
    coefficients: Sequence[float],
    intercept: float,
    *,
    c: float,
) -> float:
    if c <= 0:
        raise ValueError("C must be positive.")
    total_weight = sum(sample_weights)
    if total_weight <= 0:
        raise ValueError("Sample weights must sum to a positive value.")
    loss = 0.0
    for row, label, weight in zip(rows, labels, sample_weights):
        logit = intercept + sum(value * coefficient for value, coefficient in zip(row, coefficients))
        # Stable Bernoulli negative log-likelihood.
        if logit >= 0:
            nll = (1 - label) * logit + math.log1p(math.exp(-logit))
        else:
            nll = -label * logit + math.log1p(math.exp(logit))
        loss += weight * nll
    regularization = 0.5 * sum(value * value for value in coefficients) / c
    return (loss + regularization) / total_weight


def fit_weighted_logistic(
    rows: Sequence[Sequence[float]],
    labels: Sequence[int],
    sample_weights: Sequence[float],
    *,
    c: float,
    max_iter: int,
    learning_rate: float,
    tolerance: float,
) -> tuple[list[float], float, dict[str, Any]]:
    """Fit deterministic weighted pairwise logistic regression with Adam."""

    if not rows or len(rows) != len(labels) or len(rows) != len(sample_weights):
        raise ValueError("Rows, labels, and sample weights must be non-empty and aligned.")
    if c <= 0 or max_iter < 1 or learning_rate <= 0 or tolerance <= 0:
        raise ValueError("C, max iterations, learning rate, and tolerance must be positive.")
    width = len(rows[0])
    if width == 0 or any(len(row) != width for row in rows):
        raise ValueError("Training rows must have one consistent non-zero width.")
    if set(labels) - {0, 1}:
        raise ValueError("Logistic labels must be 0 or 1.")
    total_weight = sum(sample_weights)
    if total_weight <= 0 or any(weight < 0 for weight in sample_weights):
        raise ValueError("Sample weights must be non-negative with positive total.")

    coefficients = [0.0] * width
    intercept = 0.0
    m = [0.0] * (width + 1)
    v = [0.0] * (width + 1)
    beta1, beta2, epsilon = 0.9, 0.999, 1e-8
    previous = float("inf")
    stable_rounds = 0
    converged = False
    final_iteration = 0

    for iteration in range(1, max_iter + 1):
        gradient = [0.0] * (width + 1)
        for row, label, weight in zip(rows, labels, sample_weights):
            logit = intercept + sum(
                value * coefficient for value, coefficient in zip(row, coefficients)
            )
            probability = sigmoid(logit)
            residual = weight * (probability - label) / total_weight
            gradient[0] += residual
            for index, value in enumerate(row, start=1):
                gradient[index] += residual * value

        # sklearn-style C intuition: larger C means weaker L2 regularization.
        for index, coefficient in enumerate(coefficients, start=1):
            gradient[index] += coefficient / (c * total_weight)

        for index, value in enumerate(gradient):
            m[index] = beta1 * m[index] + (1 - beta1) * value
            v[index] = beta2 * v[index] + (1 - beta2) * value * value
            m_hat = m[index] / (1 - beta1**iteration)
            v_hat = v[index] / (1 - beta2**iteration)
            update = learning_rate * m_hat / (math.sqrt(v_hat) + epsilon)
            if index == 0:
                intercept -= update
            else:
                coefficients[index - 1] -= update

        objective = weighted_logistic_objective(
            rows,
            labels,
            sample_weights,
            coefficients,
            intercept,
            c=c,
        )
        if not math.isfinite(objective):
            raise ValueError("Optimizer produced a non-finite objective.")
        relative_change = abs(previous - objective) / max(1.0, abs(previous))
        if relative_change <= tolerance:
            stable_rounds += 1
            if stable_rounds >= 10:
                converged = True
                final_iteration = iteration
                break
        else:
            stable_rounds = 0
        previous = objective
        final_iteration = iteration

    diagnostics = {
        "optimizer": "deterministic Adam",
        "iterations": final_iteration,
        "converged": converged,
        "final_objective": weighted_logistic_objective(
            rows,
            labels,
            sample_weights,
            coefficients,
            intercept,
            c=c,
        ),
        "learning_rate": learning_rate,
        "tolerance": tolerance,
        "l2_inverse_strength_c": c,
    }
    return coefficients, intercept, diagnostics



def artifact_record(path: Path) -> dict[str, Any]:
    """Return immutable file provenance for a training or model artefact."""
    resolved = path.resolve()
    payload = resolved.read_bytes()
    return {
        "path": str(resolved),
        "name": resolved.name,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def run_train(args: argparse.Namespace) -> dict[str, Any]:
    if not 0 < args.evaluation_fraction < 1:
        raise ValueError("--evaluation-fraction must be between 0 and 1.")
    packages, skipped = load_packages(
        Path(args.input),
        test_column=args.test_column,
        headline_column=args.headline_column,
        impressions_column=args.impressions_column,
        clicks_column=args.clicks_column,
        risk_columns=args.risk_column,
        include_flagged=args.include_flagged,
    )
    differences, labels, weights, partitions, provenance = make_pairs(
        packages,
        evaluation_fraction=args.evaluation_fraction,
        max_pairs_per_test=args.max_pairs_per_test,
    )
    train_indices = [index for index, part in enumerate(partitions) if part == "training"]
    eval_indices = [index for index, part in enumerate(partitions) if part == "evaluation"]
    if len(train_indices) < 4 or len(set(labels[index] for index in train_indices)) < 2:
        raise ValueError("Not enough training pairs with both outcomes.")
    if not eval_indices:
        raise ValueError("Deterministic split produced no evaluation pairs; adjust the fraction or data.")

    train_rows = [differences[index] for index in train_indices]
    train_labels = [labels[index] for index in train_indices]
    train_weights = [weights[index] for index in train_indices]
    means, scales = weighted_mean_std(train_rows, train_weights)
    train_standardized = [standardize(row, means, scales) for row in train_rows]

    coefficients, intercept, optimizer = fit_weighted_logistic(
        train_standardized,
        train_labels,
        train_weights,
        c=args.c,
        max_iter=args.max_iter,
        learning_rate=args.learning_rate,
        tolerance=args.tolerance,
    )

    model = {
        "schema_version": 1,
        "model_type": "standardized_pairwise_logistic_regression",
        "method": METHOD,
        "feature_names": FEATURE_NAMES,
        "means": means,
        "scales": scales,
        "coefficients": coefficients,
        "intercept": intercept,
        "training": {
            "created": date.today().isoformat(),
            "input": str(Path(args.input).name),
            "input_artifact": artifact_record(Path(args.input)),
            "columns": {
                "test_id": args.test_column,
                "headline": args.headline_column,
                "impressions": args.impressions_column,
                "clicks": args.clicks_column,
                "risk_flags": list(args.risk_column),
            },
            "packages_retained": len(packages),
            "pairs_training": len(train_indices),
            "pairs_evaluation": len(eval_indices),
            "tests_training": len({provenance[index]["test_id"] for index in train_indices}),
            "tests_evaluation": len({provenance[index]["test_id"] for index in eval_indices}),
            "risk_rows_included": bool(args.include_flagged),
            "skipped": skipped,
            "evaluation_fraction": args.evaluation_fraction,
            "group_split": {
                "unit": args.test_column,
                "assignment": "sha256(test_id)",
                "leakage_guard": "all packages and pairs from one test remain in one partition",
            },
            "c": args.c,
            "optimizer": optimizer,
        },
    }

    train_probabilities = [
        predict_probability_from_difference(model, differences[index])
        for index in train_indices
    ]
    eval_probabilities = [
        predict_probability_from_difference(model, differences[index])
        for index in eval_indices
    ]
    model["training"]["training_metrics"] = evaluate_predictions(
        train_probabilities, train_labels, train_weights
    )
    model["training"]["evaluation_metrics"] = evaluate_predictions(
        eval_probabilities,
        [labels[index] for index in eval_indices],
        [weights[index] for index in eval_indices],
    )
    model["operating_scope"] = {
        "outcome": "within-test click-through comparison",
        "population_platform_period": args.operating_scope,
        "not_established": [
            "engagement on a different platform, period, language, or audience",
            "content quality, truth, scientific merit, downstream sharing, or social benefit",
        ],
    }
    return model


def predict_probability_from_difference(model: dict[str, Any], difference: Sequence[float]) -> float:
    normalized = standardize(difference, model["means"], model["scales"])
    logit = float(model["intercept"]) + sum(
        float(coefficient) * value for coefficient, value in zip(model["coefficients"], normalized)
    )
    return sigmoid(logit)


def run_predict(args: argparse.Namespace) -> dict[str, Any]:
    model = json.loads(Path(args.model).read_text(encoding="utf-8"))
    first = Path(args.first_file).read_text(encoding="utf-8") if args.first_file else args.first
    second = Path(args.second_file).read_text(encoding="utf-8") if args.second_file else args.second
    probability, feature_difference = predict_probability(model, first, second)
    selected = "first" if probability >= args.cutoff else "second"
    return {
        "method": METHOD,
        "model_artifact": artifact_record(Path(args.model)),
        "first_text": first,
        "second_text": second,
        "probability_first_higher_click_through": probability,
        "decision_cutoff": args.cutoff,
        "selected": selected,
        "feature_difference_first_minus_second": feature_difference,
        "model_training": model.get("training"),
        "operating_scope": model.get("operating_scope"),
    }


def run_features(args: argparse.Namespace) -> dict[str, Any]:
    text = Path(args.input).read_text(encoding="utf-8") if args.input else args.text
    return {
        "method": METHOD,
        "text": text,
        "features": text_features(text),
        "status": "features_only",
    }


def write_json(data: dict[str, Any], output: str | None) -> None:
    payload = json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True)
    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload + "\n", encoding="utf-8")
    print(payload)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Train or apply a source-grounded within-experiment headline engagement model."
    )
    subparsers = parser.add_subparsers(dest="command")

    train = subparsers.add_parser("train", help="Train a pairwise model from an Upworthy-style CSV.")
    train.add_argument("--input", required=True)
    train.add_argument("--output", required=True)
    train.add_argument("--test-column", default="clickability_test_id")
    train.add_argument("--headline-column", default="headline")
    train.add_argument("--impressions-column", default="impressions")
    train.add_argument("--clicks-column", default="clicks")
    train.add_argument(
        "--risk-column",
        action="append",
        default=["problem", "randomization_imbalance_risk", "randomization_imbalace_risk"],
        help="Risk flag column; may be repeated.",
    )
    train.add_argument("--include-flagged", action="store_true")
    train.add_argument("--evaluation-fraction", type=float, default=0.2)
    train.add_argument("--max-pairs-per-test", type=int, default=100)
    train.add_argument("--c", type=float, default=1.0)
    train.add_argument("--max-iter", type=int, default=4000)
    train.add_argument("--learning-rate", type=float, default=0.03)
    train.add_argument("--tolerance", type=float, default=1e-8)
    train.add_argument(
        "--operating-scope",
        default="Upworthy randomized headline tests, 2013-2015",
    )

    predict = subparsers.add_parser("predict", help="Compare two headlines with a trained JSON model.")
    predict.add_argument("--model", required=True)
    first_group = predict.add_mutually_exclusive_group(required=True)
    first_group.add_argument("--first")
    first_group.add_argument("--first-file")
    second_group = predict.add_mutually_exclusive_group(required=True)
    second_group.add_argument("--second")
    second_group.add_argument("--second-file")
    predict.add_argument("--cutoff", type=float, default=0.5)
    predict.add_argument("--output")

    features = subparsers.add_parser("features", help="Extract the model's transparent text features.")
    feature_group = features.add_mutually_exclusive_group(required=True)
    feature_group.add_argument("--text")
    feature_group.add_argument("--input")
    features.add_argument("--output")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0
    try:
        if args.command == "train":
            result = run_train(args)
            write_json(result, args.output)
        elif args.command == "predict":
            if not 0 <= args.cutoff <= 1:
                raise ValueError("--cutoff must be between 0 and 1.")
            result = run_predict(args)
            write_json(result, args.output)
        elif args.command == "features":
            result = run_features(args)
            write_json(result, args.output)
        else:
            raise ValueError(f"Unknown command {args.command}")
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
