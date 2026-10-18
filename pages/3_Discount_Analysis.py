"""Page 3: Discount and Pricing Analysis

Analyzes the structural relationship between promotional discounting,
margin destruction, loss-making orders, and includes a live policy simulation model.
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
from src.kpi_engine import calculate_discount_band_metrics, calculate_weighted_profit_margin
from src.data_cleaning import FEE_STRUCTURE

st.set_page_config(page_title="Discount & Pricing | BI Dashboard", page_icon="🏷️", layout="wide")

df_full = load_clean_data()
df = render_sidebar_filters(df_full)

st.title("🏷️ Discount & Promotional Pricing Analysis")
st.caption("Quantifying discount elasticity, margin destruction thresholds, and simulated guardrail impacts")

if df.empty:
    st.warning("⚠️ No orders match the selected filters. Please adjust your filter selections in the sidebar.")
    st.stop()

# Discount Band Breakdown Table
disc_df = calculate_discount_band_metrics(df)

d1, d2, d3, d4 = st.columns(4)
zero_band = disc_df[disc_df["discount_band"] == "0%"]
deep_band = disc_df[disc_df["discount_band"] == ">30%"]

with d1:
    m_zero = zero_band["weighted_margin_%"].iloc[0] if not zero_band.empty else 0
    render_metric_card("0% Discount Margin", f"{m_zero:.1f}%", "Healthy full-price sales", "positive")
with d2:
    m_deep = deep_band["weighted_margin_%"].iloc[0] if not deep_band.empty else 0
    render_metric_card(">30% Discount Margin", f"{m_deep:.1f}%", "Deep net loss", "negative")
with d3:
    loss_share_deep = deep_band["loss_order_share_%"].iloc[0] if not deep_band.empty else 0
    render_metric_card(">30% Loss Order %", f"{loss_share_deep:.1f}%", "Majority lose money", "negative")
with d4:
    total_deep_loss = deep_band["profit"].iloc[0] if not deep_band.empty else 0
    render_metric_card(">30% Net Dollar Loss", format_currency(total_deep_loss), "Cash drain", "negative")

st.markdown("---")

# Visual Comparison: Margin & Loss Rate across Discount Tiers
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("📉 Margin Collapse by Discount Tier")
    fig_margin = go.Figure(
        go.Bar(
            x=disc_df["discount_band"],
            y=disc_df["weighted_margin_%"],
            marker_color=[EMERALD_GREEN if m >= 20 else (BLUE_ACCENT if m >= 10 else CRIMSON_RED) for m in disc_df["weighted_margin_%"]],
            text=[f"{m:.1f}%" for m in disc_df["weighted_margin_%"]],
            textposition="auto",
            hovertemplate="<b>%{x} Band</b><br>Weighted Margin: %{y:.2f}%<extra></extra>"
        )
    )
    layout_m = get_plotly_layout(
        title="Weighted Margin % Across Discount Tiers",
        xaxis_title="Discount Tier",
        yaxis_title="Weighted Profit Margin (%)",
        height=380
    )
    fig_margin.update_layout(layout_m)
    st.plotly_chart(fig_margin, use_container_width=True)

with col_chart2:
    st.subheader("⚠️ Loss-Making Order Share (%)")
    fig_loss = go.Figure(
        go.Bar(
            x=disc_df["discount_band"],
            y=disc_df["loss_order_share_%"],
            marker_color=[CRIMSON_RED if r > 20 else AMBER_WARNING if r > 5 else BLUE_ACCENT for r in disc_df["loss_order_share_%"]],
            text=[f"{r:.1f}%" for r in disc_df["loss_order_share_%"]],
            textposition="auto",
            hovertemplate="<b>%{x} Band</b><br>Loss Orders: %{y:.1f}%<extra></extra>"
        )
    )
    layout_l = get_plotly_layout(
        title="% of Orders Generating Negative Net Profit",
        xaxis_title="Discount Tier",
        yaxis_title="Loss-Making Orders (%)",
        height=380
    )
    fig_loss.update_layout(layout_l)
    st.plotly_chart(fig_loss, use_container_width=True)

st.markdown("---")

# Discount vs Margin Scatter Plot (Sampled or Aggregated)
st.subheader("🔬 Order-Level Discount vs Profit Margin Distribution")
st.caption("Visualizing the steep mechanistic trade-off between price promotion and profitability")

# Sample for smooth browser rendering if dataset is large
sample_df = df.sample(min(2000, len(df)), random_state=42)

fig_scatter = go.Figure(
    go.Scatter(
        x=sample_df["discount"] * 100,
        y=sample_df["profit_margin"] * 100,
        mode="markers",
        marker=dict(
            size=6,
            color=sample_df["is_loss_order"].map({True: CRIMSON_RED, False: NAVY_DARK}),
            opacity=0.6
        ),
        text=sample_df["order_id"],
        hovertemplate="Order: %{text}<br>Discount: %{x:.1f}%<br>Margin: %{y:.1f}%<extra></extra>"
    )
)
fig_scatter.add_hline(y=0, line_dash="dash", line_color="#64748B", annotation_text="Break-even Profit Line ($0 Margin)")
fig_scatter.add_vline(x=20, line_dash="dot", line_color=CRIMSON_RED, annotation_text="Proposed 20% Hard Cap")

layout_s = get_plotly_layout(
    title="Order Discount % vs Profit Margin % (Red = Loss Orders)",
    xaxis_title="Discount Applied (%)",
    yaxis_title="Order Profit Margin (%)",
    height=420
)
fig_scatter.update_layout(layout_s)
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# Interactive Discount Policy Simulation Engine
st.subheader("🎮 Interactive Discount Policy Simulator")
st.markdown(
    """
    <div style="background-color: #FEF3C7; border: 1px solid #F59E0B; border-radius: 6px; padding: 12px; margin-bottom: 16px; font-size: 0.85rem; color: #92400E;">
        ⚙️ <strong>Simulation Model:</strong> Test the financial impact of capping maximum discount thresholds.
        When orders exceeding the cap are repriced, assume a portion of customers may churn due to higher prices (Retention Sensitivity).
    </div>
    """,
    unsafe_allow_html=True
)

sim_col1, sim_col2 = st.columns([1, 2])

with sim_col1:
    st.markdown("##### Simulation Controls")
    max_discount_cap = st.slider("Maximum Allowed Discount Cap (%)", min_value=10, max_value=30, value=20, step=5)
    customer_retention_rate = st.slider("Customer Retention Rate at Capped Price (%)", min_value=50, max_value=100, value=70, step=5)
    st.caption("E.g. at 70%, 30% of high-discount orders walk away; 70% buy at the capped rate.")

with sim_col2:
    # Run Simulation Logic
    cap_fraction = max_discount_cap / 100.0
    ret_fraction = customer_retention_rate / 100.0

    # Orders affected
    affected_mask = df["discount"] > cap_fraction
    affected_count = affected_mask.sum()
    baseline_affected_profit = df.loc[affected_mask, "profit"].sum()

    # Reprice affected orders:
    # new_sales = qty * unit_price * (1 - cap_fraction)
    # new_profit = (new_sales * (1 - fee) - qty * unit_cost) * ret_fraction
    sim_sales = df.loc[affected_mask, "quantity"] * df.loc[affected_mask, "unit_price"] * (1 - cap_fraction)
    sim_fee = df.loc[affected_mask, "channel"].map(FEE_STRUCTURE)
    sim_cost = df.loc[affected_mask, "quantity"] * df.loc[affected_mask, "unit_cost"]
    sim_profit_single = sim_sales * (1 - sim_fee) - sim_cost
    simulated_new_profit = (sim_profit_single * ret_fraction).sum()

    net_profit_delta = simulated_new_profit - baseline_affected_profit

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        render_metric_card("Affected Orders", f"{affected_count:,}", f"{affected_count / len(df) * 100:.1f}% of volume", "normal")
    with sc2:
        render_metric_card("Baseline Profit of Orders", format_currency(baseline_affected_profit), "Current drain", "negative")
    with sc3:
        p_color = "positive" if net_profit_delta > 0 else "negative"
        render_metric_card("Projected Profit Uplift", format_currency(net_profit_delta), f"{net_profit_delta / df['profit'].sum() * 100:+.1f}% portfolio boost", p_color)

    st.markdown(
        f"""
        **Simulation Result:** Capping discounts at **{max_discount_cap}%** with **{customer_retention_rate}% retention**
        converts a **{format_currency(baseline_affected_profit)}** loss into **{format_currency(simulated_new_profit)}** in net contribution,
        generating **{format_currency(net_profit_delta)}** in incremental profit.
        """
    )

# Download Table
csv_data = disc_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download Discount Band Breakdown as CSV",
    data=csv_data,
    file_name="discount_band_analysis.csv",
    mime="text/csv"
)
