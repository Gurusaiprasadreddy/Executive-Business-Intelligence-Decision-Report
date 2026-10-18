"""Dashboard Utilities Module

Provides shared cached loaders, filtering logic, executive navy-and-white Plotly styling,
and UI helper components for the Streamlit BI application.
"""

from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st

from src.io_utils import get_project_root, load_json


# Executive Navy-and-White Theme Palette
NAVY_DARK = "#0F2942"
NAVY_PRIMARY = "#1E3A8A"
BLUE_ACCENT = "#2563EB"
CYAN_ACCENT = "#0EA5E9"
EMERALD_GREEN = "#10B981"
AMBER_WARNING = "#F59E0B"
CRIMSON_RED = "#EF4444"
SLATE_BG = "#F8FAFC"
BORDER_GRAY = "#E2E8F0"
TEXT_PRIMARY = "#0F172A"
TEXT_MUTED = "#64748B"


@st.cache_data(show_spinner=False)
def load_clean_data() -> pd.DataFrame:
    """Load cleaned sales dataset with robust type casting."""
    root = get_project_root()
    # Try candidate clean dataset first, then Dataset/clean_dataset.csv
    candidate_path = root / "outputs" / "candidate_clean_dataset.csv"
    existing_path = root / "Dataset" / "clean_dataset.csv"

    path_to_load = candidate_path if candidate_path.exists() else existing_path
    if not path_to_load.exists():
        raise FileNotFoundError(f"Cleaned dataset not found at: {path_to_load}")

    df = pd.read_csv(path_to_load)
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df


@st.cache_data(show_spinner=False)
def load_authoritative_metrics() -> Dict[str, Any]:
    """Load the versioned metrics.json artifact."""
    root = get_project_root()
    metrics_path = root / "outputs" / "metrics.json"
    if not metrics_path.exists():
        return {}
    return load_json(metrics_path)


@st.cache_data(show_spinner=False)
def load_data_quality_report() -> pd.DataFrame:
    """Load the data quality report CSV."""
    root = get_project_root()
    dq_path = root / "outputs" / "data_quality_report.csv"
    if not dq_path.exists():
        return pd.DataFrame()
    return pd.read_csv(dq_path)


@st.cache_data(show_spinner=False)
def load_financial_reconciliation() -> pd.DataFrame:
    """Load the financial reconciliation waterfall CSV."""
    root = get_project_root()
    fr_path = root / "outputs" / "financial_reconciliation.csv"
    if not fr_path.exists():
        return pd.DataFrame()
    return pd.read_csv(fr_path)


def apply_filters(
    df: pd.DataFrame,
    date_range: Optional[Tuple[pd.Timestamp, pd.Timestamp]] = None,
    regions: Optional[List[str]] = None,
    categories: Optional[List[str]] = None,
    subcategories: Optional[List[str]] = None,
    channels: Optional[List[str]] = None,
    discount_bands: Optional[List[str]] = None
) -> pd.DataFrame:
    """Filter dataset deterministically across dimensional constraints."""
    filtered = df.copy()

    if date_range is not None and len(date_range) == 2:
        start_date, end_date = date_range
        if pd.notna(start_date) and pd.notna(end_date):
            filtered = filtered[
                (filtered["order_date"] >= pd.to_datetime(start_date)) &
                (filtered["order_date"] <= pd.to_datetime(end_date))
            ]

    if regions:
        filtered = filtered[filtered["region"].isin(regions)]

    if categories:
        filtered = filtered[filtered["category"].isin(categories)]

    if subcategories:
        filtered = filtered[filtered["sub_category"].isin(subcategories)]

    if channels:
        filtered = filtered[filtered["channel"].isin(channels)]

    if discount_bands:
        filtered = filtered[filtered["discount_band"].isin(discount_bands)]

    return filtered


def get_plotly_layout(
    title: Optional[str] = None,
    xaxis_title: Optional[str] = None,
    yaxis_title: Optional[str] = None,
    height: int = 400
) -> Dict[str, Any]:
    """Standardized executive navy-and-white Plotly layout."""
    layout = {
        "title": {
            "text": title or "",
            "font": {"size": 16, "color": NAVY_DARK, "family": "Inter, Segoe UI, sans-serif"}
        },
        "font": {"family": "Inter, Segoe UI, sans-serif", "color": TEXT_PRIMARY, "size": 12},
        "paper_bgcolor": "#FFFFFF",
        "plot_bgcolor": "#FFFFFF",
        "hovermode": "x unified",
        "xaxis": {
            "title": xaxis_title or "",
            "showgrid": True,
            "gridcolor": BORDER_GRAY,
            "zeroline": False,
            "linecolor": BORDER_GRAY,
            "ticks": "outside"
        },
        "yaxis": {
            "title": yaxis_title or "",
            "showgrid": True,
            "gridcolor": BORDER_GRAY,
            "zeroline": True,
            "zerolinecolor": BORDER_GRAY,
            "linecolor": BORDER_GRAY
        },
        "margin": {"l": 50, "r": 30, "t": 50, "b": 40},
        "height": height,
        "legend": {
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "font": {"size": 11}
        }
    }
    return layout


def render_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Render global sidebar filters and return the filtered DataFrame."""
    st.sidebar.markdown(
        """
        <div style="padding: 10px 0; border-bottom: 2px solid #E2E8F0; margin-bottom: 15px;">
            <h3 style="margin: 0; color: #0F2942; font-size: 1.15rem;">📊 Global Filters</h3>
            <span style="font-size: 0.8rem; color: #64748B;">Multi-Dimensional Slicing</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    min_date = df["order_date"].min().date()
    max_date = df["order_date"].max().date()

    # Reset button
    if st.sidebar.button("🔄 Reset All Filters", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    # Date Range Filter
    date_val = st.sidebar.date_input(
        "Order Date Horizon",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    date_range = None
    if isinstance(date_val, (tuple, list)) and len(date_val) == 2:
        date_range = (pd.to_datetime(date_val[0]), pd.to_datetime(date_val[1]))

    # Categorical Multi-Selects
    all_regions = sorted(df["region"].unique())
    selected_regions = st.sidebar.multiselect("Region", options=all_regions, default=[])

    all_channels = sorted(df["channel"].unique())
    selected_channels = st.sidebar.multiselect("Channel", options=all_channels, default=[])

    all_categories = sorted(df["category"].unique())
    selected_categories = st.sidebar.multiselect("Category", options=all_categories, default=[])

    # Filter subcategories based on category selection if applicable
    if selected_categories:
        avail_subcats = sorted(df[df["category"].isin(selected_categories)]["sub_category"].unique())
    else:
        avail_subcats = sorted(df["sub_category"].unique())
    selected_subcats = st.sidebar.multiselect("Sub-Category", options=avail_subcats, default=[])

    all_discount_bands = ["0%", "1-10%", "11-20%", "21-30%", ">30%"]
    selected_bands = st.sidebar.multiselect("Discount Band", options=all_discount_bands, default=[])

    # Apply filters
    filtered_df = apply_filters(
        df,
        date_range=date_range,
        regions=selected_regions if selected_regions else None,
        categories=selected_categories if selected_categories else None,
        subcategories=selected_subcats if selected_subcats else None,
        channels=selected_channels if selected_channels else None,
        discount_bands=selected_bands if selected_bands else None
    )

    # Sidebar Filter Summary
    st.sidebar.markdown(
        f"""
        <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 10px; margin-top: 20px;">
            <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase; font-weight: 600;">Active Filter Scope</div>
            <div style="font-size: 1.1rem; color: #0F2942; font-weight: 700; margin: 4px 0;">{len(filtered_df):,} orders</div>
            <div style="font-size: 0.8rem; color: #64748B;">({len(filtered_df) / len(df) * 100:.1f}% of total population)</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Simulated Data Disclosure
    st.sidebar.markdown(
        """
        <div style="background-color: #FEF3C7; border: 1px solid #F59E0B; border-radius: 6px; padding: 10px; margin-top: 15px; font-size: 0.75rem; color: #92400E;">
            ⚠️ <strong>Data Disclosure:</strong> This project simulates 3 years of omnichannel retail transactions (2023–2025). All metrics reflect validated data engineering pipeline results.
        </div>
        """,
        unsafe_allow_html=True
    )

    return filtered_df


def format_currency(val: float) -> str:
    """Format numeric values as currency strings ($1,234.56 or $1.2M)."""
    if pd.isna(val) or val is None:
        return "$0.00"
    if abs(val) >= 1_000_000:
        return f"${val / 1_000_000:.2f}M"
    if abs(val) >= 1_000:
        return f"${val:,.2f}"
    return f"${val:.2f}"


def format_pct(val: float) -> str:
    """Format numeric values as percentages (e.g. 15.4%)."""
    if pd.isna(val) or val is None:
        return "0.0%"
    return f"{val:.1f}%"


def render_metric_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    delta_color: str = "normal",
    subtext: Optional[str] = None
):
    """Render a clean, high-contrast metric card with executive typography."""
    delta_html = ""
    if delta:
        color = "#10B981" if delta_color == "positive" else ("#EF4444" if delta_color == "negative" else "#64748B")
        delta_html = f"<div style='font-size: 0.85rem; color: {color}; font-weight: 600; margin-top: 4px;'>{delta}</div>"

    subtext_html = f"<div style='font-size: 0.75rem; color: #64748B; margin-top: 2px;'>{subtext}</div>" if subtext else ""

    st.markdown(
        f"""
        <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 12px;">
            <div style="font-size: 0.8rem; color: #64748B; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em;">{label}</div>
            <div style="font-size: 1.75rem; color: #0F2942; font-weight: 700; margin: 4px 0 0 0; line-height: 1.2;">{value}</div>
            {delta_html}
            {subtext_html}
        </div>
        """,
        unsafe_allow_html=True
    )
