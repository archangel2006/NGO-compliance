import re
from pathlib import Path
from typing import Optional

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except Exception:
    print("WARNING: spaCy model missing. Run: python -m spacy download en_core_web_sm")
    nlp = None

from backend.services.document_templates import DOCUMENT_TEMPLATES
from backend.services.ocr import extract_text


def extract_fields(text: str, doc_type: str, state: str) -> dict:
    """
    Extract structured fields from OCR text.
    Combines regex + spaCy NER + derived boolean fields.
    """
    if doc_type not in DOCUMENT_TEMPLATES:
        return {"error": f"Unknown doc type: {doc_type}"}

    template = DOCUMENT_TEMPLATES[doc_type]
    result   = {"doc_type": doc_type, "state": state}

    # 1. Regex extraction
    for field, pattern in template["fields"].items():
        if pattern:
            val = _regex_extract(text, pattern)
            if val:
                result[field] = val

    # 2. NER for complex fields
    if nlp and template.get("ner_fields"):
        result.update(_ner_extract(text, template["ner_fields"]))

    # 3. Normalize
    result = _normalize(result)

    # 4. Derived boolean fields
    result.update(_derive_booleans(text, doc_type))

    # 5. Cross-field validation
    result["_validation"] = _validate(result, doc_type)

    return result


def extract_all(docs: list) -> dict:
    """
    Process all uploaded documents for one submission.
    docs = [{"path": "...", "doc_type": "...", "state": "..."}, ...]
    Returns merged field dict.
    """
    merged = {}
    log    = []

    for doc in docs:
        ocr    = extract_text(doc["path"], doc["state"])
        fields = extract_fields(ocr["text"], doc["doc_type"], doc["state"])

        log.append({
            "doc_type":     doc["doc_type"],
            "ocr_method":   ocr["method"],
            "ocr_quality":  ocr["quality"],
            "fields_found": sum(1 for k, v in fields.items()
                               if not k.startswith("_") and v),
        })

        for k, v in fields.items():
            if not k.startswith("_") and k not in merged and v:
                merged[k] = v

    merged["_log"] = log
    return merged


# ── Internal helpers ──────────────────────────────────────────────

def _regex_extract(text: str, pattern: str) -> Optional[str]:
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    try:
        return match.group(1).strip()
    except IndexError:
        return match.group(0).strip()


def _ner_extract(text: str, fields: list) -> dict:
    if not nlp:
        return {}
    doc    = nlp(text[:5000])
    result = {}

    if "trustee_names" in fields or "office_bearers" in fields:
        # Collect location/place tokens to exclude from person names
        location_texts = {
            e.text.strip()
            for e in doc.ents
            if e.label_ in ("GPE", "LOC", "FAC", "ORG")
        }
        # spaCy sometimes marks person names as ORG and vice-versa;
        # also apply a simple heuristic: reject tokens that are purely
        # uppercase abbreviations or have digits (not person names)
        _PERSON_BLOCKLIST = {
            "india", "mumbai", "delhi", "bangalore", "bengaluru",
            "hyderabad", "chennai", "kolkata", "pune", "ahmedabad",
            "government", "ministry", "department", "office", "commissioner",
            "registrar", "district", "court", "division", "zone",
        }
        persons = []
        for e in doc.ents:
            if e.label_ != "PERSON":
                continue
            name = e.text.strip()
            if not name:
                continue
            # Skip if this text is also classified as a location
            if name in location_texts:
                continue
            # Skip if any token is in blocklist
            if any(tok.lower() in _PERSON_BLOCKLIST for tok in name.split()):
                continue
            # Skip single-word names that are all-caps and short (abbreviations)
            if len(name.split()) == 1 and name.isupper() and len(name) <= 4:
                continue
            persons.append(name)

        result["trustee_names"] = list(dict.fromkeys(persons))[:20]
        result["trustee_count"] = len(result["trustee_names"])

    if "org_name" in fields:
        _AUTHORITY_MARKERS = [
            "income tax", "government of india", "ministry", "department",
            "office of the", "principal commissioner", "commissioner",
            "charity commissioner", "registrar", "mha", "niti",
        ]
        orgs = [e.text.strip() for e in doc.ents if e.label_ == "ORG"]
        for org in orgs:
            org_lower = org.lower()
            if any(marker in org_lower for marker in _AUTHORITY_MARKERS):
                continue  # Skip issuing authorities
            result["ner_org_name"] = org
            break  # take first non-authority ORG

    if "grant_sources" in fields:
        result["grant_sources"] = [
            e.text for e in doc.ents if e.label_ == "ORG"
        ][:10]

    return result


def _normalize(fields: dict) -> dict:
    out = {}
    for k, v in fields.items():
        if isinstance(v, str):
            v = v.strip().strip(".,;: ")
            # Reject values that are only labels
            v_upper = v.upper()
            if v_upper in {
                "NAME OF TRUST", "TRUST NAME", "ORGANISATION NAME",
                "ORGANIZATION NAME", "NAME", "NAME OF THE TRUST",
                "NAME OF SOCIETY", "NAME OF HOLDER"
            }:
                v = None
            else:
                if "pan" in k.lower():
                    v = v.upper()
                if "date" in k.lower() or "until" in k.lower() or "from" in k.lower():
                    v = _normalize_date(v)
                if any(w in k for w in ["receipts", "expenditure", "total", "balance"]):
                    v = v.replace(",", "")
        out[k] = v
    return out


def _normalize_date(val: str) -> str:
    m = re.match(r'(\d{1,2})[\/\-\s](\d{1,2}|\w+)[\/\-\s](\d{4})', val)
    if m:
        d, mo, y = m.groups()
        # Convert month names
        month_map = {"jan":"01","feb":"02","mar":"03","apr":"04","may":"05",
                     "jun":"06","jul":"07","aug":"08","sep":"09","oct":"10",
                     "nov":"11","dec":"12"}
        mo = month_map.get(mo.lower()[:3], mo.zfill(2))
        return f"{d.zfill(2)}/{mo}/{y}"
    return val


def _derive_booleans(text: str, doc_type: str) -> dict:
    d = {}
    t = text.lower()

    if doc_type == "trust_deed":
        d["non_profit_clause_present"] = bool(
            re.search(r"no\s*profit|non.profit|not\s*for\s*profit|charitable\s*purpose", t))
        d["dissolution_clause_present"] = bool(
            re.search(r"dissolut|wind\s*up|winding\s*up", t))

    if doc_type == "annual_report":
        d["csr_grant_present"]         = bool(re.search(r"csr|corporate social", t))
        d["govt_grant_present"]        = bool(re.search(r"government grant|ministry|scheme fund", t))
        d["fund_utilisation_present"]  = bool(re.search(r"utilisation statement|fund utiliz", t))

    if doc_type == "audit_report":
        d["fcra_audit_present"] = bool(
            re.search(r"(?:fcra|foreign contribution).{0,100}(?:audit|fund|account)", t))

    if doc_type == "fcra_certificate":
        d["sbi_designated_account"] = bool(
            re.search(r"(?:state bank of india|sbi).{0,150}(?:new delhi|main branch)", t))

    return d


def _validate(fields: dict, doc_type: str) -> dict:
    """Cross-field sanity checks — flags inconsistencies."""
    issues = []

    if doc_type in ("certificate_12a", "certificate_80g", "fcra_certificate"):
        pan = fields.get("pan", "")
        if pan and not re.match(r'^[A-Z]{5}\d{4}[A-Z]$', pan):
            issues.append(f"PAN format invalid: {pan}")

    if "valid_until" in fields and "valid_from" in fields:
        if fields["valid_until"] == fields["valid_from"]:
            issues.append("valid_from and valid_until are identical")

    return {"issues": issues, "clean": len(issues) == 0}


def save_document_facts(submission_id: str, merged: dict):
    """Persists extracted facts to all 8 document-specific SQL tables during live assessment."""
    from backend.models.database import SessionLocal
    from backend.models.orm import (
        ExtractedTrustDeed, ExtractedRegistrationCertificate,
        Extracted12ACertificate, Extracted80GCertificate,
        ExtractedFCRACertificate, ExtractedAnnualReport,
        ExtractedAuditReport, ExtractedPanCard
    )

    db = SessionLocal()
    try:
        def to_str(val):
            if isinstance(val, list):
                return ", ".join(str(x) for x in val)
            return str(val) if val is not None else None

        def to_float(val):
            try:
                return float(val) if val is not None else None
            except Exception:
                return None

        def to_bool(val):
            if isinstance(val, bool):
                return val
            if isinstance(val, str):
                return val.lower() in ("true", "1", "yes")
            return bool(val) if val is not None else False

        # 1. Trust Deed
        if any(k in merged for k in ("org_name", "reg_date", "objectives_clause", "quorum", "trustee_names")):
            db.merge(ExtractedTrustDeed(
                submission_id=submission_id,
                org_name=merged.get("org_name"),
                reg_date=merged.get("reg_date"),
                objectives_clause=merged.get("objectives_clause"),
                quorum=merged.get("quorum"),
                amendment_clause=merged.get("amendment_clause"),
                org_address=merged.get("org_address"),
                trustee_count=int(merged["trustee_count"]) if merged.get("trustee_count") and str(merged.get("trustee_count")).isdigit() else None,
                trustee_names=to_str(merged.get("trustee_names")),
                office_bearers=to_str(merged.get("office_bearers")),
                non_profit_clause_present=to_bool(merged.get("non_profit_clause_present")),
                dissolution_clause_present=to_bool(merged.get("dissolution_clause_present")),
            ))

        # 2. Registration Certificate
        if any(k in merged for k in ("registration_number", "registering_authority", "act_registered_under")):
            db.merge(ExtractedRegistrationCertificate(
                submission_id=submission_id,
                registration_number=merged.get("registration_number"),
                registering_authority=merged.get("registering_authority"),
                date_of_registration=merged.get("date_of_registration") or merged.get("reg_date"),
                act_registered_under=merged.get("act_registered_under"),
                state_of_registration=merged.get("state_of_registration") or merged.get("state"),
            ))

        # 3. 12A Certificate
        if "cert_12a_number" in merged:
            db.merge(Extracted12ACertificate(
                submission_id=submission_id,
                cert_12a_number=merged.get("cert_12a_number"),
                pan=merged.get("pan"),
                valid_from=merged.get("valid_from"),
                valid_until=merged.get("valid_until"),
                form_ref=merged.get("form_ref"),
                provisional_flag=to_bool(merged.get("provisional_flag")),
            ))

        # 4. 80G Certificate
        if "cert_80g_number" in merged:
            db.merge(Extracted80GCertificate(
                submission_id=submission_id,
                cert_80g_number=merged.get("cert_80g_number"),
                pan=merged.get("pan"),
                valid_until=merged.get("valid_until"),
                deduction_rate=merged.get("deduction_rate"),
            ))

        # 5. FCRA Certificate
        if "fcra_reg_number" in merged:
            db.merge(ExtractedFCRACertificate(
                submission_id=submission_id,
                fcra_reg_number=merged.get("fcra_reg_number"),
                valid_until=merged.get("valid_until"),
                bank_account=merged.get("bank_account"),
                bank_name=merged.get("bank_name"),
                bank_branch=merged.get("bank_branch"),
                sbi_designated_account=to_bool(merged.get("sbi_designated_account")),
            ))

        # 6. Annual Report
        if any(k in merged for k in ("total_receipts", "total_expenditure", "financial_year")):
            db.merge(ExtractedAnnualReport(
                submission_id=submission_id,
                financial_year=merged.get("financial_year"),
                total_receipts=to_float(merged.get("total_receipts")),
                total_expenditure=to_float(merged.get("total_expenditure")),
                csr_grant_present=to_bool(merged.get("csr_grant_present")),
                govt_grant_present=to_bool(merged.get("govt_grant_present")),
                fund_utilisation_present=to_bool(merged.get("fund_utilisation_present")),
                grant_sources=to_str(merged.get("grant_sources")),
            ))

        # 7. Audit Report
        if any(k in merged for k in ("auditor_name", "auditor_icai", "audit_period")):
            db.merge(ExtractedAuditReport(
                submission_id=submission_id,
                auditor_name=merged.get("auditor_name"),
                auditor_icai=merged.get("auditor_icai"),
                audit_period=merged.get("audit_period"),
                fcra_audit_present=to_bool(merged.get("fcra_audit_present")),
            ))

        # 8. PAN Card
        if "pan" in merged or "org_name_pan" in merged:
            db.merge(ExtractedPanCard(
                submission_id=submission_id,
                pan=merged.get("pan"),
                org_name_pan=merged.get("org_name_pan") or merged.get("org_name"),
            ))

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to save live document facts to DB: {e}")
    finally:
        db.close()