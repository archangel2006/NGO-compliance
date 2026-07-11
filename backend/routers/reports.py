from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from pathlib import Path
import os

from backend.auth import get_current_user
from backend.store import (SUBMISSIONS, FINDINGS, QUEUE, REPORTS,
                            get_submission, get_findings_for_submission,
                            get_queue_for_submission, new_id, now)

REPORTS_DIR = Path(os.getenv("REPORTS_DIR", "reports"))
router      = APIRouter()


def _build_report(submission_id: str) -> dict:
    """Assemble full report data dict."""
    sub      = get_submission(submission_id)
    findings = get_findings_for_submission(submission_id)
    queue    = get_queue_for_submission(submission_id)
    score    = sub.get("score", {})

    # Split findings into auto-assessed vs human-reviewed
    auto_findings  = [f for f in findings if f["routing"] == "auto_report"]
    human_findings = [f for f in findings if f["routing"] == "human_review"]

    # Enrich human findings with officer determination
    queue_map = {q["finding_id"]: q for q in queue}
    for f in human_findings:
        q = queue_map.get(f["id"])
        if q:
            f["officer_determination"] = q.get("officer_determination")
            f["officer_notes"]         = q.get("officer_notes")
            f["reviewed_by"]           = q.get("reviewed_by")
            f["reviewed_at"]           = q.get("reviewed_at")
            f["queue_status"]          = q.get("queue_status")

    return {
        "submission":   sub,
        "overall_score":  score.get("overall_score"),
        "score_label":    score.get("label"),
        "grant_ready":    score.get("grant_ready"),
        "score_breakdown":score.get("breakdown", {}),
        "pass_count":     score.get("pass_count"),
        "fail_count":     score.get("fail_count"),
        "uncertain_count":score.get("uncertain_count"),
        "auto_findings":   auto_findings,
        "human_findings":  human_findings,
        "pending_queue":   sum(1 for q in queue if q["queue_status"] != "reviewed"),
        "generated_at":    now(),
    }


@router.get("/{submission_id}/report")
def get_report(submission_id: str, user: dict = Depends(get_current_user)):
    sub = get_submission(submission_id)
    if not sub:
        raise HTTPException(404, "Submission not found.")
    if sub["status"] != "complete":
        raise HTTPException(400, "Assessment not yet complete.")
    return _build_report(submission_id)


@router.get("/{submission_id}/report/pdf")
def download_report_pdf(submission_id: str,
                        user: dict = Depends(get_current_user)):
    """Generate and return PDF report."""
    sub = get_submission(submission_id)
    if not sub:
        raise HTTPException(404, "Submission not found.")
    if sub["status"] != "complete":
        raise HTTPException(400, "Assessment not yet complete.")

    report_data = _build_report(submission_id)
    pdf_path    = _generate_pdf(report_data, submission_id)

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"compliance_report_{submission_id[:8]}.pdf",
    )


def _generate_pdf(data: dict, submission_id: str) -> str:
    """Render HTML template to PDF via WeasyPrint."""
    try:
        from weasyprint import HTML
    except ImportError:
        raise HTTPException(500, "WeasyPrint not installed. Run: pip install weasyprint")

    html = _render_html(data)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / f"{submission_id}.pdf"
    HTML(string=html).write_pdf(str(path))
    return str(path)


def _render_html(data: dict) -> str:
    sub   = data["submission"]
    score = data["overall_score"] or 0
    color = "#16A34A" if score >= 85 else "#D97706" if score >= 70 else "#DC2626"

    auto_rows  = "".join(_finding_row(f, "AI")     for f in data["auto_findings"])
    human_rows = "".join(_finding_row(f, "Officer") for f in data["human_findings"])

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
  body {{ font-family: Arial, sans-serif; font-size: 12px;
         color: #1E293B; margin: 30px; }}
  h1   {{ color: #1A3A6B; font-size: 20px; margin-bottom: 4px; }}
  h2   {{ color: #1A3A6B; font-size: 14px; margin-top: 24px; border-bottom:
           2px solid #E8601A; padding-bottom: 4px; }}
  .meta  {{ color: #64748B; font-size: 11px; margin-bottom: 20px; }}
  .score {{ font-size: 32px; font-weight: bold; color: {color}; }}
  .label {{ color: {color}; font-size: 13px; font-weight: bold; }}
  table  {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
  th     {{ background: #1A3A6B; color: white; padding: 8px;
            text-align: left; font-size: 11px; }}
  td     {{ padding: 7px 8px; border-bottom: 1px solid #E2E8F0;
            font-size: 11px; vertical-align: top; }}
  tr:nth-child(even) {{ background: #F8FAFC; }}
  .pass    {{ color: #16A34A; font-weight: bold; }}
  .fail    {{ color: #DC2626; font-weight: bold; }}
  .uncertain {{ color: #D97706; font-weight: bold; }}
  .disclaimer {{ font-size: 9px; color: #94A3B8; margin-top: 30px;
                 border-top: 1px solid #E2E8F0; padding-top: 10px; }}
</style>
</head>
<body>
<h1>NGO Compliance Verification Report</h1>
<div class="meta">
  {sub.get("org_name")} &nbsp;|&nbsp;
  {sub.get("state", "").title()} &nbsp;|&nbsp;
  {sub.get("entity_type")} &nbsp;|&nbsp;
  PAN: {sub.get("pan")} &nbsp;|&nbsp;
  Generated: {data["generated_at"][:10]}
</div>
<div class="score">{score}</div>
<div class="label">{data.get("score_label","")}</div>
<br/>

<h2>AI-Assessed Findings ({len(data["auto_findings"])} dimensions)</h2>
<table>
  <tr><th>Dimension</th><th>Status</th><th>Confidence</th>
      <th>Legal Citation</th><th>Reasoning</th></tr>
  {auto_rows}
</table>

<h2>Human-Reviewed Findings ({len(data["human_findings"])} dimensions)</h2>
<table>
  <tr><th>Dimension</th><th>AI</th><th>Officer</th>
      <th>Reviewed By</th><th>Notes</th></tr>
  {human_rows}
</table>

<div class="disclaimer">
This report is generated by an AI-assisted compliance screening system (NGO
Compliance Verification System — NITI Aayog Pilot) and constitutes a
decision-support tool, not a legal ruling. All findings are subject to review
by designated compliance officers. Organisations must consult the relevant
Registrar or regulatory body for final compliance decisions.
</div>
</body></html>"""


def _finding_row(f: dict, source: str) -> str:
    s = f.get("status", "")
    css = {"PASS": "pass", "FAIL": "fail"}.get(s, "uncertain")
    if source == "AI":
        return f"""<tr>
  <td>{f.get("dimension_name","")}</td>
  <td class="{css}">{s}</td>
  <td>{round(f.get("confidence",0)*100)}%</td>
  <td>{f.get("legal_citation","")[:80]}</td>
  <td>{f.get("reasoning","")[:200]}</td>
</tr>"""
    else:
        det = f.get("officer_determination","PENDING")
        css2 = {"PASS":"pass","FAIL":"fail"}.get(det,"uncertain")
        return f"""<tr>
  <td>{f.get("dimension_name","")}</td>
  <td class="{css}">{s} (AI)</td>
  <td class="{css2}">{det} (Officer)</td>
  <td>{f.get("reviewed_by","Pending")}</td>
  <td>{f.get("officer_notes","—")}</td>
</tr>"""