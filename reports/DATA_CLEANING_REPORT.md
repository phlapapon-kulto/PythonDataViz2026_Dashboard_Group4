# Data Cleaning & Quality Management Report
## โครงการ: ภัยดิจิทัลยุค AI: วิเคราะห์ความเสี่ยงจากปัญญาประดิษฐ์ ข่าวปลอม และการหลอกลวงออนไลน์
**Report Date:** 2026-11-02  
**Data Engineer & Analyst:** Senior Engineering Team  
**Status:** Verification Passed  

---

## 1. Executive Summary & Principles
All 4 core datasets have undergone systematic, programmatic data cleaning in compliance with production data quality standards:
1. **Preservation of Raw Data:** Original raw spreadsheets remain untouched under `datasets/`.
2. **No Arbitrary Imputation:** Missing values in casualties, view counts, and scam statistics were strictly **not** converted to zero.
3. **No Silent Row Deletions:** Records with missing values were retained and tagged with data completeness flags.
4. **Primary Key Integrity:** Confirmed 0 duplicate primary keys across all datasets (`Incident ID`, `post_id`, `week_start`).
5. **Auditable Transformations:** Reusable Python data cleaning pipelines were authored and verified.

---

## 2. Before & After Cleaning Statistics

| Dataset | Raw File & Sheet | Original Rows | Cleaned Rows | Deduplicated Rows | Missing Keys | Key Features Added |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AI Incident Database** | `AIID_Excel_Export-20261019.xlsx` (Incidents) | 1,749 | 1,749 | 0 | 0 | Date normalization, casualty flags (`has_casualties`), standardized risk domains |
| **Thai Fake News** | `thai-disinfo-scam-dataset.xlsx` (afnc_items) | 17,726 | 17,726 | 0 | 0 | Bangkok time parsing, `verdict_group`, 2-tier financial relevance, text keyword matching |
| **Online Scam Stats** | `thai-disinfo-scam-dataset.xlsx` (acsc_weekly) | 48 | 48 | 0 | 0 | Sunday alignment check, precision check, `is_suspect_outlier` flag |
| **Weekly Panel** | `thai-disinfo-scam-dataset.xlsx` (weekly_panel) | 409 | 409 | 0 | 0 | Verified match against AFNC and ACSC, reporting status segregation |

---

## 3. Dataset-Specific Cleaning Operations

### 3.1 Dataset A: AI Incident Database (`ai_incidents_clean.csv`)
- **Header Parsing:** Multi-level title blocks in Excel rows 1–2 were bypassed; schema initialized with row 3 column definitions.
- **Primary Key:** `incident_id` verified unique (1 to 1,749, exactly 1,749 rows).
- **Date Standardization:** Standardized to ISO YYYY-MM-DD. Extracted calendar dimensions: `year`, `month`, `quarter`.
- **Risk Domain Mapping:**
  - 1,496 categorized incidents mapped across 7 standardized domains.
  - 253 unclassified incidents explicitly labeled as `Unclassified` rather than discarded.
- **Casualties Treatment:**
  - `injuries` and `lives_lost` validated as numeric. 1,543 records have missing casualty data.
  - Engineered boolean indicators: `has_injuries` (15 incidents), `has_fatalities` (12 incidents), `has_casualties` (21 unique incidents).
  - Explicitly separated confirmed zeros from unrecorded/missing cases.
- **Geographic Data:**
  - 200 incidents with reported regions standardized (`North America`, `Asia`, `Europe`, `Global`, etc.).
  - 1,549 records without regional data labeled `Unspecified`. Coordinates were not artificially fabricated.

### 3.2 Dataset B: Thai Financial Fake News (`afnc_items_clean.csv`)
- **Primary Key:** `post_id` verified 100% unique (17,726 unique items).
- **Date & Timezone:**
  - `published_bkk` parsed as UTC+7 (Bangkok timezone).
  - Validated consistency between `published_bkk`, `date`, and `week_start`.
- **Standardized Verdicts (`verdict_group`):**
  - ข่าวปลอม (Fake News): 9,520 (53.7%)
  - ข่าวจริง (True Information): 3,503 (19.8%)
  - ข่าวบิดเบือน (Distorted Information): 1,435 (8.1%)
  - ไม่ระบุผล / Unverified: 3,268 (18.4% - non-verdict educational and advisory posts)
- **Financial News Classification:**
  - **Tier 1 (Official Primary Category):** `category_th == 'การเงิน-หุ้น'` (2,514 items; 2,339 Fake, 118 True, 57 Distorted).
  - **Tier 2 (Broad Financial Misinformation):** Regex keyword scan across 22 financial terms (`ลงทุน`, `หุ้น`, `เงินกู้`, `สินเชื่อ`, `คริปโต`, etc.) captured an additional 392 posts in government policy, digital crime, and health.
  - Distinct fields created: `is_category_finance`, `is_keyword_finance`, `financial_relevance`, `classification_reason`.
- **View Counts:**
  - Validated as numeric integers (range 6 to 595,030).
  - 0 missing, 0 negative, 0 zero values.

### 3.3 Dataset C & D: Online Scam Statistics & Weekly Panel
- **Temporal Alignment:**
  - Source `acsc_weekly` contains 48 reporting weeks from 2025-11-09 to 2026-10-18.
  - Documented 1-day alignment discrepancy for week 2026-05-30 (Saturday briefing) vs 2026-05-31 (Sunday week_start), confirming identical case and loss statistics.
- **Reporting Status:**
  - 48 weeks have confirmed official ACSC scam reports (`acsc_reported == True`).
  - 361 pre-briefing weeks preserved with null scam cases/losses (`acsc_reported == False`). Unreported values were strictly kept null instead of 0.
- **Flagged Outlier Treatment:**
  - Week 2026-08-16 flagged with `is_suspect_outlier = True` due to anomalous 79,311 cases and 2.775 billion THB loss (internal share conflict noted in official police release).

---

## 4. Remaining Data Limitations
1. **AIID Casualty Reporting Bias:** 88.2% of AIID incidents lack specific casualty records. Statistics reflect confirmed reports only.
2. **AIID Geographic Scope:** AIID is an international database; Asia accounts for 14 incidents. Not representative of Thailand-specific incidents.
3. **AFNC View Count Snapshot:** View counts reflect cumulative page views on 1 Nov 2026, not views at the exact publication date.
4. **ACSC Time Horizon:** Weekly scam reporting commenced November 2025 (48 weeks total). Long-term multi-year correlation cannot be computed prior to Nov 2025.
