import streamlit as st
import pandas as pd
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
# CSS
# -----------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
    .stApp { background-color: #f8f9fb; }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e8ecf2;
        border-radius: 10px;
        padding: 16px 20px;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.72rem !important;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #6b7280 !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 1.8rem !important;
        color: #111827 !important;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid #e8ecf2;
        border-radius: 10px;
    }

    /* Dividers */
    hr { border-color: #e8ecf2 !important; }

    /* Section label */
    .sec-label {
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #9ca3af;
        font-weight: 500;
        margin-bottom: 8px;
        margin-top: 4px;
    }

    /* Risk badges */
    .badge-high {
        background: #fef2f2; color: #991b1b;
        border: 1px solid #fca5a5;
        padding: 3px 12px; border-radius: 20px;
        font-size: 0.78rem; font-weight: 600;
        display: inline-block;
    }
    .badge-medium {
        background: #fffbeb; color: #92400e;
        border: 1px solid #fcd34d;
        padding: 3px 12px; border-radius: 20px;
        font-size: 0.78rem; font-weight: 600;
        display: inline-block;
    }
    .badge-low {
        background: #f0fdf4; color: #166534;
        border: 1px solid #86efac;
        padding: 3px 12px; border-radius: 20px;
        font-size: 0.78rem; font-weight: 600;
        display: inline-block;
    }

    /* Patient card */
    .patient-card {
        background: #ffffff;
        border: 1px solid #e8ecf2;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 16px;
    }
    .patient-card-high  { border-left: 4px solid #ef4444; }
    .patient-card-medium{ border-left: 4px solid #f59e0b; }
    .patient-card-low   { border-left: 4px solid #22c55e; }

    /* Action boxes */
    .action-high {
        background: #fef2f2; border: 1px solid #fca5a5;
        border-radius: 10px; padding: 14px 18px; margin-bottom: 16px;
    }
    .action-medium {
        background: #fffbeb; border: 1px solid #fcd34d;
        border-radius: 10px; padding: 14px 18px; margin-bottom: 16px;
    }
    .action-low {
        background: #f0fdf4; border: 1px solid #86efac;
        border-radius: 10px; padding: 14px 18px; margin-bottom: 16px;
    }
    .action-label-high   { color: #991b1b; font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600; margin-bottom: 6px; }
    .action-label-medium { color: #92400e; font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600; margin-bottom: 6px; }
    .action-label-low    { color: #166534; font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600; margin-bottom: 6px; }
    .action-text-high    { color: #b91c1c; font-size: 0.95rem; line-height: 1.5; }
    .action-text-medium  { color: #b45309; font-size: 0.95rem; line-height: 1.5; }
    .action-text-low     { color: #15803d; font-size: 0.95rem; line-height: 1.5; }

    /* Why box */
    .why-box {
        background: #f8f9fb; border: 1px solid #e8ecf2;
        border-radius: 10px; padding: 14px 18px; margin-bottom: 16px;
    }
    .why-text { font-size: 0.9rem; line-height: 1.65; color: #374151; }

    /* Confidence */
    .conf-agree    { background:#f0fdf4; border:1px solid #86efac; border-radius:8px; padding:10px 14px; font-size:0.85rem; color:#15803d; margin-bottom:16px; }
    .conf-disagree { background:#fffbeb; border:1px solid #fcd34d; border-radius:8px; padding:10px 14px; font-size:0.85rem; color:#b45309; margin-bottom:16px; }

    /* Number flag */
    .flag-bad  { color: #b91c1c; font-size: 0.75rem; font-weight: 500; margin-top: 2px; }
    .flag-warn { color: #b45309; font-size: 0.75rem; font-weight: 500; margin-top: 2px; }
    .flag-ok   { color: #15803d; font-size: 0.75rem; font-weight: 500; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# File path
# -----------------------------
DATA_PATH = Path("data/scored_data.csv")

# -----------------------------
# Data loading
# -----------------------------
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
        st.error("Risk data not found in file.")
        st.stop()

# Sort: High first, then Medium, then Low
tier_order = {"High": 0, "Medium": 1, "Low": 2}
df["_sort"] = df["final_risk"].map(tier_order)
df = df.sort_values(["_sort", "risk_score_C"], ascending=[True, False]).drop(columns=["_sort"])

# -----------------------------
# Plain English explanations
# -----------------------------
def plain_explanation(row):
    drivers = []
    if "med_count" in row.index and row["med_count"] >= 8:
        drivers.append(f"taking {int(row['med_count'])} medications (very high)")
    elif "med_count" in row.index and row["med_count"] >= 5:
        drivers.append(f"taking {int(row['med_count'])} medications (polypharmacy)")
    if "adherence_score" in row.index and row["adherence_score"] < 0.5:
        drivers.append(f"very low medication adherence ({int(row['adherence_score']*100)}%)")
    elif "adherence_score" in row.index and row["adherence_score"] < 0.7:
        drivers.append(f"below-target adherence ({int(row['adherence_score']*100)}%)")
    if "last_hospital" in row.index and row["last_hospital"] == 1:
        drivers.append("recent hospitalisation")
    if "comorbidity_count" in row.index and row["comorbidity_count"] >= 4:
        drivers.append(f"managing {int(row['comorbidity_count'])} chronic conditions (complex)")
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
            return "Schedule urgent comprehensive MTM session. Assess for deprescribing opportunities and interaction risks."
        else:
            return "High-priority outreach. Complete medication review and adherence assessment before next refill."
    elif risk == "Medium":
        if "last_hospital" in row.index and row["last_hospital"] == 1:
            return "Follow-up call within 2 weeks. Confirm medication changes after discharge."
        else:
            return "Standard MTM outreach at next scheduled interval. Monitor chronic disease management."
    else:
        return "Routine follow-up only. No urgent action required at this time."

# -----------------------------
# Header
# -----------------------------
st.markdown("""
<div style="padding: 20px 0 16px 0; border-bottom: 1px solid #e8ecf2; margin-bottom: 20px;">
    <span style="font-family:'IBM Plex Mono',monospace; font-size:0.65rem; text-transform:uppercase;
                 letter-spacing:0.12em; color:#9ca3af;">
        MTM Clinical Decision Support · Pharmacist View
    </span>
    <h1 style="font-size:1.7rem; font-weight:500; color:#111827; margin:4px 0 0 0;">
        Patient worklist
    </h1>
    <p style="color:#6b7280; font-size:0.88rem; margin-top:4px;">
        Patients sorted by risk level — highest priority first
    </p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Summary metrics
# -----------------------------
high_n   = int((df["final_risk"] == "High").sum())
medium_n = int((df["final_risk"] == "Medium").sum())
low_n    = int((df["final_risk"] == "Low").sum())
total_n  = len(df)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total patients",  total_n)
m2.metric("🔴 Need urgent review", high_n)
m3.metric("🟡 Monitor closely",    medium_n)
m4.metric("🟢 Routine follow-up",  low_n)

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------
# Filters
# -----------------------------
left_col, right_col = st.columns([1, 3])

with left_col:
    st.markdown('<p class="sec-label">Filter by risk level</p>', unsafe_allow_html=True)
    tier_filter = st.radio(
        "Risk tier",
        options=["All patients", "High only", "Medium only", "Low only"],
        label_visibility="collapsed"
    )
    st.markdown("<br>", unsafe_allow_html=True)
    if "last_hospital" in df.columns:
        hosp_only = st.checkbox("Recently hospitalised only")
    else:
        hosp_only = False

    if "all_agree" in df.columns:
        conf_only = st.checkbox("High confidence only (all models agree)")
    else:
        conf_only = False

    st.markdown("---")
    st.caption(f"Dataset: {total_n} patients · Synthetic data · Not for clinical use")

with right_col:
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
        st.warning("No patients match the selected filters.")
        st.stop()

    # Patient selector
    st.markdown('<p class="sec-label">Select a patient</p>', unsafe_allow_html=True)

    def patient_label(row):
        hosp_flag = " · Recently hospitalised" if "last_hospital" in row.index and row["last_hospital"] == 1 else ""
        adh = int(row["adherence_score"] * 100) if "adherence_score" in row.index else 0
        meds = int(row["med_count"]) if "med_count" in row.index else 0
        return f"{row['patient_id']}  [{row['final_risk']} risk]  —  {meds} meds · {adh}% adherence{hosp_flag}"

    patient_labels = [patient_label(row) for _, row in view_df.iterrows()]
    patient_ids    = view_df["patient_id"].tolist()

    selected_label = st.selectbox(
        "Select patient",
        options=patient_labels,
        label_visibility="collapsed"
    )
    selected_idx = patient_labels.index(selected_label)
    selected_id  = patient_ids[selected_idx]
    patient = view_df.loc[view_df["patient_id"] == selected_id].iloc[0]

    risk       = patient["final_risk"]
    risk_lower = risk.lower()

    # Patient header card
    age_str  = f"Age {int(patient['age'])}" if "age" in patient.index else ""
    meds_str = f"{int(patient['med_count'])} active medications" if "med_count" in patient.index else ""

    badge_html = f'<span class="badge-{risk_lower}">{risk} risk</span>'

    conf_html = ""
    if "all_agree" in patient.index:
        if bool(patient["all_agree"]):
            conf_html = '<div class="conf-agree">✅ High confidence — all models agree on this classification</div>'
        else:
            conf_html = '<div class="conf-disagree">⚠️ Models disagree — manual review recommended before acting</div>'

    st.markdown(f"""
    <div class="patient-card patient-card-{risk_lower}">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <span style="font-family:'IBM Plex Mono',monospace; font-size:1.2rem;
                             font-weight:500; color:#111827;">{selected_id}</span>
                <span style="margin-left:12px; color:#6b7280; font-size:0.88rem;">
                    {age_str} &nbsp;·&nbsp; {meds_str}
                </span>
            </div>
            {badge_html}
        </div>
    </div>
    {conf_html}
    """, unsafe_allow_html=True)

    # Recommended action
    action = clinical_action(patient) if "recommendation" not in patient.index else patient["recommendation"]
    st.markdown(f"""
    <div class="action-{risk_lower}">
        <div class="action-label-{risk_lower}">Recommended action</div>
        <div class="action-text-{risk_lower}">{action}</div>
    </div>
    """, unsafe_allow_html=True)

    # Why this risk level
    st.markdown('<p class="sec-label">Why this risk level?</p>', unsafe_allow_html=True)
    explanation = plain_explanation(patient) if "explanation" not in patient.index else patient["explanation"]
    st.markdown(f"""
    <div class="why-box">
        <div class="why-text">{explanation}</div>
    </div>
    """, unsafe_allow_html=True)

    # Key clinical numbers
    st.markdown('<p class="sec-label">Key clinical numbers</p>', unsafe_allow_html=True)
    n1, n2, n3, n4 = st.columns(4)

    if "adherence_score" in patient.index:
        adh_val = float(patient["adherence_score"])
        adh_flag = (
            '<p class="flag-bad">Below safe threshold</p>' if adh_val < 0.6
            else '<p class="flag-warn">Monitor closely</p>' if adh_val < 0.75
            else '<p class="flag-ok">Within range</p>'
        )
        n1.metric("Medication adherence", f"{int(adh_val*100)}%")
        n1.markdown(adh_flag, unsafe_allow_html=True)

    if "med_count" in patient.index:
        med_val = int(patient["med_count"])
        med_flag = (
            '<p class="flag-bad">Very high — review needed</p>' if med_val >= 8
            else '<p class="flag-warn">Polypharmacy range</p>' if med_val >= 5
            else '<p class="flag-ok">Within range</p>'
        )
        n2.metric("Active medications", med_val)
        n2.markdown(med_flag, unsafe_allow_html=True)

    if "comorbidity_count" in patient.index:
        com_val = int(patient["comorbidity_count"])
        com_flag = (
            '<p class="flag-bad">Complex patient</p>' if com_val >= 4
            else '<p class="flag-warn">Multiple conditions</p>' if com_val >= 2
            else '<p class="flag-ok">Low complexity</p>'
        )
        n3.metric("Chronic conditions", com_val)
        n3.markdown(com_flag, unsafe_allow_html=True)

    if "last_hospital" in patient.index:
        hosp_val = int(patient["last_hospital"])
        hosp_flag = (
            '<p class="flag-warn">Recently hospitalised</p>' if hosp_val == 1
            else '<p class="flag-ok">No recent admission</p>'
        )
        n4.metric("Recent hospitalisation", "Yes" if hosp_val == 1 else "No")
        n4.markdown(hosp_flag, unsafe_allow_html=True)

    # Comparison bars
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="sec-label">How this patient compares to the average</p>',
                unsafe_allow_html=True)

    import plotly.graph_objects as go

    pop_adh  = float(df["adherence_score"].mean()) if "adherence_score" in df.columns else 0.72
    pop_meds = float(df["med_count"].mean())       if "med_count" in df.columns else 5.0
    pop_com  = float(df["comorbidity_count"].mean()) if "comorbidity_count" in df.columns else 2.5

    pat_adh  = float(patient.get("adherence_score", 0))
    pat_meds = float(patient.get("med_count", 0))
    pat_com  = float(patient.get("comorbidity_count", 0))

    bar_colors = {
        "adh":  "#ef4444" if pat_adh < 0.6 else "#f59e0b" if pat_adh < 0.75 else "#22c55e",
        "meds": "#ef4444" if pat_meds >= 8 else "#f59e0b" if pat_meds >= 5 else "#22c55e",
        "com":  "#ef4444" if pat_com >= 4  else "#f59e0b" if pat_com >= 2  else "#22c55e",
    }

    categories = ["Adherence (%)", "Medications", "Comorbidities"]
    pat_vals   = [round(pat_adh * 100, 1), round(pat_meds, 1), round(pat_com, 1)]
    avg_vals   = [round(pop_adh * 100, 1), round(pop_meds, 1), round(pop_com, 1)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="This patient",
        x=categories,
        y=pat_vals,
        marker_color=[bar_colors["adh"], bar_colors["meds"], bar_colors["com"]],
        opacity=0.9,
        text=[f"{v}" for v in pat_vals],
        textposition="outside",
        textfont=dict(size=12, family="IBM Plex Mono")
    ))
    fig.add_trace(go.Bar(
        name="Population average",
        x=categories,
        y=avg_vals,
        marker_color=["#d1d5db", "#d1d5db", "#d1d5db"],
        opacity=0.6,
        text=[f"{v}" for v in avg_vals],
        textposition="outside",
        textfont=dict(size=11, family="IBM Plex Mono")
    ))
    fig.update_layout(
        paper_bgcolor="#f8f9fb",
        plot_bgcolor="#f8f9fb",
        font=dict(family="IBM Plex Sans", color="#6b7280", size=12),
        barmode="group",
        height=260,
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(font=dict(color="#6b7280", size=11), orientation="h",
                    yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False, linecolor="#e8ecf2"),
        yaxis=dict(gridcolor="#e8ecf2", linecolor="#e8ecf2"),
    )
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption(
    "Clinical view · Prototype only · Synthetic data · "
    "For pharmacist and MTM coordinator use · Not a substitute for clinical judgement"
)
