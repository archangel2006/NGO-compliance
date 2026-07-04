export default function DimensionsCard() {
  const NV = "#1A3A6B", OR = "#E8601A", BG = "#F4F6FA", WH = "#FFFFFF";
  const MT = "#64748B", TX = "#1E293B", BD = "#E2E8F0";
  const GR = "#16A34A", AM = "#D97706";

  const dims = [
    {
      n: 1, icon: "🏛️", title: "Registration & Legal Status",
      question: "Is the NGO legally registered as what it claims to be?",
      checks: ["Correct Act for the state (BPT Act / Societies Act / Section 8)", "Valid registration number from registering authority", "Maharashtra: dual registration under two Acts mandatory"],
      law: "BPT Act §18, Societies Registration Act §1-3",
      risk: "High", docs: "Trust Deed / Registration Certificate"
    },
    {
      n: 2, icon: "🏢", title: "Governance Structure",
      question: "Does the board meet minimum legal composition requirements?",
      checks: ["Named office bearers — President, Secretary, Treasurer", "Minimum governing body size defined", "Quorum requirements stated in governing document"],
      law: "BPT Act §2(13), §14 · Societies Act §2",
      risk: "High", docs: "Trust Deed / MOA / Rules & Regulations"
    },
    {
      n: 3, icon: "👥", title: "Membership Requirements",
      question: "Does member count meet the state's legal minimum?",
      checks: ["Rajasthan: minimum 10 members (§4, Raj. Societies Act 1958)", "Most states: minimum 7 members (Societies Act 1860)", "Member names, addresses, occupations on record"],
      law: "Societies Act 1860 §1 · Rajasthan Act 1958 §4",
      risk: "Medium", docs: "MOA / Trust Deed / Member Register"
    },
    {
      n: 4, icon: "💰", title: "Financial Compliance",
      question: "Are all funds — especially grants — properly accounted for?",
      checks: ["Fund utilisation statement for each grant received", "Receipts above ₹10,000 require itemized accounting", "CSR and government grant statements mandatory"],
      law: "BPT Act §32, §33 · NGO Darpan Guidelines §7.2",
      risk: "Critical", docs: "Annual Report / Fund Utilisation Statements"
    },
    {
      n: 5, icon: "📋", title: "Tax Compliance (12A / 80G)",
      question: "Are income tax exemption certificates current and consistent?",
      checks: ["12A / 12AB certificate valid and not expired", "80G certificate valid (renewable every 5 years since 2021)", "PAN on certificate matches NGO PAN across all documents"],
      law: "Income Tax Act §12A, §12AB, §80G",
      risk: "High", docs: "12A Certificate / 80G Certificate / PAN"
    },
    {
      n: 6, icon: "🌐", title: "FCRA Compliance",
      question: "Is the NGO authorised to receive and account for foreign funds?",
      checks: ["Valid FCRA registration number (5-year renewal)", "Designated SBI account — New Delhi Main Branch only", "FC-4 annual return filed for last financial year"],
      law: "FCRA 2010 §11, §17 · FCRA Amendment Rules 2020",
      risk: "Critical", docs: "FCRA Certificate / Bank Account Details / FC-4"
    },
    {
      n: 7, icon: "📊", title: "Audit Requirements",
      question: "Have accounts been properly audited by a registered CA?",
      checks: ["Auditor holds valid ICAI registration number", "Audited balance sheet + income & expenditure submitted", "FCRA-receiving NGOs: separate FCRA audit under Rule 17"],
      law: "BPT Act §33 · FCRA Rules 2011, Rule 17",
      risk: "Medium", docs: "Audited Financial Statements / FCRA Audit Report"
    },
  ];

  const riskColor = { High: "#D97706", Critical: "#DC2626", Medium: "#16A34A" };
  const riskBg = { High: "#FEF3C7", Critical: "#FEE2E2", Medium: "#DCFCE7" };

  return (
    <div style={{ fontFamily: "'Segoe UI', system-ui, sans-serif", background: BG, minHeight: "100vh", padding: "28px 24px" }}>
      {/* Header */}
      <div style={{ maxWidth: 1100, margin: "0 auto 24px" }}>
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", flexWrap: "wrap", gap: 12 }}>
          <div>
            <div style={{ fontSize: 11, fontWeight: 700, color: OR, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6 }}>
              NGO COMPLIANCE VERIFICATION SYSTEM · PILOT
            </div>
            <h1 style={{ margin: 0, fontSize: 26, fontWeight: 800, color: NV, lineHeight: 1.2 }}>
              Compliance Framework
            </h1>
            <p style={{ margin: "6px 0 0", fontSize: 13, color: MT, maxWidth: 600 }}>
              7 stable dimensions checked for every NGO regardless of state. Legal requirements are retrieved dynamically from the corpus per state — no rules are hardcoded.
            </p>
          </div>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {[["7", "Dimensions"], ["4", "Pilot States"], ["RAG+LLM", "Engine"]].map(([v, l]) => (
              <div key={l} style={{ background: WH, border: `1px solid ${BD}`, borderRadius: 8, padding: "10px 14px", textAlign: "center" }}>
                <div style={{ fontSize: 18, fontWeight: 800, color: OR }}>{v}</div>
                <div style={{ fontSize: 10, color: MT }}>{l}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Central strip */}
        <div style={{ background: NV, borderRadius: 8, padding: "10px 16px", marginTop: 16, display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: OR, textTransform: "uppercase", letterSpacing: "0.08em" }}>Always included (all states):</div>
          {["FCRA 2010 + Amendment Rules 2020", "Income Tax Act — §12A, §12AB, §80G", "Societies Registration Act 1860 (base)", "NGO Darpan Registration Guidelines"].map(t => (
            <div key={t} style={{ background: "rgba(255,255,255,.08)", borderRadius: 4, padding: "3px 10px", fontSize: 11, color: "#C7D7F0" }}>· {t}</div>
          ))}
        </div>
      </div>

      {/* Cards grid */}
      <div style={{ maxWidth: 1100, margin: "0 auto", display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: 14 }}>
        {dims.map(d => (
          <div key={d.n} style={{
            background: WH, borderRadius: 12, border: `1px solid ${BD}`,
            boxShadow: "0 1px 8px rgba(0,0,0,.06)", overflow: "hidden",
            borderTop: `3px solid ${d.risk === "Critical" ? "#DC2626" : d.risk === "High" ? "#D97706" : "#16A34A"}`
          }}>
            {/* Card header */}
            <div style={{ padding: "16px 18px 12px", borderBottom: `1px solid ${BD}` }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 6 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <div style={{ width: 32, height: 32, borderRadius: 8, background: "#FFF3EB", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16 }}>
                    {d.icon}
                  </div>
                  <div style={{ fontSize: 9, fontWeight: 700, color: OR, textTransform: "uppercase", letterSpacing: "0.08em" }}>
                    Dimension {d.n}
                  </div>
                </div>
                <span style={{ background: riskBg[d.risk], color: riskColor[d.risk], fontSize: 10, fontWeight: 700, padding: "3px 9px", borderRadius: 12 }}>
                  {d.risk} Priority
                </span>
              </div>
              <div style={{ fontSize: 15, fontWeight: 700, color: NV, marginBottom: 4 }}>{d.title}</div>
              <div style={{ fontSize: 12, color: MT, fontStyle: "italic" }}>{d.question}</div>
            </div>

            {/* What's checked */}
            <div style={{ padding: "12px 18px" }}>
              <div style={{ fontSize: 10, fontWeight: 700, color: NV, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 7 }}>
                What the system checks
              </div>
              {d.checks.map((c, i) => (
                <div key={i} style={{ display: "flex", gap: 7, marginBottom: 5, alignItems: "flex-start" }}>
                  <div style={{ width: 16, height: 16, borderRadius: "50%", background: NV, color: WH, fontSize: 8, fontWeight: 700, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, marginTop: 1 }}>{i + 1}</div>
                  <span style={{ fontSize: 12, color: TX, lineHeight: 1.5 }}>{c}</span>
                </div>
              ))}
            </div>

            {/* Footer */}
            <div style={{ background: "#F8FAFC", borderTop: `1px solid ${BD}`, padding: "10px 18px", display: "flex", gap: 10, flexWrap: "wrap", justifyContent: "space-between" }}>
              <div>
                <div style={{ fontSize: 9, color: MT, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 2 }}>Legal basis</div>
                <div style={{ fontSize: 11, color: NV, fontWeight: 600 }}>{d.law}</div>
              </div>
              <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: 9, color: MT, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 2 }}>Source documents</div>
                <div style={{ fontSize: 11, color: MT }}>{d.docs}</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* How RAG uses this */}
      <div style={{ maxWidth: 1100, margin: "20px auto 0" }}>
        <div style={{ background: WH, border: `1px solid ${BD}`, borderRadius: 10, padding: "16px 20px", display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16 }}>
          <div>
            <div style={{ fontSize: 11, fontWeight: 700, color: NV, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 6 }}>Per dimension, the engine:</div>
            {["Retrieves relevant law chunks from ChromaDB", "Extracts matching evidence from NGO document", "Local LLM reasons over both and outputs verdict"].map((t, i) => (
              <div key={i} style={{ display: "flex", gap: 7, marginBottom: 5, alignItems: "center" }}>
                <div style={{ width: 20, height: 20, borderRadius: "50%", background: OR, color: WH, fontSize: 10, fontWeight: 700, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>{i + 1}</div>
                <span style={{ fontSize: 12, color: TX }}>{t}</span>
              </div>
            ))}
          </div>
          <div>
            <div style={{ fontSize: 11, fontWeight: 700, color: NV, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 6 }}>Output per dimension:</div>
            {[["✓ PASS", GR, "#DCFCE7"], ["✗ FAIL", "#DC2626", "#FEE2E2"], ["? UNCERTAIN", AM, "#FEF3C7"]].map(([t, c, bg]) => (
              <div key={t} style={{ background: bg, borderRadius: 6, padding: "5px 10px", marginBottom: 5, fontSize: 12, fontWeight: 600, color: c }}>{t} + legal citation + NGO evidence + reasoning</div>
            ))}
          </div>
          <div>
            <div style={{ fontSize: 11, fontWeight: 700, color: NV, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 6 }}>Routing:</div>
            <div style={{ background: "#ECFDF5", borderRadius: 6, padding: "7px 10px", marginBottom: 7, fontSize: 12, color: "#065F46" }}>
              <strong>High confidence</strong> → published to report automatically
            </div>
            <div style={{ background: "#FEF3C7", borderRadius: 6, padding: "7px 10px", fontSize: 12, color: "#78350F" }}>
              <strong>UNCERTAIN / low conf.</strong> → Human Review Queue for officer determination
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
