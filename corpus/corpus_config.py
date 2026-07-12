# corpus/corpus_config.py

CORPUS_CONFIG = {

    # ── CENTRAL — SOCIETIES ──────────────────────────────────────
    "central/societies/societies_registration_act_1860.pdf": {
        "act_name": "Societies Registration Act, 1860",
        "jurisdiction": "central",
        "applicable_states": ["all"],
        "source_url": "indiacode.nic.in/bitstream/123456789/2262/1/AA1860-21.pdf"
    },

    # ── CENTRAL — FCRA ───────────────────────────────────────────
    "central/fcra/fcra_act_2010.pdf": {
        "act_name": "Foreign Contribution (Regulation) Act, 2010",
        "jurisdiction": "central",
        "applicable_states": ["all"],
        "source_url": "fcraonline.nic.in/home/PDF_Doc/FC-RegulationAct-2010-C.pdf"
    },
    "central/fcra/fcra_amendment_act_2020.pdf": {
        "act_name": "Foreign Contribution (Regulation) Amendment Act, 2020",
        "jurisdiction": "central",
        "applicable_states": ["all"],
        "source_url": "fcraonline.nic.in/home/PDF_Doc/fc_amend_07102020_1.pdf"
    },

    # ── CENTRAL — INCOME TAX ─────────────────────────────────────
    "central/income_tax/income_tax_act_1961_consolidated.pdf": {
        "act_name": "Income Tax Act, 1961 (consolidated, includes 12A, 12AB, 80G)",
        "jurisdiction": "central",
        "applicable_states": ["all"],
        "source_url": "incometaxindia.gov.in"
    },

    # ── CENTRAL — DARPAN / NGO GUIDANCE ─────────────────────────
    "central/darpan/ngo_darpan_id_for_fcra.pdf": {
        "act_name": "NGO Darpan ID for FCRA Registration — MHA Circular",
        "jurisdiction": "central",
        "applicable_states": ["all"],
        "source_url": "ngodarpan.gov.in/rss/oc/rsrc/NGO_Darpan_ID_for_FCRA.pdf"
    },
    "central/darpan/npo_guidance_note_india_2023.pdf": {
        "act_name": "NPO Guidance Note India 2023",
        "jurisdiction": "central",
        "applicable_states": ["all"],
        "source_url": "ngodarpan.gov.in/rss/oc/rsrc/NPO_Guidance_Note_India_2023_v2.pdf"
    },
    "central/darpan/rbi_master_circular_ngo_accounts.pdf": {
        "act_name": "RBI Master Circular — NGO Bank Accounts Chapter VII-46A",
        "jurisdiction": "central",
        "applicable_states": ["all"],
        "source_url": "ngodarpan.gov.in/rss/oc/rsrc/RBI_Master_Circular-Chatpter-VII-46A.pdf"
    },
    "central/darpan/pmla_gazette_notification.pdf": {
        "act_name": "PMLA Gazette Notification — NGO Compliance",
        "jurisdiction": "central",
        "applicable_states": ["all"],
        "source_url": "ngodarpan.gov.in/rss/oc/rsrc/PMLA_Gazette_Notification.pdf"
    },

    # ── MAHARASHTRA ──────────────────────────────────────────────
    "maharashtra/bombay_public_trusts_act_1950.pdf": {
        "act_name": "Bombay Public Trusts Act, 1950",
        "jurisdiction": "state",
        "applicable_states": ["maharashtra"],
        "source_url": "charity.maharashtra.gov.in/Portals/0/Files/B.P.T.Act,1950.pdf"
    },
    "maharashtra/bombay_public_trusts_rules_1951.pdf": {
        "act_name": "Bombay Public Trusts Rules, 1951",
        "jurisdiction": "state",
        "applicable_states": ["maharashtra"],
        "source_url": "charity.maharashtra.gov.in/Portals/0/Files/B.P.T.Rules,1951.pdf"
    },
    "maharashtra/societies_registration_act_1860_maharashtra.pdf": {
        "act_name": "Societies Registration Act, 1860 (Maharashtra)",
        "jurisdiction": "state",
        "applicable_states": ["maharashtra"],
        "source_url": "charity.maharashtra.gov.in/Portals/0/Files/S.R.Act1860.pdf"
    },

    # ── DELHI ────────────────────────────────────────────────────
    "delhi/societies_registration_act_1860_delhi.pdf": {
        "act_name": "Societies Registration Act, 1860 (as applicable to Delhi)",
        "jurisdiction": "state",
        "applicable_states": ["delhi"],
        "source_url": "indiacode.nic.in/bitstream/123456789/2262/1/AA1860-21.pdf"
    },

    # ── KARNATAKA ────────────────────────────────────────────────
    "karnataka/karnataka_societies_registration_act_1960.pdf": {
        "act_name": "Karnataka Societies Registration Act, 1960",
        "jurisdiction": "state",
        "applicable_states": ["karnataka"],
        "source_url": "indiacode.nic.in/bitstream/123456789/7743/1/17_of_1960_(e).pdf"
    },
    "karnataka/karnataka_societies_registration_rules_1961.pdf": {
        "act_name": "Karnataka Societies Registration Rules, 1961",
        "jurisdiction": "state",
        "applicable_states": ["karnataka"],
        "source_url": "dpal.karnataka.gov.in"
    },

    # ── RAJASTHAN ────────────────────────────────────────────────
    "rajasthan/rajasthan_societies_registration_act_1958.pdf": {
        "act_name": "Rajasthan Societies Registration Act, 1958",
        "jurisdiction": "state",
        "applicable_states": ["rajasthan"],
        "source_url": "indiacode.nic.in/bitstream/123456789/18835/1/the_rajasthan_societies_registration_act,_1958_with_foot_note.pdf"
    },
}


# What must be ingested before assessing each state
REQUIRED_CORPUS = {
    "maharashtra": [
        "maharashtra/bombay_public_trusts_act_1950.pdf",
        "maharashtra/bombay_public_trusts_rules_1951.pdf",
        "central/fcra/fcra_act_2010.pdf",
        "central/fcra/fcra_amendment_act_2020.pdf",
        "central/income_tax/income_tax_act_1961_consolidated.pdf",
    ],
    "delhi": [
        "delhi/societies_registration_act_1860_delhi.pdf",
        "central/fcra/fcra_act_2010.pdf",
        "central/income_tax/income_tax_act_1961_consolidated.pdf",
    ],
    "karnataka": [
        "karnataka/karnataka_societies_registration_act_1960.pdf",
        "central/fcra/fcra_act_2010.pdf",
        "central/income_tax/income_tax_act_1961_consolidated.pdf",
    ],
    "rajasthan": [
        "rajasthan/rajasthan_societies_registration_act_1958.pdf",
        "central/fcra/fcra_act_2010.pdf",
        "central/income_tax/income_tax_act_1961_consolidated.pdf",
    ],
}