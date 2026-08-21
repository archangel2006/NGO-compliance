from sqlalchemy import Column, String, Integer, Boolean, Float, ForeignKey
from backend.models.database import Base


# ── Core Relational Tables ────────────────────────────────────────

class Submission(Base):
    """NGO Submission record with flat relational compliance score columns."""
    __tablename__ = "submissions"
    id = Column(String, primary_key=True)
    org_name = Column(String, nullable=False)
    state = Column(String(5))
    entity_type = Column(String)
    pan = Column(String(10))
    sector = Column(String)
    contact_email = Column(String)
    year_of_incorporation = Column(Integer)
    darpan_id = Column(String, nullable=True)
    status = Column(String, default="pending")
    submitted_by = Column(String, nullable=True)
    progress_step = Column(Integer, default=0)
    
    # Flat Relational Score Columns
    overall_score = Column(Float, nullable=True)
    score_label = Column(String, nullable=True)
    grant_ready = Column(Boolean, nullable=True)
    pass_count = Column(Integer, default=0)
    fail_count = Column(Integer, default=0)
    uncertain_count = Column(Integer, default=0)
    corpus_gap_count = Column(Integer, default=0)

    error = Column(String, nullable=True)
    created_at = Column(String)
    updated_at = Column(String)


class UploadedDocument(Base):
    """File upload registry table."""
    __tablename__ = "uploaded_documents"
    id = Column(String, primary_key=True)
    submission_id = Column(String, ForeignKey("submissions.id", ondelete="CASCADE"))
    doc_type = Column(String)
    file_path = Column(String)
    file_name = Column(String, nullable=True)
    file_size = Column(Integer)
    ocr_status = Column(String)
    ocr_method = Column(String, nullable=True)
    ocr_quality = Column(String, nullable=True)
    uploaded_at = Column(String)


class ExtractedFields(Base):
    """Extraction metadata table."""
    __tablename__ = "extracted_fields"
    submission_id = Column(String, ForeignKey("submissions.id", ondelete="CASCADE"), primary_key=True)
    total_fields_extracted = Column(Integer, default=0)
    extraction_status = Column(String)
    created_at = Column(String)


class ComplianceFinding(Base):
    """Compliance assessment finding table per dimension."""
    __tablename__ = "compliance_findings"
    id = Column(String, primary_key=True)
    submission_id = Column(String, ForeignKey("submissions.id", ondelete="CASCADE"))
    dimension_id = Column(String)
    dimension_name = Column(String)
    status = Column(String)
    confidence = Column(Float)
    legal_citation = Column(String)
    ngo_evidence = Column(String)
    reasoning = Column(String)
    routing = Column(String)
    citation_valid = Column(Boolean)
    raw_llm_output = Column(String, nullable=True)
    matched_requirement = Column(String, default="")
    human_determination = Column(String, nullable=True)
    reviewed_by = Column(String, nullable=True)
    reviewed_at = Column(String, nullable=True)
    created_at = Column(String)


class HumanReviewQueue(Base):
    """Human review officer queue table."""
    __tablename__ = "human_review_queue"
    id = Column(String, primary_key=True)
    finding_id = Column(String, ForeignKey("compliance_findings.id", ondelete="CASCADE"))
    submission_id = Column(String, ForeignKey("submissions.id", ondelete="CASCADE"))
    dimension_name = Column(String)
    assigned_officer = Column(String)
    queue_status = Column(String)
    ai_recommendation_revealed = Column(Boolean, default=False)
    officer_determination = Column(String, nullable=True)
    officer_notes = Column(String, nullable=True)
    reviewed_by = Column(String, nullable=True)
    reviewed_at = Column(String, nullable=True)
    created_at = Column(String)


# ── Document-Specific Extraction Fact Tables (Flat Relational Columns) ────

class ExtractedTrustDeed(Base):
    """Extracted fields from Trust Deed / MOA."""
    __tablename__ = "extracted_trust_deeds"
    submission_id = Column(String, ForeignKey("submissions.id", ondelete="CASCADE"), primary_key=True)
    org_name = Column(String)
    reg_date = Column(String)
    objectives_clause = Column(String)
    quorum = Column(String)
    amendment_clause = Column(String)
    org_address = Column(String)
    trustee_count = Column(Integer)
    trustee_names = Column(String)       # Comma-separated text list
    office_bearers = Column(String)      # Comma-separated text list
    non_profit_clause_present = Column(Boolean)
    dissolution_clause_present = Column(Boolean)


class ExtractedRegistrationCertificate(Base):
    """Extracted fields from Registration Certificate."""
    __tablename__ = "extracted_registration_certificates"
    submission_id = Column(String, ForeignKey("submissions.id", ondelete="CASCADE"), primary_key=True)
    registration_number = Column(String)
    registering_authority = Column(String)
    date_of_registration = Column(String)
    act_registered_under = Column(String)
    state_of_registration = Column(String)


class Extracted12ACertificate(Base):
    """Extracted fields from Income Tax 12A / 12AB Certificate."""
    __tablename__ = "extracted_12a_certificates"
    submission_id = Column(String, ForeignKey("submissions.id", ondelete="CASCADE"), primary_key=True)
    cert_12a_number = Column(String)
    pan = Column(String(10))
    valid_from = Column(String)
    valid_until = Column(String)
    form_ref = Column(String)
    provisional_flag = Column(Boolean, default=False)


class Extracted80GCertificate(Base):
    """Extracted fields from Income Tax 80G Certificate."""
    __tablename__ = "extracted_80g_certificates"
    submission_id = Column(String, ForeignKey("submissions.id", ondelete="CASCADE"), primary_key=True)
    cert_80g_number = Column(String)
    pan = Column(String(10))
    valid_until = Column(String)
    deduction_rate = Column(String)


class ExtractedFCRACertificate(Base):
    """Extracted fields from FCRA Registration Certificate."""
    __tablename__ = "extracted_fcra_certificates"
    submission_id = Column(String, ForeignKey("submissions.id", ondelete="CASCADE"), primary_key=True)
    fcra_reg_number = Column(String)
    valid_until = Column(String)
    bank_account = Column(String)
    bank_name = Column(String)
    bank_branch = Column(String)
    sbi_designated_account = Column(Boolean, default=False)


class ExtractedAnnualReport(Base):
    """Extracted fields from Annual Report."""
    __tablename__ = "extracted_annual_reports"
    submission_id = Column(String, ForeignKey("submissions.id", ondelete="CASCADE"), primary_key=True)
    financial_year = Column(String)
    total_receipts = Column(Float)
    total_expenditure = Column(Float)
    csr_grant_present = Column(Boolean, default=False)
    govt_grant_present = Column(Boolean, default=False)
    fund_utilisation_present = Column(Boolean, default=False)
    grant_sources = Column(String)      # Comma-separated text list


class ExtractedAuditReport(Base):
    """Extracted fields from CA Audit Report."""
    __tablename__ = "extracted_audit_reports"
    submission_id = Column(String, ForeignKey("submissions.id", ondelete="CASCADE"), primary_key=True)
    auditor_name = Column(String)
    auditor_icai = Column(String)
    audit_period = Column(String)
    fcra_audit_present = Column(Boolean, default=False)


class ExtractedPanCard(Base):
    """Extracted fields from PAN Card."""
    __tablename__ = "extracted_pan_cards"
    submission_id = Column(String, ForeignKey("submissions.id", ondelete="CASCADE"), primary_key=True)
    pan = Column(String(10))
    org_name_pan = Column(String)
