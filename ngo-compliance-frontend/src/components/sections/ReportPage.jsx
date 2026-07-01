import { Download } from "lucide-react";
import { THEME, NGO, FINDINGS } from "@/lib/api";
import Crumb from "@/components/sections/Crumb";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Bar from "@/components/ui/Bar";
import Ring from "@/components/ui/Ring";

export default function ReportPage({ go }) {
  const auto = FINDINGS.filter((finding) => finding.route === "auto");
  const human = FINDINGS.filter((finding) => finding.route === "human");
  const statusRow = [
    ["Registration & Legal Status", "PASS", THEME.GR],
    ["Governance Structure", "PASS", THEME.GR],
    ["Membership Requirements", "UNCERTAIN", THEME.AM],
    ["Financial Compliance", "FAIL", THEME.RD],
    ["Tax Compliance", "PASS", THEME.GR],
    ["FCRA Compliance", "PASS", THEME.GR],
    ["Audit Requirements", "PASS (Officer)", THEME.GR],
  ];

  return (
    <div style={{ background: THEME.BG, minHeight: "100vh" }}>
      <Crumb items={[{ label: "Home", page: "landing" }, { label: "Dashboard", page: "dashboard" }, { label: "Final Report" }]} go={go} />

      <div style={{ background: THEME.WH, borderBottom: `1px solid ${THEME.BD}`, padding: "8px 20px" }}>
        <div style={{ maxWidth: 940, margin: "0 auto", display: "flex", justifyContent: "flex-end", gap: 7 }}>
          <button style={{ background: THEME.WH, color: THEME.NV, border: `1px solid ${THEME.BD}`, borderRadius: 6, padding: "6px 12px", fontSize: 12, cursor: "pointer" }}>🖨 Print</button>
          <button style={{ background: THEME.OR, color: THEME.WH, border: "none", borderRadius: 6, padding: "6px 14px", fontSize: 12, fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", gap: 5 }}><Download size={13} />Download PDF</button>
        </div>
      </div>

      <div style={{ maxWidth: 940, margin: "0 auto", padding: "18px 20px" }}>
        <Card s={{ marginBottom: 14, background: "linear-gradient(135deg,#1A3A6B,#0F2451)", border: "none" }}>
          <div style={{ display: "flex", gap: 20, alignItems: "center" }}>
            <Ring score={74} />
            <div style={{ flex: 1 }}>
              <div style={{ color: THEME.OR, fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 4 }}>NITI AAYOG · NGO DARPAN COMPLIANCE VERIFICATION SYSTEM · CONFIDENTIAL</div>
              <h2 style={{ color: THEME.WH, fontSize: 17, fontWeight: 800, margin: "0 0 2px" }}>{NGO.name}</h2>
              <div style={{ color: "#94A3B8", fontSize: 12, marginBottom: 10 }}>Reg: {NGO.reg} · PAN: {NGO.pan}</div>
              <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
                {[['State', NGO.state], ['Type', NGO.type], ['Sector', NGO.sector], ['Assessment Date', '24 Jun 2026'], ['Submitted By', NGO.by]].map(([label, value]) => (
                  <div key={label}><div style={{ color: "#64748B", fontSize: 9, textTransform: "uppercase" }}>{label}</div><div style={{ color: "#CBD5E1", fontSize: 11, fontWeight: 500 }}>{value}</div></div>
                ))}
              </div>
            </div>
            <div style={{ background: "rgba(251,191,36,.12)", border: "1px solid rgba(251,191,36,.3)", borderRadius: 9, padding: "12px 14px", flexShrink: 0, textAlign: "center" }}>
              <div style={{ color: "#FCD34D", fontWeight: 700, fontSize: 13 }}>⚠ Not Grant Ready</div>
              <div style={{ color: "#FDE68A", fontSize: 11, marginTop: 4, lineHeight: 1.5 }}>Resolve 1 critical<br />failure + 1 pending</div>
            </div>
          </div>
        </Card>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 280px", gap: 14, marginBottom: 14 }}>
          <Card>
            <div style={{ fontSize: 12, fontWeight: 700, color: THEME.NV, marginBottom: 12, textTransform: "uppercase", letterSpacing: "0.05em" }}>Compliance Status Overview</div>
            {statusRow.map(([label, state, color]) => (
              <div key={label} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "7px 0", borderBottom: `1px solid ${THEME.BD}` }}>
                <span style={{ fontSize: 13, color: THEME.TX }}>{label}</span>
                <span style={{ fontSize: 11, fontWeight: 700, color }}>{state}</span>
              </div>
            ))}
          </Card>

          <div style={{ display: "grid", gap: 10, alignContent: "start" }}>
            <div style={{ background: "#FEE2E2", border: "1px solid #FCA5A5", borderRadius: 8, padding: 12 }}>
              <div style={{ fontWeight: 700, color: THEME.RD, fontSize: 12, marginBottom: 4 }}>Critical — Action Required</div>
              <div style={{ fontSize: 11, color: THEME.RD, lineHeight: 1.55 }}>Submit fund utilisation statement for FY 2023–24 CSR grant (₹18.5L, TCS Foundation) with Charity Commissioner, Maharashtra.</div>
            </div>
            <div style={{ background: "#FEF3C7", border: "1px solid #FDE68A", borderRadius: 8, padding: 12 }}>
              <div style={{ fontWeight: 700, color: THEME.AM, fontSize: 12, marginBottom: 4 }}>Pending Review</div>
              <div style={{ fontSize: 11, color: THEME.AM, lineHeight: 1.55 }}>Membership Requirements — awaiting Officer Ramesh K. re: Circular 12/2021.</div>
            </div>
            <div style={{ background: "#ECFDF5", border: "1px solid #A7F3D0", borderRadius: 8, padding: 12 }}>
              <div style={{ fontWeight: 600, color: THEME.GR, fontSize: 11 }}>✓ Registration, Tax, FCRA, Governance and Audit requirements satisfied.</div>
            </div>
          </div>
        </div>

        <div style={{ marginBottom: 14 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
            <span style={{ background: "#EEF2FF", color: "#4F46E5", padding: "4px 12px", borderRadius: 6, fontSize: 11, fontWeight: 700 }}>AI ASSESSED</span>
            <span style={{ fontSize: 12, color: THEME.MT }}>{auto.length} findings · automated · high confidence</span>
          </div>
          <div style={{ display: "grid", gap: 7 }}>
            {auto.map((finding) => {
              const color = finding.status === "PASS" ? THEME.GR : THEME.RD;
              return (
                <div key={finding.id} style={{ background: THEME.WH, borderRadius: 8, border: `1px solid ${THEME.BD}`, borderLeft: `4px solid ${color}`, padding: "12px 16px", display: "flex", gap: 12, alignItems: "flex-start" }}>
                  <Badge s={finding.status} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 700, color: THEME.NV, fontSize: 13, marginBottom: 3 }}>{finding.dim}</div>
                    <div style={{ fontSize: 11, color: THEME.MT, marginBottom: 5 }}>Confidence: {Math.round(finding.conf * 100)}% · {finding.citation}</div>
                    <div style={{ fontSize: 12, color: THEME.TX, lineHeight: 1.55 }}>{finding.reasoning}</div>
                    {finding.status === "FAIL" && <div style={{ marginTop: 7, background: "#FEE2E2", borderRadius: 5, padding: "6px 10px", fontSize: 11, color: THEME.RD }}>⚠ Action Required: {finding.fix}</div>}
                  </div>
                  <div style={{ textAlign: "right", minWidth: 90, flexShrink: 0 }}>
                    <div style={{ fontSize: 10, color: THEME.MT, marginBottom: 3 }}>Confidence</div>
                    <Bar v={finding.conf} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div style={{ marginBottom: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
            <span style={{ background: "#ECFDF5", color: THEME.GR, padding: "4px 12px", borderRadius: 6, fontSize: 11, fontWeight: 700 }}>OFFICER REVIEWED</span>
            <span style={{ fontSize: 12, color: THEME.MT }}>{human.length} findings · reviewed by designated compliance officers</span>
          </div>
          <div style={{ display: "grid", gap: 7 }}>
            {human.map((finding) => (
              <div key={finding.id} style={{ background: THEME.WH, borderRadius: 8, border: `1px solid ${THEME.BD}`, borderLeft: `4px solid ${finding.qStatus === "reviewed" ? THEME.GR : THEME.AM}`, padding: "12px 16px" }}>
                <div style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
                  <Badge s={finding.qStatus === "reviewed" ? (finding.determination || "PASS") : finding.status} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 700, color: THEME.NV, fontSize: 13, marginBottom: 2 }}>{finding.dim}</div>
                    <div style={{ fontSize: 11, color: THEME.MT, marginBottom: 6 }}>{finding.qStatus === "reviewed" ? `Reviewed by ${finding.officer} (${finding.role}) · ${finding.reviewedAt}` : `Pending review · ${finding.officer} (${finding.role})`}</div>
                    {finding.qStatus === "reviewed" ? (
                      <div style={{ background: "#ECFDF5", borderRadius: 6, padding: "7px 10px", fontSize: 12, color: THEME.TX }}>{finding.officerNotes}</div>
                    ) : (
                      <div style={{ background: "#FEF3C7", borderRadius: 6, padding: "7px 10px", fontSize: 12, color: THEME.AM }}>⟳ Awaiting officer determination. Report is provisional for this dimension.</div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div style={{ background: "#F8FAFC", border: `1px solid ${THEME.BD}`, borderRadius: 8, padding: "12px 14px", fontSize: 11, color: THEME.MT, lineHeight: 1.7 }}>
          <strong style={{ color: THEME.NV }}>Disclaimer:</strong> This report is generated by an AI-assisted compliance screening system (NGO Darpan Compliance Verification Pilot) and constitutes a decision-support tool, not a legal ruling. All AI findings are subject to review by designated compliance officers. NITI Aayog / NIC does not assume responsibility for automated compliance determinations. Organisations must consult the relevant Registrar or regulatory body for final compliance decisions.
        </div>
      </div>
    </div>
  );
}
