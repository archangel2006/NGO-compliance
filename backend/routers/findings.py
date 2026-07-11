from fastapi import APIRouter, HTTPException, Depends
from backend.auth import get_current_user
from backend.store import (SUBMISSIONS, EXTRACTED,
                            get_submission, get_findings_for_submission)

router = APIRouter()


@router.get("/{submission_id}/findings")
def get_findings(submission_id: str,
                 user: dict = Depends(get_current_user)):
    sub = get_submission(submission_id)
    if not sub:
        raise HTTPException(404, "Submission not found.")
    if sub["status"] not in ("complete", "processing"):
        raise HTTPException(400, "Assessment not yet run.")

    findings  = get_findings_for_submission(submission_id)
    score     = sub.get("score", {})

    return {
        "submission_id":   submission_id,
        "org_name":        sub["org_name"],
        "state":           sub["state"],
        "entity_type":     sub["entity_type"],
        "overall_score":   score.get("overall_score"),
        "score_label":     score.get("label"),
        "grant_ready":     score.get("grant_ready"),
        "pass_count":      score.get("pass_count"),
        "fail_count":      score.get("fail_count"),
        "uncertain_count": score.get("uncertain_count"),
        "corpus_gap_count":score.get("corpus_gap_count"),
        "findings":        findings,
    }


@router.get("/{submission_id}/findings/{dimension_id}")
def get_single_finding(submission_id: str, dimension_id: str,
                       user: dict = Depends(get_current_user)):
    findings = get_findings_for_submission(submission_id)
    match    = next((f for f in findings
                     if f["dimension_id"] == dimension_id), None)
    if not match:
        raise HTTPException(404, f"Finding for dimension '{dimension_id}' not found.")
    return match


@router.get("/{submission_id}/extracted")
def get_extracted_fields(submission_id: str,
                         user: dict = Depends(get_current_user)):
    """Returns the raw extracted fields JSON — useful for debugging."""
    sub = get_submission(submission_id)
    if not sub:
        raise HTTPException(404, "Submission not found.")
    from backend.store import EXTRACTED
    extracted = EXTRACTED.get(submission_id)
    if not extracted:
        raise HTTPException(404, "No extraction data yet.")
    return extracted