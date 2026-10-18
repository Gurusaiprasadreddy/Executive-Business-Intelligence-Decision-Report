"""Page 2: Revenue and Profitability Analysis

Deconstructs revenue drivers, product category rankings, subcategory margins,
loss-making orders, and the cumulative profit bridge from gross sales to net contribution.
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
    CYAN_ACCENT,
    CRIMSON_RED,
    EMERALD_GREEN
)
from src.kpi_engine import (
    calculate_annual_metrics,
    calculate_category_metrics,
    calculate_weighted_profit_margin
)

st.set_page_config(page_title="Revenue & Profitability | BI Dashboard", page_icon="💰", layout="wide")

df_full = load_clean_data()
df = render_sidebar_filters(df_full)

st.title("💰 Revenue & Profitability Decomposition")
st.caption("Detailed margin contribution, product category rankings, and full-spectrum profit waterfall")

if df.empty:
    st.warning("⚠️ No orders match the selected filters. Please adjust your filter selections in the sidebar.")
    st.stop()

# Annual Trend Table and Growth Metrics
st.subheader("📊 Annual Performance Summary")
annual_df = calculate_annual_metrics(df)

# Render formatted dataframe
display_annual = annual_df.copy()
display_annual["Revenue"] = display_annual["Revenue"].apply(lambda v: f"${v:,.2f}")
display_annual["Profit"] = display_annual["Profit"].apply(lambda v: f"${v:,.2f}")
display_annual["Weighted_Profit_Margin_%"] = display_annual["Weighted_Profit_Margin_%"].apply(lambda v: f"{v:.2f}%")
display_annual["AOV"] = display_annual["AOV"].apply(lambda v: f"${v:,.2f}")
display_annual["Return_Rate_%"] = display_annual["Return_Rate_%"].apply(lambda v: f"{v:.2f}%")
display_annual["Late_Rate_%"] = display_annual["Late_Rate_%"].apply(lambda v: f"{v:.2f}%")

st.dataframe(display_annual, use_container_width=True, hide_index=True)

st.markdown("---")

# Profit Waterfall Bridge
st.subheader("🌉 Accounting Profit Bridge (Gross Potential Sales to Net Profit)")
st.caption("Explicit decomposition of gross merchandise volume, promotional discounting, channel fees, and product cost")

# Reconstruct gross sales before discount
gross_sales = (df["quantity"] * df["unit_price"]).sum()
discount_loss = gross_sales - df["sales"].sum()
net_sales = df["sales"].sum()
channel_fees = (df["sales"] * df["channel_fee"]).sum()
cogs = (df["quantity"] * df["unit_cost"]).sum()
net_profit = df["profit"].sum()

fig_bridge = go.Figure(
    go.Waterfall(
        name="Profit Bridge",
        orientation="v",
        measure=["relative", "relative", "total", "relative", "relative", "total"],
        x=[
            "Gross List Price Value",
            "Promotional Discounts",
            "Recognized Net Sales",
            "Channel Fees (Platform)",
            "Cost of Goods Sold (COGS)",
            "Final Contribution Profit"
        ],
        textposition="outside",
        text=[
            f"${gross_sales:,.0f}",
            f"-${discount_loss:,.0f}",
            f"${net_sales:,.0f}",
            f"-${channel_fees:,.0f}",
            f"-${cogs:,.0f}",
            f"${net_profit:,.0f}"
        ],
        y=[gross_sales, -discount_loss, 0, -channel_fees, -cogs, 0],
        connector={"line": {"color": "#94A3B8"}},
        decreasing={"marker": {"color": CRIMSON_RED}},
        increasing={"marker": {"color": EMERALD_GREEN}},
        totals={"marker": {"color": NAVY_DARK}}
    )
)

layout_bridge = get_plotly_layout(
    title="Comprehensive Revenue-to-Profit Waterfall Bridge ($)",
    xaxis_title="Accounting Cost & Revenue Layers",
    yaxis_title="Total Value ($)",
    height=450
)
fig_bridge.update_layout(layout_bridge)
st.plotly_chart(fig_bridge, use_container_width=True)

st.markdown("---")

# Category and Sub-Category Rankings
col_cat1, col_cat2 = st.columns([1, 1])

with col_cat1:
    st.subheader("📦 Performance by Category")
    cat_df = calculate_category_metrics(df)

    fig_cat = go.Figure()
    fig_cat.add_trace(
        go.Bar(
            x=cat_df["category"],
            y=cat_df["revenue"],
            name="Revenue ($)",
            marker_color=NAVY_DARK,
            hovertemplate="Revenue: $%{y:,.2f}<extra></extra>"
        )
    )
    fig_cat.add_trace(
        go.Bar(
            x=cat_df["category"],
            y=cat_df["profit"],
            name="Profit ($)",
            marker_color=BLUE_ACCENT,
            hovertemplate="Profit: $%{y:,.2f}<extra></extra>"
        )
    )
    layout_cat = get_plotly_layout(
        title="Revenue & Profit by Category",
        xaxis_title="Product Category",
        yaxis_title="Financials ($)",
        height=380
    )
    layout_cat["barmode"] = "group"
    fig_cat.update_layout(layout_cat)
    st.plotly_chart(fig_cat, use_container_width=True)

with col_cat2:
    st.subheader("🏷️ Category Margin Comparison")
    fig_cat_margin = go.Figure(
        go.Bar(
            x=cat_df["category"],
            y=cat_df["weighted_margin_%"],
            marker_color=[EMERALD_GREEN if m >= 20 else (BLUE_ACCENT if m >= 10 else CRIMSON_RED) for m in cat_df["weighted_margin_%"]],
            text=[f"{m:.1f}%" for m in cat_df["weighted_margin_%"]],
            textposition="auto",
            hovertemplate="<b>%{x}</b><br>Weighted Margin: %{y:.2f}%<extra></extra>"
        )
    )
    layout_cat_margin = get_plotly_layout(
        title="Weighted Margin % by Category (Office Supplies Leads at 35.2%)",
        xaxis_title="Product Category",
        yaxis_title="Weighted Profit Margin (%)",
        height=380
    )
    fig_cat_margin.update_layout(layout_cat_margin)
    st.plotly_chart(fig_cat_margin, use_container_width=True)

# Sub-Category Rankings Table and Analysis
st.subheader("📑 Sub-Category Profitability Breakdown")
subcat_summary = (
    df.groupby(["category", "sub_category"])
    .agg(
        orders=("order_id", "count"),
        revenue=("sales", "sum"),
        profit=("profit", "sum")
    )
    .reset_index()
)
subcat_summary["weighted_margin_%"] = (subcat_summary["profit"] / subcat_summary["revenue"] * 100).round(2)
subcat_summary = subcat_summary.sort_values(by="profit", ascending=False)

fig_subcat = go.Figure(
    go.Bar(
        y=subcat_summary["sub_category"],
        x=subcat_summary["profit"],
        orientation="h",
        marker_color=[EMERALD_GREEN if p > 0 else CRIMSON_RED for p in subcat_summary["profit"]],
        text=[f"${p:,.0f} ({m:.1f}%)" for p, m in zip(subcat_summary["profit"], subcat_summary["weighted_margin_%"])],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Profit: $%{x:,.2f}<extra></extra>"
    )
)
layout_subcat = get_plotly_layout(
    title="Sub-Category Net Profit Ranking & Margins",
    xaxis_title="Net Contribution Profit ($)",
    yaxis_title="Sub-Category",
    height=480
)
fig_subcat.update_layout(layout_subcat)
st.plotly_chart(fig_subcat, use_container_width=True)

st.markdown("---")

# Loss-Making Orders Analysis
st.subheader("🚨 Loss-Making Orders Deep Dive")
loss_orders = df[df["is_loss_order"]]
loss_count = len(loss_orders)
loss_share = loss_count / len(df) * 100 if len(df) > 0 else 0
total_loss = loss_orders["profit"].sum()

lc1, lc2, lc3 = st.columns(3)
with lc1:
    render_metric_card("Loss-Making Orders", f"{loss_count:,}", f"{loss_share:.1f}% of filtered volume", "negative", "Orders with profit < $0")
with lc2:
    render_metric_card("Cumulative Cash Loss", format_currency(total_loss), "Capital drain", "negative", "Net negative profit sum")
with lc3:
    worst_order = loss_orders["profit"].min() if not loss_orders.empty else 0
    render_metric_card("Worst Single Order", format_currency(worst_order), "Deep margin erosion", "negative", "Single worst order profit")

# Loss by channel and category
col_loss_chn, col_loss_cat = st.columns(2)
with col_loss_chn:
    loss_by_chn = loss_orders.groupby("channel")["profit"].agg(["count", "sum"]).reset_index()
    loss_by_chn["sum"] = loss_by_chn["sum"].abs()
    fig_loss_chn = go.Figure(
        go.Bar(
            x=loss_by_chn["channel"],
            y=loss_by_chn["sum"],
            marker_color=CRIMSON_RED,
            text=[f"${s:,.0f} ({c} orders)" for s, c in zip(loss_by_chn["sum"], loss_by_chn["count"])],
            textposition="auto"
        )
    )
    layout_lchn = get_plotly_layout("Loss Amount by Channel ($ Drain)", "Channel", "Total Losses ($)", height=320)
    fig_loss_chn.update_layout(layout_lchn)
    st.plotly_chart(fig_loss_chn, use_container_width=True)

with col_loss_cat:
    loss_by_cat = loss_orders.groupby("category")["profit"].agg(["count", "sum"]).reset_index()
    loss_by_cat["sum"] = loss_by_cat["sum"].abs()
    fig_loss_cat = go.Figure(
        go.Bar(
            x=loss_by_cat["category"],
            y=loss_by_cat["sum"],
            marker_color=AMBER_WARNING,
            text=[f"${s:,.0f} ({c} orders)" for s, c in zip(loss_by_cat["sum"], loss_by_cat["count"])],
            textposition="auto"
        )
    )
    layout_lcat = get_plotly_layout("Loss Amount by Category ($ Drain)", "Category", "Total Losses ($)", height=320)
    fig_loss_cat.update_layout(layout_lcat)
    st.plotly_chart(fig_loss_cat, use_container_width=True)

# CSV Download
csv_data = subcat_summary.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download Sub-Category Breakdown as CSV",
    data=csv_data,
    file_name="subcategory_profitability_breakdown.csv",
    mime="text/csv"
)
