#!/usr/bin/env python3
"""Estimate a sample size for a proportion under declared assumptions.

The calculator implements the normal-approximation precision formula with
optional design effect, finite-population correction, and attrition inflation.
Its supplied research use includes silicon-sampling validation: dependence
between model/persona/prompt draws is represented through a declared or
empirically estimated design effect rather than silently treating every draw as
independent.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from statistics import NormalDist
from typing import Any


def calculate_sample_size(
    margin_of_error: float,
    confidence_level: float = 0.95,
    proportion: float = 0.5,
    design_effect: float = 1.0,
    population: int | None = None,
    attrition: float = 0.0,
) -> dict[str, Any]:
    if not 0 < margin_of_error < 1:
        raise ValueError("Margin of error must be between 0 and 1.")
    if not 0 < confidence_level < 1:
        raise ValueError("Confidence level must be between 0 and 1.")
    if not 0 <= proportion <= 1:
        raise ValueError("Proportion must be between 0 and 1.")
    if design_effect <= 0:
        raise ValueError("Design effect must be positive.")
    if population is not None and population < 1:
        raise ValueError("Population must be at least 1.")
    if not 0 <= attrition < 1:
        raise ValueError("Attrition must be in [0, 1).")

    z = NormalDist().inv_cdf(0.5 + confidence_level / 2)
    base = z * z * proportion * (1 - proportion) / (margin_of_error * margin_of_error)
    designed = base * design_effect
    finite = designed
    if population is not None:
        finite = designed / (1 + (designed - 1) / population)
    recruited = finite / (1 - attrition)
    return {
        "tool": "sample_size",
        "method": {
            "runtime_class": "formal calculator",
            "formula": "normal approximation for a proportion",
            "source_context": "synthetic-HCI validation and standard survey precision planning",
        },
        "z_score": z,
        "base_independent_sample": math.ceil(base),
        "after_design_effect": math.ceil(designed),
        "after_finite_population_correction": math.ceil(finite),
        "target_recruitment_after_attrition": math.ceil(recruited),
        "assumptions": {
            "margin_of_error": margin_of_error,
            "confidence_level": confidence_level,
            "proportion": proportion,
            "design_effect": design_effect,
            "population": population,
            "attrition": attrition,
            "method": "normal approximation for a proportion",
        },
        "operating_condition": (
            "The design effect must represent clustering/dependence in the intended "
            "sampling process; estimate it empirically when repeated model, prompt, "
            "persona, or session outputs are the sampling units."
        ),
        "method_selection_note": (
            "Use a method-specific power, precision, information-power, or saturation "
            "analysis when this proportion-precision formula does not match the inferential target."
        ),
    }


def calculate_silicon_sample_size(
    margin_of_error: float,
    confidence_level: float = 0.95,
    heterogeneity: float = 0.5,
    design_effect: float = 1.2,
) -> dict[str, Any]:
    """Compatibility wrapper; the result does not validate synthetic populations."""
    result = calculate_sample_size(margin_of_error, confidence_level, heterogeneity, design_effect)
    result["synthetic_sampling_note"] = (
        "The returned target is a planning count for declared synthetic sampling units. "
        "External validity against the intended human population and an empirically grounded "
        "design effect remain separate validation requirements."
    )
    return result


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Estimate a proportion sample size from explicit assumptions.")
    p.add_argument("--margin", type=float, default=0.05, help="Absolute margin of error, e.g. 0.05.")
    p.add_argument("--confidence", type=float, default=0.95)
    p.add_argument("--proportion", type=float, default=0.5)
    p.add_argument("--design-effect", type=float, default=1.0)
    p.add_argument("--population", type=int)
    p.add_argument("--attrition", type=float, default=0.0)
    p.add_argument("--output", type=Path, help="Write JSON here; stdout if omitted.")
    p.add_argument("--demo", action="store_true")
    return p


def main() -> int:
    args = parser().parse_args()
    try:
        report = calculate_sample_size(
            args.margin,
            args.confidence,
            args.proportion,
            args.design_effect,
            args.population,
            args.attrition,
        )
    except ValueError as exc:
        print(f"sample_size: {exc}", file=sys.stderr)
        return 2
    if args.demo:
        report["demo"] = True
    payload = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
