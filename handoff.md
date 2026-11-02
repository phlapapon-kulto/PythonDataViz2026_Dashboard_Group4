# Technical Handoff Document

## โครงการ: ภัยดิจิทัลยุค AI --- วิเคราะห์ความเสี่ยงจากปัญญาประดิษฐ์ ข่าวปลอม และการหลอกลวงออนไลน์

เอกสารนี้ใช้ส่งมอบรายละเอียดทางเทคนิคให้ Developer, Data Engineer, Data Analyst
หรือผู้ดูแลระบบ เพื่อให้สามารถติดตั้ง รัน ตรวจสอบ แก้ไข และพัฒนาระบบต่อได้

> **สถานะ:** เอกสารข้อกำหนดการส่งมอบ (Implementation Handoff) รายละเอียด
> Framework, คำสั่งรัน, โครงสร้างไฟล์จริง และ URL ต้องปรับให้ตรงกับ Repository
> หลังตรวจสอบและพัฒนาจริง ห้ามถือว่ารายการที่ยังไม่ได้ตรวจสอบเป็นสิ่งที่ติดตั้งหรือ Deploy
> แล้ว

------------------------------------------------------------------------

## 1. Project Summary

**ชื่อระบบ:** ภัยดิจิทัลยุค AI: วิเคราะห์ความเสี่ยงจากปัญญาประดิษฐ์ ข่าวปลอม
และการหลอกลวงออนไลน์

**เป้าหมายทางเทคนิค**

-   อ่าน Dataset จาก GitHub Repository
-   ตรวจสอบคุณภาพและทำความสะอาดข้อมูล
-   แปลงข้อมูลให้อยู่ในรูปแบบพร้อมวิเคราะห์
-   เชื่อมข้อมูลข่าวปลอมกับสถิติการหลอกลวงในระดับรายสัปดาห์
-   คำนวณ KPI และสถิติที่ใช้ใน Dashboard
-   ให้บริการ Dashboard แบบ Interactive จำนวน 3 Tabs
-   ทดสอบระบบและจัดทำเอกสาร
-   ใช้ GitHub สำหรับ Version Control และ CI/CD
-   Deploy ด้วย Hosting ที่เหมาะกับ Framework จริง

## 2. Repository & File Discovery

ก่อนเริ่มแก้ไขระบบ ให้ตรวจสอบ Repository จริง:

``` bash
pwd
git status
git branch --show-current
git remote -v
find . -maxdepth 3 -type f
```

ตรวจสอบเพิ่มเติม:

-   ไฟล์ Dataset และชื่อไฟล์จริง
-   โครงสร้างโฟลเดอร์
-   Framework และเวอร์ชัน
-   Dependency files
-   Entry point ของแอป
-   Script สำหรับทำความสะอาดและวิเคราะห์ข้อมูล
-   Test suite
-   GitHub Actions
-   Deployment configuration

ห้ามย้ายหรือลบไฟล์เดิมก่อนเข้าใจการใช้งาน

## 3. Source Datasets

### 3.1 AI Incident Database

**ไฟล์ที่คาดว่าจะใช้:** `AIID_Excel_Export-20261026.xlsx`\
**ชีต:** `Incidents`

คอลัมน์หลัก:

-   `Incident ID`
-   `date` หรือ `year`
-   `Risk Domain`
-   `Risk Subdomain`
-   `Harm Domain`
-   `Injuries`
-   `Lives Lost`
-   `Location Region`

**การใช้งาน:** วิเคราะห์จำนวนเหตุการณ์ ประเภทความเสี่ยง ผลกระทบ
และแนวโน้มตามเวลา

### 3.2 Financial Fake News

**ไฟล์ที่คาดว่าจะใช้:** `04_Thai_Disinformation_and_Scams/csv/afnc_items.csv`

คอลัมน์หลัก:

-   `post_id`
-   `published_bkk`
-   `date`
-   `week_start`
-   `month`
-   `verdict_th`
-   `category_th`
-   `title`
-   `content`
-   `topic_tags`
-   `view_count`

**การใช้งาน:** วิเคราะห์ข่าวการเงิน ผลตรวจสอบ ประเด็นข่าว แนวโน้มรายเดือน
และยอดเข้าชม

### 3.3 Weekly Panel

**ไฟล์ที่คาดว่าจะใช้:** `weekly_panel.csv`

คอลัมน์หลัก:

-   `week_start`
-   `afnc_false_finance`
-   `acsc_reported`
-   `acsc_cases`
-   `acsc_loss_baht`
-   `acsc_loss_precision`

**การใช้งาน:** ตารางเชื่อมข้อมูลรายสัปดาห์และเป็นแหล่งตรวจสอบผลการรวมข้อมูล

### 3.4 Online Scam Weekly

**ไฟล์ที่คาดว่าจะใช้:** `acsc_weekly.csv`

คอลัมน์หลัก:

-   `week_start`
-   `cases`
-   `loss_baht`
-   `loss_precision`

**การใช้งาน:** ตรวจสอบจำนวนคดีและมูลค่าความเสียหายรายสัปดาห์

**ข้อกำหนด:** ชื่อไฟล์และตำแหน่งข้างต้นต้องตรวจสอบกับ Repository จริงก่อนรัน
หากชื่อหรือโฟลเดอร์ต่างออกไป ให้ใช้ตำแหน่งจริงและบันทึกไว้ในรายงาน

## 4. Recommended System Architecture

แยกระบบออกเป็นชั้นเพื่อให้แก้ไขและตรวจสอบได้ง่าย

``` text
GitHub Repository
       |
       v
Raw Datasets
       |
       v
Data Inspection
       |
       v
Data Cleaning
       |
       v
Data Transformation
       |
       v
Data Integration
       |
       v
Analysis-ready Datasets
       |
       v
Analytics / KPI Layer
       |
       v
Dashboard Data Layer
       |
       v
Interactive Dashboard
       |
       v
User
```

### 4.1 Data Layer

รับผิดชอบ:

-   อ่าน CSV และ Excel
-   ตรวจสอบ Schema
-   ตรวจสอบชนิดข้อมูล
-   ตรวจสอบ Missing Values และ Duplicates
-   ทำความสะอาดข้อมูล
-   บันทึก Processed Datasets
-   เก็บ Mapping และ Metadata

### 4.2 Analytics Layer

รับผิดชอบ:

-   คำนวณ KPI
-   สร้างข้อมูลสรุปสำหรับกราฟ
-   รวมข้อมูลตามเวลา
-   คำนวณ Pearson correlation
-   ตรวจสอบจำนวนตัวอย่างและความครบถ้วน

### 4.3 Presentation Layer

รับผิดชอบ:

-   Sidebar และ Navigation
-   Dashboard 3 Tabs
-   KPI Cards
-   Charts
-   Tables
-   Filters
-   Tooltips
-   Empty States
-   Responsive Layout

### 4.4 Deployment Layer

รับผิดชอบ:

-   Dependency Installation
-   Automated Tests
-   Build
-   GitHub Actions
-   Deployment
-   Deployment Verification

## 5. Recommended Repository Structure

ปรับโครงสร้างนี้ตาม Framework และ Repository ที่มีอยู่จริง

``` text
project-root/
│
├── data/
│   ├── raw/
│   ├── intermediate/
│   └── processed/
│
├── src/
│   ├── data_cleaning/
│   │   ├── inspect_data.py
│   │   ├── clean_ai_incidents.py
│   │   ├── clean_fake_news.py
│   │   ├── clean_scam_data.py
│   │   └── validate_data.py
│   │
│   ├── data_integration/
│   │   └── build_weekly_panel.py
│   │
│   ├── analytics/
│   │   ├── ai_risk_analysis.py
│   │   ├── financial_news_analysis.py
│   │   └── scam_correlation_analysis.py
│   │
│   └── dashboard/
│       ├── app entry point
│       ├── components/
│       ├── pages/
│       └── styles/
│
├── tests/
│   ├── test_data_quality.py
│   ├── test_kpi.py
│   ├── test_weekly_integration.py
│   └── test_dashboard_logic.py
│
├── reports/
│   ├── DATA_INSPECTION_REPORT.md
│   ├── DATA_CLEANING_REPORT.md
│   ├── DATA_INTEGRATION_REPORT.md
│   ├── QA_TEST_REPORT.md
│   └── FINAL_IMPLEMENTATION_REPORT.md
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
│
├── BRD.md
├── handoff.md
├── DATA_DICTIONARY.md
├── README.md
├── .gitignore
└── dependency configuration
```

ไฟล์ตัวอย่างเป็นโครงสร้างแนะนำ ไม่ใช่ข้อกำหนดให้สร้างซ้ำหากมีไฟล์เทียบเท่าอยู่แล้ว

## 6. Data Cleaning Workflow

### 6.1 General Rules

1.  เก็บ Raw Data โดยไม่แก้ไขทับ
2.  ทำงานผ่าน Script ที่รันซ้ำได้
3.  ตรวจสอบ Schema ก่อนประมวลผล
4.  Standardize วันที่ ตัวเลข และข้อความ
5.  ตรวจสอบ Primary Key และ Duplicate
6.  เก็บ Missing Values ตามความหมายจริง
7.  ไม่แทน Missing ด้วย Zero โดยไม่มีหลักฐาน
8.  บันทึกจำนวนแถวก่อนและหลังการเปลี่ยนแปลง
9.  บันทึกกฎการแปลงข้อมูล
10. ทดสอบข้อมูลหลังทำความสะอาด

### 6.2 AI Incident Cleaning

-   ตรวจสอบ `Incident ID` ซ้ำและความขัดแย้งของข้อมูล
-   แปลงวันที่เป็น Datetime
-   สร้าง `year`, `month` จากวันที่ที่ถูกต้อง
-   ทำมาตรฐาน Risk Domain, Risk Subdomain และ Harm Domain
-   แปลง Injuries และ Lives Lost เป็นตัวเลข
-   ตรวจสอบค่าติดลบ ค่าว่าง และค่าผิดปกติ
-   นับเหตุการณ์ด้วย Incident ID ไม่ซ้ำ
-   นับเหตุการณ์ที่มีผลกระทบเมื่อมีค่ามากกว่า 0 ที่ยืนยันได้
-   ไม่ถือค่าที่หายไปเป็นศูนย์
-   ไม่สร้างพิกัดจากชื่อพื้นที่ที่กำกวม

### 6.3 Financial Fake News Cleaning

-   ตรวจสอบ `post_id` ซ้ำและรายการที่มีข้อมูลขัดแย้ง
-   แปลง `published_bkk`, `date`, `week_start`
-   ตรวจสอบ Timezone และความสอดคล้องของวัน
-   ตรวจสอบค่าจริงทั้งหมดของ `verdict_th`
-   สร้าง `verdict_group` โดยเก็บค่าเดิมไว้
-   แยก Fake, Distorted, True, Other และ Unverified
-   สร้างกฎการจำแนกข่าวการเงินที่อธิบายได้
-   เก็บ Category Match, Keyword Match และ Classification Reason
-   แปลง `view_count` เป็นตัวเลข
-   คง Missing View Count เป็น Missing

### 6.4 Scam Data Cleaning

-   ตรวจสอบ `week_start` ซ้ำ
-   ตรวจสอบระดับการสรุปของแต่ละแถว
-   แปลง `cases` และ `loss_baht` เป็นตัวเลข
-   ตรวจสอบค่าติดลบและค่าผิดปกติ
-   เก็บ `loss_precision` ไว้
-   แยกสัปดาห์ที่ไม่มีรายงานจากสัปดาห์ที่รายงานเป็นศูนย์

## 7. Weekly Data Integration

Tab 3 ต้องใช้ข้อมูลที่มีหน่วยเวลาเดียวกัน คือรายสัปดาห์

### 7.1 Integration Key

ใช้ `week_start` เป็นคีย์หลักหลังตรวจสอบว่าแต่ละแหล่งใช้กติกาวันเริ่มต้นสัปดาห์เดียวกัน

### 7.2 Processing Steps

1.  อ่านข้อมูลข่าวจาก `afnc_items.csv`
2.  กรองข่าวการเงินตามกฎที่บันทึกไว้
3.  เลือกเฉพาะผลตรวจสอบที่เข้าเกณฑ์ข่าวปลอมตามนิยาม
4.  Aggregate จำนวนข่าวต่อสัปดาห์
5.  อ่านข้อมูลจาก `acsc_weekly.csv`
6.  ตรวจสอบจำนวนคดีและมูลค่าความเสียหาย
7.  ตรวจสอบ `weekly_panel.csv` เทียบกับแหล่งต้นทาง
8.  Join ด้วย `week_start`
9.  ตรวจสอบ Duplicate, Missing และ Unmatched Weeks
10. บันทึกผลเป็น `weekly_panel_final.csv`

### 7.3 Important Missing-Data Rules

-   `acsc_reported = false` หรือสถานะที่เทียบเท่า
    ต้องไม่ถูกตีความเป็นจำนวนคดีศูนย์โดยอัตโนมัติ
-   ค่าว่างใน `acsc_cases` ไม่เท่ากับศูนย์
-   ค่าว่างใน `acsc_loss_baht` ไม่เท่ากับไม่มีความเสียหาย
-   คำนวณ Average Loss per Case เมื่อข้อมูลทั้งสองครบและจำนวนคดีมากกว่า 0
-   Correlation แต่ละคู่ต้องใช้ Complete Cases ของตัวแปรคู่นั้นแยกกัน

### 7.4 Integration Validation

ตรวจสอบ:

-   จำนวนสัปดาห์ในแต่ละแหล่ง
-   จำนวนสัปดาห์ที่จับคู่กันได้
-   สัปดาห์ที่ไม่ตรงกัน
-   สัปดาห์ที่ข้อมูลคดีหาย
-   สัปดาห์ที่ข้อมูลความเสียหายหาย
-   สัปดาห์ที่ข้อมูลซ้ำ
-   ความแตกต่างระหว่าง Weekly Panel กับข้อมูลต้นทาง

## 8. Analytics & KPI Logic

### 8.1 Tab 1 --- AI Risk Analysis

**Total AI Incidents**

จำนวน `Incident ID` ที่ไม่ซ้ำหลังผ่านกฎจัดการข้อมูลซ้ำ

**Incidents with Injuries or Fatalities**

จำนวน Incident ID ไม่ซ้ำที่มีอย่างน้อยหนึ่งเงื่อนไข:

-   `Injuries > 0`
-   `Lives Lost > 0`

กรณีข้อมูลผลกระทบขาดหายต้องไม่ถูกนับเป็นไม่มีผลกระทบโดยไม่มีหลักฐาน

**Annual Growth**

``` text
((Current Year Incidents - Previous Year Incidents)
 / Previous Year Incidents) * 100
```

หากปีก่อนเป็น 0 ให้แสดง N/A

**Charts**

-   Top 5 Risk Domains
-   AI Incidents Over Time
-   Risk Distribution Treemap

### 8.2 Tab 2 --- Financial Fake News Analysis

**Total Financial News Checked**

จำนวน `post_id` ไม่ซ้ำที่เข้าเกณฑ์ข่าวการเงิน

**Total Fake Financial News**

จำนวนรายการข่าวการเงินที่ `verdict_group` เป็น Fake ตาม Mapping ที่ตรวจสอบแล้ว

**Total Distorted Financial News**

จำนวนรายการข่าวการเงินที่ `verdict_group` เป็น Distorted / Misleading

**Fake News Percentage**

``` text
Fake Financial News
------------------------------- * 100
Financial News with Valid Verdict
```

ตัวหารต้องรวมเฉพาะรายการที่มีผลตรวจสอบชัดเจนตามนิยามที่ประกาศไว้

**Average Views**

``` text
Sum of Valid View Counts
------------------------
Number of Records with Valid View Counts
```

**Charts**

-   Fake News by Topic
-   Verdict Distribution
-   Monthly Financial News Trend
-   Top News by View Count

### 8.3 Tab 3 --- Fake News & Online Scam Relationship

**Average Loss per Case**

``` text
Weekly Financial Loss / Weekly Scam Cases
```

คำนวณเมื่อข้อมูลทั้งสองครบและจำนวนคดีมากกว่า 0

**Pearson Correlation**

คำนวณแยกสำหรับ:

1.  `afnc_false_finance` กับ `acsc_cases`
2.  `afnc_false_finance` กับ `acsc_loss_baht`

ใช้ข้อมูลรายสัปดาห์ที่ valid และ complete ในแต่ละคู่

ต้องแสดง:

-   Pearson r
-   Number of valid observations (n)
-   Correlation direction
-   คำอธิบายความสัมพันธ์
-   ข้อจำกัดของข้อมูล

หากข้อมูลไม่เพียงพอหรือค่าตัวแปรไม่มีความแปรปรวน ให้แสดง N/A พร้อมเหตุผล ห้ามสร้างค่า r
ขึ้นเอง

## 9. Dashboard Specification

### 9.1 Shared Layout

-   Sidebar / Navigation
-   Page Title และ Description
-   Filter Area
-   KPI Cards
-   Chart Grid
-   Data Table เมื่อเหมาะสม
-   Data Source และ Data Notes

### 9.2 Tab 1

KPI:

-   Total AI Incidents
-   Incidents with Injuries or Fatalities

Charts:

-   Horizontal Bar: Top 5 Risk Domains
-   Line: AI Incidents Over Time
-   Treemap: Risk Distribution

Filters:

-   Year
-   Location Region
-   Risk Domain
-   Harm Domain

### 9.3 Tab 2

KPI:

-   Financial News Checked
-   Fake Financial News
-   Distorted Financial News

Charts:

-   Fake News by Topic
-   Verdict Distribution
-   Monthly Trend
-   Top View Count

Filters:

-   Date Range
-   News Category
-   Verdict
-   Search Keyword

Table:

-   Publication Date
-   News Title
-   Category
-   Verdict
-   View Count

### 9.4 Tab 3

KPI:

-   Weekly Financial Fake News
-   Online Scam Cases
-   Financial Loss
-   Average Loss per Case

Charts:

-   Weekly Trend Comparison
-   Fake News vs Scam Cases
-   Fake News vs Financial Loss

Filters:

-   Weekly Date Range
-   Financial News Category
-   Case Count Range
-   Financial Loss Range

แสดง Pearson r และ n แยกใน Scatter Plot แต่ละชุด

## 10. Filter & Interaction Contract

ตัวกรองต้องทำงานกับข้อมูลจริง ไม่ใช่เพียงเปลี่ยนรูปลักษณ์

### 10.1 Shared Rules

-   ทุกองค์ประกอบใน Tab เดียวกันต้องอ้างอิง Filtered Dataset ที่สอดคล้องกัน
-   รองรับการใช้หลาย Filter พร้อมกัน
-   Reset ต้องคืนค่าเริ่มต้น
-   แสดง Active Filters
-   เมื่อไม่พบข้อมูล ให้แสดง `ไม่พบข้อมูล`
-   KPI, Chart และ Table ต้องอัปเดตตาม Filter
-   ห้ามนับ Missing เป็น Zero

### 10.2 Filter Scope

  Tab            Filter         องค์ประกอบที่ต้องอัปเดต
  -------------- -------------- -------------------------------
  AI Risk        Year           KPI, ทุกกราฟ และตาราง
  AI Risk        Region         KPI, กราฟ และข้อมูลพื้นที่
  AI Risk        Risk Domain    KPI และกราฟที่เกี่ยวข้อง
  AI Risk        Harm Domain    KPI และกราฟที่เกี่ยวข้อง
  Fake News      Date Range     KPI, กราฟ และตาราง
  Fake News      Category       KPI, กราฟ และตาราง
  Fake News      Verdict        KPI, Donut, Trend และตาราง
  Fake News      Keyword        รายการข่าวและกราฟที่เกี่ยวข้อง
  Relationship   Weekly Range   KPI, Trend, Scatter และตาราง
  Relationship   Category       จำนวนข่าวและการวิเคราะห์ที่เกี่ยวข้อง
  Relationship   Cases Range    องค์ประกอบที่เกี่ยวข้องกับคดี
  Relationship   Loss Range     องค์ประกอบที่เกี่ยวข้องกับความเสียหาย

**ข้อควรระวัง:** การกรอง Case Count หรือ Loss Range
จะเปลี่ยนกลุ่มสัปดาห์ที่นำไปคำนวณ Correlation ด้วย
ต้องแสดงสถานะตัวกรองและจำนวนตัวอย่างที่เหลือหลังกรอง

## 11. UI/UX Handoff

**Theme:** Modern Cyber Intelligence + Minimal Dashboard

**Color Palette**

  Color       Hex         Suggested Role
  ----------- ----------- -------------------------
  Blue        `#2391FF`   ข้อมูลหลักและองค์ประกอบสำคัญ
  Yellow      `#FFF83F`   การเน้นข้อมูล
  Orange      `#FFCD54`   การเปรียบเทียบและตัวชี้วัด
  Pink        `#F70063`   ประเด็นความเสี่ยง
  Dark Text   `#202938`   ข้อความหลัก

-   ใช้พื้นหลังขาวหรือเทาอ่อน
-   กระจายสีทั้ง 4 สีอย่างสมดุล
-   ใช้ฟอนต์ไทยหลักหนึ่งตระกูล
-   KPI Card มีตัวเลขเด่นและคำอธิบาย
-   หลีกเลี่ยงเงาหนักและกรอบหนา
-   ไม่ใช้ 3D Charts
-   มี Tooltip, Legend และหน่วยวัดตามความจำเป็น
-   รองรับ Desktop, Tablet และ Mobile

## 12. Data Outputs

ชื่อไฟล์ที่แนะนำสำหรับผลลัพธ์หลังทำความสะอาด:

``` text
data/processed/
├── ai_incidents_clean.csv
├── afnc_items_clean.csv
├── acsc_weekly_clean.csv
├── weekly_panel_clean.csv
└── weekly_panel_final.csv
```

ไฟล์ Mapping และ Metadata อาจจัดเก็บใน:

``` text
data/intermediate/
├── verdict_mapping.csv
├── financial_topic_rules.csv
└── data_quality_metadata.json
```

ชื่อและรูปแบบไฟล์สุดท้ายสามารถปรับตามสถาปัตยกรรมจริงได้

## 13. Documentation Deliverables

ต้องมีเอกสารแยกกันดังนี้:

  File                               Purpose
  ---------------------------------- -----------------------------------
  `BRD.md`                           ความต้องการทางธุรกิจและขอบเขตโครงการ
  `handoff.md`                       วิธีดูแล พัฒนา รัน และส่งมอบระบบ
  `DATA_DICTIONARY.md`               คำอธิบาย Dataset และคอลัมน์
  `DATA_INSPECTION_REPORT.md`        ผลตรวจสอบข้อมูลก่อน Cleaning
  `DATA_CLEANING_REPORT.md`          รายละเอียดการทำความสะอาด
  `DATA_INTEGRATION_REPORT.md`       ผลการรวมข้อมูลรายสัปดาห์
  `QA_TEST_REPORT.md`                ผลทดสอบ
  `FINAL_IMPLEMENTATION_REPORT.md`   สรุปสิ่งที่พัฒนาและสถานะส่งมอบ
  `README.md`                        ภาพรวมและวิธีเริ่มต้นใช้งาน

เอกสารต้องตรงกับการทำงานจริง ไม่เขียนว่ามีฟีเจอร์หรือผลลัพธ์แล้วหากยังไม่ได้พัฒนาและทดสอบ

## 14. Local Setup & Run

ให้ตรวจสอบ Framework และ Dependency ก่อนเลือกคำสั่ง

### 14.1 Python Project

หากใช้ Python ให้ตรวจสอบ `requirements.txt`, `pyproject.toml` หรือไฟล์จัดการ
Dependency ที่มีอยู่

ตัวอย่างการสร้าง Virtual Environment:

``` bash
python -m venv .venv
```

Windows:

``` bash
.venv\\Scripts\\activate
```

macOS / Linux:

``` bash
source .venv/bin/activate
```

ติดตั้ง Dependencies เมื่อมี `requirements.txt`:

``` bash
pip install -r requirements.txt
```

### 14.2 Streamlit

หากตรวจสอบแล้วว่าใช้ Streamlit และ Entry Point คือ `app.py`:

``` bash
streamlit run app.py
```

### 14.3 React / Vite

หากตรวจสอบแล้วว่าเป็นโปรเจกต์ Node.js ที่มี `package.json`:

``` bash
npm install
npm run dev
```

Production Build:

``` bash
npm run build
```

### 14.4 Next.js

ใช้คำสั่งตาม Scripts ที่กำหนดใน `package.json` โดยทั่วไป:

``` bash
npm install
npm run dev
```

Production Build:

``` bash
npm run build
```

> คำสั่งข้างต้นเป็นตัวอย่าง ต้องตรวจสอบ Entry Point และ Scripts ของ Repository
> ก่อนใช้งานจริง ห้ามสันนิษฐานว่าโปรเจกต์ใช้ Framework ใด Framework หนึ่ง

## 15. Testing & Quality Assurance

### 15.1 Data Tests

ตรวจสอบ:

-   Incident ID ไม่ซ้ำตามระดับข้อมูลที่กำหนด
-   post_id ไม่ซ้ำ
-   week_start มีรูปแบบถูกต้อง
-   วันและ Timezone ถูกต้อง
-   ตัวเลขอยู่ในชนิดข้อมูลที่เหมาะสม
-   Missing และ Zero แยกจากกัน
-   Verdict Mapping ครอบคลุมค่าจริง
-   Financial Classification ตรวจสอบย้อนกลับได้

### 15.2 Integration Tests

ตรวจสอบ:

-   วันเริ่มต้นสัปดาห์ตรงกัน
-   Weekly Join ไม่ทำให้จำนวนแถวเพิ่มโดยไม่ตั้งใจ
-   ไม่มี Duplicate Week ที่ไม่อธิบาย
-   Missing Reporting ไม่ถูกเติมเป็น Zero
-   Weekly Panel สอดคล้องกับข้อมูลต้นทาง

### 15.3 KPI Tests

ใช้ชุดข้อมูลขนาดเล็กที่กำหนดค่าไว้ใน Unit Tests เพื่อทดสอบสูตรได้
แต่ต้องไม่แสดงข้อมูลทดสอบเป็นผลจริงบน Dashboard

ทดสอบ:

-   Incident Count
-   Injury / Fatality Count
-   Annual Growth
-   Fake News Percentage
-   Average Views
-   Average Loss per Case
-   Pearson Correlation และจำนวนตัวอย่าง

### 15.4 UI Tests

ตรวจสอบ:

-   Navigation ทั้ง 3 Tabs
-   Filter แต่ละตัว
-   Multi-filter
-   Reset Filters
-   Search
-   Pagination
-   Empty State
-   Tooltip
-   Chart Selection เมื่อรองรับ
-   Responsive Layout

### 15.5 Test Reporting

สร้าง `reports/QA_TEST_REPORT.md` พร้อมแยก:

-   PASS
-   FAIL
-   NOT IMPLEMENTED
-   BLOCKED

รายงานเฉพาะการทดสอบที่ได้รันจริง

## 16. GitHub & CI/CD Handoff

### 16.1 Before Push

``` bash
git status
git branch --show-current
git remote -v
git diff --stat
```

ตรวจสอบ `.gitignore` และห้าม Commit:

-   `.env` ที่มี Secrets
-   API Keys
-   Passwords
-   Access Tokens
-   Credentials
-   ไฟล์ชั่วคราว
-   ไฟล์ขนาดใหญ่ที่ไม่จำเป็น

### 16.2 Commit & Push

หลังตรวจสอบและทดสอบ:

``` bash
git add .
git status
git commit -m "feat: build AI digital threat intelligence dashboard"
git push origin HEAD
```

-   ใช้ Branch ที่เหมาะสมกับ Repository
-   ห้าม Force Push
-   ห้ามเขียนทับ Remote History
-   หาก Push ไม่สำเร็จ ให้เก็บ Local Changes และรายงานสาเหตุ

### 16.3 GitHub Actions

สร้าง Workflow ใน `.github/workflows/` ตาม Framework จริง โดยควรทำงานดังนี้:

1.  Checkout Repository
2.  Setup Runtime
3.  Install Dependencies
4.  Validate Project Structure
5.  Run Data Validation Tests
6.  Run Unit / Integration Tests
7.  Build Application
8.  รายงานสถานะการทำงาน

ไม่ควร Deploy เมื่อ Critical Tests หรือ Build ล้มเหลว

### 16.4 Deployment

เลือก Hosting ให้ตรงกับสถาปัตยกรรม:

-   Static Frontend: สามารถพิจารณา GitHub Pages หรือ Static Hosting อื่น
-   Python Dashboard / Backend: ใช้ Hosting ที่รองรับ Python Runtime
    และการรัน Server
-   Full-stack Application: เลือก Hosting ที่รองรับทั้ง Frontend และ Backend

ข้อควรระวัง:

-   GitHub Pages ไม่ใช่ Python Application Server
-   ตรวจสอบว่า Dataset ที่ Deploy เป็นข้อมูลที่อนุญาตให้เผยแพร่
-   ห้ามเปิดเผย Secrets
-   ตั้งค่า Environment Variables ผ่านระบบจัดการ Secrets ของ Hosting
-   ตรวจสอบ URL และการโหลดข้อมูลหลัง Deploy

## 17. Operational Notes & Troubleshooting

  -----------------------------------------------------------------------
  ปัญหา                                แนวทางตรวจสอบ
  ----------------------------------- -----------------------------------
  ไม่พบ Dataset                        ตรวจสอบ Path, ชื่อไฟล์ และ Working
                                      Directory

  อ่าน Excel ไม่ได้                      ตรวจสอบชื่อ Sheet และ Library สำหรับ
                                      Excel

  วันที่กลายเป็น NaT                      ตรวจสอบ Format, Timezone
                                      และค่าที่ไม่ถูกต้อง

  จำนวนรายการเพิ่มหลัง Join              ตรวจสอบ Duplicate Key และระดับ
                                      Aggregation

  KPI ไม่ตรงกับตาราง                    ตรวจสอบ Filter Scope และนิยามการนับ

  Correlation เป็น N/A                 ตรวจสอบจำนวน Complete Cases
                                      และความแปรปรวนของตัวแปร

  กราฟไม่มีข้อมูล                         ตรวจสอบ Filter, Missing Values และ
                                      Empty State

  Git Push ถูกปฏิเสธ                    ตรวจสอบ Authentication, Permission
                                      และ Branch Protection

  Build ล้มเหลว                        ตรวจสอบ Dependency, Runtime Version
                                      และ Build Logs

  Deployment เปิดไม่ได้                  ตรวจสอบ Hosting Logs, Environment
                                      Variables และ Base Path
  -----------------------------------------------------------------------

## 18. Security & Data Governance

-   ห้าม Commit Secrets ลง Git
-   ใช้ Environment Variables สำหรับค่าลับ
-   จำกัดสิทธิ์การเข้าถึง Repository และ Hosting ตามความจำเป็น
-   ตรวจสอบสิทธิ์ในการเผยแพร่ Dataset
-   ไม่แสดงข้อมูลส่วนบุคคลที่ไม่จำเป็น
-   เก็บ Raw Data และ Processed Data แยกจากกัน
-   บันทึกแหล่งที่มาและขั้นตอนแปลงข้อมูล
-   ไม่กล่าวอ้างผลวิเคราะห์เกินกว่าข้อมูลรองรับ

## 19. Final Handoff Checklist

### Data

-   [ ] ตรวจสอบ Dataset จริงครบทุกไฟล์
-   [ ] เก็บ Raw Data ไว้
-   [ ] สร้าง Cleaned Datasets
-   [ ] จัดทำ Data Dictionary
-   [ ] ตรวจสอบ Weekly Integration
-   [ ] จัดทำ Data Cleaning Report
-   [ ] จัดทำ Data Integration Report

### Analytics

-   [ ] ตรวจสอบนิยาม KPI
-   [ ] ตรวจสอบการนับรายการไม่ซ้ำ
-   [ ] ตรวจสอบการจัดประเภท Verdict
-   [ ] ตรวจสอบ Financial Classification
-   [ ] ตรวจสอบ Pearson Correlation และ n
-   [ ] ระบุข้อจำกัดของข้อมูล

### Dashboard

-   [ ] AI Risk Analysis
-   [ ] Financial Fake News Analysis
-   [ ] Fake News & Online Scam Relationship
-   [ ] Functional Filters
-   [ ] Reset Filters
-   [ ] KPI และ Charts อัปเดตตาม Filter
-   [ ] Search และ Data Table
-   [ ] Empty State
-   [ ] Responsive Layout
-   [ ] Data Sources และ Notes

### Engineering

-   [ ] โค้ดแยกส่วนและดูแลต่อได้
-   [ ] Dependencies ระบุครบ
-   [ ] มีคำสั่ง Run ที่ตรวจสอบแล้ว
-   [ ] Automated Tests ทำงาน
-   [ ] GitHub Actions ทำงาน
-   [ ] ไม่มี Secrets ใน Git
-   [ ] Push สำเร็จหรือมีรายงาน Blocker
-   [ ] Deployment ผ่านการตรวจสอบหรือระบุสถานะชัดเจน

### Documentation

-   [ ] `BRD.md`
-   [ ] `handoff.md`
-   [ ] `DATA_DICTIONARY.md`
-   [ ] `README.md`
-   [ ] `DATA_INSPECTION_REPORT.md`
-   [ ] `DATA_CLEANING_REPORT.md`
-   [ ] `DATA_INTEGRATION_REPORT.md`
-   [ ] `QA_TEST_REPORT.md`
-   [ ] `FINAL_IMPLEMENTATION_REPORT.md`

## 20. Final Delivery Information

ผู้ส่งมอบควรเติมข้อมูลต่อไปนี้หลังตรวจสอบระบบจริง:

  รายการ                ค่าที่ต้องบันทึก
  --------------------- -----------------------
  GitHub Repository     URL จริง
  Active Branch         Branch ที่ใช้งานจริง
  Latest Commit         Commit Hash
  Framework / Version   ค่าที่ตรวจสอบจากโปรเจกต์
  Runtime Version       เวอร์ชันที่ใช้รัน
  Local Run Command     คำสั่งที่ทดสอบแล้ว
  Test Status           ผลการทดสอบจริง
  GitHub Actions        URL หรือสถานะ Workflow
  Hosting Provider      ผู้ให้บริการที่ใช้จริง
  Deployment URL        URL ที่เปิดใช้งานจริง
  Known Issues          ปัญหาที่ยังเหลือ
  Handoff Date          วันที่ส่งมอบ

**หลักการส่งมอบ:** ผู้รับงานต้องสามารถตรวจสอบที่มาของข้อมูล
ทำความสะอาดและสร้างผลวิเคราะห์ซ้ำ รัน Dashboard ทดสอบระบบ
และเข้าใจข้อจำกัดของข้อมูลได้ โดยไม่ต้องอาศัยการคาดเดาจากผู้พัฒนาคนเดิม
