# Interactive Streamlit BI Dashboard User Guide

**Application Entry Point:** `app.py`  
**Page Directory:** `pages/` (9 Specialized Analytical Views)  
**Utility Support:** `src/dashboard_utils.py`  
**Execution Command:** `streamlit run app.py`

---

## 1. Executive BI Overview

The interactive Business Intelligence suite is built using **Streamlit (v1.38.0)** and **Plotly (v6.9.0)**, delivering an executive dark/navy-and-white interface tailored for business leaders, financial planners, and operational managers.

### Key Capabilities
- **Authoritative Pre-computed Metrics Integration:** Connects directly to audited Stage 2 KPIs in `outputs/metrics.json` and clean datasets to prevent browser-side calculation drift.
- **Dynamic Cross-Filtering:** Filters across Date Range, Channel, Region, Product Category, and Discount Band with automatic caching (`@st.cache_data`).
- **Interactive Scenario Simulation:** Allows C-suite stakeholders to dynamically toggle between Conservative, Base, and Optimistic ROI projections and modify operational parameters in real time.

---

## 2. Dashboard Architecture & Page Breakdown

```
app.py (Landing & Executive Performance Summary)
  │
  ├── 1_Executive_Overview.py       ──► C-Suite Performance Cockpit & KPI Scorecard
  ├── 2_Revenue_Profitability.py    ──► Top-line Growth vs. Margin Erosion Breakdown
  ├── 3_Discount_Analysis.py        ──► Margin Bleed Curves & Discount Band Auditing
  ├── 4_Channel_Regional_Analysis.py──► Marketplace Fee Drag & Regional Logistics
  ├── 5_Customer_Analytics.py       ──► Cohort Retention & Pareto Concentration
  ├── 6_Delivery_Returns.py         ──► Fulfillment Delays & Return Rate Diagnostics
  ├── 7_Statistical_Insights.py     ──► Hypothesis Testing (Welch's t-test H1/H2/H3)
  ├── 8_Strategic_Decisions.py      ──► 36-Month Dynamic ROI Scenario Engine
  └── 9_Data_Quality.py             ──► Data Cleaning Reconciliation & Audit Trail
```

---

## 3. Page-by-Page Feature Matrix

### Page 1: Executive Overview (`pages/1_Executive_Overview.py`)
- **KPI Metric Ribbon:** Total Revenue ($3.37M), Total Contribution Profit ($458.1K), Authoritative Weighted Margin (13.58%), AOV ($281.23), Unique Orders (11,996).
- **Executive Diagnostic:** High-level executive narrative outlining the 3-year margin drop (-351 bps) despite +56.2% revenue growth.
- **Multi-Year Macro Chart:** Side-by-side annual comparison of Revenue, Profit, and Profit Margin.

### Page 2: Revenue & Profitability (`pages/2_Revenue_Profitability.py`)
- **Monthly Time Series:** Revenue vs. Profit run-rate from 2023 through 2025 showing seasonal Q4 surges and accelerating margin erosion.
- **Category Profitability Matrix:** Revenue and margin breakdown across Technology, Furniture, and Office Supplies.
- **Loss-Making Order Deep Dive:** Distribution of the 1,579 unprofitable orders (-$129,119.31 loss) across product lines.

### Page 3: Discount Analysis (`pages/3_Discount_Analysis.py`)
- **Discount Band Performance:** Comparative table across 5 tiers (`0%`, `1-10%`, `11-20%`, `21-30%`, `>30%`).
- **The "Tipping Point" Chart:** Visualizes how contribution margin turns negative once discounts exceed 20%, plummeting to -22.55% on discounts $>30\%$.
- **Loss Concentration:** Demonstrates that 54.71% of orders in the $>30\%$ discount band generate net losses.

### Page 4: Channel & Regional Analysis (`pages/4_Channel_Regional_Analysis.py`)
- **Channel P&L Comparison:** Audits Online (15.00% margin), Retail Store (21.22% margin), and Marketplace (-2.55% negative margin).
- **Marketplace Commission Breakdown:** Demonstrates the impact of the 13.0% commission fee ($88,929.17 in total fees) which turns positive operating margin into a net loss.
- **Regional Logistics Map:** Highlights Central Region's 58.41% late delivery rate vs. West Region's 11.86%.

### Page 5: Customer Analytics (`pages/5_Customer_Analytics.py`)
- **Retention Cohort Waterfall:** Year-over-year repeat rates (54.39% from 2023 to 2024, 49.65% from 2024 to 2025).
- **Pareto Revenue Concentration:** Visualizes that the top 20% of customers generate 66.08% of total revenue.
- **Repeat vs. One-Time Comparison:** Proves repeat buyers account for 94.95% of orders.

### Page 6: Delivery & Returns (`pages/6_Delivery_Returns.py`)
- **Fulfillment Duration Distribution:** Shipping days histogram showing SLA compliance vs. violations (>5 days).
- **Late Delivery Return Penalty:** Comparative return rate analysis (14.91% for delayed orders vs. 4.78% for on-time orders).
- **Estimated Financial Drag:** Quantifies reverse logistics costs and inventory restocking friction.

### Page 7: Statistical Insights (`pages/7_Statistical_Insights.py`)
- **Formal Hypothesis Testing Dashboard:** Displays Welch's two-sample t-test statistical outputs for H1 (Discount Bleed), H2 (Marketplace Drag), and H3 (Late Shipping Returns).
- **Distribution Histograms:** Overlay of margin distributions between high-discount and low-discount orders.
- **Confidence Intervals:** 95% and 99% confidence interval displays confirming statistical significance ($p < 0.0001$).

### Page 8: Strategic Decisions & ROI Engine (`pages/8_Strategic_Decisions.py`)
- **Scenario Toggle:** Instant switching between Conservative, Base Case, and Optimistic models.
- **36-Month Cumulative Cash Flow Chart:** Visualizes portfolio breakeven at Month 8 and final net benefit ($200,722.56).
- **Standalone Recommendation Diagnostics:** Clearly flags that Recommendation 3 operates at a -$18,794.58 deficit.
- **Dynamic Sensitivity Sliders:** Real-time user adjustments for fee renegotiation, discount retention, and implementation delays.

### Page 9: Data Quality & Governance (`pages/9_Data_Quality.py`)
- **Reconciliation Audit Waterfall:** Step-by-step audit trail reconciling raw data (12,400 rows) to clean data (11,996 rows).
- **Categorical Mapping Logs:** Interactive inspection of raw-to-clean label standardization rules.
- **Unresolved Exceptions Register:** Full disclosure of 1,018 documented low-severity edge cases.

---

## 4. How to Launch and Use the Dashboard

### Prerequisites
Ensure your virtual environment is active and dependencies are installed:
```bash
pip install -r requirements.txt
```

### Launch Command
From the project root directory, run:
```bash
streamlit run app.py
```

The application will launch automatically in your default browser at `http://localhost:8501`.

### Navigation Tips
1. Use the left-hand sidebar to navigate between analytical modules.
2. In **Page 8 (Strategic Decisions)**, explore interactive slider sensitivity adjustments to model bespoke corporate scenarios.
3. Use the filter panel in analytical pages to isolate specific annual periods or geographic territories.
