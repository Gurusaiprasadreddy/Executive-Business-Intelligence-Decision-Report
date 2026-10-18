"""ROI Model -- Validated Financial Scenario Engine
===================================================

Models incremental financial benefit, implementation cost, and 36-month
cash-flow trajectory for three strategic recommendations:

    Rec 1 -- Discount Guardrails
    Rec 2 -- Marketplace Margin Repair
    Rec 3 -- Delivery SLA Improvement and Customer Retention

Design Principles
-----------------
* Baseline and incremental benefits are modelled separately and never
  combined without an explicit anti-double-counting guard.
* Revenue, contribution profit, and net benefit are distinct quantities.
* One-time (capex) and recurring (opex) costs are tracked independently.
* Monthly cash flows span 36 months with configurable launch timing/ramp.
* Three scenarios (Conservative / Base / Optimistic) differ only in
  assumption values, not in formula structure.
* Assumptions not provable from data are labelled USER_SUPPLIED or
  HYPOTHETICAL.
* No result is forced to match the original notebook figures. Those values
  emerge (or do not) from the assumptions alone.
* Observational associations (e.g. discount -> margin, shipping delay -> return rate)
  do NOT prove causality.

Data Provenance (from Stage 2 verified metrics.json)
-----------------------------------------------------
* 2025 baseline revenue  : $1,400,396.80  (exact, verified)
* 2025 baseline profit   : $167,087.95    (exact, verified)
* 2025 baseline margin   : 11.93%         (exact, verified)
* 2025 total orders      : 4,978
* Late return rate       : 14.91%         (exact, from H3 hypothesis test)
* On-time return rate    : 4.78%          (exact, from H3 hypothesis test)
* 2024 active customers  : 1,003          (exact, from metrics.json)
* Retention 2024->2025   : 49.65%         (exact, from metrics.json)
* Channel fees: Retail 0%, Online 4%, Marketplace 13%
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd

from src.io_utils import get_project_root, save_csv, save_json, load_csv


# ---------------------------------------------------------------------------
# Authoritative constants (sourced from src/data_cleaning.py -- never change)
# ---------------------------------------------------------------------------
FEE_STRUCTURE: Dict[str, float] = {
    "Retail Store": 0.00,
    "Online": 0.04,
    "Marketplace": 0.13,
}

# ---------------------------------------------------------------------------
# Assumption registry
# source in {"DATA_VERIFIED", "USER_SUPPLIED", "HYPOTHETICAL"}
# ---------------------------------------------------------------------------
ASSUMPTION_REGISTRY: Dict[str, Dict[str, Any]] = {
    # Rec 1 - Discount Guardrails
    "r1_cap_discount": {
        "value": 0.20,
        "source": "DATA_VERIFIED",
        "description": (
            "Maximum allowed discount after guardrail. Orders >20% are repriced "
            "to exactly 20%. Verified: >20% band has aggregate margin -0.56% "
            "(21-30%) and -22.55% (>30%)."
        ),
    },
    "r1_order_retention_base": {
        "value": 0.70,
        "source": "USER_SUPPLIED",
        "description": (
            "Fraction of >20%-discount orders retained when price rises to 20% cap. "
            "Range tested: 0.55 (conservative) to 0.80 (optimistic). "
            "NOT derivable from observational data alone."
        ),
    },
    "r1_launch_month": {
        "value": 1,
        "source": "USER_SUPPLIED",
        "description": "Month (1-indexed) when Rec 1 becomes active.",
    },
    "r1_ramp_months": {
        "value": 3,
        "source": "USER_SUPPLIED",
        "description": "Months over which Rec 1 benefits ramp from 0% to full run-rate.",
    },
    "r1_one_time_cost": {
        "value": 10_000.0,
        "source": "USER_SUPPLIED",
        "description": "One-time cost: policy rollout, pricing system config, training.",
    },
    "r1_monthly_opex": {
        "value": 333.33,
        "source": "USER_SUPPLIED",
        "description": "Monthly recurring cost for guardrail system ($4,000/yr / 12).",
    },
    # Rec 2 - Marketplace Margin Repair
    "r2_marketplace_discount_cap": {
        "value": 0.10,
        "source": "USER_SUPPLIED",
        "description": (
            "Maximum promotional discount on Marketplace after repair. "
            "NOT derivable from data; business policy decision."
        ),
    },
    "r2_marketplace_order_retention_base": {
        "value": 0.75,
        "source": "USER_SUPPLIED",
        "description": "Fraction of Marketplace >10%-discount orders retained. Range: 0.60-0.85.",
    },
    "r2_fee_reduction_pp_base": {
        "value": 1.0,
        "source": "HYPOTHETICAL",
        "description": (
            "Percentage-point reduction in Marketplace fee via volume negotiation "
            "(13% -> 12%). Entirely speculative; binary outcome uncertain."
        ),
    },
    "r2_launch_month": {
        "value": 3,
        "source": "USER_SUPPLIED",
        "description": "Month when Rec 2 becomes active (after Rec 1 stabilises).",
    },
    "r2_ramp_months": {
        "value": 6,
        "source": "USER_SUPPLIED",
        "description": "Ramp period for Rec 2 benefits (months).",
    },
    "r2_one_time_cost": {
        "value": 12_000.0,
        "source": "USER_SUPPLIED",
        "description": "One-time cost for contract renegotiation and channel config.",
    },
    "r2_monthly_opex": {
        "value": 500.0,
        "source": "USER_SUPPLIED",
        "description": "Monthly recurring cost for Marketplace strategy ($6,000/yr / 12).",
    },
    # Rec 3 - Delivery SLA and Customer Retention
    "r3_central_late_rate_target": {
        "value": 0.15,
        "source": "USER_SUPPLIED",
        "description": (
            "Target Central region late-delivery rate after 3PL overhaul "
            "(from 58.41% baseline). NOT provable from observational data."
        ),
    },
    "r3_other_late_rate_improvement_pct": {
        "value": 0.10,
        "source": "USER_SUPPLIED",
        "description": "Proportional improvement in late rate for non-Central regions. Speculative.",
    },
    "r3_return_rate_if_ontime": {
        "value": 0.0478,
        "source": "DATA_VERIFIED",
        "description": "Empirical on-time return rate: 4.78%. From H3 test (metrics.json).",
    },
    "r3_return_rate_if_late": {
        "value": 0.1491,
        "source": "DATA_VERIFIED",
        "description": "Empirical late-delivery return rate: 14.91%. From H3 test (metrics.json).",
    },
    "r3_handling_cost_pct_of_sales": {
        "value": 0.05,
        "source": "USER_SUPPLIED",
        "description": "Estimated return-handling cost as fraction of order sales (5%). Hypothetical.",
    },
    "r3_retention_uplift_pp_base": {
        "value": 4.35,
        "source": "USER_SUPPLIED",
        "description": (
            "Target improvement in annual customer retention rate (pp): 49.65% -> 54.0%. "
            "Hypothetical; assumes loyalty programme effectiveness."
        ),
    },
    "r3_avg_retained_revenue_base": {
        "value": 700.0,
        "source": "USER_SUPPLIED",
        "description": (
            "CAUTION - SURVIVORSHIP BIAS. Historical avg revenue per repeat customer "
            "(~$1,292) overstates marginal churner spend. Conservative 54% haircut "
            "($700 used). Range tested: $500-$1,000."
        ),
    },
    "r3_launch_month": {
        "value": 6,
        "source": "USER_SUPPLIED",
        "description": "Month when Rec 3 becomes active.",
    },
    "r3_ramp_months": {
        "value": 9,
        "source": "USER_SUPPLIED",
        "description": "Ramp period for Rec 3 benefits (months).",
    },
    "r3_one_time_cost": {
        "value": 12_000.0,
        "source": "USER_SUPPLIED",
        "description": "One-time cost: 3PL rebid, loyalty system setup.",
    },
    "r3_monthly_opex": {
        "value": 750.0,
        "source": "USER_SUPPLIED",
        "description": "Monthly recurring cost for 3PL SLA + loyalty programme ($9,000/yr / 12).",
    },
}


# ---------------------------------------------------------------------------
# Scenario multiplier table
# DATA_VERIFIED assumptions are NEVER modified by scenario.
# ---------------------------------------------------------------------------
SCENARIO_MULTIPLIERS: Dict[str, Dict[str, Any]] = {
    "Conservative": {
        "r1_order_retention": 0.55,
        "r2_marketplace_order_retention": 0.60,
        "r2_fee_reduction_pp": 0.0,
        "r3_retention_uplift_pp": 2.0,
        "r3_avg_retained_revenue": 500.0,
        "r3_central_late_rate_target": 0.25,
        "r3_other_improvement_pct": 0.05,
        "r3_return_rate_if_late": 0.12,
        "cost_multiplier": 1.20,
        "launch_delay_months": 2,
    },
    "Base": {
        "r1_order_retention": 0.70,
        "r2_marketplace_order_retention": 0.75,
        "r2_fee_reduction_pp": 1.0,
        "r3_retention_uplift_pp": 4.35,
        "r3_avg_retained_revenue": 700.0,
        "r3_central_late_rate_target": 0.15,
        "r3_other_improvement_pct": 0.10,
        "r3_return_rate_if_late": 0.1491,
        "cost_multiplier": 1.00,
        "launch_delay_months": 0,
    },
    "Optimistic": {
        "r1_order_retention": 0.80,
        "r2_marketplace_order_retention": 0.85,
        "r2_fee_reduction_pp": 2.0,
        "r3_retention_uplift_pp": 7.0,
        "r3_avg_retained_revenue": 1000.0,
        "r3_central_late_rate_target": 0.10,
        "r3_other_improvement_pct": 0.20,
        "r3_return_rate_if_late": 0.18,
        "cost_multiplier": 0.90,
        "launch_delay_months": 0,
    },
}


# ---------------------------------------------------------------------------
# Result containers
# ---------------------------------------------------------------------------

class RecommendationResult:
    """Financial result for a single recommendation."""

    def __init__(
        self,
        name: str,
        annual_benefit_run_rate: float,
        annual_benefit_revenue_delta: float,
        annual_benefit_contrib_profit_delta: float,
        one_time_cost: float,
        annual_opex: float,
        total_cost_36m: float,
        net_benefit_36m: float,
        roi_pct: float,
        payback_month: Optional[int],
        double_counting_guard: str,
    ):
        self.name = name
        self.annual_benefit_run_rate = annual_benefit_run_rate
        self.annual_benefit_revenue_delta = annual_benefit_revenue_delta
        self.annual_benefit_contrib_profit_delta = annual_benefit_contrib_profit_delta
        self.one_time_cost = one_time_cost
        self.annual_opex = annual_opex
        self.total_cost_36m = total_cost_36m
        self.net_benefit_36m = net_benefit_36m
        self.roi_pct = roi_pct
        self.payback_month = payback_month
        self.double_counting_guard = double_counting_guard

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "annual_benefit_run_rate": self.annual_benefit_run_rate,
            "annual_benefit_revenue_delta": self.annual_benefit_revenue_delta,
            "annual_benefit_contrib_profit_delta": self.annual_benefit_contrib_profit_delta,
            "one_time_cost": self.one_time_cost,
            "annual_opex": self.annual_opex,
            "total_cost_36m": self.total_cost_36m,
            "net_benefit_36m": self.net_benefit_36m,
            "roi_pct": self.roi_pct,
            "payback_month": self.payback_month,
            "double_counting_guard": self.double_counting_guard,
        }


class ScenarioResult:
    """Aggregate results for a single scenario."""

    def __init__(
        self,
        scenario: str,
        rec1: RecommendationResult,
        rec2: RecommendationResult,
        rec3: RecommendationResult,
        total_annual_benefit: float,
        total_cost_36m: float,
        total_net_benefit_36m: float,
        total_roi_pct: float,
        combined_payback_month: Optional[int],
        npv_10pct: float,
        monthly_cash_flows: List[float],
    ):
        self.scenario = scenario
        self.rec1 = rec1
        self.rec2 = rec2
        self.rec3 = rec3
        self.total_annual_benefit = total_annual_benefit
        self.total_cost_36m = total_cost_36m
        self.total_net_benefit_36m = total_net_benefit_36m
        self.total_roi_pct = total_roi_pct
        self.combined_payback_month = combined_payback_month
        self.npv_10pct = npv_10pct
        self.monthly_cash_flows = monthly_cash_flows

        # Derived aggregate cost and benefit components
        self.total_one_time_cost = round(rec1.one_time_cost + rec2.one_time_cost + rec3.one_time_cost, 2)
        self.total_annual_opex = round(rec1.annual_opex + rec2.annual_opex + rec3.annual_opex, 2)
        self.total_annual_revenue_delta = round(
            rec1.annual_benefit_revenue_delta + rec2.annual_benefit_revenue_delta + rec3.annual_benefit_revenue_delta, 2
        )
        self.total_annual_contrib_profit_delta = round(
            rec1.annual_benefit_contrib_profit_delta + rec2.annual_benefit_contrib_profit_delta + rec3.annual_benefit_contrib_profit_delta, 2
        )


# ---------------------------------------------------------------------------
# Core computation helpers
# ---------------------------------------------------------------------------

def npv_monthly(discount_rate_annual: float, cash_flows: List[float]) -> float:
    """NPV of a monthly cash-flow series at an annual discount rate."""
    if not cash_flows:
        return 0.0
    r = (1.0 + discount_rate_annual) ** (1.0 / 12.0) - 1.0
    return float(sum(cf / (1.0 + r) ** (t + 1) for t, cf in enumerate(cash_flows)))


def find_payback_month(cum_cf: List[float]) -> Optional[int]:
    """
    Return 1-indexed month where cumulative CF first turns non-negative after investment outlay.

    Financial definition & safeguards:
    - If cumulative cash flow dips below zero (cash outflow / investment exceeds inflow),
      payback is the first month at or after that initial deficit where cumulative cash flow
      reaches >= 0.0.
    - If cumulative cash flow enters a deficit and never reaches >= 0.0 through the horizon,
      payback is None (representing 'Never (>36m)').
    - If cumulative cash flow never dips below zero:
      * If all values are 0.0 (no investment, no return), returns None.
      * If positive cash flows exist with zero/immediate recovery, returns the first month
        with positive cash flow (e.g. Month 1).
    """
    if not cum_cf or len(cum_cf) == 0:
        return None

    # Check for presence of investment outlay (deficit)
    neg_indices = [i for i, val in enumerate(cum_cf) if val < 0.0]

    if neg_indices:
        first_neg_idx = neg_indices[0]
        for i in range(first_neg_idx, len(cum_cf)):
            if cum_cf[i] >= 0.0:
                return i + 1
        return None

    # If it never entered deficit, find first month with positive flow
    for i, val in enumerate(cum_cf):
        if val > 0.0:
            return i + 1

    return None


def build_monthly_benefit(
    annual_run_rate: float,
    launch_month: int,
    ramp_months: int,
    horizon: int = 36,
) -> List[float]:
    """Linear ramp-up from launch_month over ramp_months, then flat."""
    monthly_run = annual_run_rate / 12.0
    benefits = []
    for m in range(1, horizon + 1):
        if m < launch_month:
            benefits.append(0.0)
        elif m < launch_month + ramp_months:
            fraction = (m - launch_month + 1) / ramp_months
            benefits.append(monthly_run * fraction)
        else:
            benefits.append(monthly_run)
    return benefits


def build_monthly_cost(
    one_time_cost: float,
    monthly_opex: float,
    launch_month: int,
    horizon: int = 36,
) -> List[float]:
    """One-time cost at launch_month; opex every month from launch onward."""
    costs = []
    for m in range(1, horizon + 1):
        c = 0.0
        if m == launch_month:
            c += one_time_cost
        if m >= launch_month:
            c += monthly_opex
        costs.append(c)
    return costs


def total_36m_cost(
    one_time_cost: float,
    monthly_opex: float,
    launch_month: int,
    horizon: int = 36,
) -> float:
    return sum(build_monthly_cost(one_time_cost, monthly_opex, launch_month, horizon))


def compute_roi(net_benefit: float, total_cost: float) -> float:
    """ROI as percentage. Returns 0.0 if cost is zero or negative."""
    if total_cost <= 0.0:
        return 0.0
    return (net_benefit / total_cost) * 100.0


# ---------------------------------------------------------------------------
# Recommendation benefit calculators
# ---------------------------------------------------------------------------

def compute_rec1_benefit(
    df_2025: pd.DataFrame,
    order_retention: float,
) -> Tuple[float, float, float, pd.DataFrame]:
    """
    Recommendation 1 -- Discount Guardrails.

    Logic:
      1. Identify 2025 orders with discount > 20%.
      2. Reprice retained fraction to discount = 20%.
      3. Recompute profit via channel fee formula.
      4. Annual benefit = post-Rec1 profit - baseline 2025 profit.

    Returns (annual_benefit, revenue_delta, contrib_profit_delta, df_post1).
    df_post1 is passed to Rec 2 to prevent double-counting.

    Double-counting guard: Rec 1 modifies ALL channels at >20%. Rec 2
    receives df_post1 and only applies its Marketplace-specific 10% cap
    to orders not already resolved by Rec 1.
    """
    df = df_2025.copy()
    baseline_profit = float(df["profit"].sum()) if len(df) > 0 else 0.0
    baseline_revenue = float(df["sales"].sum()) if len(df) > 0 else 0.0

    mask_high = df["discount"] > 0.20
    df_below = df[~mask_high].copy()
    df_high = df[mask_high].copy()

    n_retained = int(round(len(df_high) * order_retention))

    if n_retained > 0 and len(df_high) > 0:
        df_high_ret = df_high.nlargest(n_retained, "sales").copy()
    else:
        df_high_ret = df_high.iloc[0:0].copy()

    df_high_ret = df_high_ret.copy()
    df_high_ret["discount"] = 0.20
    df_high_ret["sales"] = (
        df_high_ret["quantity"] * df_high_ret["unit_price"] * 0.80
    )
    fee_vals = df_high_ret["channel"].map(FEE_STRUCTURE).fillna(0.0)
    df_high_ret["profit"] = (
        df_high_ret["sales"] * (1.0 - fee_vals)
        - df_high_ret["quantity"] * df_high_ret["unit_cost"]
    )

    df_post1 = pd.concat([df_below, df_high_ret], ignore_index=True)
    post1_profit = float(df_post1["profit"].sum()) if len(df_post1) > 0 else 0.0
    post1_revenue = float(df_post1["sales"].sum()) if len(df_post1) > 0 else 0.0

    annual_benefit = post1_profit - baseline_profit
    revenue_delta = post1_revenue - baseline_revenue
    contrib_profit_delta = annual_benefit

    return (
        annual_benefit,
        revenue_delta,
        contrib_profit_delta,
        df_post1,
    )


def compute_rec2_benefit(
    df_post1: pd.DataFrame,
    marketplace_order_retention: float,
    fee_reduction_pp: float,
) -> Tuple[float, float, float, pd.DataFrame]:
    """
    Recommendation 2 -- Marketplace Margin Repair.

    Applied AFTER Rec 1 on the post-Rec1 portfolio.
    Incremental benefit = post-Rec2 profit - post-Rec1 profit.

    Double-counting guard: Rec 1 already handled >20% cross-channel.
    Rec 2 only touches Marketplace orders that still have discount > 10%.
    Fee reduction is applied to ALL remaining Marketplace orders (incremental
    vs post-Rec1 baseline, so no double-counting with Rec 1 savings).
    """
    df = df_post1.copy()
    post1_profit = float(df["profit"].sum()) if len(df) > 0 else 0.0
    post1_revenue = float(df["sales"].sum()) if len(df) > 0 else 0.0

    mask_mp = df["channel"] == "Marketplace"
    mask_mp_high = mask_mp & (df["discount"] > 0.10)

    df_mp_high = df[mask_mp_high].copy()
    n_retained = int(round(len(df_mp_high) * marketplace_order_retention))

    if n_retained > 0 and len(df_mp_high) > 0:
        df_mp_ret = df_mp_high.nlargest(n_retained, "sales").copy()
    else:
        df_mp_ret = df_mp_high.iloc[0:0].copy()

    effective_fee = max(0.0, FEE_STRUCTURE["Marketplace"] - fee_reduction_pp / 100.0)

    df_mp_ret = df_mp_ret.copy()
    df_mp_ret["discount"] = 0.10
    df_mp_ret["sales"] = (
        df_mp_ret["quantity"] * df_mp_ret["unit_price"] * 0.90
    )
    df_mp_ret["profit"] = (
        df_mp_ret["sales"] * (1.0 - effective_fee)
        - df_mp_ret["quantity"] * df_mp_ret["unit_cost"]
    )

    # All other marketplace rows: retain original pricing, apply fee reduction only
    df_mp_other = df[mask_mp & ~mask_mp_high].copy()
    if fee_reduction_pp > 0 and len(df_mp_other) > 0:
        df_mp_other["profit"] = (
            df_mp_other["sales"] * (1.0 - effective_fee)
            - df_mp_other["quantity"] * df_mp_other["unit_cost"]
        )

    # Non-marketplace rows unchanged
    df_non_mp = df[~mask_mp].copy()

    pieces = [p for p in [df_non_mp, df_mp_other, df_mp_ret] if len(p) > 0]
    df_post2 = pd.concat(pieces, ignore_index=True) if pieces else df.iloc[0:0].copy()

    post2_profit = float(df_post2["profit"].sum()) if len(df_post2) > 0 else 0.0
    post2_revenue = float(df_post2["sales"].sum()) if len(df_post2) > 0 else 0.0

    annual_benefit = post2_profit - post1_profit
    revenue_delta = post2_revenue - post1_revenue
    contrib_profit_delta = annual_benefit

    return (
        annual_benefit,
        revenue_delta,
        contrib_profit_delta,
        df_post2,
    )


def compute_rec3_benefit(
    df_2025: pd.DataFrame,
    df_post2: pd.DataFrame,
    central_late_rate_target: float,
    other_late_rate_improvement_pct: float,
    return_rate_if_ontime: float,
    return_rate_if_late: float,
    handling_cost_pct: float,
    retention_uplift_pp: float,
    avg_retained_revenue: float,
    n_active_2024_customers: int = 1003,
) -> Tuple[float, float, float]:
    """
    Recommendation 3 -- Delivery SLA Improvement and Customer Retention.

    Two independent sub-components with NO overlap:

    A) Fulfilment savings: avoided return costs on orders converted
       from late to on-time delivery. Uses only ship_days/returned flags;
       independent of discount/channel changes made by Rec 1/2.

    B) Retention uplift: incremental profit from saved churning customers.
       Uses customer-level cohort counts; independent of order-level repricing.
       CAUTION: avg_retained_revenue is USER_SUPPLIED with survivorship bias.

    Zero-floor on loss-making orders in Component A prevents double-counting
    losses already partially addressed by Rec 1 and Rec 2 margin improvements.
    """
    post2_profit = float(df_post2["profit"].sum()) if len(df_post2) > 0 else 0.0
    post2_revenue = float(df_post2["sales"].sum()) if len(df_post2) > 0 else 0.0
    portfolio_margin = post2_profit / post2_revenue if post2_revenue > 0 else 0.0

    # -- Component A: Fulfilment savings ------------------------------------
    fulfilment_saving = 0.0
    if len(df_post2) > 0 and "is_late" in df_post2.columns and "region" in df_post2.columns:
        avoidable_late = 0.0
        for region, grp in df_post2.groupby("region"):
            n_region = len(grp)
            current_late_n = int(grp["is_late"].sum())
            if region == "Central":
                target_late_n = int(round(n_region * central_late_rate_target))
            else:
                current_rate = current_late_n / n_region if n_region > 0 else 0.0
                target_rate = current_rate * (1.0 - other_late_rate_improvement_pct)
                target_late_n = int(round(n_region * target_rate))
            avoidable_late += max(0.0, float(current_late_n - target_late_n))

        marginal_return_rate = return_rate_if_late - return_rate_if_ontime
        avoidable_returns = avoidable_late * marginal_return_rate

        df_late = df_post2[df_post2["is_late"] == True]
        if len(df_late) > 0:
            avg_late_sales = float(df_late["sales"].mean())
            avg_late_profit_floored = float(df_late["profit"].clip(lower=0.0).mean())
        else:
            avg_late_sales = 0.0
            avg_late_profit_floored = 0.0

        avoided_cost_per_return = (handling_cost_pct * avg_late_sales) + avg_late_profit_floored
        fulfilment_saving = avoidable_returns * avoided_cost_per_return

    # -- Component B: Retention uplift --------------------------------------
    n_saved = (retention_uplift_pp / 100.0) * n_active_2024_customers
    incremental_revenue = n_saved * avg_retained_revenue
    incremental_profit = incremental_revenue * portfolio_margin

    annual_benefit = fulfilment_saving + incremental_profit
    revenue_delta = incremental_revenue
    contrib_profit_delta = annual_benefit

    return float(annual_benefit), float(revenue_delta), float(contrib_profit_delta)


# ---------------------------------------------------------------------------
# Main scenario runner
# ---------------------------------------------------------------------------

def run_scenario(
    df_2025: pd.DataFrame,
    scenario_name: str = "Base",
    horizon: int = 36,
    npv_discount_rate: float = 0.10,
) -> ScenarioResult:
    """
    Run the full 3-recommendation financial model for a named scenario.

    Parameters
    ----------
    df_2025 : 2025 subset of the clean dataset (filtered by order_date year == 2025)
    scenario_name : "Conservative", "Base", or "Optimistic"
    horizon : cash-flow horizon in months (default 36)
    npv_discount_rate : annual discount rate for NPV calculation (default 10%)

    Returns
    -------
    ScenarioResult with all financial outputs
    """
    if scenario_name not in SCENARIO_MULTIPLIERS:
        raise ValueError(
            f"Unknown scenario '{scenario_name}'. "
            f"Valid options: {list(SCENARIO_MULTIPLIERS.keys())}"
        )

    sm = SCENARIO_MULTIPLIERS[scenario_name]
    delay = int(sm.get("launch_delay_months", 0))
    cost_mult = float(sm.get("cost_multiplier", 1.0))

    r1_one_time = ASSUMPTION_REGISTRY["r1_one_time_cost"]["value"] * cost_mult
    r1_opex = ASSUMPTION_REGISTRY["r1_monthly_opex"]["value"] * cost_mult
    r1_launch = max(1, int(ASSUMPTION_REGISTRY["r1_launch_month"]["value"]) + delay)
    r1_ramp = int(ASSUMPTION_REGISTRY["r1_ramp_months"]["value"])

    r2_one_time = ASSUMPTION_REGISTRY["r2_one_time_cost"]["value"] * cost_mult
    r2_opex = ASSUMPTION_REGISTRY["r2_monthly_opex"]["value"] * cost_mult
    r2_launch = max(1, int(ASSUMPTION_REGISTRY["r2_launch_month"]["value"]) + delay)
    r2_ramp = int(ASSUMPTION_REGISTRY["r2_ramp_months"]["value"])

    r3_one_time = ASSUMPTION_REGISTRY["r3_one_time_cost"]["value"] * cost_mult
    r3_opex = ASSUMPTION_REGISTRY["r3_monthly_opex"]["value"] * cost_mult
    r3_launch = max(1, int(ASSUMPTION_REGISTRY["r3_launch_month"]["value"]) + delay)
    r3_ramp = int(ASSUMPTION_REGISTRY["r3_ramp_months"]["value"])

    # Benefit calculations (sequential, anti-double-counting)
    r1_benefit, r1_rev, r1_prof, df_post1 = compute_rec1_benefit(
        df_2025=df_2025,
        order_retention=float(sm["r1_order_retention"]),
    )
    r2_benefit, r2_rev, r2_prof, df_post2 = compute_rec2_benefit(
        df_post1=df_post1,
        marketplace_order_retention=float(sm["r2_marketplace_order_retention"]),
        fee_reduction_pp=float(sm["r2_fee_reduction_pp"]),
    )
    r3_benefit, r3_rev, r3_prof = compute_rec3_benefit(
        df_2025=df_2025,
        df_post2=df_post2,
        central_late_rate_target=float(sm["r3_central_late_rate_target"]),
        other_late_rate_improvement_pct=float(sm.get("r3_other_improvement_pct", ASSUMPTION_REGISTRY["r3_other_late_rate_improvement_pct"]["value"])),
        return_rate_if_ontime=float(ASSUMPTION_REGISTRY["r3_return_rate_if_ontime"]["value"]),
        return_rate_if_late=float(sm.get("r3_return_rate_if_late", ASSUMPTION_REGISTRY["r3_return_rate_if_late"]["value"])),
        handling_cost_pct=float(ASSUMPTION_REGISTRY["r3_handling_cost_pct_of_sales"]["value"]),
        retention_uplift_pp=float(sm["r3_retention_uplift_pp"]),
        avg_retained_revenue=float(sm["r3_avg_retained_revenue"]),
    )

    # Build monthly series
    b1 = build_monthly_benefit(r1_benefit, r1_launch, r1_ramp, horizon)
    b2 = build_monthly_benefit(r2_benefit, r2_launch, r2_ramp, horizon)
    b3 = build_monthly_benefit(r3_benefit, r3_launch, r3_ramp, horizon)

    c1 = build_monthly_cost(r1_one_time, r1_opex, r1_launch, horizon)
    c2 = build_monthly_cost(r2_one_time, r2_opex, r2_launch, horizon)
    c3 = build_monthly_cost(r3_one_time, r3_opex, r3_launch, horizon)

    monthly_cf = [
        (b1[i] + b2[i] + b3[i]) - (c1[i] + c2[i] + c3[i])
        for i in range(horizon)
    ]
    cum_cf = list(np.cumsum(monthly_cf))

    r1_cum = list(np.cumsum([b1[i] - c1[i] for i in range(horizon)]))
    r2_cum = list(np.cumsum([b2[i] - c2[i] for i in range(horizon)]))
    r3_cum = list(np.cumsum([b3[i] - c3[i] for i in range(horizon)]))

    r1_tc = total_36m_cost(r1_one_time, r1_opex, r1_launch, horizon)
    r2_tc = total_36m_cost(r2_one_time, r2_opex, r2_launch, horizon)
    r3_tc = total_36m_cost(r3_one_time, r3_opex, r3_launch, horizon)

    r1_tb = sum(b1)
    r2_tb = sum(b2)
    r3_tb = sum(b3)

    total_cost = r1_tc + r2_tc + r3_tc
    total_benefit = r1_tb + r2_tb + r3_tb
    total_net = total_benefit - total_cost
    total_roi = compute_roi(total_net, total_cost)

    rec1 = RecommendationResult(
        name="Rec 1 -- Discount Guardrails",
        annual_benefit_run_rate=round(r1_benefit, 2),
        annual_benefit_revenue_delta=round(r1_rev, 2),
        annual_benefit_contrib_profit_delta=round(r1_prof, 2),
        one_time_cost=round(r1_one_time, 2),
        annual_opex=round(r1_opex * 12, 2),
        total_cost_36m=round(r1_tc, 2),
        net_benefit_36m=round(r1_tb - r1_tc, 2),
        roi_pct=round(compute_roi(r1_tb - r1_tc, r1_tc), 2),
        payback_month=find_payback_month(r1_cum),
        double_counting_guard=(
            "Rec 1 reprices ALL channels at >20% discount. "
            "Rec 2 receives post-Rec1 dataset and applies Marketplace-specific "
            "10% cap ONLY to orders not already resolved by Rec 1."
        ),
    )

    rec2 = RecommendationResult(
        name="Rec 2 -- Marketplace Margin Repair",
        annual_benefit_run_rate=round(r2_benefit, 2),
        annual_benefit_revenue_delta=round(r2_rev, 2),
        annual_benefit_contrib_profit_delta=round(r2_prof, 2),
        one_time_cost=round(r2_one_time, 2),
        annual_opex=round(r2_opex * 12, 2),
        total_cost_36m=round(r2_tc, 2),
        net_benefit_36m=round(r2_tb - r2_tc, 2),
        roi_pct=round(compute_roi(r2_tb - r2_tc, r2_tc), 2),
        payback_month=find_payback_month(r2_cum),
        double_counting_guard=(
            "Rec 2 operates on post-Rec1 portfolio. "
            "Incremental benefit = post-Rec2 profit - post-Rec1 profit. "
            "Channel-fee reduction is independent of discount repricing."
        ),
    )

    rec3 = RecommendationResult(
        name="Rec 3 -- Delivery SLA & Customer Retention",
        annual_benefit_run_rate=round(r3_benefit, 2),
        annual_benefit_revenue_delta=round(r3_rev, 2),
        annual_benefit_contrib_profit_delta=round(r3_prof, 2),
        one_time_cost=round(r3_one_time, 2),
        annual_opex=round(r3_opex * 12, 2),
        total_cost_36m=round(r3_tc, 2),
        net_benefit_36m=round(r3_tb - r3_tc, 2),
        roi_pct=round(compute_roi(r3_tb - r3_tc, r3_tc), 2),
        payback_month=find_payback_month(r3_cum),
        double_counting_guard=(
            "Fulfilment savings use ship_days/returned flags independent of "
            "pricing changes. Retention uplift uses customer-level cohort counts "
            "independent of order-level repricing. Zero-floor on loss orders "
            "prevents double-counting losses from Rec 1/2 improvements."
        ),
    )

    return ScenarioResult(
        scenario=scenario_name,
        rec1=rec1,
        rec2=rec2,
        rec3=rec3,
        total_annual_benefit=round(r1_benefit + r2_benefit + r3_benefit, 2),
        total_cost_36m=round(total_cost, 2),
        total_net_benefit_36m=round(total_net, 2),
        total_roi_pct=round(total_roi, 2),
        combined_payback_month=find_payback_month(cum_cf),
        npv_10pct=round(npv_monthly(npv_discount_rate, monthly_cf), 2),
        monthly_cash_flows=[round(v, 2) for v in monthly_cf],
    )


# ---------------------------------------------------------------------------
# Sensitivity analysis -- one-at-a-time (OAT)
# Covers customer retention, marketplace fee reduction, order retention,
# delivery improvement, return rates, implementation costs, and launch delays.
# ---------------------------------------------------------------------------

SENSITIVITY_VARIABLES = [
    "r1_order_retention",
    "r2_marketplace_order_retention",
    "r2_fee_reduction_pp",
    "r3_retention_uplift_pp",
    "r3_avg_retained_revenue",
    "r3_central_late_rate_target",
    "r3_other_improvement_pct",
    "r3_return_rate_if_late",
    "cost_multiplier",
    "launch_delay_months",
]


def run_sensitivity_analysis(
    df_2025: pd.DataFrame,
    n_steps: int = 5,
) -> pd.DataFrame:
    """
    One-at-a-time (OAT) sensitivity analysis.

    For each variable, sweeps from Conservative to Optimistic value while
    holding all others at Base scenario values. Returns a tidy DataFrame.
    """
    conservative = SCENARIO_MULTIPLIERS["Conservative"]
    optimistic = SCENARIO_MULTIPLIERS["Optimistic"]
    base = dict(SCENARIO_MULTIPLIERS["Base"])

    rows = []
    for var in SENSITIVITY_VARIABLES:
        low = float(conservative[var])
        high = float(optimistic[var])
        sweep_values = np.linspace(low, high, n_steps)

        for val in sweep_values:
            custom_sm = dict(base)
            custom_sm[var] = float(val)
            SCENARIO_MULTIPLIERS["_oat_"] = custom_sm
            try:
                result = run_scenario(df_2025, scenario_name="_oat_")
                rows.append({
                    "variable": var,
                    "value": round(float(val), 4),
                    "total_annual_benefit": result.total_annual_benefit,
                    "total_net_36m": result.total_net_benefit_36m,
                    "roi_pct": result.total_roi_pct,
                    "payback_month": (
                        result.combined_payback_month
                        if result.combined_payback_month is not None
                        else "Never (>36m)"
                    ),
                    "npv_10pct": result.npv_10pct,
                })
            finally:
                if "_oat_" in SCENARIO_MULTIPLIERS:
                    del SCENARIO_MULTIPLIERS["_oat_"]

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Output builders
# ---------------------------------------------------------------------------

def build_scenarios_summary(
    df_2025: pd.DataFrame,
) -> Tuple[pd.DataFrame, Dict[str, ScenarioResult]]:
    """Run all three scenarios and return summary DataFrame plus results dict."""
    results: Dict[str, ScenarioResult] = {}
    rows = []

    for scenario in ["Conservative", "Base", "Optimistic"]:
        res = run_scenario(df_2025, scenario_name=scenario)
        results[scenario] = res

        for rec in [res.rec1, res.rec2, res.rec3]:
            rows.append({
                "scenario": scenario,
                "recommendation": rec.name,
                "annual_benefit_run_rate": rec.annual_benefit_run_rate,
                "annual_revenue_delta": rec.annual_benefit_revenue_delta,
                "annual_contrib_profit_delta": rec.annual_benefit_contrib_profit_delta,
                "one_time_cost": rec.one_time_cost,
                "annual_opex": rec.annual_opex,
                "total_cost_36m": rec.total_cost_36m,
                "net_benefit_36m": rec.net_benefit_36m,
                "roi_pct": rec.roi_pct,
                "payback_month": rec.payback_month if rec.payback_month is not None else "Never (>36m)",
            })

        rows.append({
            "scenario": scenario,
            "recommendation": "TOTAL",
            "annual_benefit_run_rate": res.total_annual_benefit,
            "annual_revenue_delta": res.total_annual_revenue_delta,
            "annual_contrib_profit_delta": res.total_annual_contrib_profit_delta,
            "one_time_cost": res.total_one_time_cost,
            "annual_opex": res.total_annual_opex,
            "total_cost_36m": res.total_cost_36m,
            "net_benefit_36m": res.total_net_benefit_36m,
            "roi_pct": res.total_roi_pct,
            "payback_month": (
                res.combined_payback_month
                if res.combined_payback_month is not None
                else "Never (>36m)"
            ),
        })

    return pd.DataFrame(rows), results


def build_monthly_cash_flow_df(results: Dict[str, ScenarioResult]) -> pd.DataFrame:
    """Long-format monthly cash-flow table for all scenarios."""
    rows = []
    for scenario, res in results.items():
        cumulative = 0.0
        for i, cf in enumerate(res.monthly_cash_flows):
            cumulative += cf
            rows.append({
                "scenario": scenario,
                "month": i + 1,
                "monthly_net_cash_flow": round(cf, 2),
                "cumulative_net_cash_flow": round(cumulative, 2),
            })
    return pd.DataFrame(rows)


def build_break_even_df(
    results: Dict[str, ScenarioResult],
    df_2025: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Break-even analysis summary table with standalone recommendation and portfolio metrics."""
    rows = []
    for scenario, res in results.items():
        # Effective years of benefit realization over 36 months (accounting for launch & ramp)
        effective_benefit_years = (
            sum(res.monthly_cash_flows) / (res.total_annual_benefit / 12.0) / 12.0
            if res.total_annual_benefit > 0
            else 3.0
        )
        break_even_annual_benefit = (
            round(res.total_cost_36m / effective_benefit_years, 2)
            if effective_benefit_years > 0
            else round(res.total_cost_36m / 3.0, 2)
        )

        rows.append({
            "scenario": scenario,
            "payback_month": res.combined_payback_month if res.combined_payback_month is not None else "Never (>36m)",
            "total_annual_benefit": res.total_annual_benefit,
            "total_cost_36m": res.total_cost_36m,
            "total_net_benefit_36m": res.total_net_benefit_36m,
            "total_roi_pct": res.total_roi_pct,
            "npv_10pct_discount_rate": res.npv_10pct,
            "break_even_annual_benefit": break_even_annual_benefit,
            "rec1_payback_month": res.rec1.payback_month if res.rec1.payback_month is not None else "Never (>36m)",
            "rec2_payback_month": res.rec2.payback_month if res.rec2.payback_month is not None else "Never (>36m)",
            "rec3_payback_month": res.rec3.payback_month if res.rec3.payback_month is not None else "Never (>36m)",
        })
    return pd.DataFrame(rows)


def build_assumptions_export() -> pd.DataFrame:
    """Export the assumption registry as a structured DataFrame."""
    return pd.DataFrame([
        {
            "assumption_key": key,
            "value": meta["value"],
            "source": meta["source"],
            "description": meta["description"],
        }
        for key, meta in ASSUMPTION_REGISTRY.items()
    ])


def build_assumptions_json_dict() -> Dict[str, Any]:
    """Build the versioned, auditable JSON dictionary of all financial inputs and limits."""
    return {
        "schema_version": "4.0.0",
        "generated_at": pd.Timestamp.now().isoformat(),
        "pipeline_stage": "STAGE_4_VALIDATED_ROI_ENGINE",
        "caution": (
            "Assumptions labelled USER_SUPPLIED or HYPOTHETICAL cannot be verified "
            "from the historical dataset alone. They represent management judgements, "
            "industry estimates, or negotiation targets. Observational associations "
            "(e.g., discount -> margin, shipping delay -> return rate) do NOT prove causality. "
            "Do NOT treat projections as guaranteed forecasts."
        ),
        "data_verified_inputs": {
            "baseline_2025_revenue": {
                "value": 1400396.80,
                "source": "DATA_VERIFIED",
                "note": "Exact 2025 revenue from metrics.json",
            },
            "baseline_2025_profit": {
                "value": 167087.95,
                "source": "DATA_VERIFIED",
                "note": "Exact 2025 profit from metrics.json",
            },
            "baseline_2025_margin_pct": {
                "value": 11.93,
                "source": "DATA_VERIFIED",
                "note": "Exact 2025 weighted profit margin from metrics.json",
            },
            "baseline_2025_orders": {
                "value": 4978,
                "source": "DATA_VERIFIED",
                "note": "Exact 2025 order count from metrics.json",
            },
            "marketplace_channel_fee_pct": {
                "value": 13.0,
                "source": "DATA_VERIFIED",
                "note": "From data_cleaning.py FEE_STRUCTURE",
            },
            "online_channel_fee_pct": {
                "value": 4.0,
                "source": "DATA_VERIFIED",
                "note": "From data_cleaning.py FEE_STRUCTURE",
            },
            "retail_channel_fee_pct": {
                "value": 0.0,
                "source": "DATA_VERIFIED",
                "note": "From data_cleaning.py FEE_STRUCTURE",
            },
            "late_delivery_return_rate_pct": {
                "value": 14.91,
                "source": "DATA_VERIFIED",
                "note": "From H3 hypothesis test in metrics.json",
            },
            "ontime_delivery_return_rate_pct": {
                "value": 4.78,
                "source": "DATA_VERIFIED",
                "note": "From H3 hypothesis test in metrics.json",
            },
            "n_active_2024_customers": {
                "value": 1003,
                "source": "DATA_VERIFIED",
                "note": "Active purchasing accounts in 2024 from metrics.json",
            },
            "customer_retention_2024_to_2025_pct": {
                "value": 49.65,
                "source": "DATA_VERIFIED",
                "note": "Empirical cohort retention from metrics.json",
            },
            "central_region_late_rate_pct": {
                "value": 58.41,
                "source": "DATA_VERIFIED",
                "note": "Empirical Central region late shipping rate from metrics.json",
            },
            "discount_cap_threshold": {
                "value": 0.20,
                "source": "DATA_VERIFIED",
                "note": "Empirical discount cliff: >20% band has negative profit (-$40,094 in 2025)",
            },
        },
        "user_supplied_inputs": {
            "r1_order_retention_conservative": {
                "value": 0.55,
                "source": "USER_SUPPLIED",
                "note": "Fraction of >20% discount orders retained at 20% cap (Conservative)",
            },
            "r1_order_retention_base": {
                "value": 0.70,
                "source": "USER_SUPPLIED",
                "note": "Fraction of >20% discount orders retained at 20% cap (Base)",
            },
            "r1_order_retention_optimistic": {
                "value": 0.80,
                "source": "USER_SUPPLIED",
                "note": "Fraction of >20% discount orders retained at 20% cap (Optimistic)",
            },
            "r1_one_time_cost": {
                "value": 10000.0,
                "source": "USER_SUPPLIED",
                "note": "One-time cost: policy rollout, pricing system config, training",
            },
            "r1_annual_opex": {
                "value": 4000.0,
                "source": "USER_SUPPLIED",
                "note": "Recurring annual guardrail maintenance and audit cost ($333.33/mo)",
            },
            "r2_marketplace_discount_cap": {
                "value": 0.10,
                "source": "USER_SUPPLIED",
                "note": "Promotional discount cap on Marketplace channel",
            },
            "r2_marketplace_order_retention_base": {
                "value": 0.75,
                "source": "USER_SUPPLIED",
                "note": "Fraction of Marketplace >10% discount orders retained at 10% cap (Base)",
            },
            "r2_one_time_cost": {
                "value": 12000.0,
                "source": "USER_SUPPLIED",
                "note": "Contract renegotiation, channel catalog repricing, and integration setup",
            },
            "r2_annual_opex": {
                "value": 6000.0,
                "source": "USER_SUPPLIED",
                "note": "Recurring annual channel account management ($500.00/mo)",
            },
            "r3_central_late_rate_target_base": {
                "value": 0.15,
                "source": "USER_SUPPLIED",
                "note": "Target late rate for Central region following 3PL SLA overhaul (Base: 15%)",
            },
            "r3_return_handling_cost_pct_of_sales": {
                "value": 0.05,
                "source": "USER_SUPPLIED",
                "note": "Estimated return handling expense (5% of order sales; no cost data in raw CSV)",
            },
            "r3_retention_uplift_pp_base": {
                "value": 4.35,
                "source": "USER_SUPPLIED",
                "note": "Annual retention uplift target: 49.65% -> 54.0% (+4.35pp in Base)",
            },
            "r3_avg_retained_customer_revenue_base": {
                "value": 700.0,
                "source": "USER_SUPPLIED",
                "note": (
                    "SURVIVORSHIP BIAS WARNING: Historical repeat customers spent ~$1,292/year. "
                    "A 54% haircut ($700) is applied to reflect lower spending from marginally-saved churners. "
                    "Tested range: $500 to $1,000."
                ),
            },
            "r3_one_time_cost": {
                "value": 12000.0,
                "source": "USER_SUPPLIED",
                "note": "3PL vendor rebid, carrier API integration, loyalty program setup",
            },
            "r3_annual_opex": {
                "value": 9000.0,
                "source": "USER_SUPPLIED",
                "note": "Carrier SLA premium fee and loyalty rewards operational cost ($750.00/mo)",
            },
        },
        "hypothetical_inputs": {
            "r2_marketplace_fee_reduction_pp_base": {
                "value": 1.0,
                "source": "HYPOTHETICAL",
                "note": (
                    "Assumes a 1pp reduction in Marketplace commission fee (13% -> 12%). "
                    "Entirely speculative volume negotiation target. Conservative assumes 0pp (fails)."
                ),
            }
        },
        "scenario_multipliers": SCENARIO_MULTIPLIERS,
        "model_limitations": [
            "All cash flows are pre-tax and undiscounted by default. 10% annual WACC NPV is provided.",
            "Observational associations do NOT prove causal intervention effectiveness.",
            "Order price-elasticity retention rates (r1, r2) are management assumptions requiring A/B testing validation.",
            "Marketplace commission fee reduction is binary and speculative.",
            "Repeat customer spending is subject to survivorship bias; marginal churners may spend less.",
            "Seasonality and market macroeconomic growth are not assumed; 2025 order volume is held constant.",
            "Rec 3 on a standalone basis fails to break even over 36 months in Base and Conservative scenarios due to $9,000 annual opex exceeding standalone annual benefits.",
        ],
    }


def generate_roi_artifacts(
    df_2025: Optional[pd.DataFrame] = None,
    output_dir: Optional[Path] = None,
) -> Dict[str, Path]:
    """
    Generate all Stage 4 ROI deliverables deterministically:
      1. outputs/roi_scenarios.csv
      2. outputs/monthly_cash_flow.csv
      3. outputs/break_even_analysis.csv
      4. outputs/sensitivity_analysis.csv
      5. outputs/roi_assumptions.json
    """
    root = get_project_root()
    if output_dir is None:
        output_dir = root / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    if df_2025 is None:
        clean_path = root / "Dataset" / "clean_dataset.csv"
        df = pd.read_csv(clean_path)
        df["order_date"] = pd.to_datetime(df["order_date"])
        df_2025 = df[df["order_date"].dt.year == 2025].copy()

    # 1. Scenarios summary
    scenarios_df, results = build_scenarios_summary(df_2025)
    scenarios_path = output_dir / "roi_scenarios.csv"
    save_csv(scenarios_df, scenarios_path)

    # 2. Monthly cash flow
    monthly_cf_df = build_monthly_cash_flow_df(results)
    monthly_path = output_dir / "monthly_cash_flow.csv"
    save_csv(monthly_cf_df, monthly_path)

    # 3. Break-even analysis
    break_even_df = build_break_even_df(results, df_2025=df_2025)
    break_even_path = output_dir / "break_even_analysis.csv"
    save_csv(break_even_df, break_even_path)

    # 4. Sensitivity analysis (sweeping all 7 required dimensions)
    sensitivity_df = run_sensitivity_analysis(df_2025, n_steps=5)
    sensitivity_path = output_dir / "sensitivity_analysis.csv"
    save_csv(sensitivity_df, sensitivity_path)

    # 5. Assumptions JSON
    assumptions_dict = build_assumptions_json_dict()
    assumptions_path = output_dir / "roi_assumptions.json"
    save_json(assumptions_dict, assumptions_path, indent=2)

    return {
        "scenarios": scenarios_path,
        "monthly_cash_flow": monthly_path,
        "break_even": break_even_path,
        "sensitivity": sensitivity_path,
        "assumptions": assumptions_path,
    }


if __name__ == "__main__":
    paths = generate_roi_artifacts()
    print("Stage 4 ROI artifacts generated successfully:")
    for k, v in paths.items():
        print(f" - {k}: {v}")
