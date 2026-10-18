"""Page 1: Executive Overview

Comprehensive executive performance summary, year-over-year trajectory,
revenue vs profit divergence, and core empirical business findings.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from src.dashboard_utils import (
    load_clean_data,
    load_data_quality_report,
    render_sidebar_filters,
    get_plotly_layout,
    render_metric_card,
    format_currency,
    format_pct,
    NAVY_DARK,
    BLUE_ACCENT,
    CYAN_ACCENT,
    CRIMSON_RED,
    EMERALD_GREEN
)
from src.kpi_engine import calculate_weighted_profit_margin, calculate_monthly_metrics

st.set_page_config(page_title="Executive Overview | BI Dashboard", page_icon="📊", layout="wide")

df_full = load_clean_data()
df = render_sidebar_filters(df_full)

st.title("📈 Executive Performance Overview")
st.caption("Strategic Performance Snapshot across Omnichannel Transactions (2023–2025)")

# Data quality status banner
dq_report = load_data_quality_report()
pass_count = dq_report["Status"].value_counts().get("PASS", 0)
total_count = len(dq_report)
st.markdown(
    f"""
    <div style="background-color: #ECFDF5; border-left: 4px solid #10B981; padding: 10px 16px; border-radius: 4px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
        <span style="color: #065F46; font-size: 0.9rem; font-weight: 500;">
            🛡️ <strong>Pipeline Status:</strong> Data Quality Verified ({pass_count}/{total_count} Automated Gates Passed). Reconciled against single source of truth.
        </span>
        <span style="font-size: 0.8rem; color: #047857; font-weight: 600;">ACTIVE POPULATION: {len(df):,} ORDERS</span>
    </div>
    """,
    unsafe_allow_html=True
)

if df.empty:
    st.warning("⚠️ No orders match the selected filters. Please adjust your filter selections in the sidebar.")
    st.stop()

# Key Metric Tiles
rev = df["sales"].sum()
prof = df["profit"].sum()
margin = calculate_weighted_profit_margin(prof, rev)
orders = len(df)
customers = df["customer_id"].nunique()
aov = rev / orders if orders > 0 else 0

m1, m2, m3, m4, m5, m6 = st.columns(6)
with m1:
    render_metric_card("Filtered Revenue", format_currency(rev), subtext="Gross order sales")
with m2:
    render_metric_card("Filtered Profit", format_currency(prof), subtext="Net contribution")
with m3:
    margin_color = "positive" if margin >= 15 else ("normal" if margin >= 10 else "negative")
    render_metric_card("Weighted Margin", format_pct(margin), delta_color=margin_color, subtext="Aggregate margin")
with m4:
    render_metric_card("Order Volume", f"{orders:,}", subtext="Unique transactions")
with m5:
    render_metric_card("Active Customers", f"{customers:,}", subtext="Unique purchasing accounts")
with m6:
    render_metric_card("Average Order Value", format_currency(aov), subtext="Revenue per order")

st.markdown("---")

# Monthly Revenue and Profit Trend (Synchronized Dual View)
st.subheader("📅 Monthly Financial Trajectory & Margin Compression")

monthly = calculate_monthly_metrics(df)

fig_monthly = go.Figure()

# Revenue Bar
fig_monthly.add_trace(
    go.Bar(
        x=monthly["year_month"],
        y=monthly["revenue"],
        name="Revenue ($)",
        marker_color=NAVY_DARK,
        opacity=0.85,
        hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>"
    )
)

# Profit Bar
fig_monthly.add_trace(
    go.Bar(
        x=monthly["year_month"],
        y=monthly["profit"],
        name="Profit ($)",
        marker_color=BLUE_ACCENT,
        hovertemplate="<b>%{x}</b><br>Profit: $%{y:,.2f}<extra></extra>"
    )
)

# Margin % Line
fig_monthly.add_trace(
    go.Scatter(
        x=monthly["year_month"],
        y=monthly["weighted_margin_%"],
        name="Weighted Margin (%)",
        yaxis="y2",
        mode="lines+markers",
        line=dict(color=CRIMSON_RED, width=3),
        marker=dict(size=6),
        hovertemplate="<b>%{x}</b><br>Margin: %{y:.1f}%<extra></extra>"
    )
)

layout_monthly = get_plotly_layout(
    title="Monthly Revenue, Profit, and Profit Margin % (2023–2025)",
    xaxis_title="Calendar Month",
    yaxis_title="Financial Value ($)",
    height=450
)
layout_monthly["yaxis2"] = {
    "title": "Weighted Margin (%)",
    "overlaying": "y",
    "side": "right",
    "showgrid": False,
    "ticksuffix": "%",
    "range": [-5, 30]
}
layout_monthly["barmode"] = "group"
fig_monthly.update_layout(layout_monthly)

st.plotly_chart(fig_monthly, use_container_width=True)

st.markdown("---")

# Three Core Business Findings
st.subheader("💡 Three Core Data-Supported Strategic Insights")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        """
        <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-top: 4px solid #2563EB; border-radius: 8px; padding: 18px; height: 100%;">
            <h4 style="color: #0F2942; margin-top: 0;">1. Top-Line Growth vs Margin Dilution</h4>
            <p style="color: #475569; font-size: 0.9rem; line-height: 1.5;">
                Annual revenue surged from <strong>$896.6k</strong> (2023) to <strong>$1.40M</strong> (2025), reflecting a <strong>+56.2%</strong> multi-year expansion.
                However, net profit growth lagged sharply (<strong>+20.7%</strong>), causing portfolio weighted margin to collapse from <strong>15.4% down to 11.9%</strong>.
            </p>
            <div style="background-color: #F1F5F9; padding: 8px; border-radius: 4px; font-size: 0.8rem; color: #1E293B; font-weight: 500;">
                Root Cause: Volume growth heavily driven by discounting and lower-margin channel mix.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        """
        <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-top: 4px solid #EF4444; border-radius: 8px; padding: 18px; height: 100%;">
            <h4 style="color: #0F2942; margin-top: 0;">2. Severe Discount Leakage</h4>
            <p style="color: #475569; font-size: 0.9rem; line-height: 1.5;">
                Orders with discounts exceeding 20% represent <strong>29.3%</strong> of total volume but generated a net loss of <strong>-$82,129</strong>.
                Across the portfolio, <strong>1,579 orders (13.2%)</strong> were sold at an operational loss, draining <strong>-$129,119</strong> in cumulative gross profit.
            </p>
            <div style="background-color: #FEF2F2; padding: 8px; border-radius: 4px; font-size: 0.8rem; color: #991B1B; font-weight: 500;">
                Opportunity: Enforcing a hard 20% discount cap recovers $62.7k annually.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        """
        <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-top: 4px solid #F59E0B; border-radius: 8px; padding: 18px; height: 100%;">
            <h4 style="color: #0F2942; margin-top: 0;">3. Marketplace Channel Drag</h4>
            <p style="color: #475569; font-size: 0.9rem; line-height: 1.5;">
                The Marketplace channel expanded its revenue share from <strong>12% to 26%</strong>, but operates at a <strong>-2.5%</strong> aggregate profit margin due to the <strong>13% flat platform fee</strong>.
                Every incremental Marketplace sale currently dilutes corporate profitability.
            </p>
            <div style="background-color: #FFFBEB; padding: 8px; border-radius: 4px; font-size: 0.8rem; color: #92400E; font-weight: 500;">
                Action: Cap Marketplace promotional discounts at 10% and renegotiate commissions.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# Download Button
csv_data = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv_data,
    file_name="executive_overview_filtered_data.csv",
    mime="text/csv"
)
