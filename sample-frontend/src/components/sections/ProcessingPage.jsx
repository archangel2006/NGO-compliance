"use client";

import { useEffect, useState } from "react";
import { THEME, NGO, STEPS } from "@/lib/api";
import Card from "@/components/ui/Card";

export default function ProcessingPage({ go }) {
  const [step, setStep] = useState(0);

  useEffect(() => {
    if (step < STEPS.length) {
      const timer = setTimeout(() => setStep((current) => current + 1), 680);
      return () => clearTimeout(timer);
    }

    const timer = setTimeout(() => go("dashboard"), 700);
    return () => clearTimeout(timer);
  }, [step, go]);

  const percent = Math.round((step / STEPS.length) * 100);

  return (
    <div style={{ background: THEME.BG, minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <Card s={{ maxWidth: 480, width: "100%", margin: "0 24px" }}>
        <div style={{ textAlign: "center", marginBottom: 22 }}>
          <div style={{ fontSize: 38, marginBottom: 8 }}>{step >= STEPS.length ? "✅" : "⚙️"}</div>
          <h2 style={{ color: THEME.NV, fontWeight: 800, margin: "0 0 4px", fontSize: 17 }}>{step >= STEPS.length ? "Analysis Complete" : "Analysing Documents…"}</h2>
          <p style={{ color: THEME.MT, margin: 0, fontSize: 12 }}>{NGO.name} · {NGO.state} · {NGO.type}</p>
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
      </Card>
    </div>
  );
}
