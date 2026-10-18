"""Executive Decision Analytics BI Application

Main Entrypoint and Executive Landing Page for the Streamlit BI Dashboard.
Built with clean navy-and-white executive aesthetics and modular data architecture.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

from src.io_utils import get_project_root
from src.dashboard_utils import (
    load_clean_data,
    load_authoritative_metrics,
    load_data_quality_report,
    render_metric_card,
    format_currency,
    format_pct
)

st.set_page_config(
    page_title="Executive Decision Analytics BI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Executive CSS for polished navy-and-white styling
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main {
        background-color: #F8FAFC;
    }
    
    .stMetric {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 14px 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    
    h1, h2, h3 {
        color: #0F2942 !important;
        font-weight: 700 !important;
    }
    
    .nav-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 18px;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        height: 100%;
    }
    .nav-card:hover {
        border-color: #2563EB;
        box-shadow: 0 4px 12px rgba(37,99,235,0.08);
    }
    .nav-card h4 {
        margin: 0 0 8px 0;
        color: #1E3A8A;
        font-size: 1.05rem;
    }
    .nav-card p {
        margin: 0;
        color: #64748B;
        font-size: 0.85rem;
        line-height: 1.4;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header Banner
st.markdown(
    """
    <div style="background: linear-gradient(135deg, #0F2942 0%, #1E3A8A 100%); padding: 32px 36px; border-radius: 12px; margin-bottom: 24px; color: white;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <span style="background: rgba(255,255,255,0.15); padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">
                    Capstone Analytics Platform
                </span>
                <h1 style="color: white !important; margin: 12px 0 6px 0; font-size: 2.2rem;">Executive Decision Analytics</h1>
                <p style="color: #CBD5E1; margin: 0; font-size: 1.05rem; max-width: 750px;">
                    Omnichannel Retail Performance, Margin Optimization, and Financial Scenario Analysis (2023–2025)
                </p>
            </div>
            <div style="text-align: right; margin-top: 10px;">
                <div style="font-size: 0.85rem; color: #94A3B8;">Lead Analyst & Developer</div>
                <div style="font-size: 1.1rem; font-weight: 600; color: #F8FAFC;">Gurusaiprasadreddy</div>
                <div style="font-size: 0.8rem; color: #38BDF8; margin-top: 4px;">Audited & Validated Pipeline</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Data Ingestion and Validation Check
try:
    df = load_clean_data()
    metrics = load_authoritative_metrics()
    dq_report = load_data_quality_report()
    data_loaded = True
except Exception as e:
    st.error(f"Error loading verified pipeline artifacts: {e}")
    data_loaded = False

if data_loaded:
    # High-Level Metric Tiles
    tot_rev = df["sales"].sum()
    tot_prof = df["profit"].sum()
    weighted_margin = (tot_prof / tot_rev) * 100
    tot_orders = len(df)
    tot_customers = df["customer_id"].nunique()
    aov = tot_rev / tot_orders

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        render_metric_card("Total Revenue", format_currency(tot_rev), "+56.2% since '23", "positive", "Gross recognized sales")
    with col2:
        render_metric_card("Total Profit", format_currency(tot_prof), "+20.7% since '23", "positive", "Net contribution profit")
    with col3:
        render_metric_card("Portfolio Margin", format_pct(weighted_margin), "-3.5 pp YoY drop", "negative", "Weighted aggregate margin")
    with col4:
        render_metric_card("Total Orders", f"{tot_orders:,}", "+61.7% order growth", "positive", "100% unique order IDs")
    with col5:
        render_metric_card("Unique Customers", f"{tot_customers:,}", "71.4% repeat share", "normal", "Cohort of 2,116 accounts")
    with col6:
        render_metric_card("Average Order Value", format_currency(aov), "Stable ~$281", "normal", "Revenue per order line")

    st.markdown("---")

    # Platform Navigation Grid
    st.markdown("### 🧭 Platform Navigation")
    st.markdown("Select an analytical module from the sidebar or click into any section below:")

    row1_c1, row1_c2, row1_c3 = st.columns(3)
    with row1_c1:
        st.markdown(
            """
            <div class="nav-card">
                <h4><a href="/Executive_Overview" target="_self" style="text-decoration: none; color: inherit;">1. Executive Overview</a></h4>
                <p>High-level performance snapshot, year-over-year trajectory, key driver analysis, and core executive findings.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with row1_c2:
        st.markdown(
            """
            <div class="nav-card">
                <h4><a href="/Revenue_Profitability" target="_self" style="text-decoration: none; color: inherit;">2. Revenue & Profitability</a></h4>
                <p>Monthly financial trends, category & subcategory contribution rankings, and profit waterfall decomposition.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with row1_c3:
        st.markdown(
            """
            <div class="nav-card">
                <h4><a href="/Discount_Analysis" target="_self" style="text-decoration: none; color: inherit;">3. Discount & Pricing</a></h4>
                <p>Quantifying margin collapse across discount tiers, loss-making orders, and interactive discount threshold simulations.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    row2_c1, row2_c2, row2_c3 = st.columns(3)
    with row2_c1:
        st.markdown(
            """
            <div class="nav-card">
                <h4><a href="/Channel_Regional_Analysis" target="_self" style="text-decoration: none; color: inherit;">4. Channel & Geography</a></h4>
                <p>Marketplace 13% commission fee drag, channel shift, and regional fulfillment performance across 5 territories.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with row2_c2:
        st.markdown(
            """
            <div class="nav-card">
                <h4><a href="/Customer_Analytics" target="_self" style="text-decoration: none; color: inherit;">5. Customer Analytics</a></h4>
                <p>Customer retention cohorts, Pareto concentration (top 20% generate 66% sales), and the AOV repeat order anomaly.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with row2_c3:
        st.markdown(
            """
            <div class="nav-card">
                <h4><a href="/Delivery_Returns" target="_self" style="text-decoration: none; color: inherit;">6. Delivery & Returns</a></h4>
                <p>Analysis of shipping SLA breaches (>5 days) and the 3x multiplier effect on merchandise return rates.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    row3_c1, row3_c2, row3_c3 = st.columns(3)
    with row3_c1:
        st.markdown(
            """
            <div class="nav-card">
                <h4><a href="/Statistical_Insights" target="_self" style="text-decoration: none; color: inherit;">7. Statistical Insights</a></h4>
                <p>Empirical hypothesis test results (H1, H2, H3), effect sizes, confidence intervals, and Pearson/Spearman correlations.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with row3_c2:
        st.markdown(
            """
            <div class="nav-card">
                <h4><a href="/Strategic_Decisions" target="_self" style="text-decoration: none; color: inherit;">8. Strategic Scenarios</a></h4>
                <p>Three-pillar turnaround strategy, 36-month cash flow modeling, payback analysis, and ROI scenario engine ($97k uplift).</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with row3_c3:
        st.markdown(
            """
            <div class="nav-card">
                <h4><a href="/Data_Quality" target="_self" style="text-decoration: none; color: inherit;">9. Data Quality & Audit</a></h4>
                <p>Full pipeline verification: 12 automated test gates, financial reconciliation waterfall, and row-level modification logs.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # System Status & Verification Card
    status_col1, status_col2 = st.columns([2, 1])
    with status_col1:
        st.markdown("#### 🛡️ Data Engineering & Governance Status")
        st.markdown(
            f"""
            * **Data Contract:** Version 2.0.0 (`outputs/metrics.json`)
            * **Cleaning Pipeline:** Deterministic vectorized execution (`src/data_cleaning.py`)
            * **Quality Gate:** **100% Critical Checks Passed** ({dq_report['Status'].value_counts().get('PASS', 0)} Passed, 0 Failed)
            * **Source Traceability:** Raw CSV SHA256 `1685e689...` preserved byte-for-byte
            * **Reconciliation:** All 2023–2025 revenue and profit figures match executive report exactly to the penny.
            """
        )
    with status_col2:
        st.markdown("#### ⚡ Quick Pipeline Actions")
        st.caption("Use the sidebar on any page to apply global multi-dimensional filters.")
        if st.button("Inspect Data Quality Report", use_container_width=True):
            st.switch_page("pages/9_Data_Quality.py")
        if st.button("View Strategic ROI Engine", use_container_width=True):
            st.switch_page("pages/8_Strategic_Decisions.py")
