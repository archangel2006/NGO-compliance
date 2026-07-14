# Triggers the full assessment pipeline for a submission.
# Runs synchronously for the pilot — in production use BackgroundTasks.

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from backend.auth import get_current_user
from backend.store import (
    SUBMISSIONS, DOCUMENTS, EXTRACTED, FINDINGS, QUEUE,
    new_id, now,
    get_submission, get_documents_for_submission,
)
from backend.services.ocr import extract_text
from backend.services.extraction import extract_all
from backend.services.rag import run_full_assessment
from backend.services.scoring import calculate_score

router = APIRouter()


def _run_assessment(submission_id: str):
    """
    Full pipeline for one submission.
    Runs asynchronously via BackgroundTasks.
    """
    import json
    from pathlib import Path

    sub  = get_submission(submission_id)
    docs = get_documents_for_submission(submission_id)

    if not sub:
        return
    if not docs:
        SUBMISSIONS[submission_id]["status"] = "error_no_documents"
        return

    SUBMISSIONS[submission_id]["status"] = "processing"
    SUBMISSIONS[submission_id]["progress_step"] = 1
    SUBMISSIONS[submission_id]["updated_at"] = now()

    state       = sub["state"]
    entity_type = sub["entity_type"]

    try:
        # ── STEP 1: OCR all uploaded documents ─────────────────────
        doc_inputs = []
        for doc in docs:
            SUBMISSIONS[submission_id]["progress_step"] = 2
            ocr_result = extract_text(doc["file_path"], state)

            if ocr_result.get("method") == "tesseract":
                SUBMISSIONS[submission_id]["progress_step"] = 3

            # Update OCR status in store
            DOCUMENTS[doc["id"]]["ocr_status"]  = "done"
            DOCUMENTS[doc["id"]]["ocr_method"]  = ocr_result["method"]
            DOCUMENTS[doc["id"]]["ocr_quality"] = ocr_result["quality"]

            doc_inputs.append({
                "path":     doc["file_path"],
                "doc_type": doc["doc_type"],
                "state":    state,
                "text":     ocr_result["text"],
            })

        # ── STEP 2: Structured extraction ──────────────────────────
        SUBMISSIONS[submission_id]["progress_step"] = 4
        merged = extract_all(doc_inputs)
        EXTRACTED[submission_id] = {
            "submission_id":   submission_id,
            "merged_fields":   merged,
            "extraction_log":  merged.pop("_log", []),
            "created_at":      now(),
        }

        # ── STEP 3: RAG + LLM per dimension ────────────────────────
        SUBMISSIONS[submission_id]["progress_step"] = 5
        findings = run_full_assessment(merged, state, entity_type)

        SUBMISSIONS[submission_id]["progress_step"] = 6
        for f in findings:
            fid = new_id()
            FINDINGS[fid] = {
                "id":             fid,
                "submission_id":  submission_id,
                "dimension_id":   f.dimension_id,
                "dimension_name": f.dimension_name,
                "status":         f.status,
                "confidence":     f.confidence,
                "legal_citation": f.legal_citation,
                "ngo_evidence":   f.ngo_evidence,
                "reasoning":      f.reasoning,
                "routing":        f.routing,
                "citation_valid": f.citation_valid,
                "raw_llm_output": f.raw_llm_output,
                "created_at":     now(),
            }

            # Route to human review queue if needed
            if f.routing == "human_review":
                SUBMISSIONS[submission_id]["progress_step"] = 7
                qid = new_id()
                QUEUE[qid] = {
                    "id":                          qid,
                    "finding_id":                  fid,
                    "submission_id":               submission_id,
                    "dimension_name":              f.dimension_name,
                    "assigned_officer":            "officer@darpan.gov.in",
                    "queue_status":                "pending",
                    "ai_recommendation_revealed":  False,
                    "officer_determination":       None,
                    "officer_notes":               None,
                    "reviewed_at":                 None,
                    "created_at":                  now(),
                }

        # ── STEP 4: Calculate score ─────────────────────────────────
        SUBMISSIONS[submission_id]["progress_step"] = 8
        score = calculate_score(findings)
        SUBMISSIONS[submission_id]["score"]      = score
        SUBMISSIONS[submission_id]["status"]     = "complete"
        SUBMISSIONS[submission_id]["updated_at"] = now()

        # Save findings array to assessment_results/{submission_id}.json
        results_dir = Path("assessment_results")
        results_dir.mkdir(parents=True, exist_ok=True)
        findings_list = [FINDINGS[fid] for fid in FINDINGS if FINDINGS[fid]["submission_id"] == submission_id]
        with open(results_dir / f"{submission_id}.json", "w") as f:
            json.dump({
                "submission_id": submission_id,
                "findings": findings_list,
                "score": score
            }, f, indent=2, default=str)

        print(f"[Assessment complete] {sub['org_name']} "
              f"→ score {score['overall_score']} / {score['label']}")

    except Exception as e:
        SUBMISSIONS[submission_id]["status"]     = "error"
        SUBMISSIONS[submission_id]["error"]      = str(e)
        SUBMISSIONS[submission_id]["updated_at"] = now()
        print(f"[Assessment ERROR] {submission_id}: {e}")
        raise


@router.post("/{submission_id}/assess")
def trigger_assessment(
    submission_id: str,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
):
    sub = get_submission(submission_id)
    if not sub:
        raise HTTPException(404, "Submission not found.")
    if sub["status"] == "processing":
        raise HTTPException(409, "Assessment already running.")
    if sub["status"] == "complete":
        raise HTTPException(409, "Assessment already complete. Create a new submission to re-assess.")

    docs = get_documents_for_submission(submission_id)
    if not docs:
        raise HTTPException(400, "No documents uploaded yet.")

    # Queue background task
    background_tasks.add_task(_run_assessment, submission_id)
    SUBMISSIONS[submission_id]["status"] = "processing"
    SUBMISSIONS[submission_id]["progress_step"] = 1

    return {
        "submission_id": submission_id,
        "status":        "processing",
        "message":       "Assessment started in background.",
    }


@router.get("/{submission_id}/status")
def get_assessment_status(submission_id: str,
                          user: dict = Depends(get_current_user)):
    """Polled by the frontend processing screen."""
    sub = get_submission(submission_id)
    if not sub:
        raise HTTPException(404, "Submission not found.")
    return {
        "submission_id":  submission_id,
        "status":         sub["status"],
        "progress_step":  sub.get("progress_step", 0),
        "score":          sub.get("score"),
        "error":          sub.get("error"),
    }