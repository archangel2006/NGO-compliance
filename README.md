# NGO Compliance System

Full-stack system for NGO document ingestion, OCR extraction, compliance analysis, and report generation.

## Tech Stack
- Frontend: Next.js 14 (App Router), Tailwind CSS
- Backend: FastAPI (Python)
- OCR: PyMuPDF, Tesseract
- Vector DB: ChromaDB
- LLM: Ollama (Mistral 7B)
- Database: PostgreSQL

---

## Project Structure

```
ngo-compliance/
├── frontend/                  ← Next.js
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.jsx           ← Landing
│   │   │   ├── directory/
│   │   │   │   └── page.jsx
│   │   │   ├── submit/
│   │   │   │   └── page.jsx
│   │   │   ├── dashboard/
│   │   │   │   └── page.jsx
│   │   │   └── report/
│   │   │       └── page.jsx
│   │   └── components/
│   │       ├── Nav.jsx
│   │       ├── StatusBadge.jsx
│   │       └── ComplianceRing.jsx
│   └── package.json
│
└── backend/                   ← FastAPI
    ├── main.py
    ├── routers/
    │   ├── submissions.py
    │   ├── compliance.py
    │   └── reports.py
    ├── services/
    │   ├── ocr.py
    │   ├── extraction.py
    │   ├── rag.py
    │   └── llm.py
    ├── models/
    │   └── database.py
    ├── corpus/                ← Legal documents go here
    │   ├── maharashtra/
    │   ├── delhi/
    │   ├── karnataka/
    │   └── rajasthan/
    └── requirements.txt

```

---

## Backend Setup

### 1. Create virtual environment

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run server

```bash
uvicorn main:app --reload
```
Backend runs at: http://localhost:8000

---

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: http://localhost:3000

---

### API Health Check

```bash
GET /
```

Response:

```json
{"status": "ok"}
```