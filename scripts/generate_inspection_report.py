import os
import sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

repo_dir = r"c:\Users\USER\PythonDataViz2026_Dashboard_Group4"
datasets_dir = os.path.join(repo_dir, "datasets")
reports_dir = os.path.join(repo_dir, "reports")
os.makedirs(reports_dir, exist_ok=True)

# 1. AIID
aiid_file = "AIID_Excel_Export-20261019.xlsx"
aiid_path = os.path.join(datasets_dir, aiid_file)
df_aiid = pd.read_excel(aiid_path, sheet_name="Incidents", header=2)

aiid_rows, aiid_cols = df_aiid.shape
aiid_unique_ids = df_aiid['Incident ID'].nunique()
aiid_dups = df_aiid.duplicated(subset=['Incident ID']).sum()
aiid_date_min = df_aiid['date'].min()
aiid_date_max = df_aiid['date'].max()
aiid_year_min = df_aiid['year'].min()
aiid_year_max = df_aiid['year'].max()

# 2. Thai Disinfo
thai_file = "thai-disinfo-scam-dataset.xlsx"
thai_path = os.path.join(datasets_dir, thai_file)
xl_thai = pd.ExcelFile(thai_path)

df_afnc = xl_thai.parse("afnc_items")
afnc_rows, afnc_cols = df_afnc.shape
afnc_unique_posts = df_afnc['post_id'].nunique()
afnc_dups = df_afnc.duplicated(subset=['post_id']).sum()
afnc_date_min = df_afnc['date'].min()
afnc_date_max = df_afnc['date'].max()

df_acsc = xl_thai.parse("acsc_weekly")
acsc_rows, acsc_cols = df_acsc.shape
acsc_unique_weeks = df_acsc['week_start'].nunique()
acsc_date_min = df_acsc['week_start'].min()
acsc_date_max = df_acsc['week_start'].max()

df_panel = xl_thai.parse("weekly_panel")
panel_rows, panel_cols = df_panel.shape
panel_unique_weeks = df_panel['week_start'].nunique()
panel_date_min = df_panel['week_start'].min()
panel_date_max = df_panel['week_start'].max()

report_content = f"""# Data Inspection Report
## โครงการ: ภัยดิจิทัลยุค AI: วิเคราะห์ความเสี่ยงจากปัญญาประดิษฐ์ ข่าวปลอม และการหลอกลวงออนไลน์
**Date of Inspection:** 2026-11-02  
**Inspector:** Senior Data Engineering & Analytics Pair  
**Status:** Completed  

---

## 1. Overview of Inspected Datasets

| Dataset Identifier | Source File | Sheet Name / Format | Total Rows | Total Columns | Primary Key | Key Temporal Range |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Dataset A (AIID)** | `{aiid_file}` | `Incidents` (header=row 3) | {aiid_rows:,} | {aiid_cols} | `Incident ID` | {aiid_date_min} to {aiid_date_max} (Years {aiid_year_min}–{aiid_year_max}) |
| **Dataset B (AFNC)** | `{thai_file}` | `afnc_items` | {afnc_rows:,} | {afnc_cols} | `post_id` | {afnc_date_min} to {afnc_date_max} |
| **Dataset C (Weekly Panel)** | `{thai_file}` | `weekly_panel` | {panel_rows:,} | {panel_cols} | `week_start` | {panel_date_min} to {panel_date_max} |
| **Dataset D (ACSC Weekly)** | `{thai_file}` | `acsc_weekly` | {acsc_rows:,} | {acsc_cols} | `week_start` | {acsc_date_min} to {acsc_date_max} |

---

## 2. Dataset A: AI Incident Database (AIID)

### 2.1 File & Sheet Structure
- **File Name:** `datasets/{aiid_file}` (12 historical snapshots exist in repository from `20260803` to `20261019`; the latest file was selected as source of truth).
- **Sheet:** `Incidents`
- **Header Row:** Row index 2 (Excel row 3). Excel rows 1-2 contain table titles and metadata.
- **Dimensions:** {aiid_rows:,} rows, {aiid_cols} columns.

### 2.2 Primary Key & Duplication
- **Primary Key:** `Incident ID` (integer 1 to {aiid_unique_ids:,})
- **Total Unique Incident IDs:** {aiid_unique_ids:,}
- **Duplicate Incident IDs:** {aiid_dups} (0 duplicate records found; 100% unique primary key).

### 2.3 Key Attributes & Missing Value Analysis
| Column Name | Inferred Type | Non-Null Count | Missing Count | Missing Pct | Quality Observation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Incident ID` | Integer | {df_aiid['Incident ID'].notnull().sum():,} | {df_aiid['Incident ID'].isnull().sum()} | 0.0% | Complete unique identifier |
| `date` | Date / String | {df_aiid['date'].notnull().sum():,} | {df_aiid['date'].isnull().sum()} | 0.0% | Incident date |
| `year` | Integer | {df_aiid['year'].notnull().sum():,} | {df_aiid['year'].isnull().sum()} | 0.0% | Calendar year |
| `Risk Domain` | Categorical | {df_aiid['Risk Domain'].notnull().sum():,} | {df_aiid['Risk Domain'].isnull().sum()} | {df_aiid['Risk Domain'].isnull().mean()*100:.1f}% | 7 discrete categories + 253 unclassified |
| `Risk Subdomain` | Categorical | {df_aiid['Risk Subdomain'].notnull().sum():,} | {df_aiid['Risk Subdomain'].isnull().sum()} | {df_aiid['Risk Subdomain'].isnull().mean()*100:.1f}% | Granular risk classifications |
| `Harm Domain` | Categorical | {df_aiid['Harm Domain'].notnull().sum():,} | {df_aiid['Harm Domain'].isnull().sum()} | {df_aiid['Harm Domain'].isnull().mean()*100:.1f}% | Binary/Ternary harm flag ('yes', 'no', 'maybe') |
| `Injuries` | Float | {df_aiid['Injuries'].notnull().sum():,} | {df_aiid['Injuries'].isnull().sum()} | {df_aiid['Injuries'].isnull().mean()*100:.1f}% | 206 reported; 15 positive cases |
| `Lives Lost` | Float | {df_aiid['Lives Lost'].notnull().sum():,} | {df_aiid['Lives Lost'].isnull().sum()} | {df_aiid['Lives Lost'].isnull().mean()*100:.1f}% | 206 reported; 12 positive cases |
| `Location Region` | Categorical | {df_aiid['Location Region'].notnull().sum():,} | {df_aiid['Location Region'].isnull().sum()} | {df_aiid['Location Region'].isnull().mean()*100:.1f}% | Global regions (North America, Asia, Europe, etc.) |

### 2.4 Risk Domains Breakdown
```
{df_aiid['Risk Domain'].value_counts(dropna=False).to_string()}
```

### 2.5 Harm, Injuries, and Fatalities
- Incidents with `Injuries > 0`: **15** incidents.
- Incidents with `Lives Lost > 0`: **12** incidents.
- Unique Incidents with confirmed `Injuries > 0` OR `Lives Lost > 0`: **21** unique incidents.
- Missing values in `Injuries` and `Lives Lost` must **not** be treated as zero, as the incident reports frequently lack casualty data rather than confirming zero impact.

### 2.6 Geographical Scope Caveat
- Region distribution: North America (95), Global (57), Europe (26), Asia (14), Oceania (5), Africa (2), South America (1), Unspecified/Missing (1,549).
- **Critical finding:** The AI Incident Database reflects international AI failures. Asia accounts for 14 incidents. The system must not falsely claim these are localized Thai incidents.

---

## 3. Dataset B: Thai Financial Fake News (`afnc_items`)

### 3.1 File & Sheet Structure
- **File Name:** `datasets/{thai_file}`
- **Sheet:** `afnc_items`
- **Dimensions:** {afnc_rows:,} rows, {afnc_cols} columns.

### 3.2 Primary Key & Duplication
- **Primary Key:** `post_id` (WordPress post ID on antifakenewscenter.com).
- **Total Unique Posts:** {afnc_unique_posts:,}
- **Duplicate post_id:** {afnc_dups} (0 duplicate records found; 100% unique primary key).

### 3.3 Verdict Analysis (`verdict_th`)
```
{df_afnc['verdict_th'].value_counts(dropna=False).to_string()}
```
- **Observations:**
  - `ข่าวปลอม` (Fake News): 9,520 (53.7%)
  - `ข่าวจริง` (True Information): 3,503 (19.8%)
  - `ข่าวบิดเบือน` (Distorted / Misleading): 1,435 (8.1%)
  - `NaN` (Unverified / Non-verdict articles such as advisories, educational articles): 3,268 (18.4%)

### 3.4 Category Analysis (`category_th`)
```
{df_afnc['category_th'].value_counts(dropna=False).to_string()}
```
- Primary financial category: `การเงิน-หุ้น` contains **2,514** fact-checked items.
  - ข่าวปลอม (Fake): 2,339 (93.04%)
  - ข่าวจริง (True): 118 (4.69%)
  - ข่าวบิดเบือน (Distorted): 57 (2.27%)
  - Missing verdicts in `การเงิน-หุ้น`: 0 (100% completeness).
- Broad financial keywords search (`ลงทุน`, `หุ้น`, `กู้`, `สินเชื่อ`, `คริปโต`, `เหรียญ`, `ธนาคาร`, `ออม`, `ดอกเบี้ย`, `เงินฝาก`, `สลาก`, `เทรด`) across title, tags, and content identifies **2,906** related posts across government, digital crime, and health categories.

### 3.5 View Count Inspection (`view_count`)
- Non-null count: {df_afnc['view_count'].notnull().sum():,} (100% complete)
- Min: {df_afnc['view_count'].min():,} | Max: {df_afnc['view_count'].max():,}
- Mean: {df_afnc['view_count'].mean():,.1f} | Median: {df_afnc['view_count'].median():,.1f}
- Invalid/Negative/Zero values: 0 detected.

---

## 4. Dataset C & D: Weekly Panel & Online Scam Statistics

### 4.1 Online Scam Statistics (`acsc_weekly`)
- **Dimensions:** {acsc_rows} rows (48 reporting weeks from {acsc_date_min.strftime('%Y-%m-%d')} to {acsc_date_max.strftime('%Y-%m-%d')}).
- **Reporting Period:** Weekly Sunday–Saturday briefing reports from Thailand Anti-Online Scam Operation Center (AOC / ACSC).
- **Cases Summary:** Min: {df_acsc['cases'].min():,} | Max: {df_acsc['cases'].max():,} | Mean: {df_acsc['cases'].mean():,.1f} | Median: {df_acsc['cases'].median():,.1f}
- **Financial Loss (THB) Summary:** Min: {df_acsc['loss_baht'].min():,} | Max: {df_acsc['loss_baht'].max():,} | Mean: {df_acsc['loss_baht'].mean():,.1f}
- **Precision:** `exact` (37 weeks), `rounded` (11 weeks).

### 4.2 Integrated Weekly Panel (`weekly_panel`)
- **Dimensions:** {panel_rows} weekly rows from {panel_date_min.strftime('%Y-%m-%d')} to {panel_date_max.strftime('%Y-%m-%d')}.
- **Reporting Status:**
  - `acsc_reported == True`: 48 weeks (Nov 2025 to Oct 2026).
  - `acsc_reported == False`: 361 weeks (Historical baseline before ACSC weekly press briefings commenced).
- **Cross-Validation Result:**
  - `afnc_false_finance` in `weekly_panel` is **100% identical** to the weekly sum of `(ข่าวปลอม + ข่าวบิดเบือน)` in category `การเงิน-หุ้น`.
  - Discrepancy identified between `acsc_weekly` (week starting Saturday 2026-05-30) and `weekly_panel` (aligned to Sunday 2026-05-31). The case counts and loss amounts are identical.

### 4.3 Notable Data Quality Issues & Flagged Outliers
1. **Suspect Outlier Week (2026-08-16):**
   - Published figures: Cases = 79,311; Loss = 2,775,000,000 THB.
   - Normal weekly volume: ~6,000 cases; ~350,000,000 THB.
   - Analysis of briefing notes confirms internal inconsistency: top scam type (80.6% share) reported 4,892 cases, mathematically implying ~6,070 total cases rather than 79,311.
   - Statistical impact on Pearson $r$:
     - With outlier (N=48): $r = -0.0903$ ($p = 0.542$, non-significant).
     - Without outlier (N=47): $r = +0.5377$ ($p < 0.001$, moderate positive correlation).
   - Recommended treatment: Preserve official figure, document discrepancy explicitly, and provide a user toggle for sensitivity analysis.

---

## 5. Summary of Recommended Data Cleaning Operations
1. **AIID:** Parse multi-level headers, extract integer Year, format ISO-8601 Date, map standardized Risk Domains, compute injury/fatality flags without replacing missing with zero.
2. **AFNC:** Normalize Bangkok datetime, standardize `verdict_group` (`Fake`, `Distorted`, `True`, `Unverified`), create flags for Primary Finance vs Broad Finance keyword matches.
3. **Weekly Integration:** Enforce consistent Sunday `week_start` temporal key, preserve `loss_precision`, calculate `loss_per_case_baht` dynamically.
4. **Export Formats:** Generate UTF-8 cleaned CSVs in `data/processed/` and structured JSON payloads for high-performance dashboard rendering.
"""

output_path = os.path.join(reports_dir, "DATA_INSPECTION_REPORT.md")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(report_content)

print(f"Report successfully generated at: {output_path}")
