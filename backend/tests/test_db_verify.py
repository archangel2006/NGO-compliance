"""
DB Verification Script — Checks 1, 2, 3
Run from the project root:  python backend/tests/test_db_verify.py
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

from backend.models.database import engine, SessionLocal, Base
import backend.models.orm  # registers all ORM classes with Base

from backend.models.orm import (
    Submission, UploadedDocument, ExtractedFields, ComplianceFinding, HumanReviewQueue
)
from sqlalchemy import inspect, text
import uuid, datetime

PASS = "[PASS]"
FAIL = "[FAIL]"
INFO = "[INFO]"

def sep(title):
    print(f"\n{'-'*60}")
    print(f"  {title}")
    print('-'*60)


# ── CHECK 1: Tables exist ─────────────────────────────────────────

sep("CHECK 1 — Connection & Schema Validation")

expected_tables = {
    "submissions",
    "uploaded_documents",
    "extracted_fields",
    "compliance_findings",
    "human_review_queue",
}

try:
    inspector = inspect(engine)
    actual_tables = set(inspector.get_table_names())
    print(f"{INFO} Tables found in database: {sorted(actual_tables)}\n")

    missing = expected_tables - actual_tables
    extra   = actual_tables - expected_tables

    if not missing:
        print(f"{PASS} All 5 required tables exist.")
    else:
        print(f"{FAIL} Missing tables: {missing}")

    if extra:
        print(f"{INFO} Extra tables (not managed by this app): {extra}")

    # Print column layout per table
    for tname in sorted(expected_tables & actual_tables):
        cols = [c["name"] for c in inspector.get_columns(tname)]
        print(f"  {tname}: {cols}")

except Exception as e:
    print(f"{FAIL} Cannot connect to database: {e}")
    sys.exit(1)


# ── CHECK 2: FK Cascade ───────────────────────────────────────────

sep("CHECK 2 — Transaction Integrity & FK Cascade")

db = SessionLocal()
test_sub_id = str(uuid.uuid4())

try:
    # Seed a submission
    sub = Submission(
        id=test_sub_id,
        org_name="Test Cascade NGO",
        state="dl",
        entity_type="Society",
        pan="TESTPAN001",
        sector="Education",
        contact_email="test@test.com",
        year_of_incorporation=2010,
        status="pending",
        created_at=datetime.datetime.utcnow().isoformat(),
        updated_at=datetime.datetime.utcnow().isoformat(),
    )
    db.add(sub)
    db.flush()

    # Seed an extracted_fields row
    ext = ExtractedFields(
        submission_id=test_sub_id,
        merged_fields={"registration_number": "TEST-123"},
        extraction_log=[],
        created_at=datetime.datetime.utcnow().isoformat(),
    )
    db.add(ext)

    # Seed a compliance finding
    fid = str(uuid.uuid4())
    finding = ComplianceFinding(
        id=fid,
        submission_id=test_sub_id,
        dimension_id="registration",
        dimension_name="Registration & Legal Status",
        status="PASS",
        confidence=0.90,
        legal_citation="Societies Registration Act 1860, s.1",
        ngo_evidence="reg no TEST-123",
        reasoning="Test reasoning.",
        routing="auto_report",
        citation_valid=True,
        created_at=datetime.datetime.utcnow().isoformat(),
    )
    db.add(finding)

    # Seed a queue item
    qid = str(uuid.uuid4())
    queue_item = HumanReviewQueue(
        id=qid,
        finding_id=fid,
        submission_id=test_sub_id,
        dimension_name="Registration & Legal Status",
        assigned_officer="officer@darpan.gov.in",
        queue_status="pending",
        ai_recommendation_revealed=False,
        created_at=datetime.datetime.utcnow().isoformat(),
    )
    db.add(queue_item)
    db.commit()
    print(f"{INFO} Seeded test submission {test_sub_id[:8]}... with finding + queue item.")

    # Now delete the submission — cascade should wipe everything
    db.delete(sub)
    db.commit()
    print(f"{INFO} Submission deleted. Checking cascade...")

    remaining_findings = db.query(ComplianceFinding).filter(ComplianceFinding.submission_id == test_sub_id).all()
    remaining_queue    = db.query(HumanReviewQueue).filter(HumanReviewQueue.submission_id == test_sub_id).all()
    remaining_ext      = db.query(ExtractedFields).filter(ExtractedFields.submission_id == test_sub_id).all()

    if not remaining_findings and not remaining_queue and not remaining_ext:
        print(f"{PASS} Cascade delete works — all child rows removed.")
    else:
        if remaining_findings:
            print(f"{FAIL} ComplianceFinding rows still exist: {len(remaining_findings)}")
        if remaining_queue:
            print(f"{FAIL} HumanReviewQueue rows still exist: {len(remaining_queue)}")
        if remaining_ext:
            print(f"{FAIL} ExtractedFields rows still exist: {len(remaining_ext)}")

except Exception as e:
    db.rollback()
    print(f"{FAIL} Cascade test error: {e}")
    # Cleanup in case partial commit
    try:
        leftover = db.query(Submission).filter(Submission.id == test_sub_id).first()
        if leftover:
            db.delete(leftover)
            db.commit()
    except Exception:
        pass
finally:
    db.close()


# ── CHECK 3: Row-count sanity (API contract smoke test) ───────────

sep("CHECK 3 — API Contract Smoke Test (via store wrappers)")

from backend.store import SUBMISSIONS, DOCUMENTS, FINDINGS, QUEUE, EXTRACTED, new_id, now

smoke_id = new_id()
try:
    SUBMISSIONS[smoke_id] = {
        "id": smoke_id,
        "org_name": "Smoke Test NGO",
        "state": "ka",
        "entity_type": "Public Trust",
        "pan": "SMKPAN001",
        "sector": "Health",
        "contact_email": "smoke@test.com",
        "year_of_incorporation": 2015,
        "status": "pending",
        "submitted_by": "officer@darpan.gov.in",
        "created_at": now(),
        "updated_at": now(),
    }

    # Simulate in-place status update (the pattern used in compliance.py)
    SUBMISSIONS[smoke_id]["status"] = "processing"

    fetched = SUBMISSIONS.get(smoke_id)
    assert fetched is not None, "Submission not found after insert"
    assert fetched["status"] == "processing", f"Status update not persisted: got {fetched['status']}"
    assert fetched["org_name"] == "Smoke Test NGO", "org_name mismatch"

    print(f"{PASS} INSERT via store wrapper works.")
    print(f"{PASS} In-place mutation (RowDict.__setitem__) persists to DB.")
    print(f"{PASS} GET via store wrapper returns correct data.")

    # Cleanup
    del SUBMISSIONS[smoke_id]
    assert SUBMISSIONS.get(smoke_id) is None, "Submission still exists after delete"
    print(f"{PASS} DELETE via store wrapper works.")

except AssertionError as e:
    print(f"{FAIL} Store wrapper assertion failed: {e}")
except Exception as e:
    print(f"{FAIL} Store wrapper error: {e}")
    try:
        del SUBMISSIONS[smoke_id]
    except Exception:
        pass

sep("All checks complete")
