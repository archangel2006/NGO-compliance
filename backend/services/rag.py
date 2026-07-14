import os
import chromadb
import ollama
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Resolve paths relative to the current file or environment variable
backend_dir = Path(__file__).parent.parent
load_dotenv(backend_dir / ".env")

env_vectorstore = os.getenv("VECTORSTORE_PATH")
if env_vectorstore:
    VECTORSTORE = (backend_dir / env_vectorstore).resolve()
else:
    VECTORSTORE = (backend_dir / "../vectorstore").resolve()

EMBED_MODEL  = os.getenv("EMBED_MODEL", "nomic-embed-text")
LLM_MODEL    = os.getenv("LLM_MODEL", "mistral")
COLLECTION   = "legal_corpus"

chroma_client = chromadb.PersistentClient(path=str(VECTORSTORE))

# ── Dynamic Dimension Checks & Auto-recovery ──
existing_dim = None
current_dim = None
rebuilt = False

# 1. Determine dimension of the current embedding model
try:
    test_embedding = ollama.embeddings(model=EMBED_MODEL, prompt="test")["embedding"]
    current_dim = len(test_embedding)
except Exception as e:
    print(f"[WARN] Failed to peek current embedding model dimension: {e}. Defaulting to 768.")
    current_dim = 768

# 2. Get/create collection and check stored dimension
try:
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION,
        metadata={"hnsw:space": "cosine"}
    )
    
    # Peek at the database to fetch one document's embedding
    peek_result = collection.peek(limit=1)
    if peek_result and peek_result.get("embeddings") is not None and len(peek_result["embeddings"]) > 0:
        existing_dim = len(peek_result["embeddings"][0])
except Exception as e:
    print(f"[WARN] Failed to read existing database dimension: {e}")
    existing_dim = None

# 3. Check for mismatches and auto-rebuild if dimensions differ
if existing_dim is not None and current_dim is not None and existing_dim != current_dim:
    print("\n" + "=" * 50)
    print("WARNING: EMBEDDING DIMENSION MISMATCH DETECTED")
    print(f"  Existing collection dimension: {existing_dim}")
    print(f"  Configured model '{EMBED_MODEL}' dimension: {current_dim}")
    print("Rebuilding collection to prevent query errors...")
    print("=" * 50 + "\n")
    
    try:
        chroma_client.delete_collection(COLLECTION)
        collection = chroma_client.get_or_create_collection(
            name=COLLECTION,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Trigger ingestion
        from backend.services.ingest import ingest_all
        ingest_all()
        rebuilt = True
    except Exception as err:
        print(f"[ERROR] Failed to rebuild vector database: {err}")
        # Re-raise so backend doesn't run with corrupted DB
        raise err
else:
    rebuilt = False

# 4. Mandatory Log Output
print("\n=== ChromaDB Embedding Initialization ===")
print(f"Embedding model: {EMBED_MODEL}")
print(f"Embedding dimension: {current_dim}")
if existing_dim is not None:
    print(f"Existing collection dimension: {existing_dim}")
if rebuilt:
    print("Status: Collection was rebuilt due to dimension mismatch.")
else:
    print("Status: Using existing vector database (dimensions match).")
print("==========================================\n")

# ── Compliance dimensions ─────────────────────────────────────────
DIMENSIONS = [
    {
        "id":    "registration",
        "name":  "Registration & Legal Status",
        "query": "NGO registration requirements valid registration certificate {entity_type} {state}",
        "evidence_fields": ["registration_number", "registering_authority",
                            "act_registered_under", "date_of_registration"],
        "weight": 0.20,
    },
    {
        "id":    "governance",
        "name":  "Governance Structure",
        "query": "board of trustees governing body composition quorum {entity_type} {state}",
        "evidence_fields": ["trustee_names", "office_bearers",
                            "governing_body_size", "quorum_clause"],
        "weight": 0.15,
    },
    {
        "id":    "membership",
        "name":  "Membership Requirements",
        "query": "minimum number of members trustees {entity_type} {state} registration",
        "evidence_fields": ["member_count", "trustee_count", "member_names"],
        "weight": 0.10,
    },
    {
        "id":    "financial",
        "name":  "Financial Compliance",
        "query": "fund utilisation statement accounts grants receipts {state}",
        "evidence_fields": ["annual_report_year", "csr_grants",
                            "govt_grants", "fund_utilisation_present"],
        "weight": 0.20,
    },
    {
        "id":    "tax",
        "name":  "Tax Compliance (12A/80G)",
        "query": "12A 12AB 80G income tax exemption certificate charitable organisation",
        "evidence_fields": ["cert_12a_number", "cert_12a_expiry",
                            "cert_80g_number", "cert_80g_expiry", "pan"],
        "weight": 0.15,
    },
    {
        "id":    "fcra",
        "name":  "FCRA Compliance",
        "query": "FCRA registration foreign contribution designated bank account annual return FC-4",
        "evidence_fields": ["fcra_reg_number", "fcra_expiry",
                            "fcra_bank_account", "fc4_filed"],
        "weight": 0.10,
    },
    {
        "id":    "audit",
        "name":  "Audit Requirements",
        "query": "audited financial statements chartered accountant FCRA Rule 17 separate audit",
        "evidence_fields": ["auditor_name", "auditor_icai",
                            "audit_period", "fcra_audit_present"],
        "weight": 0.10,
    },
]


@dataclass
class Finding:
    dimension_id:     str
    dimension_name:   str
    status:           str   # PASS | FAIL | UNCERTAIN | CORPUS_GAP
    confidence:       float
    legal_citation:   str
    ngo_evidence:     str
    reasoning:        str
    routing:          str   # auto_report | human_review | corpus_alert
    citation_valid:   bool = True
    raw_llm_output:   Optional[str] = None


def retrieve_legal_context(query: str, state: str, n_results: int = 5) -> tuple:
    """
    Query ChromaDB for relevant legal provisions.
    Returns (combined_text, list_of_citations).
    """
    query_embedding = ollama.embeddings(
        model=EMBED_MODEL, prompt=query
    )["embedding"]

    # Debug info requested by user
    total_count = collection.count()
    
    # Raw query without filters to inspect what's available
    raw_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    raw_docs_count = len(raw_results["documents"][0]) if raw_results["documents"] else 0
    
    # Query with state filter
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where={
            "$or": [
                {"state": state},
                {"state": "all"},
            ]
        },
    )
    filtered_docs_count = len(results["documents"][0]) if results["documents"] else 0

    print(f"\n===== RAG Retrieval Debug =====")
    print(f"Query: {query}")
    print(f"State Input: {state}")
    print(f"Embedding dimension: {len(query_embedding)}")
    print(f"Collection count: {total_count}")
    print(f"Raw retrieved docs (no filter): {raw_docs_count}")
    if raw_docs_count > 0:
        raw_states = [m.get("state") for m in raw_results["metadatas"][0]]
        print(f"Raw doc states: {raw_states}")
    print(f"After state filter: {filtered_docs_count}")
    
    combined = "\n\n---\n\n".join(results["documents"][0]) if filtered_docs_count > 0 else ""
    print(f"Final legal context length: {len(combined)} chars")
    if not combined.strip():
        print(f"REASON WHY EMPTY: No documents matched state='{state}' or state='all'. Stored metadata states are likely different.")
    print("================================\n")

    if not results["documents"] or not results["documents"][0]:
        return "", []

    docs      = results["documents"][0]
    metas     = results["metadatas"][0]
    citations = [
        f"{m.get('act_name', 'Unknown Act')} · {m.get('section_ref', '')}"
        for m in metas
    ]

    combined = "\n\n---\n\n".join(docs)
    return combined, citations


def build_prompt(dimension: dict, legal_context: str,
                 ngo_evidence: str, state: str, entity_type: str) -> str:
    return f"""You are a legal compliance officer reviewing NGO registration documents for India.

COMPLIANCE DIMENSION: {dimension['name']}
STATE: {state} | ENTITY TYPE: {entity_type}

LEGAL PROVISIONS RETRIEVED:
{legal_context}

NGO DOCUMENT EVIDENCE:
{ngo_evidence}

TASK: Assess whether this NGO satisfies the {dimension['name']} requirement based strictly on the legal provisions and evidence above.

Rules:
- Use ONLY the legal text provided above. Do not invent or assume any legal requirements.
- If the evidence is ambiguous or incomplete, use UNCERTAIN.
- If evidence clearly satisfies the law, use PASS.
- If evidence clearly violates or is missing key requirements, use FAIL.
- Keep reasoning to 2-3 sentences maximum.

Return ONLY a valid JSON object, no other text:
{{
  "status": "PASS" or "FAIL" or "UNCERTAIN",
  "confidence": 0.0 to 1.0,
  "legal_citation": "exact act name and section that applies",
  "ngo_evidence": "specific text or field from NGO documents that you assessed",
  "reasoning": "2-3 sentence explanation"
}}"""


def validate_citation(citation: str, state: str) -> bool:
    """
    Check if the cited section actually exists in ChromaDB corpus.
    Prevents hallucinated citations from reaching the report.
    """
    if not citation or len(citation) < 5:
        return False

    # Search for the exact citation text
    citation_embedding = ollama.embeddings(
        model=EMBED_MODEL,
        prompt=citation
    )["embedding"]

    results = collection.query(
        query_embeddings=[citation_embedding],
        n_results=3,
        where={
            "$or":[
                {"state":state},
                {"state":"all"}
            ]
        }
    )

    if not results["documents"] or not results["documents"][0]:
        return False

    # citation in any retrieved chunk
    citation_lower = citation.lower()

    for meta in results["metadatas"][0]:
        act = meta.get("act_name", "").lower()
        section = meta.get("section_ref", "").lower()

        if act and act in citation_lower:
            return True

        if section and section in citation_lower:
            return True

        return False


def assess_dimension(dimension: dict, ngo_json: dict,
                     state: str, entity_type: str) -> Finding:
    """
    Run full RAG + LLM assessment for one compliance dimension.
    """
    STATE_MAP = {
        "dl": "delhi",
        "mh": "maharashtra",
        "ka": "karnataka",
        "rj": "rajasthan"
    }
    canonical_state = STATE_MAP.get(state.lower(), state.lower())

    # 1. Build retrieval query
    query = dimension["query"].format(
        state=canonical_state, entity_type=entity_type
    )

    # 2. Retrieve legal context
    legal_context, retrieved_citations = retrieve_legal_context(query, canonical_state)

    # 3. Handle corpus gap
    if not legal_context.strip():
        return Finding(
            dimension_id=dimension["id"],
            dimension_name=dimension["name"],
            status="CORPUS_GAP",
            confidence=0.0,
            legal_citation="",
            ngo_evidence="",
            reasoning=f"No legal provisions found for {dimension['name']} "
                      f"in {canonical_state}. Add the relevant Act to the corpus.",
            routing="corpus_alert",
            citation_valid=False,
        )

    # 4. Extract relevant NGO evidence fields
    ngo_evidence = extract_evidence(ngo_json, dimension["evidence_fields"])

    # 5. Call LLM
    prompt = build_prompt(dimension, legal_context, ngo_evidence,
                          canonical_state, entity_type)

    raw = ollama.generate(
        model=LLM_MODEL,
        prompt=prompt,
        options={"temperature": 0.1}   # low temp for legal reasoning
    )["response"]

    # 6. Parse JSON output
    result = safe_parse_json(raw)

    # 7. Validate citation
    citation = result.get("legal_citation", "")
    citation_valid = validate_citation(citation, canonical_state)

    if not citation_valid and result.get("status") in ("PASS", "FAIL"):
        result["status"] = "UNCERTAIN"
        result["confidence"] = min(result.get("confidence", 0.5), 0.5)

    # 8. Determine routing
    status     = result.get("status", "UNCERTAIN")
    confidence = result.get("confidence", 0.0)

    if status == "CORPUS_GAP":
        routing = "corpus_alert"
    elif status in ("PASS", "FAIL") and confidence >= 0.85 and citation_valid:
        routing = "auto_report"
    else:
        routing = "human_review"

    return Finding(
        dimension_id=dimension["id"],
        dimension_name=dimension["name"],
        status=status,
        confidence=confidence,
        legal_citation=citation,
        ngo_evidence=result.get("ngo_evidence", ngo_evidence),
        reasoning=result.get("reasoning", ""),
        routing=routing,
        citation_valid=citation_valid,
        raw_llm_output=raw,
    )


def run_full_assessment(ngo_json: dict, state: str, entity_type: str) -> list:
    """
    Run all 7 dimensions. Returns list of Finding objects.
    Can be parallelised with asyncio later.
    """
    findings = []
    for dim in DIMENSIONS:
        print(f"  Assessing: {dim['name']}...")
        finding = assess_dimension(dim, ngo_json, state, entity_type)
        findings.append(finding)
        print(f"  → {finding.status} ({round(finding.confidence*100)}% conf) "
              f"[{finding.routing}]")
    return findings


# ── Helpers ───────────────────────────────────────────────────────

def extract_evidence(ngo_json: dict, fields: list) -> str:
    """Pull relevant fields from extracted NGO JSON for the prompt."""
    lines = []
    for field in fields:
        val = ngo_json.get(field)
        if val:
            lines.append(f"- {field}: {val}")
    return "\n".join(lines) if lines else "No relevant fields extracted."


def safe_parse_json(raw: str) -> dict:
    """Safely parse LLM output, handle markdown code fences."""
    import re
    # Strip markdown code blocks if present
    cleaned = re.sub(r'```(?:json)?', '', raw).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to find JSON object in the response
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    # Fallback: return UNCERTAIN
    return {
        "status": "UNCERTAIN",
        "confidence": 0.3,
        "legal_citation": "",
        "ngo_evidence": "",
        "reasoning": "LLM output could not be parsed as valid JSON.",
    }