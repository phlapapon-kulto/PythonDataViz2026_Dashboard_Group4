# Data Integration Quality Report
## โครงการ: ภัยดิจิทัลยุค AI: วิเคราะห์ความเสี่ยงจากปัญญาประดิษฐ์ ข่าวปลอม และการหลอกลวงออนไลน์
**Report Date:** 2026-11-02  
**Status:** Validated  

---

## 1. Executive Summary
This report documents the cross-source integration of the Thailand Anti-Fake News Center (`afnc_items`), the Anti-Online Scam Operation Center (`acsc_weekly`), and the integrated panel (`weekly_panel`). All records were synchronized on Sunday-aligned calendar weeks (`week_start`).

---

## 2. Integration Alignment & Coverage

| Source Dataset | Time Key | Total Records | Date Range | Integration Alignment | Unmatched Records |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **afnc_items** (Financial) | `week_start` (Sunday) | 2,514 items | 2019-01-05 to 2026-10-31 | Aggregated to Sunday weekly sum | 0 |
| **acsc_weekly** | `week_start` | 48 briefings | 2025-11-09 to 2026-10-18 | Aligned with Sunday weekly key | 0 |
| **weekly_panel_final** | `week_start` | 409 weeks | 2018-12-30 to 2026-10-25 | 1 row per reporting week | 0 |

---

## 3. Discrepancy Analysis & Resolutions
1. **Week Alignment Discrepancy (2026-05-30 vs 2026-05-31):**
   - Source briefing `acsc_weekly` reported an 8-day period starting Saturday 2026-05-30.
   - `weekly_panel` aligned this record to Sunday 2026-05-31 to maintain standard Sunday-Saturday calendar periods.
   - **Resolution:** Retained Sunday key (2026-05-31) in `weekly_panel_final.csv`. Both files carry identical case figures (5,355) and loss values (128,002,691 THB).
2. **Derivation of `afnc_false_finance`:**
   - Evaluated against `afnc_items`: Exactly matches `count(verdict_th in ['ข่าวปลอม', 'ข่าวบิดเบือน'])` where `category_th == 'การเงิน-หุ้น'`.
   - Result: 0 discrepancy across all 409 weeks.

---

## 4. Correlation & Analytical Sensitivity Analysis

### 4.1 Series A: All 48 Official Reporting Weeks
- **Financial Fake News vs Scam Cases:**
  - Pearson $r$: **-0.0903**
  - $p$-value: **0.5418**
  - Sample Size ($N$): **48** weeks
  - Interpretation: Very weak negative correlation, statistically non-significant.
- **Financial Fake News vs Financial Loss (THB):**
  - Pearson $r$: **0.0557**
  - $p$-value: **0.7070**
  - Sample Size ($N$): **48** weeks
  - Interpretation: Very weak positive correlation, statistically non-significant.

### 4.2 Series B: Sensitivity Analysis (Excluding Flagged Outlier Week 2026-08-16)
- **Financial Fake News vs Scam Cases:**
  - Pearson $r$: **0.5377**
  - $p$-value: **9.7244e-05** ($p < 0.001$)
  - Sample Size ($N$): **47** weeks
  - Interpretation: Moderate positive correlation, statistically significant.
- **Financial Fake News vs Financial Loss (THB):**
  - Pearson $r$: **0.5720**
  - $p$-value: **2.6654e-05** ($p < 0.0001$)
  - Sample Size ($N$): **47** weeks
  - Interpretation: Moderate positive correlation, statistically significant.

### 4.3 Scientific Causal Warning
- **Correlation does not imply causation.**
- Increased fact-checking activity may reflect enhanced inter-agency vigilance or high-profile public reporting campaigns rather than direct scam causation.
- Victims may be lured by private messaging (LINE, Telegram, SMS) rather than public news websites.
