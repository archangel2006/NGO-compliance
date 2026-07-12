import { Eye, FileText, List } from "lucide-react";
import { THEME, NGO, FINDINGS } from "@/lib/api";
import Crumb from "@/components/sections/Crumb";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Bar from "@/components/ui/Bar";
import Ring from "@/components/ui/Ring";

export default function DashboardPage({ go }) {
  const pass = FINDINGS.filter((finding) => finding.status === "PASS").length;
  const fail = FINDINGS.filter((finding) => finding.status === "FAIL").length;
  const uncertain = FINDINGS.filter((finding) => finding.status === "UNCERTAIN").length;

  return (
    <div style={{ background: THEME.BG, minHeight: "100vh" }}>
      <Crumb items={[{ label: "Home", page: "landing" }, { label: "Compliance Check", page: "submit" }, { label: "Dashboard" }]} go={go} />

      <div style={{ background: THEME.WH, borderBottom: `1px solid ${THEME.BD}`, padding: "8px 20px" }}>
        <div style={{ maxWidth: 1060, margin: "0 auto", display: "flex", justifyContent: "flex-end", gap: 8 }}>
          <button onClick={() => go("findings")} style={{ background: "#EEF2F9", color: THEME.NV, border: "1px solid #C7D7F0", borderRadius: 6, padding: "6px 12px", fontSize: 12, fontWeight: 500, cursor: "pointer", display: "flex", alignItems: "center", gap: 5 }}>
            <List size={13} />Detailed Findings
          </button>
          <button onClick={() => go("queue")} style={{ background: "#FEF3C7", color: THEME.AM, border: "1px solid #FDE68A", borderRadius: 6, padding: "6px 12px", fontSize: 12, fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", gap: 5 }}>
            <Eye size={13} />Human Review Queue
            <span style={{ background: THEME.AM, color: THEME.WH, borderRadius: 10, padding: "0 5px", fontSize: 10 }}>2</span>
          </button>
          <button onClick={() => go("report")} style={{ background: THEME.OR, color: THEME.WH, border: "none", borderRadius: 6, padding: "6px 14px", fontSize: 12, fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", gap: 5 }}>
            <FileText size={13} />Full Report
          </button>
        </div>
      </div>

      <div style={{ maxWidth: 1060, margin: "0 auto", padding: "18px 20px" }}>
        <Card s={{ marginBottom: 16, background: "linear-gradient(135deg,#1A3A6B,#0F2451)", border: "none" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 22 }}>
            <Ring score={74} />
            <div style={{ flex: 1 }}>
              <div style={{ color: THEME.OR, fontSize: 10, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 3 }}>Compliance Assessment · {NGO.state} · {NGO.type}</div>
              <h2 style={{ color: THEME.WH, fontSize: 17, fontWeight: 800, margin: "0 0 3px" }}>{NGO.name}</h2>
              <div style={{ color: "#94A3B8", fontSize: 12, marginBottom: 12 }}>PAN: {NGO.pan} · {NGO.sector}</div>
              <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                {[[pass, "PASSED", "#4ADE80", "rgba(22,163,74,.2)", "rgba(22,163,74,.3)"], [fail, "FAILED", "#FCA5A5", "rgba(220,38,38,.2)", "rgba(220,38,38,.3)"], [uncertain, "UNCERTAIN", "#FCD34D", "rgba(217,119,6,.2)", "rgba(217,119,6,.3)"]].map(([value, label, color, background, border]) => (
                  <div key={label} style={{ background, border: `1px solid ${border}`, borderRadius: 7, padding: "8px 16px", textAlign: "center" }}>
                    <div style={{ color, fontWeight: 900, fontSize: 20, lineHeight: 1 }}>{value}</div>
                    <div style={{ color, fontSize: 9, marginTop: 2, letterSpacing: "0.05em" }}>{label}</div>
                  </div>
                ))}
                <div style={{ background: "rgba(255,255,255,.06)", border: "1px solid rgba(255,255,255,.12)", borderRadius: 7, padding: "8px 16px", textAlign: "center" }}>
                  <div style={{ color: "#CBD5E1", fontWeight: 900, fontSize: 20, lineHeight: 1 }}>7</div>
                  <div style={{ color: "#94A3B8", fontSize: 9, marginTop: 2 }}>TOTAL</div>
                </div>
              </div>
            </div>
            <div style={{ background: "rgba(251,191,36,.1)", border: "1px solid rgba(251,191,36,.3)", borderRadius: 9, padding: "14px 16px", maxWidth: 170, flexShrink: 0 }}>
              <div style={{ color: "#FCD34D", fontWeight: 700, fontSize: 13, marginBottom: 4 }}>⚠ Not Grant Ready</div>
              <div style={{ color: "#FDE68A", fontSize: 12, lineHeight: 1.5 }}>1 critical failure and 1 pending human review must be resolved.</div>
            </div>
          </div>
        </Card>

        <div style={{ background: THEME.WH, borderRadius: 8, border: `1px solid ${THEME.BD}`, padding: "10px 16px", marginBottom: 16, display: "flex", gap: 24, flexWrap: "wrap" }}>
          {[['Organisation', NGO.name], ['State', NGO.state], ['Reg. No.', NGO.reg], ['Sector', NGO.sector], ['Submitted by', NGO.by]].map(([label, value]) => (
            <div key={label}>
              <div style={{ fontSize: 9, color: THEME.MT, textTransform: "uppercase", letterSpacing: "0.05em" }}>{label}</div>
              <div style={{ fontSize: 12, color: THEME.NV, fontWeight: 600 }}>{value}</div>
            </div>
          ))}
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          {FINDINGS.map((finding) => {
            const Icon = finding.icon;
            const color = finding.status === "PASS" ? THEME.GR : finding.status === "FAIL" ? THEME.RD : THEME.AM;
            return (
              <Card key={finding.id} s={{ cursor: "pointer", borderLeft: `4px solid ${color}`, padding: 16 }} onClick={() => go("findings")}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10 }}>
                  <div style={{ display: "flex", gap: 9, alignItems: "center" }}>
                    <div style={{ width: 30, height: 30, borderRadius: 7, background: finding.status === "PASS" ? "#DCFCE7" : finding.status === "FAIL" ? "#FEE2E2" : "#FEF3C7", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                      <Icon size={14} style={{ color }} />
                    </div>
                    <div>
                      <div style={{ fontSize: 13, fontWeight: 700, color: THEME.NV, lineHeight: 1.2 }}>{finding.dim}</div>
                      <div style={{ fontSize: 10, color: THEME.MT, marginTop: 2 }}>{finding.route === "auto" ? "AI Assessed" : finding.qStatus === "reviewed" ? `Reviewed · ${finding.determination}` : "Pending Review"}</div>
                    </div>
                  </div>
                  <Badge s={finding.status} />
                </div>
                <Bar v={finding.conf} />
                <div style={{ marginTop: 9, fontSize: 11, color: THEME.MT, lineHeight: 1.5, display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" }}>{finding.reasoning}</div>
                {finding.status === "FAIL" && <div style={{ marginTop: 8, background: "#FEE2E2", border: "1px solid #FCA5A5", borderRadius: 5, padding: "6px 9px", fontSize: 11, color: THEME.RD }}>⚠ Action Required: Fund utilisation statement missing</div>}
                {finding.route === "human" && finding.qStatus === "pending" && <div style={{ marginTop: 8, background: "#FEF3C7", border: "1px solid #FDE68A", borderRadius: 5, padding: "6px 9px", fontSize: 11, color: THEME.AM }}>⟳ Pending review · {finding.officer}</div>}
                {finding.route === "human" && finding.qStatus === "reviewed" && <div style={{ marginTop: 8, background: "#ECFDF5", border: "1px solid #A7F3D0", borderRadius: 5, padding: "6px 9px", fontSize: 11, color: THEME.GR }}>✓ Reviewed by {finding.officer} → {finding.determination}</div>}
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}
