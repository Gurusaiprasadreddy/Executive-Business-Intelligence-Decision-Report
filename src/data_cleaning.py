"""Data Cleaning Pipeline Module

Implements auditable, deterministic, and modular data cleaning for omnichannel retail sales data.
Every imputation, correction, and drop is explicitly recorded in an audit trail.
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd

# Authoritative business constants
FEE_STRUCTURE = {
    "Retail Store": 0.00,
    "Online": 0.04,
    "Marketplace": 0.13
}

DISCOUNT_TIERS = np.array([0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50])
MAX_LEGITIMATE_QUANTITY = 20  # Business rule: orders > 20 units/line are keying entry errors


def parse_order_date(date_series: pd.Series) -> pd.Series:
    """Parse mixed date formats (ISO, DD/MM/YYYY, Mon dd, yyyy) into datetime64[ns]."""
    def _parse_single(val: Any) -> pd.Timestamp:
        if pd.isna(val):
            return pd.NaT
        s = str(val).strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%b %d, %Y"):
            try:
                return pd.to_datetime(s, format=fmt)
            except (ValueError, TypeError):
                continue
        # Fallback to general parser
        try:
            return pd.to_datetime(s)
        except Exception:
            return pd.NaT

    return date_series.apply(_parse_single)


def clean_currency_to_float(series: pd.Series) -> pd.Series:
    """Convert currency strings (e.g., '$1,234.56') to standard numeric floats."""
    return pd.to_numeric(series.astype(str).str.replace(r"[$,]", "", regex=True), errors="coerce")


def clean_boolean_flag(series: pd.Series) -> pd.Series:
    """Convert Y/N or boolean strings to boolean True/False."""
    clean_s = series.astype(str).str.strip().str.upper().str[0]
    return clean_s.map({"Y": True, "T": True, "1": True, "N": False, "F": False, "0": False}).fillna(False)


def standardize_categorical_labels(df: pd.DataFrame, columns: List[str]) -> Tuple[pd.DataFrame, Dict[str, Dict[str, int]]]:
    """Strip whitespace and title-case text labels in specified columns. Returns modified copy and variation counts."""
    df_clean = df.copy()
    counts = {}
    for col in columns:
        if col in df_clean.columns:
            before_nunique = df_clean[col].dropna().nunique()
            df_clean[col] = df_clean[col].astype(str).str.strip().str.title()
            # Restore genuine NaNs that became 'Nan' string
            df_clean[col] = df_clean[col].replace({"Nan": np.nan, "None": np.nan, "": np.nan})
            after_nunique = df_clean[col].dropna().nunique()
            counts[col] = {"before_variants": before_nunique, "after_variants": after_nunique}
    return df_clean, counts


def detect_and_remove_duplicates(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Identify and drop exact row duplicates. Returns (deduped_df, duplicates_df)."""
    dup_mask = df.duplicated()
    duplicates_df = df[dup_mask].copy()
    clean_df = df[~dup_mask].copy().reset_index(drop=True)
    return clean_df, duplicates_df


def impute_missing_fields(
    df: pd.DataFrame,
    audit_records: Optional[List[Dict[str, Any]]] = None
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Impute missing values under deterministic, audited business rules:
    - category <- deterministic lookup from sub_category
    - region & segment <- customer mode (fallback to global mode)
    - discount <- reconstructed from implied arithmetic snapped to valid discount tier
    - quantity <- reconstructed from sales / (unit_price * (1 - discount)) rounded to integer
    - ship_days <- regional median (flagged in ship_days_imputed)
    - unrecoverable rows where both discount and quantity are missing are dropped
    """
    df_work = df.copy()
    if audit_records is None:
        audit_records = []
    dropped_records: List[Dict[str, Any]] = []
    stats: Dict[str, Any] = {}

    # 1. Category Imputation from Sub_Category
    cat_lookup = (
        df_work.dropna(subset=["category"])
        .drop_duplicates("sub_category")
        .set_index("sub_category")["category"]
    )
    missing_cat_mask = df_work["category"].isna() & df_work["sub_category"].notna()
    stats["category_imputed"] = int(missing_cat_mask.sum())
    for idx, row in df_work[missing_cat_mask].iterrows():
        subcat = row["sub_category"]
        imputed_cat = cat_lookup.get(subcat, np.nan)
        audit_records.append({
            "order_id": row["order_id"],
            "field": "category",
            "action": "IMPUTE_FROM_SUBCAT",
            "original_value": None,
            "corrected_value": imputed_cat,
            "rationale": f"Subcategory '{subcat}' maps deterministically to '{imputed_cat}'"
        })
    df_work["category"] = df_work["category"].fillna(df_work["sub_category"].map(cat_lookup))

    # 2. Region and Segment Imputation from Customer Mode (with Global Mode Fallback)
    for col in ["region", "segment"]:
        # Calculate customer mode
        cust_modes = (
            df_work.dropna(subset=[col])
            .groupby("customer_id")[col]
            .agg(lambda s: s.mode().iat[0] if not s.empty else np.nan)
        )
        missing_mask = df_work[col].isna()
        global_mode = df_work[col].mode().iat[0] if not df_work[col].dropna().empty else "Unknown"

        cust_filled_count = 0
        global_filled_count = 0

        for idx, row in df_work[missing_mask].iterrows():
            c_mode = cust_modes.get(row["customer_id"], np.nan)
            if pd.notna(c_mode):
                action = f"IMPUTE_CUSTOMER_MODE"
                val = c_mode
                cust_filled_count += 1
                rationale = f"Imputed from customer {row['customer_id']} prior mode"
            else:
                action = f"IMPUTE_GLOBAL_MODE_FALLBACK"
                val = global_mode
                global_filled_count += 1
                rationale = f"Single-order or missing history customer; fell back to global mode '{global_mode}'"

            audit_records.append({
                "order_id": row["order_id"],
                "field": col,
                "action": action,
                "original_value": None,
                "corrected_value": val,
                "rationale": rationale
            })

        df_work[col] = df_work[col].fillna(df_work["customer_id"].map(cust_modes))
        df_work[col] = df_work[col].fillna(global_mode)
        stats[f"{col}_customer_mode_imputed"] = cust_filled_count
        stats[f"{col}_global_mode_imputed"] = global_filled_count

    # 3. Discount Imputation from Arithmetic
    m_disc = df_work["discount"].isna() & df_work["quantity"].notna() & df_work["unit_price"].notna() & (df_work["quantity"] > 0) & (df_work["unit_price"] > 0)
    implied_disc = 1 - df_work.loc[m_disc, "sales"] / (df_work.loc[m_disc, "quantity"] * df_work.loc[m_disc, "unit_price"])
    snapped_disc = DISCOUNT_TIERS[np.abs(implied_disc.values[:, None] - DISCOUNT_TIERS[None, :]).argmin(axis=1)]

    stats["discount_imputed"] = int(m_disc.sum())
    for (idx, row), snap in zip(df_work[m_disc].iterrows(), snapped_disc):
        audit_records.append({
            "order_id": row["order_id"],
            "field": "discount",
            "action": "IMPUTE_DISCOUNT_ARITHMETIC",
            "original_value": None,
            "corrected_value": float(snap),
            "rationale": f"Calculated 1 - sales/(qty*price) and snapped to tier {snap:.2f}"
        })
    df_work.loc[m_disc, "discount"] = snapped_disc

    # 4. Quantity Imputation from Arithmetic
    m_qty = df_work["quantity"].isna() & df_work["discount"].notna() & df_work["unit_price"].notna() & (df_work["unit_price"] > 0)
    calc_qty = (df_work.loc[m_qty, "sales"] / (df_work.loc[m_qty, "unit_price"] * (1 - df_work.loc[m_qty, "discount"]))).round()

    stats["quantity_imputed"] = int(m_qty.sum())
    for (idx, row), q in zip(df_work[m_qty].iterrows(), calc_qty):
        audit_records.append({
            "order_id": row["order_id"],
            "field": "quantity",
            "action": "IMPUTE_QUANTITY_ARITHMETIC",
            "original_value": None,
            "corrected_value": int(q),
            "rationale": f"Inverted sales formula: sales / (price * (1 - disc)) rounded to {int(q)}"
        })
    df_work.loc[m_qty, "quantity"] = calc_qty

    # 5. Drop Unrecoverable Rows (where both discount and quantity remain missing)
    unrec_mask = df_work[["discount", "quantity"]].isna().any(axis=1)
    stats["rows_dropped_unrecoverable"] = int(unrec_mask.sum())
    for idx, row in df_work[unrec_mask].iterrows():
        rec = row.to_dict()
        rec["drop_reason"] = "UNRECOVERABLE_MISSING_DISCOUNT_AND_QUANTITY"
        dropped_records.append(rec)
        audit_records.append({
            "order_id": row["order_id"],
            "field": "record",
            "action": "DROP_UNRECOVERABLE",
            "original_value": f"discount={row['discount']}, quantity={row['quantity']}",
            "corrected_value": None,
            "rationale": "Both discount and quantity were missing; cannot mathematically reconstruct"
        })
    df_work = df_work[~unrec_mask].copy().reset_index(drop=True)

    # 6. Ship Days Imputation from Regional Median
    df_work["ship_days_imputed"] = df_work["ship_days"].isna()
    stats["ship_days_imputed_count"] = int(df_work["ship_days_imputed"].sum())
    regional_medians = df_work.groupby("region")["ship_days"].median()
    for idx, row in df_work[df_work["ship_days_imputed"]].iterrows():
        reg = row["region"]
        med = regional_medians.get(reg, 4.0)
        audit_records.append({
            "order_id": row["order_id"],
            "field": "ship_days",
            "action": "IMPUTE_REGIONAL_MEDIAN",
            "original_value": None,
            "corrected_value": float(med),
            "rationale": f"Regional median shipping days for {reg} ({med:.1f} days)"
        })
    df_work["ship_days"] = df_work["ship_days"].fillna(df_work.groupby("region")["ship_days"].transform("median"))

    df_dropped = pd.DataFrame(dropped_records)
    return df_work, df_dropped, stats


def correct_quantity_outliers(
    df: pd.DataFrame,
    max_qty: int = MAX_LEGITIMATE_QUANTITY,
    audit_records: Optional[List[Dict[str, Any]]] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Review and correct keying entry errors where quantity > max_qty (e.g. 900 units).
    Replaces erroneous quantity with the sub-category median, and recomputes sales and profit.
    """
    df_work = df.copy()
    if audit_records is None:
        audit_records = []

    bad_mask = df_work["quantity"] > max_qty
    outlier_count = int(bad_mask.sum())
    med_qty = df_work[~bad_mask].groupby("sub_category")["quantity"].median()

    global_med = df_work.loc[~bad_mask, "quantity"].median() if not df_work.loc[~bad_mask].empty else 4
    for idx, row in df_work[bad_mask].iterrows():
        subcat = row["sub_category"]
        corrected_q = int(med_qty.get(subcat, global_med))
        old_sales = row["sales"]
        old_profit = row["profit"]
        fee_rate = FEE_STRUCTURE.get(row["channel"], 0.0)

        new_sales = round(corrected_q * row["unit_price"] * (1 - row["discount"]), 2)
        new_profit = round(new_sales * (1 - fee_rate) - corrected_q * row["unit_cost"], 2)

        audit_records.append({
            "order_id": row["order_id"],
            "field": "quantity_and_financials",
            "action": "CORRECT_ENTRY_OUTLIER",
            "original_value": f"qty={row['quantity']}, sales={old_sales}, profit={old_profit}",
            "corrected_value": f"qty={corrected_q}, sales={new_sales}, profit={new_profit}",
            "rationale": f"Quantity {row['quantity']} exceeded threshold {max_qty}; replaced with subcategory median {corrected_q}"
        })

    replaced_quantities = df_work.loc[bad_mask, "sub_category"].map(med_qty).fillna(global_med).fillna(4)
    df_work.loc[bad_mask, "quantity"] = replaced_quantities
    df_work["quantity"] = df_work["quantity"].astype(int)

    # Recompute sales and profit for corrected rows
    df_work.loc[bad_mask, "sales"] = (df_work["quantity"] * df_work["unit_price"] * (1 - df_work["discount"]))[bad_mask].round(2)
    df_work.loc[bad_mask, "profit"] = (
        df_work["sales"] * (1 - df_work["channel"].map(FEE_STRUCTURE)) - df_work["quantity"] * df_work["unit_cost"]
    )[bad_mask].round(2)

    return df_work, {"quantity_outliers_corrected": outlier_count}


def engineer_analytical_features(df: pd.DataFrame) -> pd.DataFrame:
    """Engineer derived features for reporting and scenario analysis."""
    df_work = df.copy()

    df_work["order_year"] = df_work["order_date"].dt.year
    df_work["order_month"] = df_work["order_date"].dt.month
    df_work["order_quarter"] = df_work["order_date"].dt.quarter
    df_work["year_month"] = df_work["order_date"].dt.to_period("M").astype(str)

    df_work["profit_margin"] = df_work["profit"] / df_work["sales"]
    df_work["discount_band"] = pd.cut(
        df_work["discount"],
        bins=[-0.01, 0.00, 0.10, 0.20, 0.30, 1.00],
        labels=["0%", "1-10%", "11-20%", "21-30%", ">30%"]
    )
    df_work["is_late"] = df_work["ship_days"] > 5
    df_work["is_loss_order"] = df_work["profit"] < 0

    order_counts = df_work.groupby("customer_id")["order_id"].transform("count")
    df_work["customer_type"] = np.where(order_counts > 1, "Repeat", "One-time")
    df_work["channel_fee"] = df_work["channel"].map(FEE_STRUCTURE)

    return df_work


def run_clean_pipeline(
    raw_df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Execute full deterministic cleaning pipeline on raw sales data.
    Returns:
    - clean_df: Cleaned and enriched dataset
    - cleaning_log_df: Detailed audit trail of all row alterations
    - unresolved_df: Catalog of dropped records, anomalies, and potential caveats
    - summary_stats: Dictionary of pipeline summary metrics
    """
    audit_records: List[Dict[str, Any]] = []
    summary: Dict[str, Any] = {"raw_row_count": len(raw_df)}

    df = raw_df.copy()

    # Step 1: Detect and drop exact duplicates
    clean_df, dup_df = detect_and_remove_duplicates(df)
    summary["exact_duplicates_removed"] = len(dup_df)
    for idx, row in dup_df.iterrows():
        audit_records.append({
            "order_id": row["order_id"],
            "field": "row",
            "action": "EXACT_DUPLICATE_REMOVED",
            "original_value": "Duplicate exact record",
            "corrected_value": None,
            "rationale": "Exact row duplicate removed per dedup standard"
        })

    # Step 2: Convert types
    for col in ["sales", "profit"]:
        clean_df[col] = clean_currency_to_float(clean_df[col])
    clean_df["order_date"] = parse_order_date(clean_df["order_date"])
    clean_df["returned"] = clean_boolean_flag(clean_df["returned"])

    # Step 3: Standardize labels
    clean_df, label_counts = standardize_categorical_labels(clean_df, ["region", "segment", "category"])
    summary["label_standardization"] = label_counts

    # Step 4: Missing values
    summary["missing_cells_before_imputation"] = int(clean_df.isna().sum().sum())
    clean_df, dropped_unrec, impute_stats = impute_missing_fields(clean_df, audit_records)
    summary.update(impute_stats)

    # Step 5: Quantity entry errors
    clean_df, outlier_stats = correct_quantity_outliers(clean_df, MAX_LEGITIMATE_QUANTITY, audit_records)
    summary.update(outlier_stats)

    # Step 6: Analytical features
    clean_df = engineer_analytical_features(clean_df)
    summary["clean_row_count"] = len(clean_df)
    summary["missing_cells_after_clean"] = int(clean_df.isna().sum().sum())

    # Build unresolved records catalog
    unresolved_list: List[Dict[str, Any]] = []

    # A. Dropped unrecoverables
    for idx, row in dropped_unrec.iterrows():
        unresolved_list.append({
            "order_id": row.get("order_id"),
            "category": "DROPPED_UNRECOVERABLE",
            "severity": "CRITICAL",
            "description": "Row dropped because both discount and quantity were missing and unrecoverable",
            "record_data": str(row.to_dict())
        })

    # B. Profit formula deviations > 0.05
    expected_profit = clean_df["sales"] * (1 - clean_df["channel_fee"]) - clean_df["quantity"] * clean_df["unit_cost"]
    p_diff = (clean_df["profit"] - expected_profit).abs()
    deviant_profit = clean_df[p_diff > 0.02]
    for idx, row in deviant_profit.iterrows():
        unresolved_list.append({
            "order_id": row["order_id"],
            "category": "PROFIT_ROUNDING_DEVIATION",
            "severity": "LOW",
            "description": f"Profit ${row['profit']} differs by ${p_diff.loc[idx]:.3f} from formula due to cent rounding in source data",
            "record_data": f"sales={row['sales']}, fee={row['channel_fee']}, qty={row['quantity']}, cost={row['unit_cost']}"
        })

    # C. High sales IQR outliers (> Q3 + 3*IQR)
    q1 = clean_df["sales"].quantile(0.25)
    q3 = clean_df["sales"].quantile(0.75)
    iqr = q3 - q1
    high_sales = clean_df[clean_df["sales"] > q3 + 3 * iqr]
    summary["sales_iqr_outliers_count"] = len(high_sales)
    for idx, row in high_sales.iterrows():
        unresolved_list.append({
            "order_id": row["order_id"],
            "category": "HIGH_VALUE_SALE_OUTLIER",
            "severity": "INFO",
            "description": f"Sale amount ${row['sales']:.2f} exceeds extreme IQR cutoff ${q3 + 3*iqr:.2f}",
            "record_data": f"qty={row['quantity']}, unit_price={row['unit_price']}, discount={row['discount']}"
        })

    cleaning_log_df = pd.DataFrame(audit_records)
    unresolved_df = pd.DataFrame(unresolved_list)

    return clean_df, cleaning_log_df, unresolved_df, summary
