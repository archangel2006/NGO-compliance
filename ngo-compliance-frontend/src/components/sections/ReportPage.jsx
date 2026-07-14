"use client";

import { useEffect, useState } from "react";
import { Download } from "lucide-react";
import { THEME, NGO, FINDINGS, getFindings, getSubmissionDetails } from "@/lib/api";
import Crumb from "@/components/sections/Crumb";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Bar from "@/components/ui/Bar";
import Ring from "@/components/ui/Ring";

export default function ReportPage({ go }) {
  const [findingsState, setFindingsState] = useState([]);
  const [ngoDetails, setNgoDetails] = useState(NGO);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const subId = localStorage.getItem("active_submission_id");
    if (!subId) {
      setFindingsState(FINDINGS);
      setNgoDetails(NGO);
      setLoading(false);
      return;
    }

    const loadData = async () => {
      try {
        const details = await getSubmissionDetails(subId);
        const res = await getFindings(subId);
        
        setNgoDetails({
          name: details.org_name || NGO.name,
          id: details.darpan_id || NGO.id,
          state: details.state ? details.state.toUpperCase() : NGO.state,
          type: details.entity_type || NGO.type,
          reg: details.registration_no || NGO.reg,
          pan: details.pan || NGO.pan,
          sector: details.sector || NGO.sector,
          by: details.submitted_by || NGO.by,
          date: details.created_at ? details.created_at.substring(0, 10) : NGO.date,
          city: NGO.city,
        });

        const mapped = (res.findings || []).map((f) => ({
          id: f.id,
          dim: f.dimension_name,
          dimension_id: f.dimension_id,
          status: f.status,
          conf: f.confidence,
          route: f.routing === "human_review" ? "human" : "auto",
          qStatus: f.human_determination ? "reviewed" : "pending",
          officer: "Officer Ramesh K.",
          role: "Sr. Compliance Officer",
          determination: f.human_determination || null,
          citation: f.legal_citation,
          evidence: f.ngo_evidence,
          reasoning: f.reasoning,
          fix: f.status === "FAIL" ? "Submit the missing files to satisfy the relevant statutory requirement." : null,
          reviewedAt: f.reviewed_at ? new Date(f.reviewed_at).toLocaleString() : ""
        }));
        setFindingsState(mapped.length ? mapped : FINDINGS);
      } catch (err) {
        console.error("Report data load failed, using fallbacks:", err);
        setFindingsState(FINDINGS);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const auto = findingsState.filter((finding) => finding.route === "auto");
  const human = findingsState.filter((finding) => finding.route === "human");
  
  const pass = findingsState.filter((finding) => finding.status === "PASS").length;
  const fail = findingsState.filter((finding) => finding.status === "FAIL").length;
  const uncertain = findingsState.filter((finding) => finding.status === "UNCERTAIN").length;
  const overallScore = loading ? 74 : Math.round((pass / (findingsState.length || 7)) * 100);

  const statusRow = findingsState.map((f) => {
    const displayStatus = f.qStatus === "reviewed" ? `${f.determination} (Officer)` : f.status;
    const color = f.status === "PASS" || f.determination === "PASS" ? THEME.GR : f.status === "FAIL" ? THEME.RD : THEME.AM;
    return [f.dim, displayStatus, color];
  });

  return (
    <div style={{ background: THEME.BG, minHeight: "100vh" }}>
      <Crumb items={[{ label: "Home", page: "landing" }, { label: "Dashboard", page: "dashboard" }, { label: "Final Report" }]} go={go} />

      <div style={{ background: THEME.WH, borderBottom: `1px solid ${THEME.BD}`, padding: "8px 20px" }}>
        <div style={{ maxWidth: 940, margin: "0 auto", display: "flex", justifyContent: "flex-end", gap: 7 }}>
          <button onClick={() => window.print()} style={{ background: THEME.WH, color: THEME.NV, border: `1px solid ${THEME.BD}`, borderRadius: 6, padding: "6px 12px", fontSize: 12, cursor: "pointer" }}>🖨 Print</button>
          <button onClick={() => window.open(`http://localhost:8000/submissions/${localStorage.getItem("active_submission_id")}/report/pdf`)} style={{ background: THEME.OR, color: THEME.WH, border: "none", borderRadius: 6, padding: "6px 14px", fontSize: 12, fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", gap: 5 }}><Download size={13} />Download PDF</button>
        </div>
      </div>

      <div style={{ maxWidth: 940, margin: "0 auto", padding: "18px 20px" }}>
        <Card s={{ marginBottom: 14, background: "linear-gradient(135deg,#1A3A6B,#0F2451)", border: "none" }}>
          <div style={{ display: "flex", gap: 20, alignItems: "center" }}>
            <Ring score={overallScore} />
            <div style={{ flex: 1 }}>
              <div style={{ color: THEME.OR, fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 4 }}>NITI AAYOG · NGO DARPAN COMPLIANCE VERIFICATION SYSTEM · CONFIDENTIAL</div>
              <h2 style={{ color: THEME.WH, fontSize: 17, fontWeight: 800, margin: "0 0 2px" }}>{ngoDetails.name}</h2>
              <div style={{ color: "#94A3B8", fontSize: 12, marginBottom: 10 }}>Reg: {ngoDetails.reg} · PAN: {ngoDetails.pan}</div>
              <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
                {[['State', ngoDetails.state], ['Type', ngoDetails.type], ['Sector', ngoDetails.sector], ['Assessment Date', ngoDetails.date], ['Submitted By', ngoDetails.by]].map(([label, value]) => (
                  <div key={label}><div style={{ color: "#64748B", fontSize: 9, textTransform: "uppercase" }}>{label}</div><div style={{ color: "#CBD5E1", fontSize: 11, fontWeight: 500 }}>{value}</div></div>
                ))}
              </div>
            </div>
            <div style={{ background: "rgba(251,191,36,.12)", border: "1px solid rgba(251,191,36,.3)", borderRadius: 9, padding: "12px 14px", flexShrink: 0, textAlign: "center" }}>
              <div style={{ color: "#FCD34D", fontWeight: 700, fontSize: 13 }}>{overallScore >= 85 ? "✓ Grant Ready" : "⚠ Action Needed"}</div>
              <div style={{ color: "#FDE68A", fontSize: 11, marginTop: 4, lineHeight: 1.5 }}>
                {overallScore >= 85 ? "Compliant and fit\nfor grants." : `Resolve ${fail} critical\nfailure + ${uncertain} pending`}
              </div>
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
            {fail > 0 && (
              <div style={{ background: "#FEE2E2", border: "1px solid #FCA5A5", borderRadius: 8, padding: 12 }}>
                <div style={{ fontWeight: 700, color: THEME.RD, fontSize: 12, marginBottom: 4 }}>Critical — Action Required</div>
                <div style={{ fontSize: 11, color: THEME.RD, lineHeight: 1.55 }}>Submit all compliance documents to resolve critical dimension failures.</div>
              </div>
            )}
            {uncertain > 0 && (
              <div style={{ background: "#FEF3C7", border: "1px solid #FDE68A", borderRadius: 8, padding: 12 }}>
                <div style={{ fontWeight: 700, color: THEME.AM, fontSize: 12, marginBottom: 4 }}>Pending Review</div>
                <div style={{ fontSize: 11, color: THEME.AM, lineHeight: 1.55 }}>Awaiting officer determinations on routed uncertain dimensions.</div>
              </div>
            )}
            {fail === 0 && uncertain === 0 && (
              <div style={{ background: "#ECFDF5", border: "1px solid #A7F3D0", borderRadius: 8, padding: 12 }}>
                <div style={{ fontWeight: 600, color: THEME.GR, fontSize: 11 }}>✓ All checked compliance dimensions successfully satisfied.</div>
              </div>
            )}
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
