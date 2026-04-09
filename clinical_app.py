import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="MTM Patient Worklist",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# CSS — dark theme, fixed layout
# -----------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }

    /* Dark background */
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .main .block-container { padding: 16px 24px 8px 24px !important; max-width: 100% !important; }
    section[data-testid="stSidebar"] { display: none; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: #161b22; }
    ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 4px; }

    /* Metrics */
    [data-testid="stMetric"] {
        background: #161b22 !important;
        border: 1px solid #21262d !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.68rem !important; text-transform: uppercase;
        letter-spacing: 0.08em; color: #8b949e !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 1.6rem !important; color: #e6edf3 !important;
    }

    /* Radio buttons — fix label visibility */
    [data-testid="stRadio"] label {
        color: #c9d1d9 !important;
        font-size: 0.88rem !important;
    }
    [data-testid="stRadio"] > div {
        gap: 4px !important;
    }
    [data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {
        color: #c9d1d9 !important;
        font-size: 0.88rem !important;
    }

    /* Checkbox */
    [data-testid="stCheckbox"] label {
        color: #c9d1d9 !important;
        font-size: 0.85rem !important;
    }

    /* Selectbox */
    [data-testid="stSelectbox"] > div > div {
        background: #161b22 !important;
        border: 1px solid #30363d !important;
        color: #c9d1d9 !important;
        border-radius: 8px !important;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] { border: 1px solid #21262d; border-radius: 10px; }

    /* Dividers */
    hr { border-color: #21262d !important; }

    /* Section label */
    .sec-label {
        font-size: 0.65rem; text-transform: uppercase;
        letter-spacing: 0.1em; color: #8b949e;
        font-weight: 500; margin-bottom: 8px; margin-top: 2px;
    }

    /* Risk badges */
    .badge-high   { background:#3d1a1a; color:#ff7b7b; border:1px solid #6e2d2d; padding:3px 12px; border-radius:20px; font-size:0.78rem; font-weight:600; display:inline-block; }
    .badge-medium { background:#3d2e0a; color:#ffc057; border:1px solid #6e500f; padding:3px 12px; border-radius:20px; font-size:0.78rem; font-weight:600; display:inline-block; }
    .badge-low    { background:#0d2e1a; color:#57d989; border:1px solid #1a6e3d; padding:3px 12px; border-radius:20px; font-size:0.78rem; font-weight:600; display:inline-block; }

    /* Patient header card */
    .patient-card { background:#161b22; border:1px solid #21262d; border-radius:12px; padding:14px 18px; margin-bottom:10px; }
    .patient-card-high   { border-left:4px solid #ef4444; }
    .patient-card-medium { border-left:4px solid #f59e0b; }
    .patient-card-low    { border-left:4px solid #22c55e; }

    /* Action boxes */
    .action-high   { background:#1f0d0d; border:1px solid #6e2d2d; border-radius:10px; padding:12px 16px; margin-bottom:10px; }
    .action-medium { background:#1f1a0d; border:1px solid #6e500f; border-radius:10px; padding:12px 16px; margin-bottom:10px; }
    .action-low    { background:#0d1f14; border:1px solid #1a6e3d; border-radius:10px; padding:12px 16px; margin-bottom:10px; }

    .action-label-high   { color:#ff7b7b; font-size:0.65rem; text-transform:uppercase; letter-spacing:0.08em; font-weight:600; margin-bottom:5px; }
    .action-label-medium { color:#ffc057; font-size:0.65rem; text-transform:uppercase; letter-spacing:0.08em; font-weight:600; margin-bottom:5px; }
    .action-label-low    { color:#57d989; font-size:0.65rem; text-transform:uppercase; letter-spacing:0.08em; font-weight:600; margin-bottom:5px; }

    .action-text-high   { color:#fca5a5; font-size:0.9rem; line-height:1.5; }
    .action-text-medium { color:#fcd34d; font-size:0.9rem; line-height:1.5; }
    .action-text-low    { color:#86efac; font-size:0.9rem; line-height:1.5; }

    /* Why box */
    .why-box { background:#161b22; border:1px solid #21262d; border-radius:10px; padding:12px 16px; margin-bottom:10px; }
    .why-text { font-size:0.88rem; line-height:1.6; color:#8b949e; }
    .why-text strong { color:#c9d1d9; font-weight:500; }

    /* Confidence */
    .conf-agree    { background:#0d2e1a; border:1px solid #1a6e3d; border-radius:8px; padding:8px 14px; font-size:0.82rem; color:#57d989; margin-bottom:10px; }
    .conf-disagree { background:#1f1a0d; border:1px solid #6e500f; border-radius:8px; padding:8px 14px; font-size:0.82rem; color:#ffc057; margin-bottom:10px; }

    /* Number flags */
    .flag-bad  { color:#ff7b7b; font-size:0.72rem; font-weight:500; margin-top:2px; }
    .flag-warn { color:#ffc057; font-size:0.72rem; font-weight:500; margin-top:2px; }
    .flag-ok   { color:#57d989; font-size:0.72rem; font-weight:500; margin-top:2px; }

    /* Metric cards dark */
    [data-testid="stMetric"] [data-testid="stMetricDelta"] { display:none; }

    /* Filter panel */
    .filter-panel {
        background:#161b22; border:1px solid #21262d;
        border-radius:12px; padding:16px;
        height:100%;
    }

    /* Plotly chart background */
    .js-plotly-plot { border-radius:10px; overflow:hidden; }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# File path + data loading
# -----------------------------
DATA_PATH = Path("data/scored_data.csv")

@st.cache_data
def load_data(path):
    if not path.exists():
        raise FileNotFoundError(f"Could not find file at: {path}")
    return pd.read_csv(path)

try:
    df = load_data(DATA_PATH)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

if "final_risk" not in df.columns:
    if "risk_score_C" in df.columns:
        df["final_risk"] = "Low"
        df.loc[df["risk_score_C"] >= 0.6, "final_risk"] = "Medium"
        df.loc[df["risk_score_C"] >= 0.8, "final_risk"] = "High"
    else:
        st.error("Risk data not found.")
        st.stop()

tier_order = {"High": 0, "Medium": 1, "Low": 2}
df["_sort"] = df["final_risk"].map(tier_order)
df = df.sort_values(["_sort", "risk_score_C"], ascending=[True, False]).drop(columns=["_sort"])

# -----------------------------
# Helpers
# -----------------------------
def plain_explanation(row):
    drivers = []
    if "med_count" in row.index and row["med_count"] >= 8:
        drivers.append(f"taking {int(row['med_count'])} medications (very high)")
    elif "med_count" in row.index and row["med_count"] >= 5:
        drivers.append(f"taking {int(row['med_count'])} medications (polypharmacy)")
    if "adherence_score" in row.index and row["adherence_score"] < 0.5:
        drivers.append(f"very low adherence ({int(row['adherence_score']*100)}%)")
    elif "adherence_score" in row.index and row["adherence_score"] < 0.7:
        drivers.append(f"below-target adherence ({int(row['adherence_score']*100)}%)")
    if "last_hospital" in row.index and row["last_hospital"] == 1:
        drivers.append("recent hospitalisation")
    if "comorbidity_count" in row.index and row["comorbidity_count"] >= 4:
        drivers.append(f"{int(row['comorbidity_count'])} chronic conditions (complex)")
    elif "comorbidity_count" in row.index and row["comorbidity_count"] >= 2:
        drivers.append(f"{int(row['comorbidity_count'])} chronic conditions")
    if not drivers:
        return "No major risk factors identified at this time."
    if len(drivers) == 1:
        return f"This patient is flagged due to {drivers[0]}."
    return f"This patient is flagged due to {', '.join(drivers[:-1])}, and {drivers[-1]}."

def clinical_action(row):
    risk = row["final_risk"]
    if risk == "High":
        if "last_hospital" in row.index and row["last_hospital"] == 1:
            return "Call today — post-discharge medication review needed. Reconcile discharge medications and assess adherence barriers."
        elif "med_count" in row.index and row.get("med_count", 0) >= 8:
            return "Schedule urgent comprehensive MTM session. Assess for deprescribing opportunities and drug interaction risks."
        else:
            return "High-priority outreach. Complete medication review and adherence assessment before next refill."
    elif risk == "Medium":
        if "last_hospital" in row.index and row["last_hospital"] == 1:
            return "Follow-up call within 2 weeks. Confirm medication changes after discharge."
        return "Standard MTM outreach at next scheduled interval. Monitor chronic disease management."
    return "Routine follow-up only. No urgent action required at this time."

# -----------------------------
# Header row — compact
# -----------------------------
st.markdown("""
<div style="padding:8px 0 12px 0; border-bottom:1px solid #21262d; margin-bottom:14px;
            display:flex; justify-content:space-between; align-items:flex-end;">
    <div>
        <span style="font-family:'IBM Plex Mono',monospace; font-size:0.62rem;
                     text-transform:uppercase; letter-spacing:0.12em; color:#8b949e;">
            MTM Clinical Decision Support · Pharmacist View
        </span>
        <h1 style="font-size:1.4rem; font-weight:500; color:#e6edf3; margin:2px 0 0 0;">
            Patient worklist
        </h1>
    </div>
    <span style="font-size:0.78rem; color:#8b949e;">Sorted: highest priority first</span>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Summary metrics row — compact
# -----------------------------
high_n   = int((df["final_risk"] == "High").sum())
medium_n = int((df["final_risk"] == "Medium").sum())
low_n    = int((df["final_risk"] == "Low").sum())

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total patients",        len(df))
m2.metric("🔴 Urgent review",       high_n)
m3.metric("🟡 Monitor closely",     medium_n)
m4.metric("🟢 Routine follow-up",   low_n)

st.markdown("<div style='margin-bottom:12px'></div>", unsafe_allow_html=True)

# -----------------------------
# Main layout — 3 columns
# left: filters | middle: patient info | right: chart + numbers
# -----------------------------
col_filters, col_main, col_right = st.columns([1, 2, 2])

# ── LEFT — Filters ──────────────────────────────────────────
with col_filters:
    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)

    st.markdown('<p class="sec-label">Filter by risk level</p>', unsafe_allow_html=True)
    tier_filter = st.radio(
        "Risk level",
        options=["All patients", "High only", "Medium only", "Low only"],
        label_visibility="collapsed",
        key="tier_radio"
    )

    st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)
    st.markdown('<p class="sec-label">Additional filters</p>', unsafe_allow_html=True)

    hosp_only = False
    conf_only = False
    if "last_hospital" in df.columns:
        hosp_only = st.checkbox("Recently hospitalised only", key="hosp_chk")
    if "all_agree" in df.columns:
        conf_only = st.checkbox("High confidence only", key="conf_chk")

    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
    st.markdown('<p class="sec-label">Select patient</p>', unsafe_allow_html=True)

    # Apply filters
    view_df = df.copy()
    if tier_filter == "High only":
        view_df = view_df[view_df["final_risk"] == "High"]
    elif tier_filter == "Medium only":
        view_df = view_df[view_df["final_risk"] == "Medium"]
    elif tier_filter == "Low only":
        view_df = view_df[view_df["final_risk"] == "Low"]
    if hosp_only and "last_hospital" in view_df.columns:
        view_df = view_df[view_df["last_hospital"] == 1]
    if conf_only and "all_agree" in view_df.columns:
        view_df = view_df[view_df["all_agree"] == True]

    if len(view_df) == 0:
        st.warning("No patients match filters.")
        st.stop()

    def patient_label(row):
        adh  = int(row["adherence_score"] * 100) if "adherence_score" in row.index else 0
        meds = int(row["med_count"]) if "med_count" in row.index else 0
        hosp = " · Hosp." if "last_hospital" in row.index and row["last_hospital"] == 1 else ""
        return f"{row['patient_id']}  [{row['final_risk']}]  {meds} meds · {adh}%{hosp}"

    labels     = [patient_label(r) for _, r in view_df.iterrows()]
    patient_ids = view_df["patient_id"].tolist()

    selected_label = st.selectbox(
        "Patient", options=labels, label_visibility="collapsed", key="patient_sel"
    )
    selected_id = patient_ids[labels.index(selected_label)]
    patient     = view_df.loc[view_df["patient_id"] == selected_id].iloc[0]
    risk        = patient["final_risk"]
    risk_lower  = risk.lower()

    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#0d1117; border:1px solid #21262d; border-radius:8px; padding:10px 12px;">
        <p style="font-size:0.68rem; text-transform:uppercase; letter-spacing:0.08em;
                  color:#8b949e; margin:0 0 6px 0;">Showing</p>
        <p style="font-size:0.85rem; color:#e6edf3; margin:0;">
            <strong style="color:#e6edf3">{len(view_df)}</strong> patients
        </p>
        <p style="font-size:0.78rem; color:#8b949e; margin:4px 0 0 0;">
            {int((view_df['final_risk']=='High').sum())} high &nbsp;·&nbsp;
            {int((view_df['final_risk']=='Medium').sum())} medium &nbsp;·&nbsp;
            {int((view_df['final_risk']=='Low').sum())} low
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ── MIDDLE — Patient info ───────────────────────────────────
with col_main:

    age_str  = f"Age {int(patient['age'])}" if "age" in patient.index else ""
    meds_str = f"{int(patient['med_count'])} active medications" if "med_count" in patient.index else ""

    # Patient header
    st.markdown(f"""
    <div class="patient-card patient-card-{risk_lower}">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <span style="font-family:'IBM Plex Mono',monospace; font-size:1.15rem;
                             font-weight:500; color:#e6edf3;">{selected_id}</span>
                <span style="margin-left:10px; color:#8b949e; font-size:0.85rem;">
                    {age_str} &nbsp;·&nbsp; {meds_str}
                </span>
            </div>
            <span class="badge-{risk_lower}">{risk} risk</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Confidence
    if "all_agree" in patient.index:
        if bool(patient["all_agree"]):
            st.markdown('<div class="conf-agree">✅ High confidence — all models agree on this classification</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="conf-disagree">⚠️ Models disagree — manual review recommended before acting</div>', unsafe_allow_html=True)

    # Recommended action
    action = clinical_action(patient) if "recommendation" not in patient.index else patient["recommendation"]
    st.markdown(f"""
    <div class="action-{risk_lower}">
        <div class="action-label-{risk_lower}">Recommended action</div>
        <div class="action-text-{risk_lower}">{action}</div>
    </div>
    """, unsafe_allow_html=True)

    # Why this risk
    st.markdown('<p class="sec-label">Why this risk level?</p>', unsafe_allow_html=True)
    explanation = plain_explanation(patient) if "explanation" not in patient.index else patient["explanation"]
    st.markdown(f"""
    <div class="why-box">
        <div class="why-text">{explanation}</div>
    </div>
    """, unsafe_allow_html=True)

    # Key numbers — 2x2 compact grid
    st.markdown('<p class="sec-label">Key clinical numbers</p>', unsafe_allow_html=True)
    n1, n2 = st.columns(2)
    n3, n4 = st.columns(2)

    if "adherence_score" in patient.index:
        adh_val  = float(patient["adherence_score"])
        adh_flag = (
            '<p class="flag-bad">Below safe threshold</p>' if adh_val < 0.6
            else '<p class="flag-warn">Monitor closely</p>' if adh_val < 0.75
            else '<p class="flag-ok">Within range</p>'
        )
        n1.metric("Medication adherence", f"{int(adh_val*100)}%")
        n1.markdown(adh_flag, unsafe_allow_html=True)

    if "med_count" in patient.index:
        med_val  = int(patient["med_count"])
        med_flag = (
            '<p class="flag-bad">Very high — review needed</p>' if med_val >= 8
            else '<p class="flag-warn">Polypharmacy range</p>' if med_val >= 5
            else '<p class="flag-ok">Within range</p>'
        )
        n2.metric("Active medications", med_val)
        n2.markdown(med_flag, unsafe_allow_html=True)

    if "comorbidity_count" in patient.index:
        com_val  = int(patient["comorbidity_count"])
        com_flag = (
            '<p class="flag-bad">Complex patient</p>' if com_val >= 4
            else '<p class="flag-warn">Multiple conditions</p>' if com_val >= 2
            else '<p class="flag-ok">Low complexity</p>'
        )
        n3.metric("Chronic conditions", com_val)
        n3.markdown(com_flag, unsafe_allow_html=True)

    if "last_hospital" in patient.index:
        hosp_val  = int(patient["last_hospital"])
        hosp_flag = (
            '<p class="flag-warn">Recently hospitalised</p>' if hosp_val == 1
            else '<p class="flag-ok">No recent admission</p>'
        )
        n4.metric("Recent hospitalisation", "Yes" if hosp_val == 1 else "No")
        n4.markdown(hosp_flag, unsafe_allow_html=True)

# ── RIGHT — Chart ───────────────────────────────────────────
with col_right:

    st.markdown('<p class="sec-label">Patient vs population average</p>', unsafe_allow_html=True)

    pop_adh  = float(df["adherence_score"].mean()) if "adherence_score" in df.columns else 0.72
    pop_meds = float(df["med_count"].mean())        if "med_count"       in df.columns else 5.0
    pop_com  = float(df["comorbidity_count"].mean()) if "comorbidity_count" in df.columns else 2.5

    pat_adh  = float(patient.get("adherence_score",  0))
    pat_meds = float(patient.get("med_count",         0))
    pat_com  = float(patient.get("comorbidity_count", 0))

    bar_col = {
        "adh":  "#ef4444" if pat_adh  < 0.6 else "#f59e0b" if pat_adh  < 0.75 else "#22c55e",
        "meds": "#ef4444" if pat_meds >= 8   else "#f59e0b" if pat_meds >= 5   else "#22c55e",
        "com":  "#ef4444" if pat_com  >= 4   else "#f59e0b" if pat_com  >= 2   else "#22c55e",
    }

    categories = ["Adherence (%)", "Medications", "Comorbidities"]
    pat_vals   = [round(pat_adh*100, 1), round(pat_meds, 1), round(pat_com, 1)]
    avg_vals   = [round(pop_adh*100, 1), round(pop_meds,  1), round(pop_com,  1)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="This patient",
        x=categories, y=pat_vals,
        marker_color=[bar_col["adh"], bar_col["meds"], bar_col["com"]],
        opacity=0.9,
        text=[str(v) for v in pat_vals],
        textposition="outside",
        textfont=dict(size=12, family="IBM Plex Mono", color="#e6edf3")
    ))
    fig.add_trace(go.Bar(
        name="Population avg",
        x=categories, y=avg_vals,
        marker_color=["#30363d", "#30363d", "#30363d"],
        opacity=0.8,
        text=[str(v) for v in avg_vals],
        textposition="outside",
        textfont=dict(size=11, family="IBM Plex Mono", color="#8b949e")
    ))
    fig.update_layout(
        paper_bgcolor="#161b22",
        plot_bgcolor="#161b22",
        font=dict(family="IBM Plex Sans", color="#8b949e", size=12),
        barmode="group",
        height=220,
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(
            font=dict(color="#8b949e", size=11),
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            bgcolor="rgba(0,0,0,0)"
        ),
        xaxis=dict(showgrid=False, linecolor="#21262d", tickfont=dict(color="#8b949e")),
        yaxis=dict(gridcolor="#21262d", linecolor="#21262d", tickfont=dict(color="#8b949e")),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Risk score breakdown — horizontal bar
    st.markdown('<p class="sec-label">Risk score breakdown</p>', unsafe_allow_html=True)

    if "risk_score_C" in patient.index:
        score = float(patient["risk_score_C"])
        score_pct = round(score * 100, 1)

        adh_contrib  = round((1 - pat_adh) * 0.40 * 100, 1)
        med_contrib  = round((pat_meds / max(float(df["med_count"].max()), 1)) * 0.25 * 100, 1)
        hosp_contrib = round(float(patient.get("last_hospital", 0)) * 0.20 * 100, 1)
        com_contrib  = round((pat_com / max(float(df["comorbidity_count"].max()), 1)) * 0.15 * 100, 1)

        fig2 = go.Figure(go.Bar(
            x=[adh_contrib, med_contrib, hosp_contrib, com_contrib],
            y=["Adherence risk", "Medications", "Hospitalisation", "Comorbidities"],
            orientation="h",
            marker_color=["#ef4444", "#f59e0b", "#a78bfa", "#38bdf8"],
            text=[f"{v}%" for v in [adh_contrib, med_contrib, hosp_contrib, com_contrib]],
            textposition="outside",
            textfont=dict(size=11, family="IBM Plex Mono", color="#e6edf3")
        ))
        fig2.update_layout(
            paper_bgcolor="#161b22",
            plot_bgcolor="#161b22",
            font=dict(family="IBM Plex Sans", color="#8b949e", size=11),
            height=190,
            margin=dict(l=10, r=50, t=10, b=10),
            xaxis=dict(showgrid=False, showticklabels=False, linecolor="#21262d", range=[0, 30]),
            yaxis=dict(showgrid=False, linecolor="#21262d", tickfont=dict(color="#c9d1d9", size=11)),
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown(f"""
        <div style="background:#161b22; border:1px solid #21262d; border-radius:8px;
                    padding:10px 14px; display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:0.78rem; color:#8b949e;">Overall risk score</span>
            <span style="font-family:'IBM Plex Mono',monospace; font-size:1.2rem;
                         font-weight:500; color:{'#ff7b7b' if risk=='High' else '#ffc057' if risk=='Medium' else '#57d989'};">
                {score_pct}%
            </span>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# Footer
# -----------------------------
st.markdown("""
<div style="border-top:1px solid #21262d; margin-top:16px; padding-top:8px;">
    <p style="font-size:0.72rem; color:#8b949e; margin:0;">
        Clinical view · Prototype only · Synthetic data ·
        Not a substitute for clinical judgement · Not for clinical use
    </p>
</div>
""", unsafe_allow_html=True)
