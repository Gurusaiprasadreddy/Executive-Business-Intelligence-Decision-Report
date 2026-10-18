# Executive Decision Analytics BI & Capstone Portfolio

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Tests Passed](https://img.shields.io/badge/tests-75%20passed-brightgreen.svg)](tests/)
[![Data Quality](https://img.shields.io/badge/data%20quality-validated%20(11%2F12)-brightgreen.svg)](outputs/data_quality_report.csv)
[![Base 36M Net ROI](https://img.shields.io/badge/Base%2036M%20Net%20ROI-232.72%25-navy.svg)](outputs/roi_scenarios.csv)
[![Discounted NPV](https://img.shields.io/badge/10%25%20WACC%20NPV-%2B%24168%2C399.10-success.svg)](outputs/break_even_analysis.csv)

> **Executive Summary:** A comprehensive, audited Business Intelligence and Financial Analytics Capstone engineered to diagnose e-commerce margin erosion, establish robust data cleaning pipelines, model multi-year ROI scenarios, and deliver C-suite decision support via interactive dashboards and board-ready presentations.

---

## Table of Contents
1. [Project Title & Concise Overview](#1-project-title--concise-overview)
2. [Business Problem & Objectives](#2-business-problem--objectives)
3. [Key Findings & Executive Takeaways](#3-key-findings--executive-takeaways)
4. [Dataset Description & Simulated Data Disclosure](#4-dataset-description--simulated-data-disclosure)
5. [Technology Stack](#5-technology-stack)
6. [Repository Structure](#6-repository-structure)
7. [Analytical Methodology & Data-Cleaning Pipeline](#7-analytical-methodology--data-cleaning-pipeline)
8. [Data-Quality Validation & Financial Reconciliation](#8-data-quality-validation--financial-reconciliation)
9. [Interactive Dashboard Features & Execution](#9-interactive-dashboard-features--execution)
10. [How to Run the Pipeline & Test Suite](#10-how-to-run-the-pipeline--test-suite)
11. [ROI Methodology & Scenario Assumptions](#11-roi-methodology--scenario-assumptions)
12. [Three Actionable Strategic Recommendations](#12-three-actionable-strategic-recommendations)
13. [Final Deliverables & Executive Presentation Links](#13-final-deliverables--executive-presentation-links)
14. [Limitations, Uncertainty & Governance](#14-limitations-uncertainty--governance)
15. [Future Enhancements](#15-future-enhancements)
16. [Author & Project Purpose](#16-author--project-purpose)

---

## 1. Project Title & Concise Overview

**Title:** Enterprise Retail E-Commerce Profitability Diagnosis, Data Architecture & Financial Decision Modeling  
**Domain:** Business Intelligence, Data Engineering, Financial Analytics & Strategic Management  

This project resolves a critical corporate dilemma observed across retail e-commerce operations: **rapid top-line revenue expansion accompanied by accelerating profit margin contraction**. Through a modular Python analytics engine, automated data validation, an interactive Streamlit BI application, and an audited 36-month ROI framework, this repository provides enterprise executives with the evidence and roadmap necessary to recover **+$102,997 in steady-state annual operating profit**.

---

## 2. Business Problem & Objectives

### The Business Dilemma
Between 2023 and 2025, the enterprise achieved impressive top-line growth:
- **Revenue expanded +56.2%** from **$896,588.03** (2023) to **$1,400,396.80** (2025).
- **Order volume surged +61.7%** from **3,079 orders** to **4,978 orders**.
- **Active customer accounts grew +162.6%** from **524** to **1,376**.

However, financial diagnostic analysis revealed severe underlying margin decay:
- **Authoritative Weighted Profit Margin collapsed from 15.44% to 11.93%** (-351 basis points).
- **1,579 loss-making orders (13.16% of all transactions)** destroyed **-$129,119.31** in operating income.

### Core Objectives
1. **Data Architecture & Hygiene:** Clean, normalize, and validate 12,400 raw transaction records into a deterministic, audit-trailed candidate dataset.
2. **Diagnostic Analytics:** Statistically isolate the root drivers of margin bleed across discount bands, sales channels, product categories, and fulfillment logistics.
3. **Financial Scenario Modeling:** Build an audited 36-month dynamic ROI engine evaluating three strategic interventions under Conservative, Base Case, and Optimistic operational assumptions.
4. **C-Suite Decision Support:** Deliver an interactive multi-page Streamlit BI dashboard, a 15-slide widescreen executive presentation (PDF & editable PowerPoint), and comprehensive technical documentation.

---

## 3. Key Findings & Executive Takeaways

| Analytical Area | Core Finding & Audited Metric | Business Implication |
| :--- | :--- | :--- |
| **Top-Line Growth** | Total 3-year revenue: **$3,373,628.44** across **11,996 clean orders** | Strong customer acquisition and market demand. |
| **Profitability Bleed** | Total 3-year contribution profit: **$458,057.99**; margin dropped from **15.44% to 11.93%** | Revenue growth is heavily subsidized by unmonitored margin erosion. |
| **Deep Discounting (Rec 1)** | Discounts $>20\%$ generated **-$82,129.46** in net losses; $>30\%$ discounts lost **-22.55%** margin | Welch's t-test ($t = -68.02, p < 0.0001$) proves discounts $>20\%$ destroy margin. |
| **Marketplace Channel Drag (Rec 2)** | Marketplace GMV was **$684,070.56** (20.28% share) but lost **-$17,436.80** (-2.55% margin) | The 13.0% platform take-rate renders Marketplace fundamentally unviable without intervention. |
| **Fulfillment Bottlenecks (Rec 3)**| Late shipments ($>5$ days) suffer a **14.91% return rate** vs. **4.78%** on-time ($t = 14.13, p < 0.0001$)| Shipping delays directly trigger costly merchandise returns; Central late rate is **58.41%**. |
| **Customer Retention Dynamics** | Repeat buyers generate **94.95% of orders** and **66.08% of revenue** | **Customer Contagion Risk:** Discount reform must not blindly terminate cross-category profitable buyers. |
| **Rec 3 Standalone Deficit** | Recommendation 3 yields **-$18,794.58 net 36M deficit** in Base Case (`Never` breakeven) | Logistics reform cannot be justified purely on standalone direct savings; requires pilot or restructuring. |
| **Portfolio 36M Base Case** | **+$200,722.56 Net Cash Benefit**, **232.72% Net ROI**, **$168,399.10 10% NPV**, **Payback: Month 8**| Highly attractive portfolio return recovering investment within 8 months of launch. |

---

## 4. Dataset Description & Simulated Data Disclosure

> **Explicit Analytical Disclosure:**  
> The underlying transactional dataset used in this project is synthetically generated and modeled for business intelligence design, academic demonstration, and executive decision-making. All transaction IDs, customer names, corporate segments, and financial records simulate real-world e-commerce enterprise conditions, incorporating authentic anomalies such as currency formatting artifacts, text capitalization variances, missing values, exact duplicates, and typographical entry errors.

- **Primary Input File:** [`Dataset/raw_sales_data.csv`](Dataset/raw_sales_data.csv) (12,400 raw rows, 16 attributes)
- **Validated Clean File:** [`Dataset/clean_dataset.csv`](Dataset/clean_dataset.csv) (11,996 clean rows, 27 attributes)
- **Reporting Period:** January 1, 2023 – December 31, 2025 (3 Full Calendar Years)
- Detailed column definitions, data types, and transformation rules are documented in [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md).

---

## 5. Technology Stack

- **Core Analytics & Numerical Computing:** Python 3.12+, `pandas` (v2.2.2), `numpy` (v2.3.5), `scipy` (v1.18.1)
- **Interactive BI & Dashboarding:** `streamlit` (v1.38.0), `plotly` (v6.9.0)
- **Document & Presentation Generation:** `reportlab` (v5.0.1), `python-pptx` (v1.0.2), `matplotlib` (v3.9.0)
- **Automated Testing & QA:** `pytest` (v9.1.1)

---

## 6. Repository Structure

```
.
├── .gitignore                                      # Production Git ignore specifications
├── app.py                                          # Streamlit BI application entry point
├── Dataset/                                        # Protected baseline data assets
│   ├── raw_sales_data.csv                          # Uncleaned raw input (12,400 rows) [PROTECTED]
│   └── clean_dataset.csv                           # Clean baseline data (11,996 rows) [PROTECTED]
├── docs/                                           # Comprehensive technical documentation
│   ├── DATA_DICTIONARY.md                          # Schema, column descriptions, and cleaning rules
│   ├── FINANCIAL_MODEL.md                          # 36-month ROI framework, formulas, and assumptions
│   ├── PROJECT_METHODOLOGY.md                      # 7-stage analytical and engineering methodology
│   ├── DASHBOARD_GUIDE.md                          # Streamlit application navigation and feature guide
│   ├── REPRODUCIBILITY.md                          # Step-by-step setup and re-execution instructions
│   └── DELIVERABLES.md                             # Index and cryptographic manifest of deliverables
├── Executive_Decision_Analysis.ipynb               # Original exploratory notebook [PROTECTED]
├── Executive_Decision_Report.pdf                   # Original baseline PDF submission [PROTECTED]
├── notebooks/                                      # Refactored computational notebooks
│   └── Executive_Decision_Analysis_Refactored.ipynb# Modular pipeline notebook using src/
├── outputs/                                        # Generated reports, metrics, and deliverables
│   ├── Executive_Decision_Report_Final.pdf         # Final 15-slide widescreen C-suite report (ReportLab)
│   ├── Executive_Decision_Report_Final.pptx        # Final 15-slide editable slide deck (python-pptx)
│   ├── STAGE_2_REPORT.md                           # Data quality and modular foundation audit report
│   ├── STAGE_4_REPORT.md                           # Validated ROI engine and scenario analysis report
│   ├── STAGE_4_1_AUDIT_REPORT.md                   # Independent financial consistency audit report
│   ├── STAGE_5_REPORT.md                           # Executive presentation design and verification report
│   ├── STAGE_5_1_QA_REPORT.md                      # Presentation visual and numerical QA audit report
│   ├── STAGE_6_REPORT.md                           # Portfolio documentation and submission checklist
│   ├── data_quality_report.csv                     # 12-point automated data quality scorecard
│   ├── financial_reconciliation.csv                # Step-by-step P&L reconciliation table
│   ├── metrics.json                                # Complete pre-computed authoritative metrics
│   ├── roi_scenarios.csv                           # 36-month Conservative, Base, Optimistic summaries
│   ├── monthly_cash_flow.csv                       # Month-by-month cash flows across 36 months
│   ├── break_even_analysis.csv                     # Breakeven months and discounted 10% WACC NPV
│   ├── sensitivity_analysis.csv                    # 7-dimensional sensitivity sweep results
│   ├── roi_assumptions.json                        # Assumption register with business citations
│   └── charts/                                     # Publication-grade vector/PNG visual charts
├── pages/                                          # Streamlit multi-page BI views
│   ├── 1_Executive_Overview.py                     # High-level scorecard and executive summary
│   ├── 2_Revenue_Profitability.py                  # P&L trends, categories, and monthly seasonality
│   ├── 3_Discount_Analysis.py                      # Margin bleed curves and discount bands
│   ├── 4_Channel_Regional_Analysis.py              # Channel economics and regional logistics
│   ├── 5_Customer_Analytics.py                     # Cohort retention and customer Pareto curves
│   ├── 6_Delivery_Returns.py                       # SLA violation distributions and return penalties
│   ├── 7_Statistical_Insights.py                   # Welch's t-test hypotheses and distributions
│   ├── 8_Strategic_Decisions.py                    # Interactive 36-month ROI scenario simulator
│   └── 9_Data_Quality.py                           # Cleaning audit trail and exception registers
├── requirements.txt                                # Pinned Python dependencies
├── run_pipeline.py                                 # Master deterministic pipeline execution script
├── src/                                            # Modular production Python source code
│   ├── dashboard_utils.py                          # Streamlit caching, UI cards, and Plotly styling
│   ├── data_cleaning.py                            # Idempotent 7-step data cleaning pipeline
│   ├── generate_presentation.py                    # PDF/PPTX document generation engine
│   ├── io_utils.py                                 # Deterministic file I/O and path resolution
│   ├── kpi_engine.py                               # Authoritative KPI and statistical calculation
│   ├── roi_model.py                                # Dynamic 36-month ROI engine and sensitivity
│   └── validation.py                               # 12-point automated data quality gate
└── tests/                                          # Automated unit and regression test suite
    ├── test_dashboard_utils.py                     # Dashboard utility and filter unit tests
    ├── test_data_cleaning.py                       # Data cleaning and imputation tests
    ├── test_kpi_engine.py                          # Financial formula and weighted margin tests
    ├── test_roi_model.py                           # ROI, cash flow, NPV, and sensitivity tests
    └── test_validation.py                         # Data quality gate boundary tests
```

---

## 7. Analytical Methodology & Data-Cleaning Pipeline

The pipeline processes raw data through seven deterministic, audit-logged transformation stages:

1. **Exact Deduplication:** 400 identical rows identified and removed (-$185,341.10 revenue, -$36,702.15 profit).
2. **Text Normalization:** Standardizes 29 region variants to 5, 9 segment variants to 3, and 18 category variants to 3.
3. **Hierarchical Categorical Imputation:** Imputes missing `segment` and `region` values using historical customer account mode prior to falling back to global population mode.
4. **Sub-Category Lookup Imputation:** Resolves missing product categories directly from granular sub-categories.
5. **Numerical Median Imputation:** Imputes missing discount rates and order quantities using sub-category medians.
6. **Unrecoverable Drop Policy:** Drops 4 records lacking both `quantity` and `discount` (-$1,123.56 revenue) where mathematical reconstruction was impossible without bias.
7. **Typographical Outlier Correction:** Corrects 28 typographical errors with quantities $>20$ units (scaling entries up to 900 units down to subcategory medians, adjusting -$552,348.78 in erroneous revenue).

For a complete breakdown, refer to [`docs/PROJECT_METHODOLOGY.md`](docs/PROJECT_METHODOLOGY.md).

---

## 8. Data-Quality Validation & Financial Reconciliation

### Automated 12-Point Data Quality Gate (`src/validation.py`)
- **Status:** **VALIDATED** (11 Passed, 0 Failed, 1 Info Warning).
- **Checks Enforced:** Zero nulls, unique `order_id`, revenue arithmetic ($|sales - [qty \times price \times (1-disc)]| < \$0.05$), profit arithmetic, positive prices, valid calendar dates, and canonical categoricals.

### Financial Reconciliation Waterfall
```
Raw Dataset (12,400 rows)           :  $4,112,441.88 Rev | $652,660.61 Profit | 15.87% Margin
  ├── Deduplication (-400 rows)     : -$  185,341.10 Rev | -$ 36,702.15 Profit
  ├── Dropped Unrecoverable (-4)    : -$    1,123.56 Rev | -$    288.90 Profit
  └── Outlier Corrections (28 rows) : -$  552,348.78 Rev | -$157,611.57 Profit
Clean Candidate Dataset (11,996)    :  $3,373,628.44 Rev | $458,057.99 Profit | 13.58% Margin
```
*Exact verification against `Dataset/clean_dataset.csv`: 100% Match (0 Discrepancies).*

---

## 9. Interactive Dashboard Features & Execution

The multi-page Streamlit application delivers an executive-grade BI interface:
- **Interactive Multi-Page Navigation:** 9 dedicated analytical views covering executives, sales, discounts, channels, cohorts, logistics, statistics, ROI, and data hygiene.
- **Dynamic Scenario Toggling:** Real-time parameter switching between Conservative, Base Case, and Optimistic models on Page 8.
- **Enterprise UI Aesthetics:** Curated navy-and-white theme (`#1E3A8A`, `#0EA5E9`, `#F8FAFC`) with responsive Plotly visualizations and zero page lag via cached data layers.

### Launching the Dashboard
```bash
streamlit run app.py
```
For full navigation details, see [`docs/DASHBOARD_GUIDE.md`](docs/DASHBOARD_GUIDE.md).

---

## 10. How to Run the Pipeline & Test Suite

### 1. Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows PowerShell
# source .venv/bin/activate    # Linux / macOS

# Install pinned dependencies
pip install -r requirements.txt
```

### 2. Execute Deterministic Data Pipeline
```bash
python run_pipeline.py
```
*Regenerates all Stage 2 & Stage 4 audit artifacts, metrics, and scenario files in `outputs/`.*

### 3. Generate Executive Presentation Deliverables (PDF & PPTX)
```bash
python src/generate_presentation.py
```
*Generates the 15-slide ReportLab PDF and python-pptx PowerPoint decks.*

### 4. Run Automated Test Suite
```bash
python -m pytest tests/ -v
```
*Executes all 75 unit, regression, and data-integrity tests. Expected runtime: ~6–8 seconds.*

Complete step-by-step reproducibility instructions are available in [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md).

---

## 11. ROI Methodology & Scenario Assumptions

The 36-month dynamic financial simulation incorporates launch delays, operational ramp-up curves, double-counting protections, and 10% annual WACC discounting.

### 36-Month Scenario Comparison

| Scenario | Annual Revenue Delta | Annual Profit Uplift | 36M Total Cost | 36M Net Cash Benefit | 36M Net ROI | 10% WACC NPV | Payback Month |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Conservative**| +$52,969.71 | +$82,453.73 | $99,699.86 | +$119,554.59 | **119.91%** | **$99,444.20** | **Month 12** |
| **Base Case** | **+$110,370.55**| **+$102,997.42**| **$86,249.88** | **+$200,722.56** | **232.72%** | **$168,399.10**| **Month 8** |
| **Optimistic** | +$165,783.68 | +$121,792.14 | $77,624.89 | +$256,068.11 | **329.88%** | **$215,649.30**| **Month 5** |

### Robustness & Sensitivity Highlights
- **Sequential Double-Counting Guard:** Recommendation 2 calculations operate strictly on the post-Rec 1 Marketplace revenue baseline ($625,110 GMV), preventing artificial double-counting of savings.
- **Multi-Dimensional Sensitivity:** Tested across 7 dimensions (order retention, commission cuts, customer retention, shipping delays, return costs, capex overruns, launch delays). In all scenarios, portfolio net benefit remains substantially positive.

Detailed formulas and parameter tables are documented in [`docs/FINANCIAL_MODEL.md`](docs/FINANCIAL_MODEL.md).

---

## 12. Three Actionable Strategic Recommendations

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ RECOMMENDATION 1: DISCOUNT GUARDRAILS & LOSS PREVENTION                         │
│ • Policy: Enforce strict 20% discount cap and hard price floor on all channels. │
│ • Economics: Recaptures $79.3k/yr in losses with 85% order retention guardrail. │
│ • Base Return: Annual Uplift $66,332 | 36M Net $171,468 | ROI 779% | Payback M3 │
└─────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ RECOMMENDATION 2: MARKETPLACE MARGIN REPAIR                                      │
│ • Policy: Renegotiate take-rate (13% -> 10%) and institute +3% channel parity.  │
│ • Economics: Eliminates $17.4k channel deficit across $625k baseline GMV.       │
│ • Base Return: Annual Uplift $29,352 | 36M Net $48,049 | ROI 166% | Payback M12 │
└─────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ RECOMMENDATION 3: DELIVERY SLA ENFORCEMENT & TARGETED PILOT                     │
│ • Policy: Enforce 3-day carrier SLAs; launch regional micro-fulfillment 3PL.    │
│ • Economics: Slashes late shipments (Central 58.4%) and cuts returns (14.9%).   │
│ • Base Return: Annual Uplift $7,314 | 36M Deficit -$18,795 | Payback Never (>36)│
│ • STRATEGIC MANDATE: Do NOT launch at full scale. Restructure opex or restrict  │
│   to a focused pilot on high-margin Technology lines in the Central Region.     │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 13. Final Deliverables & Executive Presentation Links

| Deliverable Asset | Repository Path | Description |
| :--- | :--- | :--- |
| **Final Executive Decision Report (PDF)** | [`outputs/Executive_Decision_Report_Final.pdf`](outputs/Executive_Decision_Report_Final.pdf) | 15-slide widescreen PDF engineered via ReportLab. |
| **Final Presentation Deck (PowerPoint)** | [`outputs/Executive_Decision_Report_Final.pptx`](outputs/Executive_Decision_Report_Final.pptx) | 15-slide editable PowerPoint presentation (python-pptx). |
| **Deliverables & Artifact Manifest** | [`docs/DELIVERABLES.md`](docs/DELIVERABLES.md) | Cryptographic verification manifest of all project files. |
| **Stage 5 Presentation Report** | [`outputs/STAGE_5_REPORT.md`](outputs/STAGE_5_REPORT.md) | Complete presentation design and slide content documentation. |
| **Stage 5.1 Presentation QA Report** | [`outputs/STAGE_5_1_QA_REPORT.md`](outputs/STAGE_5_1_QA_REPORT.md) | Slide-by-slide visual and numerical verification audit. |
| **Stage 6 Submission Report** | [`outputs/STAGE_6_REPORT.md`](outputs/STAGE_6_REPORT.md) | Repository hygiene audit and final submission checklist. |

---

## 14. Limitations, Uncertainty & Governance

1. **Simulated Model Boundaries:** All analyses derive from a synthetically generated transaction dataset. While mathematically consistent, these projections represent decision models rather than historical corporate accounting records.
2. **Customer Elasticity Risk:** The 85% order retention assumption in Recommendation 1 represents an modeled estimate. If price elasticity leads to retention falling below 65%, pricing uplift may be impaired.
3. **Marketplace Counterparty Risk:** Recommendation 2 assumes marketplace partners will accept a 300 bps commission concession. If negotiations fail, price parity must be raised to +6% to compensate.
4. **Logistics Opex Drag:** As proven by the standalone deficit of Recommendation 3 (-$18,794.58), fulfillment logistics must be strictly governed by performance SLAs to avoid cost overruns.

---

## 15. Future Enhancements

- **Machine Learning Elasticity Modeling:** Train an econometric price-elasticity model per SKU sub-category to predict customer churn under customized discount caps.
- **Automated Reverse Logistics API:** Integrate real-time carrier webhooks (FedEx/UPS/3PL) to automate customer notifications and SLA penalty claims.
- **Multi-Currency & Tax Engine:** Expand the financial engine to support international VAT, tariff structures, and dynamic currency conversions.

---

## 16. Author & Project Purpose

**Program:** Data Analytics & Business Intelligence Internship Capstone  
**Target Audience:** Corporate Board of Directors, Chief Financial Officer (CFO), Chief Operating Officer (COO), and Capstone Review Committee  
**Verification Date:** October 2026  
**License:** MIT License  
