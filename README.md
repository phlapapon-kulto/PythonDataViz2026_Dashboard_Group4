# ภัยดิจิทัลยุค AI: วิเคราะห์ความเสี่ยงจากปัญญาประดิษฐ์ ข่าวปลอม และการหลอกลวงออนไลน์
### AI Digital Threat Intelligence Dashboard (Python DataViz 2026 - Group 4)

[![Data Quality CI](https://github.com/phlapapon-kulto/PythonDataViz2026_Dashboard_Group4/actions/workflows/ci_deploy.yml/badge.svg)](https://github.com/phlapapon-kulto/PythonDataViz2026_Dashboard_Group4/actions)
[![Live Dashboard](https://img.shields.io/badge/Live_Dashboard-GitHub_Pages-2391FF?style=flat&logo=github)](https://phlapapon-kulto.github.io/PythonDataViz2026_Dashboard_Group4/)
[![Python](https://img.shields.io/badge/Python-3.14-blue.svg?logo=python)](https://python.org)
[![Offline Ready](https://img.shields.io/badge/Offline-100%25_Standalone-success.svg)]()
[![License](https://img.shields.io/badge/License-Academic_Use-emerald.svg)]()

---

## 1. บทนำและภาพรวมโครงการ (Project Overview)
ในยุคปัจจุบัน เทคโนโลยีปัญญาประดิษฐ์ (Artificial Intelligence: AI) มีการเติบโตอย่างรวดเร็วและเข้ามามีบทบาทในชีวิตประจำวัน ขณะเดียวกันได้ก่อให้เกิดภัยคุกคามทางดิจิทัลในมิติต่างๆ ไม่ว่าจะเป็นความผิดพลาดของระบบ AI, การสร้างข่าวปลอมและการบิดเบือนข้อมูลทางการเงิน (Financial Misinformation), ตลอดจนกลโกงการหลอกลวงออนไลน์ (Online Fraud & Scams)

โครงการนี้พัฒนาขึ้นเพื่อรวบรวม ตรวจสอบ ทำความสะอาด และวิเคราะห์ข้อมูลจากแหล่งข้อมูลจริงทางประวัติศาสตร์และปัจจุบัน เพื่อนำเสนอข้อมูลเชิงลึกผ่าน **Interactive Intelligence Dashboard** จำนวน 3 ส่วนหลัก (3 Tabs) ด้วยการออกแบบตามแนวคิด **Modern Cyber Intelligence** ที่ตอบโจทย์การใช้งานทั้งบนคอมพิวเตอร์ แท็บเล็ต และสมาร์ตโฟน โดยรองรับการใช้งานอย่างสมบูรณ์แบบทั้ง 3 รูปแบบ: **Local Web Server**, **Standalone Offline (ไม่ใช้อินเทอร์เน็ต)**, และ **GitHub Pages Deployment**

---

## 2. โครงสร้างแดชบอร์ด 3 ส่วนหลัก (Dashboard Architecture)

```
========================================================================================
                          AI DIGITAL THREAT INTELLIGENCE DASHBOARD
========================================================================================
  [ TAB 1: AI Risk Analysis ]  |  [ TAB 2: Financial Fake News ]  |  [ TAB 3: Scam Correlation ]
  - 1,749 AI Incidents         |  - 2,514 Financial Fact-Checks  |  - Weekly Dual Time-Series
  - Casualties: 21 incidents   |  - Fake News: 93.04% (2,339)     |  - Scatter Plots + Linear Fit
  - Top 5 Risk Domains         |  - Top Topics (Loans, Stocks)    |  - Outlier Sensitivity Mode
  - Timeline & Region Filters  |  - Searchable Paginated Table   |  - Pearson r & Causation Caveat
========================================================================================
```

### 1) Tab 1: AI Risk Analysis (วิเคราะห์ความเสี่ยงจากปัญญาประดิษฐ์)
- **KPIs:** จำนวนเหตุการณ์ความเสี่ยง AI รวม (1,749 เหตุการณ์), เหตุการณ์ที่มีผู้บาดเจ็บหรือเสียชีวิต (21 เหตุการณ์), อัตราการเติบโตรายปี (YoY Growth %), จำนวนกลุ่มความเสี่ยงหลัก (7 กลุ่ม)
- **Visualizations:** กราฟแท่งแนวนอน Top 5 Risk Domains, กราฟเส้นแนวโน้มเหตุการณ์รายปี (1983–2026), โดนัทสัดส่วนการกระจายตัวของความเสี่ยง, กราฟแท่งการกระจายตัวตามภูมิภาคทั่วโลก
- **Filters:** ตัวกรองปีที่เกิดเหตุ, กลุ่มความเสี่ยง (Risk Domain), ภูมิภาค (Location Region), และกล่องค้นหาคำสำคัญ

### 2) Tab 2: Financial Fake News Analysis (วิเคราะห์ข่าวปลอมด้านการเงิน)
- **KPIs:** จำนวนข่าวการเงินที่ได้รับการตรวจ (2,514 ข่าว), ข่าวปลอมด้านการเงิน (2,339 ข่าว), ข่าวบิดเบือน (57 ข่าว), สัดส่วนข่าวปลอม (93.04%), ยอดเข้าชมเฉลี่ยต่อข่าว (1,429 ครั้ง)
- **Visualizations:** กราฟแท่งหัวข้อข่าวปลอมการเงินยอดนิยม (สินเชื่อ, เพจปลอม, หุ้น), กราฟโดนัทสัดส่วนผลการตรวจ (Fake, True, Distorted), กราฟเส้นแนวโน้มการตรวจข่าวรายเดือน, กราฟแท่งข่าวที่มียอดวิวสูงสุด 10 อันดับ
- **Interactive News Table:** ตารางค้นหาข่าวพร้อมระบบแบ่งหน้า (Pagination) และลิงก์ไปยังบทความตรวจสอบจริงบนเว็บศูนย์ต่อต้านข่าวปลอม (AFNC)

### 3) Tab 3: Fake News & Online Scam Relationship (ความสัมพันธ์ข่าวปลอมและภัยหลอกลวงออนไลน์)
- **KPIs:** ข่าวปลอมการเงินเฉลี่ยต่อสัปดาห์, คดีหลอกลวงออนไลน์เฉลี่ยต่อสัปดาห์, มูลค่าความเสียหายเฉลี่ยต่อสัปดาห์, ความเสียหายเฉลี่ยต่อคดี (บาท)
- **Sensitivity Analysis (สวิตช์วิเคราะห์ความอ่อนไหวต่อค่าผิดปกติ):**
  - *รวมทุกสัปดาห์ (48 สัปดาห์):* $r = -0.0903$ ($p = 0.5418$ ไม่มีนัยสำคัญ)
  - *ไม่รวมสัปดาห์ผิดปกติ 16 ส.ค. 2026 (47 สัปดาห์):* $r = +0.5377$ ($p < 0.001$ ความสัมพันธ์เชิงบวกระดับปานกลางอย่างมีนัยสำคัญ)
- **Visualizations:** กราฟแนวโน้มคู่ 2 แกน (Dual-Axis Weekly Trend), แผนภาพการกระจายพร้อมเส้นแนวโน้มถดถอยเชิงเส้น (Linear Trendline) ทั้งมิติจำนวนคดีและมูลค่าความเสียหาย
- **Statistical Integrity:** คำเตือนทางสถิติว่า **Correlation ไม่ได้หมายความถึง Causation** พร้อมระบุข้อจำกัดของช่องทางการหลอกลวงและพฤติกรรมการแจ้งความ

---

## 3. แหล่งข้อมูลจริง (Source Datasets)

| รหัสชุดข้อมูล | ชื่อไฟล์ต้นทาง | คำอธิบายและขอบเขต | จำนวนเรคคอร์ด |
| :--- | :--- | :--- | :--- |
| **Dataset A** | `AIID_Excel_Export-20261019.xlsx` (Incidents) | ฐานข้อมูลความเสี่ยงจาก AI ระดับนานาชาติ (AI Incident Database) | 1,749 เหตุการณ์ |
| **Dataset B** | `thai-disinfo-scam-dataset.xlsx` (afnc_items) | ฐานข้อมูลผลการตรวจสอบข่าวของศูนย์ต่อต้านข่าวปลอมแห่งประเทศไทย (AFNC) | 17,726 ข่าว (หมวดการเงิน 2,514 ข่าว) |
| **Dataset C** | `thai-disinfo-scam-dataset.xlsx` (acsc_weekly) | สถิติคดีแจ้งความออนไลน์และความเสียหายรายสัปดาห์จาก ศปอส. (AOC / ACSC) | 48 สัปดาห์รายงาน |
| **Dataset D** | `thai-disinfo-scam-dataset.xlsx` (weekly_panel) | ชุดข้อมูลรวมระดับสัปดาห์ (Sunday–Saturday Calendar Weeks) | 409 สัปดาห์ (2018–2026) |

---

## 4. โครงสร้างโฟลเดอร์ของโปรเจกต์ (Repository Structure)

```
PythonDataViz2026_Dashboard_Group4/
├── .github/
│   └── workflows/
│       └── ci_deploy.yml           # Automated CI Testing & GitHub Pages Deployment
├── css/
│   └── custom.css                  # Cyber Intelligence Custom Styles & Typography
├── js/
│   └── app.js                      # Reactive State, Filtering, Math, & Chart.js Controllers
├── vendor/                         # Local vendor bundles for 100% offline support
│   ├── tailwindcss.js              # Standalone Tailwind CSS Engine
│   ├── chart.umd.min.js            # Chart.js library
│   └── lucide.min.js               # Lucide icons library
├── data/
│   ├── raw/                        # Protected raw data staging
│   ├── processed/                  # Cleaned CSV & JSON datasets
│   │   ├── ai_incidents_clean.csv
│   │   ├── afnc_items_clean.csv
│   │   ├── acsc_weekly_clean.csv
│   │   ├── weekly_panel_final.csv
│   │   ├── ai_incidents.json
│   │   ├── financial_news.json
│   │   ├── weekly_scams.json
│   │   └── data_store.js           # Zero-CORS bundle for offline & static hosting
│   └── intermediate/               # Classification mappings & schema metadata
├── datasets/                       # Original raw source files
│   ├── AIID_Excel_Export-*.xlsx
│   └── thai-disinfo-scam-dataset.xlsx
├── reports/                        # Professional Engineering & Quality Reports
│   ├── DATA_INSPECTION_REPORT.md   # Detailed pre-cleaning data inspection
│   ├── DATA_CLEANING_REPORT.md     # Cleaning methodology & before/after audit
│   ├── DATA_INTEGRATION_REPORT.md  # Multi-source temporal alignment & correlation
│   ├── QA_TEST_REPORT.md           # Automated test results & UI QA audit
│   └── FINAL_IMPLEMENTATION_REPORT.md # Comprehensive final handoff delivery
├── scripts/                        # Automated Data Engineering Pipelines
│   ├── clean_data.py               # Systematic data cleaning script
│   ├── integrate_data.py           # Weekly data aggregation and integration script
│   ├── generate_datastore_js.py    # Zero-CORS static data store builder
│   └── download_vendor_assets.py   # Offline vendor asset synchronizer
├── tests/                          # Automated Python Test Suite
│   ├── test_data_quality.py        # Primary key uniqueness, missing value integrity
│   ├── test_analytics.py           # Pearson r, regression slope, KPI formulas
│   └── test_offline_readiness.py   # Relative paths, local assets, zero-CORS audit
├── index.html                      # Production SPA Web Application
├── BRD.md                          # Business Requirements Document
├── handoff.md                      # Technical Operations Manual & Architecture Handoff
├── DATA_DICTIONARY.md              # Complete Column & Attribute Catalog
└── README.md                       # Main Project Documentation
```

---

## 5. วิธีการเปิดใช้งานแดชบอร์ด 3 รูปแบบ (Execution Modes)

### 5.1 โหมดที่ 1: Local Web Server (แนะนำสำหรับการพัฒนา)
สามารถเปิดเว็บเซิร์ฟเวอร์จำลองในเครื่องได้โดยใช้คำสั่งมาตรฐานของ Python:
```bash
python -m http.server 8000
```
จากนั้นเปิดเว็บบราวเซอร์ (Chrome, Edge, Safari หรือ Firefox) แล้วเข้าไปที่:
**[http://localhost:8000](http://localhost:8000)**

*ข้อดี:* สามารถทดสอบการตอบสนองของ HTTP Headers และการโหลดไฟล์แบบ Client-Server ได้อย่างสมจริง

---

### 5.2 โหมดที่ 2: Standalone Offline (เปิดใช้งานโดยไม่ต่ออินเทอร์เน็ต)
แดชบอร์ดนี้ถูกออกแบบและติดตั้งระบบ **Zero-CORS Client Architecture** พร้อมไลบรารี Vendor ในโฟลเดอร์ `vendor/` ครบครัน:
1. ปิดการเชื่อมต่ออินเทอร์เน็ต (หรือเข้า Airplane Mode)
2. ดับเบิลคลิกเปิดไฟล์ `index.html` บนโฟลเดอร์ของเครื่องคอมพิวเตอร์ได้ทันที
3. บราวเซอร์จะเปิดไฟล์ด้วย URL รูปแบบ `file:///.../index.html`

*ความสามารถในโหมด Offline:*
- ข้อมูลทั้งหมดถูกโหลดทันทีผ่าน `data/processed/data_store.js` โดยไม่มีปัญหา CORS Restriction
- หน้าตา ดีไซน์ และ Layout ทำงานสมบูรณ์ด้วย `./vendor/tailwindcss.js` ในเครื่อง
- กราฟทุกตัวเรนเดอร์ได้ 100% ผ่าน `./vendor/chart.umd.min.js`
- ไอคอนแสดงผลครบถ้วนผ่าน `./vendor/lucide.min.js`
- ฟอนต์ภาษาไทยสลับใช้ System Fonts (`Leelawadee UI`, `Segoe UI`, `Tahoma`) อัตโนมัติเมื่อไม่ต่ออินเทอร์เน็ต
- ฟังก์ชัน Filter, Search, Pagination, การสลับ Sensitivity Toggle, และการส่งออก CSV ทำงานได้ตามปกติ

---

### 5.3 โหมดที่ 3: GitHub Pages Deployment (เข้าชมออนไลน์)
โปรเจกต์ได้รับการตั้งค่าระบบ CI/CD ผ่าน GitHub Actions อัตโนมัติ:
- **Repository URL:** [https://github.com/phlapapon-kulto/PythonDataViz2026_Dashboard_Group4/](https://github.com/phlapapon-kulto/PythonDataViz2026_Dashboard_Group4/)
- **Live URL:** [https://phlapapon-kulto.github.io/PythonDataViz2026_Dashboard_Group4/](https://phlapapon-kulto.github.io/PythonDataViz2026_Dashboard_Group4/)

*ขั้นตอนการเปิดใช้งาน GitHub Pages ใน Repository:*
1. ไปที่แท็บ **Settings** ของ GitHub Repository
2. เลือกเมนู **Pages** ในแถบด้านซ้าย
3. ในหัวข้อ **Build and deployment > Source** ให้เลือก:
   - **GitHub Actions** (ระบบจะใช้ `.github/workflows/ci_deploy.yml` ในการทดสอบและ Deploy อัตโนมัติ)
   - หรือเลือก **Deploy from a branch** แล้วระบุ Branch `main` และโฟลเดอร์ `/ (root)`
4. เมื่อ Workflow รันเสร็จสิ้น เว็บไซต์จะแสดงผลออนไลน์ที่ URL ข้างต้นทันที

---

## 6. การทดสอบระบบอัตโนมัติ (Automated Testing)
โปรเจกต์มีชุดทดสอบอัตโนมัติ 3 มิติ (Data Quality, Analytics Math, Offline Readiness):
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```
**ผลการทดสอบจริง:**
```
test_average_loss_per_case (test_analytics.TestAnalytics) ... ok
test_pearson_correlation_all_48_weeks (test_analytics.TestAnalytics) ... ok
test_pearson_correlation_excluding_outlier (test_analytics.TestAnalytics) ... ok
test_afnc_financial_news_counts (test_data_quality.TestDataQuality) ... ok
test_afnc_post_id_uniqueness (test_data_quality.TestDataQuality) ... ok
test_aiid_casualties_calculation (test_data_quality.TestDataQuality) ... ok
test_aiid_primary_key_uniqueness (test_data_quality.TestDataQuality) ... ok
test_missing_values_preserved_not_zero (test_data_quality.TestDataQuality) ... ok
test_view_counts_non_negative (test_data_quality.TestDataQuality) ... ok
test_weekly_panel_integration (test_data_quality.TestDataQuality) ... ok
test_datastore_offline_bundle (test_offline_readiness.TestOfflineReadiness) ... ok
test_local_vendor_assets_exist (test_offline_readiness.TestOfflineReadiness) ... ok
test_no_broken_absolute_asset_paths (test_offline_readiness.TestOfflineReadiness) ... ok

----------------------------------------------------------------------
Ran 13 tests in 0.495s
OK
```

---

## 7. การแก้ไขปัญหาทั่วไป (Troubleshooting)

| ปัญหาที่อาจพบ | สาเหตุ | วิธีแก้ไข |
| :--- | :--- | :--- |
| **Port 8000 is already in use** | มีโปรแกรมอื่นเปิดพอร์ต 8000 ค้างไว้ | เปลี่ยนพอร์ตที่ใช้รัน เช่น `python -m http.server 8080` แล้วเข้าผ่าน `http://localhost:8080` |
| **เปิดไฟล์ตรงแล้วกราฟไม่ขึ้น** | เปิดผ่านบราวเซอร์รุ่นเก่าที่ไม่รองรับ ES6 | เปิดด้วยบราวเซอร์รุ่นใหม่ (Google Chrome, MS Edge, Safari) หรือเปิดผ่าน Local Server |
| **ไอคอนไม่แสดงผลเมื่อ Offline** | ไฟล์ `vendor/lucide.min.js` สูญหายหรือไม่ได้ดาวน์โหลด | รันคำสั่ง `python scripts/download_vendor_assets.py` เพื่อซิงก์ไฟล์เข้าสู่ `vendor/` |
| **ข้อมูลในตารางไม่ตรงกับ Raw Data** | ยังไม่ได้รันสคริปต์ Clean และ Integrate | รันคำสั่ง `python scripts/clean_data.py` และ `python scripts/integrate_data.py` |
| **GitHub Pages แสดงหน้า 404** | ยังไม่ได้เปิดการตั้งค่า Pages ใน GitHub Settings | ไปที่แท็บ Settings > Pages และเลือก Source เป็น GitHub Actions หรือ main branch |
