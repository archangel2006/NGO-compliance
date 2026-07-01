import { ChevronRight, Upload, Search, Shield, FileCheck, Building2, Receipt, Globe } from "lucide-react";
import Card from "@/components/ui/Card";

export default function LandingPage({ go }) {
  return (
    <div style={{ background: "#F4F6FA", minHeight: "100vh" }}>
      <div style={{ background: "linear-gradient(135deg,#FFFBF7 0%,#FFF5EE 50%,#F0F4FF 100%)", borderBottom: "1px solid #F0E8E0", padding: "48px 24px 40px" }}>
        <div style={{ maxWidth: 960, margin: "0 auto", display: "grid", gridTemplateColumns: "1fr 1fr", gap: 40, alignItems: "center" }}>
          <div>
            <span style={{ background: "#FFF3EB", color: "#E8601A", padding: "4px 12px", borderRadius: 20, fontSize: 11, fontWeight: 700, border: "1px solid #FDDBC8", display: "inline-block", marginBottom: 14 }}>
              PILOT · Maharashtra · Delhi · Karnataka · Rajasthan
            </span>
            <h1 style={{ color: "#1A3A6B", fontSize: 32, fontWeight: 800, margin: "0 0 12px", lineHeight: 1.25 }}>
              A Digital Platform To
              <br />
              <span style={{ color: "#E8601A" }}>Verify NGO Compliance</span>
            </h1>
            <p style={{ color: "#64748B", fontSize: 14, lineHeight: 1.75, margin: "0 0 24px", maxWidth: 420 }}>
              Upload your NGO's registration documents. Our AI engine cross-checks them against state-specific laws and returns a detailed, evidence-backed compliance report.
            </p>
            <div style={{ display: "flex", gap: 10 }}>
              <button onClick={() => go("submit")} style={{ background: "#E8601A", color: "#FFFFFF", border: "none", borderRadius: 8, padding: "12px 22px", fontSize: 14, fontWeight: 700, cursor: "pointer", display: "flex", alignItems: "center", gap: 6, boxShadow: "0 2px 8px rgba(232,96,26,.3)" }}>
                Get Started <ChevronRight size={15} />
              </button>
              <button onClick={() => go("dashboard")} style={{ background: "#FFFFFF", color: "#1A3A6B", border: "1px solid #E2E8F0", borderRadius: 8, padding: "12px 18px", fontSize: 14, cursor: "pointer", fontWeight: 500 }}>
                View Sample Report
              </button>
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <div style={{ background: "#FFFFFF", borderRadius: 12, border: "1px solid #E2E8F0", padding: 20, boxShadow: "0 2px 12px rgba(26,58,107,.06)" }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: "#1A3A6B", marginBottom: 14, textTransform: "uppercase", letterSpacing: "0.07em" }}>How it works</div>
              {[[Upload, "Upload Documents", "Trust Deed, 12A/80G, FCRA, Audits"], [Search, "AI Extracts & Analyses", "OCR + RAG over Indian legal corpus"], [Shield, "State-Law Matching", "Acts, Gazettes, FCRA, IT provisions"], [FileCheck, "Compliance Report", "Pass / Fail / Uncertain + legal citations"]].map(([Icon, title, description], index) => (
                <div key={`${title}-${index}`}>
                  <div style={{ display: "flex", gap: 10, alignItems: "center", padding: "8px 0" }}>
                    <div style={{ width: 28, height: 28, borderRadius: 6, background: "#FFF3EB", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                      <Icon size={14} style={{ color: "#E8601A" }} />
                    </div>
                    <div>
                      <div style={{ fontSize: 13, fontWeight: 600, color: "#1A3A6B" }}>{title}</div>
                      <div style={{ fontSize: 11, color: "#64748B" }}>{description}</div>
                    </div>
                  </div>
                  {index < 3 && <div style={{ borderLeft: "2px dashed #E2E8F0", height: 8, marginLeft: 14 }} />}
                </div>
              ))}
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8 }}>
              {[['7', 'Dimensions Checked'], ['4 States', 'Pilot Scope'], ['RAG+LLM', 'AI Engine']].map(([value, label]) => (
                <div key={label} style={{ background: "#FFFFFF", borderRadius: 8, border: "1px solid #E2E8F0", padding: "12px 10px", textAlign: "center" }}>
                  <div style={{ color: "#E8601A", fontWeight: 800, fontSize: 16 }}>{value}</div>
                  <div style={{ color: "#64748B", fontSize: 10, marginTop: 2 }}>{label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div style={{ maxWidth: 960, margin: "0 auto", padding: "36px 24px" }}>
        <div style={{ textAlign: "center", marginBottom: 24 }}>
          <div style={{ color: "#E8601A", fontSize: 11, fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6 }}>WHAT WE VERIFY</div>
          <h2 style={{ fontSize: 22, fontWeight: 800, color: "#1A3A6B", margin: 0 }}>Compliance as a Decision-Support Layer</h2>
          <p style={{ color: "#64748B", marginTop: 6, fontSize: 13 }}>Not an automated ruling system. An AI assistant for compliance officers.</p>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 14, marginBottom: 36 }}>
          {[[Shield, "Registration", "Bombay Public Trusts Act, Societies Act, Charity Commissioner filings"], [Building2, "Governance", "Board composition, trustee qualifications, quorum requirements"], [Receipt, "Tax 12A/80G", "Income Tax exemption certificates, validity, PAN matching"], [Globe, "FCRA", "Foreign contribution registration, designated bank account, annual returns"]].map(([Icon, title, description]) => (
            <Card key={title} s={{ padding: 16 }}>
              <div style={{ width: 34, height: 34, borderRadius: 8, background: "#FFF3EB", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 10 }}>
                <Icon size={16} style={{ color: "#E8601A" }} />
              </div>
              <div style={{ fontWeight: 700, color: "#1A3A6B", fontSize: 13, marginBottom: 5 }}>{title}</div>
              <div style={{ color: "#64748B", fontSize: 11, lineHeight: 1.6 }}>{description}</div>
            </Card>
          ))}
        </div>

        <div style={{ background: "#FFFFFF", borderRadius: 12, border: "1px solid #E2E8F0", padding: 24, marginBottom: 24 }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: "#1A3A6B", marginBottom: 16, textTransform: "uppercase", letterSpacing: "0.06em" }}>Pilot States — Legal Corpus Coverage</div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 12 }}>
            {[['Maharashtra', 'Bombay Public Trusts Act, 1950\nSocieties Registration Act\nCharity Commissioner Rules'], ['Delhi', 'Delhi Societies Registration Act, 2006\nFCRA Guidelines\nIncome Tax provisions'], ['Karnataka', 'Karnataka Societies Registration Act, 1960\nPublic Trust provisions\nIT Act'], ['Rajasthan', 'Rajasthan Societies Registration Act, 1958\nState Public Trust Act\nIT Act']].map(([state, acts]) => (
              <div key={state} style={{ background: "#F8FAFC", borderRadius: 8, padding: 12, border: "1px solid #E2E8F0" }}>
                <div style={{ fontWeight: 700, color: "#1A3A6B", fontSize: 13, marginBottom: 5 }}>{state}</div>
                {acts.split("\n").map((act) => (
                  <div key={act} style={{ fontSize: 11, color: "#64748B", lineHeight: 1.6 }}>· {act}</div>
                ))}
              </div>
            ))}
          </div>
        </div>

        <div style={{ background: "linear-gradient(135deg,#FFF3EB,#FFF8F5)", border: "1px solid #FDDBC8", borderRadius: 12, padding: "28px 32px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div>
            <h3 style={{ color: "#1A3A6B", fontSize: 17, fontWeight: 700, margin: "0 0 5px" }}>Ready to check your NGO's compliance?</h3>
            <p style={{ color: "#64748B", margin: 0, fontSize: 13 }}>Upload documents and receive a state-specific compliance report.</p>
          </div>
          <button onClick={() => go("submit")} style={{ background: "#E8601A", color: "#FFFFFF", border: "none", borderRadius: 8, padding: "12px 22px", fontSize: 14, fontWeight: 700, cursor: "pointer", display: "flex", alignItems: "center", gap: 6, flexShrink: 0, boxShadow: "0 2px 8px rgba(232,96,26,.3)" }}>
            Start Compliance Check <ChevronRight size={15} />
          </button>
        </div>
      </div>
    </div>
  );
}
