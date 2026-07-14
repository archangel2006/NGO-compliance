# NGO Compliance Verification System

An internship project developed in collaboration with the NITI Aayog Informatics Division, focused on building an AI‑assisted decision‑support system for NGO compliance verification.

The system is designed to help assess NGO registration and compliance documents against applicable state‑specific and central legal requirements. Rather than acting as an automated authority, it supports structured review by extracting evidence from uploaded documents, retrieving relevant legal provisions, and generating an auditable compliance assessment.

## Project Overview

The current NGO Darpan ecosystem primarily verifies registration identity rather than validating the documentary evidence behind it. This creates a gap where registration documents may not be cross‑checked against the legal framework that governs them. This project addresses that challenge by creating a local, evidence‑based workflow for document review and compliance analysis.

## Problem Statement

NGOs often submit registration and compliance documents that are self‑declared and not systematically validated against the laws applicable to their legal form and state of registration. This can lead to inconsistencies, missing legal clauses, and compliance issues that are discovered late in grant or regulatory processes.

The proposed system aims to reduce this risk by providing a structured review layer that:
- verifies uploaded documents against relevant laws and regulations,
- highlights missing or non‑compliant clauses with supporting evidence,
- cites the legal provisions and document sources used in the assessment, and
- routes uncertain findings to human review for final judgment.

## Objectives
- Build a decision‑support system for NGO compliance assessment.
- Cross‑check registration documents against relevant state and central regulations.
- Support legal reasoning through retrieval and evidence‑backed analysis.
- Provide a transparent workflow for human review and decision‑making.
- Keep the system local‑first and privacy‑conscious.

## Scope

The initial implementation focuses on a limited set of states and core compliance dimensions, including:
- Registration and legal status
- Governance structure
- Membership requirements
- Financial compliance
- Tax compliance
- FCRA compliance
- Audit requirements

## System Architecture

The system is organized into three functional layers:
1. **Knowledge Layer** – Stores legal corpus content from state and central regulations and organizes legal text into retrievable sections.
2. **Framework Layer** – Defines compliance dimensions and review logic while allowing legal requirements to vary by state.
3. **Assessment Layer** – Processes uploaded documents, extracts structured information, retrieves relevant legal content, and generates a compliance assessment with citations, evidence, and confidence‑based routing.

## Compliance Framework

| Dimension | Focus Area |
|---|---|
| Registration & Legal Status | Validity of registration, legal identity, and recognized status |
| Governance Structure | Board composition, trustee or office bearer structure, and governance requirements |
| Membership Requirements | Minimum membership and eligibility criteria as defined by law |
| Financial Compliance | Financial records, utilization, and financial reporting obligations |
| Tax Compliance | 12A/80G‑related compliance and tax exemption requirements |
| FCRA Compliance | Registration, designated account, and reporting obligations |
| Audit Requirements | Audit‑related compliance and documentation requirements |

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Next.js | User interface and application experience |
| Frontend Styling | Tailwind CSS | Responsive interface design |
| Backend | FastAPI | API services and application logic |
| Document Processing | PyMuPDF, Tesseract | OCR and text extraction from uploaded documents |
| Vector Search | ChromaDB | Retrieval of relevant legal content |
| Language Model | Ollama (Mistral 7B) | Local reasoning and analysis support |
| Database | PostgreSQL | Structured storage for application and review data |

## Project Structure

```text
NGO-compliance/
├── ngo-compliance-frontend/   # Next.js UI
├── ngo-compliance-backend/    # FastAPI services
├── README.md
└── .gitignore
```

## Prerequisites
- **Python 3.10+** (recommended via pyenv or virtualenv)
- **Node.js 18+** and npm
- **PostgreSQL** (running locally, default port 5432)
- **Ollama** installed and running (`ollama serve`)
- **Ollama models**: `mistral` and `nomic-embed-text` pulled beforehand
- **Tesseract OCR** installed and accessible in PATH
- **Git** (for version control)

## Local Setup
### 1. Clone the repository
```bash
git clone <repo-url>
cd NGO-compliance
```
### 2. Backend setup
```bash
cd ngo-compliance-backend
python -m venv venv
# Windows
venv\Scripts\activate
# Unix/macOS
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```
Create a `.env` file (copy from `.env.example` if present) and set the required variables:
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=ngo_compliance
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
VECTORSTORE_PATH=../vectorstore   # path to Chroma persistent storage
EMBEDDING_MODEL=nomic-embed-text
LLM_MODEL=mistral
```
#### Initialise the database tables
```bash
alembic upgrade head   # if Alembic migrations are configured, otherwise run custom init script
```
#### Ingest the legal corpus (only required once or when the corpus changes)
```bash
python -m services.ingest
```
The script will create/refresh the Chroma collection at the location defined by `VECTORSTORE_PATH`.
### 3. Frontend setup
```bash
cd ../ngo-compliance-frontend
npm install
npm run dev
```
The UI will be served at `http://localhost:3000`.
### 4. Run the backend server
```bash
# still inside ngo-compliance-backend
uvicorn main:app --reload --port 8000
```
The API will be available at `http://localhost:8000`.

## Running the Full Stack
1. Start **Ollama** (`ollama serve`).
2. Ensure PostgreSQL is running.
3. Run the backend (`uvicorn`).
4. In a separate terminal, launch the frontend (`npm run dev`).
5. Open the web app, create a submission, upload documents, and click *Assess*.

## Re‑building the Vector Store
If you change the embedding model or suspect a dimension mismatch, the system will automatically detect the inconsistency, delete the incompatible collection, and re‑ingest the corpus on the next start‑up. No manual file‑system cleanup is required.

## Testing
```bash
# From the backend directory
pytest backend/tests
```
All unit and integration tests should pass, confirming OCR, extraction, RAG, and scoring pipelines.

## Troubleshooting
- **Embedding dimension mismatch** – Ensure the same model name is set for `EMBEDDING_MODEL` in `.env` for both ingestion and retrieval. The startup logs will indicate whether the existing collection was reused or rebuilt.
- **State metadata not matching** – The backend normalises short state codes (`dl`, `mh`, `ka`, `rj`) to full names (`delhi`, `maharashtra`, `karnataka`, `rajasthan`). Verify the frontend is sending one of the supported codes.
- **Chroma empty** – Check that `VECTORSTORE_PATH` points to the correct directory and that `services.ingest` completed without errors.

## License
This project is for educational and prototype purposes. See `LICENSE` for details.


An internship project developed in collaboration with the NITI Aayog Informatics Division, focused on building an AI-assisted decision-support system for NGO compliance verification.

The system is designed to help assess NGO registration and compliance documents against applicable state-specific and central legal requirements. Rather than acting as an automated authority, it supports structured review by extracting evidence from uploaded documents, retrieving relevant legal provisions, and generating an auditable compliance assessment.

## Project Overview

The current NGO Darpan ecosystem primarily verifies registration identity rather than validating the documentary evidence behind it. This creates a gap where registration documents may not be cross-checked against the legal framework that governs them. This project addresses that challenge by creating a local, evidence-based workflow for document review and compliance analysis.

## Problem Statement

NGOs often submit registration and compliance documents that are self-declared and not systematically validated against the laws applicable to their legal form and state of registration. This can lead to inconsistencies, missing legal clauses, and compliance issues that are discovered late in grant or regulatory processes.

The proposed system aims to reduce this risk by providing a structured review layer that:

- verifies uploaded documents against relevant laws and regulations,
- highlights missing or non-compliant clauses with supporting evidence,
- cites the legal provisions and document sources used in the assessment, and
- routes uncertain findings to human review for final judgment.

## Objectives

- Build a decision-support system for NGO compliance assessment.
- Cross-check registration documents against relevant state and central regulations.
- Support legal reasoning through retrieval and evidence-backed analysis.
- Provide a transparent workflow for human review and decision-making.
- Keep the system local-first and privacy-conscious.

## Scope

The initial implementation focuses on a limited set of states and core compliance dimensions, including:

- Registration and legal status
- Governance structure
- Membership requirements
- Financial compliance
- Tax compliance
- FCRA compliance
- Audit requirements

## System Architecture

The system is organized into three functional layers:

1. Knowledge Layer
   - Stores legal corpus content from state and central regulations.
   - Organizes legal text into retrievable sections for evidence-based reasoning.

2. Framework Layer
   - Defines compliance dimensions and review logic.
   - Keeps the assessment structure stable while allowing legal requirements to vary by state.

3. Assessment Layer
   - Processes uploaded documents, extracts structured information, retrieves relevant legal content, and generates a compliance assessment.
   - Produces findings with citations, evidence, and confidence-based routing for human review.

## Compliance Framework

| Dimension | Focus Area |
| --- | --- |
| Registration & Legal Status | Validity of registration, legal identity, and recognized status |
| Governance Structure | Board composition, trustee or office bearer structure, and governance requirements |
| Membership Requirements | Minimum membership and eligibility criteria as defined by law |
| Financial Compliance | Financial records, utilization, and financial reporting obligations |
| Tax Compliance | 12A/80G-related compliance and tax exemption requirements |
| FCRA Compliance | Registration, designated account, and reporting obligations |
| Audit Requirements | Audit-related compliance and documentation requirements |

## Tech Stack

| Layer | Technology | Purpose |
| --- | --- | --- |
| Frontend | Next.js | User interface and application experience |
| Frontend Styling | Tailwind CSS | Responsive interface design |
| Backend | FastAPI | API services and application logic |
| Document Processing | PyMuPDF, Tesseract | OCR and text extraction from uploaded documents |
| Vector Search | ChromaDB | Retrieval of relevant legal content |
| Language Model | Ollama | Local reasoning and analysis support |
| Database | PostgreSQL | Structured storage for application and review data |

## Project Structure

```text
NGO-compliance/
├── ngo-compliance-frontend/     # Next.js-based user interface
├── ngo-compliance-backend/      # FastAPI-based backend services
├── compliance-dimensions-card.jsx
├── ngo-compliance-prototype.jsx
└── README.md
```

## Data Sources

The legal corpus is sourced from official government and regulatory materials, including:

- India Code
- State government legal portals and registrars
- FCRA online resources
- Income Tax Department guidance
- NGO Darpan guidelines and compliance materials

## Getting Started

### Frontend

```bash
cd ngo-compliance-frontend
npm install
npm run dev
```

The frontend will be available at http://localhost:3000.

### Backend

```bash
cd ngo-compliance-backend
pip install -r requirements.txt
```

The backend services are intended to be run locally as the application logic is completed and integrated.

## Project Status

This repository contains the initial structure and interface for an internship project focused on NGO compliance verification using AI-assisted review workflows. The work is centered on building an auditable, evidence-based compliance system for legal and regulatory assessment.
