# backend/main.py

import os
from dotenv import load_dotenv

load_dotenv()  # Must run before any module that reads DATABASE_URL

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.models.database import engine, Base
import backend.models.orm  # Registers all ORM mappings with Base

Base.metadata.create_all(bind=engine)  # Creates tables if they don't exist

# Import all routers
from backend.routers import (
    auth,
    submissions,
    compliance,
    findings,
    queue,
    reports,
)
from backend.services.llm import check_llm_available
from backend.services.ingest import check_coverage


# ── Startup / shutdown ────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup checks
    print("\n=== NGO Compliance Verification System ===")
    print("Starting up...\n")

    llm = check_llm_available()
    if llm["available"]:
        print(f"[OK] LLM online: {llm['model']}")
    else:
        print(f"[WARN] LLM unavailable: {llm.get('error')}")
        print("       Run: ollama serve")

    # Quick corpus coverage check
    for state in ["maharashtra", "delhi", "karnataka", "rajasthan"]:
        missing = check_coverage(state)
        if missing:
            print(f"[WARN] Corpus gap ({state}): {len(missing)} files missing")
        else:
            print(f"[OK] Corpus: {state} fully covered")

    print("\nReady. API docs at http://localhost:8000/docs\n")
    yield
    print("Shutting down.")


# ── App ───────────────────────────────────────────────────────────

app = FastAPI(
    title="NGO Compliance Verification System",
    description="AI-assisted document compliance verification · NITI Aayog Pilot",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routers ──────────────────────────────────────────────

app.include_router(auth.router,        prefix="/auth",        tags=["auth"])
app.include_router(submissions.router, prefix="/submissions",  tags=["submissions"])
app.include_router(compliance.router,  prefix="/submissions",  tags=["compliance"])
app.include_router(findings.router,    prefix="/submissions",  tags=["findings"])
app.include_router(reports.router,     prefix="/submissions",  tags=["reports"])
app.include_router(queue.router,       prefix="/queue",        tags=["queue"])


# ── Health endpoint ───────────────────────────────────────────────

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "NGO Compliance Verification System",
        "version": "0.1.0",
    }


# ── Run directly ──────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)