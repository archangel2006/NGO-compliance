"""
Field extraction templates per document type.
Defines: regex patterns, NER fields needed, which dimensions each doc feeds.
"""

DOCUMENT_TEMPLATES = {

    "trust_deed": {
        "description": "Trust Deed or Declaration of Trust",
        "fields": {
            # Matches label + colon/space + a title-cased name that is NOT the label word itself
            "org_name":           r"(?:name\s+of\s+(?:the\s+)?trust|known\s+as|trust(?:ed)?\s+as)[:\s]+(?!name|of|the)([A-Z][A-Za-z\s&]{4,80}(?:Trust|Society|Foundation|Samiti|Sangh|Welfare|Seva|NGO))",
            "reg_date":           r"(?:executed on|this deed dated|dated this)[:\s]+(\d{1,2}[\s\/\-]\w+[\s\/\-]\d{4})",
            "non_profit_clause":  r"(no(?:t for)? profit|charitable purpose|non.profit)[^\n]{0,200}",
            "objectives_clause":  r"(?:objects?|objectives?|purposes?)[:\s]+([^\n]{50,})",
            "quorum":             r"quorum[:\s]+(\w+|\d+)",
            "amendment_clause":   r"(?:amendment|alteration)[^\n]{0,150}",
        },
        "ner_fields":   ["trustee_names", "org_address", "office_bearers"],
        "dimensions":   ["registration", "governance", "membership"],
    },

    "registration_certificate": {
        "description": "State registration certificate",
        "fields": {
            "registration_number":   r"(?:reg(?:istration)?\.?\s*no|certificate\s*no)[.:\s]+([A-Z0-9\/\-]+)",
            "registering_authority": r"(?:issued by|registrar|charity commissioner)[:\s]+([^\n]+)",
            "date_of_registration":  r"(?:registered on|date of registration|this\s+\w+\s+day)[:\s]+(\d{1,2}[\s\/\-]\w+[\s\/\-]\d{4})",
            "act_registered_under":  r"(?:under|pursuant to)[:\s]+([^\n]+(?:Act|Rules)[^\n]{0,50})",
            "state_of_registration": r"(?:state of|registered in|in the state of)[:\s]+([A-Z][a-z]+)",
        },
        "ner_fields": [],
        "dimensions": ["registration"],
    },

    "certificate_12a": {
        "description": "Income Tax 12A / 12AB Certificate",
        "fields": {
            "cert_12a_number":  r"(?:certificate\s*no|order\s*no)[.:\s]+([A-Z0-9\/\-]+)",
            "pan":              r"\b([A-Z]{5}\d{4}[A-Z])\b",
            "valid_from":       r"(?:valid from|effective from|w\.?e\.?f\.?)[:\s]+(\d{1,2}[\s\/\-]\w+[\s\/\-]\d{4})",
            "valid_until":      r"(?:valid (?:till|until|upto)|validity expires?)[:\s]+(\d{1,2}[\s\/\-]\w+[\s\/\-]\d{4})",
            "form_ref":         r"(?:Form\s*No\.?|application\s*in\s*Form)[:\s]+(10A|10AB)",
            "provisional_flag": r"(provisional|final|permanent)\s*(?:registration|approval)",
        },
        # org_name is intentionally NOT extracted from 12A/80G —
        # the issuing authority (Income Tax Department) dominates NER;
        # org name should come from trust_deed or pan_card instead.
        "ner_fields": [],
        "dimensions": ["tax"],
    },

    "certificate_80g": {
        "description": "Income Tax 80G Certificate",
        "fields": {
            "cert_80g_number": r"(?:certificate\s*no|order\s*no)[.:\s]+([A-Z0-9\/\-]+)",
            "pan":             r"\b([A-Z]{5}\d{4}[A-Z])\b",
            "valid_until":     r"(?:valid (?:till|until|upto)|validity expires?)[:\s]+(\d{1,2}[\s\/\-]\w+[\s\/\-]\d{4})",
            "deduction_rate":  r"(\d+)\s*%\s*(?:of\s*the\s*)?(?:donation|contribution)",
        },
        "ner_fields": [],
        "dimensions": ["tax"],
    },

    "fcra_certificate": {
        "description": "FCRA Registration Certificate from Ministry of Home Affairs",
        "fields": {
            "fcra_reg_number":  r"(?:FCRA\s*reg(?:istration)?\s*no|registration\s*number)[.:\s]+(\d{9,12})",
            "valid_until":      r"(?:valid\s*(?:till|until|upto)|validity)[:\s]+(\d{1,2}[\s\/\-]\w+[\s\/\-]\d{4})",
            "bank_account":     r"(?:account\s*(?:number|no)|A\/C\s*No)[.:\s]+(\d{9,18})",
            "bank_name":        r"(?:bank\s*name|name\s*of\s*bank)[:\s]+([^\n]{5,50})",
            "bank_branch":      r"(?:branch|branch\s*name)[:\s]+([^\n]{5,60})",
        },
        # org_name from FCRA cert is NOT in ner_fields — issuing authority text
        # dominates NER here; org name should come from trust_deed or pan_card
        "ner_fields": [],
        "dimensions": ["fcra"],
    },

    "annual_report": {
        "description": "Annual Report / Activity Report",
        "fields": {
            "financial_year":    r"(?:financial\s*year|for\s*the\s*year|year\s*ending)[:\s]+(\d{4}[-–]\d{2,4})",
            "total_receipts":    r"(?:total\s*receipts?|total\s*income)[:\s]+(?:Rs\.?|₹)?\s*([\d,]+)",
            "total_expenditure": r"(?:total\s*expenditure|total\s*expenses?)[:\s]+(?:Rs\.?|₹)?\s*([\d,]+)",
        },
        "ner_fields": ["grant_sources"],
        "dimensions": ["financial"],
    },

    "audit_report": {
        "description": "Audited Financial Statements",
        "fields": {
            "auditor_name":    r"(?:(?:firm|auditor)\s*name|chartered\s*accountant)[:\s]+([^\n]{5,80})",
            "auditor_icai":    r"(?:ICAI\s*(?:reg(?:istration)?)?\s*no|membership\s*no|firm\s*reg(?:istration)?\s*no)[.:\s]+([A-Z]?\d{5,8})",
            "audit_period":    r"(?:for\s*the\s*(?:year|period)|as\s*at|year\s*ended)[:\s]+(\d{1,2}[\s\/\-]\w+[\s\/\-]\d{4})",
            "balance_sheet":   r"(?:total\s*assets|balance\s*sheet\s*total)[:\s]+(?:Rs\.?|₹)?\s*([\d,]+)",
        },
        "ner_fields": ["auditor_firm"],
        "dimensions": ["audit"],
    },

    "pan_card": {
        "description": "PAN Card of the Organisation",
        "fields": {
            "pan":         r"\b([A-Z]{5}\d{4}[A-Z])\b",
            "org_name_pan": r"\n([A-Z\s]{5,60}(?:TRUST|SOCIETY|FOUNDATION|SAMITI|SANGH|WELFARE|SEVA))",
        },
        "ner_fields": [],
        "dimensions": ["tax", "fcra"],
    },
}

VALID_DOC_TYPES = list(DOCUMENT_TEMPLATES.keys())