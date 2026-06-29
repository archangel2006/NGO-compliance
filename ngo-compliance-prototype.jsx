import { useState, useEffect } from "react";
import { ChevronRight, FileText, Upload, Download, Eye, Shield, Users, DollarSign, Receipt, Globe, BarChart2, Building2, ChevronDown, ChevronUp, CheckCircle, AlertTriangle, XCircle, Clock, Search, Bell, LogIn, Home, List, BarChart, FileCheck, Menu } from "lucide-react";

// ── Design tokens ─────────────────────────────────────────────────
const OR="#E8601A", NV="#1A3A6B", GR="#16A34A", RD="#DC2626", AM="#D97706";
const BG="#F4F6FA", WH="#FFFFFF", BD="#E2E8F0", MT="#64748B", TX="#1E293B";

// ── Mock data ─────────────────────────────────────────────────────
const NGO={name:"Asha Jyoti Welfare Foundation",id:"MH/2019/0234521",state:"Maharashtra",type:"Public Trust",reg:"E-23847/2019",pan:"AAETA2384K",sector:"Education & Women Empowerment",by:"Priya Sharma (Secretary)",date:"14 March 2019",city:"Pune, Maharashtra"};

const DOCS=[
  {name:"Trust Deed",cat:"Registration",size:"2.4 MB",pages:18,ok:true},
  {name:"Charity Commissioner Certificate",cat:"Registration",size:"1.1 MB",pages:2,ok:true},
  {name:"12A Certificate",cat:"Tax",size:"0.8 MB",pages:3,ok:true},
  {name:"80G Certificate",cat:"Tax",size:"0.7 MB",pages:3,ok:true},
  {name:"Annual Report 2024–25",cat:"Financial",size:"3.2 MB",pages:42,ok:true},
  {name:"FCRA Certificate",cat:"FCRA",size:"0.9 MB",pages:4,ok:true},
  {name:"Audited Financial Statements",cat:"Audit",size:"4.1 MB",pages:56,ok:true},
];

const FINDINGS=[
  {id:1,dim:"Registration & Legal Status",icon:Shield,status:"PASS",conf:0.95,route:"auto",
   citation:"Section 18, Bombay Public Trusts Act, 1950; Maharashtra Charity Commissioner Guidelines, 2018",
   evidence:"Trust Deed dated 14 March 2019 confirms registration under Bombay Public Trusts Act, 1950. Certificate No. MH-CC-2019-23847 issued. Registration current and valid.",
   reasoning:"Trust Deed clearly establishes registration under BPT Act 1950. Charity Commissioner certificate matches reg number. All mandatory fields present and consistent."},
  {id:2,dim:"Governance Structure",icon:Building2,status:"PASS",conf:0.89,route:"auto",
   citation:"Section 2(13) & Section 14, Bombay Public Trusts Act, 1950 — Composition of Board of Trustees",
   evidence:"Trust Deed lists 5 trustees: President, Secretary, Treasurer and 2 members. Board composition documented with names, addresses and designations.",
   reasoning:"Governing body satisfies Section 14 requirements. No related-party concentration issues. Quorum requirements clearly stated in Trust Deed."},
  {id:3,dim:"Membership Requirements",icon:Users,status:"UNCERTAIN",conf:0.64,route:"human",qStatus:"pending",officer:"Officer Ramesh K.",role:"Sr. Compliance Officer",
   citation:"Section 4, BPT Act, 1950; Maharashtra Charity Commissioner Circular No. 12/2021",
   evidence:"Trust Deed lists 5 trustees. However Circular 12/2021 may impose additional sector-specific requirements. OCR extraction on page 4 of Trust Deed incomplete.",
   reasoning:"Base trustee count meets minimum statutory requirements. However a 2021 circular for education-sector trusts could not be fully assessed due to partial OCR on page 4. Human review recommended."},
  {id:4,dim:"Financial Compliance",icon:DollarSign,status:"FAIL",conf:0.91,route:"auto",
   citation:"Section 32 & 33, Bombay Public Trusts Act, 1950; NGO Darpan Guidelines Clause 7.2",
   evidence:"Annual Report 2024–25 submitted. Fund utilisation statement for CSR grant FY 2023–24 (₹18.5L from TCS Foundation) is ABSENT from submitted documents.",
   reasoning:"NGO received CSR funding in FY 2023–24 but mandatory fund utilisation statement is missing. Section 32 requires detailed accounts for all receipts above ₹10,000. Critical compliance gap.",
   fix:"Submit fund utilisation statement for FY 2023–24 (₹18.5L CSR grant, TCS Foundation) under Section 32, Bombay Public Trusts Act. File with Charity Commissioner and upload to Darpan portal under 'Grant Utilisation'."},
  {id:5,dim:"Tax Compliance",icon:Receipt,status:"PASS",conf:0.93,route:"auto",
   citation:"Section 12A & 80G, Income Tax Act, 1961 — Tax Exemption for Charitable Organisations",
   evidence:"12A Certificate No. IT-12A-MH-2019-4821 valid until 31 March 2028. 80G Certificate valid until 31 March 2028. Both verified against IT records.",
   reasoning:"Both certificates valid and within renewal window. Certificate numbers, NGO name and PAN match across all submitted documents. No pending IT notices."},
  {id:6,dim:"FCRA Compliance",icon:Globe,status:"PASS",conf:0.88,route:"auto",
   citation:"Section 11 & 17, FCRA 2010; FCRA Amendment Rules, 2020",
   evidence:"FCRA Reg. No. 083780142 granted by MHA. Annual return filed for FY 2024–25. Designated FCRA bank account with SBI (A/C ending 4892) maintained.",
   reasoning:"FCRA registration valid. Annual returns filed. Dedicated FCRA bank account maintained as mandated by 2020 amendment rules."},
  {id:7,dim:"Audit Requirements",icon:BarChart2,status:"UNCERTAIN",conf:0.71,route:"human",qStatus:"reviewed",officer:"Officer Lakshmi T.",role:"FCRA Specialist",
   determination:"PASS",reviewedAt:"23 Jun 2026, 3:45 PM",
   officerNotes:"FCRA audit report found on page 12 of the combined audit document. Header was unclear due to scan quality but content is complete and compliant. Confirmed PASS.",
   citation:"Section 33, BPT Act 1950; FCRA Rules 2011, Rule 17 — Audit of FCRA Accounts",
   evidence:"Audited statements submitted. Auditor: M/s Mehta & Associates (ICAI Reg. 112847). Separate FCRA audit under Rule 17 not clearly identified in submitted documents.",
   reasoning:"General audit report present from registered CA firm. However FCRA Rule 17 requires a separate audit for foreign contribution accounts not clearly identified. Human review recommended."},
];

const STEPS=[
  "Receiving uploaded documents (7 files · 13.2 MB)",
  "Extracting text with PyMuPDF…",
  "Running Tesseract OCR — lang: eng+mar",
  "Structured field extraction (names, dates, reg numbers)",
  "Querying legal corpus — Maharashtra Acts · FCRA · IT Act",
  "Assessing 7 compliance dimensions via RAG + LLM",
  "Routing 2 findings to Human Review Queue",
  "Generating compliance report",
];

// ── Reusable atoms ────────────────────────────────────────────────
function Badge({s,lg}){
  const m={PASS:{bg:"#DCFCE7",c:GR,t:"✓ PASS"},FAIL:{bg:"#FEE2E2",c:RD,t:"✗ FAIL"},UNCERTAIN:{bg:"#FEF3C7",c:AM,t:"? UNCERTAIN"}};
  const r=m[s]||m.UNCERTAIN;
  return <span style={{background:r.bg,color:r.c,padding:lg?"5px 14px":"3px 10px",borderRadius:20,fontSize:lg?13:11,fontWeight:700,whiteSpace:"nowrap"}}>{r.t}</span>;
}
function Bar({v}){
  const p=Math.round(v*100),c=p>=85?GR:p>=70?AM:RD;
  return <div style={{display:"flex",alignItems:"center",gap:8}}>
    <div style={{flex:1,background:BD,borderRadius:4,height:5}}><div style={{width:`${p}%`,height:5,borderRadius:4,background:c}}/></div>
    <span style={{fontSize:11,color:c,fontWeight:600,minWidth:28}}>{p}%</span>
  </div>;
}
function Card({children,s}){return <div style={{background:WH,borderRadius:10,border:`1px solid ${BD}`,padding:20,...s}}>{children}</div>;}
function Crumb({items,go}){
  return <div style={{background:WH,borderBottom:`1px solid ${BD}`,padding:"10px 20px"}}>
    <div style={{maxWidth:1040,margin:"0 auto",display:"flex",alignItems:"center",gap:4,fontSize:12,color:MT,flexWrap:"wrap"}}>
      {items.map((x,i)=><span key={i} style={{display:"flex",alignItems:"center",gap:4}}>
        {i>0&&<ChevronRight size={11}/>}
        <span style={{color:x.page?OR:NV,fontWeight:x.page?400:600,cursor:x.page?"pointer":"default"}} onClick={x.page?()=>go(x.page):undefined}>{x.label}</span>
      </span>)}
    </div>
  </div>;
}
function Ring({score}){
  const r=48,circ=2*Math.PI*r,dash=(score/100)*circ,c=score>=80?GR:score>=60?AM:RD;
  return <div style={{position:"relative",width:120,height:120,flexShrink:0}}>
    <svg viewBox="0 0 120 120" style={{transform:"rotate(-90deg)",position:"absolute",top:0,left:0}}>
      <circle cx="60" cy="60" r={r} fill="none" stroke="#E2E8F0" strokeWidth="9"/>
      <circle cx="60" cy="60" r={r} fill="none" stroke={c} strokeWidth="9" strokeDasharray={`${dash} ${circ-dash}`} strokeLinecap="round"/>
    </svg>
    <div style={{position:"absolute",inset:0,display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center"}}>
      <span style={{fontSize:26,fontWeight:900,color:c,lineHeight:1}}>{score}</span>
      <span style={{fontSize:9,color:c,fontWeight:700,textTransform:"uppercase",marginTop:2}}>At Risk</span>
    </div>
  </div>;
}

// ── Gov bar ───────────────────────────────────────────────────────
function GovBar(){
  return <div style={{background:NV,color:"#94A3B8",fontSize:11,padding:"4px 20px",display:"flex",gap:8,alignItems:"center"}}>
    <span style={{color:"#C49A1A",fontWeight:700}}>भारत सरकार</span>
    <span style={{color:"#334155"}}>|</span>
    <span>Government of India</span>
    <span style={{marginLeft:"auto",color:"#475569"}}>National Informatics Centre · NITI Aayog</span>
  </div>;
}

// ── Nav ───────────────────────────────────────────────────────────
function Nav({go,page}){
  const links=["Home","NPO Directory","Compliance Check"];
  const pageMap={"Home":"landing","NPO Directory":"directory","Compliance Check":"submit"};
  return <div style={{background:WH,borderBottom:`3px solid ${OR}`,padding:"0 20px",display:"flex",alignItems:"center"}}>
    <div style={{display:"flex",alignItems:"center",gap:10,padding:"10px 0",marginRight:28,cursor:"pointer"}} onClick={()=>go("landing")}>
      <div>
        <div style={{fontWeight:800,fontSize:17,color:NV,letterSpacing:"0.02em"}}>NGO Compliance</div>
        <div style={{fontSize:9,color:MT}}>Verification System · Pilot</div>
      </div>
    </div>
    <div style={{display:"flex",flex:1}}>
      {links.map(l=>{
        const active=(l==="Compliance Check"&&["submit","processing","dashboard","findings","queue","report"].includes(page))||(l==="NPO Directory"&&page==="directory");
        const isHome=l==="Home"&&page==="landing";
        const hi=active||isHome;
        return <div key={l} onClick={pageMap[l]?()=>go(pageMap[l]):undefined}
          style={{padding:"14px 12px",fontSize:12,cursor:pageMap[l]?"pointer":"default",color:hi?OR:NV,
            borderBottom:hi?`3px solid ${OR}`:"3px solid transparent",fontWeight:hi?700:400,whiteSpace:"nowrap"}}>
          {l}
        </div>;
      })}
    </div>
    <div style={{display:"flex",gap:6,alignItems:"center"}}>
      <div style={{position:"relative",cursor:"pointer",padding:6}}>
        <Bell size={16} style={{color:MT}}/>
        <span style={{position:"absolute",top:3,right:3,width:7,height:7,borderRadius:"50%",background:RD}}/>
      </div>
      <button onClick={()=>go("landing")} style={{background:OR,color:WH,border:"none",borderRadius:6,padding:"7px 14px",fontWeight:600,fontSize:12,cursor:"pointer",display:"flex",alignItems:"center",gap:5}}>
        <LogIn size={13}/>Login / Signup
      </button>
    </div>
  </div>;
}

// ══════════════════════════════════════════════════════════════════
// PAGE 1 — LANDING
// ══════════════════════════════════════════════════════════════════
function Landing({go}){
  return <div style={{background:BG,minHeight:"100vh"}}>
    {/* Hero */}
    <div style={{background:"linear-gradient(135deg,#FFFBF7 0%,#FFF5EE 50%,#F0F4FF 100%)",borderBottom:`1px solid #F0E8E0`,padding:"48px 24px 40px"}}>
      <div style={{maxWidth:960,margin:"0 auto",display:"grid",gridTemplateColumns:"1fr 1fr",gap:40,alignItems:"center"}}>
        <div>
          <span style={{background:"#FFF3EB",color:OR,padding:"4px 12px",borderRadius:20,fontSize:11,fontWeight:700,border:`1px solid #FDDBC8`,display:"inline-block",marginBottom:14}}>
            PILOT · Maharashtra · Delhi · Karnataka · Rajasthan
          </span>
          <h1 style={{color:NV,fontSize:32,fontWeight:800,margin:"0 0 12px",lineHeight:1.25}}>
            A Digital Platform To<br/>
            <span style={{color:OR}}>Verify NGO Compliance</span>
          </h1>
          <p style={{color:MT,fontSize:14,lineHeight:1.75,margin:"0 0 24px",maxWidth:420}}>
            Upload your NGO's registration documents. Our AI engine cross-checks them against state-specific laws and returns a detailed, evidence-backed compliance report.
          </p>
          <div style={{display:"flex",gap:10}}>
            <button onClick={()=>go("submit")} style={{background:OR,color:WH,border:"none",borderRadius:8,padding:"12px 22px",fontSize:14,fontWeight:700,cursor:"pointer",display:"flex",alignItems:"center",gap:6,boxShadow:"0 2px 8px rgba(232,96,26,.3)"}}>
              Get Started <ChevronRight size={15}/>
            </button>
            <button onClick={()=>go("dashboard")} style={{background:WH,color:NV,border:`1px solid ${BD}`,borderRadius:8,padding:"12px 18px",fontSize:14,cursor:"pointer",fontWeight:500}}>
              View Sample Report
            </button>
          </div>

        </div>
        {/* Illustration panel */}
        <div style={{display:"flex",flexDirection:"column",gap:10}}>
          {/* Mini flow diagram */}
          <div style={{background:WH,borderRadius:12,border:`1px solid ${BD}`,padding:20,boxShadow:"0 2px 12px rgba(26,58,107,.06)"}}>
            <div style={{fontSize:11,fontWeight:700,color:NV,marginBottom:14,textTransform:"uppercase",letterSpacing:"0.07em"}}>How it works</div>
            {[[Upload,"Upload Documents","Trust Deed, 12A/80G, FCRA, Audits"],[Search,"AI Extracts & Analyses","OCR + RAG over Indian legal corpus"],[Shield,"State-Law Matching","Acts, Gazettes, FCRA, IT provisions"],[FileCheck,"Compliance Report","Pass / Fail / Uncertain + legal citations"]].map(([Ic,t,d],i)=>(
              <div key={i}>
                <div style={{display:"flex",gap:10,alignItems:"center",padding:"8px 0"}}>
                  <div style={{width:28,height:28,borderRadius:6,background:"#FFF3EB",display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0}}>
                    <Ic size={14} style={{color:OR}}/>
                  </div>
                  <div><div style={{fontSize:13,fontWeight:600,color:NV}}>{t}</div><div style={{fontSize:11,color:MT}}>{d}</div></div>
                </div>
                {i<3&&<div style={{borderLeft:`2px dashed ${BD}`,height:8,marginLeft:14}}/>}
              </div>
            ))}
          </div>
          {/* Stats row */}
          <div style={{display:"grid",gridTemplateColumns:"1fr 1fr 1fr",gap:8}}>
            {[["7","Dimensions Checked"],["4 States","Pilot Scope"],["RAG+LLM","AI Engine"]].map(([v,l])=>(
              <div key={l} style={{background:WH,borderRadius:8,border:`1px solid ${BD}`,padding:"12px 10px",textAlign:"center"}}>
                <div style={{color:OR,fontWeight:800,fontSize:16}}>{v}</div>
                <div style={{color:MT,fontSize:10,marginTop:2}}>{l}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>

    {/* Feature cards */}
    <div style={{maxWidth:960,margin:"0 auto",padding:"36px 24px"}}>
      <div style={{textAlign:"center",marginBottom:24}}>
        <div style={{color:OR,fontSize:11,fontWeight:700,letterSpacing:"0.1em",textTransform:"uppercase",marginBottom:6}}>WHAT WE VERIFY</div>
        <h2 style={{fontSize:22,fontWeight:800,color:NV,margin:0}}>Compliance as a Decision-Support Layer</h2>
        <p style={{color:MT,marginTop:6,fontSize:13}}>Not an automated ruling system. An AI assistant for compliance officers.</p>
      </div>
      <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:14,marginBottom:36}}>
        {[
          [Shield,"Registration","Bombay Public Trusts Act, Societies Act, Charity Commissioner filings"],
          [Building2,"Governance","Board composition, trustee qualifications, quorum requirements"],
          [Receipt,"Tax 12A/80G","Income Tax exemption certificates, validity, PAN matching"],
          [Globe,"FCRA","Foreign contribution registration, designated bank account, annual returns"],
        ].map(([Ic,t,d])=>(
          <Card key={t} s={{padding:16}}>
            <div style={{width:34,height:34,borderRadius:8,background:"#FFF3EB",display:"flex",alignItems:"center",justifyContent:"center",marginBottom:10}}>
              <Ic size={16} style={{color:OR}}/>
            </div>
            <div style={{fontWeight:700,color:NV,fontSize:13,marginBottom:5}}>{t}</div>
            <div style={{color:MT,fontSize:11,lineHeight:1.6}}>{d}</div>
          </Card>
        ))}
      </div>

      {/* States */}
      <div style={{background:WH,borderRadius:12,border:`1px solid ${BD}`,padding:24,marginBottom:24}}>
        <div style={{fontSize:12,fontWeight:700,color:NV,marginBottom:16,textTransform:"uppercase",letterSpacing:"0.06em"}}>Pilot States — Legal Corpus Coverage</div>
        <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:12}}>
          {[["Maharashtra","Bombay Public Trusts Act, 1950\nSocieties Registration Act\nCharity Commissioner Rules"],
            ["Delhi","Delhi Societies Registration Act, 2006\nFCRA Guidelines\nIncome Tax provisions"],
            ["Karnataka","Karnataka Societies Registration Act, 1960\nPublic Trust provisions\nIT Act"],
            ["Rajasthan","Rajasthan Societies Registration Act, 1958\nState Public Trust Act\nIT Act"],
          ].map(([st,acts])=>(
            <div key={st} style={{background:"#F8FAFC",borderRadius:8,padding:12,border:`1px solid ${BD}`}}>
              <div style={{fontWeight:700,color:NV,fontSize:13,marginBottom:5}}>{st}</div>
              {acts.split("\n").map((a,i)=><div key={i} style={{fontSize:11,color:MT,lineHeight:1.6}}>· {a}</div>)}
            </div>
          ))}
        </div>
      </div>

      {/* CTA banner */}
      <div style={{background:"linear-gradient(135deg,#FFF3EB,#FFF8F5)",border:`1px solid #FDDBC8`,borderRadius:12,padding:"28px 32px",display:"flex",alignItems:"center",justifyContent:"space-between"}}>
        <div>
          <h3 style={{color:NV,fontSize:17,fontWeight:700,margin:"0 0 5px"}}>Ready to check your NGO's compliance?</h3>
          <p style={{color:MT,margin:0,fontSize:13}}>Upload documents and receive a state-specific compliance report.</p>
        </div>
        <button onClick={()=>go("submit")} style={{background:OR,color:WH,border:"none",borderRadius:8,padding:"12px 22px",fontSize:14,fontWeight:700,cursor:"pointer",display:"flex",alignItems:"center",gap:6,flexShrink:0,boxShadow:"0 2px 8px rgba(232,96,26,.3)"}}>
          Start Compliance Check <ChevronRight size={15}/>
        </button>
      </div>
    </div>
  </div>;
}

// ══════════════════════════════════════════════════════════════════
// PAGE 2 — SUBMISSION (3-step: State → Details → Documents)
// ══════════════════════════════════════════════════════════════════
const STATES=[
  {code:"MH",name:"Maharashtra",acts:["Bombay Public Trusts Act, 1950","Societies Registration Act (MH)","Charity Commissioner Rules"],complexity:"High",ngos:"2,84,000+"},
  {code:"DL",name:"Delhi",acts:["Delhi Societies Registration Act, 2006","Delhi Public Charitable Trust","NITI Aayog Darpan Guidelines"],complexity:"Medium",ngos:"96,000+"},
  {code:"KA",name:"Karnataka",acts:["Karnataka Societies Registration Act, 1960","Karnataka Public Trust Act","Charity Commissioner (KA) Rules"],complexity:"Medium",ngos:"1,12,000+"},
  {code:"RJ",name:"Rajasthan",acts:["Rajasthan Societies Registration Act, 1958","Rajasthan Public Trusts Act","Rajasthan Charity Commissioner Rules"],complexity:"Medium",ngos:"78,000+"},
];

function Submit({go}){
  const [subStep,setSubStep]=useState(0);
  const [selState,setSelState]=useState(null);
  const [docsLoaded,setDocsLoaded]=useState(false);
  const [form,setForm]=useState({name:"",type:"",pan:"",year:"",sector:"",email:""});

  const set=k=>e=>setForm(f=>({...f,[k]:e.target.value}));
  const autoFillForm=()=>setForm({name:NGO.name,type:"Public Trust",pan:NGO.pan,year:"2019",sector:NGO.sector,email:"priya.sharma@ashajyoti.org"});
  const formComplete=form.name&&form.type&&form.pan&&form.year&&form.sector&&form.email;

  const inp=(label,key,ph)=>(
    <div>
      <label style={{fontSize:11,fontWeight:700,color:NV,display:"block",marginBottom:5,textTransform:"uppercase",letterSpacing:"0.05em"}}>{label}</label>
      <input value={form[key]} onChange={set(key)} placeholder={ph}
        style={{width:"100%",padding:"9px 12px",border:`1px solid ${form[key]?OR+"66":BD}`,borderRadius:7,fontSize:13,
          background:WH,color:TX,boxSizing:"border-box",outline:"none"}}/>
    </div>
  );

  const STEP_LABELS=["Select State","NGO Details","Upload Documents","Submit"];
  const complexCol={High:RD,Medium:AM};
  const stateName=STATES.find(s=>s.code===selState)?.name||"";

  return <div style={{background:BG,minHeight:"100vh"}}>
    <Crumb items={[{label:"Home",page:"landing"},{label:"Compliance Check"}]} go={go}/>

    {/* Stepper */}
    <div style={{background:WH,borderBottom:`1px solid ${BD}`,padding:"12px 20px"}}>
      <div style={{maxWidth:860,margin:"0 auto",display:"flex",alignItems:"center"}}>
        {STEP_LABELS.map((s,i)=>{
          const done=i<subStep;
          const cur=i===subStep;
          return <div key={s} style={{display:"flex",alignItems:"center",flex:i<3?1:0}}>
            <div style={{display:"flex",alignItems:"center",gap:6}}>
              <div style={{width:24,height:24,borderRadius:"50%",background:done?GR:cur?OR:BD,color:WH,display:"flex",alignItems:"center",justifyContent:"center",fontWeight:700,fontSize:10}}>
                {done?"✓":i+1}
              </div>
              <span style={{fontSize:12,fontWeight:cur?700:400,color:cur?NV:done?GR:MT,whiteSpace:"nowrap"}}>{s}</span>
            </div>
            {i<3&&<div style={{flex:1,height:1,background:done?GR:BD,margin:"0 10px",transition:"background 0.3s"}}/>}
          </div>;
        })}
      </div>
    </div>

    <div style={{maxWidth:860,margin:"0 auto",padding:"28px 20px"}}>

      {/* ── STEP 0: Select State ── */}
      {subStep===0&&<div>
        <div style={{textAlign:"center",marginBottom:28}}>
          <div style={{color:OR,fontSize:11,fontWeight:700,letterSpacing:"0.1em",textTransform:"uppercase",marginBottom:6}}>STEP 1 OF 3</div>
          <h2 style={{fontSize:22,fontWeight:800,color:NV,margin:"0 0 8px"}}>Select State of Registration</h2>
          <p style={{color:MT,fontSize:13,margin:0}}>Each state has different NGO laws. We'll cross-reference your documents against the exact rules for your state.</p>
        </div>
        <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:16,marginBottom:20}}>
          {STATES.map(st=>{
            const sel=selState===st.code;
            return <div key={st.code} onClick={()=>setSelState(st.code)}
              style={{background:WH,borderRadius:12,border:`2px solid ${sel?OR:BD}`,padding:20,cursor:"pointer",
                boxShadow:sel?"0 0 0 3px rgba(232,96,26,.12)":"none",transition:"all 0.15s",position:"relative"}}>
              {sel&&<div style={{position:"absolute",top:14,right:14,width:20,height:20,borderRadius:"50%",background:OR,display:"flex",alignItems:"center",justifyContent:"center",color:WH,fontSize:11,fontWeight:700}}>✓</div>}
              <div style={{display:"flex",alignItems:"center",gap:12,marginBottom:12}}>
                <div style={{width:44,height:44,borderRadius:10,background:sel?"#FFF3EB":"#F4F6FA",border:`1px solid ${sel?OR:BD}`,display:"flex",alignItems:"center",justifyContent:"center",fontWeight:900,fontSize:15,color:sel?OR:NV}}>
                  {st.code}
                </div>
                <div>
                  <div style={{fontWeight:800,fontSize:16,color:NV}}>{st.name}</div>
                  <div style={{fontSize:11,color:MT,marginTop:1}}>{st.ngos} registered NGOs</div>
                </div>
              </div>
              <div style={{marginBottom:10}}>
                {st.acts.map(a=><div key={a} style={{fontSize:11,color:MT,lineHeight:1.6}}>· {a}</div>)}
              </div>
              <div style={{display:"flex",alignItems:"center",gap:6}}>
                <span style={{fontSize:10,fontWeight:700,color:complexCol[st.complexity]||AM,background:st.complexity==="High"?"#FEE2E2":"#FEF3C7",padding:"2px 8px",borderRadius:10}}>{st.complexity} Complexity</span>
                <span style={{fontSize:10,color:MT}}>+ Central: FCRA · IT Act · Darpan</span>
              </div>
            </div>;
          })}
        </div>
        <div style={{background:"#EEF2F9",border:"1px solid #C7D7F0",borderRadius:9,padding:"12px 16px",marginBottom:24,display:"flex",gap:10,alignItems:"center"}}>
          <Shield size={14} style={{color:NV,flexShrink:0}}/>
          <div style={{fontSize:12,color:NV,lineHeight:1.6}}><strong>Central regulations always included</strong> — FCRA, Income Tax Act (12A / 80G), and NITI Aayog Darpan guidelines are checked for every submission automatically.</div>
        </div>
        <div style={{display:"flex",justifyContent:"space-between"}}>
          <button onClick={()=>go("landing")} style={{background:WH,color:NV,border:`1px solid ${BD}`,borderRadius:7,padding:"10px 18px",fontSize:13,cursor:"pointer"}}>← Back</button>
          <button onClick={()=>selState&&setSubStep(1)} disabled={!selState}
            style={{background:selState?OR:"#CBD5E1",color:WH,border:"none",borderRadius:7,padding:"10px 24px",fontSize:13,fontWeight:700,cursor:selState?"pointer":"not-allowed",display:"flex",alignItems:"center",gap:6,boxShadow:selState?"0 2px 8px rgba(232,96,26,.3)":"none"}}>
            Next: NGO Details <ChevronRight size={15}/>
          </button>
        </div>
      </div>}

      {/* ── STEP 1: NGO Details ── */}
      {subStep===1&&<div style={{display:"grid",gridTemplateColumns:"1fr 280px",gap:18}}>
        <div>
          <div style={{background:"#ECFDF5",border:"1px solid #A7F3D0",borderRadius:7,padding:"8px 14px",marginBottom:14,display:"flex",alignItems:"center",justifyContent:"space-between"}}>
            <div style={{fontSize:12,color:"#065F46",display:"flex",gap:6,alignItems:"center"}}>
              <CheckCircle size={13}/><strong>{stateName}</strong> selected · Central regulations included
            </div>
            <button onClick={()=>setSubStep(0)} style={{fontSize:11,color:OR,background:"none",border:"none",cursor:"pointer",textDecoration:"underline"}}>Change</button>
          </div>
          <Card>
            <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:16}}>
              <div>
                <h2 style={{margin:0,fontSize:15,fontWeight:700,color:NV}}>NGO Details</h2>
                <p style={{margin:"3px 0 0",color:MT,fontSize:12}}>Enter your NGO's basic information to route the compliance check.</p>
              </div>
              <button onClick={autoFillForm} style={{background:"#FFF3EB",color:OR,border:`1px solid #FDDBC8`,borderRadius:6,padding:"7px 12px",fontSize:12,fontWeight:600,cursor:"pointer",whiteSpace:"nowrap",flexShrink:0}}>✦ Auto-fill Sample</button>
            </div>
            <div style={{display:"grid",gap:12}}>
              {inp("Organisation Name *","name","e.g. Asha Jyoti Welfare Foundation")}
              <div>
                <label style={{fontSize:11,fontWeight:700,color:NV,display:"block",marginBottom:5,textTransform:"uppercase",letterSpacing:"0.05em"}}>NGO Type *</label>
                <select value={form.type} onChange={set("type")}
                  style={{width:"100%",padding:"9px 12px",border:`1px solid ${form.type?OR+"66":BD}`,borderRadius:7,fontSize:13,background:WH,color:form.type?TX:"#9CA3AF",boxSizing:"border-box"}}>
                  <option value="">Select type…</option>
                  {["Public Trust","Society","Section 8 Company"].map(s=><option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:12}}>
                {inp("PAN Number *","pan","AAAAA0000A")}
                {inp("Year of Incorporation *","year","e.g. 2019")}
              </div>
              <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:12}}>
                {inp("Primary Sector *","sector","Education · Health · Women Empowerment…")}
                {inp("Contact Email *","email","report will be sent here")}
              </div>
            </div>
          </Card>
        </div>
        <div>
          <Card s={{background:"#EEF2F9",border:"1px solid #C7D7F0",marginBottom:12}}>
            <div style={{fontWeight:700,color:NV,marginBottom:10,fontSize:12,textTransform:"uppercase",letterSpacing:"0.05em"}}>Will be checked</div>
            {["Registration & Legal Status","Governance Structure","Membership Requirements","Financial Compliance","Tax Compliance (12A/80G)","FCRA Compliance","Audit Requirements"].map((d,i)=>(
              <div key={d} style={{display:"flex",gap:7,alignItems:"flex-start",marginBottom:7}}>
                <div style={{width:17,height:17,borderRadius:"50%",background:OR,color:WH,fontSize:9,fontWeight:700,display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0,marginTop:1}}>{i+1}</div>
                <span style={{fontSize:12,color:NV,lineHeight:1.4}}>{d}</span>
              </div>
            ))}
          </Card>
          <Card s={{background:"#ECFDF5",border:"1px solid #A7F3D0",marginBottom:12}}>
            <div style={{fontSize:11,color:"#065F46",marginBottom:7,fontWeight:700}}>OCR extracts for you</div>
            {["Registration / certificate numbers","Trustee & member names","Dates of registration","Clause text from Trust Deed","Financial figures & audit details"].map(f=>(
              <div key={f} style={{fontSize:11,color:"#065F46",marginBottom:3}}>· {f}</div>
            ))}
          </Card>
          <div style={{display:"flex",flexDirection:"column",gap:8}}>
            <button onClick={()=>setSubStep(0)} style={{background:WH,color:NV,border:`1px solid ${BD}`,borderRadius:7,padding:"9px",fontSize:12,cursor:"pointer"}}>← Back</button>
            <button onClick={()=>formComplete&&setSubStep(2)} disabled={!formComplete}
              style={{background:formComplete?OR:"#CBD5E1",color:WH,border:"none",borderRadius:7,padding:"10px",fontSize:13,fontWeight:700,
                cursor:formComplete?"pointer":"not-allowed",display:"flex",alignItems:"center",justifyContent:"center",gap:6,
                boxShadow:formComplete?"0 2px 8px rgba(232,96,26,.3)":"none"}}>
              Next: Upload Documents <ChevronRight size={14}/>
            </button>
            {!formComplete&&<div style={{textAlign:"center",fontSize:11,color:MT}}>Fill all fields to continue</div>}
          </div>
        </div>
      </div>}

      {/* ── STEP 2: Upload Documents ── */}
      {subStep===2&&<div style={{display:"grid",gridTemplateColumns:"1fr 280px",gap:18}}>
        <div>
          <div style={{background:"#ECFDF5",border:"1px solid #A7F3D0",borderRadius:7,padding:"8px 14px",marginBottom:14,display:"flex",alignItems:"center",justifyContent:"space-between"}}>
            <div style={{fontSize:12,color:"#065F46",display:"flex",gap:6,alignItems:"center"}}>
              <CheckCircle size={13}/><strong>{stateName}</strong> · {form.name} · {form.type}
            </div>
            <button onClick={()=>setSubStep(1)} style={{fontSize:11,color:OR,background:"none",border:"none",cursor:"pointer",textDecoration:"underline"}}>Edit</button>
          </div>
          <Card>
            <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:14}}>
              <div>
                <h3 style={{margin:"0 0 3px",fontSize:14,fontWeight:700,color:NV}}>Upload Your Documents</h3>
                <p style={{margin:0,color:MT,fontSize:12}}>Upload what you have. We'll check against {stateName} laws + central regulations and flag what's missing.</p>
              </div>
              {!docsLoaded&&<button onClick={()=>setDocsLoaded(true)}
                style={{background:"#FFF3EB",color:OR,border:`1px solid #FDDBC8`,borderRadius:6,padding:"7px 12px",fontSize:12,fontWeight:600,cursor:"pointer",whiteSpace:"nowrap",flexShrink:0,marginLeft:12}}>
                ✦ Auto-fill Sample
              </button>}
            </div>
            {!docsLoaded?(
              <div style={{border:`2px dashed #CBD5E1`,borderRadius:10,padding:"32px 20px",textAlign:"center"}}>
                <Upload size={26} style={{margin:"0 auto 8px",display:"block",color:OR}}/>
                <div style={{fontWeight:600,color:NV,marginBottom:3,fontSize:13}}>Drag & drop documents here</div>
                <div style={{fontSize:11,color:MT}}>PDF, PNG, JPG — max 10 MB per file</div>
                <div style={{marginTop:8,fontSize:11,color:MT}}>Trust Deed · Registration Certificate · 12A / 80G · FCRA · Audited Accounts</div>
                <button style={{marginTop:12,background:WH,color:NV,border:`1px solid ${BD}`,borderRadius:6,padding:"7px 14px",fontSize:12,cursor:"pointer"}}>Browse Files</button>
              </div>
            ):(
              <div>
                <div style={{background:"#ECFDF5",border:"1px solid #A7F3D0",borderRadius:7,padding:"8px 12px",marginBottom:12,fontSize:12,color:"#065F46",display:"flex",gap:6,alignItems:"center"}}>
                  <CheckCircle size={13}/> 7 sample documents loaded · 13.2 MB total
                </div>
                <div style={{display:"grid",gap:7}}>
                  {DOCS.map(d=>(
                    <div key={d.name} style={{display:"flex",alignItems:"center",gap:10,padding:"9px 12px",background:"#FAFAFA",borderRadius:7,border:`1px solid ${BD}`}}>
                      <FileText size={13} style={{color:OR,flexShrink:0}}/>
                      <div style={{flex:1}}>
                        <div style={{fontSize:13,fontWeight:600,color:NV}}>{d.name}</div>
                        <div style={{fontSize:10,color:MT}}>{d.cat} · {d.size} · {d.pages} pages</div>
                      </div>
                      <span style={{background:"#DCFCE7",color:GR,fontSize:10,fontWeight:700,padding:"2px 8px",borderRadius:10}}>✓ Uploaded</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Card>
        </div>
        <div>
          <Card s={{background:"#EEF2F9",border:"1px solid #C7D7F0",marginBottom:12}}>
            <div style={{fontWeight:700,color:NV,marginBottom:8,fontSize:12}}>Checking Against</div>
            <div style={{fontSize:12,fontWeight:600,color:OR,marginBottom:6}}>{stateName} State Laws</div>
            {(STATES.find(s=>s.code===selState)||STATES[0]).acts.map(a=><div key={a} style={{fontSize:11,color:MT,marginBottom:3}}>· {a}</div>)}
            <div style={{borderTop:`1px solid ${BD}`,marginTop:10,paddingTop:10}}>
              <div style={{fontSize:12,fontWeight:600,color:NV,marginBottom:6}}>Central Regulations</div>
              {["FCRA 2010 + Amendment Rules 2020","Income Tax Act — 12A & 80G","NITI Aayog Darpan Guidelines"].map(a=><div key={a} style={{fontSize:11,color:MT,marginBottom:3}}>· {a}</div>)}
            </div>
          </Card>
          <Card s={{background:"#FFFBEB",border:"1px solid #FDE68A",marginBottom:12}}>
            <div style={{fontSize:11,color:"#92400E",marginBottom:3,fontWeight:600}}>Tip</div>
            <div style={{fontSize:12,color:"#78350F",lineHeight:1.5}}>Don't have all documents? Upload what you have. We'll flag exactly what's missing.</div>
          </Card>
          <div style={{display:"flex",flexDirection:"column",gap:8}}>
            <button onClick={()=>setSubStep(1)} style={{background:WH,color:NV,border:`1px solid ${BD}`,borderRadius:7,padding:"9px",fontSize:12,cursor:"pointer"}}>← Back</button>
            <button onClick={()=>docsLoaded&&go("processing")} disabled={!docsLoaded}
              style={{background:docsLoaded?OR:"#CBD5E1",color:WH,border:"none",borderRadius:7,padding:"11px",fontSize:13,fontWeight:700,
                cursor:docsLoaded?"pointer":"not-allowed",display:"flex",alignItems:"center",justifyContent:"center",gap:6,
                boxShadow:docsLoaded?"0 2px 8px rgba(232,96,26,.3)":"none"}}>
              Run Compliance Check <ChevronRight size={14}/>
            </button>
            {!docsLoaded&&<div style={{textAlign:"center",fontSize:11,color:MT}}>Upload documents to proceed</div>}
          </div>
        </div>
      </div>}
    </div>
  </div>;
}

// ══════════════════════════════════════════════════════════════════
// PAGE 3 — PROCESSING
// ══════════════════════════════════════════════════════════════════
function Processing({go}){
  const [step,setStep]=useState(0);
  useEffect(()=>{
    if(step<STEPS.length){const t=setTimeout(()=>setStep(s=>s+1),680);return()=>clearTimeout(t);}
    else{const t=setTimeout(()=>go("dashboard"),700);return()=>clearTimeout(t);}
  },[step]);
  const pct=Math.round((step/STEPS.length)*100);
  return <div style={{background:BG,minHeight:"100vh",display:"flex",alignItems:"center",justifyContent:"center"}}>
    <Card s={{maxWidth:480,width:"100%",margin:"0 24px"}}>
      <div style={{textAlign:"center",marginBottom:22}}>
        <div style={{fontSize:38,marginBottom:8}}>{step>=STEPS.length?"✅":"⚙️"}</div>
        <h2 style={{color:NV,fontWeight:800,margin:"0 0 4px",fontSize:17}}>{step>=STEPS.length?"Analysis Complete":"Analysing Documents…"}</h2>
        <p style={{color:MT,margin:0,fontSize:12}}>{NGO.name} · {NGO.state} · {NGO.type}</p>
      </div>
      <div style={{marginBottom:18}}>
        <div style={{display:"flex",justifyContent:"space-between",fontSize:11,color:MT,marginBottom:4}}><span>Progress</span><span style={{fontWeight:600,color:OR}}>{pct}%</span></div>
        <div style={{background:BD,borderRadius:8,height:7}}><div style={{height:7,borderRadius:8,background:`linear-gradient(90deg,${OR},#F97316)`,width:`${pct}%`,transition:"width 0.5s ease"}}/></div>
      </div>
      <div style={{display:"grid",gap:5}}>
        {STEPS.map((s,i)=>(
          <div key={i} style={{display:"flex",gap:9,alignItems:"center",padding:"7px 10px",borderRadius:7,
            background:i<step?"#ECFDF5":i===step?"#FFF3EB":"transparent",transition:"background 0.3s"}}>
            <div style={{width:18,height:18,borderRadius:"50%",flexShrink:0,display:"flex",alignItems:"center",justifyContent:"center",
              background:i<step?GR:i===step?OR:BD,color:WH,fontSize:9,fontWeight:700}}>
              {i<step?"✓":i===step?"…":i+1}
            </div>
            <span style={{fontSize:12,color:i<step?GR:i===step?OR:MT,fontWeight:i===step?600:400}}>{s}</span>
          </div>
        ))}
      </div>
    </Card>
  </div>;
}

// ══════════════════════════════════════════════════════════════════
// PAGE 4 — DASHBOARD
// ══════════════════════════════════════════════════════════════════
function Dashboard({go}){
  const pass=FINDINGS.filter(f=>f.status==="PASS").length;
  const fail=FINDINGS.filter(f=>f.status==="FAIL").length;
  const unc=FINDINGS.filter(f=>f.status==="UNCERTAIN").length;
  return <div style={{background:BG,minHeight:"100vh"}}>
    <Crumb items={[{label:"Home",page:"landing"},{label:"Compliance Check",page:"submit"},{label:"Dashboard"}]} go={go}/>
    {/* Top action bar */}
    <div style={{background:WH,borderBottom:`1px solid ${BD}`,padding:"8px 20px"}}>
      <div style={{maxWidth:1060,margin:"0 auto",display:"flex",justifyContent:"flex-end",gap:8}}>
        <button onClick={()=>go("findings")} style={{background:"#EEF2F9",color:NV,border:"1px solid #C7D7F0",borderRadius:6,padding:"6px 12px",fontSize:12,fontWeight:500,cursor:"pointer",display:"flex",alignItems:"center",gap:5}}>
          <List size={13}/>Detailed Findings
        </button>
        <button onClick={()=>go("queue")} style={{background:"#FEF3C7",color:AM,border:"1px solid #FDE68A",borderRadius:6,padding:"6px 12px",fontSize:12,fontWeight:600,cursor:"pointer",display:"flex",alignItems:"center",gap:5}}>
          <Eye size={13}/>Human Review Queue
          <span style={{background:AM,color:WH,borderRadius:10,padding:"0 5px",fontSize:10}}>2</span>
        </button>
        <button onClick={()=>go("report")} style={{background:OR,color:WH,border:"none",borderRadius:6,padding:"6px 14px",fontSize:12,fontWeight:600,cursor:"pointer",display:"flex",alignItems:"center",gap:5}}>
          <FileText size={13}/>Full Report
        </button>
      </div>
    </div>

    <div style={{maxWidth:1060,margin:"0 auto",padding:"18px 20px"}}>
      {/* Summary hero card */}
      <Card s={{marginBottom:16,background:"linear-gradient(135deg,#1A3A6B,#0F2451)",border:"none"}}>
        <div style={{display:"flex",alignItems:"center",gap:22}}>
          <Ring score={74}/>
          <div style={{flex:1}}>
            <div style={{color:OR,fontSize:10,fontWeight:700,textTransform:"uppercase",letterSpacing:"0.08em",marginBottom:3}}>Compliance Assessment · {NGO.state} · {NGO.type}</div>
            <h2 style={{color:WH,fontSize:17,fontWeight:800,margin:"0 0 3px"}}>{NGO.name}</h2>
            <div style={{color:"#94A3B8",fontSize:12,marginBottom:12}}>PAN: {NGO.pan} · {NGO.sector}</div>
            <div style={{display:"flex",gap:10,flexWrap:"wrap"}}>
              {[[pass,"PASSED","#4ADE80","rgba(22,163,74,.2)","rgba(22,163,74,.3)"],
                [fail,"FAILED","#FCA5A5","rgba(220,38,38,.2)","rgba(220,38,38,.3)"],
                [unc,"UNCERTAIN","#FCD34D","rgba(217,119,6,.2)","rgba(217,119,6,.3)"]].map(([n,l,c,bg,br])=>(
                <div key={l} style={{background:bg,border:`1px solid ${br}`,borderRadius:7,padding:"8px 16px",textAlign:"center"}}>
                  <div style={{color:c,fontWeight:900,fontSize:20,lineHeight:1}}>{n}</div>
                  <div style={{color:c,fontSize:9,marginTop:2,letterSpacing:"0.05em"}}>{l}</div>
                </div>
              ))}
              <div style={{background:"rgba(255,255,255,.06)",border:"1px solid rgba(255,255,255,.12)",borderRadius:7,padding:"8px 16px",textAlign:"center"}}>
                <div style={{color:"#CBD5E1",fontWeight:900,fontSize:20,lineHeight:1}}>7</div>
                <div style={{color:"#94A3B8",fontSize:9,marginTop:2}}>TOTAL</div>
              </div>
            </div>
          </div>
          <div style={{background:"rgba(251,191,36,.1)",border:"1px solid rgba(251,191,36,.3)",borderRadius:9,padding:"14px 16px",maxWidth:170,flexShrink:0}}>
            <div style={{color:"#FCD34D",fontWeight:700,fontSize:13,marginBottom:4}}>⚠ Not Grant Ready</div>
            <div style={{color:"#FDE68A",fontSize:12,lineHeight:1.5}}>1 critical failure and 1 pending human review must be resolved.</div>
          </div>
        </div>
      </Card>

      {/* NGO info strip */}
      <div style={{background:WH,borderRadius:8,border:`1px solid ${BD}`,padding:"10px 16px",marginBottom:16,display:"flex",gap:24,flexWrap:"wrap"}}>
        {[["Organisation",NGO.name],["State",NGO.state],["Reg. No.",NGO.reg],["Sector",NGO.sector],["Submitted by",NGO.by]].map(([k,v])=>(
          <div key={k}><div style={{fontSize:9,color:MT,textTransform:"uppercase",letterSpacing:"0.05em"}}>{k}</div><div style={{fontSize:12,color:NV,fontWeight:600}}>{v}</div></div>
        ))}
      </div>

      {/* Findings grid */}
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:12}}>
        {FINDINGS.map(f=>{
          const Ic=f.icon,lc=f.status==="PASS"?GR:f.status==="FAIL"?RD:AM;
          return <Card key={f.id} s={{cursor:"pointer",borderLeft:`4px solid ${lc}`,padding:16}} onClick={()=>go("findings")}>
            <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:10}}>
              <div style={{display:"flex",gap:9,alignItems:"center"}}>
                <div style={{width:30,height:30,borderRadius:7,background:f.status==="PASS"?"#DCFCE7":f.status==="FAIL"?"#FEE2E2":"#FEF3C7",display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0}}>
                  <Ic size={14} style={{color:lc}}/>
                </div>
                <div>
                  <div style={{fontSize:13,fontWeight:700,color:NV,lineHeight:1.2}}>{f.dim}</div>
                  <div style={{fontSize:10,color:MT,marginTop:2}}>{f.route==="auto"?"AI Assessed":f.qStatus==="reviewed"?`Reviewed · ${f.determination}`:"Pending Review"}</div>
                </div>
              </div>
              <Badge s={f.status}/>
            </div>
            <Bar v={f.conf}/>
            <div style={{marginTop:9,fontSize:11,color:MT,lineHeight:1.5,display:"-webkit-box",WebkitLineClamp:2,WebkitBoxOrient:"vertical",overflow:"hidden"}}>{f.reasoning}</div>
            {f.status==="FAIL"&&<div style={{marginTop:8,background:"#FEE2E2",border:"1px solid #FCA5A5",borderRadius:5,padding:"6px 9px",fontSize:11,color:RD}}>⚠ Action Required: Fund utilisation statement missing</div>}
            {f.route==="human"&&f.qStatus==="pending"&&<div style={{marginTop:8,background:"#FEF3C7",border:"1px solid #FDE68A",borderRadius:5,padding:"6px 9px",fontSize:11,color:AM}}>⟳ Pending review · {f.officer}</div>}
            {f.route==="human"&&f.qStatus==="reviewed"&&<div style={{marginTop:8,background:"#ECFDF5",border:"1px solid #A7F3D0",borderRadius:5,padding:"6px 9px",fontSize:11,color:GR}}>✓ Reviewed by {f.officer} → {f.determination}</div>}
          </Card>;
        })}
      </div>
    </div>
  </div>;
}

// ══════════════════════════════════════════════════════════════════
// PAGE 5 — DETAILED FINDINGS
// ══════════════════════════════════════════════════════════════════
function Findings({go}){
  const [open,setOpen]=useState(4);
  const [filter,setFilter]=useState("All");
  const shown=filter==="All"?FINDINGS:FINDINGS.filter(f=>f.status===filter);
  return <div style={{background:BG,minHeight:"100vh"}}>
    <Crumb items={[{label:"Home",page:"landing"},{label:"Dashboard",page:"dashboard"},{label:"Detailed Findings"}]} go={go}/>
    <div style={{background:WH,borderBottom:`1px solid ${BD}`,padding:"8px 20px"}}>
      <div style={{maxWidth:960,margin:"0 auto",display:"flex",alignItems:"center",justifyContent:"space-between",flexWrap:"wrap",gap:8}}>
        <div>
          <span style={{fontSize:14,fontWeight:700,color:NV}}>{NGO.name}</span>
          <span style={{fontSize:12,color:MT,marginLeft:8}}>· {NGO.state} · {NGO.type} · 7 dimensions</span>
        </div>
        <div style={{display:"flex",gap:5}}>
          {["All","PASS","FAIL","UNCERTAIN"].map(f=>(
            <button key={f} onClick={()=>setFilter(f)}
              style={{background:filter===f?OR:WH,color:filter===f?WH:MT,border:`1px solid ${BD}`,borderRadius:16,padding:"4px 12px",fontSize:11,cursor:"pointer",fontWeight:filter===f?600:400}}>
              {f}
            </button>
          ))}
        </div>
      </div>
    </div>
    <div style={{maxWidth:960,margin:"0 auto",padding:"18px 20px"}}>
      <div style={{display:"grid",gap:10}}>
        {shown.map(f=>{
          const lc=f.status==="PASS"?GR:f.status==="FAIL"?RD:AM;
          const isOpen=open===f.id;
          return <Card key={f.id} s={{padding:0,overflow:"hidden",borderLeft:`4px solid ${lc}`}}>
            <div style={{display:"flex",alignItems:"center",gap:12,padding:"13px 16px",cursor:"pointer"}} onClick={()=>setOpen(isOpen?null:f.id)}>
              <Badge s={f.status}/>
              <div style={{flex:1}}>
                <div style={{fontWeight:700,color:NV,fontSize:13}}>{f.dim}</div>
                <div style={{fontSize:10,color:MT,marginTop:1}}>
                  {f.route==="auto"?"AI Assessed (automated)":f.qStatus==="reviewed"?`Human Reviewed → ${f.determination} · ${f.officer}`:`Pending Human Review · ${f.officer}`}
                </div>
              </div>
              <div style={{textAlign:"right",minWidth:100}}>
                <div style={{fontSize:10,color:MT,marginBottom:3}}>AI Confidence</div>
                <Bar v={f.conf}/>
              </div>
              <div style={{color:MT,flexShrink:0}}>{isOpen?<ChevronUp size={15}/>:<ChevronDown size={15}/>}</div>
            </div>
            {isOpen&&<div style={{borderTop:`1px solid ${BD}`,padding:"14px 16px"}}>
              <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:10,marginBottom:10}}>
                <div style={{background:"#F8FAFC",borderRadius:7,padding:12,gridColumn:"1/-1"}}>
                  <div style={{fontSize:10,fontWeight:700,color:NV,textTransform:"uppercase",letterSpacing:"0.05em",marginBottom:5}}>Legal Citation</div>
                  <div style={{fontSize:12,color:TX,lineHeight:1.65}}>{f.citation}</div>
                </div>
                <div style={{background:"#EEF2F9",borderRadius:7,padding:12}}>
                  <div style={{fontSize:10,fontWeight:700,color:NV,textTransform:"uppercase",letterSpacing:"0.05em",marginBottom:5}}>NGO Document Evidence</div>
                  <div style={{fontSize:12,color:TX,lineHeight:1.65}}>{f.evidence}</div>
                </div>
                <div style={{background:"#F0F9FF",borderRadius:7,padding:12}}>
                  <div style={{fontSize:10,fontWeight:700,color:"#0369A1",textTransform:"uppercase",letterSpacing:"0.05em",marginBottom:5}}>AI Reasoning</div>
                  <div style={{fontSize:12,color:TX,lineHeight:1.65}}>{f.reasoning}</div>
                </div>
              </div>
              {f.qStatus==="reviewed"&&<div style={{background:"#ECFDF5",border:"1px solid #A7F3D0",borderRadius:7,padding:12,marginBottom:8}}>
                <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:5}}>
                  <div style={{fontSize:10,fontWeight:700,color:GR,textTransform:"uppercase"}}>Officer Determination: {f.determination}</div>
                  <span style={{fontSize:10,color:MT}}>{f.reviewedAt}</span>
                </div>
                <div style={{fontSize:12,color:TX,lineHeight:1.6}}>{f.officerNotes}</div>
                <div style={{fontSize:10,color:MT,marginTop:4}}>Reviewed by {f.officer} · {f.role}</div>
              </div>}
              {f.status==="FAIL"&&<div style={{background:"#FEE2E2",border:"1px solid #FCA5A5",borderRadius:7,padding:12}}>
                <div style={{fontSize:10,fontWeight:700,color:RD,textTransform:"uppercase",marginBottom:5}}>How to Resolve</div>
                <div style={{fontSize:12,color:RD,lineHeight:1.6}}>{f.fix}</div>
              </div>}
              {f.route==="human"&&f.qStatus==="pending"&&<div style={{background:"#FEF3C7",border:"1px solid #FDE68A",borderRadius:7,padding:12}}>
                <div style={{fontSize:10,fontWeight:700,color:AM,textTransform:"uppercase",marginBottom:5}}>Pending Officer Review</div>
                <div style={{fontSize:12,color:AM}}>Assigned to {f.officer} ({f.role}). Awaiting determination.</div>
              </div>}
            </div>}
          </Card>;
        })}
      </div>
      <div style={{marginTop:16,textAlign:"center"}}>
        <button onClick={()=>go("queue")} style={{background:WH,color:NV,border:`1px solid ${BD}`,borderRadius:7,padding:"9px 18px",fontSize:13,cursor:"pointer",marginRight:8}}>View Review Queue</button>
        <button onClick={()=>go("report")} style={{background:OR,color:WH,border:"none",borderRadius:7,padding:"9px 18px",fontSize:13,fontWeight:600,cursor:"pointer"}}>Generate Full Report →</button>
      </div>
    </div>
  </div>;
}

// ══════════════════════════════════════════════════════════════════
// PAGE 6 — HUMAN REVIEW QUEUE
// ══════════════════════════════════════════════════════════════════
function Queue({go}){
  const [det,setDet]=useState(null);
  const items=FINDINGS.filter(f=>f.route==="human");
  return <div style={{background:BG,minHeight:"100vh"}}>
    <Crumb items={[{label:"Home",page:"landing"},{label:"Dashboard",page:"dashboard"},{label:"Human Review Queue"}]} go={go}/>
    <div style={{maxWidth:900,margin:"0 auto",padding:"18px 20px"}}>
      <div style={{display:"flex",alignItems:"center",justifyContent:"space-between",marginBottom:14}}>
        <div>
          <h2 style={{margin:0,fontSize:16,fontWeight:800,color:NV}}>Human Review Queue</h2>
          <p style={{margin:"3px 0 0",fontSize:12,color:MT}}>UNCERTAIN findings are routed here for officer review</p>
        </div>
        <div style={{display:"flex",gap:6}}>
          <span style={{background:"#FEE2E2",color:RD,padding:"4px 12px",borderRadius:20,fontSize:11,fontWeight:700}}>1 PENDING</span>
          <span style={{background:"#DCFCE7",color:GR,padding:"4px 12px",borderRadius:20,fontSize:11,fontWeight:700}}>1 REVIEWED</span>
        </div>
      </div>

      <div style={{background:"#EEF2F9",border:"1px solid #C7D7F0",borderRadius:9,padding:"12px 14px",marginBottom:16,display:"flex",gap:10}}>
        <span style={{fontSize:18,flexShrink:0}}>ℹ</span>
        <div style={{fontSize:12,color:NV,lineHeight:1.65}}>
          <strong>Blinded Review Protocol:</strong> Officers review the legal provisions and NGO evidence before seeing the AI recommendation. This prevents anchoring bias. Their determination is final and logged with full audit trail.
        </div>
      </div>

      <div style={{display:"grid",gap:14}}>
        {items.map(f=>(
          <Card key={f.id} s={{borderLeft:`4px solid ${f.qStatus==="reviewed"?GR:AM}`}}>
            <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:14}}>
              <div>
                <div style={{fontWeight:800,color:NV,fontSize:14}}>{f.dim}</div>
                <div style={{fontSize:11,color:MT,marginTop:2}}>{NGO.name}</div>
              </div>
              <div style={{display:"flex",gap:7,alignItems:"center"}}>
                <Badge s={f.status}/>
                <span style={{background:f.qStatus==="reviewed"?"#DCFCE7":"#FEF3C7",color:f.qStatus==="reviewed"?GR:AM,padding:"3px 10px",borderRadius:12,fontSize:10,fontWeight:700}}>
                  {f.qStatus==="reviewed"?"✓ REVIEWED":"⟳ PENDING"}
                </span>
              </div>
            </div>

            <div style={{display:"grid",gridTemplateColumns:"1fr 1fr 1fr",gap:10,marginBottom:12}}>
              <div style={{background:"#F8FAFC",borderRadius:7,padding:11}}>
                <div style={{fontSize:10,fontWeight:700,color:NV,textTransform:"uppercase",marginBottom:4}}>Why Routed</div>
                <div style={{fontSize:12,color:TX,lineHeight:1.5}}>AI confidence <strong>{Math.round(f.conf*100)}%</strong> — below 75% threshold. {f.id===3?"OCR incomplete on page 4.":"Separate FCRA audit not clearly identified."}</div>
              </div>
              <div style={{background:"#F8FAFC",borderRadius:7,padding:11}}>
                <div style={{fontSize:10,fontWeight:700,color:NV,textTransform:"uppercase",marginBottom:4}}>Legal Citation</div>
                <div style={{fontSize:12,color:TX,lineHeight:1.5}}>{f.citation}</div>
              </div>
              <div style={{background:"#F8FAFC",borderRadius:7,padding:11}}>
                <div style={{fontSize:10,fontWeight:700,color:NV,textTransform:"uppercase",marginBottom:4}}>Assigned Officer</div>
                <div style={{display:"flex",gap:7,alignItems:"center",marginTop:2}}>
                  <div style={{width:26,height:26,borderRadius:"50%",background:"#EEF2F9",display:"flex",alignItems:"center",justifyContent:"center",color:NV,fontWeight:700,fontSize:11}}>{f.officer[8]}</div>
                  <div><div style={{fontSize:12,fontWeight:600,color:NV}}>{f.officer}</div><div style={{fontSize:10,color:MT}}>{f.role}</div></div>
                </div>
              </div>
            </div>

            {/* Evidence section */}
            <div style={{background:"#F0F9FF",borderRadius:7,padding:11,marginBottom:10}}>
              <div style={{fontSize:10,fontWeight:700,color:"#0369A1",textTransform:"uppercase",marginBottom:4}}>NGO Document Evidence (shown to officer first)</div>
              <div style={{fontSize:12,color:TX,lineHeight:1.6}}>{f.evidence}</div>
            </div>

            {f.qStatus==="reviewed"?(
              <div style={{background:"#ECFDF5",border:"1px solid #A7F3D0",borderRadius:7,padding:12}}>
                <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:6}}>
                  <div style={{fontSize:11,fontWeight:700,color:GR}}>OFFICER DETERMINATION: {f.determination}</div>
                  <span style={{fontSize:10,color:MT}}>{f.reviewedAt}</span>
                </div>
                <div style={{fontSize:12,color:TX,lineHeight:1.6}}>{f.officerNotes}</div>
                <div style={{fontSize:10,color:MT,marginTop:5}}>Reviewed by {f.officer} · {f.role} · Audit trail logged</div>
              </div>
            ):(
              <div style={{background:"#FEF3C7",border:"1px solid #FDE68A",borderRadius:7,padding:12}}>
                <div style={{fontSize:10,fontWeight:700,color:AM,textTransform:"uppercase",marginBottom:8}}>Awaiting Officer Review</div>
                <div style={{fontSize:11,color:"#78350F",marginBottom:10}}>Review the legal citation and NGO evidence above, then mark your determination:</div>
                <div style={{display:"flex",gap:7}}>
                  <button style={{background:GR,color:WH,border:"none",borderRadius:6,padding:"8px 16px",fontSize:12,fontWeight:600,cursor:"pointer",display:"flex",alignItems:"center",gap:5}}><CheckCircle size={13}/>Mark PASS</button>
                  <button style={{background:RD,color:WH,border:"none",borderRadius:6,padding:"8px 16px",fontSize:12,fontWeight:600,cursor:"pointer",display:"flex",alignItems:"center",gap:5}}><XCircle size={13}/>Mark FAIL</button>
                  <button style={{background:WH,color:NV,border:`1px solid ${BD}`,borderRadius:6,padding:"8px 14px",fontSize:12,cursor:"pointer"}}>Escalate</button>
                  <button style={{background:WH,color:NV,border:`1px solid ${BD}`,borderRadius:6,padding:"8px 14px",fontSize:12,cursor:"pointer"}}>Request More Docs</button>
                </div>
                <div style={{fontSize:10,color:AM,marginTop:8}}>* AI recommendation is hidden during review to prevent anchoring bias.</div>
              </div>
            )}
          </Card>
        ))}
      </div>

      <div style={{marginTop:16,textAlign:"center"}}>
        <button onClick={()=>go("report")} style={{background:OR,color:WH,border:"none",borderRadius:7,padding:"10px 22px",fontSize:13,fontWeight:600,cursor:"pointer"}}>Generate Final Report →</button>
      </div>
    </div>
  </div>;
}

// ══════════════════════════════════════════════════════════════════
// PAGE 7 — FINAL REPORT
// ══════════════════════════════════════════════════════════════════
function Report({go}){
  const auto=FINDINGS.filter(f=>f.route==="auto");
  const human=FINDINGS.filter(f=>f.route==="human");
  const statusRow=[["Registration & Legal Status","PASS",GR],["Governance Structure","PASS",GR],["Membership Requirements","UNCERTAIN",AM],["Financial Compliance","FAIL",RD],["Tax Compliance","PASS",GR],["FCRA Compliance","PASS",GR],["Audit Requirements","PASS (Officer)",GR]];
  return <div style={{background:BG,minHeight:"100vh"}}>
    <Crumb items={[{label:"Home",page:"landing"},{label:"Dashboard",page:"dashboard"},{label:"Final Report"}]} go={go}/>
    <div style={{background:WH,borderBottom:`1px solid ${BD}`,padding:"8px 20px"}}>
      <div style={{maxWidth:940,margin:"0 auto",display:"flex",justifyContent:"flex-end",gap:7}}>
        <button style={{background:WH,color:NV,border:`1px solid ${BD}`,borderRadius:6,padding:"6px 12px",fontSize:12,cursor:"pointer"}}>🖨 Print</button>
        <button style={{background:OR,color:WH,border:"none",borderRadius:6,padding:"6px 14px",fontSize:12,fontWeight:600,cursor:"pointer",display:"flex",alignItems:"center",gap:5}}><Download size={13}/>Download PDF</button>
      </div>
    </div>
    <div style={{maxWidth:940,margin:"0 auto",padding:"18px 20px"}}>
      {/* Report header */}
      <Card s={{marginBottom:14,background:"linear-gradient(135deg,#1A3A6B,#0F2451)",border:"none"}}>
        <div style={{display:"flex",gap:20,alignItems:"center"}}>
          <Ring score={74}/>
          <div style={{flex:1}}>
            <div style={{color:OR,fontSize:9,fontWeight:700,textTransform:"uppercase",letterSpacing:"0.1em",marginBottom:4}}>NITI AAYOG · NGO DARPAN COMPLIANCE VERIFICATION SYSTEM · CONFIDENTIAL</div>
            <h2 style={{color:WH,fontSize:17,fontWeight:800,margin:"0 0 2px"}}>{NGO.name}</h2>
            <div style={{color:"#94A3B8",fontSize:12,marginBottom:10}}>Reg: {NGO.reg} · PAN: {NGO.pan}</div>
            <div style={{display:"flex",gap:16,flexWrap:"wrap"}}>
              {[["State",NGO.state],["Type",NGO.type],["Sector",NGO.sector],["Assessment Date","24 Jun 2026"],["Submitted By",NGO.by]].map(([k,v])=>(
                <div key={k}><div style={{color:"#64748B",fontSize:9,textTransform:"uppercase"}}>{k}</div><div style={{color:"#CBD5E1",fontSize:11,fontWeight:500}}>{v}</div></div>
              ))}
            </div>
          </div>
          <div style={{background:"rgba(251,191,36,.12)",border:"1px solid rgba(251,191,36,.3)",borderRadius:9,padding:"12px 14px",flexShrink:0,textAlign:"center"}}>
            <div style={{color:"#FCD34D",fontWeight:700,fontSize:13}}>⚠ Not Grant Ready</div>
            <div style={{color:"#FDE68A",fontSize:11,marginTop:4,lineHeight:1.5}}>Resolve 1 critical<br/>failure + 1 pending</div>
          </div>
        </div>
      </Card>

      <div style={{display:"grid",gridTemplateColumns:"1fr 280px",gap:14,marginBottom:14}}>
        {/* Status summary */}
        <Card>
          <div style={{fontSize:12,fontWeight:700,color:NV,marginBottom:12,textTransform:"uppercase",letterSpacing:"0.05em"}}>Compliance Status Overview</div>
          {statusRow.map(([d,s,c])=>(
            <div key={d} style={{display:"flex",justifyContent:"space-between",alignItems:"center",padding:"7px 0",borderBottom:`1px solid ${BD}`}}>
              <span style={{fontSize:13,color:TX}}>{d}</span>
              <span style={{fontSize:11,fontWeight:700,color:c}}>{s}</span>
            </div>
          ))}
        </Card>
        {/* Actions */}
        <div style={{display:"grid",gap:10,alignContent:"start"}}>
          <div style={{background:"#FEE2E2",border:"1px solid #FCA5A5",borderRadius:8,padding:12}}>
            <div style={{fontWeight:700,color:RD,fontSize:12,marginBottom:4}}>Critical — Action Required</div>
            <div style={{fontSize:11,color:RD,lineHeight:1.55}}>Submit fund utilisation statement for FY 2023–24 CSR grant (₹18.5L, TCS Foundation) with Charity Commissioner, Maharashtra.</div>
          </div>
          <div style={{background:"#FEF3C7",border:"1px solid #FDE68A",borderRadius:8,padding:12}}>
            <div style={{fontWeight:700,color:AM,fontSize:12,marginBottom:4}}>Pending Review</div>
            <div style={{fontSize:11,color:AM,lineHeight:1.55}}>Membership Requirements — awaiting Officer Ramesh K. re: Circular 12/2021.</div>
          </div>
          <div style={{background:"#ECFDF5",border:"1px solid #A7F3D0",borderRadius:8,padding:12}}>
            <div style={{fontWeight:600,color:GR,fontSize:11}}>✓ Registration, Tax, FCRA, Governance and Audit requirements satisfied.</div>
          </div>
        </div>
      </div>

      {/* AI Assessed */}
      <div style={{marginBottom:14}}>
        <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:10}}>
          <span style={{background:"#EEF2FF",color:"#4F46E5",padding:"4px 12px",borderRadius:6,fontSize:11,fontWeight:700}}>AI ASSESSED</span>
          <span style={{fontSize:12,color:MT}}>{auto.length} findings · automated · high confidence</span>
        </div>
        <div style={{display:"grid",gap:7}}>
          {auto.map(f=>{
            const lc=f.status==="PASS"?GR:RD;
            return <div key={f.id} style={{background:WH,borderRadius:8,border:`1px solid ${BD}`,borderLeft:`4px solid ${lc}`,padding:"12px 16px",display:"flex",gap:12,alignItems:"flex-start"}}>
              <Badge s={f.status}/>
              <div style={{flex:1}}>
                <div style={{fontWeight:700,color:NV,fontSize:13,marginBottom:3}}>{f.dim}</div>
                <div style={{fontSize:11,color:MT,marginBottom:5}}>Confidence: {Math.round(f.conf*100)}% · {f.citation}</div>
                <div style={{fontSize:12,color:TX,lineHeight:1.55}}>{f.reasoning}</div>
                {f.status==="FAIL"&&<div style={{marginTop:7,background:"#FEE2E2",borderRadius:5,padding:"6px 10px",fontSize:11,color:RD}}>⚠ Action Required: {f.fix}</div>}
              </div>
              <div style={{textAlign:"right",minWidth:90,flexShrink:0}}>
                <div style={{fontSize:10,color:MT,marginBottom:3}}>Confidence</div>
                <Bar v={f.conf}/>
              </div>
            </div>;
          })}
        </div>
      </div>

      {/* Human reviewed */}
      <div style={{marginBottom:16}}>
        <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:10}}>
          <span style={{background:"#ECFDF5",color:GR,padding:"4px 12px",borderRadius:6,fontSize:11,fontWeight:700}}>OFFICER REVIEWED</span>
          <span style={{fontSize:12,color:MT}}>{human.length} findings · reviewed by designated compliance officers</span>
        </div>
        <div style={{display:"grid",gap:7}}>
          {human.map(f=>(
            <div key={f.id} style={{background:WH,borderRadius:8,border:`1px solid ${BD}`,borderLeft:`4px solid ${f.qStatus==="reviewed"?GR:AM}`,padding:"12px 16px"}}>
              <div style={{display:"flex",gap:12,alignItems:"flex-start"}}>
                <Badge s={f.qStatus==="reviewed"?(f.determination||"PASS"):f.status}/>
                <div style={{flex:1}}>
                  <div style={{fontWeight:700,color:NV,fontSize:13,marginBottom:2}}>{f.dim}</div>
                  <div style={{fontSize:11,color:MT,marginBottom:6}}>{f.qStatus==="reviewed"?`Reviewed by ${f.officer} (${f.role}) · ${f.reviewedAt}`:`Pending review · ${f.officer} (${f.role})`}</div>
                  {f.qStatus==="reviewed"?(
                    <div style={{background:"#ECFDF5",borderRadius:6,padding:"7px 10px",fontSize:12,color:TX}}>{f.officerNotes}</div>
                  ):(
                    <div style={{background:"#FEF3C7",borderRadius:6,padding:"7px 10px",fontSize:12,color:AM}}>⟳ Awaiting officer determination. Report is provisional for this dimension.</div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Disclaimer */}
      <div style={{background:"#F8FAFC",border:`1px solid ${BD}`,borderRadius:8,padding:"12px 14px",fontSize:11,color:MT,lineHeight:1.7}}>
        <strong style={{color:NV}}>Disclaimer:</strong> This report is generated by an AI-assisted compliance screening system (NGO Darpan Compliance Verification Pilot) and constitutes a decision-support tool, not a legal ruling. All AI findings are subject to review by designated compliance officers. NITI Aayog / NIC does not assume responsibility for automated compliance determinations. Organisations must consult the relevant Registrar or regulatory body for final compliance decisions.
      </div>
    </div>
  </div>;
}

// ══════════════════════════════════════════════════════════════════
// NPO DIRECTORY PAGE
// ══════════════════════════════════════════════════════════════════
const DIR_DATA=[
  {name:"Asha Jyoti Welfare Foundation",state:"Maharashtra",type:"Public Trust",sector:"Education & Women Empowerment",reg:"E-23847/2019",score:74,cStatus:"partial",vStatus:"Partially Verified"},
  {name:"Delhi Shiksha Samiti",state:"Delhi",type:"Society",sector:"Education",reg:"S-11234/2018",score:null,cStatus:"unverified",vStatus:"Unverified"},
  {name:"Karnataka Arogya Trust",state:"Karnataka",type:"Public Trust",sector:"Health",reg:"KA-T-8821/2020",score:91,cStatus:"verified",vStatus:"Verified"},
  {name:"Rajasthan Gramin Vikas Sangh",state:"Rajasthan",type:"Society",sector:"Rural Development",reg:"RJ-S-4412/2017",score:null,cStatus:"unverified",vStatus:"Unverified"},
  {name:"Mumbai Women Empowerment Trust",state:"Maharashtra",type:"Public Trust",sector:"Women Empowerment",reg:"E-19023/2021",score:88,cStatus:"verified",vStatus:"Verified"},
  {name:"Bengaluru Youth Foundation",state:"Karnataka",type:"Section 8 Company",sector:"Youth & Sports",reg:"CIN-U85300KA2019",score:62,cStatus:"partial",vStatus:"Partially Verified"},
  {name:"Delhi Environmental Society",state:"Delhi",type:"Society",sector:"Environment",reg:"S-9934/2016",score:null,cStatus:"unverified",vStatus:"Unverified"},
  {name:"Jaipur Bal Vikas Sanstha",state:"Rajasthan",type:"Society",sector:"Child Welfare",reg:"RJ-S-7721/2019",score:79,cStatus:"partial",vStatus:"Partially Verified"},
];

function Directory({go}){
  const [query,setQuery]=useState("");
  const [filterState,setFilterState]=useState("All");
  const [filterV,setFilterV]=useState("All");
  const [selected,setSelected]=useState(null);

  const filtered=DIR_DATA.filter(n=>{
    const q=query.toLowerCase();
    const matchQ=!q||n.name.toLowerCase().includes(q)||n.sector.toLowerCase().includes(q)||n.reg.toLowerCase().includes(q);
    const matchS=filterState==="All"||n.state===filterState;
    const matchV=filterV==="All"||(filterV==="Verified"&&n.cStatus==="verified")||(filterV==="Partial"&&n.cStatus==="partial")||(filterV==="Unverified"&&n.cStatus==="unverified");
    return matchQ&&matchS&&matchV;
  });

  const vCol={verified:{bg:"#DCFCE7",c:GR,t:"Verified"},partial:{bg:"#FEF3C7",c:AM,t:"Partially Verified"},unverified:{bg:"#F1F5F9",c:MT,t:"Unverified"}};

  // Profile modal
  if(selected){
    const n=selected;
    const vc=vCol[n.cStatus];
    return <div style={{background:BG,minHeight:"100vh"}}>
      <Crumb items={[{label:"Home",page:"landing"},{label:"NPO Directory",page:"directory"},{label:n.name}]} go={go}/>
      <div style={{maxWidth:860,margin:"0 auto",padding:"24px 20px"}}>
        <Card s={{marginBottom:16}}>
          <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",flexWrap:"wrap",gap:12}}>
            <div>
              <div style={{display:"flex",gap:8,alignItems:"center",marginBottom:6}}>
                <h2 style={{margin:0,fontSize:18,fontWeight:800,color:NV}}>{n.name}</h2>
                <span style={{background:vc.bg,color:vc.c,fontSize:11,fontWeight:700,padding:"3px 10px",borderRadius:12}}>{vc.t}</span>
              </div>
              <div style={{display:"flex",gap:16,flexWrap:"wrap"}}>
                {[["State",n.state],["Type",n.type],["Sector",n.sector],["Reg. No.",n.reg]].map(([k,v])=>(
                  <div key={k}><div style={{fontSize:9,color:MT,textTransform:"uppercase"}}>{k}</div><div style={{fontSize:12,color:NV,fontWeight:600}}>{v}</div></div>
                ))}
              </div>
            </div>
            {n.score?(
              <div style={{textAlign:"center"}}>
                <Ring score={n.score}/>
                <div style={{fontSize:11,color:MT,marginTop:4}}>Compliance Score</div>
              </div>
            ):(
              <div style={{background:"#F1F5F9",border:`1px solid ${BD}`,borderRadius:10,padding:"16px 20px",textAlign:"center"}}>
                <div style={{fontSize:13,fontWeight:700,color:MT,marginBottom:4}}>Not Checked</div>
                <div style={{fontSize:11,color:MT}}>No compliance report</div>
              </div>
            )}
          </div>
        </Card>

        {n.cStatus==="unverified"?(
          <Card s={{border:`2px dashed ${BD}`,background:"#FAFAFA",textAlign:"center",padding:"36px 24px"}}>
            <div style={{width:48,height:48,borderRadius:"50%",background:"#F1F5F9",display:"flex",alignItems:"center",justifyContent:"center",margin:"0 auto 14px"}}>
              <Shield size={20} style={{color:MT}}/>
            </div>
            <h3 style={{color:NV,fontWeight:700,fontSize:15,margin:"0 0 6px"}}>No Compliance Report Yet</h3>
            <p style={{color:MT,fontSize:13,margin:"0 0 20px",maxWidth:380,marginLeft:"auto",marginRight:"auto"}}>This NGO has not completed a compliance verification. Documents have not been checked against {n.state} state laws or central regulations.</p>
            <button onClick={()=>go("submit")} style={{background:OR,color:WH,border:"none",borderRadius:8,padding:"11px 22px",fontSize:13,fontWeight:700,cursor:"pointer",display:"inline-flex",alignItems:"center",gap:6,boxShadow:"0 2px 8px rgba(232,96,26,.25)"}}>
              Run Compliance Check <ChevronRight size={14}/>
            </button>
          </Card>
        ):(
          <div>
            <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:10,marginBottom:14}}>
              {[["Passed",FINDINGS.filter(f=>f.status==="PASS").length,GR,"#DCFCE7"],["Failed",FINDINGS.filter(f=>f.status==="FAIL").length,RD,"#FEE2E2"],["Uncertain",FINDINGS.filter(f=>f.status==="UNCERTAIN").length,AM,"#FEF3C7"],["Total","7",NV,"#EEF2F9"]].map(([l,v,c,bg])=>(
                <div key={l} style={{background:bg,borderRadius:8,padding:"12px 14px",textAlign:"center"}}>
                  <div style={{fontSize:20,fontWeight:900,color:c}}>{v}</div>
                  <div style={{fontSize:10,color:c,marginTop:2,textTransform:"uppercase",letterSpacing:"0.04em"}}>{l}</div>
                </div>
              ))}
            </div>
            <div style={{display:"grid",gap:7}}>
              {FINDINGS.map(f=>{
                const lc=f.status==="PASS"?GR:f.status==="FAIL"?RD:AM;
                return <div key={f.id} style={{background:WH,borderRadius:8,border:`1px solid ${BD}`,borderLeft:`3px solid ${lc}`,padding:"10px 14px",display:"flex",alignItems:"center",gap:12}}>
                  <Badge s={f.status}/>
                  <div style={{flex:1,fontSize:13,fontWeight:500,color:NV}}>{f.dim}</div>
                  <div style={{fontSize:11,color:MT}}>{Math.round(f.conf*100)}% confidence</div>
                </div>;
              })}
            </div>
            <div style={{marginTop:14,display:"flex",gap:8}}>
              <button onClick={()=>go("dashboard")} style={{background:OR,color:WH,border:"none",borderRadius:7,padding:"9px 18px",fontSize:13,fontWeight:600,cursor:"pointer"}}>View Full Report</button>
              <button onClick={()=>go("submit")} style={{background:WH,color:NV,border:`1px solid ${BD}`,borderRadius:7,padding:"9px 16px",fontSize:13,cursor:"pointer"}}>Re-run Check</button>
            </div>
          </div>
        )}
      </div>
    </div>;
  }

  // Directory listing
  return <div style={{background:BG,minHeight:"100vh"}}>
    <Crumb items={[{label:"Home",page:"landing"},{label:"NPO Directory"}]} go={go}/>
    <div style={{background:WH,borderBottom:`1px solid ${BD}`,padding:"20px"}}>
      <div style={{maxWidth:900,margin:"0 auto"}}>
        <div style={{marginBottom:14}}>
          <h2 style={{margin:"0 0 4px",fontSize:18,fontWeight:800,color:NV}}>NPO Directory</h2>
          <p style={{margin:0,fontSize:13,color:MT}}>Search registered NGOs and view their compliance verification status.</p>
        </div>
        {/* Search bar */}
        <div style={{position:"relative",marginBottom:12}}>
          <Search size={15} style={{position:"absolute",left:12,top:"50%",transform:"translateY(-50%)",color:MT}}/>
          <input value={query} onChange={e=>setQuery(e.target.value)}
            placeholder="Search by name, sector, or registration number…"
            style={{width:"100%",padding:"10px 12px 10px 36px",border:`1px solid ${BD}`,borderRadius:8,fontSize:13,color:TX,background:WH,boxSizing:"border-box",outline:"none"}}/>
        </div>
        {/* Filters */}
        <div style={{display:"flex",gap:8,flexWrap:"wrap",alignItems:"center"}}>
          <span style={{fontSize:12,color:MT}}>State:</span>
          {["All","Maharashtra","Delhi","Karnataka","Rajasthan"].map(s=>(
            <button key={s} onClick={()=>setFilterState(s)}
              style={{background:filterState===s?NV:WH,color:filterState===s?WH:MT,border:`1px solid ${BD}`,borderRadius:16,padding:"3px 12px",fontSize:11,cursor:"pointer",fontWeight:filterState===s?600:400}}>
              {s}
            </button>
          ))}
          <span style={{fontSize:12,color:MT,marginLeft:8}}>Status:</span>
          {["All","Verified","Partial","Unverified"].map(v=>(
            <button key={v} onClick={()=>setFilterV(v)}
              style={{background:filterV===v?NV:WH,color:filterV===v?WH:MT,border:`1px solid ${BD}`,borderRadius:16,padding:"3px 12px",fontSize:11,cursor:"pointer",fontWeight:filterV===v?600:400}}>
              {v}
            </button>
          ))}
        </div>
      </div>
    </div>

    <div style={{maxWidth:900,margin:"0 auto",padding:"16px 20px"}}>
      <div style={{fontSize:12,color:MT,marginBottom:12}}>{filtered.length} NGO{filtered.length!==1?"s":""} found</div>
      <div style={{display:"grid",gap:10}}>
        {filtered.map((n,i)=>{
          const vc=vCol[n.cStatus];
          return <div key={i} onClick={()=>setSelected(n)}
            style={{background:WH,borderRadius:10,border:`1px solid ${BD}`,padding:"14px 18px",cursor:"pointer",display:"flex",alignItems:"center",gap:14,
              transition:"box-shadow 0.15s"}}
            onMouseEnter={e=>e.currentTarget.style.boxShadow="0 2px 12px rgba(0,0,0,.08)"}
            onMouseLeave={e=>e.currentTarget.style.boxShadow="none"}>
            {/* Avatar */}
            <div style={{width:40,height:40,borderRadius:10,background:"#EEF2F9",display:"flex",alignItems:"center",justifyContent:"center",fontWeight:800,fontSize:14,color:NV,flexShrink:0}}>
              {n.name[0]}
            </div>
            <div style={{flex:1,minWidth:0}}>
              <div style={{fontWeight:700,color:NV,fontSize:14,marginBottom:2}}>{n.name}</div>
              <div style={{fontSize:11,color:MT}}>{n.state} · {n.type} · {n.sector} · Reg: {n.reg}</div>
            </div>
            {/* Score or dash */}
            <div style={{textAlign:"center",minWidth:52,flexShrink:0}}>
              {n.score?(
                <div>
                  <div style={{fontSize:18,fontWeight:900,color:n.score>=80?GR:n.score>=60?AM:RD}}>{n.score}</div>
                  <div style={{fontSize:9,color:MT,textTransform:"uppercase"}}>Score</div>
                </div>
              ):<div style={{fontSize:12,color:MT}}>—</div>}
            </div>
            {/* Status badge */}
            <span style={{background:vc.bg,color:vc.c,fontSize:11,fontWeight:700,padding:"4px 12px",borderRadius:12,flexShrink:0}}>{vc.t}</span>
            {/* CTA */}
            {n.cStatus==="unverified"?(
              <button onClick={e=>{e.stopPropagation();go("submit");}}
                style={{background:OR,color:WH,border:"none",borderRadius:6,padding:"7px 12px",fontSize:11,fontWeight:700,cursor:"pointer",flexShrink:0,whiteSpace:"nowrap"}}>
                Run Check
              </button>
            ):(
              <ChevronRight size={16} style={{color:MT,flexShrink:0}}/>
            )}
          </div>;
        })}
        {filtered.length===0&&(
          <div style={{textAlign:"center",padding:"40px 20px",color:MT}}>
            <Search size={28} style={{display:"block",margin:"0 auto 10px",opacity:0.4}}/>
            <div style={{fontWeight:600,color:NV,marginBottom:4}}>No NGOs found</div>
            <div style={{fontSize:12}}>Try a different search term or filter</div>
          </div>
        )}
      </div>

      {/* Legend */}
      <div style={{marginTop:20,background:WH,borderRadius:9,border:`1px solid ${BD}`,padding:"12px 16px",display:"flex",gap:20,flexWrap:"wrap",alignItems:"center"}}>
        <span style={{fontSize:11,fontWeight:700,color:NV}}>Status key:</span>
        {[["Verified",GR,"#DCFCE7","Compliance check passed"],["Partially Verified",AM,"#FEF3C7","Check run, some issues found"],["Unverified",MT,"#F1F5F9","No compliance check run yet"]].map(([l,c,bg,d])=>(
          <div key={l} style={{display:"flex",gap:6,alignItems:"center"}}>
            <span style={{background:bg,color:c,fontSize:10,fontWeight:700,padding:"2px 8px",borderRadius:10}}>{l}</span>
            <span style={{fontSize:11,color:MT}}>{d}</span>
          </div>
        ))}
      </div>
    </div>
  </div>;
}

// ══════════════════════════════════════════════════════════════════
// APP SHELL
// ══════════════════════════════════════════════════════════════════
export default function App(){
  const [page,setPage]=useState("landing");
  const pages={landing:<Landing go={setPage}/>,submit:<Submit go={setPage}/>,processing:<Processing go={setPage}/>,dashboard:<Dashboard go={setPage}/>,findings:<Findings go={setPage}/>,queue:<Queue go={setPage}/>,report:<Report go={setPage}/>,directory:<Directory go={setPage}/>};
  return <div style={{fontFamily:"'Segoe UI',system-ui,-apple-system,sans-serif",lineHeight:1.5,color:TX,minHeight:"100vh"}}>
    <GovBar/>
    <Nav go={setPage} page={page}/>
    {pages[page]||pages.landing}
  </div>;
}
