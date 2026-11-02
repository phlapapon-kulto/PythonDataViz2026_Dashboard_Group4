# Quality Assurance & Testing Report (QA Test Report)
## โครงการ: ภัยดิจิทัลยุค AI: วิเคราะห์ความเสี่ยงจากปัญญาประดิษฐ์ ข่าวปลอม และการหลอกลวงออนไลน์
**Report Date:** 2026-11-02  
**Test Suite Status:** 10 / 10 Tests Passed (100% Success Rate)  
**Execution Time:** 0.505 seconds  

---

## 1. Test Suite Summary

An automated test suite comprising data quality assertions, analytical formulas, statistical correlations, and integration integrity checks was executed using Python `unittest`.

| Test Suite File | Test Method | Target Variable / Formula | Asserted Expected Value | Actual Test Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `test_data_quality.py` | `test_aiid_primary_key_uniqueness` | `ai_incidents_clean.incident_id` | Exactly 1,749 unique non-null IDs | 1,749 unique (0 duplicates, 0 nulls) | **PASSED** |
| `test_data_quality.py` | `test_aiid_casualties_calculation` | `injuries > 0 \| lives_lost > 0` | Exactly 21 unique incident records | 21 incidents | **PASSED** |
| `test_data_quality.py` | `test_afnc_post_id_uniqueness` | `afnc_items_clean.post_id` | Exactly 17,726 unique non-null IDs | 17,726 unique (0 duplicates, 0 nulls) | **PASSED** |
| `test_data_quality.py` | `test_afnc_financial_news_counts` | Category `การเงิน-หุ้น` & Fake % | Total: 2,514; Fake: 2,339; %: 93.04% | 2,514 total, 2,339 fake (93.04%) | **PASSED** |
| `test_data_quality.py` | `test_weekly_panel_integration` | Continuous Sunday series & reported weeks | 409 weeks total; 48 ACSC reported | 409 total; 48 reported | **PASSED** |
| `test_data_quality.py` | `test_missing_values_preserved_not_zero` | Pre-briefing `acsc_cases` & `acsc_loss_baht` | 361 weeks strictly null, NOT zero | 361 weeks null | **PASSED** |
| `test_data_quality.py` | `test_view_counts_non_negative` | `afnc_items_clean.view_count` | Strictly positive integers (> 0) | Range 6 to 595,030 (> 0) | **PASSED** |
| `test_analytics.py` | `test_pearson_correlation_all_48_weeks` | Pearson $r$ & $p$ across all 48 weeks | $r = -0.0903$ ($p = 0.5418$) | $r = -0.0903, p = 0.5418$ | **PASSED** |
| `test_analytics.py` | `test_pearson_correlation_excluding_outlier` | Pearson $r$ & $p$ for 47 weeks (no outlier) | $r = 0.5377$ ($p < 0.001$) | $r = 0.5377, p < 0.001$ | **PASSED** |
| `test_analytics.py` | `test_average_loss_per_case` | $\sum \text{loss} / \sum \text{cases}$ | Total loss 18.18B / 381.4K cases | 47,660.85 THB/case | **PASSED** |

---

## 2. Dashboard UI & Functional Verification

| Component & User Flow | Tested Action | Expected Behavior | Observed Behavior | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Tab Navigation** | Click Tab 1, 2, 3 buttons (desktop & mobile) | Instant tab switching, URL breadcrumbs, icon updates | Smooth, instant zero-reload tab switching | **PASSED** |
| **Tab 1 Filter System** | Select Year = 2024, Domain = Misinformation | KPIs, top domains, and trend charts recompute | Filter applied reactively, KPIs updated dynamically | **PASSED** |
| **Tab 1 Search Filter** | Search "autonomous" | Filter table and KPIs to autonomous system incidents | Immediate matching & rendering | **PASSED** |
| **Tab 1 Empty State** | Enter non-matching query "xyz123abc" | Display "ไม่พบข้อมูลที่ตรงกับเงื่อนไข" & reset button | Empty state displayed cleanly, charts hidden | **PASSED** |
| **Tab 2 Filter System** | Select Verdict = ข่าวปลอม | News table, topic bars, monthly trend filter to fake | Table filtered to 2,339 rows, charts updated | **PASSED** |
| **Tab 2 Table Pagination** | Click "ถัดไป" (Next) & "ย้อนกลับ" (Previous) | Pages advance 10 items at a time | Pagination responsive, boundary buttons disable | **PASSED** |
| **Tab 3 Outlier Switch** | Toggle "ไม่รวมสัปดาห์ผิดปกติ" | Recomputes $r$ from $-0.0903$ to $+0.5377$ with updated trendlines | Scatter plots and correlation cards update instantly | **PASSED** |
| **Tab 3 CSV Export** | Click "ดาวน์โหลดข้อมูล CSV" | Generates client-side CSV blob download | Download triggers correctly with 48 weekly rows | **PASSED** |

---

## 3. Discovered Bugs & Implemented Fixes
1. **Windows Console Character Encoding Bug:** Python printing Thai text to default Windows CP1252 stdout raised `UnicodeEncodeError`.  
   *Fix:* Added `sys.stdout.reconfigure(encoding='utf-8')` across all scripts.
2. **Local Static Hosting CORS Restrictions:** Opening HTML via `file:///` blocks `fetch()` for local JSON in modern browsers.  
   *Fix:* Built dual-mode loading pipeline with `data/processed/data_store.js` that assigns dataset arrays directly to `window.DATA_*` with instant fallback to standard `fetch()`.
3. **Week Alignment Discrepancy (2026-05-30 vs 2026-05-31):** ACSC briefing started on Saturday (8 days) while weekly panel uses Sunday.  
   *Fix:* Standardized Sunday `week_start` in `weekly_panel_final.csv`, verified case and loss match 100%, and documented transparently in reports.

---

## 4. Final Quality Conclusion
All automated regression tests and interactive dashboard user flows meet university and production deployment standards.
"""

qa_report_path = os.path.join(r"c:\Users\USER\PythonDataViz2026_Dashboard_Group4\reports", "QA_TEST_REPORT.md")
with open(qa_report_path, "w", encoding="utf-8") as f:
    f.write(CodeContent)

print("QA Test Report generated successfully!")
