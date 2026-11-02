# ภัยดิจิทัลยุค AI: วิเคราะห์ความเสี่ยงจากปัญญาประดิษฐ์ ข่าวปลอม และการหลอกลวงออนไลน์
### AI Digital Threat Intelligence Dashboard (Python DataViz 2026 - Group 4)

[![Data Quality CI](https://github.com/phlapapon-kulto/PythonDataViz2026_Dashboard_Group4/actions/workflows/ci_deploy.yml/badge.svg)](https://github.com/phlapapon-kulto/PythonDataViz2026_Dashboard_Group4/actions)
[![Live Dashboard](https://img.shields.io/badge/Live_Dashboard-GitHub_Pages-2391FF?style=flat&logo=github)](https://phlapapon-kulto.github.io/PythonDataViz2026_Dashboard_Group4/)
[![Python](https://img.shields.io/badge/Python-3.14-blue.svg?logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-Academic_Use-emerald.svg)]()

---

## 1. บทนำและภาพรวมโครงการ (Project Overview)
ในยุคปัจจุบัน เทคโนโลยีปัญญาประดิษฐ์ (Artificial Intelligence: AI) มีการเติบโตอย่างรวดเร็วและเข้ามามีบทบาทในชีวิตประจำวัน ขณะเดียวกันได้ก่อให้เกิดภัยคุกคามทางดิจิทัลในมิติต่างๆ ไม่ว่าจะเป็นความผิดพลาดของระบบ AI, การสร้างข่าวปลอมและการบิดเบือนข้อมูลทางการเงิน (Financial Misinformation), ตลอดจนกลโกงการหลอกลวงออนไลน์ (Online Fraud & Scams)

โครงการนี้พัฒนาขึ้นเพื่อรวบรวม ตรวจสอบ ทำความสะอาด และวิเคราะห์ข้อมูลจากแหล่งข้อมูลจริงทางประวัติศาสตร์และปัจจุบัน เพื่อนำเสนอข้อมูลเชิงลึกผ่าน **Interactive Intelligence Dashboard** จำนวน 3 ส่วนหลัก (3 Tabs) ด้วยการออกแบบตามแนวคิด **Modern Cyber Intelligence** ที่ตอบโจทย์การใช้งานทั้งบนคอมพิวเตอร์ แท็บเล็ต และสมาร์ตโฟน

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
│   └── custom.css                  # Cyber Intelligence Custom Styles & Animations
├── js/
│   └── app.js                      # Reactive State, Filtering, Math, & Chart.js Controllers
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
│   └── generate_datastore_js.py    # Zero-CORS static data store builder
├── tests/                          # Automated Python Test Suite
│   ├── test_data_quality.py        # Primary key uniqueness, missing value integrity
│   └── test_analytics.py           # Pearson r, regression slope, KPI formulas
├── index.html                      # Production SPA Web Application
├── BRD.md                          # Business Requirements Document
├── handoff.md                      # Technical Operations Manual & Architecture Handoff
├── DATA_DICTIONARY.md              # Complete Column & Attribute Catalog
└── README.md                       # Main Project Documentation
```

---

## 5. วิธีการติดตั้งและรันระบบในเครื่อง (Local Setup & Run)

### 5.1 ความต้องการของระบบ (Prerequisites)
- **Python 3.10+** (ทดสอบสมบูรณ์บน Python 3.14)
- เว็บบราวเซอร์มาตรฐาน (Google Chrome, Microsoft Edge, Safari, Firefox)

### 5.2 การติดตั้งแพ็กเกจ (Install Dependencies)
```bash
pip install pandas openpyxl scipy numpy
```

### 5.3 การรันกระบวนการทำความสะอาดและรวมข้อมูล (Data Pipeline)
หากต้องการรันกระบวนการ Clean และ Integrate ใหม่จาก Raw Data:
```bash
# 1. รันการทำความสะอาดข้อมูล
python scripts/clean_data.py

# 2. รันการแปลงและรวมข้อมูลสถิติรายสัปดาห์
python scripts/integrate_data.py

# 3. สร้าง data_store.js สำหรับการรันแบบ Static
python scripts/generate_datastore_js.py
```

### 5.4 การรันชุดทดสอบอัตโนมัติ (Run Automated Tests)
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```
ผลลัพธ์ที่ได้: **Ran 10 tests in ~0.5s (10/10 OK - 100% Passed)**

### 5.5 การเปิดใช้งาน Dashboard
สามารถเปิดใช้งานได้ 2 วิธี:
1. **ผ่าน Local Web Server (แนะนำ):**
   ```bash
   python -m http.server 8000
   ```
   เปิดบราวเซอร์ไปที่: `http://localhost:8000`

2. **เปิดไฟล์โดยตรง (Direct File Opening):**
   ดับเบิลคลิกไฟล์ `index.html` เพื่อเปิดใช้งานได้ทันทีโดยไม่ต้องต่ออินเทอร์เน็ต (ระบบมี `data_store.js` รองรับการรันแบบ Standalone ไร้ปัญหา CORS)

---

## 6. การทดสอบและการส่งมอบงาน (CI/CD & Deployment)
- โปรเจกต์ถูกตั้งค่าให้ทดสอบอัตโนมัติผ่าน GitHub Actions (`.github/workflows/ci_deploy.yml`) เมื่อมีการ Push โค้ด
- รองรับการ Deploy อัตโนมัติขึ้น **GitHub Pages**
- URL เข้าชมสด: **[https://phlapapon-kulto.github.io/PythonDataViz2026_Dashboard_Group4/](https://phlapapon-kulto.github.io/PythonDataViz2026_Dashboard_Group4/)**
