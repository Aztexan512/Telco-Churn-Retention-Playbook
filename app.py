"""
Telecom Churn -- Cross-Industry Retention Dashboard
Author: Luciano Casillas
Version: 4.0
---
Single-file Streamlit app. To run:
    streamlit run app.py

To edit: open app.py in VS Code. Each tab has its own render_ function.
Search for the function name to jump to that section.

    render_kpi_header     -- persistent KPI row above all tabs
    render_sidebar        -- all filters
    render_overview       -- Tab 1
    render_churn_drivers  -- Tab 2
    render_model_risk     -- Tab 3
    render_financial_impact -- Tab 4
    render_insurance_playbook -- Tab 5
    render_recommendations  -- Tab 6
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Telecom Churn -- Retention Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# COLOR PALETTE -- Option A: Steel Blue Analogous
# ─────────────────────────────────────────────
NAVY       = "#0A3360"   # Primary -- headings, key callout bars, KPI values
STEEL_700  = "#405E7C"   # Secondary -- supporting bars, labels
BLUE_700   = "#0077B3"   # Tertiary -- accent lines, links, badges
BLUE_500   = "#4EBEE5"   # Quaternary -- light chart series, neutral baseline bars
STEEL_300  = "#D1E2E5"   # Light fill -- card backgrounds, borders
STEEL_100  = "#F4F9FA"   # Very light -- section backgrounds
WHITE      = "#FFFFFF"
BLACK      = "#2D2D2D"   # All body text
GRAY_700   = "#707070"   # Secondary labels only
GRAY_300   = "#CCCCCC"   # Borders, grid lines
GREEN_700  = "#08CAA9"   # Positive / retained / recovered
GREEN_900  = "#067462"   # Strong positive
ORANGE_700 = "#FF8A39"   # Caution / warning

CHART_FONT = dict(family="Georgia, 'Times New Roman', serif", color=NAVY)

def base_layout(height=340):
    return dict(
        height=height,
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        font=CHART_FONT,
        margin=dict(l=16, r=16, t=44, b=44),
    )


# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main, .block-container {{
    background-color: {WHITE} !important;
    color: {BLACK} !important;
    font-size: 14px !important;
}}
[data-testid="stSidebar"], [data-testid="stSidebarContent"] {{
    background-color: {WHITE} !important;
    border-right: 1px solid #E0E0E0 !important;
}}
.stTabs [data-baseweb="tab-list"] {{
    background-color: {WHITE} !important;
    border-bottom: 2px solid #E0E0E0 !important;
    gap: 4px;
}}
.stTabs [data-baseweb="tab"] {{
    background-color: {WHITE} !important;
    color: {GRAY_700} !important;
    border: none !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 10px 20px !important;
    border-radius: 0 !important;
}}
.stTabs [aria-selected="true"] {{
    background-color: {WHITE} !important;
    color: {NAVY} !important;
    border-bottom: 3px solid {BLUE_700} !important;
    font-weight: 700 !important;
}}
.stTabs [data-baseweb="tab-panel"] {{
    background-color: {WHITE} !important;
    padding-top: 1.4rem !important;
}}

/* KPI cards with left blue accent */
[data-testid="stMetric"] {{
    background-color: {WHITE} !important;
    border: 1px solid #E0E0E0 !important;
    border-left: 4px solid {BLUE_700} !important;
    border-radius: 0 10px 10px 0 !important;
    padding: 14px 18px !important;
}}
[data-testid="stMetricLabel"] {{
    font-size: 12px !important;
    font-weight: 700 !important;
    color: {GRAY_700} !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}}
[data-testid="stMetricValue"] {{
    font-size: 26px !important;
    font-weight: 700 !important;
    color: {NAVY} !important;
}}
[data-testid="stMetricDelta"] {{
    font-size: 13px !important;
    color: {BLACK} !important;
}}
[data-testid="stSidebar"] label {{
    font-size: 13px !important;
    font-weight: 700 !important;
    color: {NAVY} !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
}}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div {{
    font-size: 13px !important;
    color: {BLACK} !important;
}}
[data-testid="stPlotlyChart"] {{
    background-color: {WHITE} !important;
    border-radius: 8px !important;
}}
[data-baseweb="tag"] {{
    background-color: {BLUE_700} !important;
    color: {WHITE} !important;
}}

/* Insight strip */
.insight-strip {{
    background-color: {WHITE};
    border-left: 4px solid {BLUE_700};
    border-top: 1px solid #E0E0E0;
    border-right: 1px solid #E0E0E0;
    border-bottom: 1px solid #E0E0E0;
    border-radius: 0 8px 8px 0;
    padding: 16px 20px;
    margin: 0 0 16px 0;
}}
.insight-label {{
    font-size: 13px;
    font-weight: 700;
    color: {NAVY};
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 8px;
}}
.insight-text {{
    font-size: 15px;
    font-weight: 600;
    color: {NAVY};
    line-height: 1.6;
}}

/* Section header with blue left accent */
.section-header {{
    border-left: 4px solid {BLUE_700};
    padding: 8px 0 8px 14px;
    margin: 20px 0 14px 0;
    background: {STEEL_100};
    border-radius: 0 6px 6px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}}
.section-header-title {{
    font-size: 13px;
    font-weight: 700;
    color: {NAVY};
    text-transform: uppercase;
    letter-spacing: 0.06em;
}}
.section-subtitle {{
    font-size: 13px;
    color: {BLACK};
    margin: 0 0 16px 0;
    line-height: 1.6;
}}

/* Info icon tooltip */
.info-icon {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    border: 2px solid {BLUE_700};
    color: {BLUE_700};
    font-size: 11px;
    font-weight: 700;
    cursor: help;
    flex-shrink: 0;
    line-height: 1;
}}

/* Filter summary pill */
.filter-pill {{
    display: inline-block;
    background: {STEEL_100};
    border: 1px solid {STEEL_300};
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 12px;
    color: {NAVY};
    margin: 2px 4px 2px 0;
    font-weight: 600;
}}
.filter-label {{
    font-size: 11px;
    color: {GRAY_700};
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-right: 4px;
}}

/* Divider */
.divider {{ border: none; border-top: 1px solid #E0E0E0; margin: 20px 0 16px 0; }}

/* Recommendation cards */
.rec-card {{
    background: {WHITE};
    border: 1px solid #E0E0E0;
    border-left: 4px solid {BLUE_700};
    border-radius: 0 10px 10px 0;
    padding: 18px 22px;
    margin-bottom: 14px;
}}
.rec-tier {{
    font-size: 11px;
    font-weight: 700;
    color: {GRAY_700};
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 4px;
}}
.rec-title {{
    font-size: 16px;
    font-weight: 700;
    color: {NAVY};
    margin-bottom: 10px;
}}
.rec-badges {{
    margin-bottom: 12px;
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}}
.rec-value {{
    display: inline-block;
    font-size: 14px;
    font-weight: 700;
    color: {GREEN_900};
    background: #E8F5F2;
    padding: 4px 12px;
    border-radius: 20px;
}}
.rec-effort {{
    display: inline-block;
    font-size: 14px;
    font-weight: 700;
    color: {NAVY};
    background: {STEEL_300};
    padding: 4px 12px;
    border-radius: 20px;
}}
.rec-body {{
    font-size: 14px;
    color: {BLACK};
    line-height: 1.7;
    margin-bottom: 10px;
}}
.rec-evidence {{
    font-size: 13px;
    color: {NAVY};
    font-style: italic;
    border-left: 2px solid {STEEL_300};
    padding-left: 10px;
}}

/* Tile cards (equal height) */
.tile-card {{
    background: {STEEL_100};
    border: 1px solid {STEEL_300};
    border-left: 4px solid {BLUE_700};
    border-radius: 0 10px 10px 0;
    padding: 18px 20px;
    height: 100%;
    min-height: 160px;
}}
.tile-label {{
    font-size: 12px;
    font-weight: 700;
    color: {GRAY_700};
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 12px;
}}
.tile-body {{
    font-size: 14px;
    color: {BLACK};
    line-height: 2.2;
}}

h1, h2, h3 {{ color: {NAVY} !important; }}
p, li, td, th {{ color: {BLACK}; font-size: 14px; }}
#MainMenu, footer {{ visibility: hidden; }}
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: #F8F8F8; }}
::-webkit-scrollbar-thumb {{ background: {GRAY_300}; border-radius: 3px; }}
[data-testid="stSlider"] label {{
    font-size: 13px !important;
    font-weight: 700 !important;
    color: {NAVY} !important;
    text-transform: uppercase !important;
}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data/telco_churn_225k_v120.csv")
    df["billing_call_resolved"] = pd.to_numeric(df["billing_call_resolved"], errors="coerce")
    df["tech_issue_resolved"]   = pd.to_numeric(df["tech_issue_resolved"],   errors="coerce")

    rng = np.random.default_rng(42)
    df["estimated_margin_pct"] = rng.uniform(0.15, 0.35, len(df))
    df["cltv"] = (df["monthly_charges"] * 24 * df["estimated_margin_pct"]).round(2)

    df["tenure_bucket"] = pd.cut(
        df["tenure_months"],
        bins=[0, 12, 24, 36, 48, 72],
        labels=["1-12 Mo", "13-24 Mo", "25-36 Mo", "37-48 Mo", "49-72 Mo"],
    )
    df["promo_label"]   = df["is_on_promo"].map({1: "On Promo", 0: "Full Rate"})
    df["autopay_label"] = df["is_autopay"].map({1: "Autopay", 0: "Manual Pay"})

    df["is_at_risk"] = (
        (df["churn"] == 1)
        & (
            ((df["first_60d_billing_call"] == 1) & (df["billing_call_resolved"] == 0))
            | ((df["first_60d_tech_call"]   == 1) & (df["tech_issue_resolved"]   == 0))
        )
    ).astype(int)

    def churn_type(row):
        if row["churn"] == 0:
            return "Retained"
        if row["is_at_risk"] == 1:
            return "Preventable"
        if row["contract_type"] == "month_to_month" or row["is_on_promo"] == 1:
            return "Structural"
        return "Undetermined"

    df["churn_type"] = df.apply(churn_type, axis=1)

    # Derive join year-month from tenure (snapshot reference: Dec 2024)
    _ref = pd.Timestamp("2024-12-01")
    df["join_date"] = df["tenure_months"].apply(
        lambda m: _ref - pd.DateOffset(months=int(m) - 1)
    )
    df["join_ym"] = (df["join_date"].dt.year * 100 + df["join_date"].dt.month).astype(int)

    return df


# ─────────────────────────────────────────────
# SESSION STATE -- filter reset support
# ─────────────────────────────────────────────
def init_session_state(df):
    defaults = {
        "contract_sel": sorted(df["contract_type"].unique()),
        "segment_sel":  sorted(df["service_segment"].unique()),
        "channel_sel":  sorted(df["sales_channel"].unique()),
        "tenure_range": (1, 72),
        "promo_sel":    ["On Promo", "Full Rate"],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    return defaults


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def insight(label, text):
    st.markdown(
        f'<div class="insight-strip">'
        f'<div class="insight-label">{label}</div>'
        f'<div class="insight-text">{text}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

def section_header(title, tooltip_text=None):
    icon_html = ""
    if tooltip_text:
        safe = tooltip_text.replace("'", "&#39;").replace('"', "&quot;")
        icon_html = (
            f'<span class="info-icon" title="{safe}">i</span>'
        )
    st.markdown(
        f'<div class="section-header">'
        f'<div class="section-header-title">{title}</div>'
        f'{icon_html}'
        f'</div>',
        unsafe_allow_html=True,
    )

def section_subtitle(text):
    st.markdown(f'<div class="section-subtitle">{text}</div>', unsafe_allow_html=True)

def filter_summary_block(df, df_full, contract_sel, segment_sel,
                          channel_sel, tenure_range, promo_sel):
    """Shows active filter state as pills. Used in Financial Impact tab."""
    contract_labels = {"month_to_month": "Month-to-Month",
                       "one_year": "One Year", "two_year": "Two Year"}
    segment_labels  = {"cable_only": "Cable Only", "internet_only": "Internet Only",
                       "internet_plus_other": "Internet + Other", "mobile": "Mobile"}
    channel_labels  = {"agent_call_center": "Inbound Sales", "online": "Online",
                       "store": "Store", "third_party_retailer": "Third-Party Retailer"}

    all_contracts = sorted(df_full["contract_type"].unique())
    all_segments  = sorted(df_full["service_segment"].unique())
    all_channels  = sorted(df_full["sales_channel"].unique())

    def pills(selected, all_opts, label_map):
        if sorted(selected) == sorted(all_opts):
            return '<span class="filter-pill">All</span>'
        return "".join(
            f'<span class="filter-pill">{label_map.get(v, v)}</span>'
            for v in selected
        )

    tenure_str = (
        "All" if tenure_range == (1, 72)
        else f"{tenure_range[0]} to {tenure_range[1]} Months"
    )
    promo_str = (
        "All" if sorted(promo_sel) == ["Full Rate", "On Promo"]
        else " + ".join(promo_sel) if promo_sel else "None"
    )

    rows = [
        ("Contract Type",  pills(contract_sel, all_contracts, contract_labels)),
        ("Service Segment", pills(segment_sel, all_segments, segment_labels)),
        ("Sales Channel",   pills(channel_sel, all_channels, channel_labels)),
        ("Tenure Range",    f'<span class="filter-pill">{tenure_str}</span>'),
        ("Promo Status",    f'<span class="filter-pill">{promo_str}</span>'),
    ]
    html = (
        f"<div style='background:{STEEL_100};border:1px solid {STEEL_300};"
        f"border-left:4px solid {BLUE_700};border-radius:0 8px 8px 0;"
        f"padding:14px 18px;margin-bottom:14px;'>"
        f"<div style='font-size:12px;font-weight:700;color:{GRAY_700};"
        f"text-transform:uppercase;letter-spacing:0.05em;margin-bottom:10px;'>"
        f"Active Filters</div>"
    )
    for label, pills_html in rows:
        html += (
            f"<div style='margin-bottom:5px;'>"
            f"<span class='filter-label'>{label}:</span>{pills_html}</div>"
        )
    html += f"</div>"
    st.markdown(html, unsafe_allow_html=True)

def bar_chart(x, y, title, xlabel="", ylabel="Churn Rate (%)",
              colors=None, height=320, text_vals=None,
              horizontal=False, y_max=None):
    if colors is None:
        colors = [NAVY] * len(x)
    if text_vals is None:
        text_vals = [f"{v:.2f}%" for v in y]

    computed_max = (y_max if y_max is not None
                    else (max(y) * 1.25 if y else 1))
    fig = go.Figure()
    if horizontal:
        fig.add_trace(go.Bar(
            y=x, x=y, orientation="h",
            marker_color=colors,
            text=text_vals, textposition="outside",
            textfont=dict(size=12, color=NAVY),
        ))
        fig.update_layout(
            **base_layout(height),
            title=dict(text=title, font=dict(size=15, color=NAVY), x=0),
            xaxis_title=ylabel, yaxis_title=xlabel,
            yaxis=dict(autorange="reversed", gridcolor=GRAY_300,
                       tickfont=dict(size=12, color=BLACK)),
            xaxis=dict(range=[0, computed_max], gridcolor=GRAY_300,
                       tickfont=dict(size=12, color=BLACK)),
            showlegend=False,
        )
    else:
        fig.add_trace(go.Bar(
            x=x, y=y,
            marker_color=colors,
            text=text_vals, textposition="outside",
            textfont=dict(size=12, color=NAVY),
        ))
        fig.update_layout(
            **base_layout(height),
            title=dict(text=title, font=dict(size=15, color=NAVY), x=0),
            xaxis_title=xlabel, yaxis_title=ylabel,
            yaxis=dict(range=[0, computed_max], gridcolor=GRAY_300,
                       tickfont=dict(size=12, color=BLACK)),
            xaxis=dict(gridcolor=GRAY_300, tickfont=dict(size=12, color=BLACK)),
            showlegend=False,
        )
    return fig

def sparkline(values, color=BLUE_700, height=36):
    fig = go.Figure(go.Scatter(
        y=values, mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy",
        fillcolor=f"rgba(0,119,179,0.10)",
    ))
    fig.update_layout(
        height=height,
        paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        showlegend=False,
    )
    return fig


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar(df):
    st.sidebar.markdown(
        f"<div style='font-size:16px;font-weight:700;color:{NAVY};"
        f"margin-bottom:6px;'>Filters</div>"
        f"<div style='font-size:12px;color:{GRAY_700};margin-bottom:16px;'>"
        f"All filters apply across every tab.</div>",
        unsafe_allow_html=True,
    )

    contract_opts   = sorted(df["contract_type"].unique())
    contract_labels = {"month_to_month": "Month-to-Month",
                       "one_year": "One Year", "two_year": "Two Year"}
    contract_sel = st.sidebar.multiselect(
        "Contract Type",
        options=contract_opts, default=st.session_state["contract_sel"],
        format_func=lambda x: contract_labels.get(x, x),
        key="contract_sel",
    )

    segment_opts   = sorted(df["service_segment"].unique())
    segment_labels = {
        "cable_only":          "Cable Only",
        "internet_only":       "Internet Only",
        "internet_plus_other": "Internet + Other",
        "mobile":              "Mobile",
    }
    seg_tooltip = (
        "Internet Only: Broadband (DSL or Fiber), no phone service. | "
        "Internet + Other: Broadband plus a landline phone package. | "
        "Mobile: Broadband plus a mobile/cellular line. | "
        "Cable Only: Cable TV only -- no internet, no phone."
    )
    st.sidebar.markdown(
        f"<div style='font-size:13px;font-weight:700;color:{NAVY};"
        f"text-transform:uppercase;letter-spacing:0.04em;margin-bottom:4px;'>"
        f"Service Segment "
        f'<span class="info-icon" title="{seg_tooltip}">i</span>'
        f"</div>",
        unsafe_allow_html=True,
    )
    segment_sel = st.sidebar.multiselect(
        "Service Segment",
        options=segment_opts, default=st.session_state["segment_sel"],
        format_func=lambda x: segment_labels.get(x, x),
        label_visibility="collapsed",
        key="segment_sel",
    )

    channel_opts   = sorted(df["sales_channel"].unique())
    channel_labels = {
        "agent_call_center":    "Inbound Sales",
        "online":               "Online",
        "store":                "Store",
        "third_party_retailer": "Third-Party Retailer",
    }
    channel_sel = st.sidebar.multiselect(
        "Sales Channel",
        options=channel_opts, default=st.session_state["channel_sel"],
        format_func=lambda x: channel_labels.get(x, x),
        key="channel_sel",
    )

    tenure_range = st.sidebar.slider(
        "Tenure Range (Months)",
        min_value=1, max_value=72,
        value=st.session_state["tenure_range"],
        step=1, key="tenure_range",
    )

    promo_opts = ["On Promo", "Full Rate"]
    promo_sel  = st.sidebar.multiselect(
        "Promo Status",
        options=promo_opts, default=st.session_state["promo_sel"],
        key="promo_sel",
    )

    # Date range filter -- month/year slider (covers full 72-month tenure range)
    _months = [f"{m:02d}/{y}" for y in range(2019, 2025) for m in range(1, 13)]
    date_month_range = st.sidebar.select_slider(
        "Join Date Range",
        options=_months,
        value=(_months[0], _months[-1]),
        key="date_month_range",
    )

    st.sidebar.markdown(
        f"<hr style='border-color:#E0E0E0;margin:16px 0;'>",
        unsafe_allow_html=True,
    )

    # Apply filters
    def _ym(s):
        m, y = s.split("/")
        return int(y) * 100 + int(m)

    start_ym, end_ym = _ym(date_month_range[0]), _ym(date_month_range[1])

    mask = (
        df["contract_type"].isin(contract_sel)
        & df["service_segment"].isin(segment_sel)
        & df["sales_channel"].isin(channel_sel)
        & df["tenure_months"].between(tenure_range[0], tenure_range[1])
        & df["join_ym"].between(start_ym, end_ym)
    )
    if promo_sel and len(promo_sel) < 2:
        if "On Promo" in promo_sel:
            mask &= df["is_on_promo"] == 1
        else:
            mask &= df["is_on_promo"] == 0

    df_f = df[mask].copy()
    pct  = len(df_f) / len(df) * 100

    st.sidebar.markdown(
        f"<div style='font-size:13px;color:{BLACK};'>"
        f"Showing <b style='color:{NAVY};'>{len(df_f):,}</b> of "
        f"{len(df):,} customers ({pct:.2f}%)</div>",
        unsafe_allow_html=True,
    )
    st.sidebar.progress(min(pct / 100, 1.0))

    if st.sidebar.button("Reset All Filters", use_container_width=True):
        defaults = init_session_state(df)
        for k, v in defaults.items():
            st.session_state[k] = v
        st.rerun()

    return df_f, contract_sel, segment_sel, channel_sel, tenure_range, promo_sel


# ─────────────────────────────────────────────
# PERSISTENT KPI HEADER
# ─────────────────────────────────────────────
def render_kpi_header(df, df_full):
    churned_count = int(df["churn"].sum())
    churn_rate    = df["churn"].mean() * 100
    base_rate     = df_full["churn"].mean() * 100
    delta_pts     = churn_rate - base_rate

    at_risk_df    = df[df["is_at_risk"] == 1]
    cltv_at_risk  = at_risk_df["cltv"].sum()
    at_risk_count = len(at_risk_df)
    at_risk_pct   = at_risk_count / churned_count * 100 if churned_count > 0 else 0

    spark_data = (df.groupby("tenure_bucket", observed=True)["churn"]
                  .mean().mul(100).tolist())
    if len(spark_data) < 2:
        spark_data = [churn_rate] * 5

    kpi_tooltip = (
        "• Overall Churn Rate: Percentage of customers who left during the selected period.\n"
        "• Churned Customers: Total number of customers who have disconnected or left.\n"
        "• CLTV at Risk: The estimated 24-month contribution margin from At-Risk Customers "
        "with unresolved service issues -- revenue recoverable with a retention program.\n"
        "• Preventable Share: The portion of churned customers whose departure was linked to "
        "an unresolved billing or technical issue in their first 60 days."
    )

    section_header("Key Performance Indicators", kpi_tooltip)

    # 4-column layout: each column has metric + sparkline side by side
    c1, c2, c3, c4 = st.columns(4)

    def kpi_with_spark(col, label, value, delta, delta_color,
                       spark_vals, spark_color, spark_key):
        with col:
            st.metric(label, value, delta=delta, delta_color=delta_color)
            st.plotly_chart(
                sparkline(spark_vals, spark_color),
                use_container_width=True,
                config={"displayModeBar": False},
                key=spark_key,
            )

    kpi_with_spark(c1, "Overall Churn Rate",
                   f"{churn_rate:.2f}%",
                   f"{delta_pts:+.2f} pts vs. baseline", "inverse",
                   spark_data, NAVY, "spark1")

    spark2 = (df.groupby("tenure_bucket", observed=True)["churn"]
              .sum().tolist())
    kpi_with_spark(c2, "Churned Customers",
                   f"{churned_count:,}",
                   f"of {len(df):,} customers", "off",
                   spark2, STEEL_700, "spark2")

    spark3 = (df.groupby("tenure_bucket", observed=True)["cltv"]
              .sum().div(1e6).tolist())
    kpi_with_spark(c3, "CLTV at Risk (24-Month)",
                   f"${cltv_at_risk/1e6:.2f}M",
                   "At-Risk Customers only", "off",
                   spark3, BLUE_700, "spark3")

    spark4 = (df.groupby("tenure_bucket", observed=True)["is_at_risk"]
              .mean().mul(100).tolist())
    kpi_with_spark(c4, "Preventable Share",
                   f"{at_risk_pct:.2f}%",
                   "Unresolved service issues", "off",
                   spark4, GREEN_700, "spark4")

    st.markdown(
        f"<hr style='border:none;border-top:2px solid {BLUE_700};"
        f"margin:10px 0 0 0;'>",
        unsafe_allow_html=True,
    )
    return churned_count, churn_rate, cltv_at_risk, at_risk_count, at_risk_pct


# ─────────────────────────────────────────────
# TAB 1 -- OVERVIEW
# ─────────────────────────────────────────────
def render_overview(df, churn_rate, cltv_at_risk, at_risk_pct):
    m2m_rate = (df[df["contract_type"] == "month_to_month"]["churn"].mean() * 100
                if len(df[df["contract_type"] == "month_to_month"]) > 0 else 0)

    insight("Key Finding",
        f"Month-to-Month customers churn at {m2m_rate:.2f}% -- the single largest driver "
        f"of CLTV at risk. Preventable churn represents {at_risk_pct:.2f}% of all churned "
        f"customers and ${cltv_at_risk/1e6:.2f}M in recoverable customer value.")

    col_a, col_b = st.columns([2, 3])

    with col_a:
        donut_tooltip = (
            "Retained: Customers who remained active during the selected period. | "
            "Preventable: Churned customers who had at least one unresolved billing or "
            "technical issue in their first 60 days -- a service failure, not a pricing "
            "or contract decision. | "
            "Structural: Churned customers whose departure is tied to contract type or "
            "pricing mechanics (Month-to-Month contracts, promo-to-full-rate transitions) "
            "rather than a service event. | "
            "Undetermined: Churned customers on annual or two-year contracts at full rate "
            "with no logged service issues -- the available data signals do not point to "
            "a clear cause."
        )
        section_header("Churn Composition", donut_tooltip)

        type_counts = df["churn_type"].value_counts()
        color_map   = {
            "Retained":     STEEL_300,
            "Preventable":  NAVY,
            "Structural":   ORANGE_700,
            "Undetermined": GRAY_300,
        }
        churned_total = int(df["churn"].sum())
        fig_donut = go.Figure(go.Pie(
            labels=list(type_counts.index),
            values=list(type_counts.values),
            hole=0.60,
            marker_colors=[color_map.get(l, GRAY_300) for l in type_counts.index],
            textinfo="percent",
            textposition="outside",
            textfont=dict(size=13, color=BLACK),
            hovertemplate="%{label}: %{value:,} customers (%{percent:.2%})<extra></extra>",
        ))
        fig_donut.update_layout(
            **base_layout(310),
            title=dict(text="Churn Composition", font=dict(size=15, color=NAVY), x=0),
            showlegend=True,
            legend=dict(
                orientation="h", x=0.5, xanchor="center",
                y=-0.22, font=dict(size=12, color=BLACK),
            ),
            annotations=[dict(
                text=f"{churned_total:,}<br>churned",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=14, color=NAVY), xanchor="center",
            )],
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_b:
        section_header("Churn Rate by Contract Type")
        ct = df.groupby("contract_type").agg(
            total=("churn", "count"),
            churned=("churn", "sum"),
            rate=("churn", "mean"),
        ).reset_index()
        ct_labels = {"month_to_month": "Month-to-Month",
                     "one_year": "One Year", "two_year": "Two Year"}
        ct["label"] = ct["contract_type"].map(ct_labels)
        ct["rate_pct"] = ct["rate"] * 100

        # Distinct colors per contract type
        palette = {"Month-to-Month": NAVY, "One Year": STEEL_700, "Two Year": BLUE_500}
        colors  = [palette.get(l, BLUE_700) for l in ct["label"]]

        # Custom hover: "90,351 out of 124,190 Month-to-Month customers churned"
        hover = [
            f"<b>{row['label']}</b><br>"
            f"{int(row['churned']):,} out of {int(row['total']):,} "
            f"{row['label']} customers churned<br>"
            f"Churn Rate: {row['rate_pct']:.2f}%<extra></extra>"
            for _, row in ct.iterrows()
        ]

        shared_max = ct["rate_pct"].max() * 1.25
        fig_ct = go.Figure(go.Bar(
            x=ct["label"], y=ct["rate_pct"],
            marker_color=colors,
            text=[f"{v:.2f}%" for v in ct["rate_pct"]],
            textposition="outside",
            textfont=dict(size=12, color=NAVY),
            hovertemplate=hover,
            customdata=list(zip(ct["churned"], ct["total"])),
        ))
        fig_ct.add_hline(
            y=churn_rate, line_dash="dash",
            line_color=GRAY_300, line_width=1.5,
            annotation_text=f"Avg {churn_rate:.2f}%",
            annotation_font_size=11, annotation_font_color=GRAY_700,
        )
        fig_ct.update_layout(
            **base_layout(310),
            title=dict(text="Churn Rate by Contract Type",
                       font=dict(size=15, color=NAVY), x=0),
            yaxis_title="Churn Rate (%)",
            yaxis=dict(range=[0, shared_max], gridcolor=GRAY_300,
                       tickfont=dict(size=12, color=BLACK)),
            xaxis=dict(gridcolor=GRAY_300, tickfont=dict(size=12, color=BLACK)),
            showlegend=False,
        )
        st.plotly_chart(fig_ct, use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    col_d, col_e, col_f = st.columns(3)

    with col_d:
        st.markdown(
            f"<div class='tile-card'>"
            f"<div class='tile-label'>Top Churn Drivers (SHAP Ranked)</div>"
            f"<div class='tile-body'>"
            f"<b style='color:{NAVY};'>1. Contract Type</b><br>"
            f"<span style='font-size:13px;color:{GRAY_700};'>"
            f"Month-to-Month: 72.75% vs. 24% annual (3x gap)</span><br><br>"
            f"<b style='color:{NAVY};'>2. Early Service Friction</b><br>"
            f"<span style='font-size:13px;color:{GRAY_700};'>"
            f"Technical unresolved: 70.99% vs. 46.35% no friction</span><br><br>"
            f"<b style='color:{NAVY};'>3. No Autopay Enrollment</b><br>"
            f"<span style='font-size:13px;color:{GRAY_700};'>"
            f"Manual pay: 57.11% vs. 42.88% autopay (14.2 pt gap)</span>"
            f"</div></div>",
            unsafe_allow_html=True,
        )

    with col_e:
        model_tooltip = (
            "ROC AUC: Measures how well the model separates churned from retained customers. "
            "A score of 0.84 means the model correctly ranks a random churned customer above "
            "a random retained customer 84% of the time. Random guessing scores 0.50. | "
            "Top Decile Lift 1.84x: The highest-risk 10% of customers churn at nearly "
            "double the average rate -- meaning outreach to this group is almost twice as "
            "efficient as random contact. | "
            "Top 20% Captures 35.2%: Contacting just the top 20% of highest-risk customers "
            "reaches more than 1 in 3 of all customers who will eventually churn."
        )
        st.markdown(
            f"<div class='tile-card'>"
            f"<div class='tile-label'>Model Performance Summary "
            f'<span class="info-icon" title="{model_tooltip}">i</span>'
            f"</div>"
            f"<div class='tile-body'>"
            f"ROC AUC <b style='color:{NAVY};'>0.84</b><br>"
            f"<span style='font-size:13px;color:{GRAY_700};'>"
            f"Model ranks churned above retained 84% of the time</span><br><br>"
            f"Top Decile Lift <b style='color:{NAVY};'>1.84x</b><br>"
            f"<span style='font-size:13px;color:{GRAY_700};'>"
            f"Top 10% risk segment churns at nearly 2x the average</span><br><br>"
            f"Top 20% Captures <b style='color:{NAVY};'>35.2%</b><br>"
            f"<span style='font-size:13px;color:{GRAY_700};'>"
            f"Reach 1 in 3 churners by contacting 1 in 5 customers</span>"
            f"</div></div>",
            unsafe_allow_html=True,
        )

    with col_f:
        st.markdown(
            f"<div class='tile-card'>"
            f"<div class='tile-label'>Auto Insurance Connection</div>"
            f"<div style='font-size:14px;color:{BLACK};line-height:1.75;'>"
            f"Every driver identified here maps directly to a retention lever in auto "
            f"insurance. Contract type parallels policy term length. Early service friction "
            f"parallels first-60-day claims experience. Autopay enrollment parallels EFT "
            f"and auto-renewal setup.<br><br>"
            f"<span style='color:{BLUE_700};font-weight:700;'>"
            f"See the Insurance Playbook tab for the full translation.</span>"
            f"</div></div>",
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────
# TAB 2 -- CHURN DRIVERS
# ─────────────────────────────────────────────
def render_churn_drivers(df):
    tab_tooltip = (
        "This tab breaks down the key behavioral and contract factors driving churn. "
        "Use the sidebar filters to explore how patterns shift across contract types, "
        "service segments, sales channels, and tenure ranges. "
        "CLTV (Customer Lifetime Value): The estimated 24-month contribution margin "
        "per customer, used to weigh the financial importance of each segment."
    )

    # No Friction, Billing Resolved, Technical Unresolved
    tech_unres_churn = (
        df[(df["first_60d_tech_call"] == 1) & (df["tech_issue_resolved"] == 0)]
        ["churn"].mean() * 100
    ) if len(df[(df["first_60d_tech_call"] == 1) & (df["tech_issue_resolved"] == 0)]) > 0 else 0

    no_fric_churn = (
        df[(df["first_60d_billing_call"] == 0) & (df["first_60d_tech_call"] == 0)]
        ["churn"].mean() * 100
    )
    billing_res_churn = (
        df[(df["first_60d_billing_call"] == 1) & (df["billing_call_resolved"] == 1)]
        ["churn"].mean() * 100
    )

    tech_gap  = tech_unres_churn - no_fric_churn
    tech_cnt  = len(df[(df["first_60d_tech_call"] == 1) &
                       (df["tech_issue_resolved"] == 0) & (df["churn"] == 1)])

    # ── Key Finding first ────────────────────
    insight("Key Finding -- Contract and Friction Drivers",
        f"Month-to-Month contracts are the top churn driver at "
        f"{df[df['contract_type']=='month_to_month']['churn'].mean()*100:.2f}% vs. "
        f"{df[df['contract_type']=='two_year']['churn'].mean()*100:.2f}% for Two-Year contracts. "
        f"Customers with an unresolved technical issue in their first 60 days churn at "
        f"{tech_unres_churn:.2f}% vs. {no_fric_churn:.2f}% for those with no friction -- "
        f"a {tech_gap:.2f} point gap representing {tech_cnt:,} recoverable churned customers.")

    section_header("Contract, Pricing, and Friction Drivers", tab_tooltip)

    # Shared y-axis max for rows 1 and 2
    ct_vals   = df.groupby("contract_type")["churn"].mean().mul(100).tolist()
    promo_vals = df.groupby("promo_label")["churn"].mean().mul(100).tolist()
    row1_max  = max(ct_vals + promo_vals) * 1.25

    fric_vals = [no_fric_churn, billing_res_churn, tech_unres_churn]
    tb_vals   = df.groupby("tenure_bucket", observed=True)["churn"].mean().mul(100).tolist()
    row2_max  = max(fric_vals + tb_vals) * 1.25

    col_a, col_b = st.columns(2)
    with col_a:
        ct = df.groupby("contract_type").agg(
            total=("churn", "count"),
            churned=("churn", "sum"),
            rate=("churn", "mean"),
        ).reset_index()
        ct_labels = {"month_to_month": "Month-to-Month",
                     "one_year": "One Year", "two_year": "Two Year"}
        ct["label"]    = ct["contract_type"].map(ct_labels)
        ct["rate_pct"] = ct["rate"] * 100
        palette        = {"Month-to-Month": NAVY, "One Year": STEEL_700, "Two Year": BLUE_500}
        colors_ct      = [palette.get(l, BLUE_700) for l in ct["label"]]
        hover_ct = [
            f"<b>{row['label']}</b><br>"
            f"{int(row['churned']):,} out of {int(row['total']):,} "
            f"{row['label']} customers churned<br>"
            f"Churn Rate: {row['rate_pct']:.2f}%<extra></extra>"
            for _, row in ct.iterrows()
        ]
        fig1 = go.Figure(go.Bar(
            x=ct["label"], y=ct["rate_pct"],
            marker_color=colors_ct,
            text=[f"{v:.2f}%" for v in ct["rate_pct"]],
            textposition="outside",
            textfont=dict(size=12, color=NAVY),
            hovertemplate=hover_ct,
        ))
        fig1.update_layout(
            **base_layout(320),
            title=dict(text="Churn Rate by Contract Type",
                       font=dict(size=15, color=NAVY), x=0),
            yaxis_title="Churn Rate (%)",
            yaxis=dict(range=[0, row1_max], gridcolor=GRAY_300,
                       tickfont=dict(size=12, color=BLACK)),
            xaxis=dict(gridcolor=GRAY_300, tickfont=dict(size=12, color=BLACK)),
            showlegend=False,
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        promo   = df.groupby("promo_label").agg(
            total=("churn", "count"),
            churned=("churn", "sum"),
            rate=("churn", "mean"),
        )
        promo["rate_pct"] = promo["rate"] * 100
        colsp   = [NAVY if v == promo["rate_pct"].max() else STEEL_700 for v in promo["rate_pct"].values]
        hover_promo = [
            f"<b>{idx}</b><br>"
            f"{int(row['churned']):,} out of {int(row['total']):,} "
            f"{idx} customers churned<br>"
            f"Churn Rate: {row['rate_pct']:.2f}%<extra></extra>"
            for idx, row in promo.iterrows()
        ]
        fig2 = go.Figure(go.Bar(
            x=list(promo.index), y=list(promo["rate_pct"].values),
            marker_color=colsp,
            text=[f"{v:.2f}%" for v in promo["rate_pct"].values],
            textposition="outside",
            textfont=dict(size=12, color=NAVY),
            hovertemplate=hover_promo,
        ))
        fig2.update_layout(
            **base_layout(320),
            title=dict(text="Churn Rate by Promo Status",
                       font=dict(size=15, color=NAVY), x=0),
            yaxis_title="Churn Rate (%)",
            yaxis=dict(range=[0, row1_max], gridcolor=GRAY_300,
                       tickfont=dict(size=12, color=BLACK)),
            xaxis=dict(gridcolor=GRAY_300, tickfont=dict(size=12, color=BLACK)),
            showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)

    col_c, col_d = st.columns(2)
    with col_c:
        labels_f = ["No Friction", "Billing Resolved", "Technical Unresolved"]
        vals_f   = [no_fric_churn, billing_res_churn, tech_unres_churn]

        # Counts for hover text
        no_fric_total    = len(df[(df["first_60d_billing_call"] == 0) & (df["first_60d_tech_call"] == 0)])
        no_fric_churned  = int(df[(df["first_60d_billing_call"] == 0) & (df["first_60d_tech_call"] == 0)]["churn"].sum())
        bill_res_total   = len(df[(df["first_60d_billing_call"] == 1) & (df["billing_call_resolved"] == 1)])
        bill_res_churned = int(df[(df["first_60d_billing_call"] == 1) & (df["billing_call_resolved"] == 1)]["churn"].sum())
        tech_unr_total   = len(df[(df["first_60d_tech_call"] == 1) & (df["tech_issue_resolved"] == 0)])
        tech_unr_churned = int(df[(df["first_60d_tech_call"] == 1) & (df["tech_issue_resolved"] == 0)]["churn"].sum())

        hover_f = [
            f"<b>No Friction</b><br>{no_fric_churned:,} out of {no_fric_total:,} No Friction customers churned<br>Churn Rate: {no_fric_churn:.2f}%<extra></extra>",
            f"<b>Billing Resolved</b><br>{bill_res_churned:,} out of {bill_res_total:,} Billing Resolved customers churned<br>Churn Rate: {billing_res_churn:.2f}%<extra></extra>",
            f"<b>Technical Unresolved</b><br>{tech_unr_churned:,} out of {tech_unr_total:,} Technical Unresolved customers churned<br>Churn Rate: {tech_unres_churn:.2f}%<extra></extra>",
        ]
        # No Friction = neutral baseline (Blue 500), Billing Resolved = positive (Green),
        # Technical Unresolved = key concern (Navy)
        colors_f = [BLUE_500, GREEN_700, NAVY]
        fig3 = go.Figure(go.Bar(
            x=labels_f, y=vals_f,
            marker_color=colors_f,
            text=[f"{v:.2f}%" for v in vals_f],
            textposition="outside",
            textfont=dict(size=12, color=NAVY),
            hovertemplate=hover_f,
        ))
        fig3.update_layout(
            **base_layout(320),
            title=dict(text="Early Friction Impact on Churn (First 60 Days)",
                       font=dict(size=15, color=NAVY), x=0),
            yaxis_title="Churn Rate (%)",
            yaxis=dict(range=[0, row2_max], gridcolor=GRAY_300,
                       tickfont=dict(size=12, color=BLACK)),
            xaxis=dict(gridcolor=GRAY_300, tickfont=dict(size=12, color=BLACK)),
            showlegend=False,
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        tb_agg = df.groupby("tenure_bucket", observed=True).agg(
            total=("churn", "count"),
            churned=("churn", "sum"),
            rate=("churn", "mean"),
        )
        tb_agg["rate_pct"] = tb_agg["rate"] * 100
        colors_t = [NAVY if v == tb_agg["rate_pct"].max() else
                    ORANGE_700 if v > tb_agg["rate_pct"].mean() else BLUE_700
                    for v in tb_agg["rate_pct"].values]
        hover_tb = [
            f"<b>{idx}</b><br>"
            f"{int(row['churned']):,} out of {int(row['total']):,} "
            f"{idx} customers churned<br>"
            f"Churn Rate: {row['rate_pct']:.2f}%<extra></extra>"
            for idx, row in tb_agg.iterrows()
        ]
        fig4 = go.Figure(go.Bar(
            x=list(tb_agg.index.astype(str)), y=list(tb_agg["rate_pct"].values),
            marker_color=colors_t,
            text=[f"{v:.2f}%" for v in tb_agg["rate_pct"].values],
            textposition="outside",
            textfont=dict(size=12, color=NAVY),
            hovertemplate=hover_tb,
        ))
        fig4.update_layout(
            **base_layout(320),
            title=dict(text="Churn Rate by Tenure Bucket",
                       font=dict(size=15, color=NAVY), x=0),
            yaxis_title="Churn Rate (%)",
            yaxis=dict(range=[0, row2_max], gridcolor=GRAY_300,
                       tickfont=dict(size=12, color=BLACK)),
            xaxis=dict(gridcolor=GRAY_300, tickfont=dict(size=12, color=BLACK)),
            showlegend=False,
        )
        st.plotly_chart(fig4, use_container_width=True)

    # ── Segment, Channel, Tenure analysis ────
    seg = df.groupby("service_segment").agg(
        churn_pct=("churn", lambda x: x.mean() * 100),
        avg_cltv=("cltv", "mean"),
        count=("churn", "count"),
    ).reset_index()
    seg_labels = {"cable_only": "Cable Only", "internet_only": "Internet Only",
                  "internet_plus_other": "Internet + Other", "mobile": "Mobile"}
    seg["label"] = seg["service_segment"].map(seg_labels)
    high_seg     = seg.loc[seg["avg_cltv"].idxmax()]

    insight("Key Finding -- Segment, Channel, and Tenure Analysis",
        f"{high_seg['label']} carries the highest average CLTV (${high_seg['avg_cltv']:.0f}) "
        f"with a {high_seg['churn_pct']:.2f}% churn rate. Customers in their first 12 months "
        f"churn at the highest rate across all tenure groups, making early engagement the "
        f"highest-leverage point for any retention investment.")

    section_header("Segment, Channel, and Tenure Analysis")

    col_e, col_f, col_g = st.columns(3)

    with col_e:
        section_subtitle("Which segment has the highest financial risk per customer lost?")
        colors_s = [NAVY, STEEL_700, BLUE_700, BLUE_500]
        fig5     = go.Figure()
        for i, row in seg.iterrows():
            fig5.add_trace(go.Scatter(
                x=[row["churn_pct"]], y=[row["avg_cltv"]],
                mode="markers+text", name=row["label"],
                text=[row["label"]], textposition="top center",
                textfont=dict(size=12, color=NAVY),
                marker=dict(
                    size=row["count"] / 2500,
                    color=colors_s[i % len(colors_s)],
                    opacity=0.8, line=dict(width=1, color=WHITE),
                ),
                hovertemplate=(
                    f"<b>{row['label']}</b><br>"
                    f"Churn Rate: {row['churn_pct']:.2f}%<br>"
                    f"Avg CLTV: ${row['avg_cltv']:.0f}<br>"
                    f"Customers: {row['count']:,}<extra></extra>"
                ),
            ))
        fig5.update_layout(
            **base_layout(320),
            title=dict(text="Segment Priority Matrix",
                       font=dict(size=15, color=NAVY), x=0),
            xaxis_title="Churn Rate (%)", yaxis_title="Avg CLTV ($)",
            xaxis=dict(gridcolor=GRAY_300, tickfont=dict(size=12, color=BLACK),
                       range=[
                           seg["churn_pct"].min() - 3,
                           seg["churn_pct"].max() + 3,
                       ]),
            yaxis=dict(gridcolor=GRAY_300, tickfont=dict(size=12, color=BLACK),
                       range=[
                           seg["avg_cltv"].min() - 15,
                           seg["avg_cltv"].max() + 25,
                       ]),
            showlegend=False,
        )
        st.plotly_chart(fig5, use_container_width=True)

    with col_f:
        section_subtitle("Does the highest-churn channel also carry the highest customer value?")
        ch = df.groupby("sales_channel").agg(
            churn_pct=("churn", lambda x: x.mean() * 100),
            avg_cltv=("cltv", "mean"),
            total=("churn", "count"),
            churned=("churn", "sum"),
        ).reset_index()
        ch_labels = {"agent_call_center": "Inbound Sales", "online": "Online",
                     "store": "Store", "third_party_retailer": "Third-Party"}
        ch["label"] = ch["sales_channel"].map(ch_labels)

        hover_ch = [
            f"<b>{row['label']}</b><br>"
            f"{int(row['churned']):,} out of {int(row['total']):,} "
            f"{row['label']} customers churned<br>"
            f"Churn Rate: {row['churn_pct']:.2f}%<extra></extra>"
            for _, row in ch.iterrows()
        ]

        fig6 = make_subplots(specs=[[{"secondary_y": True}]])
        fig6.add_trace(go.Bar(
            x=ch["label"], y=ch["churn_pct"],
            name="Churn Rate (%)",
            marker_color=BLUE_700, opacity=0.85,
            text=[f"{v:.2f}%" for v in ch["churn_pct"]],
            textposition="outside",
            textfont=dict(size=12, color=NAVY),
            hovertemplate=hover_ch,
        ), secondary_y=False)
        fig6.add_trace(go.Scatter(
            x=ch["label"], y=ch["avg_cltv"],
            name="Avg CLTV ($)",
            mode="lines+markers",
            line=dict(color=NAVY, width=2.5),
            marker=dict(size=9, color=NAVY),
            hovertemplate="<b>%{x}</b><br>Avg CLTV: $%{y:.2f}<extra></extra>",
        ), secondary_y=True)
        fig6.update_layout(
            **base_layout(320),
            title=dict(text="Churn Rate + Avg CLTV by Sales Channel",
                       font=dict(size=15, color=NAVY), x=0),
            legend=dict(orientation="h", x=0.5, xanchor="center",
                        y=-0.25, font=dict(size=12, color=BLACK)),
        )
        fig6.update_yaxes(title_text="Churn Rate (%)", secondary_y=False,
                          gridcolor=GRAY_300, tickfont=dict(size=12, color=BLACK),
                          range=[0, 60])
        fig6.update_yaxes(title_text="Avg CLTV ($)", secondary_y=True,
                          tickfont=dict(size=12, color=BLACK),
                          range=[0, 358], tickformat=".0f")
        st.plotly_chart(fig6, use_container_width=True)

    with col_g:
        section_subtitle("At which tenure stage is the financial impact of churn highest?")
        rw = df.groupby("tenure_bucket", observed=True).agg(
            total=("churn", "count"),
            churned=("churn", "sum"),
            churn_rate=("churn", lambda x: x.mean() * 100),
            cltv_lost=("cltv", lambda x: x[df.loc[x.index, "churn"] == 1].sum() / 1000),
        ).reset_index()
        colors_rw = [NAVY if v == rw["churn_rate"].max() else BLUE_700
                     for v in rw["churn_rate"]]
        hover_rw = [
            f"<b>{row['tenure_bucket']}</b><br>"
            f"{int(row['churned']):,} out of {int(row['total']):,} "
            f"{row['tenure_bucket']} customers churned<br>"
            f"Churn Rate: {row['churn_rate']:.2f}%<extra></extra>"
            for _, row in rw.iterrows()
        ]
        fig7 = make_subplots(specs=[[{"secondary_y": True}]])
        fig7.add_trace(go.Bar(
            x=rw["tenure_bucket"].astype(str), y=rw["churn_rate"],
            name="Churn Rate (%)", marker_color=colors_rw, opacity=0.85,
            text=[f"{v:.2f}%" for v in rw["churn_rate"]],
            textposition="outside",
            textfont=dict(size=12, color=NAVY),
            hovertemplate=hover_rw,
        ), secondary_y=False)
        fig7.add_trace(go.Scatter(
            x=rw["tenure_bucket"].astype(str), y=rw["cltv_lost"],
            name="CLTV Lost ($K)", mode="lines+markers",
            line=dict(color=ORANGE_700, width=2.5),
            marker=dict(size=9, color=ORANGE_700),
        ), secondary_y=True)
        fig7.update_layout(
            **base_layout(320),
            title=dict(text="Revenue-Weighted Tenure View",
                       font=dict(size=15, color=NAVY), x=0),
            legend=dict(orientation="h", x=0.5, xanchor="center",
                        y=-0.25, font=dict(size=12, color=BLACK)),
        )
        fig7.update_yaxes(title_text="Churn Rate (%)", secondary_y=False,
                          gridcolor=GRAY_300, tickfont=dict(size=12, color=BLACK))
        fig7.update_yaxes(title_text="CLTV Lost ($K)", secondary_y=True,
                          tickfont=dict(size=12, color=BLACK))
        st.plotly_chart(fig7, use_container_width=True)


# ─────────────────────────────────────────────
# TAB 3 -- MODEL + RISK
# ─────────────────────────────────────────────
def render_model_risk(df):
    model_tab_tooltip = (
        "This tab shows how well the predictive model identifies customers at risk "
        "of churning before they leave. Use it to understand model accuracy, which "
        "factors matter most, and which customers to prioritize for outreach. "
        "XGBoost: A machine learning algorithm that builds many decision trees and "
        "combines them to make accurate predictions. "
        "SHAP (SHapley Additive exPlanations): A method that explains how much each "
        "customer attribute contributed to the model's churn prediction -- making the "
        "model transparent and auditable."
    )

    insight("Key Finding -- Model Accuracy and Risk Targeting",
        "The predictive model correctly identifies churned customers in the top 20% "
        "of risk scores at 1.84x the average churn rate. Targeting this group alone "
        f"captures 35.2% of all churned customers while contacting only 20% of the base -- "
        "making retention outreach roughly 3.5x more efficient than a random contact strategy.")

    section_header("Model Performance", model_tab_tooltip)
    section_subtitle(
        "How accurately does the model identify customers likely to leave before they "
        "actually do? Higher lift and capture rates mean fewer wasted contacts and "
        "more revenue recovered per dollar spent on outreach."
    )

    col_a, col_b = st.columns(2)
    with col_a:
        deciles   = list(range(1, 11))
        lift_vals = [1.84, 1.66, 1.53, 1.38, 1.15, 0.93, 0.64, 0.42, 0.26, 0.14]
        colors_d  = [NAVY if i < 2 else STEEL_700 if i < 5 else BLUE_500
                     for i in range(10)]
        fig_lift  = go.Figure()
        fig_lift.add_trace(go.Bar(
            x=[str(d) for d in deciles], y=lift_vals,
            marker_color=colors_d,
            text=[f"{v:.2f}x" for v in lift_vals],
            textposition="outside", textfont=dict(size=12, color=NAVY),
        ))
        fig_lift.add_hline(y=1.0, line_dash="dash", line_color=GRAY_300, line_width=1.5,
                           annotation_text="Baseline (1.0x)",
                           annotation_font_size=11, annotation_font_color=GRAY_700)
        fig_lift.update_layout(
            **base_layout(320),
            title=dict(text="Model Lift by Decile", font=dict(size=15, color=NAVY), x=0),
            xaxis_title="Risk Decile (1 = Highest Risk)",
            yaxis_title="Lift (x Average Churn Rate)",
            xaxis=dict(gridcolor=GRAY_300, tickfont=dict(size=12, color=BLACK)),
            yaxis=dict(range=[0, 2.3], gridcolor=GRAY_300,
                       tickfont=dict(size=12, color=BLACK)),
            showlegend=False,
        )
        st.plotly_chart(fig_lift, use_container_width=True)

    with col_b:
        cum_gain   = [18.5, 35.2, 50.3, 64.8, 75.9, 85.6, 91.9, 96.2, 98.7, 100.0]
        random_ref = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        fig_gain   = go.Figure()
        fig_gain.add_trace(go.Scatter(
            x=deciles, y=cum_gain, mode="lines+markers", name="Model",
            line=dict(color=NAVY, width=2.5), marker=dict(size=8, color=NAVY),
            hovertemplate="Decile %{x}: %{y:.2f}% captured<extra></extra>",
        ))
        fig_gain.add_trace(go.Scatter(
            x=deciles, y=random_ref, mode="lines", name="Random Baseline",
            line=dict(color=GRAY_300, width=1.5, dash="dash"),
        ))
        # Annotation centered directly above the decile 2 plot point
        fig_gain.add_annotation(
            x=2, y=35.2, text="Top 20% captures 35.2%",
            showarrow=True, arrowhead=2, arrowcolor=NAVY,
            font=dict(size=12, color=NAVY),
            ax=0, ay=-50, xanchor="center", yanchor="bottom",
        )
        fig_gain.update_layout(
            **base_layout(320),
            title=dict(text="Cumulative Gain: Efficiency of Targeted Retention",
                       font=dict(size=15, color=NAVY), x=0),
            xaxis_title="Risk Decile (Cumulative)",
            yaxis_title="% of Churned Customers Captured",
            xaxis=dict(tickvals=deciles, gridcolor=GRAY_300,
                       tickfont=dict(size=12, color=BLACK)),
            yaxis=dict(range=[0, 115], gridcolor=GRAY_300,
                       tickfont=dict(size=12, color=BLACK)),
            legend=dict(orientation="h", x=0.5, xanchor="center",
                        y=-0.2, font=dict(size=12, color=BLACK)),
        )
        st.plotly_chart(fig_gain, use_container_width=True)

    section_header("Feature Importance and Model Accuracy")
    section_subtitle(
        "Which customer attributes most strongly predict churn? "
        "SHAP values show both which features matter and in which direction -- "
        "helping translate model outputs into actionable business decisions."
    )

    col_c, col_d = st.columns(2)
    with col_c:
        shap_tooltip = (
            "SHAP (SHapley Additive exPlanations) measures the average contribution "
            "of each feature to the model's churn predictions across all customers. "
            "A higher bar means that feature had a larger influence on whether the model "
            "predicted churn or retention. This is model-level importance -- it shows "
            "which signals the model relies on most overall."
        )
        features  = [
            "Contract Type (Month-to-Month)", "Autopay Enrollment",
            "Internet Service (Fiber)", "Promo Status", "Tenure (Months)",
            "First 60-Day Technical Call", "First 60-Day Billing Call",
            "Monthly Charges", "Contract Type (One Year)", "Contract Type (Two Year)",
        ]
        shap_vals  = [1.04, 0.39, 0.35, 0.26, 0.24, 0.23, 0.17, 0.14, 0.12, 0.12]
        colors_s   = [NAVY] + [STEEL_700] * 4 + [BLUE_700] * 5
        fig_shap   = bar_chart(
            features, shap_vals,
            title="SHAP Global Feature Importance",
            xlabel="Feature", ylabel="Mean |SHAP Value|",
            colors=colors_s, height=400,
            text_vals=[f"{v:.2f}" for v in shap_vals], horizontal=True,
        )
        # Add info icon via title annotation
        fig_shap.update_layout(
            title=dict(
                text="SHAP Global Feature Importance",
                font=dict(size=15, color=NAVY), x=0,
            )
        )
        st.plotly_chart(fig_shap, use_container_width=True)
        st.markdown(
            f'<div style="font-size:12px;color:{GRAY_700};margin-top:-8px;">'
            f'SHAP: SHapley Additive exPlanations -- measures how much each customer '
            f'attribute pushed the model toward predicting churn or retention.</div>',
            unsafe_allow_html=True,
        )

    with col_d:
        conf_tooltip = (
            "Confusion Matrix: Shows where the model is right and wrong. "
            "True Positives (bottom-right): Churned customers the model correctly flagged. "
            "True Negatives (top-left): Retained customers the model correctly identified. "
            "False Positives (top-right): Retained customers incorrectly flagged -- "
            "these result in unnecessary outreach contacts. "
            "False Negatives (bottom-left): Churned customers the model missed -- "
            "these are lost without any intervention. "
            "Threshold = 0.5: A customer is predicted to churn if the model's "
            "probability score exceeds 50%."
        )
        section_header("Confusion Matrix (Threshold = 0.50)", conf_tooltip)
        # Correct orientation: rows=Actual, cols=Predicted
        # z[0] = Actual Retained: [TN=16084, FP=5969]
        # z[1] = Actual Churned:  [FN=4537,  TP=18410]
        conf_z    = [[16084, 5969], [4537, 18410]]
        # Per-cell text colors:
        #   TN (16084, light cell) = dark grey  |  FP (5969, light cell) = dark grey
        #   FN (4537,  mid cell)   = dark grey  |  TP (18410, dark cell) = white
        conf_text_colors = [[WHITE, "#444444"], ["#444444", WHITE]]
        fig_conf  = go.Figure(go.Heatmap(
            z=conf_z,
            x=["Predicted: Retained", "Predicted: Churned"],
            y=["Actual: Retained", "Actual: Churned"],
            colorscale=[[0, STEEL_100], [1, NAVY]],
            showscale=False,
            hovertemplate="%{y} / %{x}: %{z:,}<extra></extra>",
        ))
        # Add per-cell annotations with correct font colors
        cell_labels = [["16,084", "5,969"], ["4,537", "18,410"]]
        for row_i, (row_labels, row_colors) in enumerate(zip(cell_labels, conf_text_colors)):
            for col_i, (label, color) in enumerate(zip(row_labels, row_colors)):
                fig_conf.add_annotation(
                    x=col_i, y=row_i,
                    text=f"<b>{label}</b>",
                    showarrow=False,
                    font=dict(size=20, color=color),
                    xref="x", yref="y",
                )
        fig_conf.update_layout(
            **base_layout(260),
            xaxis=dict(tickfont=dict(size=12, color=BLACK)),
            yaxis=dict(tickfont=dict(size=12, color=BLACK)),
            showlegend=False,
        )
        st.plotly_chart(fig_conf, use_container_width=True)
        st.markdown(
            f"<div style='background:{STEEL_100};border:1px solid {STEEL_300};"
            f"border-left:4px solid {BLUE_700};"
            f"border-radius:0 8px 8px 0;padding:14px 16px;"
            f"font-size:14px;color:{BLACK};line-height:2.3;'>"
            f"True Positives: <b style='color:{GREEN_900};'>18,410</b> -- correctly flagged<br>"
            f"True Negatives: <b style='color:{NAVY};'>16,084</b> -- correctly retained<br>"
            f"False Positives: <b style='color:{ORANGE_700};'>5,969</b> -- unnecessary outreach<br>"
            f"False Negatives: <b style='color:{STEEL_700};'>4,537</b> -- missed churners<br>"
            f"Signal Ratio: <b style='color:{NAVY};'>3.1 to 1</b></div>",
            unsafe_allow_html=True,
        )

    # ── At-Risk Customer Profile Explorer ────
    section_header("At-Risk Customer Profile Explorer")
    section_subtitle(
        "Select a risk decile range to view the profile of customers in that group: "
        "their contract mix, average CLTV, median tenure, and friction type. "
        "Use this to understand who your retention team will be contacting."
    )

    insight("Key Finding -- At-Risk Customer Profile",
        "Focusing outreach on the highest-risk deciles costs roughly $299K at $50 per "
        "contact (across 5,969 false positives) and recovers up to $6.49M in CLTV. "
        "The 3.1-to-1 signal ratio means approximately one unnecessary contact for every "
        "three correctly flagged customers -- well within acceptable bounds for a "
        "retention program.")

    decile_sel   = st.radio(
        "Select Risk Decile Range",
        ["Decile 1 to 2 (Highest Risk)", "Decile 3 to 5", "Decile 6 to 10"],
        horizontal=True,
    )
    at_risk_df = df[df["is_at_risk"] == 1].copy()
    if "churn_score" in at_risk_df.columns:
        at_risk_df = at_risk_df.sort_values("churn_score", ascending=False).reset_index(drop=True)
        n = len(at_risk_df)
        at_risk_df["decile_group"] = pd.cut(
            at_risk_df.index,
            bins=[0, n * 0.2, n * 0.5, n],
            labels=["Decile 1 to 2 (Highest Risk)", "Decile 3 to 5", "Decile 6 to 10"],
        )
        profile_df = at_risk_df[at_risk_df["decile_group"] == decile_sel]
    else:
        profile_df = at_risk_df

    ct_map     = {"month_to_month": "Month-to-Month",
                  "one_year": "One Year", "two_year": "Two Year"}
    top_ct     = (profile_df["contract_type"].map(ct_map).value_counts().idxmax()
                  if len(profile_df) > 0 else "N/A")
    top_ct_pct = (profile_df["contract_type"].value_counts(normalize=True).max() * 100
                  if len(profile_df) > 0 else 0)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Customers in Group", f"{len(profile_df):,}")
    with c2: st.metric("Avg CLTV",
                       f"${profile_df['cltv'].mean():.2f}" if len(profile_df) > 0 else "N/A")
    with c3: st.metric("Dominant Contract",
                       f"{top_ct_pct:.2f}% {top_ct}" if len(profile_df) > 0 else "N/A")
    with c4:
        med = profile_df["tenure_months"].median() if len(profile_df) > 0 else 0
        st.metric("Median Tenure", f"{med:.0f} Months")


# ─────────────────────────────────────────────
# TAB 4 -- FINANCIAL IMPACT
# ─────────────────────────────────────────────
def render_financial_impact(df, df_full, contract_sel, segment_sel,
                             channel_sel, tenure_range, promo_sel):
    at_risk_df   = df[df["is_at_risk"] == 1]
    at_risk_count = len(at_risk_df)
    cltv_total   = at_risk_df["cltv"].sum()
    avg_cltv     = at_risk_df["cltv"].mean() if at_risk_count > 0 else 0
    churned_total = int(df["churn"].sum())
    at_risk_pct  = at_risk_count / churned_total * 100 if churned_total > 0 else 0

    insight("Key Finding -- Financial Impact of Preventable Churn",
        f"At-Risk Customers with unresolved service issues represent "
        f"{at_risk_pct:.2f}% of all churned customers and ${cltv_total/1e6:.2f}M "
        f"in recoverable 24-month customer value. Use the simulator below to estimate "
        f"what a structured retention program could recover across different save-rate "
        f"and cost assumptions.")

    section_header("Save-Rate Simulator",
        "Adjust the Program Save Rate to represent the percentage of At-Risk Customers "
        "your team could retain through proactive outreach. Adjust the Outreach Cost to "
        "reflect your estimated cost per customer contact. All results update live. "
        "CLTV (Customer Lifetime Value): The estimated 24-month contribution margin "
        "per customer -- the revenue at stake if that customer churns.")

    section_subtitle(
        "Drag the sliders to model different retention program scenarios. "
        "The green bar in the chart highlights your selected save rate."
    )

    col_left, col_right = st.columns([2, 3])
    with col_left:
        save_rate         = st.slider("Program Save Rate (%)", 5, 50, 20, 5)
        outreach_cost_per = st.slider("Outreach Cost per Contact ($)", 10, 200, 50, 10)

        saved         = int(at_risk_count * save_rate / 100)
        cltv_rec      = saved * avg_cltv
        prog_cost     = (at_risk_count + 5969) * outreach_cost_per
        net_roi       = (cltv_rec - prog_cost) / prog_cost if prog_cost > 0 else 0
        breakeven     = (prog_cost / (at_risk_count * avg_cltv) * 100
                         if (at_risk_count * avg_cltv) > 0 else 0)

        st.markdown(
            f"<div style='background:{STEEL_100};border:1px solid {STEEL_300};"
            f"border-left:4px solid {BLUE_700};border-radius:0 10px 10px 0;"
            f"padding:22px 24px;margin-top:14px;'>"
            f"<div style='font-size:12px;font-weight:700;color:{GRAY_700};"
            f"text-transform:uppercase;letter-spacing:0.05em;margin-bottom:16px;'>"
            f"Simulation Results</div>"
            f"<div style='font-size:16px;color:{BLACK};line-height:2.8;'>"
            f"Customers Retained: <b style='color:{NAVY};'>{saved:,}</b><br>"
            f"CLTV Recovered: <b style='color:{GREEN_900};'>${cltv_rec/1e6:.2f}M</b><br>"
            f"Est. Program Cost: <b style='color:{NAVY};'>${prog_cost/1e3:.0f}K</b><br>"
            f"Net ROI: <b style='color:{GREEN_900};'>{net_roi:.2f}x</b><br>"
            f"Break-Even Save Rate: <b style='color:{NAVY};'>{breakeven:.2f}%</b>"
            f"</div></div>",
            unsafe_allow_html=True,
        )

    with col_right:
        rates      = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
        cltv_vals  = [int(at_risk_count * r / 100) * avg_cltv for r in rates]
        bar_colors = [GREEN_900 if r == save_rate
                      else NAVY if r < save_rate else BLUE_500
                      for r in rates]
        fig_sim = go.Figure(go.Bar(
            x=[f"{r}%" for r in rates],
            y=[v / 1e6 for v in cltv_vals],
            marker_color=bar_colors,
            text=[f"${v/1e6:.2f}M" for v in cltv_vals],
            textposition="outside", textfont=dict(size=11, color=NAVY),
            hovertemplate="Save Rate: %{x}<br>CLTV Recovered: $%{y:.2f}M<extra></extra>",
        ))
        fig_sim.update_layout(
            **base_layout(400),
            title=dict(
                text="CLTV Retained by Save Rate",
                font=dict(size=15, color=NAVY), x=0,
            ),
            xaxis_title="Program Save Rate (%)",
            yaxis_title="24-Month CLTV Retained ($M)",
            xaxis=dict(gridcolor=GRAY_300, tickfont=dict(size=12, color=BLACK)),
            yaxis=dict(range=[0, max(v / 1e6 for v in cltv_vals) * 1.28],
                       gridcolor=GRAY_300, tickfont=dict(size=12, color=BLACK)),
            showlegend=False,
        )
        st.plotly_chart(fig_sim, use_container_width=True)
        # Custom legend for bar colors
        st.markdown(
            f"<div style='display:flex;gap:20px;font-size:13px;"
            f"color:{BLACK};margin-top:-8px;justify-content:center;'>"
            f"<span><span style='display:inline-block;width:14px;height:14px;"
            f"background:{GREEN_900};border-radius:2px;margin-right:5px;"
            f"vertical-align:middle;'></span>Selected rate</span>"
            f"<span><span style='display:inline-block;width:14px;height:14px;"
            f"background:{NAVY};border-radius:2px;margin-right:5px;"
            f"vertical-align:middle;'></span>Below selected</span>"
            f"<span><span style='display:inline-block;width:14px;height:14px;"
            f"background:{BLUE_500};border-radius:2px;margin-right:5px;"
            f"vertical-align:middle;'></span>Above selected</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    # ── Churn type breakdown ──────────────────
    section_header("Preventable vs. Structural Churn Breakdown",
        "Preventable: Churned customers who had at least one unresolved billing or "
        "technical issue in their first 60 days -- a service failure that could have "
        "been addressed before the customer left. "
        "Structural: Churned customers whose departure is tied to contract type or "
        "pricing mechanics rather than a specific service event. "
        "Undetermined: Churned customers whose departure reason was not captured by "
        "the available data signals.")

    filter_summary_block(df, df_full, contract_sel, segment_sel,
                         channel_sel, tenure_range, promo_sel)

    col_m, col_n = st.columns(2)
    color_map = {"Preventable": NAVY, "Structural": ORANGE_700, "Undetermined": GRAY_300}

    with col_m:
        type_counts = df[df["churn"] == 1]["churn_type"].value_counts()
        type_counts = type_counts[type_counts.index != "Retained"]
        fig_d2 = go.Figure(go.Pie(
            labels=list(type_counts.index),
            values=list(type_counts.values),
            hole=0.60,
            marker_colors=[color_map.get(l, GRAY_300) for l in type_counts.index],
            textinfo="percent", textposition="outside",
            textfont=dict(size=13, color=BLACK),
            hovertemplate="%{label}: %{value:,} customers (%{percent:.2%})<extra></extra>",
        ))
        fig_d2.update_layout(
            **base_layout(310),
            title=dict(text="Churn Type Breakdown",
                       font=dict(size=15, color=NAVY), x=0),
            showlegend=True,
            legend=dict(orientation="h", x=0.5, xanchor="center",
                        y=-0.22, font=dict(size=12, color=BLACK)),
        )
        st.plotly_chart(fig_d2, use_container_width=True)

    with col_n:
        cltv_by_type = (df[df["churn"] == 1]
                        .groupby("churn_type")["cltv"].sum()
                        .drop("Retained", errors="ignore"))
        churn_counts = (df[df["churn"] == 1]["churn_type"].value_counts()
                        .drop("Retained", errors="ignore"))
        total_churned = int(df["churn"].sum())

        hover_cltv = [
            f"<b>{label}</b><br>"
            f"{int(churn_counts.get(label, 0)):,} out of {total_churned:,} "
            f"churned customers are {label}<br>"
            f"CLTV at Risk: ${val/1e6:.2f}M<extra></extra>"
            for label, val in zip(cltv_by_type.index, cltv_by_type.values)
        ]
        y_vals  = [v / 1e6 for v in cltv_by_type.values]
        y_max   = max(y_vals) * 1.28 if y_vals else 1
        fig_ct2 = go.Figure(go.Bar(
            x=list(cltv_by_type.index),
            y=y_vals,
            marker_color=[color_map.get(l, GRAY_300) for l in cltv_by_type.index],
            text=[f"${v:.2f}M" for v in y_vals],
            textposition="outside",
            textfont=dict(size=12, color=NAVY),
            hovertemplate=hover_cltv,
        ))
        fig_ct2.update_layout(
            **base_layout(310),
            title=dict(text="CLTV at Risk by Churn Type ($M)",
                       font=dict(size=15, color=NAVY), x=0),
            yaxis_title="Total CLTV Lost ($M)",
            yaxis=dict(range=[0, y_max], gridcolor=GRAY_300,
                       tickfont=dict(size=12, color=BLACK)),
            xaxis=dict(gridcolor=GRAY_300, tickfont=dict(size=12, color=BLACK)),
            showlegend=False,
        )
        st.plotly_chart(fig_ct2, use_container_width=True)


# ─────────────────────────────────────────────
# TAB 5 -- INSURANCE PLAYBOOK
# ─────────────────────────────────────────────
def render_insurance_playbook():
    col_a, col_b = st.columns(2)

    with col_a:
        section_header("Telecom Driver to Auto Insurance Transition")
        drivers = [
            ("Month-to-Month Contract",    "6-Month Policy Term"),
            ("Promo to Full-Rate Shift",   "Renewal Price Increase"),
            ("Early Billing Friction",     "First 60-Day Claims Friction"),
            ("No Autopay Enrollment",      "No EFT or Auto-Renewal"),
            ("Service Bundle Add-Ons",     "Multi-Policy Bundling"),
            ("Fiber Market Competition",   "Competitive Metro Markets"),
            ("Sales Channel (Aggregator)", "Online Rate Aggregator"),
        ]
        rows = "".join([
            f"<tr>"
            f"<td style='padding:12px 14px;border-bottom:1px solid {STEEL_300};"
            f"font-size:14px;color:{BLACK};vertical-align:middle;'>{t}</td>"
            f"<td style='border-bottom:1px solid {STEEL_300};width:60px;"
            f"min-width:60px;max-width:60px;text-align:center;vertical-align:middle;"
            f"font-size:20px;color:{BLUE_700};padding:0;'>&#8594;</td>"
            f"<td style='padding:12px 14px;border-bottom:1px solid {STEEL_300};"
            f"font-size:14px;color:{BLUE_700};font-weight:700;"
            f"vertical-align:middle;'>{i}</td>"
            f"</tr>"
            for t, i in drivers
        ])
        st.markdown(
            f"<table style='width:100%;border-collapse:collapse;"
            f"border:1px solid {STEEL_300};border-radius:8px;overflow:hidden;'>"
            f"<thead><tr>"
            f"<th style='padding:12px 14px;background:{STEEL_100};"
            f"font-size:13px;color:{NAVY};text-align:left;"
            f"font-weight:700;text-transform:uppercase;letter-spacing:0.04em;'>"
            f"Telecom Signal</th>"
            f"<th style='background:{STEEL_100};width:60px;min-width:60px;"
            f"max-width:60px;text-align:center;padding:0;'></th>"
            f"<th style='padding:12px 14px;background:{STEEL_100};"
            f"font-size:13px;color:{NAVY};text-align:left;"
            f"font-weight:700;text-transform:uppercase;letter-spacing:0.04em;'>"
            f"Auto Insurance Transition</th>"
            f"</tr></thead>"
            f"<tbody>{rows}</tbody></table>",
            unsafe_allow_html=True,
        )

    with col_b:
        section_header("Three Retention Levers")
        levers = [
            ("01", "Rapid Friction Resolution",
             "Deploy proactive outreach within 48 hours of any unresolved billing or "
             "technical issue in the first 60 days. This lever requires no new "
             "infrastructure -- the at-risk customer list is already identified.",
             "$6.49M recovered at 20% save rate"),
            ("02", "Annual Term Discount plus EFT Enrollment",
             "Address the root cause directly: Month-to-Month customers churn at "
             "72.75% vs. 24.14% for Two-Year contracts. Tie rate incentives to a "
             "12-month commitment and automatic payment enrollment.",
             "72.75% to 24.14% churn reduction target"),
            ("03", "Predictive Risk Scoring at Renewal",
             "Score every policyholder using the trained XGBoost model 30 days before "
             "their renewal date. Route the top 20% highest-risk customers to a "
             "dedicated retention outreach team.",
             "35.2% of churned customers captured in top quintile"),
        ]
        for num, title, desc, stat in levers:
            st.markdown(
                f"<div style='background:{STEEL_100};border:1px solid {STEEL_300};"
                f"border-left:4px solid {BLUE_700};"
                f"border-radius:0 10px 10px 0;padding:16px 20px;margin-bottom:12px;'>"
                f"<div style='font-size:22px;font-weight:700;color:{BLUE_700};"
                f"margin-bottom:5px;'>{num}</div>"
                f"<div style='font-size:15px;font-weight:700;color:{NAVY};"
                f"margin-bottom:8px;'>{title}</div>"
                f"<div style='font-size:14px;color:{BLACK};line-height:1.7;"
                f"margin-bottom:10px;'>{desc}</div>"
                f"<div style='font-size:14px;font-weight:700;color:{GREEN_900};"
                f"background:#E8F5F2;padding:5px 14px;border-radius:20px;"
                f"display:inline-block;'>{stat}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # Framework Portability and Closing Takeaway -- identical card style
    card_style = (
        f"background:{STEEL_100};border:1px solid {STEEL_300};"
        f"border-left:4px solid {BLUE_700};border-radius:0 10px 10px 0;"
        f"padding:22px 26px;margin-bottom:14px;"
    )
    label_style = (
        f"font-size:12px;font-weight:700;color:{GRAY_700};"
        f"text-transform:uppercase;letter-spacing:0.05em;margin-bottom:12px;"
    )
    body_style = f"font-size:14px;color:{BLACK};line-height:1.85;"

    section_header("Framework Portability")
    st.markdown(
        f"<div style='{card_style}'>"
        f"<div style='{label_style}'>Framework Portability</div>"
        f"<div style='{body_style}'>"
        f"The XGBoost model and SHAP feature ranking used here on telecom data can be "
        f"retrained on auto insurance policy, claims, and billing data to produce a churn "
        f"risk score for every policyholder at renewal. The financial impact framework "
        f"translates directly: swap CLTV for premium-at-risk, and at-risk customers become "
        f"policyholders who had unresolved claims or billing issues in their first 60 days "
        f"of coverage."
        f"</div></div>",
        unsafe_allow_html=True,
    )

    section_header("Closing Takeaway")
    st.markdown(
        f"<div style='{card_style}'>"
        f"<div style='{label_style}'>Closing Takeaway</div>"
        f"<div style='{body_style}'>"
        f"What was built here on telecom data is a transferable analytics framework. "
        f"The same combination of behavioral segmentation, predictive modeling, and "
        f"financial impact quantification applies directly to auto insurance retention "
        f"with policy tenure replacing contract length, renewal price changes replacing "
        f"promo transitions, and premium-at-risk replacing customer lifetime value. "
        f"The signals differ in name. The underlying dynamics do not."
        f"</div></div>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# TAB 6 -- RECOMMENDATIONS
# ─────────────────────────────────────────────
def render_recommendations(df):
    at_risk_df   = df[df["is_at_risk"] == 1]
    at_risk_count = len(at_risk_df)
    avg_cltv     = at_risk_df["cltv"].mean() if at_risk_count > 0 else 0
    saved_20     = int(at_risk_count * 0.20)
    cltv_20      = saved_20 * avg_cltv

    section_subtitle(
        "The following recommendations are ranked by time-to-value and derive directly "
        "from model outputs, EDA findings, and the financial simulation. Each recommendation "
        "includes supporting evidence tied to a specific finding, an estimated financial "
        "value, and an implementation effort rating."
    )

    def rec_card(tier, title, value_label, effort_label, body, evidence):
        tier_colors = {
            "Immediate (0 to 30 Days)":   NAVY,
            "Short-Term (30 to 90 Days)": STEEL_700,
            "Strategic (90 Plus Days)":   BLUE_700,
        }
        tier_color = tier_colors.get(tier, BLUE_700)
        st.markdown(
            f"<div class='rec-card'>"
            f"<div class='rec-tier' style='color:{tier_color};'>{tier}</div>"
            f"<div class='rec-title'>{title}</div>"
            f"<div class='rec-badges'>"
            f"<span class='rec-value'>{value_label}</span>"
            f"<span class='rec-effort'>{effort_label}</span>"
            f"</div>"
            f"<div class='rec-body'>{body}</div>"
            f"<div class='rec-evidence'>{evidence}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    section_header("Immediate Actions (0 to 30 Days)")
    rec_card(
        "Immediate (0 to 30 Days)",
        "Deploy Rapid Friction Resolution Outreach",
        f"${cltv_20/1e6:.2f}M recovered at 20% save rate",
        "Effort: Low -- outreach list is ready",
        f"Contact the {at_risk_count:,} identified at-risk customers who had an unresolved "
        f"billing or technical issue in their first 60 days. A 48-hour resolution SLA on "
        f"first-contact service issues is the single highest-ROI action available because "
        f"the customer list is already identified and requires no new infrastructure.",
        "Evidence: Unresolved technical issues drive a 70.99% churn rate vs. 46.35% for "
        "customers with no friction -- a 24.64 percentage point gap. At-Risk Customers "
        "represent 16.69% of all churned customers and carry a disproportionately high "
        "average CLTV.",
    )
    rec_card(
        "Immediate (0 to 30 Days)",
        "Prioritize Autopay and EFT Enrollment at Onboarding",
        "14.23 pt churn reduction potential",
        "Effort: Low -- onboarding process change",
        "Add autopay and EFT enrollment as a structured step in the customer onboarding "
        "flow. Manual payment customers churn at 57.11% vs. 42.88% for autopay customers -- "
        "a 14.23 percentage point gap that requires only a process change, not a new program.",
        "Evidence: Autopay enrollment is the second-ranked feature by SHAP global importance "
        "(mean |SHAP| = 0.39). It is the easiest structural churn driver to address because "
        "enrollment is fully within operational control at the point of acquisition.",
    )

    section_header("Short-Term Actions (30 to 90 Days)")
    rec_card(
        "Short-Term (30 to 90 Days)",
        "Launch Annual Term Migration Campaign",
        "72.75% to 24.14% target churn rate",
        "Effort: Medium -- pricing team required",
        "Offer a rate discount or service credit tied to upgrading from a Month-to-Month "
        "contract to a One-Year or Two-Year term. The 48.61 percentage point difference in "
        "churn rates justifies a meaningful incentive -- the cost of the discount is a "
        "fraction of the CLTV at risk.",
        "Evidence: Contract type is the top SHAP feature by a wide margin "
        "(mean |SHAP| = 1.04). Month-to-Month customers represent 55.2% of the customer "
        "base and account for 90,351 churned customers -- the largest single source of "
        "preventable revenue loss.",
    )
    rec_card(
        "Short-Term (30 to 90 Days)",
        "Build a Renewal Risk Scoring Pipeline",
        "35.2% of churned customers in top quintile",
        "Effort: Medium -- ML ops and CRM integration",
        "Implement the trained XGBoost model as a scoring job that runs 30 days before "
        "each customer renewal. Output a risk score for every account and route the top "
        "20% highest-risk customers to a proactive retention team.",
        "Evidence: The model captures 35.2% of all churned customers in the top 20% of "
        "risk scores at 1.84x baseline lift. At $50 per contact the program recovers "
        "${cltv_20/1e6:.2f}M at a 20% save rate -- a {(cltv_20-(at_risk_count+5969)*50)/(at_risk_count+5969)/50:.1f}x "
        "return on outreach investment.",
    )

    section_header("Strategic Investments (90 Plus Days)")
    rec_card(
        "Strategic (90 Plus Days)",
        "Retrain the Model on Auto Insurance Policy Data",
        "Full premium-at-risk quantification",
        "Effort: High -- data access and modeling",
        "Port this framework to auto insurance by retraining the XGBoost model on "
        "policyholder data: renewal dates, rate change history, claims friction in the "
        "first 60 days, payment method, and policy term length. Replace CLTV with "
        "12-month premium-at-risk as the financial impact metric.",
        "Evidence: Every telecom churn signal maps to a direct auto insurance analogue "
        "(see Insurance Playbook tab). The SHAP-ranked feature logic is portable -- "
        "only the training data changes.",
    )
    rec_card(
        "Strategic (90 Plus Days)",
        "Develop a Real-Time First-60-Day Friction Alert System",
        "$4M plus annual CLTV recovery potential",
        "Effort: High -- systems and operations alignment",
        "Build a monitoring pipeline that flags policyholders with unresolved service "
        "issues within their first 60 days and automatically routes them to a resolution "
        "team. This converts the at-risk identification from a retrospective model feature "
        "into a real-time intervention trigger.",
        "Evidence: 16.69% of all churn stems from preventable friction in the first 60 "
        "days. Reducing this rate by half would recover $4M or more in annual CLTV "
        "without requiring a predictive model at all.",
    )


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    df_full = load_data()
    init_session_state(df_full)

    st.markdown(
        f"<div style='padding:12px 0 6px 0;'>"
        f"<h1 style='font-size:26px;font-weight:700;color:{NAVY};"
        f"margin:0;font-family:Georgia,serif;'>"
        f"Telecom Churn -- Cross-Industry Retention Dashboard</h1>"
        f"<p style='font-size:14px;color:{BLACK};margin:5px 0 0 0;'>"
        f"A data-driven retention framework examining churn behavior, predictive risk, "
        f"and financial impact with direct application to auto insurance.</p>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<hr style='border:none;border-top:2px solid {BLUE_700};"
        f"margin:10px 0 16px 0;'>",
        unsafe_allow_html=True,
    )

    df_filtered, contract_sel, segment_sel, channel_sel, tenure_range, promo_sel = \
        render_sidebar(df_full)

    if len(df_filtered) == 0:
        st.warning("No customers match the current filters. Please adjust the sidebar.")
        return

    churned_count, churn_rate, cltv_at_risk, at_risk_count, at_risk_pct = \
        render_kpi_header(df_filtered, df_full)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Overview",
        "Churn Drivers",
        "Model + Risk",
        "Financial Impact",
        "Recommendations",
        "Insurance Playbook",
    ])

    with tab1:
        render_overview(df_filtered, churn_rate, cltv_at_risk, at_risk_pct)
    with tab2:
        render_churn_drivers(df_filtered)
    with tab3:
        render_model_risk(df_filtered)
    with tab4:
        render_financial_impact(df_filtered, df_full, contract_sel, segment_sel,
                                channel_sel, tenure_range, promo_sel)
    with tab5:
        render_recommendations(df_filtered)
    with tab6:
        render_insurance_playbook()


if __name__ == "__main__":
    main()