import {
  Shield,
  Building2,
  Users,
  DollarSign,
  Receipt,
  Globe,
  BarChart2,
} from "lucide-react";

export const THEME = {
  OR: "#E8601A",
  NV: "#1A3A6B",
  GR: "#16A34A",
  RD: "#DC2626",
  AM: "#D97706",
  BG: "#F4F6FA",
  WH: "#FFFFFF",
  BD: "#E2E8F0",
  MT: "#64748B",
  TX: "#1E293B",
};

export const NGO = {
  name: "Asha Jyoti Welfare Foundation",
  id: "MH/2019/0234521",
  state: "Maharashtra",
  type: "Public Trust",
  reg: "E-23847/2019",
  pan: "AAETA2384K",
  sector: "Education & Women Empowerment",
  by: "Priya Sharma (Secretary)",
  date: "14 March 2019",
  city: "Pune, Maharashtra",
};

export const DOCS = [
  { name: "Trust Deed", cat: "Registration", size: "2.4 MB", pages: 18, ok: true },
  {
    name: "Charity Commissioner Certificate",
    cat: "Registration",
    size: "1.1 MB",
    pages: 2,
    ok: true,
  },
  { name: "12A Certificate", cat: "Tax", size: "0.8 MB", pages: 3, ok: true },
  { name: "80G Certificate", cat: "Tax", size: "0.7 MB", pages: 3, ok: true },
  { name: "Annual Report 2024–25", cat: "Financial", size: "3.2 MB", pages: 42, ok: true },
  { name: "FCRA Certificate", cat: "FCRA", size: "0.9 MB", pages: 4, ok: true },
  {
    name: "Audited Financial Statements",
    cat: "Audit",
    size: "4.1 MB",
    pages: 56,
    ok: true,
  },
];

export const FINDINGS = [
  {
    id: 1,
    dim: "Registration & Legal Status",
    icon: Shield,
    status: "PASS",
    conf: 0.95,
    route: "auto",
    citation: "Section 18, Bombay Public Trusts Act, 1950; Maharashtra Charity Commissioner Guidelines, 2018",
    evidence:
      "Trust Deed dated 14 March 2019 confirms registration under Bombay Public Trusts Act, 1950. Certificate No. MH-CC-2019-23847 issued. Registration current and valid.",
    reasoning:
      "Trust Deed clearly establishes registration under BPT Act 1950. Charity Commissioner certificate matches reg number. All mandatory fields present and consistent.",
  },
  {
    id: 2,
    dim: "Governance Structure",
    icon: Building2,
    status: "PASS",
    conf: 0.89,
    route: "auto",
    citation: "Section 2(13) & Section 14, Bombay Public Trusts Act, 1950 — Composition of Board of Trustees",
    evidence:
      "Trust Deed lists 5 trustees: President, Secretary, Treasurer and 2 members. Board composition documented with names, addresses and designations.",
    reasoning:
      "Governing body satisfies Section 14 requirements. No related-party concentration issues. Quorum requirements clearly stated in Trust Deed.",
  },
  {
    id: 3,
    dim: "Membership Requirements",
    icon: Users,
    status: "UNCERTAIN",
    conf: 0.64,
    route: "human",
    qStatus: "pending",
    officer: "Officer Ramesh K.",
    role: "Sr. Compliance Officer",
    citation: "Section 4, BPT Act, 1950; Maharashtra Charity Commissioner Circular No. 12/2021",
    evidence:
      "Trust Deed lists 5 trustees. However Circular 12/2021 may impose additional sector-specific requirements. OCR extraction on page 4 of Trust Deed incomplete.",
    reasoning:
      "Base trustee count meets minimum statutory requirements. However a 2021 circular for education-sector trusts could not be fully assessed due to partial OCR on page 4. Human review recommended.",
  },
  {
    id: 4,
    dim: "Financial Compliance",
    icon: DollarSign,
    status: "FAIL",
    conf: 0.91,
    route: "auto",
    citation: "Section 32 & 33, Bombay Public Trusts Act, 1950; NGO Darpan Guidelines Clause 7.2",
    evidence:
      "Annual Report 2024–25 submitted. Fund utilisation statement for CSR grant FY 2023–24 (₹18.5L from TCS Foundation) is ABSENT from submitted documents.",
    reasoning:
      "NGO received CSR funding in FY 2023–24 but mandatory fund utilisation statement is missing. Section 32 requires detailed accounts for all receipts above ₹10,000. Critical compliance gap.",
    fix: "Submit fund utilisation statement for FY 2023–24 (₹18.5L CSR grant, TCS Foundation) under Section 32, Bombay Public Trusts Act. File with Charity Commissioner and upload to Darpan portal under 'Grant Utilisation'.",
  },
  {
    id: 5,
    dim: "Tax Compliance",
    icon: Receipt,
    status: "PASS",
    conf: 0.93,
    route: "auto",
    citation: "Section 12A & 80G, Income Tax Act, 1961 — Tax Exemption for Charitable Organisations",
    evidence:
      "12A Certificate No. IT-12A-MH-2019-4821 valid until 31 March 2028. 80G Certificate valid until 31 March 2028. Both verified against IT records.",
    reasoning:
      "Both certificates valid and within renewal window. Certificate numbers, NGO name and PAN match across all submitted documents. No pending IT notices.",
  },
  {
    id: 6,
    dim: "FCRA Compliance",
    icon: Globe,
    status: "PASS",
    conf: 0.88,
    route: "auto",
    citation: "Section 11 & 17, FCRA 2010; FCRA Amendment Rules, 2020",
    evidence:
      "FCRA Reg. No. 083780142 granted by MHA. Annual return filed for FY 2024–25. Designated FCRA bank account with SBI (A/C ending 4892) maintained.",
    reasoning:
      "FCRA registration valid. Annual returns filed. Dedicated FCRA bank account maintained as mandated by 2020 amendment rules.",
  },
  {
    id: 7,
    dim: "Audit Requirements",
    icon: BarChart2,
    status: "UNCERTAIN",
    conf: 0.71,
    route: "human",
    qStatus: "reviewed",
    officer: "Officer Lakshmi T.",
    role: "FCRA Specialist",
    determination: "PASS",
    reviewedAt: "23 Jun 2026, 3:45 PM",
    officerNotes:
      "FCRA audit report found on page 12 of the combined audit document. Header was unclear due to scan quality but content is complete and compliant. Confirmed PASS.",
    citation: "Section 33, BPT Act 1950; FCRA Rules 2011, Rule 17 — Audit of FCRA Accounts",
    evidence:
      "Audited statements submitted. Auditor: M/s Mehta & Associates (ICAI Reg. 112847). Separate FCRA audit under Rule 17 not clearly identified in submitted documents.",
    reasoning:
      "General audit report present from registered CA firm. However FCRA Rule 17 requires a separate audit for foreign contribution accounts not clearly identified. Human review recommended.",
  },
];

export const STEPS = [
  "Receiving uploaded documents (7 files · 13.2 MB)",
  "Extracting text with PyMuPDF…",
  "Running Tesseract OCR — lang: eng+mar",
  "Structured field extraction (names, dates, reg numbers)",
  "Querying legal corpus — Maharashtra Acts · FCRA · IT Act",
  "Assessing 7 compliance dimensions via RAG + LLM",
  "Routing 2 findings to Human Review Queue",
  "Generating compliance report",
];

export const STATES = [
  {
    code: "MH",
    name: "Maharashtra",
    acts: [
      "Bombay Public Trusts Act, 1950",
      "Societies Registration Act (MH)",
      "Charity Commissioner Rules",
    ],
    complexity: "High",
    ngos: "2,84,000+",
  },
  {
    code: "DL",
    name: "Delhi",
    acts: [
      "Delhi Societies Registration Act, 2006",
      "Delhi Public Charitable Trust",
      "NITI Aayog Darpan Guidelines",
    ],
    complexity: "Medium",
    ngos: "96,000+",
  },
  {
    code: "KA",
    name: "Karnataka",
    acts: [
      "Karnataka Societies Registration Act, 1960",
      "Karnataka Public Trust Act",
      "Charity Commissioner (KA) Rules",
    ],
    complexity: "Medium",
    ngos: "1,12,000+",
  },
  {
    code: "RJ",
    name: "Rajasthan",
    acts: [
      "Rajasthan Societies Registration Act, 1958",
      "Rajasthan Public Trusts Act",
      "Rajasthan Charity Commissioner Rules",
    ],
    complexity: "Medium",
    ngos: "78,000+",
  },
];

export const DIR_DATA = [
  {
    name: "Asha Jyoti Welfare Foundation",
    state: "Maharashtra",
    type: "Public Trust",
    sector: "Education & Women Empowerment",
    reg: "E-23847/2019",
    score: 74,
    cStatus: "partial",
    vStatus: "Partially Verified",
  },
  {
    name: "Delhi Shiksha Samiti",
    state: "Delhi",
    type: "Society",
    sector: "Education",
    reg: "S-11234/2018",
    score: null,
    cStatus: "unverified",
    vStatus: "Unverified",
  },
  {
    name: "Karnataka Arogya Trust",
    state: "Karnataka",
    type: "Public Trust",
    sector: "Health",
    reg: "KA-T-8821/2020",
    score: 91,
    cStatus: "verified",
    vStatus: "Verified",
  },
  {
    name: "Rajasthan Gramin Vikas Sangh",
    state: "Rajasthan",
    type: "Society",
    sector: "Rural Development",
    reg: "RJ-S-4412/2017",
    score: null,
    cStatus: "unverified",
    vStatus: "Unverified",
  },
  {
    name: "Mumbai Women Empowerment Trust",
    state: "Maharashtra",
    type: "Public Trust",
    sector: "Women Empowerment",
    reg: "E-19023/2021",
    score: 88,
    cStatus: "verified",
    vStatus: "Verified",
  },
  {
    name: "Bengaluru Youth Foundation",
    state: "Karnataka",
    type: "Section 8 Company",
    sector: "Youth & Sports",
    reg: "CIN-U85300KA2019",
    score: 62,
    cStatus: "partial",
    vStatus: "Partially Verified",
  },
  {
    name: "Delhi Environmental Society",
    state: "Delhi",
    type: "Society",
    sector: "Environment",
    reg: "S-9934/2016",
    score: null,
    cStatus: "unverified",
    vStatus: "Unverified",
  },
  {
    name: "Jaipur Bal Vikas Sanstha",
    state: "Rajasthan",
    type: "Society",
    sector: "Child Welfare",
    reg: "RJ-S-7721/2019",
    score: 79,
    cStatus: "partial",
    vStatus: "Partially Verified",
  },
];

export function getComplianceData() {
  return {
    NGO,
    DOCS,
    FINDINGS,
    STEPS,
    STATES,
    DIR_DATA,
    THEME,
  };
}
