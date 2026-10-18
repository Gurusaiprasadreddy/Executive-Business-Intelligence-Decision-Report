# End-to-End Reproducibility & Technical Setup Guide

**Project:** Executive Decision Analytics BI Capstone  
**Target Platform:** Cross-Platform (Windows 10/11, macOS, Linux)  
**Target Runtime:** Python 3.12+ (tested on Python 3.12.10)  
**Build Tooling:** Standard `pip`, `pytest`, `streamlit`, `reportlab`, `python-pptx`

---

## 1. System Requirements & Environment Setup

### 1.1 Prerequisites
- Python 3.12 or newer installed and accessible on system `PATH`.
- Git installed (optional, for version control tracking).

### 1.2 Virtual Environment Initialization

#### Windows (PowerShell):
```powershell
# Create dedicated virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

#### Windows (Command Prompt):
```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
```

#### macOS / Linux (Bash / Zsh):
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 1.3 Dependency Installation
Install all pinned project dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 2. Deterministic Pipeline Execution

The analytical and deliverable generation pipeline is completely deterministic and reproducible in four distinct steps:

### Step 1: Execute Data Cleaning, KPI Engine & ROI Projections
Run the master pipeline script:
```bash
python run_pipeline.py
```
**Expected Runtime:** ~5–10 seconds.  
**Execution Outputs:**
1. `outputs/data_quality_report.csv` — 12-point data quality audit summary.
2. `outputs/financial_reconciliation.csv` — Step-by-step revenue and profit reconciliation.
3. `outputs/metrics.json` — Authoritative pre-computed KPIs and hypothesis testing statistics.
4. `outputs/candidate_clean_dataset.csv` — 11,996 clean rows matching baseline SHA256.
5. `outputs/audit/cleaning_log.csv` — Transformation audit log for every modified cell.
6. `outputs/audit/unresolved_records.csv` — Log of documented exceptions and dropped rows.
7. `outputs/roi_scenarios.csv` — Conservative, Base, and Optimistic 36-month scenario table.
8. `outputs/monthly_cash_flow.csv` — 36-month monthly cash flows across all recommendations.
9. `outputs/break_even_analysis.csv` — Discounted NPV, breakeven months, and ROI metrics.
10. `outputs/sensitivity_analysis.csv` — Multi-dimensional parameter sensitivity matrix.
11. `outputs/roi_assumptions.json` — Complete assumption repository with business citations.

### Step 2: Generate Final Executive Presentations (PDF & PPTX)
Generate the 15-slide widescreen executive presentations and high-resolution charts:
```bash
python src/generate_presentation.py
```
**Expected Runtime:** ~10–15 seconds.  
**Execution Outputs:**
1. `outputs/Executive_Decision_Report_Final.pdf` — High-resolution 16:9 PDF (ReportLab).
2. `outputs/Executive_Decision_Report_Final.pptx` — Fully editable 16:9 slide deck (python-pptx).
3. `outputs/charts/` — 7 analytical publication-ready vector/PNG charts.

### Step 3: Run the Complete Automated Test Suite
Execute the 75 automated unit and regression tests:
```bash
python -m pytest tests/ -v
```
**Expected Result:** `75 passed in ~6-8s` with 0 failures and 0 errors.

### Step 4: Launch the Interactive Streamlit BI Application
Start the multi-page BI dashboard:
```bash
streamlit run app.py
```
**Access URL:** `http://localhost:8501`

---

## 3. Cryptographic Verification of Protected Assets

To guarantee data integrity and strict reproducibility, verify the SHA256 hashes of the four protected baseline assets:

```python
import hashlib

files = {
    'Dataset/raw_sales_data.csv': '1685e689491bd2d4751528030de2bd05ec85408578ef1de1f42c449b02172b83',
    'Dataset/clean_dataset.csv': '295e02511af8d63b537bb309b1cecf7181694bad28cd4ed362e38e58f1183a8e',
    'Executive_Decision_Analysis.ipynb': '7a3492db63e0af455fe033e55179fa4c4cecddeb01d9b628dfdf3d59c2346d44',
    'Executive_Decision_Report.pdf': 'dc9fca22868b985864eff1da83cd15b2a22779f3f1b5d210cf71a2e2154bfdbc'
}

for path, expected in files.items():
    actual = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    assert actual == expected, f"Hash mismatch in {path}!"
print("All protected baseline assets verified 100% intact!")
```

---

## 4. Troubleshooting & Common Pitfalls

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'pptx'` | Missing dependency in active environment | Run `pip install python-pptx==1.0.2` or reinstall via `requirements.txt`. |
| `RuntimeError: Matplotlib GUI error` | Non-headless backend configured in headless CLI | The code explicitly uses `matplotlib.use('Agg')` in `src/generate_presentation.py`. Ensure this remains untouched. |
| `Streamlit Port 8501 in use` | Another instance of Streamlit is running | Launch on an alternate port: `streamlit run app.py --server.port 8502`. |
| `PermissionError on PDF/PPTX overwrite` | Deliverable files are currently open in Adobe Acrobat or PowerPoint | Close the open viewer window and re-run `python src/generate_presentation.py`. |
| PowerShell Execution Policy error on `.venv` | Windows restricts unsigned script execution | Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` in PowerShell. |
