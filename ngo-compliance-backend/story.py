# In-memory store — all data lives here until Phase 5 (PostgreSQL).
# Every router imports from here.
# Swap this out for DB calls without touching router logic.

from datetime import datetime
import uuid

def new_id():
    return str(uuid.uuid4())

def now():
    return datetime.utcnow().isoformat()


# ── Submissions ───────────────────────────────────────────────────
# {submission_id: {id, org_name, state, entity_type, pan, sector,
#                  contact_email, year_of_incorporation, darpan_id,
#                  status, created_at, updated_at}}
SUBMISSIONS: dict = {}


# ── Uploaded documents ────────────────────────────────────────────
# {doc_id: {id, submission_id, doc_type, file_path, file_size,
#            ocr_status, ocr_method, ocr_quality, uploaded_at}}
DOCUMENTS: dict = {}


# ── Extracted fields ──────────────────────────────────────────────
# {submission_id: {merged_fields: {...}, extraction_log: [...]}}
EXTRACTED: dict = {}


# ── Compliance findings ───────────────────────────────────────────
# {finding_id: {id, submission_id, dimension_id, dimension_name,
#               status, confidence, legal_citation, ngo_evidence,
#               reasoning, routing, citation_valid, raw_llm_output,
#               created_at}}
FINDINGS: dict = {}


# ── Human review queue ────────────────────────────────────────────
# {queue_id: {id, finding_id, submission_id, assigned_officer,
#             queue_status, ai_recommendation_revealed,
#             officer_determination, officer_notes, reviewed_at,
#             created_at}}
QUEUE: dict = {}


# ── Final reports ─────────────────────────────────────────────────
# {submission_id: {id, submission_id, overall_score, score_label,
#                  grant_ready, pass_count, fail_count,
#                  uncertain_count, corpus_gap_count,
#                  report_path, generated_at}}
REPORTS: dict = {}


# ── Helpers ───────────────────────────────────────────────────────

def get_submission(submission_id: str) -> dict:
    sub = SUBMISSIONS.get(submission_id)
    if not sub:
        return None
    return sub

def get_documents_for_submission(submission_id: str) -> list:
    return [d for d in DOCUMENTS.values() if d["submission_id"] == submission_id]

def get_findings_for_submission(submission_id: str) -> list:
    return [f for f in FINDINGS.values() if f["submission_id"] == submission_id]

def get_queue_for_submission(submission_id: str) -> list:
    return [q for q in QUEUE.values() if q["submission_id"] == submission_id]