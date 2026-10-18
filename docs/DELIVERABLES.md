# Capstone Deliverables Index & Artifact Manifest

**Internship Capstone:** Executive Decision Report & Business Intelligence Analytics  
**Submission Audience:** C-Suite Leadership, Executive Board & Academic Evaluators  
**Verification Date:** October 2026

---

## 1. Executive Presentation & Report Deliverables

| Deliverable Name | File Path | Format / Specification | Status | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Final Executive Decision Report (PDF)** | [`outputs/Executive_Decision_Report_Final.pdf`](../outputs/Executive_Decision_Report_Final.pdf) | PDF (15 Widescreen 16:9 Slides, 960x540 pt) | **APPROVED** | Authoritative executive presentation engineered via ReportLab with embedded charts, KPI tables, risk register, and roadmap. |
| **Final Presentation Deck (PowerPoint)** | [`outputs/Executive_Decision_Report_Final.pptx`](../outputs/Executive_Decision_Report_Final.pptx) | PPTX (15 Widescreen 16:9 Slides, 13.33"x7.5") | **APPROVED** | Fully editable C-suite presentation deck engineered via python-pptx with executive navy typography and cards. |
| **Original Baseline Report (Protected)** | [`Executive_Decision_Report.pdf`](../Executive_Decision_Report.pdf) | PDF (Original capstone submission) | **INTACT** | Byte-for-byte preserved original baseline submission document (SHA256 verified). |

---

## 2. Interactive Business Intelligence Suite

| Component | File Path | Description | Access / Execution |
| :--- | :--- | :--- | :--- |
| **Streamlit BI App (Landing)** | [`app.py`](../app.py) | Master entry point, high-level scorecard, and navigation. | `streamlit run app.py` |
| **Executive Overview** | [`pages/1_Executive_Overview.py`](../pages/1_Executive_Overview.py) | Macro-level 3-year performance review and executive summary. | Sidebar Page 1 |
| **Revenue & Profitability** | [`pages/2_Revenue_Profitability.py`](../pages/2_Revenue_Profitability.py) | Time series, monthly seasonality, and product category margins. | Sidebar Page 2 |
| **Discount Analysis** | [`pages/3_Discount_Analysis.py`](../pages/3_Discount_Analysis.py) | Discount band performance, margin erosion curve, and bleed points. | Sidebar Page 3 |
| **Channel & Regional Analysis** | [`pages/4_Channel_Regional_Analysis.py`](../pages/4_Channel_Regional_Analysis.py) | Channel P&L comparisons, marketplace fee drag, and regional late rates. | Sidebar Page 4 |
| **Customer Analytics** | [`pages/5_Customer_Analytics.py`](../pages/5_Customer_Analytics.py) | Cohort retention waterfall, repeat customer share, and Pareto analysis. | Sidebar Page 5 |
| **Delivery & Returns** | [`pages/6_Delivery_Returns.py`](../pages/6_Delivery_Returns.py) | Fulfillment duration histograms, SLA violations, and return penalties. | Sidebar Page 6 |
| **Statistical Insights** | [`pages/7_Statistical_Insights.py`](../pages/7_Statistical_Insights.py) | Formal Welch's t-tests (H1, H2, H3) and statistical distributions. | Sidebar Page 7 |
| **Strategic Decisions & ROI** | [`pages/8_Strategic_Decisions.py`](../pages/8_Strategic_Decisions.py) | Interactive 36-month ROI simulator with scenario toggles and sliders. | Sidebar Page 8 |
| **Data Quality & Governance** | [`pages/9_Data_Quality.py`](../pages/9_Data_Quality.py) | Step-by-step cleaning audit trail and unresolved exceptions review. | Sidebar Page 9 |

---

## 3. Analytical Notebooks

| Notebook File | File Path | Status | Purpose |
| :--- | :--- | :--- | :--- |
| **Original Baseline Notebook** | [`Executive_Decision_Analysis.ipynb`](../Executive_Decision_Analysis.ipynb) | **INTACT** (Protected) | Original exploratory Jupyter Notebook preserved byte-for-byte. |
| **Refactored Modular Notebook** | [`notebooks/Executive_Decision_Analysis_Refactored.ipynb`](../notebooks/Executive_Decision_Analysis_Refactored.ipynb) | Updated & Validated | Refactored notebook importing modular functions from `src/` for clean re-execution. |

---

## 4. Analytical Modules & Automated Pipelines

| Module | File Path | Functions / Responsibilities |
| :--- | :--- | :--- |
| **Pipeline Runner** | [`run_pipeline.py`](../run_pipeline.py) | Master orchestration script running cleaning, validation, and KPI generation. |
| **Presentation Generator** | [`src/generate_presentation.py`](../src/generate_presentation.py) | Automated rendering of PDF, PPTX, and all 7 publication charts. |
| **Data Cleaning Engine** | [`src/data_cleaning.py`](../src/data_cleaning.py) | Idempotent data hygiene, deduplication, imputation, and outlier scaling. |
| **Validation Gate** | [`src/validation.py`](../src/validation.py) | 12-point automated data quality gate enforcing business integrity rules. |
| **KPI Engine** | [`src/kpi_engine.py`](../src/kpi_engine.py) | Weighted margins, annual/monthly rollups, customer cohorts, and t-tests. |
| **ROI Financial Model** | [`src/roi_model.py`](../src/roi_model.py) | 36-month scenario simulator, double-counting guards, and sensitivity sweeps. |
| **Dashboard Utilities** | [`src/dashboard_utils.py`](../src/dashboard_utils.py) | Caching layer, currency formatting, metric cards, and Plotly templates. |
| **I/O Utilities** | [`src/io_utils.py`](../src/io_utils.py) | Project root resolution, deterministic JSON/CSV read and write handlers. |

---

## 5. Audited Data & Modeling Artifacts

| Artifact Name | File Path | Key Metrics & Contents |
| :--- | :--- | :--- |
| **Data Quality Audit Report** | [`outputs/data_quality_report.csv`](../outputs/data_quality_report.csv) | 12 checks evaluated: 11 Passed, 0 Failed, 1 Info Warning. |
| **Financial Reconciliation** | [`outputs/financial_reconciliation.csv`](../outputs/financial_reconciliation.csv) | Full audit reconciling $4.11M raw revenue to $3.37M clean revenue. |
| **Authoritative Metrics** | [`outputs/metrics.json`](../outputs/metrics.json) | Complete pre-computed financial and operational metrics dictionary. |
| **ROI Scenarios Table** | [`outputs/roi_scenarios.csv`](../outputs/roi_scenarios.csv) | Conservative, Base, and Optimistic 36-month revenue, profit, cost, and ROI. |
| **Monthly Cash Flows** | [`outputs/monthly_cash_flow.csv`](../outputs/monthly_cash_flow.csv) | 36 monthly rows covering Capex, Opex, Ramp-up, and Net Cash Flow. |
| **Break-Even Analysis** | [`outputs/break_even_analysis.csv`](../outputs/break_even_analysis.csv) | Breakeven months (Base = Month 8) and discounted NPV ($168,399.10). |
| **Sensitivity Analysis** | [`outputs/sensitivity_analysis.csv`](../outputs/sensitivity_analysis.csv) | 7-dimensional sensitivity sweep across retention, fees, and delays. |
| **ROI Assumptions Register**| [`outputs/roi_assumptions.json`](../outputs/roi_assumptions.json) | Full documentation of financial assumptions, sources, and rationale. |

---

## 6. Audit & QA Reports

| Stage Report | File Path | Focus Area | Status |
| :--- | :--- | :--- | :--- |
| **Stage 2 Audit Report** | [`outputs/STAGE_2_REPORT.md`](../outputs/STAGE_2_REPORT.md) | Data Quality, Modular Pipeline & Foundation Setup | Complete & Signed |
| **Stage 4 ROI Report** | [`outputs/STAGE_4_REPORT.md`](../outputs/STAGE_4_REPORT.md) | Validated ROI Engine & Financial Scenario Analysis | Complete & Signed |
| **Stage 4.1 Audit Report**| [`outputs/STAGE_4_1_AUDIT_REPORT.md`](../outputs/STAGE_4_1_AUDIT_REPORT.md) | Independent Financial Consistency Audit | Complete & Reconciled |
| **Stage 5 Report** | [`outputs/STAGE_5_REPORT.md`](../outputs/STAGE_5_REPORT.md) | Executive Presentation Design & Deliverables | Complete & Signed |
| **Stage 5.1 QA Report** | [`outputs/STAGE_5_1_QA_REPORT.md`](../outputs/STAGE_5_1_QA_REPORT.md) | Independent Visual & Numerical Presentation QA | Complete & Verified |
| **Stage 6 Report** | [`outputs/STAGE_6_REPORT.md`](../outputs/STAGE_6_REPORT.md) | Portfolio Documentation & Final Submission Checklist | Current Milestone |
