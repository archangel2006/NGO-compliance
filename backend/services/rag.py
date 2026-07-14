import os
import chromadb
import ollama
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv
import httpx

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

# --- Ollama client with explicit timeout so generate/embeddings never hang ---
# LLM_TIMEOUT: 5 min default — Mistral 7B on a large legal prompt can take 2-5 min
# on CPU-only or low-VRAM machines. Set OLLAMA_TIMEOUT in .env to override.
LLM_TIMEOUT  = int(os.getenv("OLLAMA_TIMEOUT", "300"))
_ollama = ollama.Client(
    host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
    timeout=httpx.Timeout(LLM_TIMEOUT, connect=10.0),
)
print(f"[RAG] Ollama client ready — model: {LLM_MODEL}, timeout: {LLM_TIMEOUT}s")

chroma_client = chromadb.PersistentClient(path=str(VECTORSTORE))

# ── Dynamic Dimension Checks & Auto-recovery ──
existing_dim = None
current_dim = None
rebuilt = False

# 1. Determine dimension of the current embedding model
try:
    test_embedding = _ollama.embeddings(model=EMBED_MODEL, prompt="test")["embedding"]
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
# evidence_fields  : only fields actually emitted by extraction.py + document_templates.py.
# dimension_consistency_keys : which top-level consistency categories are relevant
#                              to this dimension (used to filter the issues list).
DIMENSIONS = [
    {
        "id":    "registration",
        "name":  "Registration & Legal Status",
        "query": "NGO registration requirements valid registration certificate {entity_type} {state}",
        # Fields produced by registration_certificate template + ner from trust_deed
        "evidence_fields": [
            "registration_number",
            "registering_authority",
            "act_registered_under",
            "date_of_registration",
            "state_of_registration",
        ],
        "dimension_consistency_keys": ["org_name", "registration_number", "date_of_registration"],
        "weight": 0.20,
    },
    {
        "id":    "governance",
        "name":  "Governance Structure",
        "query": "board of trustees governing body composition quorum {entity_type} {state}",
        # Fields produced by trust_deed template + NER (trustee_names, trustee_count).
        # office_bearers is listed in ner_fields but _ner_extract never writes it — omitted.
        "evidence_fields": [
            "trustee_names",
            "trustee_count",
            "quorum",
            "non_profit_clause_present",
            "dissolution_clause_present",
        ],
        "dimension_consistency_keys": ["org_name"],
        "weight": 0.15,
    },
    {
        "id":    "membership",
        "name":  "Membership Requirements",
        "query": "minimum number of members trustees {entity_type} {state} registration",
        # trustee_count + trustee_names come from NER on trust_deed
        "evidence_fields": [
            "trustee_count",
            "trustee_names",
        ],
        # trustee_count has only one source key in the merged dict — no consistency check possible
        "dimension_consistency_keys": [],
        "weight": 0.10,
    },
    {
        "id":    "financial",
        "name":  "Financial Compliance",
        "query": "fund utilisation statement accounts grants receipts {state}",
        # Fields produced by annual_report template + _derive_booleans
        "evidence_fields": [
            "financial_year",
            "total_receipts",
            "total_expenditure",
            "csr_grant_present",
            "govt_grant_present",
            "fund_utilisation_present",
        ],
        "dimension_consistency_keys": ["org_name"],
        "weight": 0.20,
    },
    {
        "id":    "tax",
        "name":  "Tax Compliance (12A/80G)",
        "query": "12A 12AB 80G income tax exemption certificate charitable organisation",
        # cert_12a_number, cert_80g_number from certificate_12a / certificate_80g templates.
        # valid_from / valid_until are GENERIC fields shared across 12A, 80G, and FCRA docs;
        # the extractor currently merges them into one key — whichever document is processed
        # last wins. This is an extractor limitation.
        # TODO: split into cert_12a_valid_until / cert_80g_valid_until in document_templates.py
        "evidence_fields": [
            "cert_12a_number",
            "cert_80g_number",
            "valid_from",
            "valid_until",
            "pan",
        ],
        # pan/cert numbers each appear under only one merged-dict key — no consistency check possible
        "dimension_consistency_keys": [],
        "weight": 0.15,
    },
    {
        "id":    "fcra",
        "name":  "FCRA Compliance",
        "query": "FCRA registration foreign contribution designated bank account annual return FC-4",
        # Fields produced by fcra_certificate template + _derive_booleans
        # valid_until here refers to FCRA certificate expiry (same extractor limitation as above)
        # TODO: split valid_until into fcra_valid_until in document_templates.py
        "evidence_fields": [
            "fcra_reg_number",
            "valid_until",
            "bank_account",
            "bank_name",
            "bank_branch",
            "sbi_designated_account",
        ],
        # fcra_reg_number and bank_account have only one source key — no consistency check possible
        "dimension_consistency_keys": ["org_name"],
        "weight": 0.10,
    },
    {
        "id":    "audit",
        "name":  "Audit Requirements",
        "query": "audited financial statements chartered accountant FCRA Rule 17 separate audit",
        # Fields produced by audit_report template + _derive_booleans
        "evidence_fields": [
            "auditor_name",
            "auditor_icai",
            "audit_period",
            "fcra_audit_present",
        ],
        # auditor_name and auditor_icai appear in only one document type — no consistency check possible
        "dimension_consistency_keys": [],
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
    Returns (chunks: list[str], metadatas: list[dict]).
    The caller selects the top chunk (index 0) for the prompt.
    """
    query_embedding = _ollama.embeddings(
        model=EMBED_MODEL, prompt=query
    )["embedding"]

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

    if not results["documents"] or not results["documents"][0]:
        print(f"[RAG] No chunks retrieved for state='{state}' — query: {query[:80]}")
        return [], []

    chunks  = results["documents"][0]
    metas   = results["metadatas"][0]
    print(f"[RAG] Retrieved {len(chunks)} chunks for state='{state}'")
    return chunks, metas


def build_prompt(dimension: dict, top_chunk: str, ngo_evidence: str,
                 state: str, entity_type: str,
                 consistency_issues: list | None = None) -> str:
    """
    Build a focused, evidence-disciplined prompt for one compliance dimension.
    Uses the single highest-ranked retrieved legal chunk.
    Injects only the consistency issues relevant to this dimension.
    """
    consistency_block = ""
    if consistency_issues:
        issue_lines = "\n".join(f"- {issue}" for issue in consistency_issues)
        consistency_block = f"""

CROSS-DOCUMENT CONSISTENCY ISSUES (treat each as automatic FAIL for affected fields):
{issue_lines}"""

    return f"""You are a senior legal compliance officer reviewing NGO documents for India.

STATE: {state} | ENTITY TYPE: {entity_type}
COMPLIANCE DIMENSION: {dimension['name']}

LEGAL PROVISION:
{top_chunk}

NGO EVIDENCE:
{ngo_evidence}{consistency_block}

TASK: Assess whether the NGO satisfies the {dimension['name']} requirement.

Rules:
- PASS: evidence is present and clearly satisfies the legal provision.
- FAIL: evidence contradicts the provision; OR a consistency issue above affects this dimension.
- UNCERTAIN: evidence is absent or ambiguous. Do NOT assume compliance from missing data.
- Contradictory evidence always overrides supporting evidence.
- Apply only the legal requirements relevant to the stated ENTITY TYPE ({entity_type}).
  Do not apply Society Act rules to Trusts, or Trust rules to Section 8 companies.
- Cross-document inconsistencies listed above automatically cause FAIL for the affected requirement.
- Base reasoning only on the evidence and provision shown. Do not invent or assume values.
- Keep reasoning concise and specific (1-3 sentences referencing actual field values).

Return ONLY valid JSON, no other text:
{{
  "status": "PASS" or "FAIL" or "UNCERTAIN",
  "legal_citation": "exact act name and section from the provision above",
  "ngo_evidence": "the specific field and value that determined the verdict",
  "reasoning": "concise explanation referencing specific field values"
}}"""


# ── Cross-document consistency validator ─────────────────────────

# Maps a canonical label to the distinct extraction-dict keys that all hold
# the SAME logical value but come from different document types.
# A group must have at least 2 keys to be capable of detecting a mismatch.
#
# Single-key groups (e.g. "pan": ["pan"]) are excluded: even though `pan`
# appears in multiple document templates, extract_all() merges all docs into
# one dict and the first non-None value wins — so there is never more than
# one value per key to compare.
_CONSISTENCY_FIELDS: dict = {
    # org_name appears under three distinct keys across different document types:
    #   trust_deed regex  -> "org_name"
    #   spaCy NER         -> "ner_org_name"
    #   pan_card regex    -> "org_name_pan"
    # These can genuinely diverge and be compared.
    "org_name": ["org_name", "ner_org_name", "org_name_pan"],
}


def check_consistency(ngo_json: dict) -> dict:
    """
    Detect cross-document field contradictions in the merged extraction dict.

    Returns a dict mapping canonical_label -> list[str] of issue strings.
    The outer dict is keyed so that each dimension can cheaply filter only its own issues.
    Example: {"org_name": ["org_name inconsistent: 'ABC Trust' (org_name) vs 'ABC Foundation' (org_name_pan)."]}
    """
    all_issues: dict = {canonical: [] for canonical in _CONSISTENCY_FIELDS}

    def _norm(s: str) -> str:
        return " ".join(s.lower().split())

    for canonical, keys in _CONSISTENCY_FIELDS.items():
        # Collect all non-None, non-empty values for this logical field
        seen: list[tuple[str, str]] = []   # [(key, raw_value), ...]
        for k in keys:
            v = ngo_json.get(k)
            if v and str(v).strip():
                seen.append((k, str(v).strip()))

        if len(seen) < 2:
            continue   # only one source — nothing to compare

        base_key, base_val = seen[0]
        for other_key, other_val in seen[1:]:
            if _norm(base_val) != _norm(other_val):
                all_issues[canonical].append(
                    f"{canonical} inconsistent: "
                    f"'{base_val}' ({base_key}) vs '{other_val}' ({other_key})."
                )

    return all_issues


def _filter_consistency_issues(all_issues: dict, dimension: dict) -> list:
    """
    Return only the consistency issue strings relevant to the given dimension.
    Each dimension declares which canonical keys it cares about via
    `dimension_consistency_keys`.
    """
    relevant_keys = dimension.get("dimension_consistency_keys", [])
    filtered = []
    for key in relevant_keys:
        filtered.extend(all_issues.get(key, []))
    return filtered


def validate_citation(citation: str, state: str,
                       chunk_meta: Optional[dict] = None) -> bool:
    """
    Check if the cited section actually exists in ChromaDB corpus.
    Prevents hallucinated citations from reaching the report.

    chunk_meta: optional metadata dict of the chunk used to build the prompt.
    If the LLM's citation matches this chunk's act_name, we validate immediately
    without an extra ChromaDB round-trip.
    """
    if not citation or len(citation) < 5:
        return False

    citation_lower = citation.lower()

    # Fast path: check against the chunk we actually fed to the model
    if chunk_meta:
        act = chunk_meta.get("act_name", "").lower()
        section = chunk_meta.get("section_ref", "").lower()
        if act and act in citation_lower:
            print(f"[RAG] Citation validated via prompt chunk: '{act}'")
            return True
        if section and section in citation_lower:
            print(f"[RAG] Citation validated via prompt chunk section: '{section}'")
            return True

    # Slow path: embed and search corpus
    try:
        citation_embedding = _ollama.embeddings(
            model=EMBED_MODEL,
            prompt=citation
        )["embedding"]
    except Exception as e:
        print(f"[RAG] Citation embedding failed: {e}")
        return False

    results = collection.query(
        query_embeddings=[citation_embedding],
        n_results=3,
        where={
            "$or": [
                {"state": state},
                {"state": "all"},
            ]
        }
    )

    if not results["documents"] or not results["documents"][0]:
        return False

    for meta in results["metadatas"][0]:
        act     = meta.get("act_name", "").lower()
        section = meta.get("section_ref", "").lower()
        if act and act in citation_lower:
            return True
        if section and section in citation_lower:
            return True

    return False


def assess_dimension(dimension: dict, ngo_json: dict,
                     state: str, entity_type: str,
                     consistency_issues: list | None = None) -> Finding:
    """
    Run full RAG + LLM assessment for one compliance dimension.
    Uses the top-1 retrieved legal chunk and a focused, compact prompt.
    Pre-detected cross-document consistency issues are injected into the prompt.
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

    # 2. Retrieve top-1 legal chunk
    chunks, metas = retrieve_legal_context(query, canonical_state)

    # 3. Handle corpus gap
    if not chunks:
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

    top_chunk = chunks[0]
    top_meta  = metas[0] if metas else {}

    # 4. Build evidence string from fields the extractor actually produces
    ngo_evidence = extract_evidence(ngo_json, dimension["evidence_fields"])

    # 5. Build focused prompt (with optional consistency issues)
    prompt = build_prompt(
        dimension, top_chunk, ngo_evidence,
        canonical_state, entity_type,
        consistency_issues=consistency_issues,
    )

    print(f"[RAG] Calling Ollama LLM for dimension '{dimension['id']}' "
          f"(model={LLM_MODEL}, prompt={len(prompt)} chars, timeout={LLM_TIMEOUT}s)...")
    try:
        resp = _ollama.generate(
            model=LLM_MODEL,
            prompt=prompt,
            stream=False,
            options={"temperature": 0.1},
        )
        raw = resp.response if hasattr(resp, "response") else resp["response"]
        print(f"[RAG] LLM responded for '{dimension['id']}' - {len(raw)} chars")
    except httpx.TimeoutException:
        print(f"[RAG] TIMEOUT for '{dimension['id']}' after {LLM_TIMEOUT}s.")
        return Finding(
            dimension_id=dimension["id"],
            dimension_name=dimension["name"],
            status="UNCERTAIN",
            confidence=0.0,
            legal_citation="",
            ngo_evidence=ngo_evidence,
            reasoning=f"LLM timed out after {LLM_TIMEOUT}s.",
            routing="human_review",
            citation_valid=False,
            raw_llm_output=None,
        )
    except Exception as llm_err:
        print(f"[RAG] ERROR for '{dimension['id']}': {llm_err}")
        return Finding(
            dimension_id=dimension["id"],
            dimension_name=dimension["name"],
            status="UNCERTAIN",
            confidence=0.0,
            legal_citation="",
            ngo_evidence=ngo_evidence,
            reasoning=f"LLM call failed: {llm_err}",
            routing="human_review",
            citation_valid=False,
            raw_llm_output=None,
        )

    # 6. Parse JSON output — confidence field is intentionally ignored below
    result = safe_parse_json(raw)

    llm_status = result.get("status", "UNCERTAIN")
    reasoning  = result.get("reasoning", "")
    evidence   = result.get("ngo_evidence", ngo_evidence)

    # 7. Validate citation — fast path checks the chunk we actually fed to the model
    citation       = result.get("legal_citation", "")
    citation_valid = validate_citation(citation, canonical_state, chunk_meta=top_meta)

    # 8. Downgrade if citation cannot be verified
    if not citation_valid and llm_status in ("PASS", "FAIL"):
        llm_status = "UNCERTAIN"
        reasoning  = "[Citation unverified] " + reasoning

    # 9. Deterministic confidence — no LLM self-report used.
    #    PASS/FAIL with verified citation -> high confidence.
    #    UNCERTAIN (missing evidence) -> low confidence.
    #    UNCERTAIN (parse error/fallback) -> very low confidence.
    if llm_status in ("PASS", "FAIL") and citation_valid:
        confidence = 0.90
    elif llm_status == "CORPUS_GAP":
        confidence = 0.00
    elif "could not be parsed" in reasoning:
        confidence = 0.10   # JSON parse failure
    elif ngo_evidence == "No relevant fields extracted.":
        confidence = 0.30   # evidence genuinely absent
    else:
        confidence = 0.50   # ambiguous / citation not verified

    # 10. Deterministic routing — based on system state, not confidence score.
    #     PASS or FAIL with a verified citation goes directly to report.
    #     Everything else goes to human review.
    if llm_status == "CORPUS_GAP":
        routing = "corpus_alert"
    elif llm_status in ("PASS", "FAIL") and citation_valid:
        routing = "auto_report"
    else:
        routing = "human_review"

    return Finding(
        dimension_id=dimension["id"],
        dimension_name=dimension["name"],
        status=llm_status,
        confidence=confidence,
        legal_citation=citation,
        ngo_evidence=evidence,
        reasoning=reasoning,
        routing=routing,
        citation_valid=citation_valid,
        raw_llm_output=raw,
    )


def run_full_assessment(ngo_json: dict, state: str, entity_type: str) -> list:
    """
    Run all 7 dimensions. Returns list of Finding objects.
    Cross-document consistency is checked once upfront.
    Each dimension receives only the consistency issues relevant to it.
    """
    # Run cross-document consistency check once for all dimensions
    all_consistency = check_consistency(ngo_json)
    total_issues = sum(len(v) for v in all_consistency.values())
    if total_issues:
        print(f"[RAG] Consistency issues detected ({total_issues} total):")
        for key, issues in all_consistency.items():
            for issue in issues:
                print(f"  - {issue}")
    else:
        print("[RAG] No cross-document consistency issues detected.")

    findings = []
    for dim in DIMENSIONS:
        print(f"  Assessing: {dim['name']}...")
        # Filter to only issues relevant to this dimension
        dim_issues = _filter_consistency_issues(all_consistency, dim)
        finding = assess_dimension(dim, ngo_json, state, entity_type,
                                   consistency_issues=dim_issues or None)
        findings.append(finding)
        print(f"  -> {finding.status} ({round(finding.confidence*100)}% conf) "
              f"[{finding.routing}]")
    return findings


# ── Helpers ───────────────────────────────────────────────────────

def extract_evidence(ngo_json: dict, fields: list) -> str:
    """Pull relevant fields from extracted NGO JSON for the prompt."""
    lines = []
    for field in fields:
        val = ngo_json.get(field)
        if val is not None and val != "":
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
    # Fallback: return UNCERTAIN.
    # Note: confidence is not read from this dict — assess_dimension() derives
    # it deterministically from status + citation_valid.
    return {
        "status": "UNCERTAIN",
        "legal_citation": "",
        "ngo_evidence": "",
        "reasoning": "LLM output could not be parsed as valid JSON.",
    }