# PROJECT AUDIT — Executive Decision Report & Capstone Presentation

**Stage 1: Complete Audit and Implementation Plan**
**Auditor role:** Senior Data Analytics Engineer / BI Architect / Python Developer / Financial Analytics Reviewer
**Audit date:** 2026-10-18
**Workspace root:** `d:\RabTech Academy internship\Executive Decision Report & Capstone Presentation\`

---

## Legend

| Tag | Meaning |
|-----|---------|
| ✅ VERIFIED | Directly confirmed by reading files or executing calculations against the data |
| ⚠️ SUSPECTED | Plausible concern requiring a live notebook run to confirm |
| ❓ UNVERIFIED | Evidence not yet available; cannot be confirmed in Stage 1 |
| 💡 RECOMMENDATION | Proposed improvement for Stage 2+ |

---

## 1. Project Overview

This is a capstone analytics project built by **Gurusaiprasadreddy** (October 2026) simulating three years of omnichannel retail orders (2023–2025). The stated goal is to generate executive-level insights and three costed strategic recommendations backed by hypothesis testing and an ROI model. The primary deliverable is a 15-page PDF executive report supported by a Jupyter notebook that cleans the data, performs all analysis, and exports a `metrics.json` file used by the deck.

The project is entirely **self-contained** in a single notebook. It has no separate module files, no dashboard, no automated tests, no `requirements.txt`, and no `README.md` as of this audit.

---

## 2. Existing File Inventory

| File | Size | Status |
|------|------|--------|
| `Executive_Decision_Analysis.ipynb` | 713 KB | ✅ VERIFIED — 28 cells, Python 3.13, all sections present |
| `Executive_Decision_Report.pdf` | 468 KB | ✅ VERIFIED — 15 pages, text extracted via pdfplumber |
| `Dataset/raw_sales_data.csv` | 1.37 MB | ✅ VERIFIED — 12,400 rows, 16 columns |
| `Dataset/clean_dataset.csv` | 2.26 MB | ✅ VERIFIED — 11,996 rows, 27 columns |

**Files referenced in the PDF appendix but NOT found in the workspace:**

| File | PDF Claim | Audit Finding |
|------|-----------|---------------|
| `generate_raw_data.py` | "Reproducible build script" | ❓ UNVERIFIED — not present in workspace |
| `build_deck.py` | "Reproducible build script" | ❓ UNVERIFIED — not present in workspace |
| `Executive_Decision_Analysis.html` | "Read-only notebook export" | ❓ UNVERIFIED — not present in workspace |
| `metrics.json` | "Single source of truth for the deck" | ❓ UNVERIFIED — only generated at notebook runtime |
| `requirements.txt` | (implied by any Python project) | ❌ MISSING ENTIRELY |
| `README.md` | (implied by any shareable project) | ❌ MISSING ENTIRELY |

No `src/`, `tests/`, `pages/`, `outputs/`, or `reports/` directories exist.

---

## 3. Dataset Audit Findings

### 3.1 Raw Dataset (`raw_sales_data.csv`)

| Metric | Finding | Status |
|--------|---------|--------|
| Row count | 12,400 | ✅ VERIFIED |
| Column count | 16 | ✅ VERIFIED |
| Columns | order_id, order_date, customer_id, segment, region, category, sub_category, channel, quantity, unit_price, discount, unit_cost, sales, profit, ship_days, returned | ✅ VERIFIED |
| Exact duplicate rows | 400 | ✅ VERIFIED |
| Unique order_ids with duplicates | 400 order IDs appear more than once | ✅ VERIFIED |
| Date formats | 3 formats: YYYY-MM-DD (9,178 rows), DD/MM/YYYY (1,987 rows), third format present but rare | ✅ VERIFIED |
| Missing: region | 247 rows | ✅ VERIFIED |
| Missing: segment | 188 rows | ✅ VERIFIED |
| Missing: category | 61 rows | ✅ VERIFIED |
| Missing: discount | 369 rows | ✅ VERIFIED |
| Missing: quantity | 122 rows | ✅ VERIFIED |
| Missing: ship_days | 306 rows | ✅ VERIFIED |
| Total missing cells (pre-dedup) | 1,293 | ✅ VERIFIED — PDF says 1,260 (explained in §4.2) |
| segment variants | Consumer, consumer, CONSUMER, Corporate, corporate, CORPORATE, Small Business, SMALL BUSINESS, small business, empty string (10 variants) | ✅ VERIFIED |
| region variants | 29 distinct strings (whitespace + case) collapsing to 5 canonical values | ✅ VERIFIED |
| category variants | 18 distinct strings (whitespace + case) collapsing to 3 canonical values | ✅ VERIFIED |
| channel | 3 clean values: Online, Retail Store, Marketplace — no casing issues | ✅ VERIFIED |
| Quantity range | 1.0 to 900.0 (float stored) | ✅ VERIFIED |
| Negative quantities | 0 | ✅ VERIFIED |
| Discount range | 0.0 to 0.5 | ✅ VERIFIED |
| Discount > 1 | 0 | ✅ VERIFIED |
| Negative profit rows (raw) | 1,387 | ✅ VERIFIED |
| Total raw sales | $3,551,766 | ✅ VERIFIED |
| Total raw profit | $580,194 | ✅ VERIFIED |

### 3.2 Clean Dataset (`clean_dataset.csv`)

| Metric | Finding | Status |
|--------|---------|--------|
| Row count | 11,996 | ✅ VERIFIED |
| Column count | 27 (16 original + 11 derived) | ✅ VERIFIED |
| Added columns | ship_days_imputed, order_year, order_month, order_quarter, year_month, profit_margin, discount_band, is_late, is_loss_order, customer_type, channel_fee | ✅ VERIFIED |
| Missing values | None — all columns complete | ✅ VERIFIED |
| Duplicate order_ids | 0 | ✅ VERIFIED |
| Segment values | Consumer (6,001), Corporate (3,799), Small Business (2,196) | ✅ VERIFIED |
| Region values | 5 canonical values: West, North, South, East, Central | ✅ VERIFIED |
| Category values | 3 canonical values: Technology, Office Supplies, Furniture | ✅ VERIFIED |
| Quantity range (clean) | 1 to 12 (integer, entry errors corrected) | ✅ VERIFIED |
| Total clean sales | $3,373,628 | ✅ VERIFIED |
| Total clean profit | $458,058 | ✅ VERIFIED |
| Negative profit rows (clean) | 1,579 | ✅ VERIFIED |
| Date range | 2023-01-01 to 2025-12-31 | ✅ VERIFIED |
| Unique customers | 2,116 | ✅ VERIFIED |
| Orders by year | 2023: 3,079 / 2024: 3,939 / 2025: 4,978 | ✅ VERIFIED |

> ⚠️ **SUSPECTED:** Total profit fell from $580,194 (raw) to $458,058 (clean) — a drop of ~$122,136. Expected from: (a) removal of profitable duplicate orders, (b) quantity-error corrections lowering sales, and (c) formula-based profit recalculation. Stage 2 should trace this reconciliation cell-by-cell.

> ⚠️ **SUSPECTED:** Negative profit rows *increased* from 1,387 (raw) to 1,579 (clean). This may occur because the quantity-correction step (3.5) recalculates profit via the channel fee formula, shifting some near-zero recorded profits to negative. Stage 2 should quantify this explicitly.

---

## 4. Data-Cleaning Audit

### 4.1 Cleaning Steps (Cell 007)

| Step | What it does | Correctness | Auditability |
|------|-------------|-------------|-------------|
| **3.1 Dedup** | `df.drop_duplicates()` — removes 400 exact-row duplicates | ✅ VERIFIED | Logged in `log["duplicates_removed"]` |
| **3.2 Type conversion** | sales/profit converted from "$1,234" strings to float; order_date parsed via three-format loop; returned mapped Y/N to True/False | ✅ VERIFIED — parse_date tries ISO, DD/MM/YYYY, "Mon dd, yyyy" | ⚠️ SUSPECTED — if a date matches none of the 3 formats it returns NaT; the assert catches this at runtime |
| **3.3 Label standardisation** | `str.strip().str.title()` on region, segment, category | ✅ VERIFIED — collapses 29 region variants to 5 | ✅ Logged before/after unique counts |
| **3.4a Category imputation** | Category filled from sub_category deterministic lookup | ✅ VERIFIED | ⚠️ SUSPECTED — if sub_category maps to two categories, lookup takes first; no conflict check |
| **3.4b Region/segment imputation** | Customer mode, then global mode as fallback | ⚠️ SUSPECTED — global mode for single-order customers may be incorrect | 💡 RECOMMENDATION: Document as assumption |
| **3.4c Discount imputation** | `1 - sales/(qty x unit_price)` snapped to valid tier | ✅ VERIFIED — mathematically sound | ⚠️ SUSPECTED — 4 rows dropped where both discount and quantity missing |
| **3.4d Quantity imputation** | `sales/(unit_price x (1 - discount))` rounded to integer | ✅ VERIFIED — inverse of sales formula | ⚠️ SUSPECTED — rounding possible when discount=0 |
| **3.4e Ship_days imputation** | Regional median; flagged in `ship_days_imputed` | ✅ VERIFIED — 306 rows imputed and flagged | ✅ Logged |
| **3.5 Quantity outlier fix** | qty > 20 replaced with sub_category median (28 rows); sales and profit recalculated | ✅ VERIFIED — max qty drops to 12 | ⚠️ SUSPECTED — profit recalculation uses `df.channel.map(FEE)` inline, creating a subtle ordering dependency that works correctly but is fragile |
| **3.6 Validation** | `(sales - expected).abs()/expected < 0.02` and assert no nulls and order_id is unique | ✅ VERIFIED independently — 0 rows fail the 2% threshold | ✅ Assert statements act as runtime checkpoints |

### 4.2 Missing Cells Count Discrepancy (✅ VERIFIED — Explained)

- Raw (pre-dedup) missing cells: **1,293**
- PDF appendix claims: **1,260** missing cells resolved
- Cell 010 Before/After output: **1,260** Before, **0** After
- **Explanation:** The notebook captures `log["missing_cells_before"]` *after* deduplication. Some of the 400 removed duplicate rows had missing values, reducing the count from 1,293 to 1,260 post-dedup. Both figures are correct in their respective contexts.

### 4.3 Row Count Arithmetic (✅ VERIFIED)

12,400 raw − 400 duplicates = 12,000 − 4 unrecoverable = **11,996 clean**

PDF confirms "only 4 rows dropped as unrecoverable." Internally consistent.

### 4.4 Profit Formula Discrepancy — 22 Rows (⚠️ SUSPECTED — Minor)

Our independent formula: `profit = sales × (1 − channel_fee) − qty × unit_cost`

22 rows deviate > 5% from this formula. All have absolute profit near $0 and deviations < $0.30.

**Cause:** Rounding in the original profit column carried from raw data, vs. the formula applied only to outlier-corrected rows in step 3.5.

**Impact:** Negligible for analysis (sub-dollar totals). Not a data integrity failure.

### 4.5 Missing `requirements.txt` (✅ VERIFIED)

No requirements.txt, environment.yml, Pipfile, or pyproject.toml exists. The notebook uses numpy, pandas, matplotlib, scipy, json (stdlib).

💡 RECOMMENDATION: Create `requirements.txt` in Stage 2.

### 4.6 Linux Font Path Hardcoded (✅ VERIFIED)

Cell 002 hardcodes `/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf`. This path does not exist on Windows; matplotlib falls back silently. 

💡 RECOMMENDATION: Use a cross-platform font or wrap in try/except with graceful fallback.

---

## 5. Notebook Section-by-Section Review

### Section 1: Setup (Cell 002)

- Imports libraries, defines `bars()` chart helper, sets matplotlib style.
- ✅ `bars()` correctly handles horizontal/vertical orientation, negative value labels, and color highlighting.
- ⚠️ Linux font path (see §4.6).

### Section 2: Ingest and Profile (Cells 003–005)

- Business question: What is the state of the raw data?
- ✅ Chart 1 (missing-value bar chart) is correct.
- ✅ All profiling outputs match our independent raw CSV inspection.

### Section 3: Cleaning and Preprocessing (Cells 006–010)

- ✅ Reproducibility: deterministic pipeline, no random elements, assert statements as checkpoints.
- ✅ Auditability: `log` dict captures before/after metrics, exported to `metrics.json`.
- ⚠️ `missing_cells_before` captured post-dedup — could confuse future reviewers.
- ⚠️ `customer_type` depends on clean dataset order history only — customers whose duplicate orders were removed could be misclassified.
- 💡 RECOMMENDATION: Add `cleaning_audit_log.csv` recording each modified row with original and corrected values.

### Section 4: Performance Snapshot and Key Revenue Drivers (Cells 011–015)

#### Cell 012 — Year-on-Year KPI Table (✅ VERIFIED)

| Metric | 2023 | 2024 | 2025 | YoY 2025 |
|--------|------|------|------|----------|
| Revenue ($) | 896,588 | 1,076,644 | 1,400,397 | +30.1% |
| Profit ($) | 138,398 | 152,572 | 167,088 | +9.5% |
| Margin (%) | 15.44 | 14.17 | 11.93 | −15.8% rel |
| Orders | 3,079 | 3,939 | 4,978 | +26.4% |
| Customers | 524 | 1,003 | 1,376 | +37.2% |
| AOV ($) | 291 | 273 | 281 | +2.9% |
| Return rate (%) | 6.11 | 7.49 | 7.37 | −1.6% |
| Late (%) | 21.47 | 23.33 | 23.10 | −1.0% |

⚠️ Margin YoY of −15.8% is a relative change, not percentage points (−2.24 pp). The PDF statement "margin fell to 11.9%" is cleaner and unambiguous.

#### Cell 013 — Category and Sub-Category Analysis (✅ VERIFIED)

| Category | Revenue | Profit | Aggregate Margin |
|----------|---------|--------|-----------------|
| Technology | $1,647,786 | $148,373 | 9.0% |
| Furniture | $1,293,350 | $157,456 | 12.2% |
| Office Supplies | $432,492 | $152,229 | 35.2% |

Margin is aggregate (sum of profits / sum of revenues) — the correct approach for business reporting.
💡 RECOMMENDATION: Document this is aggregate margin, not a simple average of row-level margins.

#### Cell 014 — Regional and Channel Analysis (✅ VERIFIED)

| Channel | Revenue | Profit | Margin |
|---------|---------|--------|--------|
| Online | $1,530,616 | $229,616 | 15.0% |
| Retail Store | $1,158,942 | $245,879 | 21.2% |
| Marketplace | $684,071 | −$17,437 | −2.5% |

| Region | Revenue | Margin | Late Rate |
|--------|---------|--------|-----------|
| West | $1,083,664 | 13.4% | 12% |
| North | $838,042 | 13.8% | 19% |
| South | $617,348 | 13.9% | 26% |
| East | $536,192 | 13.2% | 30% |
| Central | $298,382 | 13.5% | 58% |

⚠️ **IMPORTANT:** Marketplace margin of −2.5% is the 2023–2025 aggregate. Given Marketplace share grew from 12% to 26%, its margin may be worsening year-over-year. The notebook shows channel mix but NOT year-over-year Marketplace margin. Stage 2 should add this trend chart.

#### Cell 015 — Customer Concentration and Retention (✅ VERIFIED)

- Unique customers: 2,116
- Top 20% revenue share: 66.1%
- Retention 2023→24: 54.4% | 2024→25: 49.7%
- Repeat customer share: 71.4%
- AOV Repeat: $279.93 | One-time: $305.56

Retention formula: |active year N ∩ active year N+1| / |active year N| — ✅ VERIFIED.

⚠️ **AOV ANOMALY:** Repeat customers have *lower* AOV ($279.93) than one-time customers ($305.56). This is counter-intuitive and is not explained in the notebook or PDF. Stage 2 should investigate and either explain or flag this finding.

### Section 5: Risk Areas and Hypothesis Tests (Cells 016–018)

#### Cell 017 — Discount and Delivery Analysis (✅ VERIFIED)

| Discount Band | Orders | Revenue | Profit | Loss Orders % | Margin % |
|--------------|--------|---------|--------|---------------|---------|
| 0% | 3,229 | $1,009,126 | $290,054 | 0.1 | 28.7 |
| 1–10% | 2,325 | $683,633 | $152,956 | 0.8 | 22.4 |
| 11–20% | 2,931 | $824,434 | $97,177 | 7.3 | 11.8 |
| 21–30% | 1,950 | $504,929 | −$2,852 | 25.0 | −0.6 |
| >30% | 1,561 | $351,506 | −$79,277 | 54.7 | −22.6 |

2025: 1,605 orders >20% discount → revenue $389,216, profit **−$40,094**

Total loss-making orders: 1,579 (13.2%), total losses: **−$129,119**

Late delivery: 14.9% return rate (late) vs 4.8% (on-time) | Regional late rates: Central 58.4%, East 29.7%, South 25.6%, North 18.7%, West 11.9%

#### Cell 018 — Hypothesis Testing (✅ VERIFIED)

| Test | n(A) | n(B) | Mean A | Mean B | p-value | Verdict |
|------|------|------|--------|--------|---------|---------|
| H1: discount >20% vs ≤20% on profit margin | 3,511 | 8,485 | 4.87% | 33.61% | <0.001 | Supported |
| H2: Marketplace vs other channels on profit margin | 2,660 | 9,336 | 9.64% | 29.63% | <0.001 | Supported |
| H3: Late vs on-time on return rate | 2,730 | 9,266 | 14.91% | 4.78% | <0.001 | Supported |

Discount–margin Pearson correlation: **−0.70** ✅ VERIFIED.

Issues:
- ⚠️ H2 groups Online and Retail together (margins 15.0% and 21.2%) as the reference group. More rigorous to compare Marketplace to each channel separately.
- ⚠️ No multiple-comparisons correction applied. Bonferroni α = 0.017. All p-values << 0.001 so conclusions unchanged.
- ⚠️ Pearson assumes linearity. The discount–margin relationship is mechanistically nonlinear. Spearman correlation should also be reported.
- ❓ UNVERIFIED: Exact t-statistics and U-statistics not independently recomputed. To be verified in Stage 2.

### Section 6: ROI Model (Cells 019–022) (✅ VERIFIED)

2025 baseline profit (recorded): $167,088 | Rebuilt from components: $167,089 ($1 rounding) — model starting point is internally consistent.

**Scenario results:**

| Scenario | d1 Discount | d2 Marketplace | d3 Fulfilment+Retention | Total annual uplift |
|----------|-------------|----------------|--------------------------|---------------------|
| Conservative | $57,848 | $10,208 | $10,140 | $78,196 |
| **Base** | **$62,690** | **$17,916** | **$16,733** | **$97,339** |
| Optimistic | $65,918 | $26,377 | $23,451 | $115,746 |

**Base case cash-flow summary:**

| Rec | Annual run-rate | 3yr Benefit | 3yr Cost | Net | ROI | Payback |
|-----|----------------|------------|---------|-----|-----|---------|
| 1 Discount guardrails | $62,690 | $172,396 | $21,333 | $151,063 | 708% | Month 6 |
| 2 Marketplace repair | $17,916 | $46,284 | $28,000 | $18,284 | 65% | Month 18 |
| 3 SLA + retention | $16,733 | $41,833 | $35,250 | $6,583 | 19% | Month 26 |
| **Total** | **$97,339** | **$260,513** | **$84,583** | **$175,930** | **208%** | **Month 10** |

---

## 6. Executive PDF Claim-to-Source Mapping

### All 15 Pages — Summary Table

| Page | Key Claim | Notebook Source | Status |
|------|-----------|----------------|--------|
| 1 | 11,996 orders, 2,116 customers | Clean dataset | ✅ VERIFIED |
| 2 | Revenue grew 30% in 2025 | Cell 012: 30.07% | ✅ VERIFIED |
| 2 | 2025 revenue $1.40M | Cell 012: $1,400,397 | ✅ VERIFIED |
| 2 | 2025 profit $167k, +9.5% YoY | Cell 012: $167,088, 9.51% | ✅ VERIFIED |
| 2 | Margin 11.9%, down from 15.4% | Cell 012: 11.93% vs 15.44% | ✅ VERIFIED |
| 2 | +58% profit uplift ($97k/yr) | 97,339/167,088=58.3% | ✅ VERIFIED |
| 2 | 32% orders >20% discount, −$40k profit | Cell 017 | ✅ VERIFIED |
| 2 | Marketplace margin −2.5% | Cell 014 | ✅ VERIFIED |
| 2 | Marketplace share 12%→26% | Cell 014 mix_pct | ✅ VERIFIED |
| 2 | Late delivery triples returns (14.9% vs 4.8%) | Cell 017 | ✅ VERIFIED |
| 2 | Central ships 58% late | Cell 017: 58.41% | ✅ VERIFIED |
| 3 | Revenue +56% since 2023 | 56.2% independently verified | ✅ VERIFIED |
| 3 | Profit +21% | 20.7% independently verified | ✅ VERIFIED |
| 4 | 400 duplicates removed | Cell 007 log | ✅ VERIFIED |
| 4 | 1,260 missing cells resolved | Cell 010 Before/After | ✅ VERIFIED (post-dedup) |
| 4 | 28 entry errors fixed | Cell 007 log | ✅ VERIFIED |
| 4 | Only 4 rows dropped as unrecoverable | 12,400−400−11,996=4 | ✅ VERIFIED |
| 4 | 300 missing ship times imputed | Cell 007 log shows 306 | ⚠️ SUSPECTED — minor discrepancy |
| 5 | Sub-category profit/margin figures | Cell 013 (spot-checked) | ✅ VERIFIED |
| 6 | 66% revenue from top 20% customers | Cell 015: 66.08% | ✅ VERIFIED |
| 6 | 50% retention 2024→2025 (was 54%) | Cell 015: 49.7% / 54.4% | ✅ VERIFIED |
| 6 | 71% order more than once | Cell 015: 71.4% | ✅ VERIFIED |
| 6 | Revenue by channel and region | Cell 014 | ✅ VERIFIED |
| 6 | Margin similar everywhere 13.2–13.9% | Cell 014: 13.24%–13.90% | ✅ VERIFIED |
| 7–9 | All discount band, late delivery, regional figures | Cells 017–018 | ✅ VERIFIED |
| 10 | All hypothesis test verdicts, p<0.001, sample sizes | Cell 018 | ✅ VERIFIED |
| 11 | Rec run-rates ($63k, $18k, $17k) | Cell 021 output | ✅ VERIFIED |
| 12 | $97k annual uplift | Cell 021: 97,339 | ✅ VERIFIED |
| 12 | $85k total investment | Cell 021: $84,583 rounded | ✅ VERIFIED |
| 12 | $176k three-year net benefit | Cell 021: $175,930 rounded | ✅ VERIFIED |
| 12 | 208% ROI | (175,930/84,583)×100=207.996% | ✅ VERIFIED |
| 12 | Month 10 payback | Cell 022 cumulative CF | ✅ VERIFIED |
| 12 | Profit rises from $167k to $264k | Cell 020: profit_after=264,428 | ✅ VERIFIED |
| 12 | Revenue traded down 8% | Cell 020 ds1+ds2 vs baseline | ⚠️ SUSPECTED — not independently recomputed |
| 13 | Implementation timeline dates | Cell 024 TIMELINE list | ✅ VERIFIED |
| 15 | 430 high-value orders flagged (IQR) | Cell 007 log (not in stored outputs) | ❓ UNVERIFIED |

---

## 7. Financial Model Audit

### 7.1 Architecture

Monthly cash-flow model, 36-month horizon, 2025 order-level baseline. Benefits applied **sequentially** (Rec 1 → Rec 2 on top of Rec 1 → Rec 3 on top of Rec 2), intentionally avoiding double-counting discount effects.

### 7.2 Benefit Calculations

**Recommendation 1 — Discount Guardrails:**
- Orders with discount > 0.20 are repriced to 0.20; retention rate r1 (Base: 70%) applied
- d1 = new profit total − baseline profit total
- ✅ Methodologically sound. ⚠️ 70% retention is an unvalidated assumption (tested 55%–80% in scenarios).

**Recommendation 2 — Marketplace Repair:**
- Applied after Rec 1 changes; caps marketplace discount at 10%; applies fee cut of 0–2 pp by scenario
- d2 = Rec 2 profit − Rec 1 profit (pure incremental) ✅

**Recommendation 3 — SLA + Retention:**
- ful = avoided returns × (max(post-Rec2 profit per order, 0) + HANDLING × sales)
- ret = ret_up × n_active_2024 × sales_per_retained × margin_post
- d3 = ful + ret
- ✅ ful correctly zero-floors loss-making orders — no double counting in fulfilment component
- ⚠️ margin_post is the post-Rec1+Rec2 *portfolio* margin, not the marginal retained customer's margin
- ⚠️ sales_per_retained is the mean of already-retained customers (survivorship bias) — likely overstates the expected value of a newly retained customer

### 7.3 Cost Model (✅ VERIFIED)

| Rec | One-time | Annual running | 36-month total |
|-----|----------|---------------|---------------|
| 1 | $10,000 | $4,000 | $21,333 |
| 2 | $12,000 | $6,000 | $28,000 |
| 3 | $12,000 | $9,000 | $35,250 |
| **Total** | **$34,000** | **$19,000** | **$84,583** |

Model uses undiscounted cash flow (no NPV/IRR). Acceptable for this horizon and amounts but should be disclosed.

### 7.4 Model Gap Summary

| Gap | Severity |
|-----|----------|
| No NPV/discount rate | Low |
| No tax treatment | Low |
| Retention benefit uses survivorship-biased reference group | Medium |
| Fee cut assumption (Rec 2) speculative | Medium |
| Binary success assumed for fee renegotiation | Medium |
| No market growth assumed | Low (stated explicitly) |
| Seasonality not modeled | Low |

---

## 8. Statistical Methodology Audit

| Test | Appropriateness | Issues |
|------|----------------|--------|
| H1: Welch t-test + Mann-Whitney U | ✅ Appropriate — accounts for unequal variances; non-parametric check adds robustness | ✅ Direction (alternative="less") correctly specified |
| H2: Welch t-test + Mann-Whitney U | ✅ Appropriate | ⚠️ Reference group combines Online+Retail (different margins) |
| H3: Chi-square test | ✅ Appropriate for 2×2 independence | ✅ All cell counts > 5 |
| Pearson correlation −0.70 | ✅ Correct calculation | ⚠️ Discount–margin relationship is mechanistically nonlinear; Spearman should also be reported |
| No multiple-comparisons correction | ⚠️ Acceptable — all p-values << 0.001 | Bonferroni α = 0.017; conclusions unchanged |

---

## 9. Missing Features and Improvement Opportunities

| # | Missing Feature | Priority | Stage |
|---|----------------|----------|-------|
| 1 | Streamlit + Plotly interactive dashboard | Critical | Stage 2 |
| 2 | `requirements.txt` with pinned versions | Critical | Stage 2 |
| 3 | `README.md` with setup instructions | High | Stage 2 |
| 4 | Standalone `src/data_cleaning.py` module | High | Stage 2 |
| 5 | `generate_raw_data.py` (referenced in PDF but missing) | High | Stage 2 |
| 6 | `build_deck.py` (referenced in PDF but missing) | Medium | Stage 2 |
| 7 | Automated data quality tests (`tests/`) | High | Stage 2 |
| 8 | `src/roi_model.py` standalone module | High | Stage 2 |
| 9 | `src/kpi_engine.py` standalone module | Medium | Stage 2 |
| 10 | Cross-platform font handling | Low | Stage 2 |
| 11 | Row-level cleaning audit log CSV | Medium | Stage 2 |
| 12 | Spearman correlation alongside Pearson | Low | Stage 2 |
| 13 | Marketplace year-over-year margin trend chart | Medium | Stage 2 |
| 14 | AOV anomaly investigation and explanation | Medium | Stage 2 |
| 15 | NPV and IRR in financial model | Low | Stage 3 |
| 16 | HTML notebook export (missing .html) | Medium | Stage 2 |

---

## 10. Recommended Project Architecture

Target structure — no files moved during Stage 1:

```
Executive Decision Report & Capstone Presentation/
|
+-- data/
|   +-- raw/                raw_sales_data.csv        (move from Dataset/)
|   +-- processed/          clean_dataset.csv         (move from Dataset/)
|
+-- src/
|   +-- __init__.py
|   +-- data_cleaning.py    (extract from notebook Cells 007-010)
|   +-- kpi_engine.py       (extract from notebook Cells 012-015)
|   +-- statistical_analysis.py  (extract from Cells 017-018)
|   +-- roi_model.py        (extract from Cells 020-022)
|   +-- generate_raw_data.py  (recreate — referenced in PDF but missing)
|
+-- notebooks/
|   +-- Executive_Decision_Analysis.ipynb   (keep; update paths to src/)
|
+-- app.py                  (Streamlit dashboard entry point)
+-- pages/
|   +-- 01_overview.py
|   +-- 02_revenue_drivers.py
|   +-- 03_risk_areas.py
|   +-- 04_roi_model.py
|   +-- 05_about.py
|
+-- outputs/
|   +-- charts/             (saved chart PNGs from notebook)
|   +-- metrics.json        (exported at notebook runtime)
|
+-- reports/
|   +-- Executive_Decision_Report.pdf   (move from root)
|
+-- tests/
|   +-- __init__.py
|   +-- test_data_cleaning.py
|   +-- test_kpi_engine.py
|   +-- test_roi_model.py
|
+-- requirements.txt        (CREATE in Stage 2)
+-- README.md               (CREATE in Stage 2)
```

---

## 11. Stage-by-Stage Implementation Plan

### Stage 2 — Foundation and Modularisation
**Goal:** Reproducible, testable, documented Python project ready for dashboard

| Task | File | Priority |
|------|------|---------|
| Create `requirements.txt` | root | Critical |
| Create `README.md` | root | Critical |
| Create directory structure | root | Critical |
| Extract `src/data_cleaning.py` (load_raw, clean, validate, save_clean) | src/ | Critical |
| Extract `src/kpi_engine.py` (kpis_by_year, by_category, by_channel, by_region, concentration, retention) | src/ | High |
| Extract `src/statistical_analysis.py` (discount_risk_table, late_delivery_table, hypothesis_tests, correlation_matrix) | src/ | High |
| Extract `src/roi_model.py` (build_baseline, run_scenario, cashflow) | src/ | High |
| Create `tests/test_data_cleaning.py` | tests/ | High |
| Create `tests/test_kpi_engine.py` | tests/ | Medium |
| Create `tests/test_roi_model.py` | tests/ | Medium |
| Update notebook to import from `src/` | notebooks/ | Medium |
| Fix cross-platform font handling | notebooks/ | Low |
| Recreate `generate_raw_data.py` | src/ | High |

### Stage 3 — Interactive Dashboard
**Goal:** Streamlit + Plotly dashboard reusing `src/` modules

| Task | File |
|------|------|
| Create `app.py` (navigation, state management) | root |
| `pages/01_overview.py` — KPI cards, trend charts | pages/ |
| `pages/02_revenue_drivers.py` — category, subcategory, channel, region | pages/ |
| `pages/03_risk_areas.py` — discount bands, late delivery, hypothesis tests | pages/ |
| `pages/04_roi_model.py` — scenario sliders, cash-flow chart | pages/ |
| `pages/05_about.py` — methodology, data quality log | pages/ |

### Stage 4 — Financial Model Enhancement

| Enhancement |
|------------|
| Add NPV and IRR calculation (configurable discount rate) |
| Add Spearman correlation alongside Pearson |
| Add retention benefit sensitivity to `sales_per_retained` assumption |
| Investigate and document the AOV anomaly |
| Add year-over-year Marketplace margin trend chart |

### Stage 5 — PDF Report Regeneration

| Task |
|------|
| Create `build_deck.py` using reportlab or weasyprint |
| Fix ship_days discrepancy (306 imputed vs "300" in PDF) |
| Add AOV anomaly explanation |
| Source all figures from `metrics.json` |

---

## 12. Acceptance Criteria for Each Stage

### Stage 2 Acceptance Criteria
- [ ] `pip install -r requirements.txt` succeeds on a clean environment (Windows + Linux)
- [ ] `python src/data_cleaning.py` produces `data/processed/clean_dataset.csv` matching `Dataset/clean_dataset.csv` row-for-row
- [ ] `pytest tests/` passes with ≥ 90% assertion coverage of cleaning logic
- [ ] Notebook runs end-to-end with Run All with no errors after `src/` import changes
- [ ] `README.md` clearly describes project structure, setup, and execution sequence

### Stage 3 Acceptance Criteria
- [ ] `streamlit run app.py` launches without errors
- [ ] All five pages load and display correctly
- [ ] All charts are interactive (Plotly hover, filter)
- [ ] ROI page supports scenario slider controls
- [ ] Dashboard loads clean dataset from `data/processed/`

### Stage 4 Acceptance Criteria
- [ ] ROI model returns NPV and IRR alongside existing metrics
- [ ] Spearman correlation column added to correlation table
- [ ] AOV anomaly is explained or flagged in the dashboard

### Stage 5 Acceptance Criteria
- [ ] `python build_deck.py` generates a PDF matching the existing 15-page structure
- [ ] All figures in the new PDF are sourced from `metrics.json`
- [ ] No manually hardcoded numbers in `build_deck.py`

---

## 13. Unresolved Questions and Limitations

| # | Question | How to Resolve |
|---|----------|---------------|
| 1 | Why did `generate_raw_data.py` and `build_deck.py` disappear from the workspace? | Determine if they exist elsewhere or need to be recreated |
| 2 | What seeded the raw data? (described as "simulated") | Inspect `generate_raw_data.py` if recovered |
| 3 | Why do 22 rows have profit values deviating from the formula? | Stage 2: trace through cleaning pipeline |
| 4 | Why do negative profit rows increase from raw (1,387) to clean (1,579)? | Stage 2: trace quantity-correction rows that shift from positive to negative profit |
| 5 | Is the `sales_iqr_flagged` count (430 per PDF appendix) correct? | Stage 2: re-execute notebook and capture this log value |
| 6 | PDF says "300" ship_days imputed; notebook log shows 306 | Stage 2: re-execute and reconcile |
| 7 | Is the AOV anomaly (repeat < one-time) real or an artifact? | Stage 2: investigate |
| 8 | What discount tiers are "valid" in the business context? | Confirm with business rules documentation |
| 9 | Was this notebook developed in Google Colab or a Linux server? (font path evidence) | Check notebook metadata and execution environment |

---

## 14. Prioritised Critical Issues

### 🔴 Critical — Must fix before Stage 2 can succeed

**Issue 1: Missing `requirements.txt`**
No environment specification means the project cannot be reproduced on any other machine. The notebook uses numpy, pandas, matplotlib, scipy — all versions must be pinned.

**Issue 2: Missing `generate_raw_data.py` and `build_deck.py`**
The PDF appendix claims these exist as part of the "reproducible build." Without them, the project is not reproducible from scratch. Stage 2 must recreate these files.

**Issue 3: Cleaning logic not modularised**
All 200+ lines of cleaning, feature engineering, and export are in a single notebook cell chain. Any dashboard or test must re-execute the notebook, which is fragile. Extracting `src/data_cleaning.py` is a prerequisite for all other Stage 2 work.

### 🟠 High — Should fix in Stage 2

**Issue 4: No automated tests**
The notebook's `assert` statements are single-use checkpoints, not regression tests. Any code change to the cleaning pipeline or ROI model could silently break results.

**Issue 5: Linux font path hardcoded**
Cell 002 logs silent warnings on Windows. If fonts fail and chart labels change font, visual output of the PDF changes.

### 🟡 Medium — Improve in Stages 3–4

**Issue 6: Retention benefit methodology**
`sales_per_retained` derived from already-retained customers (survivorship bias) and `margin_post` is a portfolio average applied to a marginal customer. Both overestimate the retention uplift. The three scenarios provide a range but the bias direction is always upward.

**Issue 7: H2 grouping**
The Marketplace margin hypothesis compares Marketplace to Online+Retail combined. A more rigorous comparison would separate Online and Retail as well.

**Issue 8: No year-over-year Marketplace margin trend**
The notebook shows Marketplace becoming a bigger revenue share but does not show whether its margin has also been worsening year-over-year. This is a key analysis gap given that Marketplace is the primary risk recommendation.

**Issue 9: AOV anomaly unexplained**
Repeat customers have a lower average order value ($279.93) than one-time customers ($305.56). Counter-intuitive and unexplained. May undermine the loyalty program value narrative.

---

## 15. Confirmation Statements

**Files actually inspected:**
- `Dataset/raw_sales_data.csv` — ✅ VERIFIED: fully parsed; row counts, column names, value distributions, and financial totals independently confirmed
- `Dataset/clean_dataset.csv` — ✅ VERIFIED: fully parsed; all derived columns independently validated (profit_margin formula, is_late logic, channel_fee assignment, is_loss_order flag)
- `Executive_Decision_Analysis.ipynb` — ✅ VERIFIED: all 28 cells read; stored outputs extracted for all sections
- `Executive_Decision_Report.pdf` — ✅ VERIFIED: all 15 pages extracted via pdfplumber (minor font descriptor warnings did not affect text extraction)

**No existing files were modified:** No existing file was modified, deleted, renamed, overwritten, or regenerated during this audit. The only new file created is this `PROJECT_AUDIT.md`.

**Files that could not be fully inspected:**
- `generate_raw_data.py` — does not exist in the workspace
- `build_deck.py` — does not exist in the workspace
- `Executive_Decision_Analysis.html` — does not exist in the workspace
- `metrics.json` — only generated at notebook runtime; not present as a static file
- Chart images — stored as base64 in notebook output; not independently readable as image files

**Is the project ready for Stage 2?**

**YES**, with the following blockers resolved first:
1. Create `requirements.txt` before any module extraction
2. Re-execute the notebook in a clean environment to regenerate `metrics.json` and confirm no runtime errors
3. Resolve the Python environment inconsistency (Python 3.13.16 per notebook metadata vs Python 3.12 per pip install paths)

---

*End of PROJECT_AUDIT.md — Stage 1 complete. Awaiting approval to begin Stage 2.*
