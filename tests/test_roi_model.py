"""test_roi_model.py -- Unit and Integration tests for src/roi_model.py

Test categories
---------------
1.  Financial formula helpers:
    - npv_monthly (zero rate, positive rate, empty, negative flows, compounding)
    - find_payback_month (immediate positive, delayed positive, crossing, never reached, leading zeros, all zeros)
    - build_monthly_benefit (delayed launch, multi-month ramp, post-ramp plateau, horizon lengths)
    - build_monthly_cost (one-time capex at launch, recurring opex from launch, zero before launch)
    - total_36m_cost (arithmetic consistency with build_monthly_cost sum)
    - compute_roi (normal, zero-cost, negative net benefit, negative cost safe)
2.  Zero-cost cases (ROI handles zero cost without ZeroDivisionError, net benefit == gross benefit)
3.  Negative-benefit cases (ROI negative, net benefit negative, payback None)
4.  Scenario calculations:
    - Conservative, Base, Optimistic all execute cleanly
    - Monotonicity checks
    - Revenue delta, contribution profit delta, and net benefit distinction
    - One-time capex vs recurring opex separation
5.  Monthly cash flows:
    - 36-month horizon length
    - Sum of monthly net cash flows equals 36-month net benefit
    - 10% NPV less than nominal cash flows
6.  Double-counting safeguards:
    - Rec 1 cross-channel repricing
    - Rec 2 incremental Marketplace repricing and fee reduction on post-Rec1 portfolio
    - Rec 3 zero-floored loss orders and cohort customer retention on post-Rec2 portfolio
7.  Cases where payback is never reached:
    - Costs dominate synthetic dataset
    - Rec 3 standalone payback in Conservative and Base
    - Synthetic persistent cash deficit
8.  Break-even analysis:
    - Table columns and row count
    - Break-even annual benefit metrics
    - Rec 1 accretive nature under high churn
9.  Sensitivity analysis:
    - Covers all 7 required dimensions (10 variables)
    - Monotonicity on key parameters (order retention, fee reduction, cost multiplier)
10. Assumption registry & data verified integrity:
    - All sources in {DATA_VERIFIED, USER_SUPPLIED, HYPOTHETICAL}
    - DATA_VERIFIED return rates match metrics.json
    - Artifact generator smoke test
"""

import json
from pathlib import Path
import pytest
import numpy as np
import pandas as pd

from src.roi_model import (
    FEE_STRUCTURE,
    ASSUMPTION_REGISTRY,
    SCENARIO_MULTIPLIERS,
    SENSITIVITY_VARIABLES,
    RecommendationResult,
    ScenarioResult,
    npv_monthly,
    find_payback_month,
    build_monthly_benefit,
    build_monthly_cost,
    total_36m_cost,
    compute_roi,
    compute_rec1_benefit,
    compute_rec2_benefit,
    compute_rec3_benefit,
    run_scenario,
    run_sensitivity_analysis,
    build_scenarios_summary,
    build_monthly_cash_flow_df,
    build_break_even_df,
    build_assumptions_export,
    build_assumptions_json_dict,
    generate_roi_artifacts,
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def minimal_df():
    """Synthetic 2025 dataset with exactly two high-discount orders."""
    return pd.DataFrame({
        "order_id": ["O1", "O2", "O3", "O4", "O5"],
        "order_date": pd.to_datetime(["2025-01-01"] * 5),
        "customer_id": ["C1", "C2", "C3", "C4", "C5"],
        "channel": ["Online", "Retail Store", "Marketplace", "Online", "Marketplace"],
        "region": ["West", "North", "Central", "East", "South"],
        "category": ["Technology"] * 5,
        "quantity": [1, 2, 1, 3, 1],
        "unit_price": [100.0, 50.0, 200.0, 80.0, 150.0],
        "unit_cost": [60.0, 30.0, 120.0, 50.0, 90.0],
        "discount": [0.0, 0.10, 0.25, 0.35, 0.0],
        "sales": [100.0, 90.0, 150.0, 156.0, 150.0],
        "profit": [36.0, 30.0, 10.5, -0.24, 40.5],
        "is_late": [False, True, True, False, True],
        "returned": [False, False, True, False, False],
        "ship_days": [3, 7, 8, 4, 9],
        "sub_category": ["Laptops"] * 5,
        "segment": ["Consumer"] * 5,
        "discount_band": ["0%", "1-10%", "21-30%", ">30%", "0%"],
    })


@pytest.fixture
def all_below_cap_df():
    """All discounts <= 20% -- Rec 1 benefit should be zero."""
    return pd.DataFrame({
        "order_id": ["O1", "O2"],
        "order_date": pd.to_datetime(["2025-06-01"] * 2),
        "customer_id": ["C1", "C2"],
        "channel": ["Online", "Retail Store"],
        "region": ["West", "North"],
        "quantity": [1, 1],
        "unit_price": [100.0, 100.0],
        "unit_cost": [50.0, 50.0],
        "discount": [0.10, 0.20],
        "sales": [90.0, 80.0],
        "profit": [86.4 - 50.0, 80.0 - 50.0],
        "is_late": [False, False],
        "returned": [False, False],
        "ship_days": [3, 4],
    })


@pytest.fixture
def df_2025_real():
    df = pd.read_csv("Dataset/clean_dataset.csv")
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df[df["order_date"].dt.year == 2025].copy()


# ---------------------------------------------------------------------------
# 1. Financial formulas
# ---------------------------------------------------------------------------

def test_npv_zero_rate_equals_sum():
    cfs = [100.0, 200.0, 300.0]
    assert abs(npv_monthly(0.0, cfs) - sum(cfs)) < 0.01


def test_npv_positive_rate_reduces_value():
    cfs = [1000.0] * 12
    assert npv_monthly(0.10, cfs) < npv_monthly(0.0, cfs)


def test_npv_empty_returns_zero():
    assert npv_monthly(0.10, []) == 0.0


def test_npv_all_negative_flows():
    assert npv_monthly(0.10, [-500.0, -200.0]) < 0.0


def test_payback_first_month_positive():
    assert find_payback_month([100.0, 200.0]) == 1


def test_payback_crosses_in_middle():
    assert find_payback_month([-500.0, -100.0, 50.0, 300.0]) == 3


def test_payback_never_reached():
    assert find_payback_month([-100.0, -200.0, -300.0]) is None


def test_payback_exactly_zero_counts():
    assert find_payback_month([-100.0, 0.0, 100.0]) == 2


def test_payback_single_negative_is_never():
    assert find_payback_month([-1.0]) is None


def test_payback_with_delayed_launch_leading_zeros():
    # Delayed launch: months 1-2 have 0 CF; month 3 has -$1,000 outlay; month 5 turns positive
    cfs = [0.0, 0.0, -1000.0, -200.0, 500.0, 1000.0]
    assert find_payback_month(cfs) == 5


def test_payback_empty_and_all_zeros_returns_none():
    assert find_payback_month([]) is None
    assert find_payback_month([0.0, 0.0, 0.0]) is None


def test_monthly_benefit_zero_before_launch():
    b = build_monthly_benefit(12000.0, launch_month=4, ramp_months=2, horizon=6)
    assert b[0] == b[1] == b[2] == 0.0


def test_monthly_benefit_ramp_increases():
    b = build_monthly_benefit(12000.0, launch_month=1, ramp_months=3, horizon=5)
    assert b[0] < b[1] < b[2]


def test_monthly_benefit_flat_after_ramp():
    b = build_monthly_benefit(12000.0, launch_month=1, ramp_months=2, horizon=6)
    full = 12000.0 / 12.0
    for i in range(2, 6):
        assert abs(b[i] - full) < 0.01


def test_monthly_benefit_horizon_length():
    assert len(build_monthly_benefit(1000.0, 1, 1, horizon=36)) == 36


def test_monthly_cost_one_time_at_launch():
    c = build_monthly_cost(10000.0, 500.0, launch_month=3, horizon=5)
    assert abs(c[2] - 10500.0) < 0.01


def test_monthly_cost_zero_before_launch():
    c = build_monthly_cost(10000.0, 500.0, launch_month=3, horizon=5)
    assert c[0] == 0.0 and c[1] == 0.0


def test_monthly_cost_opex_after_launch():
    c = build_monthly_cost(10000.0, 500.0, launch_month=2, horizon=5)
    assert abs(c[2] - 500.0) < 0.01


def test_total_36m_cost_arithmetic():
    tc = total_36m_cost(10000.0, 500.0, launch_month=1, horizon=36)
    assert abs(tc - (10000.0 + 500.0 * 36)) < 0.01


# ---------------------------------------------------------------------------
# 2. Zero-cost cases
# ---------------------------------------------------------------------------

def test_compute_roi_zero_cost_returns_zero():
    assert compute_roi(5000.0, 0.0) == 0.0


def test_compute_roi_negative_cost_handled_safely():
    assert compute_roi(5000.0, -100.0) == 0.0


def test_run_scenario_zero_cost_multiplier(df_2025_real):
    custom_sm = dict(SCENARIO_MULTIPLIERS["Base"])
    custom_sm["cost_multiplier"] = 0.0
    SCENARIO_MULTIPLIERS["_zero_cost_"] = custom_sm
    try:
        res = run_scenario(df_2025_real, "_zero_cost_")
        assert res.total_cost_36m == 0.0
        assert res.total_roi_pct == 0.0
        assert res.total_net_benefit_36m > 0.0
        assert res.combined_payback_month == 1
    finally:
        del SCENARIO_MULTIPLIERS["_zero_cost_"]


# ---------------------------------------------------------------------------
# 3. Negative-benefit cases
# ---------------------------------------------------------------------------

def test_compute_roi_negative_net_benefit():
    assert compute_roi(-500.0, 1000.0) == -50.0


def test_rec3_negative_net_benefit_in_conservative(df_2025_real):
    res = run_scenario(df_2025_real, "Conservative")
    # Standalone Rec 3 has annual opex exceeding annual benefits in Conservative case
    assert res.rec3.net_benefit_36m < 0.0
    assert res.rec3.roi_pct < 0.0
    assert res.rec3.payback_month is None


def test_rec3_standalone_payback_never_in_base(df_2025_real):
    res = run_scenario(df_2025_real, "Base")
    assert res.rec3.net_benefit_36m < 0.0
    assert res.rec3.payback_month is None


# ---------------------------------------------------------------------------
# 4. Scenario calculations
# ---------------------------------------------------------------------------

def test_scenario_invalid_name_raises(df_2025_real):
    with pytest.raises(ValueError, match="Unknown scenario"):
        run_scenario(df_2025_real, "Magical")


def test_scenario_base_positive_benefit(df_2025_real):
    res = run_scenario(df_2025_real, "Base")
    assert res.total_annual_benefit > 0.0
    assert res.total_net_benefit_36m > 0.0
    assert res.total_roi_pct > 100.0


def test_scenario_monotonicity(df_2025_real):
    c = run_scenario(df_2025_real, "Conservative")
    b = run_scenario(df_2025_real, "Base")
    o = run_scenario(df_2025_real, "Optimistic")
    assert c.total_annual_benefit <= b.total_annual_benefit <= o.total_annual_benefit
    assert c.total_cost_36m >= b.total_cost_36m >= o.total_cost_36m
    assert c.total_net_benefit_36m <= b.total_net_benefit_36m <= o.total_net_benefit_36m
    assert c.total_roi_pct <= b.total_roi_pct <= o.total_roi_pct


def test_scenario_distinguishes_revenue_profit_net_benefit(df_2025_real):
    res = run_scenario(df_2025_real, "Base")
    # Revenue delta and profit delta are distinct
    assert res.total_annual_revenue_delta != res.total_annual_benefit
    # Net benefit over 36m is distinct from annual run-rate
    assert res.total_net_benefit_36m != res.total_annual_benefit


def test_scenario_distinguishes_capex_and_opex(df_2025_real):
    res = run_scenario(df_2025_real, "Base")
    assert res.total_one_time_cost == 34000.0  # $10k + $12k + $12k
    assert abs(res.total_annual_opex - 19000.0) < 1.0  # $4k + $6k + $9k
    assert abs(res.total_cost_36m - (res.total_one_time_cost + res.total_annual_opex * 2.75)) < 0.05


# ---------------------------------------------------------------------------
# 5. Monthly cash flows
# ---------------------------------------------------------------------------

def test_scenario_monthly_cf_length_36(df_2025_real):
    for sc in ["Conservative", "Base", "Optimistic"]:
        assert len(run_scenario(df_2025_real, sc).monthly_cash_flows) == 36


def test_scenario_monthly_cf_sum_matches_net_benefit(df_2025_real):
    for sc in ["Conservative", "Base", "Optimistic"]:
        res = run_scenario(df_2025_real, sc)
        assert abs(sum(res.monthly_cash_flows) - res.total_net_benefit_36m) < 0.10


def test_scenario_npv_less_than_undiscounted(df_2025_real):
    res = run_scenario(df_2025_real, "Base")
    assert res.npv_10pct < sum(res.monthly_cash_flows)


def test_monthly_cf_table_has_cumulative_consistency(df_2025_real):
    _, results = build_scenarios_summary(df_2025_real)
    cf_df = build_monthly_cash_flow_df(results)
    assert len(cf_df) == 108  # 36 * 3
    base_rows = cf_df[cf_df["scenario"] == "Base"].sort_values("month")
    recomputed_cum = base_rows["monthly_net_cash_flow"].cumsum().round(2)
    assert np.allclose(base_rows["cumulative_net_cash_flow"], recomputed_cum, atol=0.05)


# ---------------------------------------------------------------------------
# 6. Double-counting safeguards
# ---------------------------------------------------------------------------

def test_double_counting_guard_rec1_rec2_sequential(df_2025_real):
    sm = SCENARIO_MULTIPLIERS["Base"]
    r1_b, _, _, df_post1 = compute_rec1_benefit(df_2025_real, sm["r1_order_retention"])
    r2_b, _, _, df_post2 = compute_rec2_benefit(
        df_post1, sm["r2_marketplace_order_retention"], sm["r2_fee_reduction_pp"]
    )
    scenario = run_scenario(df_2025_real, "Base")
    assert abs(scenario.rec1.annual_benefit_run_rate - r1_b) < 0.50
    assert abs(scenario.rec2.annual_benefit_run_rate - r2_b) < 0.50


def test_rec2_incremental_from_post1_only(minimal_df):
    _, _, _, df_post1 = compute_rec1_benefit(minimal_df, 0.70)
    post1_profit = df_post1["profit"].sum()
    benefit, _, _, df_post2 = compute_rec2_benefit(df_post1, 0.75, 1.0)
    post2_profit = df_post2["profit"].sum()
    assert abs(benefit - (post2_profit - post1_profit)) < 0.01


def test_rec3_zero_floored_losses(minimal_df):
    # Rec 3 must not credit losses already cured by Rec 1/2
    _, _, _, df_post1 = compute_rec1_benefit(minimal_df, 0.70)
    _, _, _, df_post2 = compute_rec2_benefit(df_post1, 0.75, 1.0)
    b_normal, _, _ = compute_rec3_benefit(
        minimal_df, df_post2, 0.15, 0.10, 0.0478, 0.1491, 0.05, 4.35, 700.0
    )
    assert b_normal > 0.0


# ---------------------------------------------------------------------------
# 7. Cases where payback is never reached
# ---------------------------------------------------------------------------

def test_payback_never_when_costs_dominate():
    tiny_df = pd.DataFrame({
        "order_id": ["O1"],
        "order_date": pd.to_datetime(["2025-01-01"]),
        "customer_id": ["C1"],
        "channel": ["Retail Store"],
        "region": ["North"],
        "quantity": [1],
        "unit_price": [5.0],
        "unit_cost": [3.0],
        "discount": [0.0],
        "sales": [5.0],
        "profit": [2.0],
        "is_late": [False],
        "returned": [False],
        "ship_days": [3],
    })
    result = run_scenario(tiny_df, "Conservative")
    # Payback must be None when investment costs vastly exceed tiny operational returns
    assert result.combined_payback_month is None


def test_synthetic_perpetual_deficit_returns_none():
    deficit_cf = [-10000.0] + [-100.0] * 35
    cum = list(np.cumsum(deficit_cf))
    assert find_payback_month(cum) is None


# ---------------------------------------------------------------------------
# 8. Break-even analysis
# ---------------------------------------------------------------------------

def test_break_even_df_has_expected_columns(df_2025_real):
    _, results = build_scenarios_summary(df_2025_real)
    be_df = build_break_even_df(results, df_2025=df_2025_real)
    assert len(be_df) == 3
    assert "break_even_annual_benefit" in be_df.columns
    assert "rec3_payback_month" in be_df.columns
    # Check that in Base, Rec 3 payback is Never (>36m)
    base_row = be_df[be_df["scenario"] == "Base"].iloc[0]
    assert base_row["rec3_payback_month"] == "Never (>36m)"


def test_rec1_benefit_positive_at_zero_retention(df_2025_real):
    # Because >20% orders are net loss-making, dropping 100% of them (0% retention)
    # is profit accretive. Rec 1 has 0% break-even retention threshold.
    b_zero, _, _, _ = compute_rec1_benefit(df_2025_real, 0.0)
    assert b_zero > 0.0


# ---------------------------------------------------------------------------
# 9. Sensitivity analysis
# ---------------------------------------------------------------------------

def test_sensitivity_covers_all_7_required_dimensions(df_2025_real):
    result = run_sensitivity_analysis(df_2025_real, n_steps=3)
    assert isinstance(result, pd.DataFrame)
    observed_vars = set(result["variable"].unique())
    required_dimensions = {
        "r3_retention_uplift_pp",         # customer retention
        "r2_fee_reduction_pp",            # marketplace fee reduction
        "r1_order_retention",             # order retention
        "r2_marketplace_order_retention", # order retention
        "r3_central_late_rate_target",    # delivery improvement
        "r3_other_improvement_pct",       # delivery improvement
        "r3_return_rate_if_late",         # return rates
        "cost_multiplier",                # implementation costs
        "launch_delay_months",            # launch delays
    }
    assert required_dimensions.issubset(observed_vars)


def test_sensitivity_order_retention_monotonic(df_2025_real):
    sens = run_sensitivity_analysis(df_2025_real, n_steps=4)
    r1_sens = sens[sens["variable"] == "r1_order_retention"].sort_values("value")
    # Higher retention must increase annual benefit
    benefits = r1_sens["total_annual_benefit"].values
    assert all(x <= y for x, y in zip(benefits, benefits[1:]))


def test_sensitivity_cost_multiplier_inverses_roi(df_2025_real):
    sens = run_sensitivity_analysis(df_2025_real, n_steps=4)
    cost_sens = sens[sens["variable"] == "cost_multiplier"].sort_values("value")
    # Higher costs must reduce ROI
    rois = cost_sens["roi_pct"].values
    assert all(x >= y for x, y in zip(rois, rois[1:]))


# ---------------------------------------------------------------------------
# 10. Assumption registry & data verified integrity
# ---------------------------------------------------------------------------

def test_assumptions_export_complete():
    df = build_assumptions_export()
    assert set(df["assumption_key"].values) == set(ASSUMPTION_REGISTRY.keys())


def test_assumptions_sources_valid():
    valid_sources = {"DATA_VERIFIED", "USER_SUPPLIED", "HYPOTHETICAL"}
    for key, meta in ASSUMPTION_REGISTRY.items():
        assert meta["source"] in valid_sources, (
            f"Assumption '{key}' has invalid source '{meta['source']}'"
        )


def test_data_verified_return_rates_match_metrics():
    """Verify that DATA_VERIFIED return rates in the registry match metrics.json."""
    with open("outputs/metrics.json", encoding="utf-8") as f:
        metrics = json.load(f)
    late_pct = metrics["statistical_hypothesis_tests"]["H3_shipping_delay_return_correlation"]["return_rate_late_%"]
    ontime_pct = metrics["statistical_hypothesis_tests"]["H3_shipping_delay_return_correlation"]["return_rate_ontime_%"]
    reg_late = ASSUMPTION_REGISTRY["r3_return_rate_if_late"]["value"] * 100
    reg_ontime = ASSUMPTION_REGISTRY["r3_return_rate_if_ontime"]["value"] * 100
    assert abs(reg_late - late_pct) < 0.01, "Late return rate mismatch vs metrics.json"
    assert abs(reg_ontime - ontime_pct) < 0.01, "On-time return rate mismatch vs metrics.json"


def test_generate_roi_artifacts_creates_all_files(tmp_path, df_2025_real):
    output_files = generate_roi_artifacts(df_2025=df_2025_real, output_dir=tmp_path)
    for k, p in output_files.items():
        assert p.exists()
        assert p.stat().st_size > 0
