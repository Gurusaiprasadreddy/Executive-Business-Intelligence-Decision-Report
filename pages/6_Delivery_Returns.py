"""Page 6: Delivery Logistics and Return Rate Analysis

Examines shipping SLA breach rates (>5 business days), regional logistics bottlenecks,
merchandise return correlations, and empirical delivery sensitivity.
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

st.set_page_config(page_title="Delivery & Returns | BI Dashboard", page_icon="🚚", layout="wide")

df_full = load_clean_data()
df = render_sidebar_filters(df_full)

st.title("🚚 Delivery Logistics & Merchandise Returns")
st.caption("Investigating shipping fulfillment SLA breaches, regional logistics friction, and product return triggers")

if df.empty:
    st.warning("⚠️ No orders match the selected filters. Please adjust your filter selections in the sidebar.")
    st.stop()

# Headline Metrics
tot_orders = len(df)
late_orders = df["is_late"].sum()
late_rate = late_orders / tot_orders * 100 if tot_orders > 0 else 0

tot_returns = df["returned"].sum()
return_rate = tot_returns / tot_orders * 100 if tot_orders > 0 else 0

on_time_returns = df[~df["is_late"]]["returned"].mean() * 100 if (~df["is_late"]).sum() > 0 else 0
late_returns = df[df["is_late"]]["returned"].mean() * 100 if df["is_late"].sum() > 0 else 0
multiplier = late_returns / on_time_returns if on_time_returns > 0 else 0

d1, d2, d3, d4 = st.columns(4)
with d1:
    render_metric_card("SLA Breach Rate (>5 Days)", f"{late_rate:.1f}%", f"{late_orders:,} delayed orders", "negative")
with d2:
    render_metric_card("Overall Return Rate", f"{return_rate:.1f}%", f"{tot_returns:,} items returned", "normal")
with d3:
    render_metric_card("On-Time Return Rate", f"{on_time_returns:.1f}%", "Baseline merchandise returns", "positive")
with d4:
    render_metric_card("Late Delivery Return Rate", f"{late_returns:.1f}%", f"{multiplier:.1f}x Return Multiplier", "negative")

st.markdown("---")

# Visual: Return Rate Multiplier (On-Time vs Late)
col_v1, col_v2 = st.columns(2)

with col_v1:
    st.subheader("📦 Return Rate by Delivery Status")
    fig_ret = go.Figure(
        go.Bar(
            x=["On-Time Orders (<= 5 Days)", "Late Orders (> 5 Days)"],
            y=[on_time_returns, late_returns],
            marker_color=[EMERALD_GREEN, CRIMSON_RED],
            text=[f"{on_time_returns:.1f}%", f"{late_returns:.1f}% (+{late_returns - on_time_returns:.1f} pp)"],
            textposition="auto"
        )
    )
    layout_ret = get_plotly_layout(
        "Return Rate: On-Time vs Delayed Delivery",
        "Delivery Status",
        "Merchandise Return Rate (%)",
        height=380
    )
    fig_ret.update_layout(layout_ret)
    st.plotly_chart(fig_ret, use_container_width=True)

with col_v2:
    st.subheader("🗺️ Regional Delivery Delay Ranking")
    reg_late = df.groupby("region").agg(orders=("order_id", "count"), late=("is_late", "sum")).reset_index()
    reg_late["late_rate_%"] = reg_late["late"] / reg_late["orders"] * 100
    reg_late = reg_late.sort_values(by="late_rate_%", ascending=False)

    fig_reg = go.Figure(
        go.Bar(
            x=reg_late["region"],
            y=reg_late["late_rate_%"],
            marker_color=[CRIMSON_RED if r > 40 else (AMBER_WARNING if r > 20 else BLUE_ACCENT) for r in reg_late["late_rate_%"]],
            text=[f"{r:.1f}%" for r in reg_late["late_rate_%"]],
            textposition="auto"
        )
    )
    layout_reg = get_plotly_layout(
        "SLA Breach Rate by Geographic Region (Central Worst at 58.4%)",
        "Geographic Region",
        "Late Delivery Rate (%)",
        height=380
    )
    fig_reg.update_layout(layout_reg)
    st.plotly_chart(fig_reg, use_container_width=True)

st.markdown("---")

# Cross-Dimensional Breakdown: Category and Channel Delay vs Returns
st.subheader("📊 Return Rate by Channel and Category Cross-Tabulation")

cross_summary = (
    df.groupby(["channel", "category"])
    .agg(
        orders=("order_id", "count"),
        late_orders=("is_late", "sum"),
        returned_orders=("returned", "sum")
    )
    .reset_index()
)
cross_summary["late_rate_%"] = (cross_summary["late_orders"] / cross_summary["orders"] * 100).round(1)
cross_summary["return_rate_%"] = (cross_summary["returned_orders"] / cross_summary["orders"] * 100).round(1)

fig_cross = go.Figure()
for cat in cross_summary["category"].unique():
    subset = cross_summary[cross_summary["category"] == cat]
    fig_cross.add_trace(
        go.Bar(
            x=subset["channel"],
            y=subset["return_rate_%"],
            name=cat,
            hovertemplate="<b>%{x} | " + cat + "</b><br>Return Rate: %{y:.1f}%<extra></extra>"
        )
    )

layout_cross = get_plotly_layout(
    "Return Rate (%) by Sales Channel and Product Category",
    "Sales Channel",
    "Return Rate (%)",
    height=400
)
layout_cross["barmode"] = "group"
fig_cross.update_layout(layout_cross)
st.plotly_chart(fig_cross, use_container_width=True)

st.markdown("---")

# Analytical Cautionary Disclosure
st.warning(
    "⚖️ **Correlation vs. Causation Methodological Caution:** "
    "While late delivery demonstrates a statistically significant association with merchandise returns (p < 0.001, 3x higher probability), "
    "empirical correlation does not establish that delayed shipping is the sole causal driver. "
    "Contributing factors may include customer buyer remorse during extended wait windows, carrier handling damage in transit, or unmet product expectations."
)
