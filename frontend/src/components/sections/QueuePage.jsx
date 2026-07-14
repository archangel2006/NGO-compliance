"use client";

import { useEffect, useState } from "react";
import { CheckCircle, XCircle } from "lucide-react";
import { THEME, NGO, FINDINGS, getQueue, determineQueueItem } from "@/lib/api";
import Crumb from "@/components/sections/Crumb";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";

export default function QueuePage({ go }) {
  const [queueItems, setQueueItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchQueue = async () => {
    try {
      const data = await getQueue();
      // Map to shape required by the UI
      const mapped = (data.items || []).map((item) => ({
        id: item.id,
        finding_id: item.finding_id,
        dim: item.dimension_name,
        status: "UNCERTAIN", // base AI status that triggered queue routing
        route: "human",
        conf: 0.64,
        qStatus: item.queue_status, // "pending" | "reviewed"
        officer: "Officer Ramesh K.",
        role: "Sr. Compliance Officer",
        determination: item.officer_determination,
        reviewedAt: item.reviewed_at ? new Date(item.reviewed_at).toLocaleDateString() : "",
        officerNotes: item.officer_notes,
        evidence: "NGO details and uploaded PDF evidence are being evaluated.",
        citation: "Under review by NITI Darpan compliance verification framework.",
      }));
      setQueueItems(mapped);
    } catch (err) {
      console.error("Failed to load queue:", err);
      // Fallback
      const mock = FINDINGS.filter((finding) => finding.route === "human");
      setQueueItems(mock);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue();
  }, []);

  const handleDetermination = async (itemId, determination) => {
    const notes = prompt(`Enter review notes for ${determination}:`, `Approved by officer Ramesh K.`);
    if (notes === null) return; // cancelled
    try {
      await determineQueueItem(itemId, determination, notes);
      alert(`Determination submitted: ${determination}`);
      fetchQueue(); // Reload
    } catch (err) {
      alert("Error submitting determination: " + (err.response?.data?.detail || err.message));
    }
  };

  const pendingCount = queueItems.filter((i) => i.qStatus === "pending").length;
  const reviewedCount = queueItems.filter((i) => i.qStatus === "reviewed").length;

  return (
    <div style={{ background: THEME.BG, minHeight: "100vh" }}>
      <Crumb items={[{ label: "Home", page: "landing" }, { label: "Dashboard", page: "dashboard" }, { label: "Human Review Queue" }]} go={go} />
      <div style={{ maxWidth: 900, margin: "0 auto", padding: "18px 20px" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14 }}>
          <div>
            <h2 style={{ margin: 0, fontSize: 16, fontWeight: 800, color: THEME.NV }}>Human Review Queue</h2>
            <p style={{ margin: "3px 0 0", fontSize: 12, color: THEME.MT }}>UNCERTAIN findings are routed here for officer review</p>
          </div>
          <div style={{ display: "flex", gap: 6 }}>
            <span style={{ background: "#FEE2E2", color: THEME.RD, padding: "4px 12px", borderRadius: 20, fontSize: 11, fontWeight: 700 }}>{pendingCount} PENDING</span>
            <span style={{ background: "#DCFCE7", color: THEME.GR, padding: "4px 12px", borderRadius: 20, fontSize: 11, fontWeight: 700 }}>{reviewedCount} REVIEWED</span>
          </div>
        </div>

        <div style={{ background: "#EEF2F9", border: "1px solid #C7D7F0", borderRadius: 9, padding: "12px 14px", marginBottom: 16, display: "flex", gap: 10 }}>
          <span style={{ fontSize: 18, flexShrink: 0 }}>ℹ</span>
          <div style={{ fontSize: 12, color: THEME.NV, lineHeight: 1.65 }}>
            <strong>Blinded Review Protocol:</strong> Officers review the legal provisions and NGO evidence before seeing the AI recommendation. This prevents anchoring bias. Their determination is final and logged with full audit trail.
          </div>
        </div>

        <div style={{ display: "grid", gap: 14 }}>
          {queueItems.map((finding) => (
            <Card key={finding.id} s={{ borderLeft: `4px solid ${finding.qStatus === "reviewed" ? THEME.GR : THEME.AM}` }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 14 }}>
                <div>
                  <div style={{ fontWeight: 800, color: THEME.NV, fontSize: 14 }}>{finding.dim}</div>
                  <div style={{ fontSize: 11, color: THEME.MT, marginTop: 2 }}>{NGO.name}</div>
                </div>
                <div style={{ display: "flex", gap: 7, alignItems: "center" }}>
                  <Badge s={finding.status} />
                  <span style={{ background: finding.qStatus === "reviewed" ? "#DCFCE7" : "#FEF3C7", color: finding.qStatus === "reviewed" ? THEME.GR : THEME.AM, padding: "3px 10px", borderRadius: 12, fontSize: 10, fontWeight: 700 }}>
                    {finding.qStatus === "reviewed" ? "✓ REVIEWED" : "⟳ PENDING"}
                  </span>
                </div>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10, marginBottom: 12 }}>
                <div style={{ background: "#F8FAFC", borderRadius: 7, padding: 11 }}>
                  <div style={{ fontSize: 10, fontWeight: 700, color: THEME.NV, textTransform: "uppercase", marginBottom: 4 }}>Why Routed</div>
                  <div style={{ fontSize: 12, color: THEME.TX, lineHeight: 1.5 }}>AI confidence <strong>{Math.round(finding.conf * 100)}%</strong> — below 85% threshold. Needs verification.</div>
                </div>
                <div style={{ background: "#F8FAFC", borderRadius: 7, padding: 11 }}>
                  <div style={{ fontSize: 10, fontWeight: 700, color: THEME.NV, textTransform: "uppercase", marginBottom: 4 }}>Legal Citation</div>
                  <div style={{ fontSize: 12, color: THEME.TX, lineHeight: 1.5 }}>{finding.citation}</div>
                </div>
                <div style={{ background: "#F8FAFC", borderRadius: 7, padding: 11 }}>
                  <div style={{ fontSize: 10, fontWeight: 700, color: THEME.NV, textTransform: "uppercase", marginBottom: 4 }}>Assigned Officer</div>
                  <div style={{ display: "flex", gap: 7, alignItems: "center", marginTop: 2 }}>
                    <div style={{ width: 26, height: 26, borderRadius: "50%", background: "#EEF2F9", display: "flex", alignItems: "center", justifyContent: "center", color: THEME.NV, fontWeight: 700, fontSize: 11 }}>R</div>
                    <div>
                      <div style={{ fontSize: 12, fontWeight: 600, color: THEME.NV }}>{finding.officer}</div>
                      <div style={{ fontSize: 10, color: THEME.MT }}>{finding.role}</div>
                    </div>
                  </div>
                </div>
              </div>

              <div style={{ background: "#F0F9FF", borderRadius: 7, padding: 11, marginBottom: 10 }}>
                <div style={{ fontSize: 10, fontWeight: 700, color: "#0369A1", textTransform: "uppercase", marginBottom: 4 }}>NGO Document Evidence (shown to officer first)</div>
                <div style={{ fontSize: 12, color: THEME.TX, lineHeight: 1.6 }}>{finding.evidence}</div>
              </div>

              {finding.qStatus === "reviewed" ? (
                <div style={{ background: "#ECFDF5", border: "1px solid #A7F3D0", borderRadius: 7, padding: 12 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                    <div style={{ fontSize: 11, fontWeight: 700, color: THEME.GR }}>OFFICER DETERMINATION: {finding.determination}</div>
                    <span style={{ fontSize: 10, color: THEME.MT }}>{finding.reviewedAt}</span>
                  </div>
                  <div style={{ fontSize: 12, color: THEME.TX, lineHeight: 1.6 }}>{finding.officerNotes}</div>
                  <div style={{ fontSize: 10, color: THEME.MT, marginTop: 5 }}>Reviewed by {finding.officer} · {finding.role} · Audit trail logged</div>
                </div>
              ) : (
                <div style={{ background: "#FEF3C7", border: "1px solid #FDE68A", borderRadius: 7, padding: 12 }}>
                  <div style={{ fontSize: 10, fontWeight: 700, color: THEME.AM, textTransform: "uppercase", marginBottom: 8 }}>Awaiting Officer Review</div>
                  <div style={{ fontSize: 11, color: "#78350F", marginBottom: 10 }}>Review the legal citation and NGO evidence above, then mark your determination:</div>
                  <div style={{ display: "flex", gap: 7 }}>
                    <button onClick={() => handleDetermination(finding.id, "PASS")} style={{ background: THEME.GR, color: THEME.WH, border: "none", borderRadius: 6, padding: "8px 16px", fontSize: 12, fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", gap: 5 }}><CheckCircle size={13} />Mark PASS</button>
                    <button onClick={() => handleDetermination(finding.id, "FAIL")} style={{ background: THEME.RD, color: THEME.WH, border: "none", borderRadius: 6, padding: "8px 16px", fontSize: 12, fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", gap: 5 }}><XCircle size={13} />Mark FAIL</button>
                  </div>
                  <div style={{ fontSize: 10, color: THEME.AM, marginTop: 8 }}>* AI recommendation is hidden during review to prevent anchoring bias.</div>
                </div>
              )}
            </Card>
          ))}
        </div>

        <div style={{ marginTop: 16, textAlign: "center" }}>
          <button onClick={() => go("report")} style={{ background: THEME.OR, color: THEME.WH, border: "none", borderRadius: 7, padding: "10px 22px", fontSize: 13, fontWeight: 600, cursor: "pointer" }}>Generate Final Report →</button>
        </div>
      </div>
    </div>
  );
}
