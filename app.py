# ------------------------------------------------------------
# NCP Cyber Health Check (NIST CSF) — Streamlit PoC
# Brand: Dark navy background + gold accents
# Header uses assets/ncp_icon_512.png (rendered small for crispness)
# ------------------------------------------------------------

from __future__ import annotations
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# =========================
# Page config (Streamlit)
# =========================
st.set_page_config(
    page_title="NCP Cyber Health Check (NIST CSF)",
    page_icon="assets/ncp_icon_32.png",   # keep a 32px favicon here
    layout="wide",
)

# =========================
# Brand palette
# =========================
GOLD      = "#D4AF37"
NAVY_BG   = "#0B1220"   # page bg
CARD_BG   = "#0F172A"   # cards / sections
SOFT_BG   = "#11182B"   # inputs / tabs bg
TEXT      = "#E5E7EB"   # primary text
MUTED     = "#94A3B8"   # secondary text
BORDER    = "#1F2937"   # subtle borders

# =========================
# Global CSS (dark theme)
# =========================
st.markdown(f"""
<style>
/* App background + base typography */
html, body, .stApp {{ background: {NAVY_BG}; color: {TEXT}; }}
* {{ scrollbar-color: {GOLD} {SOFT_BG}; }}
a {{ color: {GOLD}; }}

/* Container width + spacing */
.block-container {{ max-width: 1120px; padding-top: .6rem; }}

/* Cards / blocks */
.ncp-card {{
  background: {CARD_BG};
  border: 1px solid {BORDER};
  border-radius: 14px;
  padding: 14px 16px;
}}

/* Inputs, selectboxes, radios */
.stSelectbox > div > div {{ background: {SOFT_BG}; border-radius: 10px; border:1px solid {BORDER}; }}
.stSelectbox > div > div:hover {{ border-color: {GOLD}; }}
.stRadio > div {{ row-gap: .35rem; }}
input[type="radio"], input[type="checkbox"] {{ accent-color: {GOLD}; }}

/* Buttons */
.stButton > button {{
  background: {GOLD}; border: 1px solid #C49C2C; color:#0b0b0b; font-weight:700;
  padding: .55rem 1rem; border-radius: 12px;
}}
.stButton > button:hover {{ filter: brightness(1.05); box-shadow: 0 4px 18px rgba(212,175,55,.25); }}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{ gap: 6px; }}
.stTabs [data-baseweb="tab"] {{
  color: {MUTED}; background: {SOFT_BG}; border-radius: 12px 12px 0 0;
  padding: 10px 14px; border: 1px solid {BORDER}; border-bottom: none; font-weight:700;
}}
.stTabs [aria-selected="true"] {{
  color: {TEXT}; background: {CARD_BG}; box-shadow: 0 -2px 0 0 {GOLD} inset;
}}

/* Metrics */
[data-testid="stMetricValue"] {{ color: {GOLD}; }}

/* Accent divider */
.ncp-accent {{ height:3px; background: linear-gradient(90deg,{GOLD},#f6e39a); border-radius: 999px; margin: 14px 2px 12px; }}

/* Subtle hr */
hr {{ border:0; height:1px; background:{BORDER}; }}
</style>
""", unsafe_allow_html=True)

# =========================
# Header (use st.image for reliability)
# =========================
c_logo, c_text = st.columns([0.14, 0.86], vertical_alignment="center")
with c_logo:
    st.image("assets/ncp_icon_512.png", width=56)  # high-res source, small render = crisp
with c_text:
    st.markdown(
        "<div style='line-height:1.1; font-size:28px; font-weight:800'>"
        "NCP Cyber Health Check <span style='font-weight:400'>(NIST CSF)</span>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='color:{MUTED}; margin-top:2px'>"
        "Quick maturity snapshot & clear next steps — built for SMEs"
        "</div>",
        unsafe_allow_html=True,
    )
st.markdown("<div class='ncp-accent'></div>", unsafe_allow_html=True)

# =========================
# Sidebar (short helper text)
# =========================
with st.sidebar:
    st.image("assets/ncp_icon_512.png", width=40)
    st.markdown("**NCP Cyber** — PoC")
    st.markdown(
        "Indicative assessment based on **NIST CSF** + **Essential Eight**.\n\n"
        "Results are advisory only — not a formal audit."
    )
    st.markdown("---")
    st.caption("Tip: use the report download to follow-up with prospects.")

# =========================
# Scales & question bank
# =========================
SCALE = {
    "No": 0,
    "Partially": 1,
    "Mostly": 2,
    "Fully": 3,
    "Don't know": 1,   # neutral-ish
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

# =========================
# Organization block
# =========================
st.subheader("Organization")
with st.container():
    c1, c2, c3 = st.columns([2, 1.3, 1.3])
    with c1: company = st.text_input("Company / Org name", placeholder="Acme Pty Ltd")
    with c2: industry = st.selectbox("Industry",
                                     ["Professional Services","Education","Healthcare","Finance","Retail","Government","Other"])
    with c3: size = st.selectbox("Org size", ["1–9","10–49","50–249","250–999","1000+"])

st.markdown("<div class='ncp-accent'></div>", unsafe_allow_html=True)

# =========================
# Tabs: Assessment / Results / Report
# =========================
t_assess, t_results, t_report = st.tabs(["Assessment", "Results", "Report"])

# ---- Assessment ----
with t_assess:
    st.markdown(
        f"<div class='ncp-card'>"
        f"<b>How to answer</b>: pick the option that best fits current practice. "
        f"Use <i>Don't know</i> if unsure.</div>",
        unsafe_allow_html=True,
    )
    st.write("")

    # NIST CSF Qs
    responses: dict[str, int] = {}
    for func in NIST_FUNCTIONS:
        with st.expander(f"**{func}** — {len(QUESTIONS[func])} questions", expanded=False):
            for i, q in enumerate(QUESTIONS[func], start=1):
                key = f"{func}_{i}"
                ans = st.radio(q, SCALE_LABELS, horizontal=True, index=2, key=key)
                responses[key] = SCALE[ans]

    st.markdown("---")
    st.subheader("Essential Eight quick check")
    st.caption("Pick the level that best matches your current state.")
    e8_scores: dict[str, int] = {}
    cols = st.columns(2)
    for i, control in enumerate(E8_ITEMS):
        with cols[i % 2]:
            choice = st.radio(control, E8_SCALE, horizontal=False, index=1, key=f"E8_{i}")
            e8_scores[control] = E8_SCALE.index(choice)  # 0..3

    st.write("")
    run = st.button("Calculate results")

# =========================
# Helpers (calc + report)
# =========================
def compute_nist_scores(state: dict[str, int]) -> pd.DataFrame:
    rows = []
    for func in NIST_FUNCTIONS:
        vals = [state.get(f"{func}_{i}", 1) for i in range(1, len(QUESTIONS[func]) + 1)]
        rows.append({"Function": func, "Score": float(np.mean(vals))})
    return pd.DataFrame(rows)

def compute_recos(nist_df: pd.DataFrame, e8_map: dict[str, int]) -> list[str]:
    recs: list[str] = []
    low_funcs = nist_df.sort_values("Score").head(2)["Function"].tolist()
    for lf in low_funcs:
        recs.append(f"Lift **{lf}** maturity with time-boxed actions, clear owners, and monthly check-ins.")
    for name, score in sorted(e8_map.items(), key=lambda kv: kv[1])[:2]:
        recs.append(f"Raise **Essential Eight — {name}** from Level {score} via a 30–60 day improvement plan.")
    recs.append("Enforce **MFA** universally (privileged, email, remote, cloud).")
    recs.append("Tighten **patch SLAs** for internet-exposed systems and critical apps.")
    recs.append("Ensure **tested backups** for priority data with defined RTO/RPO.")
    return recs[:6]

def build_markdown_report(company: str, industry: str, size: str,
                          nist_df: pd.DataFrame, e8_map: dict[str, int]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    title = company or "Cyber Health Check"
    lines = []
    lines.append(f"# {title} — NCP Cyber Health Check (NIST CSF)")
    lines.append("")
    lines.append(f"_Generated: {now}_  ·  _Industry:_ **{industry}**  ·  _Size:_ **{size}**")
    lines.append("")
    lines.append("## NIST CSF Results (0–3)")
    for _, r in nist_df.iterrows():
        lines.append(f"- **{r['Function']}**: {r['Score']:.2f} / 3")
    lines.append("")
    lines.append("## Essential Eight (Level 0–3)")
    for k, v in e8_map.items(): lines.append(f"- **{k}**: Level {v}")
    lines.append("")
    lines.append("## Top Recommended Actions")
    for r in compute_recos(nist_df, e8_map): lines.append(f"- {r}")
    lines.append("")
    lines.append("> Prototype only — indicative, not a formal audit or assurance report.")
    return "\n".join(lines)

# =========================
# Plotly (dark) helpers
# =========================
def darkify_fig(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=NAVY_BG,
        plot_bgcolor=NAVY_BG,
        font=dict(color=TEXT),
        margin=dict(l=10, r=10, t=10, b=10),
    )
    return fig

# ---- Results ----
with t_results:
    if run or "Identify_1" in st.session_state:
        nist_df = compute_nist_scores(st.session_state)
        overall = float(nist_df["Score"].mean()) if not nist_df.empty else 0.0

        left, right = st.columns([1.4, 1])
        with left:
            st.markdown("#### NIST CSF radar")
            r_df = pd.DataFrame({"r": nist_df["Score"], "theta": nist_df["Function"]})
            fig = px.line_polar(r_df, r="r", theta="theta", line_close=True)
            fig.update_traces(fill="toself", line_color=GOLD,
                              fillcolor="rgba(212,175,55,0.28)", name="Current")
            fig.update_layout(
                polar=dict(
                    bgcolor=NAVY_BG,
                    radialaxis=dict(visible=True, range=[0, 3], gridcolor=BORDER, linecolor=MUTED),
                    angularaxis=dict(gridcolor=BORDER, linecolor=MUTED),
                ),
                showlegend=False,
            )
            st.plotly_chart(darkify_fig(fig), use_container_width=True)

        with right:
            st.markdown("#### Overall maturity")
            st.metric("Overall (0–3)", f"{overall:.2f}")
            st.caption("Target a sustainable lift of **+0.3** over the next quarter.")

        st.markdown("---")
        st.markdown("#### Essential Eight — levels (0–3)")
        e8_df = pd.DataFrame({
            "Control": E8_ITEMS,
            "Level": [st.session_state.get(f"E8_{i}", 1) for i in range(len(E8_ITEMS))]
        })
        bar = px.bar(
            e8_df, x="Control", y="Level", range_y=[0, 3], color="Level",
            color_continuous_scale=[[0, "#5b4b17"], [0.5, "#b28f23"], [1, GOLD]],
            height=360
        )
        bar.update_layout(coloraxis_showscale=False, xaxis=dict(showgrid=False), yaxis=dict(gridcolor=BORDER))
        st.plotly_chart(darkify_fig(bar), use_container_width=True)

        st.markdown("---")
        st.markdown("#### Top recommended actions")
        recos = compute_recos(nist_df, {E8_ITEMS[i]: st.session_state.get(f"E8_{i}", 1) for i in range(len(E8_ITEMS))})
        for r in recos:
            st.markdown(f"- {r}")
    else:
        st.info("Run the assessment in the **Assessment** tab to see your results.")

# ---- Report ----
with t_report:
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

# =========================
# Footer
# =========================
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    f"<div style='display:flex;justify-content:space-between;align-items:center;"
    f"color:{MUTED};font-size:.92rem'>"
    f"<span>© 2025 National Consulting Partners — Advisory | Cyber | Data</span>"
    f"<span>Prototype only — not a formal audit or assurance report.</span>"
    f"</div>",
    unsafe_allow_html=True,
)
