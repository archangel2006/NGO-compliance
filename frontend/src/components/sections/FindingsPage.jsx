"use client";

import { useEffect, useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import { THEME, NGO, FINDINGS, getFindings } from "@/lib/api";
import Crumb from "@/components/sections/Crumb";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Bar from "@/components/ui/Bar";

export default function FindingsPage({ go }) {
  const [findingsState, setFindingsState] = useState([]);
  const [open, setOpen] = useState(null);
  const [filter, setFilter] = useState("All");

  useEffect(() => {
    const subId = localStorage.getItem("active_submission_id");
    if (!subId) {
      setFindingsState(FINDINGS);
      return;
    }

    getFindings(subId)
      .then((res) => {
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
      })
      .catch((err) => {
        console.error("Error loading findings:", err);
        setFindingsState(FINDINGS);
      });
  }, []);

  const shown = filter === "All" ? findingsState : findingsState.filter((finding) => finding.status === filter);

  return (
    <div style={{ background: THEME.BG, minHeight: "100vh" }}>
      <Crumb items={[{ label: "Home", page: "landing" }, { label: "Dashboard", page: "dashboard" }, { label: "Detailed Findings" }]} go={go} />
      <div style={{ background: THEME.WH, borderBottom: `1px solid ${THEME.BD}`, padding: "8px 20px" }}>
        <div style={{ maxWidth: 960, margin: "0 auto", display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 8 }}>
          <div>
            <span style={{ fontSize: 14, fontWeight: 700, color: THEME.NV }}>{NGO.name}</span>
            <span style={{ fontSize: 12, color: THEME.MT, marginLeft: 8 }}>· 7 dimensions</span>
          </div>
          <div style={{ display: "flex", gap: 5 }}>
            {["All", "PASS", "FAIL", "UNCERTAIN"].map((option) => (
              <button key={option} onClick={() => setFilter(option)} style={{ background: filter === option ? THEME.OR : THEME.WH, color: filter === option ? THEME.WH : THEME.MT, border: `1px solid ${THEME.BD}`, borderRadius: 16, padding: "4px 12px", fontSize: 11, cursor: "pointer", fontWeight: filter === option ? 600 : 400 }}>
                {option}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div style={{ maxWidth: 960, margin: "0 auto", padding: "18px 20px" }}>
        <div style={{ display: "grid", gap: 10 }}>
          {shown.map((finding) => {
            const color = finding.status === "PASS" ? THEME.GR : finding.status === "FAIL" ? THEME.RD : THEME.AM;
            const isOpen = open === finding.id;
            return (
              <Card key={finding.id} s={{ padding: 0, overflow: "hidden", borderLeft: `4px solid ${color}` }}>
                <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "13px 16px", cursor: "pointer" }} onClick={() => setOpen(isOpen ? null : finding.id)}>
                  <Badge s={finding.status} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 700, color: THEME.NV, fontSize: 13 }}>{finding.dim}</div>
                    <div style={{ fontSize: 10, color: THEME.MT, marginTop: 1 }}>{finding.route === "auto" ? "AI Assessed (automated)" : finding.qStatus === "reviewed" ? `Human Reviewed → ${finding.determination} · ${finding.officer}` : `Pending Human Review · ${finding.officer}`}</div>
                  </div>
                  <div style={{ textAlign: "right", minWidth: 100 }}>
                    <div style={{ fontSize: 10, color: THEME.MT, marginBottom: 3 }}>AI Confidence</div>
                    <Bar v={finding.conf} />
                  </div>
                  <div style={{ color: THEME.MT, flexShrink: 0 }}>{isOpen ? <ChevronUp size={15} /> : <ChevronDown size={15} />}</div>
                </div>
                {isOpen && (
                  <div style={{ borderTop: `1px solid ${THEME.BD}`, padding: "14px 16px" }}>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 10 }}>
                      <div style={{ background: "#F8FAFC", borderRadius: 7, padding: 12, gridColumn: "1/-1" }}>
                        <div style={{ fontSize: 10, fontWeight: 700, color: THEME.NV, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 5 }}>Legal Citation</div>
                        <div style={{ fontSize: 12, color: THEME.TX, lineHeight: 1.65 }}>{finding.citation}</div>
                      </div>
                      <div style={{ background: "#EEF2F9", borderRadius: 7, padding: 12 }}>
                        <div style={{ fontSize: 10, fontWeight: 700, color: THEME.NV, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 5 }}>NGO Document Evidence</div>
                        <div style={{ fontSize: 12, color: THEME.TX, lineHeight: 1.65 }}>{finding.evidence}</div>
                      </div>
                      <div style={{ background: "#F0F9FF", borderRadius: 7, padding: 12 }}>
                        <div style={{ fontSize: 10, fontWeight: 700, color: "#0369A1", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 5 }}>AI Reasoning</div>
                        <div style={{ fontSize: 12, color: THEME.TX, lineHeight: 1.65 }}>{finding.reasoning}</div>
                      </div>
                    </div>
                    {finding.qStatus === "reviewed" && (
                      <div style={{ background: "#ECFDF5", border: "1px solid #A7F3D0", borderRadius: 7, padding: 12, marginBottom: 8 }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 5 }}>
                           <div style={{ fontSize: 10, fontWeight: 700, color: THEME.GR, textTransform: "uppercase" }}>Officer Determination: {finding.determination}</div>
                          <span style={{ fontSize: 10, color: THEME.MT }}>{finding.reviewedAt}</span>
                        </div>
                        <div style={{ fontSize: 12, color: THEME.TX, lineHeight: 1.6 }}>{finding.officerNotes || "No notes provided."}</div>
                        <div style={{ fontSize: 10, color: THEME.MT, marginTop: 4 }}>Reviewed by {finding.officer} · {finding.role}</div>
                      </div>
                    )}
                    {finding.status === "FAIL" && (
                      <div style={{ background: "#FEE2E2", border: "1px solid #FCA5A5", borderRadius: 7, padding: 12 }}>
                        <div style={{ fontSize: 10, fontWeight: 700, color: THEME.RD, textTransform: "uppercase", marginBottom: 5 }}>How to Resolve</div>
                        <div style={{ fontSize: 12, color: THEME.RD, lineHeight: 1.6 }}>{finding.fix || "Provide additional evidence demonstrating compliance to the registrar."}</div>
                      </div>
                    )}
                    {finding.route === "human" && finding.qStatus === "pending" && (
                      <div style={{ background: "#FEF3C7", border: "1px solid #FDE68A", borderRadius: 7, padding: 12 }}>
                        <div style={{ fontSize: 10, fontWeight: 700, color: THEME.AM, textTransform: "uppercase", marginBottom: 5 }}>Pending Officer Review</div>
                        <div style={{ fontSize: 12, color: THEME.AM }}>Assigned to {finding.officer} ({finding.role}). Awaiting determination.</div>
                      </div>
                    )}
                  </div>
                )}
              </Card>
            );
          })}
        </div>
        <div style={{ marginTop: 16, textAlign: "center" }}>
          <button onClick={() => go("queue")} style={{ background: THEME.WH, color: THEME.NV, border: `1px solid ${THEME.BD}`, borderRadius: 7, padding: "9px 18px", fontSize: 13, cursor: "pointer", marginRight: 8 }}>View Review Queue</button>
          <button onClick={() => go("report")} style={{ background: THEME.OR, color: THEME.WH, border: "none", borderRadius: 7, padding: "9px 18px", fontSize: 13, fontWeight: 600, cursor: "pointer" }}>Generate Full Report →</button>
        </div>
      </div>
    </div>
  );
}
