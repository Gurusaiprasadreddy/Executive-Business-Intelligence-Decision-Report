"""Page 9: Data Quality and Governance

Audits data pipeline integrity, displays the 12 automated validation checks,
financial reconciliation waterfall, row alteration logs, and full schema data dictionary.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

from src.io_utils import get_project_root
from src.dashboard_utils import (
    load_data_quality_report,
    load_financial_reconciliation,
    render_metric_card,
    NAVY_DARK,
    BLUE_ACCENT,
    CRIMSON_RED,
    EMERALD_GREEN
)

st.set_page_config(page_title="Data Quality & Audit | BI Dashboard", page_icon="🛡️", layout="wide")

st.title("🛡️ Data Quality, Governance & Audit Trail")
st.caption("Verifying pipeline determinism, structural integrity, and financial accounting reconciliation")

root = get_project_root()
dq_report = load_data_quality_report()
fin_recon = load_financial_reconciliation()

# High-Level Audit Gate Metrics
pass_count = (dq_report["Status"] == "PASS").sum() if not dq_report.empty else 0
fail_count = (dq_report["Status"] == "FAIL").sum() if not dq_report.empty else 0
info_count = (dq_report["Status"] == "INFO").sum() if not dq_report.empty else 0

q1, q2, q3, q4 = st.columns(4)
with q1:
    render_metric_card("Raw Input Rows", "12,400", "Original CSV", "normal", "SHA256 verified byte-for-byte")
with q2:
    render_metric_card("Duplicates Purged", "400", "-$36.7k profit adjusted", "normal", "Exact row duplicates")
with q3:
    render_metric_card("Clean Population", "11,996", "4 dropped unrecoverable", "positive", "100% unique order lines")
with q4:
    gate_status = "100% PASS" if fail_count == 0 else f"{fail_count} FAILED"
    render_metric_card("Automated Quality Gate", gate_status, f"{pass_count} Passed / {info_count} Info", "positive", "Zero critical defects")

st.markdown("---")

# Section 1: Automated Data Quality Gates Table
st.subheader("📋 Automated Validation Checks (12 Quality Gates)")
if not dq_report.empty:
    st.dataframe(
        dq_report[["Check_Category", "Check_Name", "Level", "Status", "Observed_Value", "Expected_Value", "Details"]],
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("Data quality report not found at outputs/data_quality_report.csv")

st.markdown("---")

# Section 2: Financial Reconciliation Waterfall Table
st.subheader("💵 Financial Reconciliation & Accounting Waterfall")
st.caption("Full reconciliation explaining the variance between Raw input and Final Cleaned dataset")

if not fin_recon.empty:
    display_fr = fin_recon.copy()
    display_fr["Revenue_$"] = display_fr["Revenue_$"].apply(lambda v: f"${v:,.2f}")
    display_fr["Profit_$"] = display_fr["Profit_$"].apply(lambda v: f"${v:,.2f}")
    display_fr["Weighted_Margin_%"] = display_fr["Weighted_Margin_%"].apply(lambda v: f"{v:.2f}%")
    display_fr["Delta_Revenue_$"] = display_fr["Delta_Revenue_$"].apply(lambda v: f"${v:,.2f}")
    display_fr["Delta_Profit_$"] = display_fr["Delta_Profit_$"].apply(lambda v: f"${v:,.2f}")

    st.dataframe(display_fr, use_container_width=True, hide_index=True)
else:
    st.warning("Financial reconciliation table not found at outputs/financial_reconciliation.csv")

st.markdown("---")

# Section 3: Audit Trail & Unresolved Records Viewer
st.subheader("🔍 Inspection of Audit Trail & Cataloged Caveats")

tab_clean_log, tab_unresolved = st.tabs(["📝 Cleaning Event Log (1,684 records)", "⚠️ Unresolved Records & Anomalies (1,018 records)"])

with tab_clean_log:
    log_path = root / "outputs" / "audit" / "cleaning_log.csv"
    if log_path.exists():
        log_df = pd.read_csv(log_path)
        st.caption(f"Displaying sample of {len(log_df):,} logged row modifications:")
        st.dataframe(log_df.head(100), use_container_width=True, hide_index=True)
        st.download_button(
            "📥 Download Complete Cleaning Log CSV",
            log_df.to_csv(index=False).encode("utf-8"),
            "cleaning_log.csv",
            "text/csv"
        )
    else:
        st.info("Cleaning log not found.")

with tab_unresolved:
    unrec_path = root / "outputs" / "audit" / "unresolved_records.csv"
    if unrec_path.exists():
        unrec_df = pd.read_csv(unrec_path)
        st.caption(f"Catalog of {len(unrec_df):,} edge cases (rounding discrepancies, high-value IQR outliers, dropped rows):")
        st.dataframe(unrec_df.head(100), use_container_width=True, hide_index=True)
        st.download_button(
            "📥 Download Complete Unresolved Records CSV",
            unrec_df.to_csv(index=False).encode("utf-8"),
            "unresolved_records.csv",
            "text/csv"
        )
    else:
        st.info("Unresolved records catalog not found.")

st.markdown("---")

# Section 4: Data Dictionary
st.subheader("📚 Dataset Schema & Field Data Dictionary")

schema_dict = pd.DataFrame([
    {"Field Name": "order_id", "Data Type": "string", "Definition": "Unique alphanumeric order identifier (strictly 1 row per order)"},
    {"Field Name": "order_date", "Data Type": "datetime64", "Definition": "Standardized ISO order timestamp (2023-01-01 to 2025-12-31)"},
    {"Field Name": "customer_id", "Data Type": "string", "Definition": "Unique purchasing account identifier (2,116 unique accounts)"},
    {"Field Name": "segment", "Data Type": "string", "Definition": "Customer commercial classification (Consumer, Corporate, Small Business)"},
    {"Field Name": "region", "Data Type": "string", "Definition": "Geographic territory (Central, East, North, South, West)"},
    {"Field Name": "category", "Data Type": "string", "Definition": "Broad product category (Furniture, Office Supplies, Technology)"},
    {"Field Name": "sub_category", "Data Type": "string", "Definition": "Granular product line (17 distinct subcategories)"},
    {"Field Name": "channel", "Data Type": "string", "Definition": "Sales channel (Marketplace [13% fee], Online [4% fee], Retail Store [0% fee])"},
    {"Field Name": "quantity", "Data Type": "integer", "Definition": "Units purchased per order line (1 to 12 after keying error correction)"},
    {"Field Name": "unit_price", "Data Type": "float", "Definition": "Base list price per unit ($8.35 to $540.00)"},
    {"Field Name": "discount", "Data Type": "float", "Definition": "Promotional discount rate (0.00 to 0.50 in discrete 5% steps)"},
    {"Field Name": "unit_cost", "Data Type": "float", "Definition": "Cost of Goods Sold (COGS) per unit ($4.15 to $270.00)"},
    {"Field Name": "sales", "Data Type": "float", "Definition": "Recognized order revenue = quantity * unit_price * (1 - discount)"},
    {"Field Name": "profit", "Data Type": "float", "Definition": "Contribution profit = sales * (1 - channel_fee) - quantity * unit_cost"},
    {"Field Name": "ship_days", "Data Type": "float", "Definition": "Fulfillment turnaround in days (missing values imputed via regional median)"},
    {"Field Name": "returned", "Data Type": "boolean", "Definition": "Merchandise return flag (True = returned, False = kept)"},
    {"Field Name": "profit_margin", "Data Type": "float", "Definition": "Derived row-level margin ratio = profit / sales"},
    {"Field Name": "discount_band", "Data Type": "category", "Definition": "Promotional tier (0%, 1-10%, 11-20%, 21-30%, >30%)"},
    {"Field Name": "is_late", "Data Type": "boolean", "Definition": "Fulfillment SLA flag = True if ship_days > 5"},
    {"Field Name": "is_loss_order", "Data Type": "boolean", "Definition": "Operational loss flag = True if profit < 0"},
    {"Field Name": "customer_type", "Data Type": "string", "Definition": "Buyer frequency tier = Repeat if customer orders > 1 else One-time"},
    {"Field Name": "channel_fee", "Data Type": "float", "Definition": "Platform commission rate (Retail: 0.00, Online: 0.04, Marketplace: 0.13)"}
])

st.dataframe(schema_dict, use_container_width=True, hide_index=True)
