# AGENTS.md — NGO Compliance Verification System
# Internship Project · NITI Aayog NIC Informatics Division · Pilot

This file is the authoritative reference for any AI agent assisting with this
project. Read this fully before writing or modifying any code.

---

## 1. WHAT THIS PROJECT IS

An AI-assisted document compliance verification system for NGOs registered in
India. It sits as a proposed module for the NGO Darpan platform (ngodarpan.gov.in).

The core problem it solves: NGO Darpan currently issues Darpan IDs based on
self-declared affidavits only. No document is cross-checked against the actual
state law that governs the NGO. This system provides that missing verification
layer.

**What it is:** A decision-support tool that produces evidence-backed compliance
reports with legal citations, NGO document evidence, and AI reasoning per
dimension. It is NOT an automated ruling system. Uncertain findings always route
to a human compliance officer before reaching the final report.

**Pilot scope:** 4 states — Maharashtra, Delhi, Karnataka, Rajasthan.
Central regulations (FCRA, Income Tax Act 12A/80G) apply to all states always.

---

## 2. SYSTEM ARCHITECTURE — THREE LAYERS

```
LAYER 1 — KNOWLEDGE (Legal Corpus)
  State Acts + Central regulations (FCRA, IT Act, Darpan guidelines)
  → Chunked by section boundary
  → Embedded via nomic-embed-text (Ollama)
  → Stored in ChromaDB (local persistent vector store)
  → Updated by re-ingesting documents — NO code changes on law updates

LAYER 2 — FRAMEWORK (Compliance Dimensions)
  7 stable dimensions stored in PostgreSQL as data (not hardcoded in logic)
  → Registration & Legal Status   (weight 0.20)
  → Governance Structure          (weight 0.15)
  → Membership Requirements       (weight 0.10)
  → Financial Compliance          (weight 0.20)
  → Tax Compliance (12A / 80G)    (weight 0.15)
  → FCRA Compliance               (weight 0.10)
  → Audit Requirements            (weight 0.10)
  State-specific requirements are NOT hardcoded — retrieved from Layer 1 at runtime

LAYER 3 — ASSESSMENT (Pipeline)
  Document Upload
      → PyMuPDF direct extraction (digital PDFs)
      → OpenCV preprocessing + Tesseract fallback (scanned docs)
      → Structured field extraction (regex + spaCy NER + doc templates)
      → Per-dimension RAG + LLM (ChromaDB retrieval + Ollama Mistral 7B)
      → Citation validation (check citation exists in corpus)
      → Confidence routing:
            >= 0.85 confidence + valid citation → auto report
            UNCERTAIN / low confidence / failed citation → Human Review Queue
            No corpus results → Corpus Gap Alert
      → Human Review Queue (blinded review — officer sees evidence before AI verdict)
      → Final Compliance Report (AI-assessed + human-reviewed, cited PDF)
```

---

## 3. CRITICAL DESIGN DECISIONS

Read these before making any architectural choices.

### 3.1 No External APIs
Everything runs locally. OCR (Tesseract), embeddings (nomic-embed-text via
Ollama), LLM (Mistral 7B via Ollama), vector store (ChromaDB), database
(PostgreSQL). No data leaves the server. This is a hard requirement for a
government system handling sensitive NGO documents.

### 3.2 No Rule-Based Compliance Engine
State-specific legal requirements are NOT encoded as application logic. The
system retrieves actual law text from ChromaDB and reasons over it with the LLM.
When a law changes, you update a PDF in the corpus folder and re-run ingestion.
No code changes required.

### 3.3 Not Agentic
The outer pipeline structure is deterministic — all 7 dimensions are always
checked, always in the same way, producing auditable traceable output. LLM
intelligence is bounded within each dimension assessment, not allowed to control
the pipeline structure. This is intentional for legal auditability.

### 3.4 Human Review Queue is Mandatory Architecture
The system never produces a final report on uncertain findings without human
officer review. Officers review with blinded protocol — they see legal provisions
and NGO evidence BEFORE seeing the AI recommendation. This prevents anchoring
bias and makes findings legally defensible.

### 3.5 Citation Validation Before Publishing
Every legal citation from the LLM is cross-checked against ChromaDB before it
reaches any report. If a citation cannot be verified in the corpus, the finding
is downgraded to UNCERTAIN and routed to human review. This prevents hallucinated
legal citations from appearing in official reports.

### 3.6 Corpus Gap is Not a Failure
When ChromaDB returns no results for a dimension query, the finding is marked
CORPUS_GAP (not FAIL). Score contribution is 0.5 (neutral — system limitation,
not NGO failure). The report clearly labels it "Assessment pending — corpus
incomplete" and routes to a Corpus Alert queue for admin attention.

### 3.7 JSONB for Extracted Fields
Extracted NGO document fields are stored as PostgreSQL JSONB. Different document
types produce different fields. Fixed columns cannot work here. JSONB allows
querying without a rigid schema.

---

## 4. TECH STACK

```
Frontend    Next.js 14 (App Router) + Tailwind CSS
Backend     FastAPI (Python 3.10+)
Database    PostgreSQL (JSONB for extracted fields)
OCR         PyMuPDF (digital PDFs) + OpenCV preprocessing + Tesseract (scanned)
NLP         spaCy (en_core_web_sm) for NER
Vector DB   ChromaDB (local persistent, cosine similarity)
Embeddings  nomic-embed-text via Ollama (768-dim, 8192 token context)
LLM         Ollama running Mistral 7B (temperature 0.1 for legal reasoning)
Reports     WeasyPrint (HTML/CSS to PDF)
Auth        JWT (hardcoded pilot users, no signup, no user DB table)
```

---

## 5. FOLDER STRUCTURE

```
ngo-compliance/
  frontend/                        Next.js app (already built as prototype)
  backend/
    main.py                        FastAPI entry point
    auth.py                        JWT login (hardcoded pilot users)
    .env                           Environment variables
    requirements.txt
    routers/
      __init__.py
      submissions.py               POST /submissions, GET /submissions/{id}
      compliance.py                POST /submissions/{id}/assess
      findings.py                  GET /submissions/{id}/findings
      queue.py                     GET /queue, POST /queue/{id}/determine
      reports.py                   GET /submissions/{id}/report
      auth.py                      POST /auth/login
    services/
      __init__.py
      preprocessing.py             OpenCV: deskew, denoise, binarize
      ocr.py                       PyMuPDF + Tesseract fallback
      document_templates.py        Field patterns per document type
      extraction.py                Regex + spaCy NER → structured JSON
      ingest.py                    PDF → chunks → embeddings → ChromaDB
      rag.py                       Retrieval + LLM assessment + routing
      scoring.py                   Weighted confidence-adjusted score
    models/
      __init__.py
      database.py                  SQLAlchemy engine + Base
      schemas.py                   Pydantic models for API I/O
      orm.py                       SQLAlchemy ORM models
    utils/
      __init__.py
      chunker.py                   Section-boundary text splitting
  corpus/
    corpus_config.py               One entry per PDF (only manual file)
    central/
      fcra/
      income_tax/
      darpan/
      societies/
    maharashtra/
    delhi/
    karnataka/
    rajasthan/
  corpus_metadata/                 Auto-generated JSON per PDF
  vectorstore/                     ChromaDB persistent storage (auto)
  uploads/
    {submission_id}/               NGO uploaded documents per submission
  reports/                         Generated PDF compliance reports
  backend/tests/
    test_pdfs.py                   Phase 1 verification
    test_retrieval.py              Phase 2 verification
    test_extraction.py             Phase 3 verification
    test_assessment.py             Phase 4 verification
  AGENTS.md                        This file
  docker-compose.yml
```

---

## 6. DATABASE — 8 TABLES

PostgreSQL. All tables use UUID primary keys. JSONB for variable field sets.

```
submissions
  id, darpan_id (nullable), org_name, state, entity_type, pan, sector,
  contact_email, year_of_incorporation, status, created_at, updated_at

uploaded_documents
  id, submission_id (FK), doc_type, file_path, file_size, ocr_status,
  ocr_method, ocr_quality, uploaded_at

extracted_fields
  id, submission_id (FK), merged_fields (JSONB), extraction_log (JSONB),
  created_at

compliance_dimensions
  id, dimension_id (unique string), name, description, retrieval_query_template,
  evidence_fields (JSONB array), weight, applicable_entity_types (JSONB array),
  is_active

compliance_findings
  id, submission_id (FK), dimension_id (FK), status, confidence,
  legal_citation, ngo_evidence, reasoning, routing, citation_valid,
  raw_llm_output, created_at

human_review_queue
  id, finding_id (FK), submission_id (FK), assigned_officer, queue_status,
  ai_recommendation_revealed (bool), officer_determination, officer_notes,
  reviewed_at, created_at

compliance_reports
  id, submission_id (FK), overall_score, score_label, grant_ready (bool),
  pass_count, fail_count, uncertain_count, corpus_gap_count,
  report_path, version, generated_at

corpus_metadata
  id, rel_path (unique), act_name, jurisdiction, applicable_states (JSONB),
  source_url, ingested (bool), ingested_date, total_chunks, new_chunks
```

---

## 7. API ENDPOINTS

```
POST   /auth/login                         email + password → JWT token
POST   /submissions                        create new submission
GET    /submissions/{id}                   get submission status + basic info
POST   /submissions/{id}/documents         upload a document file
POST   /submissions/{id}/assess            trigger full compliance assessment
GET    /submissions/{id}/findings          all 7 dimension findings
GET    /submissions/{id}/report            full compliance report JSON
GET    /submissions/{id}/report/pdf        download PDF report

GET    /queue                              all pending human review items
GET    /queue/{id}                         single queue item (blinded)
POST   /queue/{id}/reveal                  reveal AI recommendation to officer
POST   /queue/{id}/determine               officer submits PASS/FAIL + notes

GET    /corpus/coverage/{state}            check corpus coverage for state
POST   /corpus/ingest                      trigger re-ingestion (admin only)
GET    /corpus/status                      all corpus metadata
```

---

## 8. COMPLIANCE DIMENSIONS — FULL SPEC

Each dimension has a fixed weight, retrieval query template, and evidence fields.
These are seeded into the compliance_dimensions table on startup.

```
dimension_id: registration
name: Registration & Legal Status
weight: 0.20
query: "NGO registration requirements valid registration certificate {entity_type} {state}"
evidence_fields: [registration_number, registering_authority, act_registered_under,
                  date_of_registration]
note: Maharashtra — must check dual registration (BPT Act + Societies Act)

dimension_id: governance
name: Governance Structure
weight: 0.15
query: "board of trustees governing body composition quorum {entity_type} {state}"
evidence_fields: [trustee_names, office_bearers, governing_body_size, quorum_clause]

dimension_id: membership
name: Membership Requirements
weight: 0.10
query: "minimum number of members trustees {entity_type} {state} registration"
evidence_fields: [member_count, trustee_count, member_names]
note: Rajasthan requires 10 members. Most states require 7 (Societies Act 1860).

dimension_id: financial
name: Financial Compliance
weight: 0.20
query: "fund utilisation statement accounts grants receipts {state}"
evidence_fields: [annual_report_year, csr_grants, govt_grants, fund_utilisation_present]
note: CSR and government grants require mandatory fund utilisation statements.

dimension_id: tax
name: Tax Compliance (12A / 80G)
weight: 0.15
query: "12A 12AB 80G income tax exemption certificate charitable organisation"
evidence_fields: [cert_12a_number, cert_12a_expiry, cert_80g_number, cert_80g_expiry, pan]
note: Since 2021 these certificates require renewal (12AB). Check expiry dates.

dimension_id: fcra
name: FCRA Compliance
weight: 0.10
query: "FCRA registration foreign contribution designated bank account annual return FC-4"
evidence_fields: [fcra_reg_number, fcra_expiry, fcra_bank_account, fc4_filed]
note: ONLY assess if NGO has declared foreign funding. SBI New Delhi Main Branch
      is mandatory for designated FCRA account since 2020 amendment.

dimension_id: audit
name: Audit Requirements
weight: 0.10
query: "audited financial statements chartered accountant FCRA Rule 17 separate audit"
evidence_fields: [auditor_name, auditor_icai, audit_period, fcra_audit_present]
note: FCRA-receiving NGOs need a SEPARATE audit under FCRA Rule 17 in addition
      to the general annual audit. Most common cause of UNCERTAIN findings.
```

---

## 9. DOCUMENT TYPES AND WHAT IS EXTRACTED

```
trust_deed / moa
  → org_name, reg_date, non_profit_clause_present, objectives_clause,
    quorum, trustee_names (NER), trustee_count, dissolution_clause_present
  → feeds: registration, governance, membership

registration_certificate
  → registration_number, registering_authority, date_of_registration,
    act_registered_under, state_of_registration
  → feeds: registration

certificate_12a
  → cert_12a_number, pan, valid_from, valid_until, form_ref (10A or 10AB),
    provisional_flag
  → feeds: tax

certificate_80g
  → cert_80g_number, pan, valid_until, deduction_rate
  → feeds: tax

fcra_certificate
  → fcra_reg_number, valid_until, bank_account, bank_name, bank_branch,
    sbi_designated_account (bool)
  → feeds: fcra

annual_report
  → financial_year, total_receipts, total_expenditure,
    csr_grant_present (bool), govt_grant_present (bool),
    fund_utilisation_present (bool), grant_sources (NER)
  → feeds: financial

audit_report
  → auditor_name, auditor_icai, audit_period, balance_sheet,
    fcra_audit_present (bool)
  → feeds: audit

pan_card
  → pan, org_name_pan
  → feeds: tax, fcra (PAN cross-reference)
```

---

## 10. LEGAL CORPUS — PDF SOURCES

All PDFs are downloaded manually once from official government sites.
The corpus_config.py file maps each PDF path to 5 metadata fields.
The ingest.py script reads the PDFs, chunks them, embeds them, and stores in
ChromaDB. Re-running ingest.py is safe (idempotent — already-ingested chunks
are skipped by chunk ID).

```
CENTRAL (applies to all states)
  corpus/central/fcra/FCRA_Act_2010.pdf
    source: fcraonline.nic.in/home/PDF_Doc/FC-RegulationAct-2010-C.pdf
  corpus/central/fcra/FCRA_Amendment_2020.pdf
    source: fcraonline.nic.in/home/PDF_Doc/fc_amend_07102020_1.pdf
  corpus/central/fcra/FCRA_Rules_2011.pdf
    source: fcraonline.nic.in
  corpus/central/income_tax/IT_Act_Sec_11_12.pdf
    source: incometaxindia.gov.in
  corpus/central/income_tax/IT_Act_Sec_12A_12AB.pdf
    source: incometaxindia.gov.in
  corpus/central/income_tax/IT_Act_Sec_80G.pdf
    source: incometaxindia.gov.in
  corpus/central/darpan/NGO_Darpan_Guidelines.pdf
    source: ngodarpan.gov.in
  corpus/central/societies/SRA_1860.pdf
    source: indiacode.nic.in/bitstream/123456789/14647/1/india_societies_registration_act.pdf

MAHARASHTRA
  corpus/maharashtra/BPT_Act_1950.pdf
    source: charity.maharashtra.gov.in/Portals/0/Files/B.P.T.Act,1950.pdf
  corpus/maharashtra/BPT_Rules_1951.pdf
    source: charity.maharashtra.gov.in/Portals/0/Files/B.P.T.Rules,1951.pdf
  corpus/maharashtra/SRA_1860_Maharashtra.pdf
    source: charity.maharashtra.gov.in/Portals/0/Files/S.R.Act1860.pdf

DELHI
  corpus/delhi/SRA_1860_Delhi.pdf
    source: indiacode.nic.in/bitstream/123456789/20573/1/aa1860-21.pdf

KARNATAKA
  corpus/karnataka/KSA_1960.pdf
    source: dpal.karnataka.gov.in/storage/pdf-files/acts alpha and dept wise acts/17 of 1960 (E).pdf
  corpus/karnataka/KSA_Rules_1961.pdf
    source: dpal.karnataka.gov.in

RAJASTHAN
  corpus/rajasthan/RSA_1958.pdf
    source: indiacode.nic.in/bitstream/123456789/18835/1/the_rajasthan_societies_registration_act,_1958_with_foot_note.pdf
```

---

## 11. SCORING ALGORITHM

```python
STATUS_BASE_SCORES = {
    PASS:        1.0,
    FAIL:        0.0,
    UNCERTAIN:   0.5,
    CORPUS_GAP:  0.5   # neutral — system limitation, not NGO failure
}

For PASS or FAIL:
    adjusted = base_score * confidence + 0.5 * (1 - confidence)
    # High confidence PASS (0.95) → 0.975 contribution
    # Low confidence PASS (0.60) → 0.800 contribution (partial credit for doubt)

For UNCERTAIN or CORPUS_GAP:
    adjusted = 0.5  # flat, confidence does not adjust these

overall_score = sum(adjusted * weight for each dimension) / sum(weights) * 100

Score labels:
    >= 85  Compliant — Grant Ready
    >= 70  Mostly Compliant — Minor Gaps
    >= 50  Partial Compliance — Significant Gaps
    <  50  Non-Compliant — Major Action Required
```

---

## 12. USER FLOW

```
OFFICER / NGO ARRIVES AT PLATFORM

Step 1 — Select State (card selection)
  Maharashtra / Delhi / Karnataka / Rajasthan
  Note: Central regulations (FCRA, IT Act) always included regardless

Step 2 — Enter NGO Details
  Org name, entity type, PAN, year of incorporation, sector, contact email
  (Darpan ID optional — if provided, details auto-fetch from Darpan lookup)

Step 3 — Upload Documents
  Trust Deed / MOA, Registration Certificate, 12A, 80G, FCRA, Annual Report,
  Audit Report, PAN Card (upload what you have — missing docs are flagged)

Step 4 — Processing Screen (live pipeline simulation)
  Receives documents → OCR → extraction → RAG + LLM × 7 → routing → complete

Step 5 — Compliance Dashboard
  Overall score ring, 7 dimension cards with PASS/FAIL/UNCERTAIN badges,
  confidence bars, auto vs pending-review labels

Step 6 — Detailed Findings
  Per dimension: legal citation, NGO evidence, AI reasoning, how-to-fix (FAIL)
  Filter by status. Filterable. Expandable cards.

Step 7 — Human Review Queue (officer-facing)
  Blinded review: evidence shown first, AI verdict hidden until officer submits
  Officer marks PASS / FAIL / Escalate / Request More Docs + notes
  Audit trail: officer ID + timestamp on every determination

Step 8 — Final Compliance Report
  AI-assessed findings + Officer-reviewed findings (clearly labelled separately)
  Overall score, summary table, recommended actions, disclaimer
  Download as PDF
```

---

## 13. AUTHENTICATION

Pilot uses hardcoded users. No signup. No user database table.
JWT tokens, 8-hour expiry.

```python
PILOT_USERS = {
    "officer@darpan.gov.in": {
        "password": "pilot2025",
        "name": "Officer Ramesh Kumar",
        "role": "compliance_officer"
    },
    "admin@darpan.gov.in": {
        "password": "admin2025",
        "name": "Admin",
        "role": "admin"
    }
}
```

Roles:
  compliance_officer — view submissions, access queue, submit determinations,
                       view reports
  admin — all of above + corpus management, system health

In production: integrate with NIC SSO or Darpan portal identity system.
The role-based access model is already in place.

---

## 14. LLM PROMPT CONTRACT

Every dimension assessment sends this structure to Mistral 7B (temperature 0.1):

```
System context: legal compliance officer reviewing Indian NGO documents
Legal provisions: top-5 ChromaDB chunks for the dimension query
NGO evidence: extracted fields relevant to this dimension
Task: assess PASS / FAIL / UNCERTAIN with reasoning

Required output — ONLY valid JSON, no other text:
{
  "status": "PASS" | "FAIL" | "UNCERTAIN",
  "confidence": 0.0–1.0,
  "legal_citation": "exact act name and section",
  "ngo_evidence": "specific extracted field or text used",
  "reasoning": "2-3 sentences maximum"
}
```

After receiving LLM output:
1. Parse JSON (handle markdown code fences)
2. Validate citation exists in ChromaDB corpus
3. If citation invalid → downgrade to UNCERTAIN, cap confidence at 0.5
4. Route based on status + confidence + citation_valid

---

## 15. ENVIRONMENT SETUP COMMANDS

```bash
# Clone and enter project
git clone <repo>
cd ngo-compliance

# Backend Python environment
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Ollama models
ollama pull mistral
ollama pull nomic-embed-text

# PostgreSQL — create database
psql -U postgres
CREATE DATABASE ngo_compliance;
\q

# Run backend
uvicorn main:app --reload --port 8000

# Frontend
cd ../frontend
npm install
npm run dev                        # runs on localhost:3000
```

---

## 16. PHASE-BY-PHASE BREAKDOWN WITH STATUS

---

### PHASE 0 — Project Setup

```
[✓] requirements.txt written
[✓] .env template written
[ ] git repo initialized
[ ] Python virtual environment created
[ ] npm install run in frontend
[ ] ollama pull mistral
[ ] ollama pull nomic-embed-text
[ ] PostgreSQL database created
[ ] .env filled with local values
```

Commands:
```bash
git init
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
ollama pull mistral
ollama pull nomic-embed-text
psql -U postgres -c "CREATE DATABASE ngo_compliance;"
cd ../frontend && npm install
```

No tests for Phase 0. Success = both servers start without errors.

---

### PHASE 1 — Legal Corpus Collection

```
[✓] corpus_config.py written (all 17 PDF entries + REQUIRED_CORPUS map)
[ ] corpus/ folder structure created
[ ] All central PDFs downloaded (8 files)
[ ] Maharashtra PDFs downloaded (3 files)
[ ] Delhi PDFs downloaded (1 file)
[ ] Karnataka PDFs downloaded (2 files)
[ ] Rajasthan PDFs downloaded (1 file)
```

Phase 1 is manual download work only. See Section 10 for all URLs.

Phase 1 Test:
```bash
python backend/tests/test_pdfs.py
```
Expected output: all PDFs show OK or WARN. No MISSING or ERROR lines.
If MISSING lines appear, download those PDFs before proceeding to Phase 2.

---

### PHASE 2 — Corpus Ingestion Pipeline

```
[✓] backend/utils/chunker.py written
[✓] backend/services/ingest.py written
[ ] Ingestion run on all downloaded PDFs
[ ] ChromaDB retrieval test passed
```

Run ingestion:
```bash
cd ngo-compliance
python -m backend.services.ingest
```

Expected terminal output:
```
Starting corpus ingestion — 17 documents
→ central/fcra/FCRA_Act_2010.pdf
  ✓ 84 new chunks
→ maharashtra/BPT_Act_1950.pdf
  ✓ 127 new chunks
...
Total chunks in ChromaDB: ~900-1200
```

Phase 2 Test:
```bash
python backend/tests/test_retrieval.py
```
Expected: Each of 7 test queries returns 2 results with act_name and
section_ref printed. Verify the returned text is actually relevant to the
query. If results look completely unrelated, chunking or embedding has a
problem.

---

### PHASE 3 — OCR + Extraction Pipeline

```
[✓] backend/services/preprocessing.py written
[✓] backend/services/ocr.py written
[✓] backend/services/document_templates.py written
[✓] backend/services/extraction.py written
[ ] Test files placed in uploads/test/
[ ] OCR test run on sample documents
[ ] Extraction test run and fields verified
```

Place test PDFs in uploads/test/ — can use any real or dummy NGO document
scans for testing. At minimum: one Trust Deed PDF and one certificate-style PDF.

Phase 3 Test:
```bash
python backend/tests/test_extraction.py
```
Expected: OCR outputs >500 chars per document, quality is fair or good.
Extraction outputs structured JSON with at least some fields populated.
_validation.clean is True (no cross-field issues).

Key things to verify manually in the output JSON:
- registration_number is extracted and looks like a real reg number
- pan matches format [A-Z]{5}[0-9]{4}[A-Z]
- trustee_names is a list of person names (not org names or garbled text)
- non_profit_clause_present is True for Trust Deed

---

### PHASE 4 — RAG + LLM Assessment

```
[✓] backend/services/rag.py written
    (covers: retrieval, LLM call, citation validation, routing, all 7 dimensions)
[✓] backend/services/scoring.py written
[ ] Single dimension test passed
[ ] CORPUS_GAP test passed
[ ] Full 7-dimension assessment test passed
```

Phase 4 Tests:
```bash
python backend/tests/test_assessment.py
```

What test_assessment.py should do (write this file in Phase 4):
```python
# Test 1: Single dimension
dim = get_dimension("registration")
result = assess_dimension(dim, sample_ngo_json, "maharashtra", "Public Trust")
assert result.status in ("PASS", "FAIL", "UNCERTAIN", "CORPUS_GAP")
assert 0.0 <= result.confidence <= 1.0
assert result.routing in ("auto_report", "human_review", "corpus_alert")

# Test 2: CORPUS_GAP routing
result = assess_dimension(dim, sample_ngo_json, "gujarat", "Trust")
assert result.status == "CORPUS_GAP"
assert result.routing == "corpus_alert"

# Test 3: Full assessment
findings = run_full_assessment(sample_ngo_json, "maharashtra", "Public Trust")
assert len(findings) == 7
score = calculate_score(findings)
assert 0 <= score["overall_score"] <= 100
assert score["pass_count"] + score["fail_count"] + \
       score["uncertain_count"] + score["corpus_gap_count"] == 7

# Test 4: Consistency (run twice, check score variance)
findings2 = run_full_assessment(sample_ngo_json, "maharashtra", "Public Trust")
score2 = calculate_score(findings2)
assert abs(score["overall_score"] - score2["overall_score"]) <= 5
```

---

### PHASE 5 — FastAPI Backend + Database

```
[ ] backend/models/database.py written (SQLAlchemy engine + session)
[ ] backend/models/orm.py written (all 8 ORM models)
[ ] backend/models/schemas.py written (Pydantic request/response models)
[ ] backend/main.py written (FastAPI app + router registration)
[ ] backend/routers/auth.py written
[ ] backend/routers/submissions.py written
[ ] backend/routers/compliance.py written
[ ] backend/routers/findings.py written
[ ] backend/routers/queue.py written
[ ] backend/routers/reports.py written
[ ] Database tables created (alembic migrate or create_all)
[ ] Compliance dimensions seeded into DB
```

Phase 5 Tests (run with pytest or curl):
```bash
# Start backend
uvicorn backend.main:app --reload

# Test auth
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"officer@darpan.gov.in","password":"pilot2025"}'
# Expected: {"token": "...", "name": "Officer Ramesh Kumar", "role": "compliance_officer"}

# Test submission create
curl -X POST http://localhost:8000/submissions \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"org_name":"Test NGO","state":"maharashtra","entity_type":"Public Trust","pan":"AAATA1234A","sector":"Education","contact_email":"test@ngo.org","year_of_incorporation":2019}'
# Expected: {"id": "<uuid>", "status": "pending"}

# Test document upload
curl -X POST http://localhost:8000/submissions/<id>/documents \
  -H "Authorization: Bearer <token>" \
  -F "file=@test_trust_deed.pdf" \
  -F "doc_type=trust_deed"
# Expected: {"doc_id": "<uuid>", "status": "uploaded"}

# Test assessment trigger
curl -X POST http://localhost:8000/submissions/<id>/assess \
  -H "Authorization: Bearer <token>"
# Expected: {"status": "processing"} — assessment runs async

# Test findings
curl http://localhost:8000/submissions/<id>/findings \
  -H "Authorization: Bearer <token>"
# Expected: list of 7 findings with status/confidence/citation

# Test queue
curl http://localhost:8000/queue \
  -H "Authorization: Bearer <token>"
# Expected: list of UNCERTAIN findings pending review

# Test officer determination
curl -X POST http://localhost:8000/queue/<queue_id>/determine \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"determination":"PASS","notes":"Reviewed manually, compliant."}'
# Expected: {"status": "reviewed", "determination": "PASS"}
```

All endpoints must return 2xx. Auth required endpoints must return 401
without token. Role-restricted endpoints must return 403 for wrong role.

---

### PHASE 6 — Frontend Integration

```
[ ] Frontend .env.local created (NEXT_PUBLIC_API_URL=http://localhost:8000)
[ ] Auth context + JWT storage (in-memory, not localStorage)
[ ] Login page wired → POST /auth/login
[ ] Submission form → POST /submissions
[ ] Document upload → POST /submissions/{id}/documents
[ ] Processing page polls GET /submissions/{id} until status=complete
[ ] Dashboard fetches GET /submissions/{id}/findings
[ ] Findings page fetches detailed findings per dimension
[ ] Review queue fetches GET /queue, submits POST /queue/{id}/determine
[ ] Report page fetches GET /submissions/{id}/report
[ ] PDF download triggers GET /submissions/{id}/report/pdf
```

Phase 6 Test:
Run the complete flow in the browser end-to-end.

Checklist:
  [ ] Login with officer@darpan.gov.in / pilot2025 — JWT stored in memory
  [ ] Submit a new NGO with Maharashtra, Public Trust
  [ ] Upload at least one document
  [ ] Trigger assessment — processing screen shows steps
  [ ] Dashboard loads with score and 7 findings
  [ ] At least one finding is UNCERTAIN and appears in queue
  [ ] Officer submits determination in queue
  [ ] Final report shows both AI and human-reviewed sections
  [ ] PDF download returns a file

---

### PHASE 7 — Testing + Polish

```
[ ] OCR test: worst-case scanned document (rubber stamp, low DPI)
[ ] Test all 4 states with different entity types
[ ] Test submission with missing documents (only Trust Deed uploaded)
[ ] Test CORPUS_GAP appears when state coverage is incomplete
[ ] Test Human Review Queue blinded protocol (AI verdict hidden until reveal)
[ ] Test score variance between two identical runs (must be <= 5 points)
[ ] PDF report renders correctly with all sections
[ ] Final demo run for mentor presentation
```

---

## 17. COMMON ERRORS AND FIXES

```
ChromaDB empty after ingest
  → Check PDF paths in corpus_config.py match actual folder structure
  → Run test_pdfs.py first to confirm PDFs are readable

Tesseract not found
  → Install: sudo apt-get install tesseract-ocr tesseract-ocr-hin tesseract-ocr-mar tesseract-ocr-kan
  → On Mac: brew install tesseract tesseract-lang

spaCy model missing
  → python -m spacy download en_core_web_sm

Ollama connection refused
  → Start Ollama: ollama serve
  → Confirm models: ollama list (should show mistral and nomic-embed-text)

LLM returns non-JSON output
  → safe_parse_json() in rag.py handles this — strips markdown fences
  → Persistent failures: lower temperature further (0.05) or simplify prompt

ChromaDB HNSW dimension mismatch
  → nomic-embed-text produces 768-dim vectors
  → If you changed embedding models, delete vectorstore/ and re-run ingest

PostgreSQL connection error
  → Check DATABASE_URL in .env matches local PostgreSQL credentials
  → Confirm database exists: psql -U postgres -c "\l"

WeasyPrint PDF fails
  → Install system dependencies: sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0
  → On Mac: brew install pango
```

---

## 18. WHAT IS NOT IN SCOPE FOR THIS PILOT

```
- User registration / signup (accounts provisioned by admin)
- Multi-language UI (system works on multilingual documents via Tesseract
  language packs, but the UI itself is English only)
- Real-time Darpan API integration (mocked with MOCK_DARPAN_DATA dict)
- Payment or fee processing
- Email notifications
- Mobile app
- Docker deployment (docker-compose.yml is optional/future)
- More than 4 pilot states
- Sector-specific compliance dimensions beyond the 7 core ones
- Batch processing of multiple NGOs
```

---

## 19. HOW TO EXPLAIN THIS PROJECT

For mentor / evaluator presentation:

"This is an AI-assisted compliance verification layer for NGO Darpan. NGO Darpan
currently issues Darpan IDs based on self-declared affidavits — no document is
cross-checked against state law. This system fills that gap.

An NGO uploads their registration documents. The system extracts structured data
via OCR and NLP, then uses RAG to retrieve the actual legal provisions from a
local ChromaDB vector store containing the relevant state Acts and central
regulations. A local LLM (Mistral 7B via Ollama) reasons over the legal text
and the NGO evidence for each of 7 compliance dimensions, returning a structured
finding with status, confidence, legal citation, and reasoning.

High-confidence findings publish automatically. Uncertain findings route to a
human compliance officer for blinded review. The final report clearly separates
AI-assessed and officer-reviewed findings.

Everything runs locally — no data leaves the server. Law changes are handled by
re-ingesting updated PDFs — no code changes required. The compliance dimensions
are stored as data, not code, making the framework auditable and extensible."
```

---

*Last updated: Phase 0-4 code complete. Phase 5 (FastAPI + DB) is next.*
*This file should be updated as each phase is completed.*
