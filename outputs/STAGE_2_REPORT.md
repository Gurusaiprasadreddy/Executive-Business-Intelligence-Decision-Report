# STAGE 2 REPORT — DATA QUALITY, FINANCIAL RECONCILIATION & MODULAR FOUNDATION

**Executive Decision Report & Capstone Presentation**  
**Role:** Senior Data Engineer, Financial Analytics Engineer & Python Testing Specialist  
**Execution Date:** 2026-10-18  
**Workspace Root:** `D:\RabTech Academy internship\Executive Decision Report & Capstone Presentation`  
**Pipeline Status:** ✅ **VALIDATED & PRODUCTION-READY**

---

## 1. Executive Summary

Stage 2 has successfully established a reproducible, fully auditable, and modular data pipeline for the Executive Decision Analytics capstone. All core data processing logic previously locked inside notebook cells has been decoupled into production-grade Python modules under `src/`, accompanied by an automated `pytest` validation suite under `tests/`, and standardized machine-readable audit artifacts under `outputs/`.

### Key Deliverables Produced:
* **`requirements.txt`**: Pinned, justified project dependencies.
* **`src/` package**:
  - `src/io_utils.py`: Deterministic path resolution, CSV handling, and NumPy/Pandas JSON serialization.
  - `src/data_cleaning.py`: Fully vectorized and auditable cleaning, imputation, outlier correction, and feature engineering.
  - `src/kpi_engine.py`: Single authoritative business logic for annual, monthly, dimensional, and customer cohort KPIs.
  - `src/validation.py`: Automated quality gates distinguishing critical failures from monitored baselines.
* **`tests/` suite**: 18 automated tests passing in 1.35s across synthetic fixtures.
* **`outputs/` deliverables**:
  - `outputs/data_quality_report.csv`: 12 automated validation checks (11 PASS, 1 INFO/monitored baseline, 0 FAIL).
  - `outputs/financial_reconciliation.csv`: Complete waterfall from raw data ($4.11M) to clean data ($3.37M).
  - `outputs/metrics.json`: Version 2.0.0 metadata-rich contract containing all verified KPIs, definitions, and formulas.
  - `outputs/candidate_clean_dataset.csv`: Cleaned output produced deterministically by the modular pipeline.
  - `outputs/audit/cleaning_log.csv`: 1,684 row-level audit events detailing every modification.
  - `outputs/audit/unresolved_records.csv`: 1,018 cataloged edge cases (607 minor rounding deltas, 407 extreme IQR sales, 4 unrecoverable drops).

---

## 2. Raw Data Integrity & Protection Status

As mandated by Stage 2 safety rules, all existing workspace files were protected and left unmodified.

| File Path | Baseline SHA256 Checksum | Post-Execution SHA256 Checksum | Status |
| :--- | :--- | :--- | :--- |
| `Dataset/raw_sales_data.csv` | `1685e689491bd2d4751528030de2bd05ec85408578ef1de1f42c449b02172b83` | `1685e689491bd2d4751528030de2bd05ec85408578ef1de1f42c449b02172b83` | ✅ **Byte-for-byte identical (Preserved)** |
| `Dataset/clean_dataset.csv` | `295e02511af8d63b537bb309b1cecf7181694bad28cd4ed362e38e58f1183a8e` | `295e02511af8d63b537bb309b1cecf7181694bad28cd4ed362e38e58f1183a8e` | ✅ **Unmodified in place** |
| `Executive_Decision_Analysis.ipynb` | `7a3492db63e0af455fe033e55179fa4c4cecddeb01d9b628dfdf3d59c2346d44` | `7a3492db63e0af455fe033e55179fa4c4cecddeb01d9b628dfdf3d59c2346d44` | ✅ **Preserved** |
| `Executive_Decision_Report.pdf` | `dc9fca22868b985864eff1da83cd15b2a22779f3f1b5d210cf71a2e2154bfdbc` | `dc9fca22868b985864eff1da83cd15b2a22779f3f1b5d210cf71a2e2154bfdbc` | ✅ **Preserved** |

---

## 3. Candidate Clean Dataset vs. Existing Clean Dataset

A row-by-row and column-by-column value comparison was conducted between the existing `Dataset/clean_dataset.csv` and the newly generated `outputs/candidate_clean_dataset.csv`.

* **Shape Comparison:**
  - Existing `clean_dataset.csv`: **11,996 rows × 27 columns**
  - Candidate `candidate_clean_dataset.csv`: **11,996 rows × 27 columns**
* **Schema Match:** All 27 column names and data types match identically.
* **Value Consistency:**
  - Mismatches found across all numeric fields: **0 rows**
  - Mismatches found across categorical/text fields: **0 rows**
  - Mismatches found across datetime/derived fields: **0 rows**
* **Conclusion:** The modular pipeline reproduces the benchmark clean dataset with **100% mathematical fidelity and zero drift**, confirming complete reproducibility.

---

## 4. Financial Reconciliation & Waterfall Analysis

Stage 1 suspected a large profit drop (~$122k) between raw and clean data. Stage 2 executed an exact step-by-step financial attribution to explain every dollar of variance.

### 4.1 Reconciliation Waterfall

| Step | Stage Description | Row Count | Revenue ($) | Profit ($) | Weighted Margin (%) | Delta Revenue ($) | Delta Profit ($) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | **Raw Sales Data (All Records)** | 12,400 | $4,112,441.88 | $652,660.61 | 15.87% | $0.00 | $0.00 |
| **2** | **Exact Duplicate Removal** | (400) | -$185,341.10 | -$36,702.15 | 19.80% | -$185,341.10 | -$36,702.15 |
| **3** | **Post-Deduplication Subtotal** | 12,000 | $3,927,100.78 | $615,958.46 | 15.68% | -$185,341.10 | -$36,702.15 |
| **4** | **Unrecoverable Rows Dropped** | (4) | -$1,123.56 | -$288.90 | 25.71% | -$1,123.56 | -$288.90 |
| **5** | **Quantity Entry Error Correction** | 28 lines | -$552,348.78 | -$157,611.57 | 28.53% | -$552,348.78 | -$157,611.57 |
| **6** | **Final Cleaned Dataset (Total)** | **11,996** | **$3,373,628.44** | **$458,057.99** | **13.58%** | **-$738,813.44** | **-$194,602.62** |

### 4.2 Waterfall Insights:
1. **The $194.6k Raw-to-Clean Profit Variance Explained:**
   - **81.0%** (-$157,611.57) comes directly from correcting 28 entry errors where order line quantities reached up to 900 units.
   - **18.9%** (-$36,702.15) comes from purging 400 exact duplicate orders.
   - **0.1%** (-$288.90) comes from dropping 4 records where both discount and quantity were unrecoverable.
2. **Increase in Negative-Profit Rows (1,387 raw → 1,579 clean):**
   - Correcting the 28 massive quantity keying errors recalculated profit using the channel fee formula (`sales*(1 - fee) - qty*cost`). Because these orders were in Marketplace (13% fee) or high-discount bands, removing the erroneous quantity inflated the cost-to-sales ratio, flipping orders into their true net-loss state.

---

## 5. Annual Metrics Reconciliation (2023–2025)

Every single annual metric reported in the Executive PDF Report (Slides 2, 3, 12) and Notebook Cell 012 has been independently reconciled from raw transactions:

| Metric | 2023 | 2024 | 2025 | Overall / Total | PDF & Notebook Match |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Revenue ($)** | $896,588.03 | $1,076,643.61 | $1,400,396.80 | $3,373,628.44 | ✅ Exact Cent Match |
| **Profit ($)** | $138,397.72 | $152,572.32 | $167,087.95 | $458,057.99 | ✅ Exact Cent Match |
| **Weighted Margin (%)** | 15.44% | 14.17% | 11.93% | 13.58% | ✅ Exact Basis Point Match |
| **Record Count (Orders)** | 3,079 | 3,939 | 4,978 | 11,996 | ✅ Exact Match |
| **Unique Customers** | 524 | 1,003 | 1,376 | 2,116 | ✅ Exact Match |
| **Average Order Value ($)** | $291.19 | $273.33 | $281.32 | $281.23 | ✅ Exact Match |
| **Return Rate (%)** | 6.11% | 7.49% | 7.37% | 7.09% | ✅ Exact Match |
| **Late Delivery Rate (%)** | 21.47% | 23.33% | 23.10% | 22.76% | ✅ Exact Match |

---

## 6. Core Financial & Analytical Inquiries Resolved

1. **Revenue Arithmetic Consistency:**
   - Formula: $\text{Expected Sales} = \text{Quantity} \times \text{Unit Price} \times (1 - \text{Discount})$
   - Across all 11,996 orders, **0 orders deviate by >2%**. The maximum absolute difference observed across the entire dataset is **$0.06** (due to floating-point rounding of cents).
2. **Profit Accounting Consistency:**
   - Formula: $\text{Expected Profit} = \text{Sales} \times (1 - \text{Channel Fee}) - (\text{Quantity} \times \text{Unit Cost})$
   - Across all 11,996 orders, **0 orders deviate by >$0.10**. The maximum difference observed is **$0.0456** (sub-nickel penny variance from original string truncation).
3. **Marketplace Fee Mechanism:**
   - Channel fees are strictly modeled as a percentage of gross sales:
     * **Retail Store:** $0.0\%$
     * **Online Direct:** $4.0\%$
     * **Marketplace:** $13.0\%$
   - The fee is deducted prior to deducting COGS, creating significant margin compression on Marketplace items.
4. **Treatment of Returns and Shipping Costs in Recorded Historical Data:**
   - In `raw_sales_data.csv` and `clean_dataset.csv`, `returned` is recorded as a boolean flag ($850$ returned orders, $11,146$ kept).
   - **Crucial Finding:** Neither shipping cost nor return processing expenses are deducted from the recorded historical `sales` or `profit` columns! Orders marked `returned=True` still reflect their original gross order revenue and profit.
   - **Scenario Model Handling:** In Recommendation 3 of the ROI Engine, return handling expenses ($5\%$ of order value) and lost margin are modeled as *incremental cash-flow savings* achieved by reducing shipping delays.
5. **Weighted Profit Margin vs. Unweighted Average:**
   - As proven in `tests/test_kpi_engine.py`, taking a simple average of `profit_margin` yields distorted results because it weights a $10 order equally with a $5,000 order.
   - The authoritative metric implemented throughout `src/kpi_engine.py` is $\frac{\sum \text{Profit}}{\sum \text{Sales}} \times 100\%$.

---

## 7. Data Quality Validation Report

The automated test runner in `src/validation.py` executed 12 comprehensive checks against `Dataset/clean_dataset.csv` and logged them in `outputs/data_quality_report.csv`:

| Check Category | Check Name | Severity | Observed Value | Expected Value | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Structural** | Missing Values Count | CRITICAL | 0 | 0 | ✅ PASS |
| **Structural** | Order ID Uniqueness | CRITICAL | 0 duplicates | 0 | ✅ PASS |
| **Structural** | Schema Completeness | CRITICAL | 27 columns present | 27 columns | ✅ PASS |
| **Pipeline Recon** | Row Count Arithmetic | CRITICAL | 11,996 | 12,400 - 400 - 4 = 11,996 | ✅ PASS |
| **Domain Constraints** | Date Range Validity | CRITICAL | 2023-01-01 to 2025-12-31 | 2023-01-01 to 2025-12-31 | ✅ PASS |
| **Domain Constraints** | Quantity Range & Integer | CRITICAL | min=1, max=12 | 1 <= qty <= 20 (integer) | ✅ PASS |
| **Domain Constraints** | Discount Range Check | CRITICAL | min=0.00, max=0.50 | 0.00 <= discount <= 0.50 | ✅ PASS |
| **Domain Constraints** | Price & Cost Positivity | CRITICAL | price >= 8.35, cost >= 4.15 | Both > 0 | ✅ PASS |
| **Arithmetic** | Sales Consistency (<2%) | CRITICAL | 0 rows deviating (max $0.06) | 0 rows deviating | ✅ PASS |
| **Arithmetic** | Profit Consistency (<$0.10) | CRITICAL | 0 rows deviating (max $0.046) | 0 rows deviating | ✅ PASS |
| **Feature Engineering** | Derived Logic Consistency | CRITICAL | year, margin, late, loss match | 100% logic alignment | ✅ PASS |
| **Business Metrics** | Loss-Making Orders Count | WARNING | 1,579 orders (13.2%) | Monitored baseline | ℹ️ INFO |

**Overall Quality Gate Status:** **VALIDATED (100% Critical Checks Passed)**

---

## 8. Automated Test Suite Results

Automated unit and integration testing was executed using `pytest` on synthetic test fixtures:

```powershell
python -m pytest tests/ -v
```

**Results Output:**
```
tests/test_data_cleaning.py::test_date_parsing PASSED                    [  5%]
tests/test_data_cleaning.py::test_currency_and_boolean_cleaning PASSED   [ 11%]
tests/test_data_cleaning.py::test_duplicate_detection PASSED             [ 16%]
tests/test_data_cleaning.py::test_label_standardization PASSED           [ 22%]
tests/test_data_cleaning.py::test_imputation_and_unrecoverable_drop PASSED [ 27%]
tests/test_data_cleaning.py::test_outlier_correction PASSED              [ 33%]
tests/test_data_cleaning.py::test_deterministic_cleaning_pipeline PASSED [ 38%]
tests/test_kpi_engine.py::test_safe_divide_and_zero_denominator PASSED   [ 44%]
tests/test_kpi_engine.py::test_weighted_vs_unweighted_margin PASSED      [ 50%]
tests/test_kpi_engine.py::test_annual_metrics_calculation PASSED         [ 55%]
tests/test_kpi_engine.py::test_customer_cohort_retention PASSED          [ 61%]
tests/test_kpi_engine.py::test_discount_band_metrics PASSED              [ 66%]
tests/test_validation.py::test_validation_passes_valid_data PASSED       [ 72%]
tests/test_validation.py::test_validation_fails_on_nulls PASSED          [ 77%]
tests/test_validation.py::test_validation_fails_on_duplicate_orders PASSED [ 83%]
tests/test_validation.py::test_validation_fails_on_sales_arithmetic_error PASSED [ 88%]
tests/test_validation.py::test_validation_fails_on_profit_arithmetic_error PASSED [ 94%]
tests/test_validation.py::test_validation_fails_on_missing_column PASSED [100%]

============================= 18 passed in 1.35s ==============================
```

---

## 9. Audit Trail & Traceability Summary

### 9.1 `outputs/audit/cleaning_log.csv` (1,684 records)
* **400 rows:** Exact row duplicates removed.
* **400 rows:** Missing region/segment imputed from customer purchase history mode.
* **356 rows:** Missing discounts reconstructed via $1 - \frac{\text{Sales}}{\text{Qty} \times \text{Price}}$ and snapped to the nearest commercial tier.
* **300 rows:** Missing `ship_days` imputed using regional medians and flagged in `ship_days_imputed`.
* **116 rows:** Missing quantities reconstructed via $\text{round}\left(\frac{\text{Sales}}{\text{Price} \times (1 - \text{Discount})}\right)$.
* **60 rows:** Missing categories deterministically mapped from `sub_category`.
* **28 rows:** Erroneous quantities (>20 units) corrected to subcategory medians.
* **20 rows:** Single-order customer region/segment imputed via global mode fallback.
* **4 rows:** Unrecoverable records safely dropped.

### 9.2 `outputs/audit/unresolved_records.csv` (1,018 records)
* **607 records:** Penny profit deviations ($<\$0.046$) carried from raw string truncations.
* **407 records:** High-value transactions exceeding the statistical extreme cutoff ($Q3 + 3 \times IQR = \$978.20$), flagged for executive audit.
* **4 records:** Dropped orders where both discount and quantity were absent.

---

## 10. Reproduction Commands

To reproduce all Stage 2 results, tests, and deliverables from scratch:

```powershell
# 1. Install pinned requirements
pip install -r requirements.txt

# 2. Run the automated test suite
python -m pytest tests/ -v

# 3. Execute the full modular pipeline to generate all artifacts
python run_pipeline.py
```

---

## 11. Acceptance Criteria Checklist & Stage 3 Readiness

| Criteria | Status | Evidence / Verification |
| :--- | :---: | :--- |
| **1. Raw dataset unchanged** | ✅ PASSED | SHA256 verified byte-for-byte (`1685e689...`) |
| **2. Existing notebook & PDF preserved** | ✅ PASSED | SHA256 verified byte-for-byte; no edits made |
| **3. Pipeline runs from project root** | ✅ PASSED | `python run_pipeline.py` executes cleanly from workspace root |
| **4. Cleaning is deterministic** | ✅ PASSED | Tested in `test_deterministic_cleaning_pipeline`; 0 drift |
| **5. Corrections & imputations auditable** | ✅ PASSED | Full event log saved in `outputs/audit/cleaning_log.csv` |
| **6. Financials independently reconciled** | ✅ PASSED | Waterfall and annual tables saved in `financial_reconciliation.csv` |
| **7. metrics.json generated by pipeline** | ✅ PASSED | Schema 2.0.0 JSON exported to `outputs/metrics.json` |
| **8. Automated tests executed & recorded** | ✅ PASSED | 18/18 pytest tests passing; output logged above |
| **9. Unresolved exceptions cataloged** | ✅ PASSED | Saved in `outputs/audit/unresolved_records.csv` |
| **10. Exact reproduction commands given** | ✅ PASSED | Documented in Section 10 |

### Final Recommendation
The data quality layer, financial reconciliation, and modular foundation are **100% verified and complete**. The project is completely stable and **READY FOR STAGE 3** (Analytical Jupyter Notebook refactoring and Streamlit Dashboard construction).
