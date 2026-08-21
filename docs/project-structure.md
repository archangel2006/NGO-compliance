

```bash

ngo-compliance/
│
├── frontend/
│
├── backend/
│   ├── main.py
│   ├── .env
│   ├── requirements.txt
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── submissions.py
│   │   ├── compliance.py
│   │   ├── findings.py
│   │   ├── queue.py
│   │   └── reports.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ocr.py
│   │   ├── preprocessing.py
│   │   ├── extraction.py
│   │   ├── document_templates.py
│   │   ├── ingest.py
│   │   ├── rag.py
│   │   ├── llm.py
│   │   ├── citation_validator.py
│   │   ├── scoring.py
│   │   └── router.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── schemas.py
│   └── utils/
│       ├── __init__.py
│       └── chunker.py
│
├── legal-corpus/
│   ├── corpus_config.py             
│   ├── central/
│   │   ├── fcra/
│   │   ├── income_tax/
│   │   └── darpan/
│   ├── maharashtra/
│   ├── delhi/
│   ├── karnataka/
│   └── rajasthan/
│
├── corpus_metadata/                 ← auto-generated JSONs
│
├── vectorstore/                     ← ChromaDB auto-generated
│
├── uploads/                         ← NGO uploaded docs
│   └── {submission_id}/
│
├── reports/                         ← generated PDF reports
│
└── docker-compose.yml



```