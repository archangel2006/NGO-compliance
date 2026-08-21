from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from backend.auth import require_officer
from backend.store import QUEUE, FINDINGS, SUBMISSIONS, now

router = APIRouter()


@router.get("")
def get_queue(user: dict = Depends(require_officer)):
    """All pending and in-review queue items."""
    items = []
    for item in QUEUE.values():
        finding = FINDINGS.get(item["finding_id"], {})
        items.append({
            **item,
            "confidence": finding.get("confidence", 0.50),
            "legal_citation": finding.get("legal_citation", ""),
            "ngo_evidence": finding.get("ngo_evidence", ""),
            "status": finding.get("status", "UNCERTAIN"),
        })
    items.sort(key=lambda x: x["created_at"])
    return {
        "total":   len(items),
        "pending": sum(1 for i in items if i["queue_status"] == "pending"),
        "items":   items,
    }


@router.get("/{queue_id}")
def get_queue_item(queue_id: str, user: dict = Depends(require_officer)):
    """
    Returns queue item with BLINDED finding data.
    AI recommendation is hidden until officer calls /reveal.
    """
    item = QUEUE.get(queue_id)
    if not item:
        raise HTTPException(404, "Queue item not found.")

    finding = FINDINGS.get(item["finding_id"], {})
    sub     = SUBMISSIONS.get(item["submission_id"], {})

    response = {
        **item,
        "submission": {
            "org_name":    sub.get("org_name"),
            "state":       sub.get("state"),
            "entity_type": sub.get("entity_type"),
        },
        "legal_citation": finding.get("legal_citation"),
        "ngo_evidence":   finding.get("ngo_evidence"),
        "dimension_name": finding.get("dimension_name"),
    }

    # Hide AI verdict until revealed
    if not item["ai_recommendation_revealed"]:
        response["ai_status"]     = "HIDDEN"
        response["ai_confidence"] = None
        response["ai_reasoning"]  = "Reveal AI recommendation after forming your own judgment."
    else:
        response["ai_status"]     = finding.get("status")
        response["ai_confidence"] = finding.get("confidence")
        response["ai_reasoning"]  = finding.get("reasoning")

    return response


@router.post("/{queue_id}/reveal")
def reveal_ai_recommendation(queue_id: str,
                              user: dict = Depends(require_officer)):
    """Officer explicitly reveals AI verdict after their own review."""
    item = QUEUE.get(queue_id)
    if not item:
        raise HTTPException(404, "Queue item not found.")
    if item["queue_status"] == "reviewed":
        raise HTTPException(400, "Already reviewed.")

    QUEUE[queue_id]["ai_recommendation_revealed"] = True
    QUEUE[queue_id]["queue_status"] = "in_review"

    finding = FINDINGS.get(item["finding_id"], {})
    return {
        "revealed":     True,
        "ai_status":     finding.get("status"),
        "ai_confidence": finding.get("confidence"),
        "ai_reasoning":  finding.get("reasoning"),
    }


class DeterminationRequest(BaseModel):
    determination: str           # PASS | FAIL
    notes:         Optional[str] = None


@router.post("/{queue_id}/determine")
def submit_determination(queue_id: str, body: DeterminationRequest,
                         user: dict = Depends(require_officer)):
    item = QUEUE.get(queue_id)
    if not item:
        raise HTTPException(404, "Queue item not found.")
    if item["queue_status"] == "reviewed":
        raise HTTPException(400, "Already reviewed.")
    if body.determination not in ("PASS", "FAIL"):
        raise HTTPException(400, "determination must be PASS or FAIL.")

    QUEUE[queue_id]["queue_status"]          = "reviewed"
    QUEUE[queue_id]["officer_determination"] = body.determination
    QUEUE[queue_id]["officer_notes"]         = body.notes
    QUEUE[queue_id]["reviewed_by"]           = user["name"]
    QUEUE[queue_id]["reviewed_at"]           = now()

    # Update the finding's effective status for the report
    FINDINGS[item["finding_id"]]["human_determination"] = body.determination
    FINDINGS[item["finding_id"]]["reviewed_by"]         = user["name"]
    FINDINGS[item["finding_id"]]["reviewed_at"]         = now()

    return {
        "queue_id":      queue_id,
        "status":        "reviewed",
        "determination": body.determination,
        "reviewed_by":   user["name"],
    }