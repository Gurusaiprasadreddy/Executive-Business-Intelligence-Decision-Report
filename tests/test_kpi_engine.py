"""Unit Tests for KPI Engine

Verifies financial formula precision, weighted profit margin vs unweighted averages,
zero-denominator handling, and cohort metric calculations.
"""

import pytest
import numpy as np
import pandas as pd
from src.kpi_engine import (
    safe_divide,
    calculate_weighted_profit_margin,
    calculate_annual_metrics,
    calculate_monthly_metrics,
    calculate_channel_metrics,
    calculate_discount_band_metrics,
    calculate_customer_cohort_metrics
)


def test_safe_divide_and_zero_denominator():
    """Verify division handles zero, None, and NaN safely."""
    assert safe_divide(10, 2) == 5.0
    assert safe_divide(10, 0) == 0.0
    assert safe_divide(10, 0, default=-1.0) == -1.0
    assert safe_divide(10, np.nan) == 0.0


def test_weighted_vs_unweighted_margin():
    """
    Demonstrate that weighted margin (Sum Profit / Sum Sales)
    differs from simple arithmetic average of order margins.
    """
    # Order 1: Sales $1,000, Profit $100 -> Margin 10%
    # Order 2: Sales $10, Profit $5 -> Margin 50%
    # Simple average margin = (10% + 50%) / 2 = 30%
    # True portfolio weighted margin = $105 / $1,010 = 10.396%
    df = pd.DataFrame({
        "order_id": ["O1", "O2"],
        "sales": [1000.0, 10.0],
        "profit": [100.0, 5.0]
    })
    weighted = calculate_weighted_profit_margin(df["profit"].sum(), df["sales"].sum())
    simple_avg = (df["profit"] / df["sales"]).mean() * 100.0

    assert np.isclose(weighted, 10.396, atol=1e-3)
    assert np.isclose(simple_avg, 30.0)
    assert weighted != simple_avg


def test_annual_metrics_calculation():
    """Verify annual aggregation, record counts, and derived rates."""
    df = pd.DataFrame({
        "order_id": ["O1", "O2", "O3", "O4"],
        "order_date": pd.to_datetime(["2023-05-01", "2023-11-10", "2024-03-15", "2024-09-20"]),
        "customer_id": ["C1", "C2", "C1", "C3"],
        "sales": [100.0, 200.0, 150.0, 250.0],
        "profit": [20.0, 40.0, 15.0, 50.0],
        "returned": [False, True, False, False],
        "is_late": [False, False, True, False]
    })
    ann = calculate_annual_metrics(df)

    assert len(ann) == 3  # 2023, 2024, Total
    row_2023 = ann[ann["Year"] == 2023].iloc[0]
    assert row_2023["Revenue"] == 300.0
    assert row_2023["Profit"] == 60.0
    assert row_2023["Weighted_Profit_Margin_%"] == 20.0
    assert row_2023["Record_Count"] == 2
    assert row_2023["Unique_Orders"] == 2
    assert row_2023["Unique_Customers"] == 2
    assert row_2023["Return_Rate_%"] == 50.0

    tot_row = ann[ann["Year"] == "Total / Overall"].iloc[0]
    assert tot_row["Revenue"] == 700.0
    assert tot_row["Profit"] == 125.0
    assert tot_row["Unique_Customers"] == 3


def test_customer_cohort_retention():
    """Verify retention calculation across calendar years."""
    # 2023: C1, C2 (2 customers)
    # 2024: C1, C3 (2 customers, C1 retained -> 1/2 = 50% retention)
    # 2025: C1, C3, C4 (3 customers, C1 & C3 retained -> 2/2 = 100% retention)
    df = pd.DataFrame({
        "order_id": ["O1", "O2", "O3", "O4", "O5", "O6", "O7"],
        "order_date": pd.to_datetime([
            "2023-01-10", "2023-06-12",
            "2024-02-14", "2024-08-20",
            "2025-01-05", "2025-04-10", "2025-07-15"
        ]),
        "customer_id": ["C1", "C2", "C1", "C3", "C1", "C3", "C4"],
        "sales": [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0]
    })
    res = calculate_customer_cohort_metrics(df)
    assert res["retention_2023_to_2024_%"] == 50.0
    assert res["retention_2024_to_2025_%"] == 100.0


def test_discount_band_metrics():
    """Verify grouping and loss-making order identification across discount bands."""
    df = pd.DataFrame({
        "order_id": ["O1", "O2", "O3"],
        "discount": [0.00, 0.15, 0.35],
        "sales": [100.0, 200.0, 300.0],
        "profit": [30.0, 20.0, -50.0]
    })
    disc_df = calculate_discount_band_metrics(df)
    assert len(disc_df) == 5  # 5 standard bins

    deep_disc = disc_df[disc_df["discount_band"] == ">30%"].iloc[0]
    assert deep_disc["orders"] == 1
    assert deep_disc["loss_orders"] == 1
    assert deep_disc["loss_order_share_%"] == 100.0
    assert deep_disc["profit"] == -50.0
