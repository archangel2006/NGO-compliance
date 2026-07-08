CORPUS_CONFIG = {

    # ─── CENTRAL ───────────────────────────────────────────────
    "central/fcra/FCRA_Act_2010.pdf": {
        "act_name": "Foreign Contribution (Regulation) Act, 2010",
        "jurisdiction": "central",
        "applicable_states": ["all"],
        "source_url": "fcraonline.nic.in/home/PDF_Doc/FC-RegulationAct-2010-C.pdf"
    },
    "central/fcra/FCRA_Amendment_2020.pdf": {
        "act_name": "Foreign Contribution (Regulation) Amendment Act, 2020",
        "jurisdiction": "central",
        "applicable_states": ["all"],
        "source_url": "fcraonline.nic.in/home/PDF_Doc/fc_amend_07102020_1.pdf"
    },
    "central/fcra/FCRA_Rules_2011.pdf": {
        "act_name": "Foreign Contribution (Regulation) Rules, 2011",
        "jurisdiction": "central",
        "applicable_states": ["all"],
        "source_url": "fcraonline.nic.in"
    },
    "central/income_tax/IT_Act_Sec_11_12.pdf": {
        "act_name": "Income Tax Act 1961 - Sections 11 and 12",
        "jurisdiction": "central",
        "applicable_states": ["all"],
        "source_url": "incometaxindia.gov.in"
    },
    "central/income_tax/IT_Act_Sec_12A_12AB.pdf": {
        "act_name": "Income Tax Act 1961 - Sections 12A and 12AB",
        "jurisdiction": "central",
        "applicable_states": ["all"],
        "source_url": "incometaxindia.gov.in"
    },
    "central/income_tax/IT_Act_Sec_80G.pdf": {
        "act_name": "Income Tax Act 1961 - Section 80G",
        "jurisdiction": "central",
        "applicable_states": ["all"],
        "source_url": "incometaxindia.gov.in"
    },
    "central/darpan/NGO_Darpan_Guidelines.pdf": {
        "act_name": "NGO Darpan Registration Guidelines",
        "jurisdiction": "central",
        "applicable_states": ["all"],
        "source_url": "ngodarpan.gov.in"
    },
    "central/societies/SRA_1860.pdf": {
        "act_name": "Societies Registration Act, 1860",
        "jurisdiction": "central",
        "applicable_states": ["all"],
        "source_url": "indiacode.nic.in/bitstream/123456789/14647/1/india_societies_registration_act.pdf"
    },

    # ─── MAHARASHTRA ───────────────────────────────────────────
    "maharashtra/BPT_Act_1950.pdf": {
        "act_name": "Bombay Public Trusts Act, 1950",
        "jurisdiction": "state",
        "applicable_states": ["maharashtra"],
        "source_url": "charity.maharashtra.gov.in/Portals/0/Files/B.P.T.Act,1950.pdf"
    },
    "maharashtra/BPT_Rules_1951.pdf": {
        "act_name": "Bombay Public Trusts Rules, 1951",
        "jurisdiction": "state",
        "applicable_states": ["maharashtra"],
        "source_url": "charity.maharashtra.gov.in/Portals/0/Files/B.P.T.Rules,1951.pdf"
    },
    "maharashtra/SRA_1860_Maharashtra.pdf": {
        "act_name": "Societies Registration Act (Maharashtra)",
        "jurisdiction": "state",
        "applicable_states": ["maharashtra"],
        "source_url": "charity.maharashtra.gov.in/Portals/0/Files/S.R.Act1860.pdf"
    },

    # ─── DELHI ─────────────────────────────────────────────────
    "delhi/SRA_1860_Delhi.pdf": {
        "act_name": "Societies Registration Act 1860 (as applicable to Delhi)",
        "jurisdiction": "state",
        "applicable_states": ["delhi"],
        "source_url": "indiacode.nic.in/bitstream/123456789/20573/1/aa1860-21.pdf"
    },

    # ─── KARNATAKA ─────────────────────────────────────────────
    "karnataka/KSA_1960.pdf": {
        "act_name": "Karnataka Societies Registration Act, 1960",
        "jurisdiction": "state",
        "applicable_states": ["karnataka"],
        "source_url": "dpal.karnataka.gov.in/storage/pdf-files/acts%20alpha%20and%20dept%20wise%20acts/17%20of%201960%20(E).pdf"
    },
    "karnataka/KSA_Rules_1961.pdf": {
        "act_name": "Karnataka Societies Registration Rules, 1961",
        "jurisdiction": "state",
        "applicable_states": ["karnataka"],
        "source_url": "dpal.karnataka.gov.in"
    },

    # ─── RAJASTHAN ─────────────────────────────────────────────
    "rajasthan/RSA_1958.pdf": {
        "act_name": "Rajasthan Societies Registration Act, 1958",
        "jurisdiction": "state",
        "applicable_states": ["rajasthan"],
        "source_url": "indiacode.nic.in/bitstream/123456789/18835/1/the_rajasthan_societies_registration_act,_1958_with_foot_note.pdf"
    },
}

# What must exist before assessing each state
REQUIRED_CORPUS = {
    "maharashtra": [
        "maharashtra/BPT_Act_1950.pdf",
        "central/fcra/FCRA_Act_2010.pdf",
        "central/income_tax/IT_Act_Sec_12A_12AB.pdf",
        "central/income_tax/IT_Act_Sec_80G.pdf",
    ],
    "delhi": [
        "delhi/SRA_1860_Delhi.pdf",
        "central/fcra/FCRA_Act_2010.pdf",
        "central/income_tax/IT_Act_Sec_12A_12AB.pdf",
    ],
    "karnataka": [
        "karnataka/KSA_1960.pdf",
        "central/fcra/FCRA_Act_2010.pdf",
        "central/income_tax/IT_Act_Sec_12A_12AB.pdf",
    ],
    "rajasthan": [
        "rajasthan/RSA_1958.pdf",
        "central/fcra/FCRA_Act_2010.pdf",
        "central/income_tax/IT_Act_Sec_12A_12AB.pdf",
    ],
}