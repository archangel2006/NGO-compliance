"use client";

import { useState } from "react";
import { ChevronRight, Search, Shield } from "lucide-react";
import { THEME, FINDINGS, DIR_DATA } from "@/lib/api";
import Crumb from "@/components/sections/Crumb";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Ring from "@/components/ui/Ring";

export default function DirectoryPage({ go }) {
  const [query, setQuery] = useState("");
  const [filterState, setFilterState] = useState("All");
  const [filterVerification, setFilterVerification] = useState("All");
  const [selected, setSelected] = useState(null);

  const filtered = DIR_DATA.filter((entry) => {
    const search = query.toLowerCase();
    const matchesQuery = !search || entry.name.toLowerCase().includes(search) || entry.sector.toLowerCase().includes(search) || entry.reg.toLowerCase().includes(search);
    const matchesState = filterState === "All" || entry.state === filterState;
    const matchesVerification = filterVerification === "All" || (filterVerification === "Verified" && entry.cStatus === "verified") || (filterVerification === "Partial" && entry.cStatus === "partial") || (filterVerification === "Unverified" && entry.cStatus === "unverified");
    return matchesQuery && matchesState && matchesVerification;
  });

  const verificationColors = {
    verified: { bg: "#DCFCE7", c: THEME.GR, t: "Verified" },
    partial: { bg: "#FEF3C7", c: THEME.AM, t: "Partially Verified" },
    unverified: { bg: "#F1F5F9", c: THEME.MT, t: "Unverified" },
  };

  if (selected) {
    const organisation = selected;
    const status = verificationColors[organisation.cStatus];

    return (
      <div style={{ background: THEME.BG, minHeight: "100vh" }}>
        <Crumb items={[{ label: "Home", page: "landing" }, { label: "NPO Directory", page: "directory" }, { label: organisation.name }]} go={go} />
        <div style={{ maxWidth: 860, margin: "0 auto", padding: "24px 20px" }}>
          <Card s={{ marginBottom: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 12 }}>
              <div>
                <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 6 }}>
                  <h2 style={{ margin: 0, fontSize: 18, fontWeight: 800, color: THEME.NV }}>{organisation.name}</h2>
                  <span style={{ background: status.bg, color: status.c, fontSize: 11, fontWeight: 700, padding: "3px 10px", borderRadius: 12 }}>{status.t}</span>
                </div>
                <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
                  {[['State', organisation.state], ['Type', organisation.type], ['Sector', organisation.sector], ['Reg. No.', organisation.reg]].map(([label, value]) => (
                    <div key={label}><div style={{ fontSize: 9, color: THEME.MT, textTransform: "uppercase" }}>{label}</div><div style={{ fontSize: 12, color: THEME.NV, fontWeight: 600 }}>{value}</div></div>
                  ))}
                </div>
              </div>
              {organisation.score ? (
                <div style={{ textAlign: "center" }}>
                  <Ring score={organisation.score} />
                  <div style={{ fontSize: 11, color: THEME.MT, marginTop: 4 }}>Compliance Score</div>
                </div>
              ) : (
                <div style={{ background: "#F1F5F9", border: `1px solid ${THEME.BD}`, borderRadius: 10, padding: "16px 20px", textAlign: "center" }}>
                  <div style={{ fontSize: 13, fontWeight: 700, color: THEME.MT, marginBottom: 4 }}>Not Checked</div>
                  <div style={{ fontSize: 11, color: THEME.MT }}>No compliance report</div>
                </div>
              )}
            </div>
          </Card>

          {organisation.cStatus === "unverified" ? (
            <Card s={{ border: `2px dashed ${THEME.BD}`, background: "#FAFAFA", textAlign: "center", padding: "36px 24px" }}>
              <div style={{ width: 48, height: 48, borderRadius: "50%", background: "#F1F5F9", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 14px" }}>
                <Shield size={20} style={{ color: THEME.MT }} />
              </div>
              <h3 style={{ color: THEME.NV, fontWeight: 700, fontSize: 15, margin: "0 0 6px" }}>No Compliance Report Yet</h3>
              <p style={{ color: THEME.MT, fontSize: 13, margin: "0 0 20px", maxWidth: 380, marginLeft: "auto", marginRight: "auto" }}>This NGO has not completed a compliance verification. Documents have not been checked against {organisation.state} state laws or central regulations.</p>
              <button onClick={() => go("submit")} style={{ background: THEME.OR, color: THEME.WH, border: "none", borderRadius: 8, padding: "11px 22px", fontSize: 13, fontWeight: 700, cursor: "pointer", display: "inline-flex", alignItems: "center", gap: 6, boxShadow: "0 2px 8px rgba(232,96,26,.25)" }}>
                Run Compliance Check <ChevronRight size={14} />
              </button>
            </Card>
          ) : (
            <div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 10, marginBottom: 14 }}>
                {[['Passed', FINDINGS.filter((finding) => finding.status === "PASS").length, THEME.GR, "#DCFCE7"], ['Failed', FINDINGS.filter((finding) => finding.status === "FAIL").length, THEME.RD, "#FEE2E2"], ['Uncertain', FINDINGS.filter((finding) => finding.status === "UNCERTAIN").length, THEME.AM, "#FEF3C7"], ['Total', '7', THEME.NV, "#EEF2F9"]].map(([label, value, color, background]) => (
                  <div key={label} style={{ background, borderRadius: 8, padding: "12px 14px", textAlign: "center" }}>
                    <div style={{ fontSize: 20, fontWeight: 900, color }}>{value}</div>
                    <div style={{ fontSize: 10, color, marginTop: 2, textTransform: "uppercase", letterSpacing: "0.04em" }}>{label}</div>
                  </div>
                ))}
              </div>
              <div style={{ display: "grid", gap: 7 }}>
                {FINDINGS.map((finding) => {
                  const color = finding.status === "PASS" ? THEME.GR : finding.status === "FAIL" ? THEME.RD : THEME.AM;
                  return (
                    <div key={finding.id} style={{ background: THEME.WH, borderRadius: 8, border: `1px solid ${THEME.BD}`, borderLeft: `3px solid ${color}`, padding: "10px 14px", display: "flex", alignItems: "center", gap: 12 }}>
                      <Badge s={finding.status} />
                      <div style={{ flex: 1, fontSize: 13, fontWeight: 500, color: THEME.NV }}>{finding.dim}</div>
                      <div style={{ fontSize: 11, color: THEME.MT }}>{Math.round(finding.conf * 100)}% confidence</div>
                    </div>
                  );
                })}
              </div>
              <div style={{ marginTop: 14, display: "flex", gap: 8 }}>
                <button onClick={() => go("dashboard")} style={{ background: THEME.OR, color: THEME.WH, border: "none", borderRadius: 7, padding: "9px 18px", fontSize: 13, fontWeight: 600, cursor: "pointer" }}>View Full Report</button>
                <button onClick={() => go("submit")} style={{ background: THEME.WH, color: THEME.NV, border: `1px solid ${THEME.BD}`, borderRadius: 7, padding: "9px 16px", fontSize: 13, cursor: "pointer" }}>Re-run Check</button>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div style={{ background: THEME.BG, minHeight: "100vh" }}>
      <Crumb items={[{ label: "Home", page: "landing" }, { label: "NPO Directory" }]} go={go} />
      <div style={{ background: THEME.WH, borderBottom: `1px solid ${THEME.BD}`, padding: 20 }}>
        <div style={{ maxWidth: 900, margin: "0 auto" }}>
          <div style={{ marginBottom: 14 }}>
            <h2 style={{ margin: "0 0 4px", fontSize: 18, fontWeight: 800, color: THEME.NV }}>NPO Directory</h2>
            <p style={{ margin: 0, fontSize: 13, color: THEME.MT }}>Search registered NGOs and view their compliance verification status.</p>
          </div>
          <div style={{ position: "relative", marginBottom: 12 }}>
            <Search size={15} style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", color: THEME.MT }} />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search by name, sector, or registration number…" style={{ width: "100%", padding: "10px 12px 10px 36px", border: `1px solid ${THEME.BD}`, borderRadius: 8, fontSize: 13, color: THEME.TX, background: THEME.WH, boxSizing: "border-box", outline: "none" }} />
          </div>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
            <span style={{ fontSize: 12, color: THEME.MT }}>State:</span>
            {['All', 'Maharashtra', 'Delhi', 'Karnataka', 'Rajasthan'].map((state) => (
              <button key={state} onClick={() => setFilterState(state)} style={{ background: filterState === state ? THEME.NV : THEME.WH, color: filterState === state ? THEME.WH : THEME.MT, border: `1px solid ${THEME.BD}`, borderRadius: 16, padding: "3px 12px", fontSize: 11, cursor: "pointer", fontWeight: filterState === state ? 600 : 400 }}>
                {state}
              </button>
            ))}
            <span style={{ fontSize: 12, color: THEME.MT, marginLeft: 8 }}>Status:</span>
            {['All', 'Verified', 'Partial', 'Unverified'].map((status) => (
              <button key={status} onClick={() => setFilterVerification(status)} style={{ background: filterVerification === status ? THEME.NV : THEME.WH, color: filterVerification === status ? THEME.WH : THEME.MT, border: `1px solid ${THEME.BD}`, borderRadius: 16, padding: "3px 12px", fontSize: 11, cursor: "pointer", fontWeight: filterVerification === status ? 600 : 400 }}>
                {status}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div style={{ maxWidth: 900, margin: "0 auto", padding: "16px 20px" }}>
        <div style={{ fontSize: 12, color: THEME.MT, marginBottom: 12 }}>{filtered.length} NGO{filtered.length !== 1 ? "s" : ""} found</div>
        <div style={{ display: "grid", gap: 10 }}>
          {filtered.map((organisation) => {
            const status = verificationColors[organisation.cStatus];
            return (
              <div key={organisation.reg} onClick={() => setSelected(organisation)} style={{ background: THEME.WH, borderRadius: 10, border: `1px solid ${THEME.BD}`, padding: "14px 18px", cursor: "pointer", display: "flex", alignItems: "center", gap: 14, transition: "box-shadow 0.15s" }} onMouseEnter={(event) => { event.currentTarget.style.boxShadow = "0 2px 12px rgba(0,0,0,.08)"; }} onMouseLeave={(event) => { event.currentTarget.style.boxShadow = "none"; }}>
                <div style={{ width: 40, height: 40, borderRadius: 10, background: "#EEF2F9", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800, fontSize: 14, color: THEME.NV, flexShrink: 0 }}>{organisation.name[0]}</div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 700, color: THEME.NV, fontSize: 14, marginBottom: 2 }}>{organisation.name}</div>
                  <div style={{ fontSize: 11, color: THEME.MT }}>{organisation.state} · {organisation.type} · {organisation.sector} · Reg: {organisation.reg}</div>
                </div>
                <div style={{ textAlign: "center", minWidth: 52, flexShrink: 0 }}>
                  {organisation.score ? (
                    <div>
                      <div style={{ fontSize: 18, fontWeight: 900, color: organisation.score >= 80 ? THEME.GR : organisation.score >= 60 ? THEME.AM : THEME.RD }}>{organisation.score}</div>
                      <div style={{ fontSize: 9, color: THEME.MT, textTransform: "uppercase" }}>Score</div>
                    </div>
                  ) : <div style={{ fontSize: 12, color: THEME.MT }}>—</div>}
                </div>
                <span style={{ background: status.bg, color: status.c, fontSize: 11, fontWeight: 700, padding: "4px 12px", borderRadius: 12, flexShrink: 0 }}>{status.t}</span>
                {organisation.cStatus === "unverified" ? (
                  <button onClick={(event) => { event.stopPropagation(); go("submit"); }} style={{ background: THEME.OR, color: THEME.WH, border: "none", borderRadius: 6, padding: "7px 12px", fontSize: 11, fontWeight: 700, cursor: "pointer", flexShrink: 0, whiteSpace: "nowrap" }}>Run Check</button>
                ) : <ChevronRight size={16} style={{ color: THEME.MT, flexShrink: 0 }} />}
              </div>
            );
          })}
        </div>

        {filtered.length === 0 && (
          <div style={{ textAlign: "center", padding: "40px 20px", color: THEME.MT }}>
            <Search size={28} style={{ display: "block", margin: "0 auto 10px", opacity: 0.4 }} />
            <div style={{ fontWeight: 600, color: THEME.NV, marginBottom: 4 }}>No NGOs found</div>
            <div style={{ fontSize: 12 }}>Try a different search term or filter</div>
          </div>
        )}

        <div style={{ marginTop: 20, background: THEME.WH, borderRadius: 9, border: `1px solid ${THEME.BD}`, padding: "12px 16px", display: "flex", gap: 20, flexWrap: "wrap", alignItems: "center" }}>
          <span style={{ fontSize: 11, fontWeight: 700, color: THEME.NV }}>Status key:</span>
          {[['Verified', THEME.GR, "#DCFCE7", "Compliance check passed"], ['Partially Verified', THEME.AM, "#FEF3C7", "Check run, some issues found"], ['Unverified', THEME.MT, "#F1F5F9", "No compliance check run yet"]].map(([label, color, background, description]) => (
            <div key={label} style={{ display: "flex", gap: 6, alignItems: "center" }}>
              <span style={{ background, color, fontSize: 10, fontWeight: 700, padding: "2px 8px", borderRadius: 10 }}>{label}</span>
              <span style={{ fontSize: 11, color: THEME.MT }}>{description}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
