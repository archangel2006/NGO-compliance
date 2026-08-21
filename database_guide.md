# NGO Compliance Verification System — Database Guide & Table Explorer

This document provides a reference guide for exploring and showcasing all **13 relational database tables** populated with sample NGO compliance data.

---

## 📊 Database Summary
* **Database File**: `ngo_compliance.db` (SQLite) / `ngo_compliance` (PostgreSQL)
* **Total Tables**: 13
* **Total Records**: 76
* **Seeded NGOs**:
  1. **Asha Jyoti Welfare Foundation** (Delhi — Public Trust)
  2. **Maharashtra Grameen Seva Trust** (Maharashtra — Public Trust)
  3. **Vidya Vardhini Education Society** (Karnataka — Society)

---

## 💻 Commands to View Tables

Run these commands from your terminal inside the project root (`NGO-compliance`):

### 1. View Summary of All 13 Tables
```powershell
.venv\Scripts\python.exe -m backend.tests.view_tables
```

---

### 2. Commands to View Specific Tables

#### Core Application Tables
* **View Submissions (NGO Profiles & Compliance Scores)**:
  ```powershell
  .venv\Scripts\python.exe -m backend.tests.view_tables submissions
  ```

* **View Compliance Findings (AI Reasoning, Status, Citations, Evidence per Dimension)**:
  ```powershell
  .venv\Scripts\python.exe -m backend.tests.view_tables compliance_findings
  ```

* **View Human Review Queue (Blinded Officer Queue for Uncertain Findings)**:
  ```powershell
  .venv\Scripts\python.exe -m backend.tests.view_tables human_review_queue
  ```

* **View Uploaded Documents (File Registry, OCR Status, Quality)**:
  ```powershell
  .venv\Scripts\python.exe -m backend.tests.view_tables uploaded_documents
  ```

* **View Merged Extracted Fields (Combined Flat JSON for RAG Pipeline)**:
  ```powershell
  .venv\Scripts\python.exe -m backend.tests.view_tables extracted_fields
  ```

---

#### Document-Specific Extracted Fact Tables (13-Table Relational Schema)

* **View Extracted Trust Deeds (Quorum, Trustees, Office Bearers, Non-profit Clause)**:
  ```powershell
  .venv\Scripts\python.exe -m backend.tests.view_tables extracted_trust_deeds
  ```

* **View Extracted Registration Certificates (Registration No, Authority, Act, State)**:
  ```powershell
  .venv\Scripts\python.exe -m backend.tests.view_tables extracted_registration_certificates
  ```

* **View Extracted Tax 12A / 12AB Certificates (Certificate No, Expiry, Form 10AB)**:
  ```powershell
  .venv\Scripts\python.exe -m backend.tests.view_tables extracted_12a_certificates
  ```

* **View Extracted Tax 80G Certificates (80G No, Deduction Rate, Expiry)**:
  ```powershell
  .venv\Scripts\python.exe -m backend.tests.view_tables extracted_80g_certificates
  ```

* **View Extracted FCRA Certificates (FCRA Reg No, SBI Main Branch Account)**:
  ```powershell
  .venv\Scripts\python.exe -m backend.tests.view_tables extracted_fcra_certificates
  ```

* **View Extracted Annual Reports (Receipts, Expenditure, CSR & Govt Grant Flags)**:
  ```powershell
  .venv\Scripts\python.exe -m backend.tests.view_tables extracted_annual_reports
  ```

* **View Extracted Audit Reports (Auditor Name, ICAI Reg No, FCRA Audit Flag)**:
  ```powershell
  .venv\Scripts\python.exe -m backend.tests.view_tables extracted_audit_reports
  ```

* **View Extracted PAN Cards (PAN Number, Registered Name)**:
  ```powershell
  .venv\Scripts\python.exe -m backend.tests.view_tables extracted_pan_cards
  ```

---

## 🗂️ Complete List of 13 Database Tables

| # | Table Name | Rows | Description |
|---|---|---|---|
| 1 | `submissions` | 3 | Master NGO registrations (Org name, State, Entity Type, PAN, Sector, Score, Status) |
| 2 | `uploaded_documents` | 22 | File upload registry (Path, Doc Type, OCR Status, Quality) |
| 3 | `extracted_fields` | 3 | Combined JSON store of all extracted fields used by RAG pipeline |
| 4 | `extracted_trust_deeds` | 3 | Trust deed attributes (Quorum, Trustees, Non-profit & Dissolution clauses) |
| 5 | `extracted_registration_certificates` | 3 | Registration cert attributes (Reg No, Act registered under, Registering authority) |
| 6 | `extracted_12a_certificates` | 3 | Income Tax 12A/12AB cert attributes (12AB No, Expiry Date, Form Ref) |
| 7 | `extracted_80g_certificates` | 3 | Income Tax 80G cert attributes (80G No, Deduction Rate, Expiry) |
| 8 | `extracted_fcra_certificates` | 1 | FCRA cert attributes (FCRA Reg No, SBI New Delhi Main Branch check) |
| 9 | `extracted_annual_reports` | 3 | Financial receipts, expenditure, CSR grants, and utilisation statements |
| 10 | `extracted_audit_reports` | 3 | Statutory auditor details, ICAI firm registration, separate FCRA audit flag |
| 11 | `extracted_pan_cards` | 3 | PAN Card details and cross-reference verification |
| 12 | `compliance_findings` | 21 | AI compliance evaluation across 7 dimensions per NGO (Citations, Evidence, Reasoning) |
| 13 | `human_review_queue` | 5 | Blinded compliance officer queue for uncertain AI findings |

---

## 🖼️ GUI Inspection Option for Presentations

To show a visual database GUI during a live demo or presentation:

1. **Option A: VS Code SQLite Viewer Extension**
   * Install **"SQLite Viewer"** in VS Code.
   * Right-click `ngo_compliance.db` in VS Code file explorer -> Select **"Open Database"**.

2. **Option B: DB Browser for SQLite (GUI App)**
   * Download & open **DB Browser for SQLite**.
   * Click **"Open Database"** -> Choose `ngo_compliance.db`.
   * Click the **"Browse Data"** tab to switch between all 13 tables.
