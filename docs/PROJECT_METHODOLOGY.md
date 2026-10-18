# Project Analytical Methodology & Technical Architecture

**Internship Capstone:** Executive Decision Report & Business Intelligence Analytics  
**Architecture Lead:** Senior BI Consultant & Data Analytics Engineer  
**Code Modules:** `src/data_cleaning.py`, `src/kpi_engine.py`, `src/roi_model.py`, `src/validation.py`, `src/dashboard_utils.py`, `src/generate_presentation.py`

---

## 1. Project Overview & Business Discovery

### 1.1 The Core Business Dilemma: "Top-Line Growth vs. Margin Erosion"
Between 2023 and 2025, the retail e-commerce business achieved strong top-line sales expansion:
- **Revenue surged +56.2%** from **$896,588.03** in 2023 to **$1,400,396.80** in 2025.
- **Order volume expanded +61.7%** from **3,079 orders** to **4,978 orders**.
- However, **Weighted Profit Margin collapsed from 15.44% to 11.93%** (-351 basis points).
- In total, **1,579 loss-making orders (13.16% of total orders)** destroyed **-$129,119.31** in cumulative operating profit.

### 1.2 Root Cause Discovery
Rigorous diagnostic analysis isolated three primary operational drivers of this margin collapse:
1. **Uncontrolled Discounting:** Orders with discounts exceeding 20% generated an aggregate loss of -$82,129.46. Average transaction margins dropped from +33.61% (for discounts $\le 20\%$) to +4.87% (for discounts $> 20\%$).
2. **Marketplace Commission Drag:** The third-party Marketplace channel expanded to 20.28% of overall sales ($684,070.56 GMV) but operated at a **negative contribution margin of -2.55%** (-$17,436.80 total loss) due to an aggressive 13.0% platform take-rate.
3. **Fulfillment Bottlenecks & Returns:** Deliveries taking $>5$ days suffered a return rate of **14.91%**—more than triple the 4.78% return rate observed on on-time shipments. Central region late shipments reached an alarming **58.41%**.

---

## 2. Seven-Stage Analytical Workflow

```
[ Raw Data: 12,400 Rows ]
           │
           ▼
┌──────────────────────────────────────────────┐
│ Stage 1: Data Cleaning & Hygiene             │
│ • Exact Deduplication (-400 rows)            │
│ • String & Categorical Normalization         │
│ • Median / Mode Missing Imputation (1,260)   │
│ • Unrecoverable Record Removal (-4 rows)     │
│ • Typographical Outlier Correction (28 rows) │
└──────────────────────────────────────────────┘
           │
           ▼
[ Clean Dataset: 11,996 Rows ] ──► [ Validation Suite: 12 Integrity Checks ]
           │
           ├──────────────────────────────┬──────────────────────────────┐
           ▼                              ▼                              ▼
┌────────────────────────┐    ┌────────────────────────┐    ┌────────────────────────┐
│ Stage 2: KPI Engine    │    │ Stage 3: ROI Model     │    │ Stage 4: BI Dashboard  │
│ • Weighted Margins     │    │ • 36-Month Projections │    │ • 9 Interactive Pages  │
│ • Cohort Retention     │    │ • 3 Scenarios          │    │ • Real-time Cross-filter│
│ • Hypothesis Testing   │    │ • Sensitivity Analysis │    │ • Executive Dark/Navy  │
└────────────────────────┘    └────────────────────────┘    └────────────────────────┘
           │                              │                              │
           └──────────────────────────────┴──────────────────────────────┘
                                          │
                                          ▼
                      ┌────────────────────────────────────────┐
                      │ Stage 5: Deliverable Generation        │
                      │ • ReportLab PDF (15 Widescreen Slides) │
                      │ • python-pptx (15 Editable Slides)     │
                      │ • 7 High-Resolution Analytical Charts   │
                      └────────────────────────────────────────┘
```

---

## 3. Modular Engineering Architecture (`src/`)

### 3.1 `src/data_cleaning.py`
Executes an idempotent, deterministic data hygiene pipeline:
- **Deduplication:** Identifies and drops identical transactions across all 16 attributes.
- **Categorical Mapping:** Dictionary-based canonical normalization eliminating casing, spacing, and punctuation variations.
- **Account-Level Hierarchical Imputation:** Retains customer-specific behavior by imputing missing values from customer history before resorting to global population statistics.
- **Typographical Error Mitigation:** Identifies data entry errors (>20 units in single retail lines) and scales to subcategory median.

### 3.2 `src/validation.py`
A 12-point automated data quality gate validating:
1. Row count completeness (exactly 11,996 rows).
2. Zero residual nulls across all required columns.
3. Strict uniqueness of `order_id`.
4. Currency and price positivity (`unit_price > 0`, `sales >= 0`).
5. Revenue arithmetic consistency: $|sales - [quantity \times unit\_price \times (1 - discount)]| < \$0.05$.
6. Profit arithmetic consistency: $|profit - [sales \times (1 - fee) - cogs]| < \$0.05$.
7. Standardized categorical domain boundaries (no orphan categories or regions).
8. Valid date bounds (2023-01-01 to 2025-12-31).

### 3.3 `src/kpi_engine.py`
Computes all authoritative financial and operational metrics:
- **Weighted Profit Margin:** Strictly computed as $\frac{\sum \text{Profit}}{\sum \text{Sales}} \times 100\%$ to avoid the classical arithmetic distortion of unweighted transaction means.
- **Cohort Retention Engine:** Tracks customer repurchase frequency across calendar years.
- **Statistical Hypothesis Testing:** Runs two-sample Welch's t-tests with unequal variance to confirm statistical significance ($p < 0.001$) of operational drivers.

### 3.4 `src/roi_model.py`
Simulates the 36-month operational rollout:
- Implements monthly cash-flow forecasting incorporating launch timing, operational ramp-up curves, Capex, and Opex.
- Enforces strict sequential double-counting protection between discount capping and marketplace margin restructuring.
- Runs multi-dimensional sensitivity sweeps across 7 key variables.

### 3.5 `src/generate_presentation.py`
Headless publication pipeline producing executive PDF and PowerPoint slide decks:
- 15 widescreen 16:9 slides designed with navy-and-slate executive styling.
- Generates 7 standalone publication-grade charts via Matplotlib.
- Populates structured data tables, KPI summary cards, risk registers, and governance roadmaps.

---

## 4. Statistical Verification & Hypotheses Testing

| Hypothesis Test | Null Hypothesis ($H_0$) | Test Type | Sample Sizes | Resulting Metric | t-Statistic | p-Value | Conclusion |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **H1: Discount Margin Bleed** | Margin with Discount $>20\%$ $\ge$ Margin with Discount $\le 20\%$ | Welch's Two-Sample t-test | $n_1=3,511$<br>$n_2=8,485$ | Mean Margin:<br>4.87% vs. 33.61% | -68.02 | $p < 0.0001$ | **Reject $H_0$**<br>Extreme margin destruction confirmed. |
| **H2: Marketplace Drag** | Marketplace Margin $\ge$ Direct Channels Margin | Welch's Two-Sample t-test | $n_1=2,660$<br>$n_2=9,336$ | Mean Margin:<br>9.64% vs. 29.63% | -41.63 | $p < 0.0001$ | **Reject $H_0$**<br>Channel fee structure significantly unviable. |
| **H3: Late Delivery Returns** | Return Rate for Late Orders $\le$ On-Time Orders | Welch's Two-Sample t-test | $n_1=2,730$<br>$n_2=9,266$ | Return Rate:<br>14.91% vs. 4.78% | +14.13 | $p < 0.0001$ | **Reject $H_0$**<br>Delivery delays strongly predict merchandise returns. |
