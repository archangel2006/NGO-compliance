"""
Generate 8 realistic demo NGO documents for testing the compliance pipeline.
NGO: Asha Jyoti Welfare Foundation (Maharashtra, Public Trust)
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, HRFlowable)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
import os

OUT = "/home/claude/demo_ngo_docs"
os.makedirs(OUT, exist_ok=True)

W, H = A4

def doc(filename, title):
    path = f"{OUT}/{filename}"
    d = SimpleDocTemplate(path, pagesize=A4,
                          topMargin=2*cm, bottomMargin=2*cm,
                          leftMargin=2.5*cm, rightMargin=2.5*cm)
    return d, path

styles = getSampleStyleSheet()

def S(name, **kw):
    s = ParagraphStyle(name, parent=styles["Normal"], **kw)
    return s

HEAD  = S("HEAD",  fontSize=14, fontName="Helvetica-Bold",
          alignment=TA_CENTER, spaceAfter=4)
SUB   = S("SUB",   fontSize=11, fontName="Helvetica-Bold",
          alignment=TA_CENTER, spaceAfter=8)
BODY  = S("BODY",  fontSize=10, fontName="Helvetica",
          leading=16, alignment=TA_JUSTIFY, spaceAfter=6)
LABEL = S("LABEL", fontSize=10, fontName="Helvetica-Bold", spaceAfter=3)
SMALL = S("SMALL", fontSize=9,  fontName="Helvetica",
          textColor=colors.gray, spaceAfter=4)
SEC   = S("SEC",   fontSize=11, fontName="Helvetica-Bold",
          spaceBefore=12, spaceAfter=4)

def hr(): return HRFlowable(width="100%", thickness=0.5,
                             color=colors.lightgrey, spaceAfter=8)

def sp(n=1): return Spacer(1, n * 0.3 * cm)


# ═══════════════════════════════════════════════════════════════════
# DOC 1 — TRUST DEED
# ═══════════════════════════════════════════════════════════════════
def doc1_trust_deed():
    d, path = doc("01_trust_deed.pdf", "Trust Deed")
    story = [
        Paragraph("TRUST DEED", HEAD),
        Paragraph("OF", SUB),
        Paragraph("ASHA JYOTI WELFARE FOUNDATION", HEAD),
        Paragraph("A Public Charitable Trust Registered under the Bombay Public Trusts Act, 1950", SMALL),
        hr(), sp(),

        Paragraph("THIS TRUST DEED is executed on this 14th day of March, 2019 at Pune, Maharashtra.", BODY),
        Paragraph("BY THE FOLLOWING SETTLORS AND TRUSTEES:", LABEL),

        Paragraph("""1. Priya Sharma, D/o Ramesh Sharma, residing at 42, Shivaji Nagar, Pune – 411005,
Maharashtra. Occupation: Social Worker.""", BODY),
        Paragraph("""2. Rahul Gupta, S/o Suresh Gupta, residing at 18, Model Colony, Pune – 411016,
Maharashtra. Occupation: Educator.""", BODY),
        Paragraph("""3. Anita Singh, D/o Mohan Singh, residing at 7, Kothrud, Pune – 411038,
Maharashtra. Occupation: Doctor.""", BODY),
        Paragraph("""4. Vikram Desai, S/o Arvind Desai, residing at 33, Baner Road, Pune – 411045,
Maharashtra. Occupation: Chartered Accountant.""", BODY),
        Paragraph("""5. Kavita Patel, D/o Harish Patel, residing at 55, Aundh, Pune – 411007,
Maharashtra. Occupation: Advocate.""", BODY),
        sp(),

        Paragraph("Section 1 — NAME OF THE TRUST", SEC),
        Paragraph("""The Trust shall be known as ASHA JYOTI WELFARE FOUNDATION (hereinafter referred to
as "the Trust") and shall have its registered office at 42, Shivaji Nagar, Pune – 411005,
Maharashtra, India.""", BODY),

        Paragraph("Section 2 — NATURE OF THE TRUST", SEC),
        Paragraph("""The Trust is a Public Charitable Trust established for charitable purposes only.
The Trust is a non-profit organisation. No part of the income or property of the Trust
shall be paid or transferred, directly or indirectly, by way of dividend, bonus or profit
to any person who is or has been a Trustee or member of the Trust. The Trust does not
exist for profit motive and any surplus income shall be applied solely for the objects
of the Trust.""", BODY),

        Paragraph("Section 3 — OBJECTS OF THE TRUST", SEC),
        Paragraph("The objects for which the Trust is established are:", BODY),
        Paragraph("""(a) To promote education among women and girls, particularly from economically
weaker sections of society in Maharashtra and across India.""", BODY),
        Paragraph("""(b) To establish, maintain and support schools, colleges, vocational training centres,
libraries and other educational institutions.""", BODY),
        Paragraph("""(c) To promote women empowerment through skill development, legal awareness and
livelihood programmes.""", BODY),
        Paragraph("""(d) To provide scholarships, stipends and financial assistance to meritorious but
economically disadvantaged students.""", BODY),
        Paragraph("""(e) To undertake health and nutrition programmes for women and children.""", BODY),
        Paragraph("""(f) To do all such other acts and things as may be incidental or conducive to the
attainment of the above objects.""", BODY),

        Paragraph("Section 4 — GOVERNANCE AND MANAGEMENT", SEC),
        Paragraph("""The Trust shall be managed by a Board of Trustees consisting of not less than five (5)
and not more than eleven (11) Trustees. The Board shall comprise:
(a) President — Rahul Gupta
(b) Secretary — Priya Sharma
(c) Treasurer — Vikram Desai
(d) Members — Anita Singh, Kavita Patel""", BODY),

        Paragraph("Section 5 — QUORUM", SEC),
        Paragraph("""The quorum for a meeting of the Board of Trustees shall be three (3) members.
Meetings shall be held at least once every quarter. Decisions shall be taken by a
majority of Trustees present and voting.""", BODY),

        Paragraph("Section 6 — NON-PROFIT CLAUSE", SEC),
        Paragraph("""This Trust is established exclusively for charitable purposes as defined under
Section 2(15) of the Income Tax Act, 1961. No portion of the Trust's funds shall be
used for any purpose other than the stated charitable objectives. Upon dissolution, the
assets of the Trust shall be transferred to another charitable Trust or institution
with similar objects as decided by the Board of Trustees and approved by the Charity
Commissioner, Maharashtra.""", BODY),

        Paragraph("Section 7 — AMENDMENT", SEC),
        Paragraph("""The Deed of Trust may be altered, amended or added to by a resolution passed by
not less than three-fourths (3/4) of the total number of Trustees at a special meeting
convened for this purpose, subject to the approval of the Charity Commissioner,
Maharashtra under the Bombay Public Trusts Act, 1950.""", BODY),

        sp(2),
        Paragraph("IN WITNESS WHEREOF the parties have signed this Deed on the day and year first above written.", BODY),
        sp(),
        Paragraph("Priya Sharma (Secretary) ___________________", BODY),
        Paragraph("Rahul Gupta (President) ___________________", BODY),
        Paragraph("Vikram Desai (Treasurer) ___________________", BODY),
        sp(),
        Paragraph("Registered under Bombay Public Trusts Act, 1950", SMALL),
        Paragraph("Registration No.: E-23847/2019", SMALL),
        Paragraph("Charity Commissioner, Pune Division, Maharashtra", SMALL),
    ]
    d.build(story)
    return path


# ═══════════════════════════════════════════════════════════════════
# DOC 2 — REGISTRATION CERTIFICATE
# ═══════════════════════════════════════════════════════════════════
def doc2_reg_cert():
    d, path = doc("02_registration_certificate.pdf", "Reg Cert")
    story = [
        Paragraph("GOVERNMENT OF MAHARASHTRA", HEAD),
        Paragraph("OFFICE OF THE CHARITY COMMISSIONER", SUB),
        Paragraph("Pune Division, Maharashtra", SMALL),
        hr(), sp(),

        Paragraph("CERTIFICATE OF REGISTRATION", HEAD),
        Paragraph("Under the Bombay Public Trusts Act, 1950", SUB),
        sp(),

        Paragraph("CERTIFICATE NO.: E-23847/2019", LABEL),
        sp(),

        Paragraph("""THIS IS TO CERTIFY that the public trust known as""", BODY),
        Paragraph("ASHA JYOTI WELFARE FOUNDATION", HEAD),
        Paragraph("""having its registered office at 42, Shivaji Nagar, Pune – 411005, Maharashtra
has been duly registered under Section 18 of the Bombay Public Trusts Act, 1950.""", BODY),
        sp(),

        Table([
            ["Registration Number",   "E-23847/2019"],
            ["Date of Registration",   "14 March 2019"],
            ["Act Registered Under",   "Bombay Public Trusts Act, 1950"],
            ["Registering Authority",  "Charity Commissioner, Pune Division"],
            ["State of Registration",  "Maharashtra"],
            ["Nature of Trust",        "Public Charitable Trust"],
            ["PAN of the Trust",       "AAETA2384K"],
            ["Registered Office",      "42, Shivaji Nagar, Pune – 411005"],
        ], colWidths=[7*cm, 9*cm],
        style=TableStyle([
            ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#F4F6FA")),
            ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 10),
            ("GRID", (0,0), (-1,-1), 0.5, colors.lightgrey),
            ("ROWBACKGROUNDS", (0,0), (-1,-1),
             [colors.white, colors.HexColor("#F8FAFC")]),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ])),
        sp(2),

        Paragraph("""The Trust has been registered for charitable purposes as enumerated in the Trust
Deed dated 14th March 2019, including promotion of education, women empowerment and
health among economically weaker sections of society.""", BODY),
        sp(2),

        Paragraph("Sd/-", BODY),
        Paragraph("Joint Charity Commissioner", LABEL),
        Paragraph("Pune Division, Maharashtra", BODY),
        Paragraph("Date: 28 March 2019", BODY),
        sp(),
        Paragraph("[Office Seal]", SMALL),
    ]
    d.build(story)
    return path


# ═══════════════════════════════════════════════════════════════════
# DOC 3 — 12A CERTIFICATE
# ═══════════════════════════════════════════════════════════════════
def doc3_12a():
    d, path = doc("03_certificate_12a.pdf", "12A")
    story = [
        Paragraph("INCOME TAX DEPARTMENT", HEAD),
        Paragraph("GOVERNMENT OF INDIA", SUB),
        Paragraph("Office of the Principal Commissioner of Income Tax, Pune", SMALL),
        hr(), sp(),

        Paragraph("REGISTRATION CERTIFICATE UNDER SECTION 12AB", HEAD),
        Paragraph("Income Tax Act, 1961", SUB),
        sp(),

        Paragraph("Certificate No.: IT-12AB-PUNE-2021-4821", LABEL),
        Paragraph("Application Reference: Form 10AB / 2021-22 / AAETA2384K", SMALL),
        sp(),

        Paragraph("""This is to certify that the trust / institution named below has been granted
registration under Section 12AB of the Income Tax Act, 1961.""", BODY),
        sp(),

        Table([
            ["Name of Trust",         "Asha Jyoti Welfare Foundation"],
            ["PAN",                    "AAETA2384K"],
            ["Registration Number",    "E-23847/2019"],
            ["Form of Application",    "Form No. 10AB"],
            ["Nature of Registration", "Final Registration"],
            ["Valid From",             "01 April 2021"],
            ["Valid Until",            "31 March 2026"],
            ["Order Date",             "15 June 2021"],
        ], colWidths=[7*cm, 9*cm],
        style=TableStyle([
            ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#F4F6FA")),
            ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 10),
            ("GRID", (0,0), (-1,-1), 0.5, colors.lightgrey),
            ("ROWBACKGROUNDS", (0,0), (-1,-1),
             [colors.white, colors.HexColor("#F8FAFC")]),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ])),
        sp(2),

        Paragraph("""The above-named trust has been examined and found to be established for charitable
purposes within the meaning of Section 2(15) of the Income Tax Act, 1961. Accordingly,
income of the trust applied for charitable purposes shall be exempt under Sections 11
and 12 of the Act, subject to the conditions specified therein.""", BODY),
        sp(),
        Paragraph("""This registration is valid for a period of 5 (five) years from 01 April 2021
to 31 March 2026 unless cancelled earlier under the provisions of the Act.""", BODY),
        sp(2),

        Paragraph("Sd/-", BODY),
        Paragraph("Principal Commissioner of Income Tax", LABEL),
        Paragraph("Pune, Maharashtra", BODY),
        Paragraph("Date: 15 June 2021", BODY),
    ]
    d.build(story)
    return path


# ═══════════════════════════════════════════════════════════════════
# DOC 4 — 80G CERTIFICATE
# ═══════════════════════════════════════════════════════════════════
def doc4_80g():
    d, path = doc("04_certificate_80g.pdf", "80G")
    story = [
        Paragraph("INCOME TAX DEPARTMENT", HEAD),
        Paragraph("GOVERNMENT OF INDIA", HEAD),
        Paragraph("Office of the Principal Commissioner of Income Tax, Pune", SMALL),
        hr(), sp(),

        Paragraph("CERTIFICATE OF APPROVAL UNDER SECTION 80G", HEAD),
        Paragraph("Income Tax Act, 1961", SUB),
        sp(),

        Paragraph("Certificate No.: IT-80G-PUNE-2021-7734", LABEL),
        sp(),

        Paragraph("""It is hereby certified that Asha Jyoti Welfare Foundation has been approved
under Section 80G(5)(vi) of the Income Tax Act, 1961. Donations made to the above
institution shall be eligible for deduction as specified below.""", BODY),
        sp(),

        Table([
            ["Name of Institution",    "Asha Jyoti Welfare Foundation"],
            ["PAN",                    "AAETA2384K"],
            ["Registration No.",       "E-23847/2019"],
            ["Deduction Permissible",  "50% of the amount donated"],
            ["Qualifying Limit",       "10% of adjusted gross total income"],
            ["Valid From",             "01 April 2021"],
            ["Valid Until",            "31 March 2026"],
            ["Order Date",             "15 June 2021"],
        ], colWidths=[7*cm, 9*cm],
        style=TableStyle([
            ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#F4F6FA")),
            ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 10),
            ("GRID", (0,0), (-1,-1), 0.5, colors.lightgrey),
            ("ROWBACKGROUNDS", (0,0), (-1,-1),
             [colors.white, colors.HexColor("#F8FAFC")]),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ])),
        sp(2),

        Paragraph("""This approval is subject to the following conditions:
(a) The institution shall maintain proper books of account and records.
(b) No part of income shall be used for benefit of any trustee or member.
(c) The institution shall file annual returns as required under the Income Tax Act, 1961.
(d) The institution shall apply at least 85% of its income for charitable purposes.""", BODY),
        sp(2),

        Paragraph("Sd/-", BODY),
        Paragraph("Principal Commissioner of Income Tax", LABEL),
        Paragraph("Pune, Maharashtra", BODY),
        Paragraph("Date: 15 June 2021", BODY),
    ]
    d.build(story)
    return path


# ═══════════════════════════════════════════════════════════════════
# DOC 5 — FCRA CERTIFICATE
# ═══════════════════════════════════════════════════════════════════
def doc5_fcra():
    d, path = doc("05_fcra_certificate.pdf", "FCRA")
    story = [
        Paragraph("MINISTRY OF HOME AFFAIRS", HEAD),
        Paragraph("GOVERNMENT OF INDIA", SUB),
        Paragraph("FCRA Wing, New Delhi – 110001", SMALL),
        hr(), sp(),

        Paragraph("CERTIFICATE OF REGISTRATION", HEAD),
        Paragraph("Under the Foreign Contribution (Regulation) Act, 2010", SUB),
        sp(),

        Paragraph("FCRA Registration No.: 083780142", LABEL),
        sp(),

        Paragraph("""This is to certify that the association mentioned below has been granted
registration under Section 11 of the Foreign Contribution (Regulation) Act, 2010
to accept foreign contribution for the purposes specified herein.""", BODY),
        sp(),

        Table([
            ["Name of Association",   "Asha Jyoti Welfare Foundation"],
            ["Registered Address",     "42, Shivaji Nagar, Pune – 411005, Maharashtra"],
            ["FCRA Reg. Number",       "083780142"],
            ["PAN",                    "AAETA2384K"],
            ["Purpose",                "Educational and Social Welfare Activities"],
            ["Date of Registration",   "12 September 2020"],
            ["Valid Until",            "11 September 2025"],
            ["Designated Bank",        "State Bank of India"],
            ["Branch",                 "New Delhi Main Branch"],
            ["Account Number",         "40021983748"],
            ["IFSC Code",              "SBIN0000691"],
        ], colWidths=[7*cm, 9*cm],
        style=TableStyle([
            ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#F4F6FA")),
            ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 10),
            ("GRID", (0,0), (-1,-1), 0.5, colors.lightgrey),
            ("ROWBACKGROUNDS", (0,0), (-1,-1),
             [colors.white, colors.HexColor("#F8FAFC")]),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ])),
        sp(2),

        Paragraph("""Conditions of Registration:
1. All foreign contributions shall be received only in the designated FCRA bank account
   at State Bank of India, New Delhi Main Branch as specified above.
2. Foreign contributions shall be utilised only for the purposes for which registered.
3. The association shall file Annual Return in Form FC-4 within nine months of close
   of each financial year.
4. Prior permission of the Central Government shall be obtained before utilising any
   foreign contribution for any purpose other than specified above.
5. The association shall maintain separate accounts for FCRA funds as required under
   Rule 17 of the Foreign Contribution (Regulation) Rules, 2011.""", BODY),
        sp(2),

        Paragraph("Sd/-", BODY),
        Paragraph("Joint Secretary to the Government of India", LABEL),
        Paragraph("FCRA Wing, Ministry of Home Affairs", BODY),
        Paragraph("Date: 12 September 2020", BODY),
    ]
    d.build(story)
    return path


# ═══════════════════════════════════════════════════════════════════
# DOC 6 — ANNUAL REPORT
# ═══════════════════════════════════════════════════════════════════
def doc6_annual_report():
    d, path = doc("06_annual_report.pdf", "Annual Report")
    story = [
        Paragraph("ASHA JYOTI WELFARE FOUNDATION", HEAD),
        Paragraph("ANNUAL REPORT — Financial Year 2023–24", SUB),
        Paragraph("Registration No.: E-23847/2019  |  PAN: AAETA2384K", SMALL),
        hr(), sp(),

        Paragraph("Section 1 — MESSAGE FROM THE SECRETARY", SEC),
        Paragraph("""This Annual Report covers the activities and financial performance of Asha Jyoti
Welfare Foundation for the financial year 2023–24 (April 2023 to March 2024).
The Foundation continued to advance its mission of empowering women and girls through
education, skill development and health initiatives across Pune district, Maharashtra.""", BODY),

        Paragraph("Section 2 — ACTIVITIES DURING 2023–24", SEC),
        Paragraph("""(a) Scholarship Programme: Provided scholarships to 84 meritorious girl students
from economically weaker sections across Pune district.
(b) Skill Development: Conducted 12 vocational training workshops covering tailoring,
computer literacy and entrepreneurship for 240 women beneficiaries.
(c) Legal Awareness: Organised 6 legal awareness camps on women's rights reaching
approximately 1,200 women.
(d) Health Camps: Conducted 4 health and nutrition camps in partnership with local PHCs.""", BODY),

        Paragraph("Section 3 — FINANCIAL SUMMARY 2023–24", SEC),
        Table([
            ["Particulars", "Amount (Rs.)"],
            ["RECEIPTS", ""],
            ["Opening Balance (01 April 2023)", "4,82,315"],
            ["Donation — Domestic", "18,45,000"],
            ["CSR Grant — TCS Foundation", "18,50,000"],
            ["Government Grant — Ministry of WCD", "12,00,000"],
            ["Interest Income", "38,420"],
            ["TOTAL RECEIPTS", "54,15,735"],
            ["EXPENDITURE", ""],
            ["Scholarship Disbursements", "8,40,000"],
            ["Programme Expenses", "14,22,500"],
            ["Salaries and Staff Costs", "9,85,000"],
            ["Administrative Expenses", "2,14,300"],
            ["Audit and Legal Fees", "85,000"],
            ["TOTAL EXPENDITURE", "35,46,800"],
            ["Closing Balance (31 March 2024)", "18,68,935"],
        ], colWidths=[10*cm, 6*cm],
        style=TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1A3A6B")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTNAME", (0,1), (0,1), "Helvetica-Bold"),
            ("FONTNAME", (0,8), (0,8), "Helvetica-Bold"),
            ("BACKGROUND", (0,1), (-1,1), colors.HexColor("#EEF2F9")),
            ("BACKGROUND", (0,8), (-1,8), colors.HexColor("#EEF2F9")),
            ("FONTNAME", (0,7), (-1,7), "Helvetica-Bold"),
            ("FONTNAME", (0,14), (-1,14), "Helvetica-Bold"),
            ("BACKGROUND", (0,7), (-1,7), colors.HexColor("#DCFCE7")),
            ("BACKGROUND", (0,14), (-1,14), colors.HexColor("#DCFCE7")),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("GRID", (0,0), (-1,-1), 0.5, colors.lightgrey),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ])),
        sp(),

        Paragraph("Section 4 — FUND UTILISATION STATEMENT", SEC),
        Paragraph("CSR Grant — TCS Foundation (Rs. 18,50,000) — FY 2023–24", LABEL),
        Table([
            ["Activity", "Sanctioned (Rs.)", "Utilised (Rs.)", "Balance (Rs.)"],
            ["Scholarship Programme", "8,00,000", "7,85,000", "15,000"],
            ["Skill Dev Workshops", "6,50,000", "6,37,500", "12,500"],
            ["Health Camps", "4,00,000", "3,98,000", "2,000"],
            ["TOTAL", "18,50,000", "18,20,500", "29,500"],
        ], colWidths=[6*cm, 3.5*cm, 3.5*cm, 3*cm],
        style=TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E8601A")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("GRID", (0,0), (-1,-1), 0.5, colors.lightgrey),
            ("ALIGN", (1,0), (-1,-1), "RIGHT"),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ])),
        sp(),

        Paragraph("Government Grant — Ministry of WCD (Rs. 12,00,000) — FY 2023–24", LABEL),
        Table([
            ["Activity", "Sanctioned (Rs.)", "Utilised (Rs.)", "Balance (Rs.)"],
            ["Women Skill Dev", "7,00,000", "6,95,000", "5,000"],
            ["Legal Awareness", "5,00,000", "4,87,000", "13,000"],
            ["TOTAL", "12,00,000", "11,82,000", "18,000"],
        ], colWidths=[6*cm, 3.5*cm, 3.5*cm, 3*cm],
        style=TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E8601A")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("GRID", (0,0), (-1,-1), 0.5, colors.lightgrey),
            ("ALIGN", (1,0), (-1,-1), "RIGHT"),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ])),
        sp(2),

        Paragraph("Priya Sharma", LABEL),
        Paragraph("Secretary, Asha Jyoti Welfare Foundation", BODY),
        Paragraph("Date: 30 June 2024", BODY),
    ]
    d.build(story)
    return path


# ═══════════════════════════════════════════════════════════════════
# DOC 7 — AUDITED FINANCIAL STATEMENTS
# ═══════════════════════════════════════════════════════════════════
def doc7_audit():
    d, path = doc("07_audited_financial_statements.pdf", "Audit")
    story = [
        Paragraph("ASHA JYOTI WELFARE FOUNDATION", HEAD),
        Paragraph("AUDITED FINANCIAL STATEMENTS — Year Ended 31 March 2024", SUB),
        Paragraph("PAN: AAETA2384K  |  Registration No.: E-23847/2019", SMALL),
        hr(), sp(),

        Paragraph("INDEPENDENT AUDITOR'S REPORT", SEC),
        Paragraph("To the Trustees of Asha Jyoti Welfare Foundation", LABEL),
        Paragraph("""We have audited the accompanying financial statements of Asha Jyoti Welfare Foundation
for the year ended 31st March 2024, which comprise the Balance Sheet as at 31st March 2024
and the Income and Expenditure Account for the year then ended.""", BODY),
        Paragraph("""In our opinion and to the best of our information and according to the explanations
given to us, the said financial statements give a true and fair view of the state of affairs
of the Foundation as at 31st March 2024.""", BODY),
        sp(),
        Paragraph("M/s Mehta and Associates", LABEL),
        Paragraph("Chartered Accountants", BODY),
        Paragraph("ICAI Firm Registration No.: 112847W", BODY),
        Paragraph("Membership No.: CA-384721", BODY),
        Paragraph("Date: 25 July 2024  |  Place: Pune", BODY),
        sp(),

        Paragraph("BALANCE SHEET as at 31 March 2024", SEC),
        Table([
            ["LIABILITIES", "Rs.", "ASSETS", "Rs."],
            ["Corpus Fund", "25,00,000", "Fixed Assets", "6,50,000"],
            ["General Reserves", "8,44,935", "Bank — Current A/c", "12,18,935"],
            ["CSR Grant Utilisation", "18,50,000", "Bank — FCRA A/c (SBI)", "6,50,000"],
            ["Govt Grant Utilisation", "12,00,000", "Cash in Hand", "38,000"],
            ["Creditors", "72,000", "Advances and Deposits", "3,60,000"],
            ["", "", "Prepaid Expenses", "1,50,000"],
            ["TOTAL", "64,66,935", "TOTAL", "30,66,935"],
        ], colWidths=[5.5*cm, 3*cm, 5.5*cm, 3*cm],
        style=TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1A3A6B")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("GRID", (0,0), (-1,-1), 0.5, colors.lightgrey),
            ("ALIGN", (1,0), (1,-1), "RIGHT"),
            ("ALIGN", (3,0), (3,-1), "RIGHT"),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ])),
        sp(),

        Paragraph("INCOME AND EXPENDITURE ACCOUNT — Year ended 31 March 2024", SEC),
        Table([
            ["INCOME", "Rs.", "EXPENDITURE", "Rs."],
            ["Domestic Donations", "18,45,000", "Scholarship Disbursements", "8,40,000"],
            ["CSR Grant Received", "18,50,000", "Programme Expenses", "14,22,500"],
            ["Govt Grant Received", "12,00,000", "Salaries and Staff", "9,85,000"],
            ["Interest Income", "38,420", "Admin Expenses", "2,14,300"],
            ["", "", "Audit and Legal Fees", "85,000"],
            ["TOTAL INCOME", "49,33,420", "TOTAL EXPENDITURE", "35,46,800"],
            ["", "", "Surplus for the year", "13,86,620"],
        ], colWidths=[5.5*cm, 3*cm, 5.5*cm, 3*cm],
        style=TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1A3A6B")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTNAME", (0,6), (1,6), "Helvetica-Bold"),
            ("FONTNAME", (2,6), (3,6), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("GRID", (0,0), (-1,-1), 0.5, colors.lightgrey),
            ("ALIGN", (1,0), (1,-1), "RIGHT"),
            ("ALIGN", (3,0), (3,-1), "RIGHT"),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ])),
        sp(),

        Paragraph("FCRA FUND AUDIT — Under Rule 17 of FCRA Rules, 2011", SEC),
        Paragraph("""Separate FCRA Audit Report in accordance with Rule 17 of the Foreign Contribution
(Regulation) Rules, 2011 for the year ended 31 March 2024:""", BODY),
        Table([
            ["FCRA Account Details", ""],
            ["Bank", "State Bank of India, New Delhi Main Branch"],
            ["Account Number", "40021983748"],
            ["Opening Balance (01 Apr 2023)", "Rs. 2,14,500"],
            ["Foreign Contributions Received", "Rs. 8,72,000"],
            ["Amount Utilised for Stated Purpose", "Rs. 7,98,500"],
            ["Closing Balance (31 Mar 2024)", "Rs. 2,88,000"],
            ["FC-4 Return Filed", "Yes — filed 28 December 2024"],
        ], colWidths=[8*cm, 8*cm],
        style=TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E8601A")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTNAME", (0,1), (0,-1), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("GRID", (0,0), (-1,-1), 0.5, colors.lightgrey),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ])),
        sp(),
        Paragraph("""We certify that the FCRA funds have been received, maintained and utilised in
accordance with the provisions of FCRA 2010 and FCRA Rules 2011. A separate FCRA
designated bank account has been maintained at State Bank of India, New Delhi Main Branch
as required under Section 17 of FCRA 2010 as amended.""", BODY),
        sp(),
        Paragraph("M/s Mehta and Associates  |  ICAI Reg. No.: 112847W", LABEL),
        Paragraph("Date: 25 July 2024", BODY),
    ]
    d.build(story)
    return path


# ═══════════════════════════════════════════════════════════════════
# DOC 8 — PAN CARD
# ═══════════════════════════════════════════════════════════════════
def doc8_pan():
    d, path = doc("08_pan_card.pdf", "PAN")
    story = [
        Paragraph("INCOME TAX DEPARTMENT — GOVERNMENT OF INDIA", HEAD),
        Paragraph("PERMANENT ACCOUNT NUMBER CARD", SUB),
        hr(), sp(2),

        Paragraph("PERMANENT ACCOUNT NUMBER", LABEL),
        Paragraph("AAETA2384K", S("PAN_NUM", fontSize=24,
                  fontName="Helvetica-Bold", alignment=TA_CENTER,
                  textColor=colors.HexColor("#1A3A6B"), spaceAfter=12)),
        sp(),

        Table([
            ["Name of Trust / Organisation:", "ASHA JYOTI WELFARE FOUNDATION"],
            ["Date of Incorporation:",         "14/03/2019"],
            ["Status:",                        "AOP (Trust)"],
            ["Father's / Founder's Name:",     "Priya Sharma (Secretary / Founder)"],
        ], colWidths=[7*cm, 9*cm],
        style=TableStyle([
            ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 11),
            ("TOPPADDING", (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("LINEBELOW", (0,0), (-1,-2), 0.5, colors.lightgrey),
        ])),
        sp(3),
        Paragraph("Issued by: Income Tax Department, Government of India", SMALL),
        Paragraph("This PAN is issued under Section 139A of the Income Tax Act, 1961.", SMALL),
    ]
    d.build(story)
    return path


# ═══════════════════════════════════════════════════════════════════
# GENERATE ALL
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    files = [
        ("Trust Deed",               doc1_trust_deed),
        ("Registration Certificate", doc2_reg_cert),
        ("12A Certificate",          doc3_12a),
        ("80G Certificate",          doc4_80g),
        ("FCRA Certificate",         doc5_fcra),
        ("Annual Report 2023-24",    doc6_annual_report),
        ("Audited Financial Stmts",  doc7_audit),
        ("PAN Card",                 doc8_pan),
    ]
    print("\nGenerating demo NGO documents...\n")
    for name, fn in files:
        path = fn()
        print(f"  OK  {name}")
        print(f"      {path}")
    print(f"\nAll 8 documents saved to: {OUT}/")
    print("\nDemo NGO: Asha Jyoti Welfare Foundation")
    print("State: Maharashtra | Type: Public Trust | PAN: AAETA2384K")
