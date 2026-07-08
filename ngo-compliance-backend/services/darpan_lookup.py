# In production: real API call to Darpan's internal database
# In pilot: mock response based on known Darpan IDs

MOCK_DARPAN_DATA = {
    "MH/2019/0234521": {
        "name":              "Asha Jyoti Welfare Foundation",
        "state":             "maharashtra",
        "entity_type":       "Public Trust",
        "registration_no":   "E-23847/2019",
        "pan":               "AAETA2384K",
        "sector":            "Education & Women Empowerment",
        "city":              "Pune",
        "fcra_registered":   True,
        "fcra_reg_no":       "083780142",
        "tax_12a":           True,
        "tax_80g":           True,
        "office_bearers": [
            {"name": "Priya Sharma",  "role": "Secretary"},
            {"name": "Rahul Gupta",   "role": "President"},
            {"name": "Anita Singh",   "role": "Treasurer"},
        ],
        "darpan_profile_url": "ngodarpan.gov.in/ngo/MH/2019/0234521"
    },
    "DL/2018/0112334": {
        "name":            "Delhi Shiksha Samiti",
        "state":           "delhi",
        "entity_type":     "Society",
        "registration_no": "S-11234/2018",
        "pan":             "AABDS1122K",
        "sector":          "Education",
        "city":            "New Delhi",
        "fcra_registered": False,
        "tax_12a":         True,
        "tax_80g":         False,
        "office_bearers": [],
        "darpan_profile_url": "ngodarpan.gov.in/ngo/DL/2018/0112334"
    }
}

def lookup_ngo(darpan_id: str) -> dict:
    """
    In production: call Darpan's internal API.
    In pilot: return mock data.
    """
    data = MOCK_DARPAN_DATA.get(darpan_id.upper())
    if not data:
        return {"found": False, "darpan_id": darpan_id}
    return {"found": True, "darpan_id": darpan_id, **data}