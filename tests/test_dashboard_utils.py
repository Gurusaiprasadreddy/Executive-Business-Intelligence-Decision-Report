"""Unit and Integration Tests for Dashboard Utilities & Consistency Agreement

Tests data loading, dimensional filtering, empty result handling, error states,
and mathematical agreement between the dashboard, KPI engine, and authoritative metrics.
"""

import pytest
import pandas as pd
import numpy as np

from src.dashboard_utils import (
    load_clean_data,
    load_authoritative_metrics,
    apply_filters,
    format_currency,
    format_pct,
    get_plotly_layout
)
from src.kpi_engine import (
    calculate_annual_metrics,
    calculate_weighted_profit_margin,
    calculate_channel_metrics
)
from src.io_utils import get_project_root, load_json


@pytest.fixture
def mock_dashboard_df() -> pd.DataFrame:
    """Fixture providing a controlled multi-dimensional dataset for filter testing."""
    return pd.DataFrame({
        "order_id": ["O1", "O2", "O3", "O4", "O5"],
        "order_date": pd.to_datetime(["2023-01-10", "2023-06-15", "2024-03-20", "2024-11-05", "2025-08-12"]),
        "region": ["West", "East", "Central", "West", "South"],
        "category": ["Technology", "Furniture", "Office Supplies", "Technology", "Furniture"],
        "sub_category": ["Phones", "Chairs", "Paper", "Accessories", "Tables"],
        "channel": ["Online", "Retail Store", "Marketplace", "Online", "Marketplace"],
        "discount_band": ["0%", "1-10%", "21-30%", "11-20%", ">30%"],
        "sales": [100.0, 200.0, 50.0, 150.0, 300.0],
        "profit": [20.0, 40.0, -10.0, 25.0, -50.0],
        "returned": [False, False, True, False, True],
        "is_late": [False, False, True, False, True]
    })


def test_load_clean_data():
    """Verify clean dataset loads and date column is parsed as datetime."""
    df = load_clean_data()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert pd.api.types.is_datetime64_any_dtype(df["order_date"])
    assert len(df) == 11996


def test_load_authoritative_metrics():
    """Verify authoritative metrics.json loads and matches expected schema."""
    metrics = load_authoritative_metrics()
    assert isinstance(metrics, dict)
    assert "metadata" in metrics
    assert "annual_metrics" in metrics
    assert "validation_summary" in metrics
    assert metrics["validation_summary"]["overall_validation_status"] == "VALIDATED"


def test_apply_filters_date_range(mock_dashboard_df):
    """Verify filtering by date range correctly bounds rows."""
    date_range = (pd.to_datetime("2023-01-01"), pd.to_datetime("2023-12-31"))
    filtered = apply_filters(mock_dashboard_df, date_range=date_range)
    assert len(filtered) == 2
    assert set(filtered["order_id"]) == {"O1", "O2"}


def test_apply_filters_categorical(mock_dashboard_df):
    """Verify filtering across multi-categorical dimensions."""
    filtered = apply_filters(
        mock_dashboard_df,
        regions=["West"],
        channels=["Online"],
        categories=["Technology"]
    )
    assert len(filtered) == 2
    assert set(filtered["order_id"]) == {"O1", "O4"}


def test_apply_filters_empty_result(mock_dashboard_df):
    """Verify empty filter combinations return an empty DataFrame safely without error."""
    filtered = apply_filters(mock_dashboard_df, regions=["NonExistentRegion"])
    assert isinstance(filtered, pd.DataFrame)
    assert len(filtered) == 0


def test_format_helpers():
    """Verify currency and percentage formatting."""
    assert format_currency(1234567.89) == "$1.23M"
    assert format_currency(1234.56) == "$1,234.56"
    assert format_currency(25.50) == "$25.50"
    assert format_currency(None) == "$0.00"

    assert format_pct(15.44) == "15.4%"
    assert format_pct(0.0) == "0.0%"
    assert format_pct(None) == "0.0%"


def test_get_plotly_layout():
    """Verify standard Plotly layout includes consistent navy-and-white theme elements."""
    layout = get_plotly_layout(title="Test Chart", xaxis_title="X Axis", yaxis_title="Y Axis")
    assert layout["title"]["text"] == "Test Chart"
    assert layout["paper_bgcolor"] == "#FFFFFF"
    assert layout["xaxis"]["title"] == "X Axis"


def test_dashboard_and_kpi_engine_agreement():
    """Verify calculations performed on filtered slices match kpi_engine formulas."""
    df = load_clean_data()
    # Filter for 2024 Online orders
    mask = (df["order_date"].dt.year == 2024) & (df["channel"] == "Online")
    filtered = df[mask]

    rev_filtered = filtered["sales"].sum()
    prof_filtered = filtered["profit"].sum()
    margin_filtered = calculate_weighted_profit_margin(prof_filtered, rev_filtered)

    # Calculate via channel metrics
    chn_metrics = calculate_channel_metrics(df[df["order_date"].dt.year == 2024])
    online_row = chn_metrics[chn_metrics["channel"] == "Online"].iloc[0]

    assert np.isclose(rev_filtered, online_row["revenue"], atol=1e-2)
    assert np.isclose(prof_filtered, online_row["profit"], atol=1e-2)
    assert np.isclose(margin_filtered, online_row["weighted_margin_%"], atol=1e-2)


def test_authoritative_metrics_agreement():
    """Verify that outputs/metrics.json annual figures match Dataset/clean_dataset.csv."""
    df = load_clean_data()
    annual_df = calculate_annual_metrics(df)
    metrics_json = load_authoritative_metrics()
    json_annual = {row["Year"]: row for row in metrics_json["annual_metrics"]}

    for _, row in annual_df.iterrows():
        yr = row["Year"]
        assert yr in json_annual
        json_row = json_annual[yr]
        assert np.isclose(row["Revenue"], json_row["Revenue"], atol=1e-2)
        assert np.isclose(row["Profit"], json_row["Profit"], atol=1e-2)
        assert np.isclose(row["Weighted_Profit_Margin_%"], json_row["Weighted_Profit_Margin_%"], atol=1e-2)
        assert row["Record_Count"] == json_row["Record_Count"]
