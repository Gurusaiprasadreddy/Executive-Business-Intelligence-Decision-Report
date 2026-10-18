# Data Dictionary & Schema Documentation

**Project:** Executive Decision Analytics BI & Capstone Portfolio  
**Source Dataset:** Retail E-Commerce Sales & Profitability Dataset  
**Reporting Period:** January 1, 2023 – December 31, 2025 (3 Full Calendar Years)  
**Data Nature Disclosure:** Synthetically modeled and augmented e-commerce transaction data designed for executive BI architecture, diagnostic profitability auditing, and decision modeling.

---

## 1. Pipeline Dataset Summary

| Dataset Stage | File Path | Record Count | Column Count | Total Revenue ($) | Total Profit ($) | SHA256 Checksum |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Raw Uncleaned** | `Dataset/raw_sales_data.csv` | 12,400 | 16 | $4,112,441.88 | $652,660.61 | `1685e689491bd2d4751528030de2bd05ec85408578ef1de1f42c449b02172b83` |
| **Clean Baseline** | `Dataset/clean_dataset.csv` | 11,996 | 27 | $3,373,628.44 | $458,057.99 | `295e02511af8d63b537bb309b1cecf7181694bad28cd4ed362e38e58f1183a8e` |
| **Clean Candidate** | `outputs/candidate_clean_dataset.csv`| 11,996 | 27 | $3,373,628.44 | $458,057.99 | Recomputed deterministically by `run_pipeline.py` |

---

## 2. Raw Schema (16 Original Fields)

| Field Name | Raw Data Type | Target Data Type | Null Count | Description & Ingestion Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `order_id` | String | String | 0 | Unique transaction identifier (e.g., `ORD-2023-10001`). Format validated via regex. |
| `order_date` | String | `datetime64[ns]` | 0 | Order placement date (mixed formats `YYYY-MM-DD`, `DD/MM/YYYY`, `MM-DD-YYYY`). Coerced to ISO-8601. |
| `customer_id` | String | String | 0 | Unique customer account key (e.g., `CUST-1001`). Used for customer-level cohorting. |
| `customer_name`| String | String | 0 | Full customer contact name. |
| `segment` | String | Categorical | 180 | Customer business tier (`Consumer`, `Corporate`, `Home Office`). Standardized from 9 case/alias variants. |
| `region` | String | Categorical | 240 | Geographic operating territory (`North`, `South`, `East`, `West`, `Central`). Standardized from 29 noisy variants. |
| `channel` | String | Categorical | 0 | Sales acquisition channel (`Online`, `Retail Store`, `Marketplace`). |
| `category` | String | Categorical | 60 | Top-level product category (`Furniture`, `Office Supplies`, `Technology`). Standardized from 18 variants. |
| `sub_category` | String | String | 0 | Granular merchandise grouping (17 distinct categories: e.g., Chairs, Binders, Phones). |
| `product_id` | String | String | 0 | Merchandise SKU identifier. |
| `unit_price` | String/Float | `float64` | 0 | Retail list price per unit before discounts. Currency symbols stripped ($). Must be > 0. |
| `quantity` | Float/Int | `int64` | 116 | Number of units ordered in line item. Corrected for typographical outliers (>20 units). |
| `discount` | String/Float | `float64` | 356 | Contractual discount rate as decimal [0.00 – 0.70]. Stripped of `%` signs. |
| `sales` | Float | `float64` | 0 | Gross recognized transaction value: `quantity * unit_price * (1 - discount)`. |
| `profit` | Float | `float64` | 0 | Net recognized line-item contribution profit after unit costs and platform commissions. |
| `ship_days` | Float/Int | `int64` | 300 | Fulfillment turnaround in elapsed calendar days between order and delivery confirmation. |

---

## 3. Clean Dataset Engineered Fields (11 Added Fields)

| Engineered Field | Data Type | Formula / Business Logic | Analytical Purpose |
| :--- | :--- | :--- | :--- |
| `order_year` | `int64` | `order_date.dt.year` | Annual aggregation (2023, 2024, 2025). |
| `order_month` | `int64` | `order_date.dt.month` | Monthly seasonality and run-rate modeling. |
| `order_year_month` | String | `order_date.dt.to_period('M')` | Time-series forecasting and monthly run-rate trend tracking. |
| `channel_fee_pct` | `float64` | Fixed mapping: `Marketplace` = 0.13 (13%), `Online` = 0.03 (3%), `Retail Store` = 0.00 (0%). | Platform acquisition fee structure auditing. |
| `channel_fee_amt` | `float64` | `sales * channel_fee_pct` | Dollar drag paid to channel platforms. |
| `cogs` | `float64` | `sales * (1 - channel_fee_pct) - profit` | Reconstructed Cost of Goods Sold per transaction. |
| `unit_cost` | `float64` | `cogs / quantity` | Underlying manufacturing / procurement unit cost. |
| `profit_margin` | `float64` | `(profit / sales) * 100` | Unweighted transaction-level profit margin percentage. |
| `discount_band` | Categorical | `0%`, `1-10%`, `11-20%`, `21-30%`, `>30%` | Stratification for discount governance and bleed auditing. |
| `is_late` | Boolean | `ship_days > 5` | Service Level Agreement (SLA) violation flag. |
| `is_returned` | Boolean | `ship_days > 5` probabilistic return model / status | Return rate attribution linked to delivery delays. |

---

## 4. Cleaning Rules & Data Transformation Specifications

### 4.1 Exact Duplicate Elimination
- **Rule:** Full duplicate elimination across all 16 raw transaction columns.
- **Impact:** 400 redundant records removed (-$185,341.10 revenue, -$36,702.15 profit).
- **Audit:** Eliminates double-counted billing without altering legitimate multi-item single customer baskets.

### 4.2 Text Normalization & Categorical Standardization
- **Region:** 29 raw variants (e.g., `north`, `North-Region`, `N.`, `CENTRAL`) mapped to 5 standard regions: `North`, `South`, `East`, `West`, `Central`.
- **Segment:** 9 raw variants mapped to 3 standard tiers: `Consumer`, `Corporate`, `Home Office`.
- **Category:** 18 raw variants mapped to 3 standard categories: `Furniture`, `Office Supplies`, `Technology`.

### 4.3 Missing Value Imputation Hierarchy
1. **Categorical Attributes (`segment`, `region`):**
   - Imputed via **Customer Account Mode** (prior transactions by same `customer_id`).
   - If customer has no prior history, imputed via **Global Mode** (e.g., `Consumer` segment, `West` region).
2. **Category:**
   - Imputed via **Sub-Category Lookup Table** (deterministic mapping from `sub_category`).
3. **Numerical Attributes (`discount`, `quantity`):**
   - Imputed via **Sub-Category Median**.
4. **Fulfillment Turnaround (`ship_days`):**
   - Imputed via **Regional Median Shipping Days**.

### 4.4 Unrecoverable Records Policy
- **Rule:** Records missing *both* `quantity` AND `discount` cannot be mathematically reconciled against `sales` and `profit` without introducing circular bias.
- **Action:** 4 unrecoverable records permanently dropped (`ORD-2023-10412`, `ORD-2024-10891`, `ORD-2024-11204`, `ORD-2025-12190`).
- **Revenue Impact:** -$1,123.56 (-0.03% of total revenue).

### 4.5 Outlier Capping & Typographical Correction
- **Quantity Typographical Errors:** 28 records exhibited entered quantities exceeding 20 units (including erroneous entries up to 900 units). Corrected to the subcategory median quantity.
- **Revenue/Profit Impact:** -$552,348.78 revenue, -$157,611.57 profit adjusted.
- **Price Outliers:** Unit price outliers verified against merchandise subcategories; retained to preserve legitimate premium enterprise purchases.
