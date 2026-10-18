"""Page 4: Channel and Regional Performance Analysis

Investigates omnichannel profitability, the 13% Marketplace commission drag,
mix shifts over time, and fulfillment performance across geographic sales regions.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from src.dashboard_utils import (
    load_clean_data,
    render_sidebar_filters,
    get_plotly_layout,
    render_metric_card,
    format_currency,
    format_pct,
    NAVY_DARK,
    BLUE_ACCENT,
    CRIMSON_RED,
    EMERALD_GREEN,
    AMBER_WARNING
)
from src.kpi_engine import calculate_channel_metrics, calculate_regional_metrics

st.set_page_config(page_title="Channel & Geography | BI Dashboard", page_icon="🌐", layout="wide")

df_full = load_clean_data()
df = render_sidebar_filters(df_full)

st.title("🌐 Channel & Regional Analytics")
st.caption("Examining omnichannel unit economics, platform commission fees, and regional operational efficiency")

if df.empty:
    st.warning("⚠️ No orders match the selected filters. Please adjust your filter selections in the sidebar.")
    st.stop()

# Channel Overview Metrics
chn_df = calculate_channel_metrics(df)

st.subheader("🛒 Channel Unit Economics Comparison")

c_cols = st.columns(len(chn_df))
for i, (_, row) in enumerate(chn_df.iterrows()):
    with c_cols[i]:
        m = row["weighted_margin_%"]
        m_color = "positive" if m >= 18 else ("normal" if m >= 10 else "negative")
        render_metric_card(
            f"{row['channel']}",
            format_currency(row["profit"]),
            delta=f"{m:.1f}% Margin",
            delta_color=m_color,
            subtext=f"{format_currency(row['revenue'])} rev ({row['revenue_share_%']:.1f}% mix)"
        )

st.markdown("---")

# Visual: Channel Revenue vs Profit & Margin
col_chn1, col_chn2 = st.columns(2)

with col_chn1:
    st.subheader("📊 Channel Financial Contribution")
    fig_chn = go.Figure()
    fig_chn.add_trace(go.Bar(x=chn_df["channel"], y=chn_df["revenue"], name="Revenue ($)", marker_color=NAVY_DARK))
    fig_chn.add_trace(go.Bar(x=chn_df["channel"], y=chn_df["profit"], name="Profit ($)", marker_color=BLUE_ACCENT))
    layout_c = get_plotly_layout("Revenue vs Profit by Channel ($)", "Channel", "Financial Total ($)", height=380)
    layout_c["barmode"] = "group"
    fig_chn.update_layout(layout_c)
    st.plotly_chart(fig_chn, use_container_width=True)

with col_chn2:
    st.subheader("⚠️ Weighted Profit Margin by Channel (%)")
    fig_cm = go.Figure(
        go.Bar(
            x=chn_df["channel"],
            y=chn_df["weighted_margin_%"],
            marker_color=[EMERALD_GREEN if m >= 15 else (BLUE_ACCENT if m >= 10 else CRIMSON_RED) for m in chn_df["weighted_margin_%"]],
            text=[f"{m:.1f}%" for m in chn_df["weighted_margin_%"]],
            textposition="auto"
        )
    )
    layout_cm = get_plotly_layout("Weighted Contribution Margin by Channel", "Channel", "Weighted Margin (%)", height=380)
    fig_cm.update_layout(layout_cm)
    st.plotly_chart(fig_cm, use_container_width=True)

st.markdown("---")

# Channel Mix Trend Over Time (2023 vs 2024 vs 2025)
st.subheader("📈 Omnichannel Mix Shift Over Time (2023–2025)")

df["order_year"] = df["order_date"].dt.year
mix_yearly = df.groupby(["order_year", "channel"])["sales"].sum().unstack().fillna(0)
mix_pct = mix_yearly.div(mix_yearly.sum(axis=1), axis=0) * 100

fig_mix = go.Figure()
colors = {"Online": BLUE_ACCENT, "Retail Store": NAVY_DARK, "Marketplace": CRIMSON_RED}
for ch in mix_pct.columns:
    fig_mix.add_trace(
        go.Bar(
            x=[str(y) for y in mix_pct.index],
            y=mix_pct[ch],
            name=ch,
            marker_color=colors.get(ch, "#64748B"),
            text=[f"{v:.1f}%" for v in mix_pct[ch]],
            textposition="inside"
        )
    )

layout_mix = get_plotly_layout("Revenue Share Mix % by Channel (Marketplace expanded from 12% to 26%)", "Year", "Share of Revenue (%)", height=380)
layout_mix["barmode"] = "stack"
fig_mix.update_layout(layout_mix)
st.plotly_chart(fig_mix, use_container_width=True)

st.markdown("---")

# Regional Performance Analysis
st.subheader("🗺️ Regional Geographic Performance")
reg_df = calculate_regional_metrics(df)

col_reg1, col_reg2 = st.columns(2)

with col_reg1:
    fig_reg = go.Figure()
    fig_reg.add_trace(go.Bar(x=reg_df["region"], y=reg_df["revenue"], name="Revenue ($)", marker_color=NAVY_DARK))
    fig_reg.add_trace(go.Bar(x=reg_df["region"], y=reg_df["profit"], name="Profit ($)", marker_color=BLUE_ACCENT))
    layout_r = get_plotly_layout("Regional Sales & Contribution Profit ($)", "Region", "Total ($)", height=380)
    layout_r["barmode"] = "group"
    fig_reg.update_layout(layout_r)
    st.plotly_chart(fig_reg, use_container_width=True)

with col_reg2:
    fig_rlate = go.Figure(
        go.Bar(
            x=reg_df["region"],
            y=reg_df["late_rate_%"],
            marker_color=[CRIMSON_RED if r > 40 else (AMBER_WARNING if r > 20 else BLUE_ACCENT) for r in reg_df["late_rate_%"]],
            text=[f"{r:.1f}%" for r in reg_df["late_rate_%"]],
            textposition="auto"
        )
    )
    layout_rl = get_plotly_layout("Regional Shipping SLA Breach Rate (% >5 Days)", "Region", "Late Orders (%)", height=380)
    fig_rlate.update_layout(layout_rl)
    st.plotly_chart(fig_rlate, use_container_width=True)

# Download Table
csv_data = chn_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download Channel Performance as CSV",
    data=csv_data,
    file_name="channel_performance_summary.csv",
    mime="text/csv"
)
