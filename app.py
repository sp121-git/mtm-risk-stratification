import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="MTM Risk Stratification System",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Custom CSS — clean clinical theme
# -----------------------------
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

    /* Global */
    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }

    /* Main background */
    .stApp {
        background-color: #0f1117;
        color: #e8eaf0;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161b27;
        border-right: 1px solid #2a3040;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a2035 0%, #1e2640 100%);
        border: 1px solid #2a3555;
        border-radius: 12px;
        padding: 16px 20px;
    }
    [data-testid="stMetricLabel"] {
        color: #8892a4 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    [data-testid="stMetricValue"] {
        color: #e8eaf0 !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 1.6rem !important;
    }

    /* Risk badge styling */
    .risk-high {
        background: linear-gradient(135deg, #7f1d1d, #991b1b);
        color: #fca5a5;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        display: inline-block;
        border: 1px solid #dc2626;
    }
    .risk-medium {
        background: linear-gradient(135deg, #78350f, #92400e);
        color: #fcd34d;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        display: inline-block;
        border: 1px solid #d97706;
    }
    .risk-low {
        background: linear-gradient(135deg, #064e3b, #065f46);
        color: #6ee7b7;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        display: inline-block;
        border: 1px solid #10b981;
    }

    /* Section headers */
    .section-header {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        color: #4a90d9;
        border-bottom: 1px solid #2a3555;
        padding-bottom: 8px;
        margin-bottom: 16px;
        margin-top: 8px;
    }

    /* Patient card */
    .patient-card {
        background: linear-gradient(135deg, #1a2035 0%, #1e2640 100%);
        border: 1px solid #2a3555;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 16px;
    }

    /* Alert boxes */
    .alert-agree {
        background: linear-gradient(135deg, #064e3b20, #065f4630);
        border: 1px solid #10b981;
        border-left: 4px solid #10b981;
        border-radius: 8px;
        padding: 12px 16px;
        color: #6ee7b7;
        font-size: 0.9rem;
    }
    .alert-disagree {
        background: linear-gradient(135deg, #78350f20, #92400e30);
        border: 1px solid #d97706;
        border-left: 4px solid #f59e0b;
        border-radius: 8px;
        padding: 12px 16px;
        color: #fcd34d;
        font-size: 0.9rem;
    }

    /* Gauge container */
    .gauge-label {
        text-align: center;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 2rem;
        font-weight: 600;
        color: #e8eaf0;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #161b27;
        border-bottom: 1px solid #2a3040;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #8892a4;
        border-radius: 6px 6px 0 0;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
        letter-spacing: 0.05em;
        padding: 8px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1a2035 !important;
        color: #4a90d9 !important;
        border-top: 2px solid #4a90d9 !important;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid #2a3040;
        border-radius: 8px;
    }

    /* Divider */
    hr {
        border-color: #2a3040 !important;
    }

    /* Sidebar labels */
    .sidebar-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #4a90d9;
        margin-bottom: 4px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Plotly dark theme helper
# -----------------------------
PLOT_THEME = dict(
    paper_bgcolor="#1a2035",
    plot_bgcolor="#1a2035",
    font=dict(family="IBM Plex Sans", color="#8892a4", size=12),
    title_font=dict(family="IBM Plex Mono", color="#e8eaf0", size=13),
    xaxis=dict(gridcolor="#2a3040", linecolor="#2a3040", tickfont=dict(color="#8892a4")),
    yaxis=dict(gridcolor="#2a3040", linecolor="#2a3040", tickfont=dict(color="#8892a4")),
    margin=dict(l=40, r=20, t=40, b=40)
)
RISK_COLORS = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#10b981"}

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
        st.error("Neither 'final_risk' nor 'risk_score_C' was found.")
        st.stop()

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown('<p class="sidebar-label">MTM System v2.0</p>', unsafe_allow_html=True)
    st.markdown("## 💊 Risk Dashboard")
    st.markdown("---")

    st.markdown('<p class="sidebar-label">ML Feature Importance</p>', unsafe_allow_html=True)
    st.caption("Logistic regression coefficients")

    coef_data = pd.DataFrame({
        "Feature": ["last_hospital", "med_count", "comorbidity_count", "adherence_score"],
        "Coefficient": [4.422, 2.697, 1.761, -3.017]
    }).sort_values("Coefficient", ascending=False)

    fig_coef = go.Figure(go.Bar(
        x=coef_data["Coefficient"],
        y=coef_data["Feature"],
        orientation="h",
        marker=dict(
            color=["#ef4444" if c > 0 else "#4a90d9" for c in coef_data["Coefficient"]],
            line=dict(width=0)
        ),
        text=[f"{c:+.3f}" for c in coef_data["Coefficient"]],
        textposition="outside",
        textfont=dict(family="IBM Plex Mono", size=10, color="#e8eaf0")
    ))
    fig_coef.update_layout(
        **PLOT_THEME,
        height=180,
        margin=dict(l=10, r=40, t=10, b=10),
        xaxis=dict(showgrid=False, zeroline=True, zerolinecolor="#2a3040"),
        yaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig_coef, use_container_width=True)

    st.markdown("---")
    st.markdown('<p class="sidebar-label">Filters</p>', unsafe_allow_html=True)

    risk_options = sorted(df["final_risk"].dropna().unique().tolist())
    selected_risks = st.multiselect("Risk tier", options=risk_options, default=risk_options)

    min_age = int(df["age"].min()) if "age" in df.columns else 0
    max_age = int(df["age"].max()) if "age" in df.columns else 100
    age_range = st.slider("Age range", min_age, max_age, (min_age, max_age))

    hospital_filter = st.selectbox("Recent hospitalization", ["All", "Yes", "No"])

    ml_filter = st.selectbox("ML vs Rule-based", ["All", "Agree", "Disagree"])

    st.markdown("---")
    st.caption(f"Dataset: {len(df)} patients · ROC-AUC: 0.998")

# -----------------------------
# Apply filters
# -----------------------------
filtered_df = df.copy()
if selected_risks:
    filtered_df = filtered_df[filtered_df["final_risk"].isin(selected_risks)]
if "age" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["age"].between(age_range[0], age_range[1])]
if hospital_filter == "Yes":
    filtered_df = filtered_df[filtered_df["last_hospital"] == 1]
elif hospital_filter == "No":
    filtered_df = filtered_df[filtered_df["last_hospital"] == 0]
if "tier_match" in filtered_df.columns:
    if ml_filter == "Agree":
        filtered_df = filtered_df[filtered_df["tier_match"] == True]
    elif ml_filter == "Disagree":
        filtered_df = filtered_df[filtered_df["tier_match"] == False]

# -----------------------------
# Header
# -----------------------------
st.markdown("""
<div style="padding: 24px 0 8px 0;">
    <span style="font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem;
                 text-transform: uppercase; letter-spacing: 0.15em; color: #4a90d9;">
        Clinical Decision Support · Prototype
    </span>
    <h1 style="font-family: 'IBM Plex Sans', sans-serif; font-size: 2rem;
               font-weight: 600; color: #e8eaf0; margin: 4px 0 0 0;">
        MTM Risk Stratification System
    </h1>
    <p style="color: #8892a4; font-size: 0.9rem; margin-top: 4px;">
        Rule-based scoring validated against logistic regression ML model
    </p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3 = st.tabs([
    "📊  OVERVIEW & CLINICAL DEPTH",
    "🤖  ML INSIGHTS",
    "🔍  PATIENT DETAIL"
])

# ══════════════════════════════════════════════
# TAB 1 — OVERVIEW & CLINICAL DEPTH
# ══════════════════════════════════════════════
with tab1:

    # --- Summary metrics ---
    st.markdown('<p class="section-header">Summary metrics</p>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total patients", len(filtered_df))
    c2.metric("🔴 High risk", int((filtered_df["final_risk"] == "High").sum()))
    c3.metric("🟡 Medium risk", int((filtered_df["final_risk"] == "Medium").sum()))
    c4.metric("🟢 Low risk", int((filtered_df["final_risk"] == "Low").sum()))
    c5.metric(
        "ML–Rule agreement",
        f"{filtered_df['tier_match'].mean():.0%}" if "tier_match" in filtered_df.columns and len(filtered_df) > 0 else "N/A"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Charts row 1 ---
    st.markdown('<p class="section-header">Risk distribution & population profile</p>', unsafe_allow_html=True)
    ch1, ch2, ch3 = st.columns(3)

    with ch1:
        risk_counts = filtered_df["final_risk"].value_counts().reset_index()
        risk_counts.columns = ["Risk Tier", "Count"]
        fig_pie = go.Figure(go.Pie(
            labels=risk_counts["Risk Tier"],
            values=risk_counts["Count"],
            hole=0.55,
            marker=dict(
                colors=[RISK_COLORS.get(r, "#8892a4") for r in risk_counts["Risk Tier"]],
                line=dict(color="#0f1117", width=3)
            ),
            textfont=dict(family="IBM Plex Mono", size=11),
        ))
        fig_pie.update_layout(
            **PLOT_THEME,
            title="Risk Tier Distribution",
            height=280,
            showlegend=True,
            legend=dict(font=dict(color="#8892a4", size=11))
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with ch2:
        if "age" in filtered_df.columns:
            fig_age = go.Figure()
            for tier, color in RISK_COLORS.items():
                subset = filtered_df[filtered_df["final_risk"] == tier]
                fig_age.add_trace(go.Histogram(
                    x=subset["age"],
                    name=tier,
                    marker_color=color,
                    opacity=0.75,
                    xbins=dict(size=5)
                ))
            fig_age.update_layout(
                **PLOT_THEME,
                title="Age Distribution by Risk Tier",
                barmode="overlay",
                height=280,
                legend=dict(font=dict(color="#8892a4", size=11))
            )
            st.plotly_chart(fig_age, use_container_width=True)

    with ch3:
        if "med_count" in filtered_df.columns:
            avg_by_risk = filtered_df.groupby("final_risk")[
                ["med_count", "comorbidity_count", "adherence_score"]
            ].mean().round(2).reset_index()

            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                name="Avg Medications",
                x=avg_by_risk["final_risk"],
                y=avg_by_risk["med_count"],
                marker_color="#4a90d9",
                yaxis="y"
            ))
            fig_bar.add_trace(go.Bar(
                name="Avg Comorbidities",
                x=avg_by_risk["final_risk"],
                y=avg_by_risk["comorbidity_count"],
                marker_color="#a78bfa",
                yaxis="y"
            ))
            fig_bar.update_layout(
                **PLOT_THEME,
                title="Avg Clinical Factors by Tier",
                barmode="group",
                height=280,
                legend=dict(font=dict(color="#8892a4", size=11))
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    # --- Charts row 2 ---
    st.markdown('<p class="section-header">Clinical relationships</p>', unsafe_allow_html=True)
    ch4, ch5 = st.columns(2)

    with ch4:
        fig_scatter = px.scatter(
            filtered_df,
            x="adherence_score",
            y="risk_score_C",
            color="final_risk",
            color_discrete_map=RISK_COLORS,
            size="med_count",
            hover_data=["patient_id", "med_count", "comorbidity_count"],
            title="Adherence vs Risk Score (bubble = med count)",
            labels={"adherence_score": "Adherence Score", "risk_score_C": "Risk Score"}
        )
        fig_scatter.update_layout(**PLOT_THEME, height=320,
                                   legend=dict(font=dict(color="#8892a4", size=11)))
        st.plotly_chart(fig_scatter, use_container_width=True)

    with ch5:
        # Hospitalization rate by risk tier
        if "last_hospital" in filtered_df.columns:
            hosp_rate = filtered_df.groupby("final_risk")["last_hospital"].mean().reset_index()
            hosp_rate.columns = ["Risk Tier", "Hospitalization Rate"]
            hosp_rate["Hospitalization Rate"] = (hosp_rate["Hospitalization Rate"] * 100).round(1)

            fig_hosp = go.Figure(go.Bar(
                x=hosp_rate["Risk Tier"],
                y=hosp_rate["Hospitalization Rate"],
                marker=dict(
                    color=[RISK_COLORS.get(r, "#8892a4") for r in hosp_rate["Risk Tier"]],
                    line=dict(width=0)
                ),
                text=[f"{v}%" for v in hosp_rate["Hospitalization Rate"]],
                textposition="outside",
                textfont=dict(family="IBM Plex Mono", size=12, color="#e8eaf0")
            ))
            fig_hosp.update_layout(
                **PLOT_THEME,
                title="Hospitalization Rate by Risk Tier (%)",
                height=320,
                yaxis=dict(title="% Recently Hospitalized", range=[0, 100])
            )
            st.plotly_chart(fig_hosp, use_container_width=True)

    # --- High-risk attention table ---
    st.markdown('<p class="section-header">🔴 Patients needing immediate attention</p>', unsafe_allow_html=True)
    urgent = filtered_df[
        (filtered_df["final_risk"] == "High") &
        (filtered_df.get("tier_match", pd.Series([True]*len(filtered_df))) == False)
    ] if "tier_match" in filtered_df.columns else filtered_df[filtered_df["final_risk"] == "High"]

    urgent_cols = [c for c in [
        "patient_id", "age", "med_count", "adherence_score",
        "comorbidity_count", "last_hospital", "risk_score_C",
        "ml_risk_prob", "recommendation"
    ] if c in urgent.columns]

    if len(urgent) == 0:
        st.info("No urgent flagged patients in current filter.")
    else:
        st.dataframe(
            urgent[urgent_cols].sort_values("risk_score_C", ascending=False).head(15),
            use_container_width=True, hide_index=True
        )

    # --- Full patient table ---
    st.markdown('<p class="section-header">Full patient list</p>', unsafe_allow_html=True)
    show_cols = [c for c in [
        "patient_id", "age", "med_count", "adherence_score",
        "comorbidity_count", "last_hospital", "risk_score_C",
        "final_risk", "ml_risk_prob", "ml_risk_tier", "tier_match"
    ] if c in filtered_df.columns]

    if len(filtered_df) == 0:
        st.warning("No patients match the selected filters.")
    else:
        st.dataframe(
            filtered_df[show_cols].sort_values("risk_score_C", ascending=False),
            use_container_width=True, hide_index=True
        )

# ══════════════════════════════════════════════
# TAB 2 — ML INSIGHTS
# ══════════════════════════════════════════════
with tab2:

    st.markdown('<p class="section-header">Model performance summary</p>', unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("ROC-AUC", "0.998")
    m2.metric("Accuracy", "98%")
    m3.metric("High-risk Recall", "86%")
    m4.metric("Tier Agreement", "86%")

    st.markdown("<br>", unsafe_allow_html=True)

    ml1, ml2 = st.columns(2)

    with ml1:
        st.markdown('<p class="section-header">ML probability distribution</p>', unsafe_allow_html=True)
        if "ml_risk_prob" in filtered_df.columns:
            fig_prob = go.Figure()
            for tier, color in RISK_COLORS.items():
                subset = filtered_df[filtered_df["final_risk"] == tier]
                fig_prob.add_trace(go.Histogram(
                    x=subset["ml_risk_prob"],
                    name=f"{tier} (rule-based)",
                    marker_color=color,
                    opacity=0.7,
                    xbins=dict(size=0.05)
                ))
            fig_prob.update_layout(
                **PLOT_THEME,
                title="ML High-Risk Probability by Rule-Based Tier",
                barmode="overlay",
                height=320,
                xaxis=dict(title="ML Probability", range=[0, 1]),
                legend=dict(font=dict(color="#8892a4", size=11))
            )
            st.plotly_chart(fig_prob, use_container_width=True)

    with ml2:
        st.markdown('<p class="section-header">Tier agreement breakdown</p>', unsafe_allow_html=True)
        if "tier_match" in filtered_df.columns:
            agree_counts = filtered_df.groupby(["final_risk", "tier_match"]).size().reset_index(name="count")
            agree_counts["status"] = agree_counts["tier_match"].map({True: "Agree", False: "Disagree"})

            fig_agree = px.bar(
                agree_counts,
                x="final_risk",
                y="count",
                color="status",
                color_discrete_map={"Agree": "#10b981", "Disagree": "#f59e0b"},
                title="ML vs Rule-Based Agreement by Tier",
                labels={"final_risk": "Rule-Based Tier", "count": "Patient Count"}
            )
            fig_agree.update_layout(
                **PLOT_THEME,
                height=320,
                legend=dict(font=dict(color="#8892a4", size=11))
            )
            st.plotly_chart(fig_agree, use_container_width=True)

    # --- Feature importance deep dive ---
    st.markdown('<p class="section-header">Feature importance — logistic regression coefficients</p>', unsafe_allow_html=True)
    fi1, fi2 = st.columns([1, 2])

    with fi1:
        coef_table = pd.DataFrame({
            "Feature": ["last_hospital", "med_count", "comorbidity_count", "adherence_score"],
            "Coefficient": [4.422, 2.697, 1.761, -3.017],
            "Direction": ["↑ Risk", "↑ Risk", "↑ Risk", "↓ Risk"]
        }).sort_values("Coefficient", ascending=False)
        st.dataframe(coef_table, use_container_width=True, hide_index=True)
        st.caption("Positive = increases High-risk probability. Negative = decreases it.")

    with fi2:
        fig_fi = go.Figure(go.Bar(
            x=coef_table["Coefficient"],
            y=coef_table["Feature"],
            orientation="h",
            marker=dict(
                color=["#ef4444" if c > 0 else "#4a90d9" for c in coef_table["Coefficient"]],
                line=dict(width=0)
            ),
            text=[f"{c:+.3f}" for c in coef_table["Coefficient"]],
            textposition="outside",
            textfont=dict(family="IBM Plex Mono", size=12, color="#e8eaf0")
        ))
        fig_fi.update_layout(
            **PLOT_THEME,
            title="Coefficient Magnitude — Stronger = More Influential",
            height=260,
            xaxis=dict(zeroline=True, zerolinecolor="#4a90d9", zerolinewidth=1.5),
        )
        st.plotly_chart(fig_fi, use_container_width=True)

    # --- ML vs Rule-based risk score comparison ---
    st.markdown('<p class="section-header">ML probability vs rule-based score comparison</p>', unsafe_allow_html=True)
    if "ml_risk_prob" in filtered_df.columns and "risk_score_C" in filtered_df.columns:
        fig_comp = px.scatter(
            filtered_df,
            x="risk_score_C",
            y="ml_risk_prob",
            color="final_risk",
            color_discrete_map=RISK_COLORS,
            symbol="tier_match" if "tier_match" in filtered_df.columns else None,
            hover_data=["patient_id", "ml_risk_tier", "final_risk"],
            title="Rule-Based Score vs ML Probability  (△ = disagreement)",
            labels={"risk_score_C": "Rule-Based Risk Score", "ml_risk_prob": "ML High-Risk Probability"}
        )
        fig_comp.update_layout(**PLOT_THEME, height=380,
                                legend=dict(font=dict(color="#8892a4", size=11)))
        st.plotly_chart(fig_comp, use_container_width=True)

    # --- Disagreement deep dive ---
    st.markdown('<p class="section-header">Disagreement cases — where ML and rule-based differ</p>', unsafe_allow_html=True)
    if "tier_match" in filtered_df.columns:
        disagree_df = filtered_df[filtered_df["tier_match"] == False]
        st.caption(f"{len(disagree_df)} patients flagged · These are clinical edge cases worth reviewing")
        disagree_cols = [c for c in [
            "patient_id", "age", "med_count", "adherence_score",
            "comorbidity_count", "last_hospital", "final_risk",
            "ml_risk_tier", "ml_risk_prob", "risk_score_C"
        ] if c in disagree_df.columns]
        st.dataframe(
            disagree_df[disagree_cols].sort_values("ml_risk_prob", ascending=False),
            use_container_width=True, hide_index=True
        )

# ══════════════════════════════════════════════
# TAB 3 — PATIENT DETAIL
# ══════════════════════════════════════════════
with tab3:

    if len(filtered_df) == 0:
        st.warning("No patients match the current filters.")
    else:
        # Patient selector
        st.markdown('<p class="section-header">Select patient</p>', unsafe_allow_html=True)
        selected_patient = st.selectbox(
            "Patient ID",
            options=filtered_df["patient_id"].tolist(),
            label_visibility="collapsed"
        )

        patient = filtered_df.loc[filtered_df["patient_id"] == selected_patient].iloc[0]
        risk = patient["final_risk"]
        risk_color = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#10b981"}.get(risk, "#8892a4")

        # --- Patient header card ---
        badge_class = f"risk-{risk.lower()}"
        st.markdown(f"""
        <div class="patient-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-family: 'IBM Plex Mono', monospace; font-size: 1.4rem;
                                 font-weight: 600; color: #e8eaf0;">{selected_patient}</span>
                    {'<span style="margin-left: 12px; color: #8892a4; font-size: 0.9rem;">Age: ' + str(int(patient['age'])) + '</span>' if 'age' in patient.index else ''}
                </div>
                <span class="{badge_class}">{risk} RISK</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # --- Risk gauge ---
        col_gauge, col_details = st.columns([1, 2])

        with col_gauge:
            st.markdown('<p class="section-header">Risk gauge</p>', unsafe_allow_html=True)
            score = float(patient.get("risk_score_C", 0))
            ml_prob = float(patient.get("ml_risk_prob", 0)) if "ml_risk_prob" in patient.index else None

            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=round(score * 100, 1),
                title=dict(text="Rule-Based Risk Score", font=dict(color="#8892a4", size=12)),
                number=dict(suffix="%", font=dict(
                    family="IBM Plex Mono", color=risk_color, size=36
                )),
                gauge=dict(
                    axis=dict(range=[0, 100], tickcolor="#2a3040",
                              tickfont=dict(color="#8892a4", size=10)),
                    bar=dict(color=risk_color, thickness=0.3),
                    bgcolor="#1a2035",
                    borderwidth=0,
                    steps=[
                        dict(range=[0, 50], color="#1e2640"),
                        dict(range=[50, 80], color="#2a2a1a"),
                        dict(range=[80, 100], color="#2a1a1a"),
                    ],
                    threshold=dict(
                        line=dict(color="#e8eaf0", width=2),
                        thickness=0.8,
                        value=round(score * 100, 1)
                    )
                )
            ))
            fig_gauge.update_layout(
                paper_bgcolor="#1a2035",
                font=dict(family="IBM Plex Sans", color="#8892a4"),
                height=240,
                margin=dict(l=20, r=20, t=40, b=10)
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

            if ml_prob is not None:
                fig_gauge2 = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=round(ml_prob * 100, 1),
                    title=dict(text="ML High-Risk Probability", font=dict(color="#8892a4", size=12)),
                    number=dict(suffix="%", font=dict(
                        family="IBM Plex Mono", color="#a78bfa", size=36
                    )),
                    gauge=dict(
                        axis=dict(range=[0, 100], tickcolor="#2a3040",
                                  tickfont=dict(color="#8892a4", size=10)),
                        bar=dict(color="#a78bfa", thickness=0.3),
                        bgcolor="#1a2035",
                        borderwidth=0,
                        steps=[
                            dict(range=[0, 50], color="#1e2640"),
                            dict(range=[50, 80], color="#221a35"),
                            dict(range=[80, 100], color="#2a1a40"),
                        ],
                    )
                ))
                fig_gauge2.update_layout(
                    paper_bgcolor="#1a2035",
                    font=dict(family="IBM Plex Sans", color="#8892a4"),
                    height=240,
                    margin=dict(l=20, r=20, t=40, b=10)
                )
                st.plotly_chart(fig_gauge2, use_container_width=True)

        with col_details:
            st.markdown('<p class="section-header">Clinical snapshot</p>', unsafe_allow_html=True)

            # Driver bar chart
            driver_features = {
                "Medication Count": ("med_count", df["med_count"].mean()),
                "Comorbidities": ("comorbidity_count", df["comorbidity_count"].mean()),
                "Adherence Score": ("adherence_score", df["adherence_score"].mean()),
            }

            patient_vals, avg_vals, labels = [], [], []
            for label, (col, avg) in driver_features.items():
                if col in patient.index:
                    patient_vals.append(float(patient[col]))
                    avg_vals.append(float(avg))
                    labels.append(label)

            if labels:
                fig_drivers = go.Figure()
                fig_drivers.add_trace(go.Bar(
                    name="This patient",
                    x=labels,
                    y=patient_vals,
                    marker_color=risk_color,
                    opacity=0.9
                ))
                fig_drivers.add_trace(go.Bar(
                    name="Population avg",
                    x=labels,
                    y=avg_vals,
                    marker_color="#4a90d9",
                    opacity=0.5
                ))
                fig_drivers.update_layout(
                    **PLOT_THEME,
                    title="Patient vs Population Average",
                    barmode="group",
                    height=240,
                    legend=dict(font=dict(color="#8892a4", size=11))
                )
                st.plotly_chart(fig_drivers, use_container_width=True)

            # Clinical facts
            detail_col1, detail_col2 = st.columns(2)
            with detail_col1:
                if "med_count" in patient.index:
                    st.metric("Medications", int(patient["med_count"]),
                              delta=f"{int(patient['med_count']) - int(df['med_count'].mean()):+d} vs avg")
                if "comorbidity_count" in patient.index:
                    st.metric("Comorbidities", int(patient["comorbidity_count"]),
                              delta=f"{int(patient['comorbidity_count']) - int(df['comorbidity_count'].mean()):+d} vs avg")
            with detail_col2:
                if "adherence_score" in patient.index:
                    st.metric("Adherence", f"{float(patient['adherence_score']):.0%}",
                              delta=f"{float(patient['adherence_score']) - float(df['adherence_score'].mean()):+.0%} vs avg")
                if "last_hospital" in patient.index:
                    st.metric("Recent Hospitalization",
                              "Yes" if int(patient["last_hospital"]) == 1 else "No")

        # --- Explanation and recommendation ---
        st.markdown("<br>", unsafe_allow_html=True)
        exp_col, rec_col = st.columns(2)

        with exp_col:
            st.markdown('<p class="section-header">Risk explanation</p>', unsafe_allow_html=True)
            explanation = patient.get("explanation", "No explanation available.")
            st.markdown(f"""
            <div class="patient-card">
                <p style="color: #8892a4; font-size: 0.8rem; margin: 0 0 6px 0;">MAIN DRIVERS</p>
                <p style="color: #e8eaf0; font-size: 0.95rem; margin: 0;">{explanation}</p>
            </div>
            """, unsafe_allow_html=True)

        with rec_col:
            st.markdown('<p class="section-header">Recommended MTM action</p>', unsafe_allow_html=True)
            recommendation = patient.get("recommendation", "No recommendation available.")
            st.markdown(f"""
            <div class="patient-card" style="border-color: {risk_color}40; border-left: 4px solid {risk_color};">
                <p style="color: #8892a4; font-size: 0.8rem; margin: 0 0 6px 0;">ACTION</p>
                <p style="color: #e8eaf0; font-size: 0.95rem; margin: 0;">{recommendation}</p>
            </div>
            """, unsafe_allow_html=True)

        # --- ML comparison ---
        st.markdown('<p class="section-header">ML model comparison</p>', unsafe_allow_html=True)
        ml_c1, ml_c2, ml_c3 = st.columns(3)

        with ml_c1:
            if "ml_risk_prob" in patient.index:
                st.metric("ML High-Risk Probability", f"{float(patient['ml_risk_prob']):.1%}")
        with ml_c2:
            if "ml_risk_tier" in patient.index:
                st.metric("ML Risk Tier", patient["ml_risk_tier"])
        with ml_c3:
            if "tier_match" in patient.index:
                match = bool(patient["tier_match"])
                st.metric("Systems agree?", "✅ Yes" if match else "⚠️ No")

        if "tier_match" in patient.index:
            match = bool(patient["tier_match"])
            if match:
                st.markdown(f"""
                <div class="alert-agree">
                    ✅ Both the rule-based system and ML model classify this patient as
                    <strong>{patient['final_risk']}</strong> risk. High confidence classification.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="alert-disagree">
                    ⚠️ <strong>Disagreement detected.</strong> Rule-based: <strong>{patient['final_risk']}</strong>
                    · ML model: <strong>{patient.get('ml_risk_tier', 'N/A')}</strong>.
                    This patient is a clinical edge case and may benefit from manual pharmacist review.
                </div>
                """, unsafe_allow_html=True)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption(
    "Prototype only · Synthetic data · "
    "Rule-based scoring validated against logistic regression ML model · "
    "ROC-AUC: 0.998 · Tier agreement: 86% · Not for clinical use"
)
