"use client";

import { useState } from "react";
import { ChevronRight, FileText, Upload, CheckCircle, Shield, Loader2 } from "lucide-react";
import { THEME, NGO, DOCS, STATES, createSubmission, uploadDocument } from "@/lib/api";
import Crumb from "@/components/sections/Crumb";
import Card from "@/components/ui/Card";

export default function SubmitPage({ go }) {
  const [subStep, setSubStep] = useState(0);
  const [selState, setSelState] = useState(null);
  const [uploadedFiles, setUploadedFiles] = useState({}); // { doc_type: filename }
  const [uploading, setUploading] = useState(null);
  const [form, setForm] = useState({ name: "", type: "", pan: "", year: "", sector: "", email: "" });

  const set = (key) => (event) => setForm((current) => ({ ...current, [key]: event.target.value }));
  const autoFillForm = () => setForm({ name: NGO.name, type: "Public Trust", pan: NGO.pan, year: "2019", sector: NGO.sector, email: "priya.sharma@ashajyoti.org" });
  const formComplete = Boolean(form.name && form.type && form.pan && form.year && form.sector && form.email);
  const docsLoaded = Object.keys(uploadedFiles).length > 0;
  const STEP_LABELS = ["Select State", "NGO Details", "Upload Documents", "Submit"];
  const complexCol = { High: THEME.RD, Medium: THEME.AM };
  const stateName = STATES.find((state) => state.code === selState)?.name || "";

  const docSlots = [
    { name: "Trust Deed / MOA", cat: "Registration", cat_key: "trust_deed" },
    { name: "Registration Certificate", cat: "Registration", cat_key: "registration_certificate" },
    { name: "12A Certificate", cat: "Tax", cat_key: "certificate_12a" },
    { name: "80G Certificate", cat: "Tax", cat_key: "certificate_80g" },
    { name: "FCRA Certificate", cat: "FCRA", cat_key: "fcra_certificate" },
    { name: "Annual Report", cat: "Financial", cat_key: "annual_report" },
    { name: "Audited Financial Statements", cat: "Audit", cat_key: "audit_report" },
    { name: "PAN Card", cat: "Tax / FCRA", cat_key: "pan_card" },
  ];

  const handleCreateSubmission = async () => {
    if (!formComplete) return;
    try {
      const res = await createSubmission({
        org_name: form.name,
        state: selState.toLowerCase(),
        entity_type: form.type,
        pan: form.pan.toUpperCase(),
        sector: form.sector,
        contact_email: form.email,
        year_of_incorporation: parseInt(form.year, 10),
      });
      localStorage.setItem("active_submission_id", res.id);
      setSubStep(2);
    } catch (err) {
      alert("Error creating submission: " + (err.response?.data?.detail || err.message));
    }
  };

  const handleFileUpload = async (catKey, file) => {
    if (!file) return;
    const subId = localStorage.getItem("active_submission_id");
    if (!subId) {
      alert("No active submission found. Please re-fill details.");
      return;
    }
    setUploading(catKey);
    try {
      await uploadDocument(subId, catKey, file);
      setUploadedFiles((current) => ({ ...current, [catKey]: file.name }));
    } catch (err) {
      alert("Upload failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setUploading(null);
    }
  };

  const inputField = (label, key, placeholder) => (
    <div>
      <label style={{ fontSize: 11, fontWeight: 700, color: THEME.NV, display: "block", marginBottom: 5, textTransform: "uppercase", letterSpacing: "0.05em" }}>{label}</label>
      <input
        value={form[key]}
        onChange={set(key)}
        placeholder={placeholder}
        style={{ width: "100%", padding: "9px 12px", border: `1px solid ${form[key] ? THEME.OR + "66" : THEME.BD}`, borderRadius: 7, fontSize: 13, background: THEME.WH, color: THEME.TX, boxSizing: "border-box", outline: "none" }}
      />
    </div>
  );

  return (
    <div style={{ background: THEME.BG, minHeight: "100vh" }}>
      <Crumb items={[{ label: "Home", page: "landing" }, { label: "Compliance Check" }]} go={go} />

      <div style={{ background: THEME.WH, borderBottom: `1px solid ${THEME.BD}`, padding: "12px 20px" }}>
        <div style={{ maxWidth: 860, margin: "0 auto", display: "flex", alignItems: "center" }}>
          {STEP_LABELS.map((stepLabel, index) => {
            const done = index < subStep;
            const current = index === subStep;
            return (
              <div key={stepLabel} style={{ display: "flex", alignItems: "center", flex: index < 3 ? 1 : 0 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <div style={{ width: 24, height: 24, borderRadius: "50%", background: done ? THEME.GR : current ? THEME.OR : THEME.BD, color: THEME.WH, display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: 10 }}>
                    {done ? "✓" : index + 1}
                  </div>
                  <span style={{ fontSize: 12, fontWeight: current ? 700 : 400, color: current ? THEME.NV : done ? THEME.GR : THEME.MT, whiteSpace: "nowrap" }}>{stepLabel}</span>
                </div>
                {index < 3 && <div style={{ flex: 1, height: 1, background: done ? THEME.GR : THEME.BD, margin: "0 10px", transition: "background 0.3s" }} />}
              </div>
            );
          })}
        </div>
      </div>

      <div style={{ maxWidth: 860, margin: "0 auto", padding: "28px 20px" }}>
        {subStep === 0 && (
          <div>
            <div style={{ textAlign: "center", marginBottom: 28 }}>
              <div style={{ color: THEME.OR, fontSize: 11, fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6 }}>STEP 1 OF 3</div>
              <h2 style={{ fontSize: 22, fontWeight: 800, color: THEME.NV, margin: "0 0 8px" }}>Select State of Registration</h2>
              <p style={{ color: THEME.MT, fontSize: 13, margin: 0 }}>Each state has different NGO laws. We'll cross-reference your documents against the exact rules for your state.</p>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 20 }}>
              {STATES.map((state) => {
                const selected = selState === state.code;
                return (
                  <div key={state.code} onClick={() => setSelState(state.code)} style={{ background: THEME.WH, borderRadius: 12, border: `2px solid ${selected ? THEME.OR : THEME.BD}`, padding: 20, cursor: "pointer", boxShadow: selected ? "0 0 0 3px rgba(232,96,26,.12)" : "none", transition: "all 0.15s", position: "relative" }}>
                    {selected && <div style={{ position: "absolute", top: 14, right: 14, width: 20, height: 20, borderRadius: "50%", background: THEME.OR, display: "flex", alignItems: "center", justifyContent: "center", color: THEME.WH, fontSize: 11, fontWeight: 700 }}>✓</div>}
                    <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
                       <div style={{ width: 44, height: 44, borderRadius: 10, background: selected ? "#FFF3EB" : "#F4F6FA", border: `1px solid ${selected ? THEME.OR : THEME.BD}`, display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 900, fontSize: 15, color: selected ? THEME.OR : THEME.NV }}>
                        {state.code}
                      </div>
                      <div>
                        <div style={{ fontWeight: 800, fontSize: 16, color: THEME.NV }}>{state.name}</div>
                        <div style={{ fontSize: 11, color: THEME.MT, marginTop: 1 }}>{state.ngos} registered NGOs</div>
                      </div>
                    </div>
                    <div style={{ marginBottom: 10 }}>
                      {state.acts.map((act) => <div key={act} style={{ fontSize: 11, color: THEME.MT, lineHeight: 1.6 }}>· {act}</div>)}
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      <span style={{ fontSize: 10, fontWeight: 700, color: complexCol[state.complexity] || THEME.AM, background: state.complexity === "High" ? "#FEE2E2" : "#FEF3C7", padding: "2px 8px", borderRadius: 10 }}>{state.complexity} Complexity</span>
                      <span style={{ fontSize: 10, color: THEME.MT }}>+ Central: FCRA · IT Act · Darpan</span>
                    </div>
                  </div>
                );
              })}
            </div>
            <div style={{ background: "#EEF2F9", border: "1px solid #C7D7F0", borderRadius: 9, padding: "12px 16px", marginBottom: 24, display: "flex", gap: 10, alignItems: "center" }}>
              <Shield size={14} style={{ color: THEME.NV, flexShrink: 0 }} />
              <div style={{ fontSize: 12, color: THEME.NV, lineHeight: 1.6 }}><strong>Central regulations always included</strong> — FCRA, Income Tax Act (12A / 80G), and NITI Aayog Darpan guidelines are checked for every submission automatically.</div>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <button onClick={() => go("landing")} style={{ background: THEME.WH, color: THEME.NV, border: `1px solid ${THEME.BD}`, borderRadius: 7, padding: "10px 18px", fontSize: 13, cursor: "pointer" }}>← Back</button>
              <button onClick={() => selState && setSubStep(1)} disabled={!selState} style={{ background: selState ? THEME.OR : "#CBD5E1", color: THEME.WH, border: "none", borderRadius: 7, padding: "10px 24px", fontSize: 13, fontWeight: 700, cursor: selState ? "pointer" : "not-allowed", display: "flex", alignItems: "center", gap: 6, boxShadow: selState ? "0 2px 8px rgba(232,96,26,.3)" : "none" }}>
                Next: NGO Details <ChevronRight size={15} />
              </button>
            </div>
          </div>
        )}

        {subStep === 1 && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 280px", gap: 18 }}>
            <div>
              <div style={{ background: "#ECFDF5", border: "1px solid #A7F3D0", borderRadius: 7, padding: "8px 14px", marginBottom: 14, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <div style={{ fontSize: 12, color: "#065F46", display: "flex", gap: 6, alignItems: "center" }}>
                  <CheckCircle size={13} /><strong>{stateName}</strong> selected · Central regulations included
                </div>
                <button onClick={() => setSubStep(0)} style={{ fontSize: 11, color: THEME.OR, background: "none", border: "none", cursor: "pointer", textDecoration: "underline" }}>Change</button>
              </div>
              <Card>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                  <div>
                    <h2 style={{ margin: 0, fontSize: 15, fontWeight: 700, color: THEME.NV }}>NGO Details</h2>
                    <p style={{ margin: "3px 0 0", color: THEME.MT, fontSize: 12 }}>Enter your NGO's basic information to route the compliance check.</p>
                  </div>
                  <button onClick={autoFillForm} style={{ background: "#FFF3EB", color: THEME.OR, border: "1px solid #FDDBC8", borderRadius: 6, padding: "7px 12px", fontSize: 12, fontWeight: 600, cursor: "pointer", whiteSpace: "nowrap", flexShrink: 0 }}>✦ Auto-fill Sample</button>
                </div>
                <div style={{ display: "grid", gap: 12 }}>
                  {inputField("Organisation Name *", "name", "e.g. Asha Jyoti Welfare Foundation")}
                  <div>
                    <label style={{ fontSize: 11, fontWeight: 700, color: THEME.NV, display: "block", marginBottom: 5, textTransform: "uppercase", letterSpacing: "0.05em" }}>NGO Type *</label>
                    <select value={form.type} onChange={set("type")} style={{ width: "100%", padding: "9px 12px", border: `1px solid ${form.type ? THEME.OR + "66" : THEME.BD}`, borderRadius: 7, fontSize: 13, background: THEME.WH, color: form.type ? THEME.TX : "#9CA3AF", boxSizing: "border-box" }}>
                      <option value="">Select type…</option>
                      {['Public Trust', 'Society', 'Section 8 Company'].map((option) => <option key={option} value={option}>{option}</option>)}
                    </select>
                  </div>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                    {inputField("PAN Number *", "pan", "AAAAA0000A")}
                    {inputField("Year of Incorporation *", "year", "e.g. 2019")}
                  </div>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                    {inputField("Primary Sector *", "sector", "Education · Health · Women Empowerment…")}
                    {inputField("Contact Email *", "email", "report will be sent here")}
                  </div>
                </div>
              </Card>
            </div>
            <div>
              <Card s={{ background: "#EEF2F9", border: "1px solid #C7D7F0", marginBottom: 12 }}>
                <div style={{ fontWeight: 700, color: THEME.NV, marginBottom: 10, fontSize: 12, textTransform: "uppercase", letterSpacing: "0.05em" }}>Will be checked</div>
                {['Registration & Legal Status', 'Governance Structure', 'Membership Requirements', 'Financial Compliance', 'Tax Compliance (12A/80G)', 'FCRA Compliance', 'Audit Requirements'].map((item, index) => (
                  <div key={item} style={{ display: "flex", gap: 7, alignItems: "flex-start", marginBottom: 7 }}>
                    <div style={{ width: 17, height: 17, borderRadius: "50%", background: THEME.OR, color: THEME.WH, fontSize: 9, fontWeight: 700, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, marginTop: 1 }}>{index + 1}</div>
                    <span style={{ fontSize: 12, color: THEME.NV, lineHeight: 1.4 }}>{item}</span>
                  </div>
                ))}
              </Card>
              <Card s={{ background: "#ECFDF5", border: "1px solid #A7F3D0", marginBottom: 12 }}>
                <div style={{ fontSize: 11, color: "#065F46", marginBottom: 7, fontWeight: 700 }}>OCR extracts for you</div>
                {['Registration / certificate numbers', 'Trustee & member names', 'Dates of registration', 'Clause text from Trust Deed', 'Financial figures & audit details'].map((feature) => (
                  <div key={feature} style={{ fontSize: 11, color: "#065F46", marginBottom: 3 }}>· {feature}</div>
                ))}
              </Card>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                <button onClick={() => setSubStep(0)} style={{ background: THEME.WH, color: THEME.NV, border: `1px solid ${THEME.BD}`, borderRadius: 7, padding: "9px", fontSize: 12, cursor: "pointer" }}>← Back</button>
                <button onClick={handleCreateSubmission} disabled={!formComplete} style={{ background: formComplete ? THEME.OR : "#CBD5E1", color: THEME.WH, border: "none", borderRadius: 7, padding: "10px", fontSize: 13, fontWeight: 700, cursor: formComplete ? "pointer" : "not-allowed", display: "flex", alignItems: "center", justifyContent: "center", gap: 6, boxShadow: formComplete ? "0 2px 8px rgba(232,96,26,.3)" : "none" }}>
                  Next: Upload Documents <ChevronRight size={14} />
                </button>
                {!formComplete && <div style={{ textAlign: "center", fontSize: 11, color: THEME.MT }}>Fill all fields to continue</div>}
              </div>
            </div>
          </div>
        )}

        {subStep === 2 && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 280px", gap: 18 }}>
            <div>
              <div style={{ background: "#ECFDF5", border: "1px solid #A7F3D0", borderRadius: 7, padding: "8px 14px", marginBottom: 14, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <div style={{ fontSize: 12, color: "#065F46", display: "flex", gap: 6, alignItems: "center" }}>
                  <CheckCircle size={13} /><strong>{stateName}</strong> · {form.name} · {form.type}
                </div>
                <button onClick={() => setSubStep(1)} style={{ fontSize: 11, color: THEME.OR, background: "none", border: "none", cursor: "pointer", textDecoration: "underline" }}>Edit</button>
              </div>
              <Card>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 14 }}>
                  <div>
                    <h3 style={{ margin: "0 0 3px", fontSize: 14, fontWeight: 700, color: THEME.NV }}>Upload Your Documents</h3>
                    <p style={{ margin: 0, color: THEME.MT, fontSize: 12 }}>Upload what you have. We'll check against {stateName} laws + central regulations and flag what's missing.</p>
                  </div>
                </div>

                <div>
                  <div style={{ display: "grid", gap: 7 }}>
                    {docSlots.map((document) => {
                      const uploadedFileName = uploadedFiles[document.cat_key];
                      const isThisUploading = uploading === document.cat_key;
                      return (
                        <div key={document.name} style={{ display: "flex", alignItems: "center", gap: 10, padding: "9px 12px", background: "#FAFAFA", borderRadius: 7, border: `1px solid ${THEME.BD}` }}>
                          <FileText size={13} style={{ color: THEME.OR, flexShrink: 0 }} />
                          <div style={{ flex: 1 }}>
                            <div style={{ fontSize: 13, fontWeight: 600, color: THEME.NV }}>{document.name}</div>
                            <div style={{ fontSize: 10, color: THEME.MT }}>{document.cat} · {uploadedFileName ? uploadedFileName : "No file uploaded"}</div>
                          </div>
                          {uploadedFileName ? (
                            <span style={{ background: "#DCFCE7", color: THEME.GR, fontSize: 10, fontWeight: 700, padding: "2px 8px", borderRadius: 10 }}>✓ Uploaded</span>
                          ) : isThisUploading ? (
                            <Loader2 size={14} className="animate-spin" style={{ color: THEME.OR }} />
                          ) : (
                            <label style={{ background: THEME.WH, color: THEME.NV, border: `1px solid ${THEME.BD}`, borderRadius: 6, padding: "5px 12px", fontSize: 11, cursor: "pointer", fontWeight: 600, display: "inline-block" }}>
                              Upload
                              <input
                                type="file"
                                accept=".pdf"
                                style={{ display: "none" }}
                                onChange={(e) => handleFileUpload(document.cat_key, e.target.files[0])}
                              />
                            </label>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              </Card>
            </div>
            <div>
              <Card s={{ background: "#EEF2F9", border: "1px solid #C7D7F0", marginBottom: 12 }}>
                <div style={{ fontWeight: 700, color: THEME.NV, marginBottom: 8, fontSize: 12 }}>Checking Against</div>
                <div style={{ fontSize: 12, fontWeight: 600, color: THEME.OR, marginBottom: 6 }}>{stateName} State Laws</div>
                {(STATES.find((state) => state.code === selState) || STATES[0]).acts.map((act) => <div key={act} style={{ fontSize: 11, color: THEME.MT, marginBottom: 3 }}>· {act}</div>)}
                <div style={{ borderTop: `1px solid ${THEME.BD}`, marginTop: 10, paddingTop: 10 }}>
                  <div style={{ fontSize: 12, fontWeight: 600, color: THEME.NV, marginBottom: 6 }}>Central Regulations</div>
                  {['FCRA 2010 + Amendment Rules 2020', 'Income Tax Act — 12A & 80G', 'NITI Aayog Darpan Guidelines'].map((regulation) => <div key={regulation} style={{ fontSize: 11, color: THEME.MT, marginBottom: 3 }}>· {regulation}</div>)}
                </div>
              </Card>
              <Card s={{ background: "#FFFBEB", border: "1px solid #FDE68A", marginBottom: 12 }}>
                <div style={{ fontSize: 11, color: "#92400E", marginBottom: 3, fontWeight: 600 }}>Tip</div>
                <div style={{ fontSize: 12, color: "#78350F", lineHeight: 1.5 }}>Don't have all documents? Upload what you have. We'll flag exactly what's missing.</div>
              </Card>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                <button onClick={() => setSubStep(1)} style={{ background: THEME.WH, color: THEME.NV, border: `1px solid ${THEME.BD}`, borderRadius: 7, padding: "9px", fontSize: 12, cursor: "pointer" }}>← Back</button>
                <button onClick={() => docsLoaded && go("processing")} disabled={!docsLoaded} style={{ background: docsLoaded ? THEME.OR : "#CBD5E1", color: THEME.WH, border: "none", borderRadius: 7, padding: "11px", fontSize: 13, fontWeight: 700, cursor: docsLoaded ? "pointer" : "not-allowed", display: "flex", alignItems: "center", justifyContent: "center", gap: 6, boxShadow: docsLoaded ? "0 2px 8px rgba(232,96,26,.3)" : "none" }}>
                  Run Compliance Check <ChevronRight size={14} />
                </button>
                {!docsLoaded && <div style={{ textAlign: "center", fontSize: 11, color: THEME.MT }}>Upload documents to proceed</div>}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
