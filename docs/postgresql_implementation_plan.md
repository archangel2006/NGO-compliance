# PostgreSQL Database Implementation Plan

This document outlines a structured, step-by-step blueprint for migrating the NGO Compliance Verification System from the current in-memory transient store (`store.py`) to a relational PostgreSQL database.

---

## Migration Strategy: The "Store Adapter" Pattern
To minimize the risk of breaking existing FastAPI routers, we will implement the **Store Adapter** pattern. Instead of rewriting queries directly inside all routers, we will replace the in-memory dictionary operations inside [store.py](file:///c:/Users/DELL/Desktop/NITI%20Aayog/NGO-compliance/backend/store.py) with database transactions. This preserves the existing function signatures and prevents cascading file changes.

---

## Step-by-Step Implementation Plan

```mermaid
graph TD
    A[Phase 1: Dependencies & Env] --> B[Phase 2: Database Initialization]
    B --> C[Phase 3: ORM Models & Alembic]
    C --> D[Phase 4: Relational Extraction Adapters]
    D --> E[Phase 5: Store.py Refactoring]
    E --> F[Phase 6: Validation & Tests]
```

### Phase 1: Environment & Dependencies
1. **Install PostgreSQL Packages**:
   Add the following packages to `backend/requirements.txt`:
   * `sqlalchemy>=2.0.0` (SQL Toolkit & ORM)
   * `psycopg2-binary>=2.9.0` (PostgreSQL Database Adapter)
   * `alembic>=1.11.0` (Database Migrations Manager)
2. **Update Environment Configuration**:
   Verify `DATABASE_URL` is set in [backend/.env](file:///c:/Users/DELL/Desktop/NITI%20Aayog/NGO-compliance/backend/.env):
   ```ini
   DATABASE_URL=postgresql://postgres:password@localhost:5432/ngo_compliance
   ```

### Phase 2: Database Engine & Session Initialization
1. Create a database module folder: `backend/models/`.
2. Create `backend/models/database.py`:
   * Set up `create_engine` using `DATABASE_URL`.
   * Configure `sessionmaker` with `autocommit=False, autoflush=False`.
   * Declare the declarative base `Base = declarative_base()`.
   * Add a dependency generator helper `get_db()` for FastAPI route injection.

### Phase 3: ORM Models Definition & Migrations
1. Create `backend/models/orm.py`:
   * Define `Submission`, `UploadedDocument`, `ComplianceFinding`, `HumanReviewQueue`, `ComplianceReport`, and `CorpusMetadata` classes inheriting from `Base`.
   * Define concrete relationship tables for each document facts type audited (e.g. `ExtractedTrustDeed`, `ExtractedRegistrationCertificate`, etc.) mapping foreign keys back to `submissions.id` and `uploaded_documents.id` (1-to-1 relationships).
   * Enforce primary keys (`UUID` as string/native), default timestamps (`created_at = Column(DateTime, default=datetime.utcnow)`), and relational constraints (`ON DELETE CASCADE`).
2. **Alembic Ingestion**:
   * Initialize Alembic: Run `alembic init alembic` from the `backend/` directory.
   * Update `alembic.ini` to map to `DATABASE_URL`.
   * Modify `alembic/env.py` to import `Base` from `backend.models.orm` and set `target_metadata = Base.metadata`.
   * Generate initial migration: `alembic revision --autogenerate -m "initial_schema"`.
   * Run migration: `alembic upgrade head`.

### Phase 4: Relational Extraction Adapters
Currently, `extraction.py` returns a flat dictionary representing the merged fields of all uploaded documents.
* Implement a database persistence mapper inside `backend/services/extraction.py`:
  * Map corresponding dictionary keys (e.g. `reg_date`, `quorum` for trust deeds) to their respective relational DB objects (`ExtractedTrustDeed`).
  * Persist the mapping records as part of the transaction when files are uploaded/processed.

### Phase 5: Re-routing `store.py` to PostgreSQL
Modify helper functions in [store.py](file:///c:/Users/DELL/Desktop/NITI%20Aayog/NGO-compliance/backend/store.py) to execute database queries:
* **`get_submission(submission_id)`**:
  * Query `submissions` table: `db.query(Submission).filter(Submission.id == submission_id).first()`.
* **`get_documents_for_submission(submission_id)`**:
  * Query `uploaded_documents` table: `db.query(UploadedDocument).filter(UploadedDocument.submission_id == submission_id).all()`.
* **`get_findings_for_submission(submission_id)`**:
  * Query `compliance_findings` table: `db.query(ComplianceFinding).filter(ComplianceFinding.submission_id == submission_id).all()`.

---

## Verification & Quality Checks

To ensure database consistency and prevent regression, perform these verification checks at each phase:

### 1. Connection & Schema Validation Check
* **Check**: Verify the tables are correctly created in PostgreSQL.
* **Execution**: Run `psql -d ngo_compliance -c "\dt"` to check that all tables mapped in Step 2 are active.

### 2. Transaction Integrity & FK Cascade Checks
* **Check**: Verify that deleting a submission cascades and deletes all related extraction rows, compliance findings, review items, and report rows.
* **Execution**: Write a mock test in `tests/test_db_cascade.py` that creates a test submission, populates findings, deletes the submission, and verifies that `db.query(ComplianceFinding)` returns empty.

### 3. API Contract Regression Check
* **Check**: Confirm that FastAPI endpoints continue to respond with the exact same JSON shapes expected by the React frontend.
* **Execution**: Start the server `uvicorn main:app --reload` and run the existing python test suite (e.g. `tests/test_assessment.py`) to confirm API payload validity.
