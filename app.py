# ------------------------------------------------------------
# Cyber Health Check (NIST CSF) — NCP PoC
# Polished UI: NCP branding, gold accents, radar + bar charts,
# simple assessment, and Markdown report download.
# ------------------------------------------------------------

from __future__ import annotations
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# ---------------------------
# PAGE CONFIGURATION
# ---------------------------
st.set_page_config(
    page_title="Cyber Health Check (NIST CSF) — NCP PoC",
    page_icon="assets/ncp_icon_32.png",
    layout="wide",
)

# ---------------------------
# GLOBAL THEME POLISH (CSS)
# ---------------------------
st.markdown(
    """
<style>
/* Layout width + top spacing */
.block-container {max-width: 1120px; padding-top: 0.6rem;}

/* Hero card */
.ncp-hero{display:flex;gap:16px;align-items:center;padding:14px 18px;border:1px solid #ececec;
          border-radius:14px;background:#fff;box-shadow:0 2px 14px rgba(0,0,0,.04);}
.ncp-hero img{width:48px;height:48px;display:block}
.ncp-hero h1{font-size:28px;line-height:1.15;margin:0;color:#0b0b0b;font-weight:800}
.ncp-hero small{display:block;margin-top:2px;color:#6b7280}
.ncp-accent{height:3px;background:linear-gradient(90deg,#D4AF37,#f6e39a);border-radius:999px;margin:14px 2px 0}

/* Buttons */
.stButton > button{
  background:#D4AF37;border:1px solid #C49C2C;color:#0b0b0b;font-weight:700;
  padding:.6rem 1rem;border-radius:12px;
}
.stButton > button:hover{filter:brightness(1.03); box-shadow:0 4px 14px rgba(212,175,55,.2)}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{gap:6px}
.stTabs [data-baseweb="tab"]{
  color:#374151;background:#F6F7F9;border-radius:12px 12px 0 0;
  padding:10px 14px;font-weight:700;border:1px solid #e8e8e8; border-bottom:none;
}
.stTabs [aria-selected="true"]{
  background:#fff;color:#0b0b0b;box-shadow:0 -2px 0 0 #D4AF37 inset;
}

/* Select / Radio accent (modern browsers) */
input[type="radio"], input[type="checkbox"] {accent-color:#D4AF37}
.stSelectbox > div > div {border-radius:10px}

/* Cards / sections */
.ncp-card{border:1px solid #ececec;border-radius:14px;padding:14px 16px;background:#fff}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------
# HEADER
# ---------------------------
st.markdown(
    """
<div class="ncp-hero">
  <img src="assets/ncp_icon_64.png" alt="NCP">
  <div>
    <h1>Cyber Health Check <span style="font-weight:400">(NIST CSF)</span></h1>
    <small>National Consulting Partners — quick maturity snapshot & clear next steps</small>
  </div>
</div>
<div class="ncp-accent"></div>
""",
    unsafe_allow_html=True,
)

# ---------------------------
# SIDEBAR
# ---------------------------
with st.sidebar:
    st.image("assets/ncp_icon_64.png", width=36)
    st.markdown("**NCP Cyber** — PoC")
    st.markdown(
        "This lightweight assessment gives an indicative view of maturity "
        "using **NIST CSF** and **Essential Eight**. Results are advisory only."
    )
    st.markdown("---")
    st.caption("Tip: Use this during discovery calls. Export the report and send a follow-up email.")

# ---------------------------
# INPUT HELPERS & DATA
# ---------------------------
SCALE = {
    "No": 0,
    "Partially": 1,
    "Mostly": 2,
    "Fully": 3,
    "Don't know": 1,   # neutral-ish weight
}
SCALE_LABELS = list(SCALE.keys())

NIST_FUNCTIONS = ["Identify", "Protect", "Detect", "Respond", "Recover"]

QUESTIONS = {
    "Identify": [
        "We maintain an up-to-date asset inventory (devices, SaaS, data).",
        "We classify sensitive data and know where it lives.",
        "Roles and security responsibilities are clearly assigned.",
    ],
    "Protect": [
        "Multi-factor authentication protects critical systems and remote access.",
        "Patching is managed and updates are applied within defined timeframes.",
        "Backups are tested and critical systems have recovery objectives.",
    ],
    "Detect": [
        "We collect and review security logs from critical systems.",
        "We receive threat or vendor advisories and triage them.",
        "We baseline normal behaviour and detect anomalies.",
    ],
    "Respond": [
        "We have an approved, tested incident response plan (IRP).",
        "We have a process for notifying affected parties/regulators where required.",
        "We can isolate endpoints, reset credentials and revoke access quickly.",
    ],
    "Recover": [
        "We have a disaster recovery plan with RTO/RPO targets.",
        "We complete post-incident lessons learned and update playbooks.",
        "We regularly rehearse recovery procedures for priority systems.",
    ],
}

E8_ITEMS = [
    "Application Control", "Patch Applications", "Configure MS Office Macros",
    "User Application Hardening", "Restrict Admin Privileges",
    "Patch Operating Systems", "Multi-factor Authentication", "Regular Backups"
]
E8_SCALE = ["Not implemented", "Partially", "Mostly", "Fully"]

# ---------------------------
# ORGANIZATION
# ---------------------------
st.subheader("Organization")
with st.container():
    c1, c2, c3 = st.columns([2, 1.3, 1.3])
    company = c1.text_input("Company / Org name")
    industry = c2.selectbox(
        "Industry",
        ["Professional Services", "Education", "Healthcare", "Finance", "Retail", "Government", "Other"],
    )
    size = c3.selectbox("Org size", ["1–9", "10–49", "50–249", "250–999", "1000+"])

st.divider()

# ---------------------------
# ASSESSMENT TABS
# ---------------------------
tab_assess, tab_results, tab_report = st.tabs(["Assessment", "Results", "Report"])

with tab_assess:
    st.markdown(
        "Answer honestly. Use **Don't know** if unsure — we’ll treat that as a middle score so your results stay balanced."
    )
    st.markdown("")

    responses = {}
    for func in NIST_FUNCTIONS:
        with st.expander(f"**{func}** — {len(QUESTIONS[func])} questions", expanded=False):
            for i, q in enumerate(QUESTIONS[func], start=1):
                key = f"{func}_{i}"
                ans = st.radio(q, SCALE_LABELS, horizontal=True, key=key, index=2)  # default "Mostly"
                responses[key] = SCALE[ans]

    st.markdown("---")
    st.subheader("Essential Eight quick check")
    st.caption("Indicative self-assessment of ACSC Essential Eight. Pick the level that best matches your current state.")
    e8_scores = {}
    e8_cols = st.columns(2)
    for i, name in enumerate(E8_ITEMS):
        with e8_cols[i % 2]:
            choice = st.radio(name, E8_SCALE, horizontal=False, key=f"E8_{i}", index=1)
            e8_scores[name] = E8_SCALE.index(choice)  # 0..3

    st.markdown("")
    run = st.button("Calculate results")

# ---------------------------
# CALCULATE
# ---------------------------
def compute_nist_scores(resp: dict[str, int]) -> pd.DataFrame:
    rows = []
    for func in NIST_FUNCTIONS:
        vals = [resp.get(f"{func}_{i}", 1) for i in range(1, len(QUESTIONS[func]) + 1)]
        avg = float(np.mean(vals)) if vals else 0.0
        rows.append({"Function": func, "Score": avg})
    return pd.DataFrame(rows)

def compute_recos(nist_df: pd.DataFrame, e8_map: dict[str, int]) -> list[str]:
    recs = []
    # Lowest two NIST functions
    low_funcs = nist_df.sort_values("Score").head(2)["Function"].tolist()
    for lf in low_funcs:
        recs.append(f"Raise **{lf}** maturity with short, time-boxed actions and clear owners.")
    # Highlight weakest E8 items
    e8_sorted = sorted(e8_map.items(), key=lambda x: x[1])
    for name, score in e8_sorted[:2]:
        recs.append(f"Lift **Essential Eight — {name}** from level {score} with a 30-day improvement plan.")
    # Generic quick wins
    recs.append("Enable **MFA** everywhere practical (privileged, remote, cloud, email).")
    recs.append("Tighten **patching SLAs** for internet-exposed systems and critical apps.")
    recs.append("Ensure **tested backups** for critical data and define RTO/RPO.")
    return recs[:6]

def build_markdown_report(company: str, industry: str, size: str,
                          nist_df: pd.DataFrame, e8_map: dict[str, int]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = []
    title = company or "Cyber Health Check"
    lines.append(f"# {title} — NCP Cyber Health Check (NIST CSF)")
    lines.append("")
    lines.append(f"_Generated on {now}_  \n_Industry:_ **{industry}**  ·  _Size:_ **{size}**")
    lines.append("")
    lines.append("## NIST CSF Results (0–3)")
    for _, row in nist_df.iterrows():
        lines.append(f"- **{row['Function']}**: {row['Score']:.2f} / 3")
    lines.append("")
    lines.append("## Essential Eight (Level 0–3)")
    for k, v in e8_map.items():
        lines.append(f"- **{k}**: Level {v}")
    lines.append("")
    lines.append("## Top Recommended Actions")
    for r in compute_recos(nist_df, e8_map):
        lines.append(f"- {r}")
    lines.append("")
    lines.append("> Prototype only — indicative, not a formal audit or assurance report.")
    return "\n".join(lines)

# ---------------------------
# RESULTS
# ---------------------------
with tab_results:
    if run or "Identify_1" in st.session_state:
        nist_df = compute_nist_scores(st.session_state)
        overall = nist_df["Score"].mean() if not nist_df.empty else 0.0

        left, right = st.columns([1.4, 1])
        with left:
            st.markdown("#### NIST CSF radar")
            r_df = pd.DataFrame(dict(
                r=nist_df["Score"].tolist(),
                theta=nist_df["Function"].tolist()
            ))
            fig = px.line_polar(r_df, r='r', theta='theta', line_close=True)
            fig.update_traces(fill='toself', name='Current State', line_color="#D4AF37")
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 3])),
                showlegend=False, margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig, use_container_width=True)

        with right:
            st.markdown("#### Overall maturity")
            st.metric("Overall (0–3)", f"{overall:.2f}")
            st.caption("Target a sustainable lift of **+0.3** over the next quarter.")

        st.markdown("---")
        st.markdown("#### Essential Eight — levels (0–3)")
        e8_df = pd.DataFrame({
            "Control": list(E8_ITEMS),
            "Level": [st.session_state.get(f"E8_{i}", 1) for i in range(len(E8_ITEMS))]
        })
        bar = px.bar(e8_df, x="Control", y="Level", range_y=[0,3], color="Level",
                     color_continuous_scale=[[0,"#f4e7b2"],[1,"#D4AF37"]],
                     height=360)
        bar.update_layout(margin=dict(l=10, r=10, t=10, b=10), coloraxis_showscale=False)
        st.plotly_chart(bar, use_container_width=True)

        st.markdown("---")
        st.markdown("#### Top recommended actions")
        recos = compute_recos(nist_df, {E8_ITEMS[i]: st.session_state.get(f"E8_{i}", 1) for i in range(len(E8_ITEMS))})
        for r in recos:
            st.markdown(f"- {r}")

    else:
        st.info("Run the assessment in the **Assessment** tab to see your results.")

# ---------------------------
# REPORT
# ---------------------------
with tab_report:
    if run or "Identify_1" in st.session_state:
        nist_df = compute_nist_scores(st.session_state)
        e8_map = {E8_ITEMS[i]: st.session_state.get(f"E8_{i}", 1) for i in range(len(E8_ITEMS))}
        md = build_markdown_report(company, industry, size, nist_df, e8_map)
        st.markdown("#### Download Markdown report")
        st.download_button(
            "Download report (.md)",
            md,
            file_name=f"{(company or 'NCP_Cyber_Health_Check').replace(' ','_')}.md",
            type="primary",
        )
        st.markdown("Preview:")
        st.code(md, language="markdown")
    else:
        st.info("Generate results first, then download your report here.")

# ---------------------------
# FOOTER
# ---------------------------
st.markdown(
    """
<hr style="border:0;height:1px;background:#f0f0f0;margin:32px 0 10px">
<div style="display:flex;justify-content:space-between;align-items:center;color:#6b7280;font-size:.92rem">
  <span>© 2025 National Consulting Partners — Advisory | Cyber | Data</span>
  <span>Prototype only — not a formal audit or assurance report.</span>
</div>
""",
    unsafe_allow_html=True,
)
