from dataclasses import dataclass
from typing import List

DIMENSION_WEIGHTS = {
    "registration": 0.20,
    "governance":   0.15,
    "membership":   0.10,
    "financial":    0.20,
    "tax":          0.15,
    "fcra":         0.10,
    "audit":        0.10,
}

STATUS_BASE_SCORES = {
    "PASS":       1.0,
    "FAIL":       0.0,
    "UNCERTAIN":  0.5,
    "CORPUS_GAP": 0.5,  # neutral — system limitation, not NGO failure
    "MISSING":    0.0,  # 0 points — required document not provided
}


def calculate_score(findings: list) -> dict:
    weighted_total = 0.0
    weight_sum     = 0.0
    breakdown      = {}

    for f in findings:
        weight      = DIMENSION_WEIGHTS.get(f.dimension_id, 0.10)
        base        = STATUS_BASE_SCORES.get(f.status, 0.0)
        confidence  = f.confidence

        # Confidence-adjusted: partial credit for uncertain PASS/FAIL
        # High confidence PASS  → 1.0 × weight
        # Low confidence PASS   → 0.75 × weight (less sure)
        # UNCERTAIN             → 0.5 × weight regardless of confidence
        # MISSING / CORPUS_GAP  → flat base score
        if f.status in ("PASS", "FAIL"):
            adjusted = base * confidence + 0.5 * (1 - confidence)
        else:
            adjusted = base  # UNCERTAIN/CORPUS_GAP/MISSING not confidence-adjusted

        weighted_total += adjusted * weight
        weight_sum     += weight

        breakdown[f.dimension_id] = {
            "name":           f.dimension_name,
            "status":         f.status,
            "confidence":     round(confidence, 2),
            "adjusted_score": round(adjusted, 2),
            "weight":         weight,
            "contribution":   round(adjusted * weight, 3),
        }

    overall = round((weighted_total / weight_sum) * 100) if weight_sum else 0

    return {
        "overall_score": overall,
        "label":         score_label(overall),
        "grant_ready":   overall >= 85,
        "breakdown":     breakdown,
        "pass_count":    sum(1 for f in findings if f.status == "PASS"),
        "fail_count":    sum(1 for f in findings if f.status == "FAIL"),
        "uncertain_count": sum(1 for f in findings if f.status == "UNCERTAIN"),
        "corpus_gap_count": sum(1 for f in findings if f.status == "CORPUS_GAP"),
        "missing_count": sum(1 for f in findings if f.status == "MISSING"),
    }


def score_label(score: int) -> str:
    if score >= 85: return "Compliant — Grant Ready"
    if score >= 70: return "Mostly Compliant — Minor Gaps"
    if score >= 50: return "Partial Compliance — Significant Gaps"
    return "Non-Compliant — Major Action Required"