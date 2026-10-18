"""Data Quality and Financial Validation Module

Implements automated quality gates, structural checks, mathematical consistency verification,
and detailed audit reporting for raw and clean retail sales datasets.
"""

from typing import Dict, List, Any, Tuple, Optional
import numpy as np
import pandas as pd

from src.data_cleaning import FEE_STRUCTURE


REQUIRED_CLEAN_COLUMNS = [
    "order_id", "order_date", "customer_id", "segment", "region", "category",
    "sub_category", "channel", "quantity", "unit_price", "discount", "unit_cost",
    "sales", "profit", "ship_days", "returned", "ship_days_imputed", "order_year",
    "order_month", "order_quarter", "year_month", "profit_margin", "discount_band",
    "is_late", "is_loss_order", "customer_type", "channel_fee"
]


def validate_dataset(
    clean_df: pd.DataFrame,
    raw_df: Optional[pd.DataFrame] = None
) -> Tuple[bool, pd.DataFrame, Dict[str, Any]]:
    """
    Run comprehensive suite of validation checks on the cleaned dataset.
    Returns:
    - is_valid (bool): True if all mandatory checks PASS
    - report_df (pd.DataFrame): Tabular data quality report
    - summary_dict (dict): Summary status dictionary
    """
    checks: List[Dict[str, Any]] = []

    def _add_check(
        category: str,
        name: str,
        level: str,
        status: str,
        observed: Any,
        expected: Any,
        details: str
    ):
        checks.append({
            "Check_Category": category,
            "Check_Name": name,
            "Level": level,
            "Status": status,
            "Observed_Value": str(observed),
            "Expected_Value": str(expected),
            "Details": details
        })

    # 1. Structural Checks
    null_count = int(clean_df.isna().sum().sum())
    _add_check(
        category="Structural",
        name="Missing Values Count",
        level="CRITICAL",
        status="PASS" if null_count == 0 else "FAIL",
        observed=null_count,
        expected=0,
        details="Clean dataset must contain zero null or NaT values"
    )

    dup_order_ids = int(clean_df["order_id"].duplicated().sum())
    _add_check(
        category="Structural",
        name="Order ID Uniqueness",
        level="CRITICAL",
        status="PASS" if dup_order_ids == 0 else "FAIL",
        observed=dup_order_ids,
        expected=0,
        details="Each row must represent a strictly unique order ID"
    )

    missing_cols = [c for c in REQUIRED_CLEAN_COLUMNS if c not in clean_df.columns]
    _add_check(
        category="Structural",
        name="Required Schema Completeness",
        level="CRITICAL",
        status="PASS" if not missing_cols else "FAIL",
        observed=f"{len(clean_df.columns)} columns (missing {len(missing_cols)})",
        expected=f"All {len(REQUIRED_CLEAN_COLUMNS)} required columns",
        details=f"Missing: {missing_cols}" if missing_cols else "All required schema columns present"
    )

    # 2. Pipeline Record Count Reconciliation (if raw_df is provided)
    if raw_df is not None:
        raw_rows = len(raw_df)
        raw_dups = int(raw_df.duplicated().sum())
        expected_clean_rows = raw_rows - raw_dups - 4  # 4 unrecoverable rows
        clean_rows = len(clean_df)
        _add_check(
            category="Pipeline Reconciliation",
            name="Row Count Arithmetic",
            level="CRITICAL",
            status="PASS" if clean_rows == expected_clean_rows else "FAIL",
            observed=clean_rows,
            expected=f"{expected_clean_rows} (raw: {raw_rows} - dups: {raw_dups} - unrecoverable: 4)",
            details="Clean row count must match raw count minus duplicates and dropped unrecoverables"
        )

    # 3. Domain and Range Integrity
    min_date = clean_df["order_date"].min()
    max_date = clean_df["order_date"].max()
    date_in_range = (pd.to_datetime(min_date) >= pd.to_datetime("2023-01-01")) and (pd.to_datetime(max_date) <= pd.to_datetime("2025-12-31"))
    _add_check(
        category="Domain Constraints",
        name="Date Range Validity",
        level="CRITICAL",
        status="PASS" if date_in_range else "FAIL",
        observed=f"{min_date} to {max_date}",
        expected="2023-01-01 to 2025-12-31",
        details="Order dates must fall within the 3-year study horizon"
    )

    qty_min = clean_df["quantity"].min()
    qty_max = clean_df["quantity"].max()
    qty_valid = (qty_min >= 1) and (qty_max <= 20) and (clean_df["quantity"] % 1 == 0).all()
    _add_check(
        category="Domain Constraints",
        name="Quantity Range & Integer Check",
        level="CRITICAL",
        status="PASS" if qty_valid else "FAIL",
        observed=f"min={qty_min}, max={qty_max}",
        expected="1 <= quantity <= 20 (integer)",
        details="All quantities must be valid order line integers without entry errors"
    )

    disc_min = clean_df["discount"].min()
    disc_max = clean_df["discount"].max()
    disc_valid = (disc_min >= 0.0) and (disc_max <= 0.50)
    _add_check(
        category="Domain Constraints",
        name="Discount Range Check",
        level="CRITICAL",
        status="PASS" if disc_valid else "FAIL",
        observed=f"min={disc_min:.2f}, max={disc_max:.2f}",
        expected="0.00 <= discount <= 0.50",
        details="Discount must be within legitimate commercial discount bounds"
    )

    prices_positive = (clean_df["unit_price"] > 0).all()
    costs_positive = (clean_df["unit_cost"] > 0).all()
    _add_check(
        category="Domain Constraints",
        name="Unit Price and Cost Positivity",
        level="CRITICAL",
        status="PASS" if (prices_positive and costs_positive) else "FAIL",
        observed=f"price_min={clean_df['unit_price'].min()}, cost_min={clean_df['unit_cost'].min()}",
        expected="Both > 0",
        details="Price and cost fields must be positive non-zero values"
    )

    # 4. Arithmetic and Accounting Consistency
    expected_sales = clean_df["quantity"] * clean_df["unit_price"] * (1 - clean_df["discount"])
    sales_rel_diff = (clean_df["sales"] - expected_sales).abs() / expected_sales
    sales_inconsistent = (sales_rel_diff > 0.02).sum()
    _add_check(
        category="Arithmetic Consistency",
        name="Sales Formula Consistency (<2% dev)",
        level="CRITICAL",
        status="PASS" if sales_inconsistent == 0 else "FAIL",
        observed=f"{sales_inconsistent} rows deviating >2% (max dev: ${(clean_df['sales'] - expected_sales).abs().max():.4f})",
        expected="0 rows deviating >2%",
        details="Sales must conform to quantity * unit_price * (1 - discount)"
    )

    expected_profit = clean_df["sales"] * (1 - clean_df["channel_fee"]) - clean_df["quantity"] * clean_df["unit_cost"]
    profit_abs_diff = (clean_df["profit"] - expected_profit).abs()
    profit_large_diff = (profit_abs_diff > 0.10).sum()
    _add_check(
        category="Arithmetic Consistency",
        name="Profit Formula Consistency (<$0.10 dev)",
        level="CRITICAL",
        status="PASS" if profit_large_diff == 0 else "FAIL",
        observed=f"{profit_large_diff} rows with abs dev > $0.10 (max dev: ${profit_abs_diff.max():.4f})",
        expected="0 rows deviating > $0.10",
        details="Profit must match sales * (1 - fee) - quantity * unit_cost (within cent rounding)"
    )

    # 5. Engineered Feature Consistency
    year_match = ("order_year" in clean_df.columns) and ("order_date" in clean_df.columns) and (clean_df["order_year"] == clean_df["order_date"].dt.year).all()
    margin_match = ("profit_margin" in clean_df.columns) and ("profit" in clean_df.columns) and ("sales" in clean_df.columns) and np.isclose(clean_df["profit_margin"], clean_df["profit"] / clean_df["sales"], atol=1e-5).all()
    late_match = ("is_late" in clean_df.columns) and ("ship_days" in clean_df.columns) and (clean_df["is_late"] == (clean_df["ship_days"] > 5)).all()
    loss_match = ("is_loss_order" in clean_df.columns) and ("profit" in clean_df.columns) and (clean_df["is_loss_order"] == (clean_df["profit"] < 0)).all()

    features_valid = year_match and margin_match and late_match and loss_match
    _add_check(
        category="Feature Engineering",
        name="Derived Feature Logic",
        level="CRITICAL",
        status="PASS" if features_valid else "FAIL",
        observed=f"year={year_match}, margin={margin_match}, is_late={late_match}, is_loss={loss_match}",
        expected="All derived features strictly consistent with parent columns",
        details="Validates year, profit_margin, is_late, and is_loss_order column integrity"
    )

    # 6. Informational Quality Checks (Warnings / Non-blocking)
    high_loss_orders = int((clean_df["profit"] < 0).sum())
    _add_check(
        category="Business Metrics",
        name="Loss-Making Orders Count",
        level="WARNING",
        status="INFO",
        observed=f"{high_loss_orders} orders ({high_loss_orders / len(clean_df) * 100:.1f}%)",
        expected="Monitored baseline",
        details="Orders where recorded profit is negative"
    )

    report_df = pd.DataFrame(checks)
    failures = report_df[report_df["Status"] == "FAIL"]
    is_valid = len(failures) == 0

    summary_dict = {
        "overall_validation_status": "VALIDATED" if is_valid else "FAILED",
        "total_checks": len(report_df),
        "passed_checks": int((report_df["Status"] == "PASS").sum()),
        "failed_checks": len(failures),
        "info_warnings": int((report_df["Status"] == "INFO").sum())
    }

    return is_valid, report_df, summary_dict
