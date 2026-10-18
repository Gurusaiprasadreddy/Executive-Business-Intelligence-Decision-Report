"""Unit and Integration Tests for Data Cleaning Pipeline

Uses synthetic test fixtures to test each transformation step in isolation,
and verifies determinism and complete audit trail generation.
"""

import pytest
import numpy as np
import pandas as pd
from src.data_cleaning import (
    parse_order_date,
    clean_currency_to_float,
    clean_boolean_flag,
    standardize_categorical_labels,
    detect_and_remove_duplicates,
    impute_missing_fields,
    correct_quantity_outliers,
    engineer_analytical_features,
    run_clean_pipeline
)


@pytest.fixture
def sample_raw_data() -> pd.DataFrame:
    """Fixture providing synthetic messy retail orders for pipeline testing."""
    return pd.DataFrame({
        "order_id": ["ORD001", "ORD002", "ORD002", "ORD003", "ORD004", "ORD005"],
        "order_date": ["2024-01-15", "15/02/2024", "15/02/2024", "Mar 10, 2024", "2024-04-01", "2024-05-20"],
        "customer_id": ["CUST1", "CUST2", "CUST2", "CUST1", "CUST3", "CUST4"],
        "segment": ["Consumer", " corporate ", " corporate ", np.nan, "Small Business", "Consumer"],
        "region": [" West ", "East", "East", np.nan, "Central", "North"],
        "category": [np.nan, "Technology", "Technology", "Technology", "Furniture", "Office Supplies"],
        "sub_category": ["Phones", "Accessories", "Accessories", "Phones", "Chairs", "Paper"],
        "channel": ["Online", "Marketplace", "Marketplace", "Retail Store", "Online", "Marketplace"],
        "quantity": [2.0, 5.0, 5.0, np.nan, 200.0, np.nan],  # ORD005 has both discount and qty missing
        "unit_price": [100.0, 50.0, 50.0, 100.0, 80.0, 20.0],
        "discount": [0.10, np.nan, np.nan, 0.20, 0.10, np.nan],
        "unit_cost": [60.0, 30.0, 30.0, 60.0, 40.0, 10.0],
        "sales": ["$180.00", "$225.00", "$225.00", "$160.00", "$14,400.00", "$20.00"],
        "profit": ["$45.20", "$-12.50", "$-12.50", "$40.00", "$4,800.00", "$5.00"],
        "ship_days": [3.0, 6.0, 6.0, np.nan, 4.0, 2.0],
        "returned": ["No", "Yes", "Yes", "N", "N", "Y"]
    })


def test_date_parsing():
    """Verify parsing of mixed date strings into timestamps."""
    dates = pd.Series(["2024-01-01", "15/02/2024", "Mar 10, 2024", "invalid", None])
    parsed = parse_order_date(dates)
    assert parsed.iloc[0] == pd.Timestamp("2024-01-01")
    assert parsed.iloc[1] == pd.Timestamp("2024-02-15")
    assert parsed.iloc[2] == pd.Timestamp("2024-03-10")
    assert pd.isna(parsed.iloc[3])
    assert pd.isna(parsed.iloc[4])


def test_currency_and_boolean_cleaning():
    """Verify currency stripping and boolean parsing."""
    curr = pd.Series(["$1,234.50", "$0.99", "500", "-$25.00"])
    cleaned_curr = clean_currency_to_float(curr)
    assert cleaned_curr.iloc[0] == 1234.50
    assert cleaned_curr.iloc[3] == -25.00

    flags = pd.Series(["Yes", "Y", "no", "N", "True", "False", None])
    cleaned_flags = clean_boolean_flag(flags)
    assert bool(cleaned_flags.iloc[0]) is True
    assert bool(cleaned_flags.iloc[1]) is True
    assert bool(cleaned_flags.iloc[2]) is False
    assert bool(cleaned_flags.iloc[3]) is False


def test_duplicate_detection(sample_raw_data):
    """Verify exact duplicate row identification and removal."""
    clean, dups = detect_and_remove_duplicates(sample_raw_data)
    assert len(sample_raw_data) == 6
    assert len(dups) == 1
    assert len(clean) == 5
    assert dups.iloc[0]["order_id"] == "ORD002"


def test_label_standardization():
    """Verify whitespace stripping and title casing."""
    df = pd.DataFrame({
        "region": [" north", "NORTH ", "North", "EAST", "south-west"],
        "category": [" technology ", "TECHNOLOGY", "Furniture", "furniture", "Office Supplies"]
    })
    cleaned, counts = standardize_categorical_labels(df, ["region", "category"])
    assert cleaned["region"].tolist() == ["North", "North", "North", "East", "South-West"]
    assert counts["category"]["after_variants"] == 3


def test_imputation_and_unrecoverable_drop(sample_raw_data):
    """Verify deterministic category, customer-mode region, and dropping unrecoverable records."""
    clean, _ = detect_and_remove_duplicates(sample_raw_data)
    for c in ["sales", "profit"]:
        clean[c] = clean_currency_to_float(clean[c])
    clean["order_date"] = parse_order_date(clean["order_date"])
    clean, _ = standardize_categorical_labels(clean, ["region", "segment", "category"])

    imputed, dropped, stats = impute_missing_fields(clean)

    # ORD005 had both discount and quantity missing -> must be dropped
    assert len(dropped) == 1
    assert dropped.iloc[0]["order_id"] == "ORD005"
    assert len(imputed) == 4

    # ORD001 had missing category -> imputed as Technology from Phones
    ord1 = imputed[imputed["order_id"] == "ORD001"].iloc[0]
    assert ord1["category"] == "Technology"

    # ORD003 had missing region/segment -> CUST1 mode is West / Consumer
    ord3 = imputed[imputed["order_id"] == "ORD003"].iloc[0]
    assert ord3["region"] == "West"
    assert ord3["segment"] == "Consumer"
    # ORD003 had missing quantity -> recovered from sales=160, price=100, disc=0.20 -> 160/(100*0.8) = 2.0
    assert ord3["quantity"] == 2


def test_outlier_correction():
    """Verify that quantity entry errors (>20) are corrected and financials recalculated."""
    df = pd.DataFrame({
        "order_id": ["O1", "O2"],
        "sub_category": ["Chairs", "Chairs"],
        "channel": ["Online", "Online"],
        "quantity": [4, 500],  # 500 is outlier
        "unit_price": [100.0, 100.0],
        "discount": [0.10, 0.10],
        "unit_cost": [60.0, 60.0],
        "sales": [360.0, 45000.0],
        "profit": [105.6, 13200.0]
    })
    corrected, stats = correct_quantity_outliers(df, max_qty=20)
    assert stats["quantity_outliers_corrected"] == 1
    row2 = corrected[corrected["order_id"] == "O2"].iloc[0]
    assert row2["quantity"] == 4  # replaced with median of subcategory (4)
    assert row2["sales"] == 360.0
    # profit = 360 * (1 - 0.04) - 4 * 60 = 345.60 - 240 = 105.60
    assert np.isclose(row2["profit"], 105.60)


def test_deterministic_cleaning_pipeline(sample_raw_data):
    """Verify that running the pipeline twice produces identical outputs byte-for-byte."""
    c1, log1, unrec1, stats1 = run_clean_pipeline(sample_raw_data)
    c2, log2, unrec2, stats2 = run_clean_pipeline(sample_raw_data)

    pd.testing.assert_frame_equal(c1, c2)
    pd.testing.assert_frame_equal(log1, log2)
    pd.testing.assert_frame_equal(unrec1, unrec2)
    assert stats1 == stats2
