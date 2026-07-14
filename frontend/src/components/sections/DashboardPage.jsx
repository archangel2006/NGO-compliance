"use client";

import { useEffect, useState } from "react";
import { Eye, FileText, List } from "lucide-react";
import { THEME, NGO, FINDINGS, STATES, getFindings, getSubmissionDetails } from "@/lib/api";
import Crumb from "@/components/sections/Crumb";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Bar from "@/components/ui/Bar";
import Ring from "@/components/ui/Ring";

// Map lowercase state code → display name (e.g. 'ka' → 'Karnataka')
const STATE_CODE_MAP = Object.fromEntries(
  STATES.map((s) => [s.code.toLowerCase(), s.name])
);

const toStateName = (raw) => {
  if (!raw) return "";
  const lower = raw.toLowerCase();
  return STATE_CODE_MAP[lower] || raw.charAt(0).toUpperCase() + raw.slice(1);
};

// Map string icon name/id to Lucide icon component if needed, but since we are keeping existing files,
// we can resolve finding.dimension_id to its corresponding icon from lucide-react.
import {
  Shield,
  Building2,
  Users,
  DollarSign,
  Receipt,
  Globe,
  BarChart2,
} from "lucide-react";

const ICON_MAP = {
  registration: Shield,
  governance: Building2,
  membership: Users,
  financial: DollarSign,
  tax: Receipt,
  fcra: Globe,
  audit: BarChart2,
};

export default function DashboardPage({ go }) {
  const [findingsState, setFindingsState] = useState([]);
  const [ngoDetails, setNgoDetails] = useState(NGO);
  const [loading, setLoading] = useState(true);
  const [backendScore, setBackendScore] = useState(null);

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

        // Read score returned by backend if available
        if (details.score && details.score.overall_score != null) {
          setBackendScore(Math.round(details.score.overall_score));
        }

        // Map details to match NGO shape
        setNgoDetails({
          name: details.org_name || NGO.name,
          id: details.darpan_id || NGO.id,
          // Translate stored code ('ka') to display name ('Karnataka')
          state: toStateName(details.state) || NGO.state,
          type: details.entity_type || NGO.type,
          reg: details.registration_no || NGO.reg,
          pan: details.pan || NGO.pan,
          sector: details.sector || NGO.sector,
          by: details.submitted_by || NGO.by,
          date: details.created_at ? details.created_at.substring(0, 10) : NGO.date,
          city: NGO.city,
        });

        // Map findings to match FINDINGS shape (specifically injecting icon components)
        const mapped = (res.findings || []).map((f) => ({
          id: f.id,
          dim: f.dimension_name,
          dimension_id: f.dimension_id,
          icon: ICON_MAP[f.dimension_id] || Shield,
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
        }));
        setFindingsState(mapped.length ? mapped : FINDINGS);
      } catch (err) {
        console.error("Dashboard data load failed, using fallbacks:", err);
        setFindingsState(FINDINGS);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const pass = findingsState.filter((finding) => finding.status === "PASS").length;
  const fail = findingsState.filter((finding) => finding.status === "FAIL").length;
  const uncertain = findingsState.filter((finding) => finding.status === "UNCERTAIN").length;
  // Prefer backend-calculated score; fall back to simple pass-ratio
  const overallScore = loading
    ? 74
    : backendScore != null
    ? backendScore
    : Math.round((pass / (findingsState.length || 7)) * 100);

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
            <span style={{ background: THEME.AM, color: THEME.WH, borderRadius: 10, padding: "0 5px", fontSize: 10 }}>{uncertain}</span>
          </button>
          <button onClick={() => go("report")} style={{ background: THEME.OR, color: THEME.WH, border: "none", borderRadius: 6, padding: "6px 14px", fontSize: 12, fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", gap: 5 }}>
            <FileText size={13} />Full Report
          </button>
        </div>
      </div>

      <div style={{ maxWidth: 1060, margin: "0 auto", padding: "18px 20px" }}>
        <Card s={{ marginBottom: 16, background: "linear-gradient(135deg,#1A3A6B,#0F2451)", border: "none" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 22 }}>
            <Ring score={overallScore} />
            <div style={{ flex: 1 }}>
              <div style={{ color: THEME.OR, fontSize: 10, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 3 }}>Compliance Assessment · {ngoDetails.state} · {ngoDetails.type}</div>
              <h2 style={{ color: THEME.WH, fontSize: 17, fontWeight: 800, margin: "0 0 3px" }}>{ngoDetails.name}</h2>
              <div style={{ color: "#94A3B8", fontSize: 12, marginBottom: 12 }}>PAN: {ngoDetails.pan} · {ngoDetails.sector}</div>
              <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                {[[pass, "PASSED", "#4ADE80", "rgba(22,163,74,.2)", "rgba(22,163,74,.3)"], [fail, "FAILED", "#FCA5A5", "rgba(220,38,38,.2)", "rgba(220,38,38,.3)"], [uncertain, "UNCERTAIN", "#FCD34D", "rgba(217,119,6,.2)", "rgba(217,119,6,.3)"]].map(([value, label, color, background, border]) => (
                  <div key={label} style={{ background, border: `1px solid ${border}`, borderRadius: 7, padding: "8px 16px", textAlign: "center" }}>
                    <div style={{ color, fontWeight: 900, fontSize: 20, lineHeight: 1 }}>{value}</div>
                    <div style={{ color, fontSize: 9, marginTop: 2, letterSpacing: "0.05em" }}>{label}</div>
                  </div>
                ))}
                <div style={{ background: "rgba(255,255,255,.06)", border: "1px solid rgba(255,255,255,.12)", borderRadius: 7, padding: "8px 16px", textAlign: "center" }}>
                  <div style={{ color: "#CBD5E1", fontWeight: 900, fontSize: 20, lineHeight: 1 }}>{findingsState.length}</div>
                  <div style={{ color: "#94A3B8", fontSize: 9, marginTop: 2 }}>TOTAL</div>
                </div>
              </div>
            </div>
            <div style={{ background: "rgba(251,191,36,.1)", border: "1px solid rgba(251,191,36,.3)", borderRadius: 9, padding: "14px 16px", maxWidth: 170, flexShrink: 0 }}>
              <div style={{ color: "#FCD34D", fontWeight: 700, fontSize: 13, marginBottom: 4 }}>{overallScore >= 85 ? "✓ Grant Ready" : "⚠ Action Needed"}</div>
              <div style={{ color: "#FDE68A", fontSize: 12, lineHeight: 1.5 }}>
                {overallScore >= 85
                  ? "NGO satisfies all core compliance dimensions."
                  : `${fail} critical failure and ${uncertain} pending review must be resolved.`}
              </div>
            </div>
          </div>
        </Card>

        <div style={{ background: THEME.WH, borderRadius: 8, border: `1px solid ${THEME.BD}`, padding: "10px 16px", marginBottom: 16, display: "flex", gap: 24, flexWrap: "wrap" }}>
          {[['Organisation', ngoDetails.name], ['State', ngoDetails.state], ['Reg. No.', ngoDetails.reg], ['Sector', ngoDetails.sector], ['Submitted by', ngoDetails.by]].map(([label, value]) => (
            <div key={label}>
              <div style={{ fontSize: 9, color: THEME.MT, textTransform: "uppercase", letterSpacing: "0.05em" }}>{label}</div>
              <div style={{ fontSize: 12, color: THEME.NV, fontWeight: 600 }}>{value}</div>
            </div>
          ))}
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          {findingsState.map((finding) => {
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
                {finding.status === "FAIL" && <div style={{ marginTop: 8, background: "#FEE2E2", border: "1px solid #FCA5A5", borderRadius: 5, padding: "6px 9px", fontSize: 11, color: THEME.RD }}>⚠ Action Required: Critical compliance gap found.</div>}
                {finding.route === "human" && finding.qStatus === "pending" && <div style={{ marginTop: 8, background: "#FEF3C7", border: "1px solid #FDE68A", borderRadius: 5, padding: "6px 9px", fontSize: 11, color: THEME.AM }}>⟳ Pending review · Assigned to officer</div>}
                {finding.route === "human" && finding.qStatus === "reviewed" && <div style={{ marginTop: 8, background: "#ECFDF5", border: "1px solid #A7F3D0", borderRadius: 5, padding: "6px 9px", fontSize: 11, color: THEME.GR }}>✓ Reviewed → {finding.determination}</div>}
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}
