# Financial Modeling & ROI Methodology Documentation

**Module:** `src/roi_model.py`  
**Artifacts Generated:** `outputs/roi_scenarios.csv`, `outputs/monthly_cash_flow.csv`, `outputs/break_even_analysis.csv`, `outputs/sensitivity_analysis.csv`, `outputs/roi_assumptions.json`  
**Reporting Horizon:** 36 Months (Monthly Granularity)  
**Cost of Capital (WACC):** 10.0% Annual Discount Rate (0.833% Monthly)

---

## 1. Executive Financial Summary (Audited Baseline & Scenario Outputs)

The financial engine evaluates three interrelated strategic interventions over a 36-month operational horizon. All calculations distinguish between **gross revenue**, **contribution profit**, **one-time implementation capital expenditure (Capex)**, and **recurring operating expenses (Opex)**.

### Audited 36-Month Scenario Comparison Table

| Metric | Conservative Scenario | Base Case Scenario | Optimistic Scenario | Reconciliation Source |
| :--- | :--- | :--- | :--- | :--- |
| **Annual Steady-State Revenue Delta** | +$52,969.71 | **+$110,370.55** | +$165,783.68 | `outputs/roi_scenarios.csv` |
| **Annual Steady-State Profit Uplift** | +$82,453.73 | **+$102,997.42** | +$121,792.14 | `outputs/roi_scenarios.csv` |
| **One-Time Implementation Capex** | $40,800.00 | **$34,000.00** | $30,600.00 | `outputs/roi_scenarios.csv` |
| **Annual Recurring Operating Costs (Opex)**| $22,799.95 | **$18,999.96** | $17,099.96 | `outputs/roi_scenarios.csv` |
| **36-Month Cumulative Total Cost** | $99,699.86 | **$86,249.88** | $77,624.89 | `outputs/monthly_cash_flow.csv` |
| **36-Month Cumulative Net Cash Benefit** | +$119,554.59 | **+$200,722.56** | +$256,068.11 | `outputs/monthly_cash_flow.csv` |
| **36-Month Net ROI (%)** | **119.91%** | **232.72%** | **329.88%** | `outputs/roi_scenarios.csv` |
| **Discounted Net Present Value (NPV @ 10%)**| **$99,444.20** | **$168,399.10** | **$215,649.30** | `outputs/break_even_analysis.csv` |
| **Portfolio Payback Period** | **Month 12** | **Month 8** | **Month 5** | `outputs/break_even_analysis.csv` |

---

## 2. Core Financial Metrics & Conventions

### 2.1 Net Cash Flow & Net Benefit
For each month $t \in [1, 36]$:
$$\text{Net Cash Flow}_t = \text{Incremental Contribution Profit}_t - \text{Total Cost}_t$$
where $\text{Total Cost}_t = \text{Capex}_t + \text{Opex}_t$.

The 36-month Net Cash Benefit is the undiscounted sum:
$$\text{Net Benefit}_{36\text{M}} = \sum_{t=1}^{36} \text{Net Cash Flow}_t$$

### 2.2 Return on Investment (ROI)
$$\text{Net ROI (\%)} = \left( \frac{\text{Cumulative 36-Month Net Cash Benefit}}{\text{Cumulative 36-Month Total Cost}} \right) \times 100\%$$
*Note: Net ROI expresses net profit after all capital and operating costs have been recovered (e.g., 232.72% net ROI represents $3.33 in total value created per $1.00 invested).*

### 2.3 Net Present Value (NPV)
Calculated using the conservative standard end-of-period monthly discounting convention:
$$\text{NPV} = \sum_{t=1}^{36} \frac{\text{Net Cash Flow}_t}{\left(1 + \frac{r}{12}\right)^t}$$
where $r = 0.10$ (10.0% annual WACC), yielding **$168,399.10** for the Base Case portfolio.

### 2.4 Payback Period
The exact first calendar month $t \in [1, 36]$ at which cumulative undiscounted cash flow turns non-negative:
$$\text{Payback Month} = \min \left\{ t \in [1, 36] \;\middle|\; \sum_{i=1}^t \text{Net Cash Flow}_i \ge 0 \right\}$$
If cumulative net cash flow remains negative throughout all 36 months, payback is reported as `Never (>36m)`.

---

## 3. Detailed Recommendation Breakdown (Base Scenario)

### Recommendation 1: Discount Guardrails & Loss Prevention
* **Mechanism:** Institute a strict 20% maximum discount cap and eliminate negative-margin pricing. High-discount volume (>20% discount) is constrained while capturing pricing lift.
* **Launch Timing:** Launch at Month 2; 3-month ramp-up (reaches 100% steady state by Month 5).
* **Assumptions:** Order retention rate of 85.0% on constrained volume; recaptured loss margin of $79,277/yr.
* **Financial Outputs:**
  * Annual Profit Uplift: **$66,331.86**
  * One-Time Capex: **$10,000.00** | Annual Opex: **$3,999.96**
  * 36-Month Total Cost: **$21,999.88**
  * 36-Month Net Cash Benefit: **$171,468.04**
  * Standalone ROI: **779.40%** | Standalone Payback: **Month 3**

### Recommendation 2: Marketplace Margin Repair
* **Mechanism:** Renegotiate channel partner take-rate from 13.0% down to 10.0% (-300 bps) and establish price parity (+3.0% price adjustment on external marketplaces).
* **Double-Counting Guard:** Computed strictly on post-Rec 1 clean Marketplace baseline ($625,110 annual GMV), preventing phantom savings on volume already reduced by discount caps.
* **Launch Timing:** Launch at Month 4; 4-month partner transition ramp-up.
* **Financial Outputs:**
  * Annual Profit Uplift: **$29,352.04**
  * One-Time Capex: **$12,000.00** | Annual Opex: **$6,000.00**
  * 36-Month Total Cost: **$29,000.00**
  * 36-Month Net Cash Benefit: **$48,049.10**
  * Standalone ROI: **165.69%** | Standalone Payback: **Month 12**

### Recommendation 3: Delivery SLA & Customer Retention
* **Mechanism:** Enforce 3-day carrier SLAs in Central and East regions, backed by regional 3PL micro-fulfillment centers.
* **Launch Timing:** Launch at Month 6; 6-month logistics ramp-up.
* **Financial Outputs:**
  * Annual Profit Uplift: **$7,313.52**
  * One-Time Capex: **$12,000.00** | Annual Opex: **$9,000.00**
  * 36-Month Total Cost: **$35,250.00**
  * 36-Month Net Cash Benefit: **-$18,794.58** (Deficit)
  * Standalone ROI: **-53.32%** | Standalone Payback: **Never (>36m)**

---

## 4. Key Strategic Insight: Customer Contagion & Rec 3 Justification

### 4.1 The Customer Contagion Risk (Rec 1)
Cohort analysis proves that **94.95% of orders originate from repeat customers**, who generate **66.08% of total revenue**. A blunt policy that aggressively cancels accounts purchasing at discount risks "customer contagion"—alienating high-LTV clients who purchase profitably across other product lines. Hence, Recommendation 1 models an 85% order retention guardrail rather than customer termination.

### 4.2 Standalone Deficit vs. Strategic Justification (Rec 3)
In isolation, Recommendation 3 generates an annual steady-state profit uplift of $7,313.52 against $9,000.00 in annual recurring Opex and $12,000.00 in initial Capex. Consequently, **Rec 3 produces a 36-month net cash deficit of -$18,794.58 and never breaks even independently in the Base Case**.

**Executive Recommendation:** Rec 3 must NOT be launched at full scale without modification. Management must choose between:
1. **Targeted Pilot:** Constrain carrier SLA renegotiation exclusively to high-margin Technology deliveries in the Central region (where late rate is 58.41%).
2. **Cost Restructuring:** Restructure third-party logistics agreements to keep ongoing Opex under $5,000/year.
3. **Cross-Subsidization:** Treat Rec 3 as a customer retention hedge funded by the surplus cash flow of Rec 1 ($171,468 net benefit).

---

## 5. Sensitivity Analysis Across 7 Critical Dimensions

Sensitivity testing evaluated the robustness of the Base Case portfolio across $\pm20\%$ parameter shocks:

| Sensitivity Dimension | Base Value | Low Value | High Value | Portfolio 36M Net Benefit Range | Sensitivity Impact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Order Retention (Rec 1)** | 85.0% | 70.0% | 95.0% | $189,410 to $208,264 | Moderate; strong floor due to eliminated losses |
| **Marketplace Fee Cut (Rec 2)** | 3.0% | 1.5% | 4.5% | $176,144 to $225,301 | Linear; each 1% fee cut = ~$16.4k net cash |
| **Customer Retention (Rec 3)** | +3.0% | +1.0% | +5.0% | $189,842 to $211,603 | Low direct margin; high strategic value |
| **Delivery Late Rate Drop** | -10.0% | -5.0% | -15.0% | $196,930 to $204,515 | Moderate; reduces return processing friction |
| **Return Cost per Unit** | $15.00 | $10.00 | $20.00 | $198,189 to $203,256 | Low sensitivity on overall portfolio |
| **Implementation Capex** | 1.0x ($34k)| 0.8x ($27.2k)| 1.2x ($40.8k)| $207,523 to $193,923 | Low risk; capex absorbed within 8 months |
| **Launch Delay Shock** | 0 months | +2 months | +4 months | $182,590 to $200,723 | Payback extends from Month 8 to Month 11 |

*Conclusion:* In all 7 sensitivity stress tests, the overall portfolio remains substantially profitable with Net ROI exceeding 180% and positive discounted NPV.
