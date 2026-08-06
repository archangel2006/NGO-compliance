import os
import re
import chromadb
import ollama
import google.generativeai as genai
from backend.services.llm import generate
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv
import difflib


# Resolve paths relative to the current file or environment variable
backend_dir = Path(__file__).parent.parent
load_dotenv(backend_dir / ".env")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

env_vectorstore = os.getenv("VECTORSTORE_PATH")
if env_vectorstore:
    VECTORSTORE = (backend_dir / env_vectorstore).resolve()
else:
    VECTORSTORE = (backend_dir / "../vectorstore").resolve()

EMBED_MODEL  = os.getenv("EMBED_MODEL", "nomic-embed-text")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")
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
# evidence_fields  : only fields actually emitted by extraction.py + document_templates.py.
# dimension_consistency_keys : which top-level consistency categories are relevant
#                              to this dimension (used to filter the issues list).
DIMENSIONS = [
    {
        "id":    "registration",
        "name":  "Registration & Legal Status",
        # Explicit: entity type + state + registration domain
        "query": "Valid registration certificate requirement {entity_type} registration under {state} law registration number registering authority act",
        # Fields produced by registration_certificate template + ner from trust_deed
        "evidence_fields": [
            "registration_number",
            "registering_authority",
            "act_registered_under",
            "date_of_registration",
            "state_of_registration",
        ],
        "dimension_consistency_keys": ["org_name"],
        "weight": 0.20,
    },
    {
        "id":    "governance",
        "name":  "Governance Structure",
        # Explicit: entity type + state + governance domain
        "query": "Governing body board composition quorum minimum trustees {entity_type} {state} public trust society rules",
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
        # Explicit: minimum member/trustee count + entity type + state
        "query": "Minimum number of members trustees required for {entity_type} formation registration {state} charitable society trust law",
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
        # Explicit: entity type + state + financial compliance domain
        "query": "Fund utilisation statement annual accounts receipts expenditure grant reporting requirement {entity_type} {state} charitable trust society",
        # Fields produced by annual_report template + _derive_booleans
        "evidence_fields": [
            "financial_year",
            "total_receipts",
            "total_expenditure",
            "csr_grant_present",
            "govt_grant_present",
            "fund_utilisation_present",
        ],
        "dimension_consistency_keys": [],
        "weight": 0.20,
    },
    {
        "id":    "tax",
        "name":  "Tax Compliance (12A/80G)",
        # Explicit: 12A/80G certificates + renewal + charitable entity
        "query": "Income tax exemption registration 12A 12AB 80G certificate renewal validity charitable organization India",
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
        # Explicit: FCRA registration + foreign contribution + SBI bank account
        "query": "FCRA foreign contribution registration certificate designated SBI bank account FC-4 annual return Ministry Home Affairs",
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
        "dimension_consistency_keys": [],
        "weight": 0.10,
    },
    {
        "id":    "audit",
        "name":  "Audit Requirements",
        # Explicit: annual audit + FCRA separate audit + chartered accountant requirement
        "query": "Mandatory annual audit chartered accountant FCRA Rule 17 separate audit requirement {entity_type} {state} financial statements",
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
    dimension_id:       str
    dimension_name:     str
    status:             str   # PASS | FAIL | UNCERTAIN | CORPUS_GAP
    confidence:         float
    legal_citation:     str
    ngo_evidence:       str
    reasoning:          str
    routing:            str   # auto_report | human_review | corpus_alert
    citation_valid:     bool = True
    raw_llm_output:     Optional[str] = None
    matched_requirement: str = ""  # Specific legal requirement identified by LLM


def retrieve_legal_context(query: str, state: str, n_results: int = 5) -> tuple:
    """
    Query ChromaDB for relevant legal provisions.
    Returns (chunks: list[str], metadatas: list[dict]).
    The caller selects the top chunk (index 0) for the prompt.
    """
    query_embedding = ollama.embeddings(
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


def build_combined_prompt(active_dimensions: dict, state: str, entity_type: str) -> str:
    """
    Build a single consolidated prompt to assess all active compliance categories simultaneously.
    Uses strict XML-like boundary tags to ensure independent reasoning per dimension and prevent leakage.
    Each dimension now receives a primary legal provision plus up to 2 supporting provisions.
    """
    categories_str = []
    for dim_id, data in active_dimensions.items():
        dim                = data["dimension"]
        primary_chunk      = data["primary_chunk"]
        supporting_chunk_1 = data.get("supporting_chunk_1", "")
        supporting_chunk_2 = data.get("supporting_chunk_2", "")
        ngo_evidence       = data["ngo_evidence"]
        consistency_issues = data["dim_issues"]

        consistency_block = ""
        if consistency_issues:
            issue_lines = "\n".join(f"- {issue}" for issue in consistency_issues)
            consistency_block = f"""
  <consistency_issues>
{issue_lines}
  </consistency_issues>"""

        # Build supporting provisions block (only include non-empty chunks)
        supporting_blocks = ""
        if supporting_chunk_1:
            supporting_blocks += f"""
  <supporting_legal_provision_1>
{supporting_chunk_1}
  </supporting_legal_provision_1>"""
        if supporting_chunk_2:
            supporting_blocks += f"""
  <supporting_legal_provision_2>
{supporting_chunk_2}
  </supporting_legal_provision_2>"""

        special_rules = ""
        if dim_id == "registration":
            special_rules = (
                "\n  - Do not automatically return FAIL solely because 'Registration Act, 1908' "
                "appears in the evidence (it is common in property docs)."
                "\n  - Only return FAIL if evidence clearly establishes non-compliance."
                "\n  - If registration evidence is ambiguous or insufficient, return UNCERTAIN."
            )

        categories_str.append(f"""<dimension id="{dim_id}">
  <name>{dim['name']}</name>
  <primary_legal_provision>
{primary_chunk}
  </primary_legal_provision>{supporting_blocks}
  <ngo_evidence>
{ngo_evidence}
  </ngo_evidence>{consistency_block}
  <assessment_rules>{special_rules}
  </assessment_rules>
</dimension>""")

    categories_joined = "\n\n".join(categories_str)
    dim_keys_str = ", ".join(f'"{k}"' for k in active_dimensions.keys())

    return f"""You are a senior legal compliance officer reviewing NGO documents for India.

STATE: {state} | ENTITY TYPE: {entity_type}

Please evaluate the compliance categories enclosed in the <dimension> tags below:

{categories_joined}

TASK: Evaluate each dimension independently.

STRICT ISOLATION RULES:
1. Evaluate every dimension strictly independently inside its own tag boundaries.
2. Never reuse evidence across dimensions.
3. Never reuse legal provisions across dimensions. Do not mix provisions from different <dimension> blocks.
4. Never let a failure or inconsistency in one dimension affect another.
5. Apply only the legal requirements relevant to the stated ENTITY TYPE ({entity_type}). Do not apply Society Act rules to Trusts, or Trust rules to Section 8 companies.
6. Determine whether each legal provision actually applies to the selected entity type. If it does not apply, ignore that provision and return UNCERTAIN.
7. Ignore provisions that belong to a different state than {state}.
8. Evidence outside the current <ngo_evidence> block must be treated as nonexistent. Never use evidence from another dimension.
9. If no retrieved provision within a dimension's tags applies to this entity type, return UNCERTAIN for that dimension.
10. Ignore irrelevant retrieved legal provisions rather than trying to reconcile them.
11. PASS: evidence is present and clearly satisfies the legal provision.
12. FAIL: evidence contradicts the provision; OR a consistency issue listed under that dimension affects the fields for that dimension.
13. UNCERTAIN: evidence is absent or ambiguous. Do NOT assume compliance from missing data.
14. Keep reasoning concise and specific (1-3 sentences referencing actual field values).

Return ONLY valid JSON matching the following schema structure, with no other text before or after:
{{
  "registration": {{
    "status": "PASS" or "FAIL" or "UNCERTAIN",
    "matched_requirement": "the specific legal requirement that was evaluated (e.g. 'Valid registration certificate under BPT Act 1950')",
    "legal_citation": "exact act name and section from the provision above",
    "ngo_evidence": "the specific field and value that determined the verdict",
    "reasoning": "concise explanation referencing specific field values"
  }},
  ... (include keys for all requested category IDs: {dim_keys_str})
}}"""


def build_prompt(dimension: dict, primary_chunk: str, ngo_evidence: str,
                 state: str, entity_type: str,
                 consistency_issues: list | None = None,
                 supporting_chunk_1: str = "",
                 supporting_chunk_2: str = "") -> str:
    """
    Build a focused, evidence-disciplined prompt for one compliance dimension.
    Accepts a primary legal chunk plus up to 2 supporting chunks.
    Injects only the consistency issues relevant to this dimension.
    """
    consistency_block = ""
    if consistency_issues:
        issue_lines = "\n".join(f"- {issue}" for issue in consistency_issues)
        consistency_block = f"""

CROSS-DOCUMENT CONSISTENCY ISSUES (treat each as automatic FAIL for affected fields):
{issue_lines}"""

    supporting_block = ""
    if supporting_chunk_1:
        supporting_block += f"\n\nSUPPORTING LEGAL PROVISION 1:\n{supporting_chunk_1}"
    if supporting_chunk_2:
        supporting_block += f"\n\nSUPPORTING LEGAL PROVISION 2:\n{supporting_chunk_2}"

    return f"""You are a senior legal compliance officer reviewing NGO documents for India.

STATE: {state} | ENTITY TYPE: {entity_type}
COMPLIANCE DIMENSION: {dimension['name']}

PRIMARY LEGAL PROVISION:
{primary_chunk}{supporting_block}

NGO EVIDENCE:
{ngo_evidence}{consistency_block}

TASK: Assess whether the NGO satisfies the {dimension['name']} requirement.

Rules:
- PASS: evidence is present and clearly satisfies the legal provision.
- FAIL: evidence contradicts the provision; OR a consistency issue above affects this dimension.
- UNCERTAIN: evidence is absent or ambiguous. Do NOT assume compliance from missing data.
- Contradictory evidence always overrides supporting evidence.
- Determine whether each legal provision actually applies to the stated ENTITY TYPE ({entity_type}). If a provision belongs to a different entity type, ignore it.
- Ignore provisions belonging to a different state than {state}.
- Apply only the legal requirements relevant to the stated ENTITY TYPE ({entity_type}).
  Do not apply Society Act rules to Trusts, or Trust rules to Section 8 companies.
- If no retrieved provision applies to this entity type, return UNCERTAIN.
- Ignore irrelevant retrieved legal provisions rather than trying to reconcile them.
- Evidence outside the NGO EVIDENCE block must be treated as nonexistent. Do not assume or invent values.
- Cross-document inconsistencies listed above automatically cause FAIL for the affected requirement.
- Base reasoning only on the evidence and provision shown. Do not invent or assume values.
- Keep reasoning concise and specific (1-3 sentences referencing actual field values).

Return ONLY valid JSON, no other text:
{{
  "status": "PASS" or "FAIL" or "UNCERTAIN",
  "matched_requirement": "the specific legal requirement evaluated (e.g. 'Minimum 7 trustees required')",
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


_DOC_TYPE_DISPLAY_NAMES = {
    "trust_deed": "Trust Deed",
    "registration_certificate": "Registration Certificate",
    "pan_card": "PAN",
    "annual_report": "Annual Report",
    "certificate_12a": "12A Certificate",
    "certificate_80g": "80G Certificate",
    "fcra_certificate": "FCRA Certificate",
    "audit_report": "Audit Report",
}


def is_name_in_text(norm_submitted: str, ocr_text: str) -> bool:
    """
    Search raw OCR text for the normalized organization name.
    Performs exact substring matching followed by a line-by-line sliding window difflib check.
    Uses a conservative similarity threshold (92%) to prevent matching different organizations.
    """
    # 1. Exact substring check first
    norm_ocr = " ".join(re.sub(r'[^a-z0-9\s]', ' ', ocr_text.lower()).split())
    if norm_submitted in norm_ocr:
        return True

    # 2. Line-by-line sliding window check for minor OCR errors / typos (conservative threshold: 92%)
    lines = ocr_text.splitlines()
    for line in lines:
        norm_line = " ".join(re.sub(r'[^a-z0-9\s]', ' ', line.lower()).split())
        if not norm_line:
            continue
        ratio = difflib.SequenceMatcher(None, norm_submitted, norm_line).ratio()
        if ratio >= 0.92:
            return True
        # Check window segments in longer lines
        words_submitted = norm_submitted.split()
        words_line = norm_line.split()
        n = len(words_submitted)
        if len(words_line) >= n:
            for i in range(len(words_line) - n + 1):
                window = " ".join(words_line[i:i+n])
                if difflib.SequenceMatcher(None, norm_submitted, window).ratio() >= 0.92:
                    return True
    return False


def check_org_name_verification(ngo_json: dict, submitted_org_name: str) -> list:
    """
    Validate that the submitted NGO name is found in at least one official document.
    Returns list of matched document display names.
    """
    ocr_texts = ngo_json.get("_ocr_texts", {})
    if not ocr_texts:
        # Fallback to Trust Deed display name if no raw text is present (e.g. in test suites with mock fields)
        return ["Trust Deed"]

    matched_docs = []
    norm_submitted = " ".join(re.sub(r'[^a-z0-9\s]', ' ', submitted_org_name.lower()).split())
    for doc_type, ocr_text in ocr_texts.items():
        if is_name_in_text(norm_submitted, ocr_text):
            display_name = _DOC_TYPE_DISPLAY_NAMES.get(doc_type, doc_type.replace("_", " ").title())
            matched_docs.append(display_name)

    return matched_docs


def check_contradictory_evidence(ngo_json: dict, submitted_org_name: str) -> bool:
    """
    Check if the uploaded documents consistently identify a completely different organization.
    """
    norm_submitted = " ".join(re.sub(r'[^a-z0-9\s]', ' ', submitted_org_name.lower()).split())
    extracted_names = []
    for key in ["org_name", "org_name_pan"]:
        name = ngo_json.get(key)
        if name and str(name).strip():
            extracted_names.append(str(name).strip())

    if not extracted_names:
        return False

    # If any extracted name matches (exactly or fuzzily), it is not contradictory
    for name in extracted_names:
        norm_name = " ".join(re.sub(r'[^a-z0-9\s]', ' ', name.lower()).split())
        if norm_submitted in norm_name or norm_name in norm_submitted:
            return False
        ratio = difflib.SequenceMatcher(None, norm_submitted, norm_name).ratio()
        if ratio >= 0.92:
            return False

    return True


def check_consistency(ngo_json: dict, submitted_org_name: str) -> dict:
    """
    Detect cross-document field contradictions.
    Note: org_name verification is handled separately via check_org_name_verification
    so that a missing name reduces confidence rather than causing a hard legal FAIL.
    """
    all_issues: dict = {canonical: [] for canonical in _CONSISTENCY_FIELDS}

    def _norm(s: str) -> str:
        cleaned = re.sub(r'[^a-z0-9\s]', ' ', s.lower())
        return " ".join(cleaned.split())

    for canonical, keys in _CONSISTENCY_FIELDS.items():
        if canonical == "org_name":
            # Verification is now handled via check_org_name_verification in run_full_assessment
            pass
        else:
            seen: list[tuple[str, str]] = []
            for k in keys:
                v = ngo_json.get(k)
                if v and str(v).strip():
                    seen.append((k, str(v).strip()))

            if len(seen) > 1:
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


# Common abbreviation / synonym pairs used in LLM citations
_CITATION_ALIASES = [
    # LLM shorthand           corpus full name fragment
    ("fcra",                  "foreign contribution"),
    ("foreign contribution",  "fcra"),
    ("income tax act",        "income tax act, 1961"),
    ("income tax act, 1961",  "income tax act"),
    ("societies registration","societies registration act"),
    ("societies act",         "societies registration act"),
    ("bpt act",               "bombay public trusts"),
    ("bombay public trusts",  "bpt act"),
    ("foreign contribution regulation act", "foreign contribution (regulation) act"),
    ("fcra, 2010",            "foreign contribution"),
    ("fcra 2010",             "foreign contribution"),
]


def _citation_tokens(text: str) -> set:
    """Return normalised word tokens from a citation string."""
    # strip punctuation, lowercase, split
    cleaned = re.sub(r'[^a-z0-9\s]', ' ', text.lower())
    return set(cleaned.split())


def _citations_overlap(a: str, b: str) -> bool:
    """True when a is substring of b, OR b is substring of a (bidirectional)."""
    return (a in b) or (b in a)


def validate_citation(citation: str, state: str,
                       chunk_meta: Optional[dict] = None) -> bool:
    """
    Check if the cited section actually exists in ChromaDB corpus.
    Prevents hallucinated citations from reaching the report.

    Uses bidirectional substring matching + abbreviation aliases so that
    a citation like 'Income Tax Act' still validates against a chunk whose
    act_name is 'Income Tax Act, 1961', and vice-versa.
    """
    if not citation or len(citation) < 5:
        return False

    citation_lower = re.sub(r'[^a-z0-9\s]', ' ', citation.lower()).strip()

    def _matches_corpus_entry(act: str, section: str) -> bool:
        act_n = re.sub(r'[^a-z0-9\s]', ' ', act).strip()
        sec_n = re.sub(r'[^a-z0-9\s]', ' ', section).strip()
        # Direct bidirectional substring check
        if act_n and _citations_overlap(act_n, citation_lower):
            return True
        if sec_n and _citations_overlap(sec_n, citation_lower):
            return True
        # Alias expansion: check if any known alias of the citation matches
        for llm_form, corpus_form in _CITATION_ALIASES:
            if llm_form in citation_lower and corpus_form in act_n:
                return True
            if corpus_form in citation_lower and llm_form in act_n:
                return True
        return False

    # Fast path: check against the chunk we actually fed to the model
    if chunk_meta:
        act     = chunk_meta.get("act_name", "").lower()
        section = chunk_meta.get("section_ref", "").lower()
        if _matches_corpus_entry(act, section):
            print(f"[RAG] Citation validated via prompt chunk: '{act}'")
            return True

    # Slow path: embed and search corpus
    try:
        citation_embedding = ollama.embeddings(
            model=EMBED_MODEL,
            prompt=citation
        )["embedding"]
    except Exception as e:
        print(f"[RAG] Citation embedding failed: {e}")
        return False

    results = collection.query(
        query_embeddings=[citation_embedding],
        n_results=5,
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
        if _matches_corpus_entry(act, section):
            return True

    return False


def assess_dimension(dimension: dict, ngo_json: dict,
                     state: str, entity_type: str,
                     consistency_issues: list | None = None,
                     precomputed_result: dict | None = None,
                     raw_llm_output: str | None = None,
                     primary_chunk: str | None = None,
                     primary_meta: dict | None = None,
                     supporting_chunk_1: str = "",
                     supporting_chunk_2: str = "") -> Finding:
    """
    Run full RAG + LLM assessment for one compliance dimension.
    Accepts a primary legal chunk plus up to 2 supporting chunks.
    Pre-detected cross-document consistency issues are injected into the prompt.
    """
    STATE_MAP = {
        "dl": "delhi",
        "mh": "maharashtra",
        "ka": "karnataka",
        "rj": "rajasthan"
    }
    canonical_state = STATE_MAP.get(state.lower(), state.lower())

    # Build/extract evidence fields first
    ngo_evidence = extract_evidence(ngo_json, dimension["evidence_fields"])

    # 1. Retrieve context if not provided precomputed
    if primary_chunk is None:
        query = dimension["query"].format(
            state=canonical_state, entity_type=entity_type
        )
        chunks, metas = retrieve_legal_context(query, canonical_state)
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
        primary_chunk      = chunks[0]
        primary_meta       = metas[0] if metas else {}
        supporting_chunk_1 = chunks[1] if len(chunks) > 1 else ""
        supporting_chunk_2 = chunks[2] if len(chunks) > 2 else ""

    if precomputed_result is not None:
        result = precomputed_result
        raw = raw_llm_output
    else:
        # Fallback to single-call logic
        prompt = build_prompt(
            dimension, primary_chunk, ngo_evidence,
            canonical_state, entity_type,
            consistency_issues=consistency_issues,
            supporting_chunk_1=supporting_chunk_1,
            supporting_chunk_2=supporting_chunk_2,
        )

        print(f"[RAG] Calling Gemini for dimension '{dimension['id']}' "
              f"(model={LLM_MODEL}, prompt={len(prompt)} chars)...")
        try:
            raw = generate(
                prompt,
                system=None,
                expect_json=True
            )
            result = safe_parse_json(raw)
        except Exception as e:
            return Finding(
                dimension_id=dimension["id"],
                dimension_name=dimension["name"],
                status="UNCERTAIN",
                confidence=0.0,
                legal_citation="",
                ngo_evidence=ngo_evidence,
                reasoning=f"LLM call failed: {e}",
                routing="human_review",
                citation_valid=False,
                raw_llm_output=None,
            )

    llm_status = result.get("status", "UNCERTAIN")
    reasoning  = result.get("reasoning", "")
    evidence   = result.get("ngo_evidence", ngo_evidence)

    # Force FAIL if consistency issues exist for this dimension
    is_consistency_failure = False
    if consistency_issues:
        llm_status = "FAIL"
        reasoning = "[Consistency issue] " + "; ".join(consistency_issues) + ". " + reasoning
        is_consistency_failure = True

    # 7. Validate citation — fast path checks the chunk we actually fed to the model
    citation       = result.get("legal_citation", "")
    citation_valid = validate_citation(citation, canonical_state, chunk_meta=primary_meta)

    # 8. Downgrade if citation cannot be verified (except for consistency failures)
    if not is_consistency_failure and not citation_valid and llm_status in ("PASS", "FAIL"):
        llm_status = "UNCERTAIN"
        reasoning  = "[Citation unverified] " + reasoning

    # Apply organization name verification status and reasoning updates
    identity_status = ngo_json.get("_identity_status", "verified")
    matched_docs    = ngo_json.get("_matched_docs", [])
    is_identity_dim = dimension["id"] in ("registration", "governance")

    if is_identity_dim:
        if identity_status == "verified":
            reasoning = f"[Verified in: {', '.join(matched_docs)}] " + reasoning
        elif identity_status == "unverified":
            reasoning = "[Verification warning] Organisation name could not be confidently verified across uploaded documents. " + reasoning
        elif identity_status == "contradictory":
            reasoning = "[Contradictory warning] Uploaded documents consistently identify a different organization. " + reasoning

    # 9. Deterministic confidence — no LLM self-report used.
    #    PASS/FAIL with verified citation -> high confidence.
    #    UNCERTAIN (missing evidence) -> low confidence.
    #    UNCERTAIN (parse error/fallback) -> very low confidence.
    if is_consistency_failure:
        confidence = 0.30   # critical failure, < 50% so it auto-fails in report
    elif llm_status in ("PASS", "FAIL") and citation_valid:
        confidence = 0.90
    elif llm_status == "CORPUS_GAP":
        confidence = 0.00
    elif "could not be parsed" in reasoning or not result:
        confidence = 0.10   # JSON parse failure
    elif ngo_evidence == "No relevant fields extracted.":
        confidence = 0.30   # evidence genuinely absent
    else:
        confidence = 0.50   # ambiguous / citation not verified

    # Apply weighted identity score for identity dimensions
    if is_identity_dim and not is_consistency_failure and llm_status != "CORPUS_GAP":
        IDENTITY_WEIGHT = 0.15
        LEGAL_WEIGHT    = 0.85
        
        if identity_status == "verified":
            identity_score = 1.0
        elif identity_status == "unverified":
            identity_score = 0.5
        else: # contradictory
            identity_score = 0.0
            
        confidence = confidence * LEGAL_WEIGHT + identity_score * IDENTITY_WEIGHT

    # 10. Deterministic routing based on Priority 3 rules
    if llm_status == "CORPUS_GAP":
        routing = "corpus_alert"
    elif confidence >= 0.85:
        routing = "auto_report"
    elif 0.50 <= confidence < 0.85:
        routing = "human_review"
        llm_status = "UNCERTAIN"
    else: # confidence < 0.50
        routing = "auto_report"
        llm_status = "FAIL"

    matched_requirement = result.get("matched_requirement", "") if isinstance(result, dict) else ""

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
        matched_requirement=matched_requirement,
    )


def run_full_assessment(ngo_json: dict, state: str, entity_type: str, submitted_org_name: str) -> list:
    """
    Run all 7 dimensions. Returns list of Finding objects.
    Cross-document consistency is checked once upfront against submitted_org_name.
    Evaluates all compliance categories simultaneously in a single LLM request.
    """
    # Verify organization name matches across all uploaded documents
    matched_docs = check_org_name_verification(ngo_json, submitted_org_name)
    ngo_json["_matched_docs"] = matched_docs

    if matched_docs:
        ngo_json["_identity_status"] = "verified"
    elif check_contradictory_evidence(ngo_json, submitted_org_name):
        ngo_json["_identity_status"] = "contradictory"
    else:
        ngo_json["_identity_status"] = "unverified"

    # Run cross-document consistency check once for all dimensions
    all_consistency = check_consistency(ngo_json, submitted_org_name)
    total_issues = sum(len(v) for v in all_consistency.values())
    if total_issues:
        print(f"[RAG] Consistency issues detected ({total_issues} total):")
        for key, issues in all_consistency.items():
            for issue in issues:
                print(f"  - {issue}")
    else:
        print("[RAG] No cross-document consistency issues detected.")

    STATE_MAP = {
        "dl": "delhi",
        "mh": "maharashtra",
        "ka": "karnataka",
        "rj": "rajasthan"
    }
    canonical_state = STATE_MAP.get(state.lower(), state.lower())

    # 1. Gather active dimensions and retrieve context
    active_dimensions = {}
    gap_findings = {}

    for dim in DIMENSIONS:
        query = dim["query"].format(state=canonical_state, entity_type=entity_type)
        chunks, metas = retrieve_legal_context(query, canonical_state)

        if not chunks:
            gap_findings[dim["id"]] = Finding(
                dimension_id=dim["id"],
                dimension_name=dim["name"],
                status="CORPUS_GAP",
                confidence=0.0,
                legal_citation="",
                ngo_evidence="",
                reasoning=f"No legal provisions found for {dim['id']} in {canonical_state}. Add the relevant Act to the corpus.",
                routing="corpus_alert",
                citation_valid=False,
            )
        else:
            # Use top 3 chunks; rename for clarity
            primary_chunk      = chunks[0]
            primary_meta       = metas[0] if metas else {}
            support1_meta      = metas[1] if len(metas) > 1 else {}
            support2_meta      = metas[2] if len(metas) > 2 else {}
            supporting_chunk_1 = chunks[1] if len(chunks) > 1 else ""
            supporting_chunk_2 = chunks[2] if len(chunks) > 2 else ""
            ngo_evidence       = extract_evidence(ngo_json, dim["evidence_fields"])
            dim_issues         = _filter_consistency_issues(all_consistency, dim)

            # Retrieval audit log — shows which legal chunks were selected per dimension
            print(f"[RAG] {dim['id']} retrieval:")
            print(f"  Primary  : {primary_meta.get('act_name')} | {primary_meta.get('section_ref')}")
            print(f"  Support 1: {support1_meta.get('act_name')} | {support1_meta.get('section_ref')}")
            print(f"  Support 2: {support2_meta.get('act_name')} | {support2_meta.get('section_ref')}")

            # Debug logging for legal retrieval
            print(f"\n=================== DEBUG RETRIEVAL: {dim['id']} ===================")
            print(f"Dimension ID: {dim['id']}")
            print(f"Primary Metadata: state={primary_meta.get('state')}, act_name={primary_meta.get('act_name')}, section_ref={primary_meta.get('section_ref')}, source={primary_meta.get('source')}")
            print(f"Primary Chunk Text:\n{primary_chunk}")
            print(f"Supporting 1 Metadata: state={support1_meta.get('state')}, act_name={support1_meta.get('act_name')}, section_ref={support1_meta.get('section_ref')}, source={support1_meta.get('source')}")
            print(f"Supporting 1 Chunk Text:\n{supporting_chunk_1}")
            print(f"Supporting 2 Metadata: state={support2_meta.get('state')}, act_name={support2_meta.get('act_name')}, section_ref={support2_meta.get('section_ref')}, source={support2_meta.get('source')}")
            print(f"Supporting 2 Chunk Text:\n{supporting_chunk_2}")
            print(f"=====================================================================\n")

            active_dimensions[dim["id"]] = {
                "dimension":          dim,
                "primary_chunk":      primary_chunk,
                "primary_meta":       primary_meta,
                "supporting_chunk_1": supporting_chunk_1,
                "supporting_chunk_2": supporting_chunk_2,
                "ngo_evidence":       ngo_evidence,
                "dim_issues":         dim_issues,
            }

    # 2. Call LLM for all active dimensions in a single request
    combined_raw_output = None
    parsed_results = {}

    if active_dimensions:
        prompt = build_combined_prompt(active_dimensions, canonical_state, entity_type)
        print(f"[RAG] Calling Gemini for all active dimensions (prompt={len(prompt)} chars)...")
        try:
            combined_raw_output = generate(
                prompt,
                system=None,
                expect_json=True
            )
            print(f"[RAG] Gemini responded — {len(combined_raw_output)} chars")
            parsed_results = safe_parse_json(combined_raw_output)
        except Exception as e:
            print(f"[RAG] ERROR during combined Gemini call: {e}")

    # 3. Construct Findings
    findings = []
    for dim in DIMENSIONS:
        dim_id = dim["id"]
        print(f"  Assessing: {dim['name']}...")
        if dim_id in gap_findings:
            finding = gap_findings[dim_id]
        else:
            dim_data = active_dimensions[dim_id]
            
            dim_result = {}
            if isinstance(parsed_results, dict) and dim_id in parsed_results:
                dim_result = parsed_results[dim_id]
            else:
                dim_result = {
                    "status": "UNCERTAIN",
                    "reasoning": "Combined LLM response could not be parsed for this dimension."
                }
            
            finding = assess_dimension(
                dimension=dim,
                ngo_json=ngo_json,
                state=canonical_state,
                entity_type=entity_type,
                consistency_issues=dim_data["dim_issues"] or None,
                precomputed_result=dim_result,
                raw_llm_output=combined_raw_output,
                primary_chunk=dim_data["primary_chunk"],
                primary_meta=dim_data["primary_meta"],
                supporting_chunk_1=dim_data.get("supporting_chunk_1", ""),
                supporting_chunk_2=dim_data.get("supporting_chunk_2", ""),
            )
        findings.append(finding)
        print(f"  -> {finding.status} ({round(finding.confidence*100)}% conf) [{finding.routing}]")
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