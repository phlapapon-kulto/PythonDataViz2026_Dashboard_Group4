# Data Dictionary
## โครงการ: ภัยดิจิทัลยุค AI: วิเคราะห์ความเสี่ยงจากปัญญาประดิษฐ์ ข่าวปลอม และการหลอกลวงออนไลน์
**Date:** 2026-11-02  
**Version:** 1.0.0 (Production)  

---

## 1. Dataset A: AI Incident Database (`ai_incidents_clean.csv` / `ai_incidents.json`)

Source: `datasets/AIID_Excel_Export-20261019.xlsx` (Sheet: `Incidents`, Header at row 3)  
Granularity: 1 row per unique AI incident (1,749 rows)

| Original Column | Cleaned Column | Data Type | Description (คำอธิบาย) | Transformation (การแปลงข้อมูล) | Dashboard Usage (การใช้งานในแดชบอร์ด) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Incident ID` | `incident_id` | Integer | รหัสเฉพาะของเหตุการณ์ความเสี่ยง AI | ตรวจสอบความซ้ำซ้อน ไม่พบค่าซ้ำ (1 ถึง 1,749) | Primary Key, KPI นับเหตุการณ์รวม (Tab 1) |
| `date` | `date` | Date (ISO) | วันที่เกิดเหตุการณ์ (YYYY-MM-DD) | แปลงเป็น datetime มาตรฐาน ISO | ไทม์ไลน์และตัวกรองช่วงเวลา |
| `year` | `year` | Integer | ปี ค.ศ. ที่เกิดเหตุการณ์ | สกัดเป็นจำนวนเต็ม (1983–2026) | ตัวกรองปี, กราฟแนวโน้มรายปี, คำนวณ YoY Growth |
| *(Derived)* | `month` | String | ปี-เดือน (YYYY-MM) | สกัดจาก `date` | การวิเคราะห์ช่วงเวลา |
| *(Derived)* | `quarter` | String | ไตรมาส (เช่น 2024Q1) | แปลงเป็น Period Quarter | การวิเคราะห์ไตรมาส |
| `Risk Domain` | `risk_domain` | String | กลุ่มความเสี่ยงหลักจาก AI | ตัดช่องว่าง, ปรับมาตรฐาน 7 กลุ่มหลัก, ค่าว่างระบุ 'Unclassified' | กราฟ Top 5 Risk Domains, Donut Chart, ตัวกรอง |
| `Risk Subdomain`| `risk_subdomain`| String | กลุ่มความเสี่ยงย่อย | ตัดช่องว่าง, จัดการค่าว่างเป็น 'Unclassified' | การวิเคราะห์เจาะลึกความเสี่ยง |
| `Harm Domain` | `harm_domain` | String | การเกิดความเสียหายทางกายภาพ/สังคม | ปรับเป็นตัวพิมพ์เล็ก ('yes', 'no', 'maybe', 'unspecified') | ตัวกรอง Harm Domain |
| `Injuries` | `injuries` | Float | จำนวนผู้บาดเจ็บ | แปลงเป็นตัวเลข เก็บค่าว่างไว้ (ห้ามแทนที่ด้วย 0) | คำนวณเหตุการณ์ที่มีผู้บาดเจ็บ |
| `Lives Lost` | `lives_lost` | Float | จำนวนผู้เสียชีวิต | แปลงเป็นตัวเลข เก็บค่าว่างไว้ (ห้ามแทนที่ด้วย 0) | คำนวณเหตุการณ์ที่มีผู้เสียชีวิต |
| *(Derived)* | `has_injuries` | Boolean | มีผู้บาดเจ็บหรือไม่ | `True` เมื่อ `injuries > 0` | ตัวชี้วัดความรุนแรง |
| *(Derived)* | `has_fatalities`| Boolean | มีผู้เสียชีวิตหรือไม่ | `True` เมื่อ `lives_lost > 0` | ตัวชี้วัดความรุนแรง |
| *(Derived)* | `has_casualties`| Boolean | มีผู้บาดเจ็บหรือเสียชีวิต | `has_injuries == True \| has_fatalities == True` | KPI: Incidents with Casualties (21 เหตุการณ์) |
| `Location Region`| `location_region`| String | ภูมิภาคที่เกิดเหตุ | จัดมาตรฐาน 7 ภูมิภาคหลัก และ 'Unspecified' | กราฟ Regional Breakdown |
| `title` | `title` | String | พาดหัว/ชื่อเหตุการณ์ | ตัดช่องว่าง | กล่องค้นหาคำสำคัญ, Tooltips |
| `description` | `description` | String | รายละเอียดเหตุการณ์ | รักษาข้อความต้นฉบับ | กล่องค้นหาคำสำคัญ, Tooltips |
| `deployer` | `deployer` | String | องค์กร/ผู้ประยุกต์ใช้งาน AI | รักษาข้อความต้นฉบับ | ข้อมูลประกอบ |
| `developer` | `developer` | String | ผู้พัฒนาโมเดล/ระบบ AI | รักษาข้อความต้นฉบับ | ข้อมูลประกอบ |

---

## 2. Dataset B: Thai Financial Fake News (`afnc_items_clean.csv` / `financial_news.json`)

Source: `datasets/thai-disinfo-scam-dataset.xlsx` (Sheet: `afnc_items`)  
Granularity: 1 row per fact-checked article (17,726 rows total; 2,514 in primary financial category)

| Original Column | Cleaned Column | Data Type | Description (คำอธิบาย) | Transformation (การแปลงข้อมูล) | Dashboard Usage (การใช้งานในแดชบอร์ด) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `post_id` | `post_id` | Integer | รหัสเฉพาะของบทความบนเว็บไซต์ AFNC | ตรวจสอบความซ้ำซ้อน ไม่พบค่าซ้ำ (100% Unique) | Primary Key, KPI นับจำนวนข่าวที่ตรวจ (Tab 2) |
| `published_bkk` | `published_bkk` | Datetime | วันและเวลาเผยแพร่ตามเวลาประเทศไทย | แปลง timezone เป็น UTC+7 (Asia/Bangkok) | ไทม์ไลน์รายชั่วโมง/วัน |
| `date` | `date` | Date (ISO) | วันที่เผยแพร่ (YYYY-MM-DD) | แปลงเป็น datetime มาตรฐาน ISO | การจัดกลุ่มรายวันและตัวกรอง |
| `week_start` | `week_start` | Date (ISO) | วันอาทิตย์เริ่มต้นสัปดาห์ | ตรวจสอบความสอดคล้องกับปฏิทินสากล | Time Key สำหรับเชื่อมกับสถิติคดี (Tab 3) |
| `year` | `year` | Integer | ปี ค.ศ. ที่เผยแพร่ | สกัดจาก `date` (2019–2026) | ตัวกรองปีใน Tab 2 |
| `month` | `month` | String | ปี-เดือน (YYYY-MM) | สกัดจาก `date` | กราฟ Monthly Financial News Trend |
| `verdict_th` | `verdict_th` | String | ผลการตรวจสอบภาษาไทยจาก AFNC | รักษาคำทางการ ('ข่าวปลอม', 'ข่าวจริง', 'ข่าวบิดเบือน') | Badge แสดงผลในตาราง, กราฟ Donut |
| *(Derived)* | `verdict_group` | String | กลุ่มผลการตรวจสอบมาตรฐานสากล | จัดกลุ่มเป็น Fake, True, Distorted, Unverified | KPI: ข่าวปลอม, ข่าวบิดเบือน, คำนวณ Fake % |
| *(Derived)* | `is_false_or_distorted` | Boolean | เป็นข้อมูลเท็จหรือบิดเบือนหรือไม่ | `True` เมื่อ verdict เป็นข่าวปลอมหรือข่าวบิดเบือน | ตัวนับรวมสำหรับเชื่อมตารางรายสัปดาห์ (Tab 3) |
| `category_th` | `category_th` | String | หมวดหมู่ข่าวของศูนย์ต่อต้านข่าวปลอม | ตัดช่องว่าง (หมวดหลัก: 'การเงิน-หุ้น' มี 2,514 ข่าว) | การจำแนกประเภทข่าว, ตัวกรอง |
| *(Derived)* | `is_category_finance` | Boolean | เป็นข่าวในหมวดการเงิน-หุ้นหรือไม่ | `category_th == 'การเงิน-หุ้น'` | ตัวชี้วัดการเงินทางการ (Tier 1) |
| *(Derived)* | `is_keyword_finance` | Boolean | พาดหัว/แท็ก/เนื้อหามีคำค้นการเงินหรือไม่ | สแกน 22 คำค้น เช่น หุ้น, ลงทุน, กู้, สินเชื่อ, คริปโต | ตัวชี้วัดการเงินแบบกว้าง (Tier 2, 2,906 ข่าว) |
| *(Derived)* | `financial_relevance` | String | ระดับความเกี่ยวข้องด้านการเงิน | 'Primary Finance', 'Broad Finance', 'Non-Finance' | ความโปร่งใสในการคัดเลือกข้อมูล |
| `title` | `title` | String | พาดหัวข่าว | ตัดช่องว่าง | ค้นหาคำสำคัญ, แสดงผลในตารางข่าว |
| `topic_tags` | `topic_tags` | String | แท็กประเด็นข่าว คั่นด้วยเครื่องหมาย `;` | สกัดคำสำคัญตัดแท็กทั่วไปออก | กราฟ Top Fake Financial News Topics |
| `view_count` | `view_count` | Integer | ยอดเข้าชมหน้าเว็บ ณ วันที่ 1 พ.ย. 2026 | แปลงเป็นตัวเลขจำนวนเต็มบวก ตรวจสอบไม่พบค่าติดลบ | KPI: ยอดเข้าชมเฉลี่ย, กราฟ Top 10 Views |
| `url` | `url` | URL | ลิงก์ไปยังบทความต้นฉบับบนเว็บ AFNC | ตรวจสอบความถูกต้องของ URL | ปุ่มคลิกอ่านบทความจริงในตาราง |

---

## 3. Dataset C: Online Scam Statistics (`acsc_weekly_clean.csv`)

Source: `datasets/thai-disinfo-scam-dataset.xlsx` (Sheet: `acsc_weekly`)  
Granularity: 1 row per weekly briefing (48 rows from 2025-11-09 to 2026-10-18)

| Original Column | Cleaned Column | Data Type | Description (คำอธิบาย) | Transformation (การแปลงข้อมูล) | Dashboard Usage (การใช้งานในแดชบอร์ด) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `week_start` | `week_start` | Date (ISO) | วันเริ่มต้นรอบรายงานสัปดาห์ | ตรวจสอบวันอาทิตย์ (สัปดาห์ 2026-05-30 บันทึกหมายเหตุตรงกัน) | Primary Time Key |
| `week_end` | `week_end` | Date (ISO) | วันสิ้นสุดรอบรายงานสัปดาห์ | แปลงเป็น ISO Date | แสดงรอบเวลา |
| `days` | `days` | Integer | จำนวนวันในรอบรายงาน | ตรวจสอบความยาวสัปดาห์ (ส่วนใหญ่ 7 วัน) | ตรวจสอบคุณภาพ |
| `cases` | `cases` | Integer | จำนวนคดีแจ้งความออนไลน์ในรอบสัปดาห์ | ตรวจสอบค่าผิดปกติ (สัปดาห์ 16 ส.ค. 2026 = 79,311 คดี) | KPI: คดีหลอกลวงรายสัปดาห์, แผนภาพการกระจาย |
| `loss_baht` | `loss_baht` | Float | มูลค่าความเสียหายรวม (บาท) | ตรวจสอบค่าตัวเลข (ช่วง 128M ถึง 2.775B บาท) | KPI: มูลค่าความเสียหาย, แผนภาพการกระจาย |
| `loss_precision` | `loss_precision`| String | ความแม่นยำของตัวเลขความเสียหาย | 'exact' (ระบุถึงหลักบาท) หรือ 'rounded' (ตัวเลขกลม) | ป้ายกำกับความแม่นยำในตาราง |
| `loss_per_case_baht`| `loss_per_case_baht`| Integer | ความเสียหายเฉลี่ยต่อคดี (บาท) | คำนวณจาก `loss_baht / cases` | KPI: ความเสียหายเฉลี่ยต่อคดี |
| *(Derived)* | `is_suspect_outlier`| Boolean | เป็นสัปดาห์ที่มีตัวเลขผิดปกติหรือไม่ | `True` เมื่อ `week_start == '2026-08-16'` | สวิตช์ Sensitivity Analysis ใน Tab 3 |
| `top_type_th` | `top_type_th` | String | รูปแบบคดีหลอกลวงที่มีผู้เสียหายสูงสุด | รักษาข้อความต้นฉบับ | ข้อมูลประกอบในตารางรายสัปดาห์ |
| `highest_loss_type_th`| `highest_loss_type_th`| String | รูปแบบคดีที่มีมูลค่าความเสียหายสูงสุด | รักษาข้อความต้นฉบับ | ข้อมูลประกอบในตารางรายสัปดาห์ |
| `flag` / `notes` | `flag` / `notes` | String | หมายเหตุความผิดปกติหรือที่มาของตัวเลข | บันทึกคำเตือนกรณีตัวเลขขัดแย้งกับสัดส่วนในแถลงการณ์ | Tooltip เตือนความผิดปกติในตาราง |

---

## 4. Dataset D: Integrated Weekly Panel (`weekly_panel_final.csv` / `weekly_scams.json`)

Source: Merged panel from AFNC + ACSC  
Granularity: 1 row per reporting week from 2018-12-30 to 2026-10-25 (409 rows)

| Column Name | Data Type | Description (คำอธิบาย) | Quality Rules & Derivation | Dashboard Usage |
| :--- | :--- | :--- | :--- | :--- |
| `week_start` | Date (ISO) | วันอาทิตย์เริ่มต้นสัปดาห์ | ยึดตามปฏิทินสากล ต่อเนื่อง 409 สัปดาห์ | Time Key สำหรับแกนเวลา X |
| `year` / `month` | Int / String | ปีและเดือนของสัปดาห์ | สกัดจาก `week_start` | การจัดกลุ่มเวลา |
| `afnc_false_finance` | Integer | จำนวนข่าวปลอม+ข่าวบิดเบือนการเงินในสัปดาห์ | ตรงกับยอดรวมใน `afnc_items` (หมวดการเงิน-หุ้น) 100% | กราฟแนวโน้มคู่, แกน X แผนภาพการกระจาย |
| `acsc_reported` | Boolean | มีการรายงานสถิติคดีในสัปดาห์นั้นหรือไม่ | `True` เฉพาะ 48 สัปดาห์ (พ.ย. 2025–ต.ค. 2026) | ตัวกรองแถวที่มีข้อมูลครบสำหรับคำนวณสหสัมพันธ์ |
| `acsc_cases` | Integer | คดีหลอกลวงออนไลน์รายสัปดาห์ | ว่าง (null) ก่อน พ.ย. 2025 ห้ามเติม 0 | กราฟแนวโน้มคู่, แกน Y แผนภาพการกระจาย |
| `acsc_loss_baht` | Float | มูลค่าความเสียหายรายสัปดาห์ (บาท) | ว่าง (null) ก่อน พ.ย. 2025 ห้ามเติม 0 | แกน Y แผนภาพการกระจายความเสียหาย |
| `acsc_loss_per_case_baht` | Integer | ความเสียหายเฉลี่ยต่อคดี (บาท) | `acsc_loss_baht / acsc_cases` | ตารางและตัวชี้วัด |
| `is_outlier` | Boolean | ตัวชี้วัดสัปดาห์ผิดปกติ 16 ส.ค. 2026 | สัปดาห์ที่มีคดี 79,311 คดี (สูงกว่าปกติ 13 เท่า) | สวิตช์ Sensitivity Analysis |
"""

with open(r"c:\Users\USER\PythonDataViz2026_Dashboard_Group4\DATA_DICTIONARY.md", "w", encoding="utf-8") as f:
    f.write(CodeContent)

print("DATA_DICTIONARY.md generated successfully!")
