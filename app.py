import os
import math
import datetime as dt
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st

try:
    import plotly.graph_objects as go
    PLOTLY_OK = True
except Exception:
    PLOTLY_OK = False

st.set_page_config(page_title="Cyber Health Check (NIST CSF PoC)", page_icon="🛡️", layout="wide")

NIST_FUNCTIONS = ["Identify", "Protect", "Detect", "Respond", "Recover"]

QUESTION_SET: List[Dict] = [
    {"id":"ID-1","domain":"Identify","text":"We keep an up-to-date asset inventory (devices, SaaS, data).","weight":1.0},
    {"id":"ID-2","domain":"Identify","text":"We classify sensitive data and know where it lives.","weight":1.0},
    {"id":"ID-3","domain":"Identify","text":"We have named security roles & responsibilities (RACI).","weight":1.0},
    {"id":"PR-1","domain":"Protect","text":"Multi‑factor authentication (MFA) is enforced for all admin and remote access.","weight":1.5},
    {"id":"PR-2","domain":"Protect","text":"All devices have disk encryption enabled.","weight":1.0},
    {"id":"PR-3","domain":"Protect","text":"Patching: OS/apps are updated within defined timeframes.","weight":1.2},
    {"id":"PR-4","domain":"Protect","text":"Users receive phishing/security awareness training at least annually.","weight":0.8},
    {"id":"DE-1","domain":"Detect","text":"We collect and review security logs from critical systems (e.g., M365/AWS).","weight":1.2},
    {"id":"DE-2","domain":"Detect","text":"Alerts are configured for suspicious sign‑ins and data exfiltration.","weight":1.0},
    {"id":"RS-1","domain":"Respond","text":"We have a documented incident response plan (IRP).","weight":1.2},
    {"id":"RS-2","domain":"Respond","text":"We run an incident simulation/table‑top at least annually.","weight":1.0},
    {"id":"RC-1","domain":"Recover","text":"We have tested backups for critical systems and data in the last 6 months.","weight":1.2},
    {"id":"RC-2","domain":"Recover","text":"We have defined recovery time objectives (RTO) for key services.","weight":1.0},
]

REMEDIATIONS: Dict[str, List[str]] = {
    "Identify": [
        "Establish and maintain an asset inventory across devices, accounts, SaaS, and data stores.",
        "Label and protect sensitive data; restrict access based on least‑privilege.",
        "Publish a lightweight RACI so staff know their security responsibilities."
    ],
    "Protect": [
        "Enforce MFA for all users, especially admins and remote access.",
        "Turn on full‑disk encryption and automatic lock on all endpoints.",
        "Adopt a monthly patching cadence; urgent patches within 7–14 days."
    ],
    "Detect": [
        "Enable audit logs for M365/Google/AWS and centralise high‑value alerts.",
        "Set alerts for impossible travel, excessive downloads, and repeated failed logins."
    ],
    "Respond": [
        "Write a one‑page IRP with roles, contacts, and severity levels.",
        "Run a 60‑minute tabletop exercise each quarter and capture lessons learned."
    ],
    "Recover": [
        "Back up key systems daily; test restores quarterly (at least one full test).",
        "Define RTO/RPO for each critical system and align backup strategy."
    ],
}

INDUSTRY_THREATS = {
    "Healthcare": ["Ransomware on file servers/EMR", "Phishing for patient data", "Legacy device vulnerabilities"],
    "Professional Services": ["Business email compromise (BEC)", "Account takeover", "Data leakage from SaaS"],
    "Construction": ["BEC on invoices", "Unpatched laptops on site", "Weak vendor access"],
    "Retail": ["POS malware (if applicable)", "Credential stuffing", "Unsegmented Wi‑Fi"],
    "Education": ["Phishing targeting staff/students", "Unmanaged endpoints", "Shadow IT / SaaS sprawl"],
    "Other": ["Phishing & credential theft", "Ransomware", "Shadow IT"]
}

CHOICES = ["Yes", "Partially", "No", "Don't know"]
SCORE_MAP = {"Yes": 1.0, "Partially": 0.5, "No": 0.0, "Don't know": 0.0}

def score_answers(answers: Dict[str, str]) -> Tuple[pd.DataFrame, Dict[str, float], float]:
    rows = []
    for q in QUESTION_SET:
        sel = answers.get(q["id"], "Don't know")
        raw = SCORE_MAP.get(sel, 0.0)
        weighted = raw * q["weight"]
        rows.append({
            "id": q["id"],
            "domain": q["domain"],
            "question": q["text"],
            "choice": sel,
            "raw": raw,
            "weight": q["weight"],
            "weighted": weighted
        })
    df = pd.DataFrame(rows)
    domain_scores = {}
    for dom in ["Identify","Protect","Detect","Respond","Recover"]:
        d = df[df["domain"] == dom]
        if len(d) == 0:
            domain_scores[dom] = 0.0
        else:
            max_possible = d["weight"].sum()
            got = d["weighted"].sum()
            frac = got / max_possible if max_possible > 0 else 0.0
            domain_scores[dom] = 1.0 + 4.0 * frac  # 1..5
    overall_index = round(100.0 * (sum(domain_scores.values()) / (5.0 * 5.0)), 1)
    return df, domain_scores, overall_index

def top_recommendations(domain_scores: Dict[str, float], industry: str, k: int = 6) -> List[str]:
    ranked = sorted(domain_scores.items(), key=lambda x: x[1])
    recs = []
    for dom, _ in ranked:
        for r in REMEDIATIONS.get(dom, []):
            if r not in recs:
                recs.append(r)
            if len(recs) >= k:
                break
        if len(recs) >= k:
            break
    threats = INDUSTRY_THREATS.get(industry, INDUSTRY_THREATS["Other"])
    recs.append(f"Industry watch‑outs: {', '.join(threats)}.")
    return recs

def radar_chart(domain_scores: Dict[str, float]):
    if not PLOTLY_OK:
        st.warning("Plotly not installed. Radar chart unavailable. Install `plotly` to enable charts.")
        return
    cats = list(domain_scores.keys())
    vals = list(domain_scores.values())
    cats += [cats[0]]
    vals += [vals[0]]
    import plotly.graph_objects as go
    fig = go.Figure(data=go.Scatterpolar(r=vals, theta=cats, fill='toself', name='Score'))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[1,5])),
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=20),
        height=420
    )
    st.plotly_chart(fig, use_container_width=True)

def build_markdown_report(meta: Dict, domain_scores: Dict[str, float], overall: float, recs: List[str]) -> str:
    lines = []
    lines.append(f"# Cyber Health Check — PoC Report")
    lines.append("")
    lines.append(f"**Organization:** {meta.get('name','(not provided)')}  ")
    lines.append(f"**Industry:** {meta.get('industry')}  ")
    lines.append(f"**Size:** {meta.get('size')} staff  ")
    lines.append(f"**Region:** {meta.get('region')}  ")
    lines.append(f"**Date:** {dt.date.today().isoformat()}")
    lines.append("")
    lines.append(f"## Overall Index")
    lines.append(f"**{overall}/100**  ")
    lines.append("> Index is the average of NIST CSF function scores normalised to 100.")
    lines.append("")
    lines.append("## NIST CSF Function Scores (1–5)")
    for k,v in domain_scores.items():
        lines.append(f"- **{k}:** {v:.1f}")
    lines.append("")
    lines.append("## Top Recommendations")
    for i, r in enumerate(recs, 1):
        lines.append(f"{i}. {r}")
    lines.append("")
    lines.append("_This is a demonstration prototype. Results are advisory and not a formal audit._")
    return "
".join(lines)

st.title("🛡️ Cyber Health Check (NIST CSF) — Proof of Concept")
st.caption("A lightweight prototype to assess SME cyber maturity and generate actionable next steps.")

with st.sidebar:
    st.header("Organization")
    org_name = st.text_input("Company / Org name", "")
    industry = st.selectbox("Industry", ["Professional Services","Healthcare","Construction","Retail","Education","Other"], index=0)
    size = st.number_input("Headcount", min_value=1, max_value=100000, value=25, step=1)
    region = st.selectbox("Region", ["AU/NZ", "SE Asia", "North America", "Europe/MENA", "Other"], index=0)
    st.markdown("---")
    st.write("**How scoring works**")
    st.write("• Each question is weighted.\n• Answers map to a 1–5 function score.\n• Overall index is the mean of function scores scaled to 100.")

st.subheader("Assessment")
st.write("Answer the questions below as **Yes / Partially / No / Don't know**. Keep it honest — this helps prioritise your next steps.")

with st.form("assessment"):
    answers = {}
    cols = st.columns(2)
    for i, q in enumerate(QUESTION_SET):
        with cols[i % 2]:
            answers[q["id"]] = st.radio(q["text"], CHOICES, index=2, key=q["id"])
    submitted = st.form_submit_button("Calculate Results")

if submitted:
    df, domain_scores, overall = score_answers(answers)
    st.success(f"Calculated overall Cyber Health Index: **{overall}/100**")
    c1, c2 = st.columns([1,1])
    with c1:
        st.markdown("#### NIST CSF Scores (1–5)")
        score_tbl = pd.DataFrame({
            "Function": list(domain_scores.keys()),
            "Score (1–5)": [round(v,1) for v in domain_scores.values()]
        })
        st.dataframe(score_tbl, use_container_width=True, hide_index=True)
    with c2:
        st.markdown("#### Radar View")
        radar_chart(domain_scores)

    st.markdown("#### Top Recommended Actions")
    recs = top_recommendations(domain_scores, industry, k=6)
    for i, r in enumerate(recs, 1):
        st.write(f"{i}. {r}")

    meta = {"name": org_name, "industry": industry, "size": size, "region": region}
    report_md = build_markdown_report(meta, domain_scores, overall, recs)
    st.download_button("⬇️ Download PoC Report (Markdown)", data=report_md.encode("utf-8"), file_name="cyber_health_poc_report.md", mime="text/markdown")

    st.markdown("---")
    st.caption("© PoC — For demonstration only.")

else:
    st.info("Fill the form and click **Calculate Results** to see your scores and tailored next steps.")
