# Data Inspection Report
## โครงการ: ภัยดิจิทัลยุค AI: วิเคราะห์ความเสี่ยงจากปัญญาประดิษฐ์ ข่าวปลอม และการหลอกลวงออนไลน์
**Date of Inspection:** 2026-11-02  
**Inspector:** Senior Data Engineering & Analytics Pair  
**Status:** Completed  

---

## 1. Overview of Inspected Datasets

| Dataset Identifier | Source File | Sheet Name / Format | Total Rows | Total Columns | Primary Key | Key Temporal Range |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Dataset A (AIID)** | `AIID_Excel_Export-20261019.xlsx` | `Incidents` (header=row 3) | 1,749 | 59 | `Incident ID` | 1983-09-26 00:00:00 to 2026-10-07 00:00:00 (Years 1983–2026) |
| **Dataset B (AFNC)** | `thai-disinfo-scam-dataset.xlsx` | `afnc_items` | 17,726 | 18 | `post_id` | 2019-01-05 to 2026-10-31 |
| **Dataset C (Weekly Panel)** | `thai-disinfo-scam-dataset.xlsx` | `weekly_panel` | 409 | 27 | `week_start` | 2018-12-30 00:00:00 to 2026-10-25 00:00:00 |
| **Dataset D (ACSC Weekly)** | `thai-disinfo-scam-dataset.xlsx` | `acsc_weekly` | 48 | 18 | `week_start` | 2025-11-09 00:00:00 to 2026-10-18 00:00:00 |

---

## 2. Dataset A: AI Incident Database (AIID)

### 2.1 File & Sheet Structure
- **File Name:** `datasets/AIID_Excel_Export-20261019.xlsx` (12 historical snapshots exist in repository from `20260803` to `20261019`; the latest file was selected as source of truth).
- **Sheet:** `Incidents`
- **Header Row:** Row index 2 (Excel row 3). Excel rows 1-2 contain table titles and metadata.
- **Dimensions:** 1,749 rows, 59 columns.

### 2.2 Primary Key & Duplication
- **Primary Key:** `Incident ID` (integer 1 to 1,749)
- **Total Unique Incident IDs:** 1,749
- **Duplicate Incident IDs:** 0 (0 duplicate records found; 100% unique primary key).

### 2.3 Key Attributes & Missing Value Analysis
| Column Name | Inferred Type | Non-Null Count | Missing Count | Missing Pct | Quality Observation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Incident ID` | Integer | 1,749 | 0 | 0.0% | Complete unique identifier |
| `date` | Date / String | 1,749 | 0 | 0.0% | Incident date |
| `year` | Integer | 1,749 | 0 | 0.0% | Calendar year |
| `Risk Domain` | Categorical | 1,496 | 253 | 14.5% | 7 discrete categories + 253 unclassified |
| `Risk Subdomain` | Categorical | 1,495 | 254 | 14.5% | Granular risk classifications |
| `Harm Domain` | Categorical | 200 | 1549 | 88.6% | Binary/Ternary harm flag ('yes', 'no', 'maybe') |
| `Injuries` | Float | 206 | 1543 | 88.2% | 206 reported; 15 positive cases |
| `Lives Lost` | Float | 206 | 1543 | 88.2% | 206 reported; 12 positive cases |
| `Location Region` | Categorical | 200 | 1549 | 88.6% | Global regions (North America, Asia, Europe, etc.) |

### 2.4 Risk Domains Breakdown
```
Risk Domain
Malicious Actors & Misuse                      566
AI system safety, failures, and limitations    313
NaN                                            253
Discrimination and Toxicity                    243
Misinformation                                 196
Privacy & Security                             112
Human-Computer Interaction                      42
Socioeconomic & Environmental Harms             24
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
- **File Name:** `datasets/thai-disinfo-scam-dataset.xlsx`
- **Sheet:** `afnc_items`
- **Dimensions:** 17,726 rows, 18 columns.

### 3.2 Primary Key & Duplication
- **Primary Key:** `post_id` (WordPress post ID on antifakenewscenter.com).
- **Total Unique Posts:** 17,726
- **Duplicate post_id:** 0 (0 duplicate records found; 100% unique primary key).

### 3.3 Verdict Analysis (`verdict_th`)
```
verdict_th
ข่าวปลอม        9520
ข่าวจริง        3503
NaN             3268
ข่าวบิดเบือน    1435
```
- **Observations:**
  - `ข่าวปลอม` (Fake News): 9,520 (53.7%)
  - `ข่าวจริง` (True Information): 3,503 (19.8%)
  - `ข่าวบิดเบือน` (Distorted / Misleading): 1,435 (8.1%)
  - `NaN` (Unverified / Non-verdict articles such as advisories, educational articles): 3,268 (18.4%)

### 3.4 Category Analysis (`category_th`)
```
category_th
นโยบายรัฐบาล-ข่าวสาร    6272
ผลิตภัณฑ์สุขภาพ         3788
การเงิน-หุ้น            2514
คลังความรู้             1882
อาชญากรรมออนไลน์        1317
ภัยพิบัติ                713
ความสงบและความมั่นคง     683
ข่าวอื่นๆ                391
กิจกรรม                   98
ข่าวสาร                   40
เศรษฐกิจ                  23
ยาเสพติด                   5
```
- Primary financial category: `การเงิน-หุ้น` contains **2,514** fact-checked items.
  - ข่าวปลอม (Fake): 2,339 (93.04%)
  - ข่าวจริง (True): 118 (4.69%)
  - ข่าวบิดเบือน (Distorted): 57 (2.27%)
  - Missing verdicts in `การเงิน-หุ้น`: 0 (100% completeness).
- Broad financial keywords search (`ลงทุน`, `หุ้น`, `กู้`, `สินเชื่อ`, `คริปโต`, `เหรียญ`, `ธนาคาร`, `ออม`, `ดอกเบี้ย`, `เงินฝาก`, `สลาก`, `เทรด`) across title, tags, and content identifies **2,906** related posts across government, digital crime, and health categories.

### 3.5 View Count Inspection (`view_count`)
- Non-null count: 17,726 (100% complete)
- Min: 6 | Max: 595,030
- Mean: 1,428.7 | Median: 281.0
- Invalid/Negative/Zero values: 0 detected.

---

## 4. Dataset C & D: Weekly Panel & Online Scam Statistics

### 4.1 Online Scam Statistics (`acsc_weekly`)
- **Dimensions:** 48 rows (48 reporting weeks from 2025-11-09 to 2026-10-18).
- **Reporting Period:** Weekly Sunday–Saturday briefing reports from Thailand Anti-Online Scam Operation Center (AOC / ACSC).
- **Cases Summary:** Min: 5,000 | Max: 79,311 | Mean: 7,945.6 | Median: 6,439.5
- **Financial Loss (THB) Summary:** Min: 128,002,691 | Max: 2,775,000,000 | Mean: 378,695,286.9
- **Precision:** `exact` (37 weeks), `rounded` (11 weeks).

### 4.2 Integrated Weekly Panel (`weekly_panel`)
- **Dimensions:** 409 weekly rows from 2018-12-30 to 2026-10-25.
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
