import json
import re
import ollama
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()

LLM_MODEL   = os.getenv("LLM_MODEL", "mistral")
TEMPERATURE = 0.1   # low temp — legal reasoning needs consistency


# ── Core generate call ────────────────────────────────────────────

def generate(prompt: str, system: Optional[str] = None,
             expect_json: bool = True) -> str:
    """
    Raw LLM call. Returns string response.
    All other functions in this module call this.
    """
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = ollama.chat(
        model=LLM_MODEL,
        messages=messages,
        options={
            "temperature": TEMPERATURE,
            "num_predict": 1024,   # cap output length — compliance answers are short
        },
        format="json" if expect_json else "",
    )
    return response["message"]["content"]


# ── JSON parsing (handles common LLM output failures) ────────────

def parse_json_output(raw: str) -> dict:
    """
    Parse LLM output to dict. Handles:
    - Markdown code fences (```json ... ```)
    - Trailing commas
    - Response text before/after the JSON object
    """
    # Strip markdown fences
    cleaned = re.sub(r'```(?:json)?', '', raw).strip().strip('`')

    # Try direct parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try to find JSON object within the text
    match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Last resort: return safe fallback
    return {
        "status":         "UNCERTAIN",
        "confidence":     0.2,
        "legal_citation": "",
        "ngo_evidence":   "",
        "reasoning":      "LLM output could not be parsed. Raw output logged.",
        "_parse_failed":  True,
        "_raw":           raw[:500],
    }


# ── Compliance assessment call ────────────────────────────────────

COMPLIANCE_SYSTEM = """You are a legal compliance officer reviewing NGO
registration documents for India. You assess whether an NGO satisfies
specific legal requirements based on retrieved statutory provisions and
document evidence. Be precise, cite exact sections, and use UNCERTAIN
when the evidence is insufficient or ambiguous. Never invent legal
requirements not present in the provided text."""

def assess_compliance(dimension_name: str, state: str, entity_type: str,
                      legal_context: str, ngo_evidence: str) -> dict:
    """
    Core compliance assessment. Returns structured finding dict.
    Called once per dimension per submission.
    """
    prompt = f"""COMPLIANCE DIMENSION: {dimension_name}
STATE: {state}  |  ENTITY TYPE: {entity_type}

LEGAL PROVISIONS (retrieved from corpus):
{legal_context}

NGO DOCUMENT EVIDENCE:
{ngo_evidence}

INSTRUCTIONS:
- Assess ONLY based on the legal text and evidence provided above
- Do not invent or assume any requirements not in the legal text
- PASS: evidence clearly satisfies the legal requirement
- FAIL: evidence clearly violates or is missing a key requirement
- UNCERTAIN: evidence is ambiguous, incomplete, or OCR quality was poor
- Keep reasoning to 2-3 sentences maximum

Return ONLY a valid JSON object:
{{
  "status": "PASS" or "FAIL" or "UNCERTAIN",
  "confidence": 0.0 to 1.0,
  "legal_citation": "exact act name and section reference",
  "ngo_evidence": "specific text or field from NGO documents assessed",
  "reasoning": "2-3 sentence explanation"
}}"""

    raw    = generate(prompt, system=COMPLIANCE_SYSTEM, expect_json=True)
    result = parse_json_output(raw)
    result["_raw_llm"] = raw   # keep for audit trail
    return result


# ── Corpus gap fallback — tries to reformulate query ─────────────

def decompose_query(original_query: str, state: str) -> list:
    """
    When primary query returns no ChromaDB results,
    ask the LLM to break it into simpler sub-queries.
    Returns list of alternative query strings.
    """
    prompt = f"""The following legal query returned no results from a corpus
of Indian NGO Acts:

QUERY: "{original_query}"
STATE: {state}

Generate 3 simpler alternative search queries that might find relevant
legal provisions. Return ONLY a JSON array of strings:
["query 1", "query 2", "query 3"]"""

    raw = generate(prompt, expect_json=True)
    try:
        result = parse_json_output(raw)
        if isinstance(result, list):
            return result[:3]
        # Sometimes LLM wraps in a dict
        for v in result.values():
            if isinstance(v, list):
                return v[:3]
    except Exception:
        pass
    return []


# ── Quick health check ────────────────────────────────────────────

def check_llm_available() -> dict:
    """Test Ollama is running and model is loaded."""
    try:
        response = ollama.chat(
            model=LLM_MODEL,
            messages=[{"role": "user",
                       "content": 'Reply with {"status":"ok"}'}],
            options={"temperature": 0, "num_predict": 20},
            format="json",
        )
        return {"available": True, "model": LLM_MODEL,
                "response": response["message"]["content"]}
    except Exception as e:
        return {"available": False, "model": LLM_MODEL, "error": str(e)}