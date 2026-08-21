"""
Seed script — populates all 13 database tables with 100% flat scalar relational columns.
Run from project root:
    python -m backend.tests.seed_db
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

from backend.models.database import engine, Base, SessionLocal
import backend.models.orm
from backend.models.orm import (
    Submission, UploadedDocument, ExtractedFields, ComplianceFinding, HumanReviewQueue,
    ExtractedTrustDeed, ExtractedRegistrationCertificate, Extracted12ACertificate,
    Extracted80GCertificate, ExtractedFCRACertificate, ExtractedAnnualReport,
    ExtractedAuditReport, ExtractedPanCard,
)

Base.metadata.create_all(bind=engine)

import uuid, datetime

def ts():
    return datetime.datetime.utcnow().isoformat()

def nid():
    return str(uuid.uuid4())


# ── Sample NGO Data ───────────────────────────────────────────────

NGOS = [
    {
        "submission": {
            "id": "sub-001-asha-delhi",
            "org_name": "Asha Jyoti Welfare Foundation",
            "state": "dl",
            "entity_type": "Public Trust",
            "pan": "AAJFA1234C",
            "sector": "Education",
            "contact_email": "info@ashajyoti.org",
            "year_of_incorporation": 2010,
            "darpan_id": "DL/2010/0045123",
            "status": "complete",
            "submitted_by": "officer@darpan.gov.in",
            "progress_step": 8,
            "overall_score": 84.5,
            "score_label": "Mostly Compliant - Minor Gaps",
            "grant_ready": False,
            "pass_count": 4,
            "fail_count": 1,
            "uncertain_count": 2,
            "corpus_gap_count": 0,
        },
        "documents": [
            {"doc_type": "trust_deed",                 "file_name": "asha_trust_deed.pdf",          "file_size": 524288,  "ocr_method": "pymupdf",    "ocr_quality": "good"},
            {"doc_type": "registration_certificate",   "file_name": "asha_reg_cert.pdf",            "file_size": 204800,  "ocr_method": "pymupdf",    "ocr_quality": "good"},
            {"doc_type": "certificate_12a",            "file_name": "asha_12a.pdf",                 "file_size": 153600,  "ocr_method": "pymupdf",    "ocr_quality": "good"},
            {"doc_type": "certificate_80g",            "file_name": "asha_80g.pdf",                 "file_size": 143360,  "ocr_method": "pymupdf",    "ocr_quality": "good"},
            {"doc_type": "fcra_certificate",           "file_name": "asha_fcra.pdf",               "file_size": 184320,  "ocr_method": "tesseract",  "ocr_quality": "fair"},
            {"doc_type": "annual_report",              "file_name": "asha_annual_2023.pdf",         "file_size": 1048576, "ocr_method": "pymupdf",    "ocr_quality": "good"},
            {"doc_type": "audit_report",               "file_name": "asha_audit_2023.pdf",          "file_size": 716800,  "ocr_method": "pymupdf",    "ocr_quality": "good"},
            {"doc_type": "pan_card",                   "file_name": "asha_pan.pdf",                "file_size": 102400,  "ocr_method": "tesseract",  "ocr_quality": "good"},
        ],
        "trust_deed": {
            "org_name": "Asha Jyoti Welfare Foundation",
            "reg_date": "15/03/2010",
            "objectives_clause": "To promote education, vocational training and welfare among underprivileged children in Delhi NCR.",
            "quorum": "One-third of the total trustees, minimum three trustees",
            "amendment_clause": "Amendments require two-thirds majority of trustees",
            "org_address": "Plot 24, Sector 12, Dwarka, New Delhi - 110075",
            "trustee_count": 7,
            "trustee_names": "Ramesh Kumar Sharma, Sunita Devi Gupta, Anil Kumar Verma, Priya Malhotra, Dr. Suresh Nair, Meena Agarwal, Vikram Singh",
            "office_bearers": "Ramesh Kumar Sharma (President), Sunita Devi Gupta (Secretary), Anil Kumar Verma (Treasurer)",
            "non_profit_clause_present": True,
            "dissolution_clause_present": True,
        },
        "reg_cert": {
            "registration_number": "DL/2010/0045123",
            "registering_authority": "Office of the Sub-Registrar, Dwarka, New Delhi",
            "date_of_registration": "15/03/2010",
            "act_registered_under": "Indian Trusts Act, 1882",
            "state_of_registration": "Delhi",
        },
        "cert_12a": {
            "cert_12a_number": "IT-12AB-DEL-2022-8814",
            "pan": "AAJFA1234C",
            "valid_from": "01/04/2022",
            "valid_until": "31/03/2027",
            "form_ref": "10AB",
            "provisional_flag": False,
        },
        "cert_80g": {
            "cert_80g_number": "IT-80G-DEL-2022-9127",
            "pan": "AAJFA1234C",
            "valid_until": "31/03/2027",
            "deduction_rate": "50%",
        },
        "fcra": {
            "fcra_reg_number": "231560442",
            "valid_until": "31/03/2026",
            "bank_account": "40087654321",
            "bank_name": "State Bank of India",
            "bank_branch": "New Delhi Main Branch",
            "sbi_designated_account": True,
        },
        "annual_report": {
            "financial_year": "2022-23",
            "total_receipts": 3477000.0,
            "total_expenditure": 1995000.0,
            "csr_grant_present": True,
            "govt_grant_present": False,
            "fund_utilisation_present": True,
            "grant_sources": "Infosys Foundation CSR, Individual Donors",
        },
        "audit_report": {
            "auditor_name": "M/s Kapoor & Associates",
            "auditor_icai": "FRN026871N",
            "audit_period": "01/04/2022 to 31/03/2023",
            "fcra_audit_present": True,
        },
        "pan_card": {
            "pan": "AAJFA1234C",
            "org_name_pan": "ASHA JYOTI WELFARE FOUNDATION",
        },
        "findings": [
            {"dimension_id": "registration", "dimension_name": "Registration & Legal Status",    "status": "PASS",      "confidence": 0.92, "routing": "auto_report",  "citation_valid": True,  "legal_citation": "Indian Trusts Act, 1882, Section 3",                           "ngo_evidence": "registration_number: DL/2010/0045123, registering_authority: Sub-Registrar Dwarka",                   "reasoning": "The trust is validly registered under the Indian Trusts Act, 1882 with the Sub-Registrar, Dwarka. Registration number DL/2010/0045123 confirmed."},
            {"dimension_id": "governance",   "dimension_name": "Governance Structure",           "status": "PASS",      "confidence": 0.87, "routing": "auto_report",  "citation_valid": True,  "legal_citation": "Indian Trusts Act, 1882, Section 10",                          "ngo_evidence": "trustee_count: 7, quorum: one-third minimum three trustees",                                           "reasoning": "Board of 7 trustees with a clearly defined quorum clause. Office bearers (President, Secretary, Treasurer) are designated as required."},
            {"dimension_id": "membership",   "dimension_name": "Membership Requirements",        "status": "PASS",      "confidence": 0.85, "routing": "auto_report",  "citation_valid": True,  "legal_citation": "Societies Registration Act, 1860, Section 3",                  "ngo_evidence": "trustee_count: 7",                                                                                     "reasoning": "Seven trustees meet the minimum requirement. Trust deed lists all trustees by name with roles."},
            {"dimension_id": "financial",    "dimension_name": "Financial Compliance",           "status": "UNCERTAIN", "confidence": 0.68, "routing": "human_review", "citation_valid": True,  "legal_citation": "FCRA, 2010, Section 17 — Annual Returns",                       "ngo_evidence": "total_receipts: 34,77,000, total_expenditure: 19,95,000, fund_utilisation_present: True",               "reasoning": "Fund utilisation statement is present. However, CSR grant from Infosys Foundation requires separate utilisation certificate which could not be verified from submitted documents."},
            {"dimension_id": "tax",          "dimension_name": "Tax Compliance (12A/80G)",       "status": "PASS",      "confidence": 0.95, "routing": "auto_report",  "citation_valid": True,  "legal_citation": "Income Tax Act, 1961, Section 12AB and 80G",                    "ngo_evidence": "cert_12a_number: IT-12AB-DEL-2022-8814, valid_until: 31/03/2027",                                      "reasoning": "Valid 12AB and 80G certificates confirmed, both expiring 31/03/2027. Form 10AB renewal completed post-2021 amendment."},
            {"dimension_id": "fcra",         "dimension_name": "FCRA Compliance",                "status": "UNCERTAIN", "confidence": 0.72, "routing": "human_review", "citation_valid": True,  "legal_citation": "Foreign Contribution (Regulation) Act, 2010, Section 17",       "ngo_evidence": "fcra_reg_number: 231560442, bank_branch: New Delhi Main Branch, sbi_designated_account: True",          "reasoning": "FCRA registration confirmed and SBI New Delhi Main Branch designated account is in order. However, FC-4 annual return for 2022-23 could not be verified from submitted documents."},
            {"dimension_id": "audit",        "dimension_name": "Audit Requirements",             "status": "PASS",      "confidence": 0.90, "routing": "auto_report",  "citation_valid": True,  "legal_citation": "FCRA Rules, 2011, Rule 17 — Separate FCRA Audit",               "ngo_evidence": "auditor_name: M/s Kapoor & Associates, auditor_icai: FRN026871N, fcra_audit_present: True",             "reasoning": "Separate FCRA audit conducted by a registered CA firm (ICAI FRN026871N). General and FCRA audits are distinct as required by Rule 17."},
        ],
    },

    {
        "submission": {
            "id": "sub-002-grameen-mh",
            "org_name": "Maharashtra Grameen Seva Trust",
            "state": "mh",
            "entity_type": "Public Trust",
            "pan": "AAMGM5678K",
            "sector": "Rural Development",
            "contact_email": "contact@grameen-seva.org",
            "year_of_incorporation": 2005,
            "darpan_id": "MH/2005/0012987",
            "status": "complete",
            "submitted_by": "officer@darpan.gov.in",
            "progress_step": 8,
            "overall_score": 71.0,
            "score_label": "Mostly Compliant - Minor Gaps",
            "grant_ready": False,
            "pass_count": 3,
            "fail_count": 2,
            "uncertain_count": 2,
            "corpus_gap_count": 0,
        },
        "documents": [
            {"doc_type": "trust_deed",               "file_name": "grameen_trust_deed.pdf",      "file_size": 614400,  "ocr_method": "pymupdf",    "ocr_quality": "good"},
            {"doc_type": "registration_certificate", "file_name": "grameen_reg_cert.pdf",        "file_size": 245760,  "ocr_method": "tesseract",  "ocr_quality": "fair"},
            {"doc_type": "certificate_12a",          "file_name": "grameen_12a.pdf",             "file_size": 163840,  "ocr_method": "pymupdf",    "ocr_quality": "good"},
            {"doc_type": "certificate_80g",          "file_name": "grameen_80g.pdf",             "file_size": 155648,  "ocr_method": "pymupdf",    "ocr_quality": "good"},
            {"doc_type": "annual_report",            "file_name": "grameen_annual_2023.pdf",     "file_size": 2097152, "ocr_method": "pymupdf",    "ocr_quality": "good"},
            {"doc_type": "audit_report",             "file_name": "grameen_audit_2023.pdf",      "file_size": 819200,  "ocr_method": "tesseract",  "ocr_quality": "fair"},
            {"doc_type": "pan_card",                 "file_name": "grameen_pan.pdf",             "file_size": 102400,  "ocr_method": "tesseract",  "ocr_quality": "good"},
        ],
        "trust_deed": {
            "org_name": "Maharashtra Grameen Seva Trust",
            "reg_date": "22/07/2005",
            "objectives_clause": "To uplift rural communities in Maharashtra through sustainable agriculture, water conservation, and livelihood programmes.",
            "quorum": "Three trustees or one-half of total trustees, whichever is higher",
            "amendment_clause": "Amendments require unanimous consent of all trustees",
            "org_address": "Survey No. 45, Shivapur Road, Pune - 412301, Maharashtra",
            "trustee_count": 9,
            "trustee_names": "Dattatray Bhosale, Sunanda Patil, Rajendra Kadam, Lata Deshmukh, Narayan Jadhav, Sushila Mane, Balasaheb Shinde, Kavita Pawar, Arun Kulkarni",
            "office_bearers": "Dattatray Bhosale (Chairman), Sunanda Patil (Secretary), Rajendra Kadam (Treasurer)",
            "non_profit_clause_present": True,
            "dissolution_clause_present": True,
        },
        "reg_cert": {
            "registration_number": "MH/2005/0012987",
            "registering_authority": "Office of the Charity Commissioner, Pune",
            "date_of_registration": "22/07/2005",
            "act_registered_under": "Bombay Public Trusts Act, 1950",
            "state_of_registration": "Maharashtra",
        },
        "cert_12a": {
            "cert_12a_number": "IT-12A-MH-2018-4421",
            "pan": "AAMGM5678K",
            "valid_from": "01/04/2018",
            "valid_until": "31/03/2023",
            "form_ref": "10A",
            "provisional_flag": False,
        },
        "cert_80g": {
            "cert_80g_number": "IT-80G-MH-2018-5190",
            "pan": "AAMGM5678K",
            "valid_until": "31/03/2023",
            "deduction_rate": "50%",
        },
        "fcra": None,
        "annual_report": {
            "financial_year": "2022-23",
            "total_receipts": 8920000.0,
            "total_expenditure": 7650000.0,
            "csr_grant_present": True,
            "govt_grant_present": True,
            "fund_utilisation_present": False,
            "grant_sources": "NABARD Rural Infrastructure Fund, Tata Trusts CSR, State Government MREGS",
        },
        "audit_report": {
            "auditor_name": "M/s Joshi & Gokhale Associates",
            "auditor_icai": "FRN105432W",
            "audit_period": "01/04/2022 to 31/03/2023",
            "fcra_audit_present": False,
        },
        "pan_card": {
            "pan": "AAMGM5678K",
            "org_name_pan": "MAHARASHTRA GRAMEEN SEVA TRUST",
        },
        "findings": [
            {"dimension_id": "registration", "dimension_name": "Registration & Legal Status",    "status": "PASS",      "confidence": 0.93, "routing": "auto_report",  "citation_valid": True,  "legal_citation": "Bombay Public Trusts Act, 1950, Section 18",                    "ngo_evidence": "registration_number: MH/2005/0012987, registering_authority: Charity Commissioner Pune",               "reasoning": "Validly registered under the Bombay Public Trusts Act, 1950. Maharashtra requires registration with Charity Commissioner — confirmed."},
            {"dimension_id": "governance",   "dimension_name": "Governance Structure",           "status": "PASS",      "confidence": 0.88, "routing": "auto_report",  "citation_valid": True,  "legal_citation": "Bombay Public Trusts Act, 1950, Section 22",                    "ngo_evidence": "trustee_count: 9, quorum clause present",                                                              "reasoning": "9 trustees with quorum clause requiring minimum three or one-half. Office bearers designated. Governance structure is compliant."},
            {"dimension_id": "membership",   "dimension_name": "Membership Requirements",        "status": "PASS",      "confidence": 0.86, "routing": "auto_report",  "citation_valid": True,  "legal_citation": "Bombay Public Trusts Act, 1950, Section 8",                    "ngo_evidence": "trustee_count: 9",                                                                                     "reasoning": "Nine trustees meet and exceed minimum membership requirements under the applicable state Act."},
            {"dimension_id": "financial",    "dimension_name": "Financial Compliance",           "status": "FAIL",      "confidence": 0.88, "routing": "auto_report",  "citation_valid": True,  "legal_citation": "Bombay Public Trusts Act, 1950, Section 33 — Fund Utilisation", "ngo_evidence": "csr_grant_present: True, govt_grant_present: True, fund_utilisation_present: False",                   "reasoning": "Both CSR and government grants received but no fund utilisation statement was found. Maharashtra BPT Act Section 33 mandates separate utilisation certificates for grants above Rs 5,00,000."},
            {"dimension_id": "tax",          "dimension_name": "Tax Compliance (12A/80G)",       "status": "FAIL",      "confidence": 0.95, "routing": "auto_report",  "citation_valid": True,  "legal_citation": "Income Tax Act, 1961, Section 12AB — Mandatory Renewal",        "ngo_evidence": "cert_12a_number: IT-12A-MH-2018-4421, valid_until: 31/03/2023",                                        "reasoning": "12A and 80G certificates expired 31/03/2023 and have not been renewed under the mandatory 12AB regime effective April 2021. The trust must file Form 10AB immediately."},
            {"dimension_id": "fcra",         "dimension_name": "FCRA Compliance",                "status": "UNCERTAIN", "confidence": 0.60, "routing": "human_review", "citation_valid": True,  "legal_citation": "FCRA, 2010, Section 11 — Registration Requirement",            "ngo_evidence": "No FCRA certificate submitted",                                                                        "reasoning": "No FCRA certificate was uploaded. Unable to determine whether the trust receives foreign contributions. If foreign funding exists, FCRA registration is mandatory."},
            {"dimension_id": "audit",        "dimension_name": "Audit Requirements",             "status": "UNCERTAIN", "confidence": 0.65, "routing": "human_review", "citation_valid": True,  "legal_citation": "FCRA Rules, 2011, Rule 17",                                     "ngo_evidence": "auditor_name: M/s Joshi & Gokhale, fcra_audit_present: False",                                         "reasoning": "General audit is present but FCRA-specific audit under Rule 17 is absent. If trust receives foreign contributions, a separate FCRA audit is mandatory."},
        ],
    },

    {
        "submission": {
            "id": "sub-003-vidya-ka",
            "org_name": "Vidya Vardhini Education Society",
            "state": "ka",
            "entity_type": "Society",
            "pan": "AABGV9012P",
            "sector": "Education",
            "contact_email": "admin@vidyavardhini.edu.in",
            "year_of_incorporation": 2015,
            "darpan_id": "KA/2015/0067834",
            "status": "complete",
            "submitted_by": "officer@darpan.gov.in",
            "progress_step": 8,
            "overall_score": 88.5,
            "score_label": "Compliant - Grant Ready",
            "grant_ready": True,
            "pass_count": 6,
            "fail_count": 0,
            "uncertain_count": 1,
            "corpus_gap_count": 0,
        },
        "documents": [
            {"doc_type": "trust_deed",               "file_name": "vidya_moa.pdf",               "file_size": 573440,  "ocr_method": "pymupdf",    "ocr_quality": "good"},
            {"doc_type": "registration_certificate", "file_name": "vidya_reg_cert.pdf",          "file_size": 225280,  "ocr_method": "pymupdf",    "ocr_quality": "good"},
            {"doc_type": "certificate_12a",          "file_name": "vidya_12a.pdf",               "file_size": 163840,  "ocr_method": "pymupdf",    "ocr_quality": "good"},
            {"doc_type": "certificate_80g",          "file_name": "vidya_80g.pdf",               "file_size": 143360,  "ocr_method": "pymupdf",    "ocr_quality": "good"},
            {"doc_type": "annual_report",            "file_name": "vidya_annual_2023.pdf",       "file_size": 1572864, "ocr_method": "pymupdf",    "ocr_quality": "good"},
            {"doc_type": "audit_report",             "file_name": "vidya_audit_2023.pdf",        "file_size": 663552,  "ocr_method": "pymupdf",    "ocr_quality": "good"},
            {"doc_type": "pan_card",                 "file_name": "vidya_pan.pdf",               "file_size": 102400,  "ocr_method": "tesseract",  "ocr_quality": "good"},
        ],
        "trust_deed": {
            "org_name": "Vidya Vardhini Education Society",
            "reg_date": "10/09/2015",
            "objectives_clause": "To establish and manage educational institutions providing quality schooling, technical education, and skill development in rural Karnataka.",
            "quorum": "Five members or one-third of total membership, whichever is less, minimum five",
            "amendment_clause": "Amendments require three-fourths majority at a special general meeting",
            "org_address": "No. 78, 2nd Cross, Rajajinagar, Bengaluru - 560010, Karnataka",
            "trustee_count": 11,
            "trustee_names": "Prof. Nagesh Rao, Dr. Shobha Krishnamurthy, Ravi Shankar Hegde, Usha Srinivasan, Manjunath Gowda, Kavitha Nair, Suresh Bhat, Anitha Murthy, Prakash Reddy, Leela Devi, Chandrashekar Iyengar",
            "office_bearers": "Prof. Nagesh Rao (President), Dr. Shobha Krishnamurthy (Secretary), Ravi Shankar Hegde (Treasurer)",
            "non_profit_clause_present": True,
            "dissolution_clause_present": True,
        },
        "reg_cert": {
            "registration_number": "KA/2015/0067834",
            "registering_authority": "Registrar of Societies, Bengaluru",
            "date_of_registration": "10/09/2015",
            "act_registered_under": "Karnataka Societies Registration Act, 1960",
            "state_of_registration": "Karnataka",
        },
        "cert_12a": {
            "cert_12a_number": "IT-12AB-KA-2022-3301",
            "pan": "AABGV9012P",
            "valid_from": "01/04/2022",
            "valid_until": "31/03/2027",
            "form_ref": "10AB",
            "provisional_flag": False,
        },
        "cert_80g": {
            "cert_80g_number": "IT-80G-KA-2022-4450",
            "pan": "AABGV9012P",
            "valid_until": "31/03/2027",
            "deduction_rate": "50%",
        },
        "fcra": None,
        "annual_report": {
            "financial_year": "2022-23",
            "total_receipts": 12450000.0,
            "total_expenditure": 11200000.0,
            "csr_grant_present": False,
            "govt_grant_present": True,
            "fund_utilisation_present": True,
            "grant_sources": "Karnataka State Government Education Department, Individual Donors",
        },
        "audit_report": {
            "auditor_name": "M/s Shenoy & Kamath LLP",
            "auditor_icai": "FRN119834S",
            "audit_period": "01/04/2022 to 31/03/2023",
            "fcra_audit_present": False,
        },
        "pan_card": {
            "pan": "AABGV9012P",
            "org_name_pan": "VIDYA VARDHINI EDUCATION SOCIETY",
        },
        "findings": [
            {"dimension_id": "registration", "dimension_name": "Registration & Legal Status",    "status": "PASS",      "confidence": 0.95, "routing": "auto_report",  "citation_valid": True,  "legal_citation": "Karnataka Societies Registration Act, 1960, Section 3",         "ngo_evidence": "registration_number: KA/2015/0067834, act_registered_under: KSA 1960",                                 "reasoning": "Society is validly registered under the Karnataka Societies Registration Act, 1960 with the Registrar of Societies, Bengaluru."},
            {"dimension_id": "governance",   "dimension_name": "Governance Structure",           "status": "PASS",      "confidence": 0.91, "routing": "auto_report",  "citation_valid": True,  "legal_citation": "Karnataka Societies Registration Act, 1960, Section 9",         "ngo_evidence": "trustee_count: 11, quorum: five members or one-third",                                                  "reasoning": "11-member governing body with quorum of 5. Office bearers clearly designated. Governing body size and structure exceeds statutory minimums."},
            {"dimension_id": "membership",   "dimension_name": "Membership Requirements",        "status": "PASS",      "confidence": 0.90, "routing": "auto_report",  "citation_valid": True,  "legal_citation": "Karnataka Societies Registration Act, 1960, Section 4",         "ngo_evidence": "trustee_count: 11",                                                                                     "reasoning": "Eleven governing body members meet and exceed KSA 1960 requirement of minimum seven members."},
            {"dimension_id": "financial",    "dimension_name": "Financial Compliance",           "status": "PASS",      "confidence": 0.89, "routing": "auto_report",  "citation_valid": True,  "legal_citation": "Karnataka Societies Registration Act, 1960, Section 15",        "ngo_evidence": "fund_utilisation_present: True, govt_grant_present: True, total_receipts: 1,24,50,000",                  "reasoning": "Fund utilisation statement submitted for government grant. Accounts show surplus of Rs 12,50,000 appropriately recorded."},
            {"dimension_id": "tax",          "dimension_name": "Tax Compliance (12A/80G)",       "status": "PASS",      "confidence": 0.96, "routing": "auto_report",  "citation_valid": True,  "legal_citation": "Income Tax Act, 1961, Section 12AB and 80G",                    "ngo_evidence": "cert_12a_number: IT-12AB-KA-2022-3301, valid_until: 31/03/2027",                                        "reasoning": "Valid 12AB and 80G certificates in place until 31/03/2027. Renewal done under post-2021 regime using Form 10AB."},
            {"dimension_id": "fcra",         "dimension_name": "FCRA Compliance",                "status": "UNCERTAIN", "confidence": 0.55, "routing": "human_review", "citation_valid": True,  "legal_citation": "FCRA, 2010, Section 11",                                        "ngo_evidence": "No FCRA certificate submitted",                                                                        "reasoning": "No FCRA documentation submitted. Society receives only domestic government grants, suggesting FCRA registration may not be required. Officer to confirm foreign funding status."},
            {"dimension_id": "audit",        "dimension_name": "Audit Requirements",             "status": "PASS",      "confidence": 0.92, "routing": "auto_report",  "citation_valid": True,  "legal_citation": "Karnataka Societies Registration Act, 1960, Section 15(3)",     "ngo_evidence": "auditor_name: M/s Shenoy & Kamath LLP, auditor_icai: FRN119834S",                                      "reasoning": "Annual audit completed by a registered CA firm (ICAI FRN119834S). No FCRA audit required as no foreign contributions declared."},
        ],
    },
]


# ── Seed Logic ────────────────────────────────────────────────────

def seed():
    db = SessionLocal()
    try:
        print("\n--- Seeding NGO Compliance Database (Flat Relational Mode) ---\n")

        for ngo in NGOS:
            s = ngo["submission"]
            sid = s["id"]

            exists = db.query(Submission).filter(Submission.id == sid).first()
            if exists:
                print(f"  [SKIP] {s['org_name']} — already in database.")
                continue

            print(f"  Seeding: {s['org_name']} ({s['state'].upper()}) ...")

            # 1. Submission
            db.add(Submission(created_at=ts(), updated_at=ts(), **s))
            db.flush()

            # 2. Uploaded Documents
            for doc in ngo["documents"]:
                db.add(UploadedDocument(
                    id=nid(), submission_id=sid,
                    file_path=f"uploads/{sid}/{doc['file_name']}",
                    file_size=doc["file_size"],
                    ocr_status="done",
                    ocr_method=doc["ocr_method"],
                    ocr_quality=doc["ocr_quality"],
                    uploaded_at=ts(),
                    **{k: v for k, v in doc.items() if k not in ("file_size", "ocr_method", "ocr_quality")},
                ))

            # 3. ExtractedFields (Metadata row)
            db.add(ExtractedFields(
                submission_id=sid,
                total_fields_extracted=len(ngo["trust_deed"]) + len(ngo["reg_cert"]),
                extraction_status="complete",
                created_at=ts(),
            ))

            # 4. Document-specific tables (Flat scalar columns)
            db.add(ExtractedTrustDeed(submission_id=sid, **ngo["trust_deed"]))
            db.add(ExtractedRegistrationCertificate(submission_id=sid, **ngo["reg_cert"]))
            if ngo["cert_12a"]:
                db.add(Extracted12ACertificate(submission_id=sid, **ngo["cert_12a"]))
            if ngo["cert_80g"]:
                db.add(Extracted80GCertificate(submission_id=sid, **ngo["cert_80g"]))
            if ngo["fcra"]:
                db.add(ExtractedFCRACertificate(submission_id=sid, **ngo["fcra"]))
            db.add(ExtractedAnnualReport(submission_id=sid, **ngo["annual_report"]))
            db.add(ExtractedAuditReport(submission_id=sid, **ngo["audit_report"]))
            db.add(ExtractedPanCard(submission_id=sid, **ngo["pan_card"]))

            # 5. Compliance Findings + Human Review Queue
            for f in ngo["findings"]:
                fid = nid()
                db.add(ComplianceFinding(
                    id=fid, submission_id=sid,
                    matched_requirement="",
                    raw_llm_output=None,
                    human_determination=None,
                    reviewed_by=None,
                    reviewed_at=None,
                    created_at=ts(),
                    **f,
                ))
                if f["routing"] == "human_review":
                    db.add(HumanReviewQueue(
                        id=nid(), finding_id=fid, submission_id=sid,
                        dimension_name=f["dimension_name"],
                        assigned_officer="officer@darpan.gov.in",
                        queue_status="pending",
                        ai_recommendation_revealed=False,
                        created_at=ts(),
                    ))

            db.commit()
            print(f"    [OK] {s['org_name']} seeded.")

        print("\n--- Seed complete. ---\n")

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
