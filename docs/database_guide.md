# NGO Compliance Verification System — Database Guide & Table Explorer

This document provides a step-by-step guide to explore and showcase all **13 relational database tables** populated with NGO compliance data.

---

## 📊 Database Summary
* **Database File**: `ngo_compliance.db` (SQLite) / `ngo_compliance` (PostgreSQL)
* **Total Tables**: 13
* **Total Records**: 76
* **Seeded NGO Profiles**:
  1. **Asha Jyoti Welfare Foundation** (Delhi — Public Trust)
  2. **Maharashtra Grameen Seva Trust** (Maharashtra — Public Trust)
  3. **Vidya Vardhini Education Society** (Karnataka — Society)

---

## 🚀 Terminal Commands (Command-Line Inspection)

### Step 1: Activate Virtual Environment (Run Once)
Before running any table inspection commands, activate your virtual environment:

```powershell
.venv\Scripts\activate
```

---

### Step 2: List All 13 Tables & Summary
To display the list of all 13 database tables along with their row counts:

```powershell
python -m backend.tests.view_tables
```

---

### Step 3: Inspect Specific Table Structure & Full Data

Running `python -m backend.tests.view_tables <table_name>` prints the full column structure, data types, and all populated row data for that table.

#### Core Application Tables
* **Master NGO Submissions (Flat Scores & Status)**:
  ```powershell
  python -m backend.tests.view_tables submissions
  ```

* **Compliance Findings (AI Reasoning, Status, Legal Citations per Dimension)**:
  ```powershell
  python -m backend.tests.view_tables compliance_findings
  ```

* **Human Review Queue (Blinded Officer Queue for Uncertain Findings)**:
  ```powershell
  python -m backend.tests.view_tables human_review_queue
  ```

* **Uploaded Documents (File Registry, OCR Status, Quality)**:
  ```powershell
  python -m backend.tests.view_tables uploaded_documents
  ```

* **Merged Extracted Fields (Metadata & Field Summaries)**:
  ```powershell
  python -m backend.tests.view_tables extracted_fields
  ```

---

#### Document-Specific Relational Fact Tables (Flat Columns)

* **Trust Deeds / MOA (Quorum, Trustees, Office Bearers, Dissolution Clauses)**:
  ```powershell
  python -m backend.tests.view_tables extracted_trust_deeds
  ```

* **Registration Certificates (Reg Number, Authority, Act, State)**:
  ```powershell
  python -m backend.tests.view_tables extracted_registration_certificates
  ```

* **Income Tax 12A / 12AB Certificates (12AB Reg No, Expiry, Form 10AB)**:
  ```powershell
  python -m backend.tests.view_tables extracted_12a_certificates
  ```

* **Income Tax 80G Certificates (80G Reg No, Deduction Rate, Expiry)**:
  ```powershell
  python -m backend.tests.view_tables extracted_80g_certificates
  ```

* **FCRA Certificates (FCRA Reg No, SBI Main Branch Account Check)**:
  ```powershell
  python -m backend.tests.view_tables extracted_fcra_certificates
  ```

* **Annual Reports (Total Receipts, Expenditure, CSR & Govt Grants)**:
  ```powershell
  python -m backend.tests.view_tables extracted_annual_reports
  ```

* **CA Audit Reports (Auditor Name, ICAI Reg No, FCRA Audit Flag)**:
  ```powershell
  python -m backend.tests.view_tables extracted_audit_reports
  ```

* **PAN Cards (PAN Number, Registered Entity Name)**:
  ```powershell
  python -m backend.tests.view_tables extracted_pan_cards
  ```

---

## 🖼️ Visual GUI Inspection Methods (Spreadsheet / Grid View)

For live demonstrations and presentations to mentors, you can view the database as a visual Excel-like grid:

### Method 1: VS Code SQLite Viewer Extension (Recommended)
1. Open VS Code **Extensions** (`Ctrl + Shift + X`).
2. Search for **SQLite Viewer** (by *qwtel*) and click **Install**.
3. In the VS Code file explorer on the left, right-click `ngo_compliance.db` and select **Open Database**.
4. Click any table from the sidebar to view rows and columns in a spreadsheet layout.

### Method 2: DB Browser for SQLite (Standalone GUI App)
1. Download **DB Browser for SQLite** (free): `https://sqlitebrowser.org/`
2. Launch the app and click **Open Database**.
3. Select `ngo_compliance.db` from your project folder.
4. Click the **Browse Data** tab to view, search, and filter all 13 tables.

---

## 🗂️ Complete 13-Table Schema Overview

| # | Table Name | Rows | Description |
|---|---|---|---|
| 1 | `submissions` | 3 | Master NGO registrations (Org name, State, Entity Type, PAN, Flat Scores, Status) |
| 2 | `uploaded_documents` | 22 | File upload registry (Path, Doc Type, OCR Status, Quality) |
| 3 | `extracted_fields` | 3 | Extraction metadata and field count tracking |
| 4 | `extracted_trust_deeds` | 3 | Trust deed attributes (Quorum, Trustees, Non-profit & Dissolution clauses) |
| 5 | `extracted_registration_certificates` | 3 | Registration cert attributes (Reg No, Act registered under, Registering authority) |
| 6 | `extracted_12a_certificates` | 3 | Income Tax 12A/12AB cert attributes (12AB No, Expiry Date, Form Ref) |
| 7 | `extracted_80g_certificates` | 3 | Income Tax 80G cert attributes (80G No, Deduction Rate, Expiry) |
| 8 | `extracted_fcra_certificates` | 1 | FCRA cert attributes (FCRA Reg No, SBI New Delhi Main Branch check) |
| 9 | `extracted_annual_reports` | 3 | Financial receipts, expenditure, CSR grants, and grant sources |
| 10 | `extracted_audit_reports` | 3 | Statutory auditor details, ICAI firm registration, separate FCRA audit flag |
| 11 | `extracted_pan_cards` | 3 | PAN Card details and cross-reference verification |
| 12 | `compliance_findings` | 21 | AI compliance evaluation across 7 dimensions per NGO (Citations, Evidence, Reasoning) |
| 13 | `human_review_queue` | 5 | Blinded compliance officer queue for uncertain AI findings |
