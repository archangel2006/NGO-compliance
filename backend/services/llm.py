import json
import re
from typing import Optional
from dotenv import load_dotenv
import os
import ollama
from ollama import Client


load_dotenv()

# Instantiate Ollama Client using base url config
client = Client(host=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))

LLM_MODEL = os.getenv("LLM_MODEL", "mistral")
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "8192"))

TEMPERATURE = 0.1   # low temp — legal reasoning needs consistency


# ── Core generate call ────────────────────────────────────────────

def generate(prompt: str, system: Optional[str] = None,
             expect_json: bool = True) -> str:

    full_prompt = ""
    if system:
        full_prompt += system + "\n\n"
    full_prompt += prompt

    print(f"[LLM] Calling Ollama ({LLM_MODEL}) (prompt={len(full_prompt)} chars)...")
    try:
        response = client.generate(
            model=LLM_MODEL,
            prompt=full_prompt,
            options={
                "temperature": TEMPERATURE,
                "num_ctx": OLLAMA_NUM_CTX
            }
        )
        print(f"[LLM] Successfully generated using local Ollama model {LLM_MODEL}")
        return response["response"]
    except Exception as e:
        print(f"[LLM] Ollama model {LLM_MODEL} failed: {e}")
        raise e

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

def check_llm_available():
    """Check Ollama connectivity and model loading."""

    try:
        response = client.generate(
            model=LLM_MODEL,
            prompt='Reply only with {"status":"ok"}',
            options={
                "temperature": 0.1,
                "num_ctx": OLLAMA_NUM_CTX
            }
        )

        return {
            "available": True,
            "model": LLM_MODEL,
            "response": response["response"]
        }

    except Exception as e:
        return {
            "available": False,
            "model": LLM_MODEL,
            "error": str(e)
        }