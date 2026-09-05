#!/usr/bin/env python3
"""Calculate Cohen's or Fleiss' kappa from an explicit agreement matrix.

Scientific grounding: Cohen, "A Coefficient of Agreement for Nominal Scales,"
and the Fleiss multi-rater generalization. The implementation exposes observed
agreement, chance-expected agreement, kappa, category marginals, and the source
matrix so a coding audit can reproduce the result.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Any


def validate_matrix(matrix: Any) -> list[list[float]]:
    if not isinstance(matrix, list) or not matrix or not all(isinstance(row, list) and row for row in matrix):
        raise ValueError("Matrix must be a non-empty JSON/CSV array of non-empty rows.")
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("Matrix rows must have equal length.")
    converted = [[float(value) for value in row] for row in matrix]
    if any(value < 0 or not math.isfinite(value) for row in converted for value in row):
        raise ValueError("Matrix values must be finite and non-negative.")
    return converted


def calculate_cohens_kappa(matrix: list[list[float]]) -> tuple[float, float, float]:
    m = validate_matrix(matrix)
    if len(m) != len(m[0]):
        raise ValueError("Cohen confusion matrix must be square.")
    total = sum(sum(row) for row in m)
    if total == 0:
        raise ValueError("Matrix total must be greater than zero.")
    observed = sum(m[i][i] for i in range(len(m))) / total
    row_sums = [sum(row) for row in m]
    col_sums = [sum(m[i][j] for i in range(len(m))) for j in range(len(m))]
    expected = sum(r * c for r, c in zip(row_sums, col_sums)) / (total * total)
    kappa = 1.0 if expected == 1.0 and observed == 1.0 else (observed - expected) / (1.0 - expected)
    return kappa, observed, expected


def calculate_fleiss_kappa(matrix: list[list[float]]) -> tuple[float, float, float]:
    m = validate_matrix(matrix)
    n_items = len(m)
    raters = sum(m[0])
    if raters <= 1 or any(abs(sum(row) - raters) > 1e-9 for row in m):
        raise ValueError("Each Fleiss row must contain the same number of at least two ratings.")
    category_totals = [sum(row[j] for row in m) for j in range(len(m[0]))]
    p_j = [total / (n_items * raters) for total in category_totals]
    p_i = [(sum(value * value for value in row) - raters) / (raters * (raters - 1)) for row in m]
    observed = sum(p_i) / n_items
    expected = sum(p * p for p in p_j)
    kappa = 1.0 if expected == 1.0 and observed == 1.0 else (observed - expected) / (1.0 - expected)
    return kappa, observed, expected


def interpret_kappa(kappa: float) -> str:
    if kappa < 0:
        return "below chance"
    if kappa <= 0.20:
        return "slight"
    if kappa <= 0.40:
        return "fair"
    if kappa <= 0.60:
        return "moderate"
    if kappa <= 0.80:
        return "substantial"
    return "high"


def load_matrix(path: Path) -> list[list[float]]:
    if path.suffix.casefold() == ".json":
        return validate_matrix(json.loads(path.read_text(encoding="utf-8")))
    with path.open(newline="", encoding="utf-8") as handle:
        return validate_matrix([[cell for cell in row] for row in csv.reader(handle) if row])


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Calculate Cohen's or Fleiss' kappa.")
    p.add_argument("--kind", choices=("cohen", "fleiss"), default="cohen")
    p.add_argument("--matrix", type=Path, help="JSON or CSV matrix.")
    p.add_argument("--output", type=Path, help="Write report JSON here; stdout if omitted.")
    p.add_argument("--demo", action="store_true")
    return p


def main() -> int:
    args = parser().parse_args()
    if args.demo:
        matrix = [[15, 2, 1], [1, 18, 0], [2, 1, 13]] if args.kind == "cohen" else [[0,0,5],[1,4,0],[2,0,3],[0,5,0]]
    elif args.matrix:
        matrix = load_matrix(args.matrix)
    else:
        raise SystemExit("Provide --matrix or --demo.")
    func = calculate_cohens_kappa if args.kind == "cohen" else calculate_fleiss_kappa
    kappa, observed, expected = func(matrix)
    report = {
        "tool": "intercoder",
        "method": {
            "runtime_class": "formal calculator",
            "source": "A Coefficient of Agreement for Nominal Scales",
        },
        "kind": args.kind,
        "matrix": matrix,
        "kappa": kappa,
        "observed_agreement": observed,
        "expected_agreement": expected,
        "descriptive_band": interpret_kappa(kappa),
        "warning": "Interpretation bands are conventional heuristics; inspect prevalence, uncertainty, and disagreement patterns.",
    }
    payload = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
