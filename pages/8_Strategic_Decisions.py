"""Page 8: Strategic Decisions and Validated Financial Scenario Engine

Presents the three executive turnaround recommendations, the 36-month monthly cash flow
model, payback trajectory, and transparently details assumptions and model governance caveats.
Directly integrated with src.roi_model without duplicating financial formulas.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from src.dashboard_utils import (
    load_clean_data,
    load_authoritative_metrics,
    render_metric_card,
    get_plotly_layout,
    format_currency,
    format_pct,
    NAVY_DARK,
    BLUE_ACCENT,
    CRIMSON_RED,
    EMERALD_GREEN,
    AMBER_WARNING,
    SLATE_GRAY,
)
from src.roi_model import (
    run_scenario,
    build_scenarios_summary,
    build_monthly_cash_flow_df,
    build_break_even_df,
    run_sensitivity_analysis,
    build_assumptions_export,
    ASSUMPTION_REGISTRY,
    SCENARIO_MULTIPLIERS,
    SENSITIVITY_VARIABLES,
)

st.set_page_config(page_title="Strategic Scenarios | BI Dashboard", page_icon="🎯", layout="wide")

st.title("🎯 Strategic Decisions & Validated Financial Scenario Engine")
st.caption("Three-Pillar Turnaround Strategy, 36-Month Implementation Cash Flow, and Sensitivity Analysis")

# Governance and Causality Callout Banner
st.markdown(
    """
    <div style="background-color: #FEF3C7; border-left: 4px solid #F59E0B; padding: 12px 16px; border-radius: 4px; margin-bottom: 20px;">
        <span style="color: #92400E; font-size: 0.9rem;">
            ⚠️ <strong>Financial Governance & Model Provenance Status:</strong>
            Projections below are calculated by the validated Stage 4 ROI Engine (<code>src/roi_model.py</code>).
            Historical baseline metrics (2025 revenue: $1.40M, profit: $167.1k, margin: 11.93%) are 100% data-verified.
            <strong>Causal Warning:</strong> Observational associations (e.g. discount cliffs, delivery delay vs return rates)
            do not guarantee causal uplift upon intervention. Customer price elasticity, retention spend haircuts, and marketplace
            commission cuts are explicitly labeled <code>USER_SUPPLIED</code> or <code>HYPOTHETICAL</code>.
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_2025_data():
    df = load_clean_data()
    return df[df["order_date"].dt.year == 2025].copy()


@st.cache_data
def get_all_scenarios_and_results(df_2025):
    scenarios_df, results = build_scenarios_summary(df_2025)
    monthly_cf_df = build_monthly_cash_flow_df(results)
    break_even_df = build_break_even_df(results, df_2025=df_2025)
    return scenarios_df, results, monthly_cf_df, break_even_df


@st.cache_data
def get_cached_sensitivity(df_2025):
    return run_sensitivity_analysis(df_2025, n_steps=5)


df_2025 = load_2025_data()
scenarios_df, results_dict, monthly_cf_df, break_even_df = get_all_scenarios_and_results(df_2025)

# Interactive Scenario View Selector
col_sel, col_info = st.columns([1, 2])
with col_sel:
    selected_scenario = st.selectbox(
        "Active Scenario View",
        ["Base", "Conservative", "Optimistic"],
        index=0,
        help="Switch between audited risk profiles. Base represents the recommended management case.",
    )
with col_info:
    sm = SCENARIO_MULTIPLIERS[selected_scenario]
    delay_txt = f"{sm['launch_delay_months']} mo delay" if sm['launch_delay_months'] > 0 else "On-schedule launch"
    st.info(
        f"**{selected_scenario} Case Parameters:** Order Retention: {sm['r1_order_retention']*100:.0f}%, "
        f"MP Fee Cut: {sm['r2_fee_reduction_pp']:.1f}pp, Retention Uplift: +{sm['r3_retention_uplift_pp']:.2f}pp, "
        f"Cost Multiplier: {sm['cost_multiplier']*100:.0f}%, Implementation: {delay_txt}."
    )

active_res = results_dict[selected_scenario]

# Headline ROI Summary Cards for Selected Scenario
c1, c2, c3, c4 = st.columns(4)
with c1:
    baseline_profit = 167087.95
    pct_lift = (active_res.total_annual_benefit / baseline_profit) * 100.0
    render_metric_card(
        "Annual Profit Uplift",
        format_currency(active_res.total_annual_benefit),
        f"+{pct_lift:.1f}% over 2025 baseline",
        "positive",
        "Recurring annual run-rate",
    )
with c2:
    capex_txt = f"Capex: {format_currency(active_res.total_one_time_cost)} | Opex: {format_currency(active_res.total_annual_opex)}/yr"
    render_metric_card(
        "3-Year Total Investment",
        format_currency(active_res.total_cost_36m),
        capex_txt,
        "normal",
        "Capex + recurring operating cost",
    )
with c3:
    render_metric_card(
        "3-Year Net Benefit",
        format_currency(active_res.total_net_benefit_36m),
        f"NPV (10%): {format_currency(active_res.npv_10pct)}",
        "positive" if active_res.total_net_benefit_36m > 0 else "negative",
        "Undiscounted 36-month net cash",
    )
with c4:
    pb_label = f"Month {active_res.combined_payback_month}" if active_res.combined_payback_month else "Never (>36m)"
    render_metric_card(
        "Portfolio ROI & Payback",
        f"{active_res.total_roi_pct:.1f}% ROI",
        f"Break-even: {pb_label}",
        "positive" if active_res.total_roi_pct > 0 else "negative",
        f"Combined payback: {pb_label}",
    )

st.markdown("---")

# The Three Strategic Recommendations Breakdown
st.subheader("🏛️ The Three Strategic Pillars (Audited Standalone Breakdown)")

p1, p2, p3 = st.columns(3)
r1 = active_res.rec1
r2 = active_res.rec2
r3 = active_res.rec3

with p1:
    r1_pb = f"Month {r1.payback_month}" if r1.payback_month else "Never (>36m)"
    st.markdown(
        f"""
        <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 18px; height: 100%;">
            <div style="font-size: 0.8rem; color: #2563EB; font-weight: 700; text-transform: uppercase;">Pillar 1 — Pricing Governance</div>
            <h4 style="margin: 6px 0 10px 0; color: #0F2942;">{r1.name}</h4>
            <p style="color: #475569; font-size: 0.85rem; line-height: 1.4;">
                Cap commercial discounts at <strong>20% maximum</strong> across all channels.
                Reprices excess discount orders with assumed <strong>{sm['r1_order_retention']*100:.0f}% order retention</strong>.
                Eliminates chronic negative margin on &gt;20% sales (-$40.1k in 2025).
            </p>
            <hr style="border: none; border-top: 1px solid #E2E8F0; margin: 12px 0;">
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem;">
                <span style="color: #64748B;">Annual Uplift:</span>
                <strong style="color: #10B981;">+{format_currency(r1.annual_benefit_run_rate)}/yr</strong>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-top: 4px;">
                <span style="color: #64748B;">3-Yr Investment:</span>
                <strong style="color: #0F2942;">{format_currency(r1.total_cost_36m)}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-top: 4px;">
                <span style="color: #64748B;">3-Yr Net Benefit:</span>
                <strong style="color: #10B981;">{format_currency(r1.net_benefit_36m)}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-top: 4px;">
                <span style="color: #64748B;">Pillar Payback:</span>
                <strong style="color: #2563EB;">{r1_pb}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with p2:
    r2_pb = f"Month {r2.payback_month}" if r2.payback_month else "Never (>36m)"
    st.markdown(
        f"""
        <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 18px; height: 100%;">
            <div style="font-size: 0.8rem; color: #F59E0B; font-weight: 700; text-transform: uppercase;">Pillar 2 — Channel Strategy</div>
            <h4 style="margin: 6px 0 10px 0; color: #0F2942;">{r2.name}</h4>
            <p style="color: #475569; font-size: 0.85rem; line-height: 1.4;">
                Cap Marketplace promotional discounts at <strong>10%</strong> and negotiate fee commission from 13% down by 
                <strong>{sm['r2_fee_reduction_pp']:.1f}pp</strong>.
                Applied on post-Rec1 portfolio to eliminate double-counting.
            </p>
            <hr style="border: none; border-top: 1px solid #E2E8F0; margin: 12px 0;">
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem;">
                <span style="color: #64748B;">Annual Uplift:</span>
                <strong style="color: #10B981;">+{format_currency(r2.annual_benefit_run_rate)}/yr</strong>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-top: 4px;">
                <span style="color: #64748B;">3-Yr Investment:</span>
                <strong style="color: #0F2942;">{format_currency(r2.total_cost_36m)}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-top: 4px;">
                <span style="color: #64748B;">3-Yr Net Benefit:</span>
                <strong style="color: #10B981;">{format_currency(r2.net_benefit_36m)}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-top: 4px;">
                <span style="color: #64748B;">Pillar Payback:</span>
                <strong style="color: #2563EB;">{r2_pb}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with p3:
    r3_pb = f"Month {r3.payback_month}" if r3.payback_month else "Never (>36m)"
    r3_net_color = "#10B981" if r3.net_benefit_36m >= 0 else "#DC2626"
    st.markdown(
        f"""
        <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 18px; height: 100%;">
            <div style="font-size: 0.8rem; color: #10B981; font-weight: 700; text-transform: uppercase;">Pillar 3 — Operations & Retention</div>
            <h4 style="margin: 6px 0 10px 0; color: #0F2942;">{r3.name}</h4>
            <p style="color: #475569; font-size: 0.85rem; line-height: 1.4;">
                Overhaul Central region 3PL fulfillment (target {sm['r3_central_late_rate_target']*100:.0f}% late) to reduce return rates.
                Target customer retention uplift (+{sm['r3_retention_uplift_pp']:.2f}pp) with ${sm['r3_avg_retained_revenue']:,.0f} spend haircut.
            </p>
            <hr style="border: none; border-top: 1px solid #E2E8F0; margin: 12px 0;">
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem;">
                <span style="color: #64748B;">Annual Uplift:</span>
                <strong style="color: #10B981;">+{format_currency(r3.annual_benefit_run_rate)}/yr</strong>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-top: 4px;">
                <span style="color: #64748B;">3-Yr Investment:</span>
                <strong style="color: #0F2942;">{format_currency(r3.total_cost_36m)}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-top: 4px;">
                <span style="color: #64748B;">3-Yr Net Benefit:</span>
                <strong style="color: {r3_net_color};">{format_currency(r3.net_benefit_36m)}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-top: 4px;">
                <span style="color: #64748B;">Pillar Payback:</span>
                <strong style="color: {r3_net_color};">{r3_pb}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# Cumulative Payback Trajectory Curve (36 Months)
st.subheader("📈 36-Month Cumulative Cash Flow Trajectory")

fig_cf = go.Figure()

colors = {
    "Conservative": CRIMSON_RED,
    "Base": NAVY_DARK,
    "Optimistic": EMERALD_GREEN,
}

for sc_name in ["Conservative", "Base", "Optimistic"]:
    sc_df = monthly_cf_df[monthly_cf_df["scenario"] == sc_name].sort_values("month")
    width = 3.5 if sc_name == selected_scenario else 1.8
    dash = "solid" if sc_name == selected_scenario else "dot"
    fig_cf.add_trace(
        go.Scatter(
            x=[f"M{m}" for m in sc_df["month"]],
            y=sc_df["cumulative_net_cash_flow"],
            mode="lines+markers",
            name=f"{sc_name} Case",
            line=dict(color=colors[sc_name], width=width, dash=dash),
            hovertemplate=f"<b>{sc_name} Month %{{x}}</b><br>Cumulative: $%{{y:,.2f}}<extra></extra>",
        )
    )

fig_cf.add_hline(y=0, line_dash="dash", line_color=SLATE_GRAY, annotation_text="Break-Even Threshold ($0)")

# Add break-even marker for active scenario
pb_m = active_res.combined_payback_month
if pb_m is not None:
    fig_cf.add_vline(
        x=f"M{pb_m}",
        line_dash="dashdot",
        line_color=BLUE_ACCENT,
        annotation_text=f"{selected_scenario} Payback (Month {pb_m})",
    )

layout_cf = get_plotly_layout(
    "36-Month Cumulative Net Cash Flow ($) — Audited Trajectory",
    "Implementation Month",
    "Cumulative Net Cash ($)",
    height=450,
)
fig_cf.update_layout(layout_cf)
st.plotly_chart(fig_cf, use_container_width=True)

st.markdown("---")

# Audited Scenario Comparison Table
st.subheader("⚖️ Scenario Comparison & Break-Even Analysis")

tab_scenarios, tab_breakeven = st.tabs(["📋 Complete Recommendations Matrix", "🎯 Break-Even Benchmarks"])

with tab_scenarios:
    formatted_scenarios = scenarios_df.copy()
    num_cols = [
        "annual_benefit_run_rate",
        "annual_revenue_delta",
        "annual_contrib_profit_delta",
        "one_time_cost",
        "annual_opex",
        "total_cost_36m",
        "net_benefit_36m",
    ]
    for c in num_cols:
        formatted_scenarios[c] = formatted_scenarios[c].apply(
            lambda x: format_currency(x) if isinstance(x, (int, float)) and not pd.isna(x) else ("" if pd.isna(x) else str(x))
        )
    formatted_scenarios["roi_pct"] = formatted_scenarios["roi_pct"].apply(
        lambda x: format_pct(x) if isinstance(x, (int, float)) and not pd.isna(x) else ("" if pd.isna(x) else str(x))
    )
    st.dataframe(formatted_scenarios, use_container_width=True, hide_index=True)

with tab_breakeven:
    formatted_be = break_even_df.copy()
    for col in ["total_annual_benefit", "total_cost_36m", "total_net_benefit_36m", "npv_10pct_discount_rate", "break_even_annual_benefit"]:
        formatted_be[col] = formatted_be[col].apply(lambda x: format_currency(x) if isinstance(x, (int, float)) else str(x))
    formatted_be["total_roi_pct"] = formatted_be["total_roi_pct"].apply(lambda x: format_pct(x) if isinstance(x, (int, float)) else str(x))
    st.dataframe(formatted_be, use_container_width=True, hide_index=True)

st.markdown("---")

# Sensitivity Analysis Section
st.subheader("📊 One-at-a-Time (OAT) Sensitivity Sweeps")
st.caption("Inspect the sensitivity of 36-month net cash flow, ROI, and payback period across 7 critical operational levers.")

sensitivity_df = get_cached_sensitivity(df_2025)

col_var, col_chart = st.columns([1, 2])
with col_var:
    var_labels = {
        "r1_order_retention": "Rec 1: High-Discount Order Retention Rate",
        "r2_marketplace_order_retention": "Rec 2: Marketplace Order Retention Rate",
        "r2_fee_reduction_pp": "Rec 2: Marketplace Fee Cut (pp)",
        "r3_retention_uplift_pp": "Rec 3: Customer Retention Rate Uplift (pp)",
        "r3_avg_retained_revenue": "Rec 3: Average Retained Customer Annual Spend ($)",
        "r3_central_late_rate_target": "Rec 3: Central Region Target Late Shipping Rate",
        "r3_other_improvement_pct": "Rec 3: Non-Central Shipping Improvement (%)",
        "r3_return_rate_if_late": "Rec 3: Return Rate on Late Deliveries",
        "cost_multiplier": "Execution: Implementation Cost Multiplier",
        "launch_delay_months": "Execution: Program Launch Delay (Months)",
    }
    selected_var = st.selectbox(
        "Sensitivity Variable",
        list(var_labels.keys()),
        format_func=lambda x: var_labels.get(x, x),
    )
    var_sub = sensitivity_df[sensitivity_df["variable"] == selected_var].sort_values("value")
    st.dataframe(
        var_sub[["value", "total_annual_benefit", "total_net_36m", "roi_pct", "payback_month"]].rename(
            columns={
                "value": "Param Value",
                "total_annual_benefit": "Annual Uplift ($)",
                "total_net_36m": "3-Yr Net Cash ($)",
                "roi_pct": "ROI (%)",
                "payback_month": "Payback Month",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

with col_chart:
    fig_sens = go.Figure()
    fig_sens.add_trace(
        go.Scatter(
            x=var_sub["value"],
            y=var_sub["total_net_36m"],
            mode="lines+markers",
            name="3-Yr Net Benefit ($)",
            line=dict(color=BLUE_ACCENT, width=3),
            hovertemplate="Value: %{x}<br>3-Yr Net Cash: $%{y:,.0f}<extra></extra>",
        )
    )
    fig_sens.update_layout(
        get_plotly_layout(
            f"Sensitivity: 3-Year Net Benefit vs {var_labels.get(selected_var, selected_var)}",
            "Parameter Value",
            "3-Year Net Cash ($)",
            height=380,
        )
    )
    st.plotly_chart(fig_sens, use_container_width=True)

st.markdown("---")

# Assumption Provenance Registry & Limitations
st.subheader("📚 Assumption Provenance Registry & Governance Caveats")

assumptions_df = build_assumptions_export()

tag_filter = st.multiselect(
    "Filter Provenance Tier",
    ["DATA_VERIFIED", "USER_SUPPLIED", "HYPOTHETICAL"],
    default=["DATA_VERIFIED", "USER_SUPPLIED", "HYPOTHETICAL"],
)
filtered_assumptions = assumptions_df[assumptions_df["source"].isin(tag_filter)]
st.dataframe(filtered_assumptions, use_container_width=True, hide_index=True)

st.markdown(
    """
    #### Key Methodological Caveats for Executive Decision-Makers:
    1. **Recommendation 3 Standalone Viability Warning:** In both Conservative and Base scenarios, Recommendation 3
       incurs **$9,000/year in operating opex** against only **$7,314/year in annual benefits** ($1,911 fulfillment return savings + $5,403 retention profit).
       On a standalone basis, Rec 3 runs at an annual operating deficit of -$1,686/yr and **never pays back** its $12k initial outlay.
       It only breaks even if retained churner spend exceeds **$1,438/customer** (higher than the historical repeat customer average of $1,292).
    2. **Anti-Double-Counting Architecture:** Benefits are modeled sequentially. Rec 1 reprices all >20% discount transactions.
       Rec 2 only touches remaining Marketplace orders (>10% discount). Rec 3 floors order losses to $0 so it does not take credit for losses
       already eliminated in Rec 1 and Rec 2.
    3. **Observational vs. Causal Evidence:** High discounts correlate strongly with negative margin ($r = -0.70$).
       However, capping discounts assumes customer churn will not exceed 30%. If churn reaches 50%, Rec 1 uplift drops from $66.3k to $57.8k.
    """
)
