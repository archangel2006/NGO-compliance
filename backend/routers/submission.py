from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
import shutil, os
from pathlib import Path

from backend.auth import get_current_user
from backend.store import (SUBMISSIONS, DOCUMENTS, new_id, now,
                            get_submission, get_documents_for_submission)

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
router     = APIRouter()


class SubmissionCreate(BaseModel):
    org_name:              str
    state:                 str     # maharashtra | delhi | karnataka | rajasthan
    entity_type:           str     # Public Trust | Society | Section 8 Company
    pan:                   str
    sector:                str
    contact_email:         str
    year_of_incorporation: int
    darpan_id:             Optional[str] = None


@router.post("")
def create_submission(body: SubmissionCreate,
                      user: dict = Depends(get_current_user)):
    sid = new_id()
    sub = {
        "id":                     sid,
        "org_name":               body.org_name,
        "state":                  body.state.lower(),
        "entity_type":            body.entity_type,
        "pan":                    body.pan.upper(),
        "sector":                 body.sector,
        "contact_email":          body.contact_email,
        "year_of_incorporation":  body.year_of_incorporation,
        "darpan_id":              body.darpan_id,
        "status":                 "pending",
        "submitted_by":           user["sub"],
        "created_at":             now(),
        "updated_at":             now(),
    }
    SUBMISSIONS[sid] = sub

    # Create upload folder for this submission
    (UPLOAD_DIR / sid).mkdir(parents=True, exist_ok=True)

    return {"id": sid, "status": "pending", "message": "Submission created."}


@router.get("/{submission_id}")
def get_submission_detail(submission_id: str,
                          user: dict = Depends(get_current_user)):
    sub  = get_submission(submission_id)
    if not sub:
        raise HTTPException(404, "Submission not found.")
    docs = get_documents_for_submission(submission_id)
    return {**sub, "documents": docs}


@router.post("/{submission_id}/documents")
def upload_document(
    submission_id: str,
    doc_type: str = Form(...),          # must match DOCUMENT_TEMPLATES keys
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    sub = get_submission(submission_id)
    if not sub:
        raise HTTPException(404, "Submission not found.")

    valid_types = [
        "trust_deed", "registration_certificate", "certificate_12a",
        "certificate_80g", "fcra_certificate", "annual_report",
        "audit_report", "pan_card",
    ]
    if doc_type not in valid_types:
        raise HTTPException(400, f"doc_type must be one of: {valid_types}")

    # Save file
    dest = UPLOAD_DIR / submission_id / f"{doc_type}_{file.filename}"
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    doc_id = new_id()
    DOCUMENTS[doc_id] = {
        "id":            doc_id,
        "submission_id": submission_id,
        "doc_type":      doc_type,
        "file_path":     str(dest),
        "file_name":     file.filename,
        "file_size":     dest.stat().st_size,
        "ocr_status":    "pending",
        "ocr_method":    None,
        "ocr_quality":   None,
        "uploaded_at":   now(),
    }
    return {
        "doc_id":  doc_id,
        "doc_type": doc_type,
        "status":  "uploaded",
        "path":    str(dest),
    }


@router.get("/{submission_id}/documents")
def list_documents(submission_id: str,
                   user: dict = Depends(get_current_user)):
    sub = get_submission(submission_id)
    if not sub:
        raise HTTPException(404, "Submission not found.")
    return get_documents_for_submission(submission_id)