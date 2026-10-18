"""Unit Tests for Validation Module

Verifies that validation passes on compliant datasets and fails loudly with explicit
diagnostics when nulls, duplicates, invalid ranges, or arithmetic errors are introduced.
"""

import pytest
import numpy as np
import pandas as pd
from src.validation import validate_dataset, REQUIRED_CLEAN_COLUMNS


@pytest.fixture
def valid_clean_fixture() -> pd.DataFrame:
    """Fixture providing a minimal 100% compliant clean dataset."""
    df = pd.DataFrame({
        "order_id": ["O101", "O102"],
        "order_date": pd.to_datetime(["2024-03-01", "2024-04-15"]),
        "customer_id": ["C1", "C2"],
        "segment": ["Consumer", "Corporate"],
        "region": ["West", "East"],
        "category": ["Technology", "Office Supplies"],
        "sub_category": ["Phones", "Paper"],
        "channel": ["Online", "Retail Store"],
        "quantity": [2, 5],
        "unit_price": [100.0, 20.0],
        "discount": [0.10, 0.00],
        "unit_cost": [60.0, 10.0],
        "sales": [180.0, 100.0],  # 2*100*0.9 = 180; 5*20*1 = 100
        # profit = sales*(1 - fee) - qty*cost
        # O101: 180*(1 - 0.04) - 2*60 = 172.80 - 120 = 52.80
        # O102: 100*(1 - 0.00) - 5*10 = 100 - 50 = 50.00
        "profit": [52.80, 50.00],
        "ship_days": [3.0, 6.0],
        "returned": [False, True],
        "ship_days_imputed": [False, False],
        "order_year": [2024, 2024],
        "order_month": [3, 4],
        "order_quarter": [1, 2],
        "year_month": ["2024-03", "2024-04"],
        "profit_margin": [52.80 / 180.0, 50.0 / 100.0],
        "discount_band": pd.Categorical(["1-10%", "0%"], categories=["0%", "1-10%", "11-20%", "21-30%", ">30%"]),
        "is_late": [False, True],
        "is_loss_order": [False, False],
        "customer_type": ["One-time", "One-time"],
        "channel_fee": [0.04, 0.00]
    })
    return df


def test_validation_passes_valid_data(valid_clean_fixture):
    """Verify clean compliant data passes all validation checks."""
    is_valid, report, summary = validate_dataset(valid_clean_fixture)
    assert is_valid is True
    assert summary["failed_checks"] == 0
    assert summary["overall_validation_status"] == "VALIDATED"


def test_validation_fails_on_nulls(valid_clean_fixture):
    """Verify validation catches null values."""
    bad_df = valid_clean_fixture.copy()
    bad_df.loc[0, "segment"] = np.nan
    is_valid, report, summary = validate_dataset(bad_df)
    assert is_valid is False
    assert summary["failed_checks"] >= 1
    fail_row = report[report["Check_Name"] == "Missing Values Count"].iloc[0]
    assert fail_row["Status"] == "FAIL"


def test_validation_fails_on_duplicate_orders(valid_clean_fixture):
    """Verify validation catches duplicate order IDs."""
    bad_df = valid_clean_fixture.copy()
    bad_df.loc[1, "order_id"] = "O101"  # duplicate of O101
    is_valid, report, summary = validate_dataset(bad_df)
    assert is_valid is False
    fail_row = report[report["Check_Name"] == "Order ID Uniqueness"].iloc[0]
    assert fail_row["Status"] == "FAIL"


def test_validation_fails_on_sales_arithmetic_error(valid_clean_fixture):
    """Verify validation catches discrepancy between sales and quantity*price*(1-discount)."""
    bad_df = valid_clean_fixture.copy()
    bad_df.loc[0, "sales"] = 999.0  # expected is 180.0
    is_valid, report, summary = validate_dataset(bad_df)
    assert is_valid is False
    fail_row = report[report["Check_Name"] == "Sales Formula Consistency (<2% dev)"].iloc[0]
    assert fail_row["Status"] == "FAIL"


def test_validation_fails_on_profit_arithmetic_error(valid_clean_fixture):
    """Verify validation catches discrepancy between profit and sales*(1-fee) - qty*cost."""
    bad_df = valid_clean_fixture.copy()
    bad_df.loc[0, "profit"] = 250.0  # expected is 52.80
    is_valid, report, summary = validate_dataset(bad_df)
    assert is_valid is False
    fail_row = report[report["Check_Name"] == "Profit Formula Consistency (<$0.10 dev)"].iloc[0]
    assert fail_row["Status"] == "FAIL"


def test_validation_fails_on_missing_column(valid_clean_fixture):
    """Verify validation catches missing schema column."""
    bad_df = valid_clean_fixture.drop(columns=["is_late"])
    is_valid, report, summary = validate_dataset(bad_df)
    assert is_valid is False
    fail_row = report[report["Check_Name"] == "Required Schema Completeness"].iloc[0]
    assert fail_row["Status"] == "FAIL"
