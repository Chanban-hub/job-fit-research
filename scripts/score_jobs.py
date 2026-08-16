#!/usr/bin/env python3
"""Rank jobs by candidate fit, absolute job quality, and application value.

Input scores are evidence judgments made by the agent, each on a 0–5 scale.
This script applies weights, confidence shrinkage, risk caps, and formatting.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


FIT_WEIGHTS = {
    "eligibility": 0.25,
    "skills": 0.25,
    "evidence": 0.20,
    "career": 0.15,
    "competition": 0.10,
    "constraints": 0.05,
}

QUALITY_WEIGHTS_WLB_FIRST = {
    "sustainability": 0.25,
    "growth": 0.20,
    "compensation": 0.15,
    "platform": 0.15,
    "mobility": 0.15,
    "stability": 0.10,
}

QUALITY_WEIGHTS_SALARY_GROWTH = {
    "compensation": 0.25,
    "growth": 0.25,
    "platform": 0.15,
    "mobility": 0.15,
    "sustainability": 0.10,
    "stability": 0.10,
}

QUALITY_BASES = {
    "wlb_first": QUALITY_WEIGHTS_WLB_FIRST,
    "salary_growth_fallback": QUALITY_WEIGHTS_SALARY_GROWTH,
}

BASIS_LABELS = {
    "wlb_first": "WLB",
    "salary_growth_fallback": "Salary+growth",
}


def bounded_score(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a number from 0 to 5")
    value = float(value)
    if not 0 <= value <= 5:
        raise ValueError(f"{field} must be between 0 and 5")
    return value


def fit_label(fit: float) -> str:
    if fit >= 85:
        return "excellent"
    if fit >= 70:
        return "good"
    if fit >= 55:
        return "plausible-with-gaps"
    if fit >= 40:
        return "weak/stretch"
    return "poor"


def quality_label(job_quality: float) -> str:
    if job_quality >= 85:
        return "exceptional"
    if job_quality >= 70:
        return "good"
    if job_quality >= 55:
        return "above-average/tradeoffs"
    if job_quality >= 40:
        return "below-average"
    return "poor"


def recommendation(
    fit: float,
    job_quality: float,
    application_value: float,
    hard_gate_failed: bool,
    severe_quality_risk: bool,
) -> str:
    if hard_gate_failed:
        return "ineligible"
    if severe_quality_risk or job_quality < 40:
        return "skip/quality-risk"
    if application_value >= 80 and fit >= 70:
        return "priority"
    if application_value >= 65 and fit >= 60:
        return "apply"
    if job_quality >= 70 and fit < 60:
        return "stretch"
    if application_value >= 50:
        return "conditional"
    return "skip"


def score_job(job: dict[str, Any]) -> dict[str, Any]:
    company = str(job.get("company", "")).strip()
    role = str(job.get("role", "")).strip()
    if not company or not role:
        raise ValueError("each job requires non-empty company and role")

    fit_components = job.get("fit_scores")
    if not isinstance(fit_components, dict):
        raise ValueError(f"{company} / {role}: fit_scores must be an object")

    missing = [key for key in FIT_WEIGHTS if key not in fit_components]
    if missing:
        raise ValueError(
            f"{company} / {role}: missing fit score fields: {', '.join(missing)}"
        )

    normalized_fit = {
        key: bounded_score(fit_components[key], f"{company}/{role}/fit/{key}")
        for key in FIT_WEIGHTS
    }
    fit = 20 * sum(
        normalized_fit[key] * weight for key, weight in FIT_WEIGHTS.items()
    )

    hard_gate_failed = bool(job.get("hard_gate_failed", False))
    if hard_gate_failed:
        fit = min(fit, 49.0)

    quality_components = job.get("quality_scores")
    if not isinstance(quality_components, dict):
        raise ValueError(f"{company} / {role}: quality_scores must be an object")
    quality_basis = str(job.get("quality_basis", "wlb_first")).strip().lower()
    if quality_basis not in QUALITY_BASES:
        raise ValueError(
            f"{company} / {role}: quality_basis must be "
            "'wlb_first' or 'salary_growth_fallback'"
        )
    quality_weights = QUALITY_BASES[quality_basis]
    missing_quality = [
        key for key in quality_weights if key not in quality_components
    ]
    if missing_quality:
        raise ValueError(
            f"{company} / {role}: missing quality score fields: "
            f"{', '.join(missing_quality)}"
        )
    normalized_quality = {
        key: bounded_score(quality_components[key], f"{company}/{role}/quality/{key}")
        for key in quality_weights
    }
    raw_quality = 20 * sum(
        normalized_quality[key] * weight for key, weight in quality_weights.items()
    )
    quality_confidence = bounded_score(
        job.get("quality_confidence", 0),
        f"{company}/{role}/quality_confidence",
    )
    job_quality = 50 + (raw_quality - 50) * quality_confidence / 5
    severe_quality_risk = bool(job.get("severe_quality_risk", False))
    if severe_quality_risk:
        job_quality = min(job_quality, 49.0)

    opening = bounded_score(
        job.get("opening_confidence", 0), f"{company}/{role}/opening_confidence"
    )

    application_value = (
        0.45 * fit
        + 0.40 * job_quality
        + 0.15 * opening * 20
    )
    if hard_gate_failed:
        application_value = 0.0

    result = dict(job)
    result["fit_scores"] = normalized_fit
    result["quality_scores"] = normalized_quality
    result["quality_basis"] = quality_basis
    result["fit"] = round(fit, 1)
    result["fit_label"] = fit_label(fit)
    result["raw_job_quality"] = round(raw_quality, 1)
    result["job_quality"] = round(job_quality, 1)
    result["quality_label"] = quality_label(job_quality)
    result["application_value"] = round(application_value, 1)
    result["recommendation"] = recommendation(
        fit,
        job_quality,
        application_value,
        hard_gate_failed,
        severe_quality_risk,
    )
    return result


def load_jobs(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    jobs = payload.get("jobs") if isinstance(payload, dict) else None
    if not isinstance(jobs, list) or not jobs:
        raise ValueError("input must contain a non-empty 'jobs' array")
    if not all(isinstance(job, dict) for job in jobs):
        raise ValueError("every item in 'jobs' must be an object")
    return jobs


def render_markdown(jobs: list[dict[str, Any]]) -> str:
    lines = [
        "| Rank | Company | Role | Basis | Fit | Job quality | Application value | Recommendation |",
        "|---:|---|---|---|---:|---:|---:|---|",
    ]
    for index, job in enumerate(jobs, start=1):
        company = str(job["company"]).replace("|", "\\|")
        role = str(job["role"]).replace("|", "\\|")
        lines.append(
            f"| {index} | {company} | {role} | "
            f"{BASIS_LABELS.get(job['quality_basis'], job['quality_basis'])} | "
            f"{job['fit']:.1f} | {job['job_quality']:.1f} | "
            f"{job['application_value']:.1f} | {job['recommendation']} |"
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rank job-fit evidence using the bundled rubric."
    )
    parser.add_argument("input", type=Path, help="UTF-8 JSON file with a jobs array")
    parser.add_argument(
        "--format", choices=("markdown", "json"), default="markdown"
    )
    args = parser.parse_args()

    try:
        jobs = [score_job(job) for job in load_jobs(args.input)]
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    jobs.sort(key=lambda item: item["application_value"], reverse=True)
    if args.format == "json":
        print(json.dumps({"jobs": jobs}, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(jobs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
