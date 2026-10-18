"""KPI Engine Module

Implements shared, authoritative business metric calculations for omnichannel retail analytics.
Every KPI has a mathematically explicit and consistent definition, with safe zero-denominator handling.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero or invalid."""
    if denominator is None or pd.isna(denominator) or denominator == 0:
        return default
    return float(numerator / denominator)


def calculate_weighted_profit_margin(profit_sum: float, sales_sum: float) -> float:
    """
    Authoritative weighted profit margin formula:
    (Total Profit / Total Sales) * 100
    """
    return safe_divide(profit_sum, sales_sum, default=0.0) * 100.0


def calculate_annual_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate annual financial and operational KPIs for each year from 2023 to 2025 plus Total.
    Returns DataFrame with columns:
    - Year
    - Revenue
    - Profit
    - Weighted_Profit_Margin_%
    - Record_Count
    - Unique_Orders
    - Unique_Customers
    - AOV
    - Return_Rate_%
    - Late_Rate_%
    """
    df_work = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df_work["order_date"]):
        df_work["order_date"] = pd.to_datetime(df_work["order_date"])

    years = sorted(df_work["order_date"].dt.year.unique())
    records: List[Dict[str, Any]] = []

    for yr in years:
        grp = df_work[df_work["order_date"].dt.year == yr]
        rev = grp["sales"].sum()
        prof = grp["profit"].sum()
        n_rec = len(grp)
        n_ord = grp["order_id"].nunique()
        n_cust = grp["customer_id"].nunique()
        margin = calculate_weighted_profit_margin(prof, rev)
        aov = safe_divide(rev, n_ord)
        ret_rate = safe_divide(grp["returned"].sum(), n_rec) * 100.0
        late_rate = safe_divide(grp["is_late"].sum(), n_rec) * 100.0 if "is_late" in grp.columns else 0.0

        records.append({
            "Year": int(yr),
            "Revenue": round(float(rev), 2),
            "Profit": round(float(prof), 2),
            "Weighted_Profit_Margin_%": round(float(margin), 2),
            "Record_Count": int(n_rec),
            "Unique_Orders": int(n_ord),
            "Unique_Customers": int(n_cust),
            "AOV": round(float(aov), 2),
            "Return_Rate_%": round(float(ret_rate), 2),
            "Late_Rate_%": round(float(late_rate), 2)
        })

    # Overall summary row
    tot_rev = df_work["sales"].sum()
    tot_prof = df_work["profit"].sum()
    tot_rec = len(df_work)
    tot_ord = df_work["order_id"].nunique()
    tot_cust = df_work["customer_id"].nunique()
    tot_margin = calculate_weighted_profit_margin(tot_prof, tot_rev)
    tot_aov = safe_divide(tot_rev, tot_ord)
    tot_ret = safe_divide(df_work["returned"].sum(), tot_rec) * 100.0
    tot_late = safe_divide(df_work["is_late"].sum(), tot_rec) * 100.0 if "is_late" in df_work.columns else 0.0

    records.append({
        "Year": "Total / Overall",
        "Revenue": round(float(tot_rev), 2),
        "Profit": round(float(tot_prof), 2),
        "Weighted_Profit_Margin_%": round(float(tot_margin), 2),
        "Record_Count": int(tot_rec),
        "Unique_Orders": int(tot_ord),
        "Unique_Customers": int(tot_cust),
        "AOV": round(float(tot_aov), 2),
        "Return_Rate_%": round(float(tot_ret), 2),
        "Late_Rate_%": round(float(tot_late), 2)
    })

    return pd.DataFrame(records)


def calculate_monthly_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate monthly revenue, profit, weighted margin, and order volume."""
    df_work = df.copy()
    if "year_month" not in df_work.columns:
        if not pd.api.types.is_datetime64_any_dtype(df_work["order_date"]):
            df_work["order_date"] = pd.to_datetime(df_work["order_date"])
        df_work["year_month"] = df_work["order_date"].dt.to_period("M").astype(str)

    monthly = (
        df_work.groupby("year_month")
        .agg(
            revenue=("sales", "sum"),
            profit=("profit", "sum"),
            order_count=("order_id", "count"),
            unique_customers=("customer_id", "nunique")
        )
        .reset_index()
    )
    monthly["weighted_margin_%"] = (monthly["profit"] / monthly["revenue"] * 100.0).round(2)
    monthly["revenue"] = monthly["revenue"].round(2)
    monthly["profit"] = monthly["profit"].round(2)
    return monthly


def calculate_channel_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate channel-level performance, mix percentage, and profitability."""
    tot_rev = df["sales"].sum()
    chn = (
        df.groupby("channel")
        .agg(
            orders=("order_id", "count"),
            revenue=("sales", "sum"),
            profit=("profit", "sum")
        )
        .reset_index()
    )
    chn["revenue_share_%"] = (chn["revenue"] / tot_rev * 100.0).round(2)
    chn["weighted_margin_%"] = (chn["profit"] / chn["revenue"] * 100.0).round(2)
    chn["revenue"] = chn["revenue"].round(2)
    chn["profit"] = chn["profit"].round(2)
    return chn


def calculate_discount_band_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate volume, revenue, profit, and loss rate across discount tiers."""
    df_work = df.copy()
    if "discount_band" not in df_work.columns:
        df_work["discount_band"] = pd.cut(
            df_work["discount"],
            bins=[-0.01, 0.00, 0.10, 0.20, 0.30, 1.00],
            labels=["0%", "1-10%", "11-20%", "21-30%", ">30%"]
        )

    disc = (
        df_work.groupby("discount_band", observed=False)
        .agg(
            orders=("order_id", "count"),
            revenue=("sales", "sum"),
            profit=("profit", "sum"),
            loss_orders=("profit", lambda s: (s < 0).sum())
        )
        .reset_index()
    )
    disc["loss_order_share_%"] = (disc["loss_orders"] / disc["orders"] * 100.0).round(2)
    disc["weighted_margin_%"] = (disc["profit"] / disc["revenue"] * 100.0).round(2)
    disc["revenue"] = disc["revenue"].round(2)
    disc["profit"] = disc["profit"].round(2)
    return disc


def calculate_category_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate product category performance and aggregate margins."""
    cat = (
        df.groupby("category")
        .agg(
            orders=("order_id", "count"),
            revenue=("sales", "sum"),
            profit=("profit", "sum")
        )
        .reset_index()
    )
    cat["weighted_margin_%"] = (cat["profit"] / cat["revenue"] * 100.0).round(2)
    cat["revenue"] = cat["revenue"].round(2)
    cat["profit"] = cat["profit"].round(2)
    return cat


def calculate_regional_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate regional sales, profit, weighted margin, and delivery performance."""
    reg = (
        df.groupby("region")
        .agg(
            orders=("order_id", "count"),
            revenue=("sales", "sum"),
            profit=("profit", "sum"),
            late_orders=("is_late", "sum") if "is_late" in df.columns else ("ship_days", lambda s: (s > 5).sum())
        )
        .reset_index()
    )
    reg["weighted_margin_%"] = (reg["profit"] / reg["revenue"] * 100.0).round(2)
    reg["late_rate_%"] = (reg["late_orders"] / reg["orders"] * 100.0).round(2)
    reg["revenue"] = reg["revenue"].round(2)
    reg["profit"] = reg["profit"].round(2)
    return reg


def calculate_customer_cohort_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate customer retention cohorts and concentration statistics:
    - Retention 2023 -> 2024: |active in 23 AND 24| / |active in 23|
    - Retention 2024 -> 2025: |active in 24 AND 25| / |active in 24|
    - Pareto Concentration: Share of revenue generated by top 20% of customers
    - Repeat vs One-Time order count and AOV
    """
    df_work = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df_work["order_date"]):
        df_work["order_date"] = pd.to_datetime(df_work["order_date"])

    c23 = set(df_work[df_work["order_date"].dt.year == 2023]["customer_id"].unique())
    c24 = set(df_work[df_work["order_date"].dt.year == 2024]["customer_id"].unique())
    c25 = set(df_work[df_work["order_date"].dt.year == 2025]["customer_id"].unique())

    ret_23_24 = round(len(c23 & c24) / len(c23) * 100.0, 2) if c23 else 0.0
    ret_24_25 = round(len(c24 & c25) / len(c24) * 100.0, 2) if c24 else 0.0

    # Customer revenue concentration (Pareto)
    cust_sales = df_work.groupby("customer_id")["sales"].sum().sort_values(ascending=False)
    n_top20 = max(1, int(len(cust_sales) * 0.20))
    top20_rev_share = round(float(cust_sales.iloc[:n_top20].sum() / cust_sales.sum() * 100.0), 2)

    # Repeat vs One-time orders
    cust_orders = df_work.groupby("customer_id")["order_id"].count()
    repeat_cust_ids = set(cust_orders[cust_orders > 1].index)
    df_work["_ctype"] = np.where(df_work["customer_id"].isin(repeat_cust_ids), "Repeat", "One-time")

    repeat_orders_share = round(float((df_work["_ctype"] == "Repeat").mean() * 100.0), 2)
    aov_by_type = df_work.groupby("_ctype")["sales"].mean().round(2).to_dict()

    return {
        "retention_2023_to_2024_%": ret_23_24,
        "retention_2024_to_2025_%": ret_24_25,
        "top_20_percent_customer_revenue_share_%": top20_rev_share,
        "repeat_customer_order_share_%": repeat_orders_share,
        "aov_repeat_customer_$": aov_by_type.get("Repeat", 0.0),
        "aov_onetime_customer_$": aov_by_type.get("One-time", 0.0)
    }
