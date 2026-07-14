"use client";

import { useEffect, useState, useRef } from "react";
import { THEME, STEPS, STATES, assessSubmission, getSubmissionStatus, getSubmissionDetails } from "@/lib/api";
import Card from "@/components/ui/Card";

// Map lowercase state code → display name
const STATE_CODE_MAP = Object.fromEntries(
  STATES.map((s) => [s.code.toLowerCase(), s.name])
);

export default function ProcessingPage({ go }) {
  const [step, setStep] = useState(0);
  const [errorMsg, setErrorMsg] = useState(null);
  const [orgName, setOrgName] = useState("");
  const [stateName, setStateName] = useState("");
  const [entityType, setEntityType] = useState("");
  const assessStarted = useRef(false);

  useEffect(() => {
    const subId = localStorage.getItem("active_submission_id");
    if (!subId) {
      go("submit");
      return;
    }

    // Load live submission details for the subtitle
    getSubmissionDetails(subId)
      .then((details) => {
        setOrgName(details.org_name || "");
        const rawState = details.state || "";
        setStateName(STATE_CODE_MAP[rawState.toLowerCase()] || rawState);
        setEntityType(details.entity_type || "");
      })
      .catch(() => {});

    // Trigger assessment once
    if (!assessStarted.current) {
      assessStarted.current = true;
      assessSubmission(subId).catch((err) => {
        setErrorMsg("Failed to start assessment: " + (err.response?.data?.detail || err.message));
      });
    }

    // Polling interval
    const interval = setInterval(async () => {
      try {
        const data = await getSubmissionStatus(subId);
        if (data.status === "complete") {
          setStep(STEPS.length);
          clearInterval(interval);
          setTimeout(() => go("dashboard"), 800);
        } else if (data.status === "error") {
          setErrorMsg(data.error || "An unknown assessment error occurred.");
          clearInterval(interval);
        } else if (data.status === "processing" && data.progress_step) {
          setStep(Math.min(data.progress_step, STEPS.length - 1));
        }
      } catch (err) {
        console.error("Status polling failed:", err);
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [go]);

  const percent = Math.round((step / STEPS.length) * 100);

  return (
    <div style={{ background: THEME.BG, minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <Card s={{ maxWidth: 480, width: "100%", margin: "0 24px" }}>
        {errorMsg ? (
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 38, marginBottom: 8 }}>❌</div>
            <h2 style={{ color: THEME.RD, fontWeight: 800, margin: "0 0 10px", fontSize: 17 }}>Assessment Failed</h2>
            <p style={{ color: THEME.TX, fontSize: 13, marginBottom: 18, lineHeight: 1.5 }}>{errorMsg}</p>
            <button onClick={() => go("submit")} style={{ background: THEME.OR, color: THEME.WH, border: "none", borderRadius: 6, padding: "8px 18px", fontSize: 12, fontWeight: 600, cursor: "pointer" }}>Go Back</button>
          </div>
        ) : (
          <>
            <div style={{ textAlign: "center", marginBottom: 22 }}>
              <div style={{ fontSize: 38, marginBottom: 8 }}>{step >= STEPS.length ? "✅" : "⚙️"}</div>
              <h2 style={{ color: THEME.NV, fontWeight: 800, margin: "0 0 4px", fontSize: 17 }}>{step >= STEPS.length ? "Analysis Complete" : "Analysing Documents…"}</h2>
              <p style={{ color: THEME.MT, margin: 0, fontSize: 12 }}>{orgName || "NGO"} · {stateName || "—"} · {entityType || "—"}</p>
            </div>
            <div style={{ marginBottom: 18 }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: THEME.MT, marginBottom: 4 }}>
                <span>Progress</span>
                <span style={{ fontWeight: 600, color: THEME.OR }}>{percent}%</span>
              </div>
              <div style={{ background: THEME.BD, borderRadius: 8, height: 7 }}>
                <div style={{ height: 7, borderRadius: 8, background: `linear-gradient(90deg,${THEME.OR},#F97316)`, width: `${percent}%`, transition: "width 0.5s ease" }} />
              </div>
            </div>
            <div style={{ display: "grid", gap: 5 }}>
              {STEPS.map((item, index) => (
                <div key={`${item}-${index}`} style={{ display: "flex", gap: 9, alignItems: "center", padding: "7px 10px", borderRadius: 7, background: index < step ? "#ECFDF5" : index === step ? "#FFF3EB" : "transparent", transition: "background 0.3s" }}>
                  <div style={{ width: 18, height: 18, borderRadius: "50%", flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center", background: index < step ? THEME.GR : index === step ? THEME.OR : THEME.BD, color: THEME.WH, fontSize: 9, fontWeight: 700 }}>
                    {index < step ? "✓" : index === step ? "…" : index + 1}
                  </div>
                  <span style={{ fontSize: 12, color: index < step ? THEME.GR : index === step ? THEME.OR : THEME.MT, fontWeight: index === step ? 600 : 400 }}>{item}</span>
                </div>
              ))}
            </div>
          </>
        )}
      </Card>
    </div>
  );
}
