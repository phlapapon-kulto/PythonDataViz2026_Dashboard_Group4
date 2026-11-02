# Data Inspection Report

> สร้างอัตโนมัติโดย `python run_pipeline.py` ตัวเลขทุกค่ามาจากการรันจริง ห้ามแก้ไขด้วยมือ

## 1. ไฟล์และชีตที่พบ

พบ 13 ไฟล์ในโฟลเดอร์ `datasets/` ตัวเลขในวงเล็บคือจำนวนแถวรวมหัวตารางตามที่ Excel รายงาน

| ไฟล์ | ขนาด | ชีต (จำนวนแถว) |
| --- | --- | --- |
| AIID_Excel_Export-20260803.xlsx | 2.4 MB | Incidents (1,608), Reports (7,454), Entities (6,905), Data Dictionary (61), Coverage Map (8) |
| AIID_Excel_Export-20260810.xlsx | 2.4 MB | Incidents (1,621), Reports (7,490), Entities (6,984), Data Dictionary (61), Coverage Map (8) |
| AIID_Excel_Export-20260817.xlsx | 2.4 MB | Incidents (1,633), Reports (7,528), Entities (7,018), Data Dictionary (61), Coverage Map (8) |
| AIID_Excel_Export-20260824.xlsx | 2.4 MB | Incidents (1,644), Reports (7,606), Entities (7,053), Data Dictionary (61), Coverage Map (8) |
| AIID_Excel_Export-20260831.xlsx | 2.4 MB | Incidents (1,657), Reports (7,682), Entities (7,141), Data Dictionary (61), Coverage Map (8) |
| AIID_Excel_Export-20260907.xlsx | 2.5 MB | Incidents (1,666), Reports (7,704), Entities (7,262), Data Dictionary (61), Coverage Map (8) |
| AIID_Excel_Export-20260914.xlsx | 2.5 MB | Incidents (1,678), Reports (7,763), Entities (7,307), Data Dictionary (61), Coverage Map (8) |
| AIID_Excel_Export-20260921.xlsx | 2.5 MB | Incidents (1,692), Reports (7,793), Entities (7,343), Data Dictionary (61), Coverage Map (8) |
| AIID_Excel_Export-20260928.xlsx | 2.5 MB | Incidents (1,704), Reports (7,816), Entities (7,380), Data Dictionary (61), Coverage Map (8) |
| AIID_Excel_Export-20261005.xlsx | 2.5 MB | Incidents (1,714), Reports (7,842), Entities (7,412), Data Dictionary (61), Coverage Map (8) |
| AIID_Excel_Export-20261012.xlsx | 2.6 MB | Incidents (1,737), Reports (7,922), Entities (7,467), Data Dictionary (61), Coverage Map (8) |
| AIID_Excel_Export-20261019.xlsx | 2.6 MB | Incidents (1,752), Reports (7,957), Entities (7,510), Data Dictionary (61), Coverage Map (8) |
| thai-disinfo-scam-dataset.xlsx | 8.0 MB | README (24), weekly_panel (410), afnc_items (17,727), acsc_weekly (49), data_dictionary (31) |

## 2. โครงสร้างคอลัมน์ของชีตที่ใช้

### Incidents (snapshot ล่าสุด)

| คอลัมน์ | ชนิด | ค่าว่าง | % ค่าว่าง | ค่าไม่ซ้ำ |
| --- | --- | --- | --- | --- |
| Incident ID | int64 | 0 | 0.0 | 1,749 |
| date | datetime64[us] | 0 | 0.0 | 1,199 |
| year | int64 | 0 | 0.0 | 27 |
| title | str | 0 | 0.0 | 1,749 |
| description | str | 0 | 0.0 | 1,749 |
| deployer | str | 3 | 0.2 | 1,278 |
| developer | str | 1 | 0.1 | 718 |
| harmed | str | 2 | 0.1 | 1,678 |
| Editors | str | 0 | 0.0 | 23 |
| Implicated Systems | str | 549 | 31.4 | 794 |
| Date Modified | datetime64[us] | 516 | 29.5 | 1,157 |
| Editor Notes | str | 1,218 | 69.6 | 528 |
| Data Sources | str | 253 | 14.5 | 4 |
| report_count | int64 | 0 | 0.0 | 45 |
| Risk Domain | str | 253 | 14.5 | 7 |
| Risk Subdomain | str | 254 | 14.5 | 21 |
| Responsible Entity | str | 253 | 14.5 | 3 |
| Intent | str | 253 | 14.5 | 3 |
| Timing | str | 253 | 14.5 | 3 |
| AI Goal | str | 1,708 | 97.7 | 31 |
| AI Technology | str | 1,723 | 98.5 | 24 |
| AI Technology (Potential) | str | 1,720 | 98.3 | 23 |
| Technical Failure | str | 1,723 | 98.5 | 23 |
| Technical Failure (Potential) | str | 1,713 | 97.9 | 33 |
| Harm Domain | str | 1,549 | 88.6 | 3 |
| Tangible Harm | str | 1,549 | 88.6 | 5 |
| AI Harm Level | str | 1,549 | 88.6 | 5 |
| Rights Violation | str | 1,549 | 88.6 | 3 |
| Harm Distribution Basis | str | 1,543 | 88.2 | 42 |
| Lives Lost | float64 | 1,543 | 88.2 | 8 |
| Injuries | float64 | 1,543 | 88.2 | 9 |
| Sector of Deployment | str | 1,543 | 88.2 | 51 |
| Public Sector Deployment | str | 1,549 | 88.6 | 3 |
| Infrastructure Sectors | str | 1,543 | 88.2 | 14 |
| Location Region | str | 1,549 | 88.6 | 7 |
| Country Code | str | 1,606 | 91.8 | 27 |
| Location City | str | 1,695 | 96.9 | 42 |
| Incident Year | float64 | 1,549 | 88.6 | 20 |
| Incident Month | str | 1,589 | 90.9 | 15 |
| Incident Day | str | 1,639 | 93.7 | 31 |
| Intentional Harm | str | 1,551 | 88.7 | 4 |
| Autonomy Level | str | 1,549 | 88.6 | 4 |
| AI Task | str | 1,569 | 89.7 | 139 |
| AI Methods | str | 1,646 | 94.1 | 61 |
| AI System Description | str | 1,553 | 88.8 | 196 |
| Data Inputs | str | 1,556 | 89.0 | 166 |
| Involving Minor | str | 1,549 | 88.6 | 3 |
| Protected Characteristic | str | 1,549 | 88.6 | 3 |
| AI System | str | 1,549 | 88.6 | 3 |
| Detrimental Content | str | 1,549 | 88.6 | 3 |
| Impact on Critical Services | str | 1,549 | 88.6 | 3 |
| Multiple AI Interaction | str | 1,549 | 88.6 | 3 |
| Embedded | str | 1,549 | 88.6 | 3 |
| Entities | str | 1,549 | 88.6 | 200 |
| Physical Objects | str | 1,549 | 88.6 | 3 |
| Deployed | str | 1,549 | 88.6 | 3 |
| Estimated Date | float64 | 1,542 | 88.2 | 2 |
| Estimated Harm Quantities | float64 | 1,542 | 88.2 | 2 |
| Special Interest Intangible Harm | str | 1,549 | 88.6 | 3 |

### afnc_items

| คอลัมน์ | ชนิด | ค่าว่าง | % ค่าว่าง | ค่าไม่ซ้ำ |
| --- | --- | --- | --- | --- |
| post_id | int64 | 0 | 0.0 | 17,726 |
| published_bkk | str | 0 | 0.0 | 17,725 |
| date | str | 0 | 0.0 | 2,535 |
| week_start | datetime64[us] | 0 | 0.0 | 383 |
| year | int64 | 0 | 0.0 | 8 |
| month | str | 0 | 0.0 | 93 |
| item_type | str | 0 | 0.0 | 7 |
| verdict_th | str | 3,268 | 18.4 | 3 |
| verdict_en | str | 3,268 | 18.4 | 3 |
| verdict_source | str | 3,268 | 18.4 | 2 |
| category_th | str | 0 | 0.0 | 12 |
| category_en | str | 0 | 0.0 | 12 |
| checked_by_agency | str | 3,641 | 20.5 | 1,335 |
| title | str | 0 | 0.0 | 16,704 |
| content | str | 0 | 0.0 | 17,610 |
| topic_tags | str | 640 | 3.6 | 15,303 |
| view_count | int64 | 0 | 0.0 | 3,759 |
| url | str | 0 | 0.0 | 17,726 |

### acsc_weekly

| คอลัมน์ | ชนิด | ค่าว่าง | % ค่าว่าง | ค่าไม่ซ้ำ |
| --- | --- | --- | --- | --- |
| week_start | datetime64[us] | 0 | 0.0 | 48 |
| week_end | datetime64[us] | 0 | 0.0 | 48 |
| days | int64 | 0 | 0.0 | 2 |
| cases | int64 | 0 | 0.0 | 48 |
| loss_baht | int64 | 0 | 0.0 | 47 |
| loss_precision | str | 0 | 0.0 | 2 |
| loss_per_case_baht | int64 | 0 | 0.0 | 48 |
| cases_change_vs_prev_week | float64 | 2 | 4.2 | 45 |
| loss_change_vs_prev_week_baht | float64 | 2 | 4.2 | 46 |
| top_type_th | str | 2 | 4.2 | 8 |
| top_type_case_share_pct | float64 | 11 | 22.9 | 32 |
| highest_loss_type_th | str | 3 | 6.2 | 15 |
| highest_loss_type_loss_baht | float64 | 21 | 43.8 | 27 |
| flag | str | 44 | 91.7 | 4 |
| publisher | str | 0 | 0.0 | 21 |
| article_date | str | 0 | 0.0 | 48 |
| source_url | str | 0 | 0.0 | 48 |
| notes | str | 0 | 0.0 | 48 |

### weekly_panel

| คอลัมน์ | ชนิด | ค่าว่าง | % ค่าว่าง | ค่าไม่ซ้ำ |
| --- | --- | --- | --- | --- |
| week_start | datetime64[us] | 0 | 0.0 | 409 |
| week_end | datetime64[us] | 0 | 0.0 | 409 |
| year | int64 | 0 | 0.0 | 9 |
| month | str | 0 | 0.0 | 95 |
| afnc_verdicts | int64 | 0 | 0.0 | 56 |
| afnc_fake | int64 | 0 | 0.0 | 43 |
| afnc_distorted | int64 | 0 | 0.0 | 16 |
| afnc_true | int64 | 0 | 0.0 | 26 |
| afnc_false_share_pct | float64 | 27 | 6.6 | 126 |
| afnc_false_gov_policy | int64 | 0 | 0.0 | 28 |
| afnc_false_health | int64 | 0 | 0.0 | 26 |
| afnc_false_finance | int64 | 0 | 0.0 | 21 |
| afnc_false_disaster | int64 | 0 | 0.0 | 12 |
| afnc_false_security | int64 | 0 | 0.0 | 16 |
| afnc_false_other | int64 | 0 | 0.0 | 15 |
| afnc_online_crime_advisories | int64 | 0 | 0.0 | 5 |
| acsc_reported | bool | 0 | 0.0 | 2 |
| acsc_cases | float64 | 361 | 88.3 | 48 |
| acsc_loss_baht | float64 | 361 | 88.3 | 47 |
| acsc_loss_precision | str | 361 | 88.3 | 2 |
| acsc_loss_per_case_baht | float64 | 361 | 88.3 | 48 |
| acsc_top_type_th | str | 363 | 88.8 | 8 |
| acsc_top_type_case_share_pct | float64 | 372 | 91.0 | 32 |
| acsc_highest_loss_type_th | str | 364 | 89.0 | 15 |
| acsc_highest_loss_type_loss_baht | float64 | 382 | 93.4 | 27 |
| acsc_flag | str | 405 | 99.0 | 4 |
| acsc_source_url | str | 361 | 88.3 | 48 |

## 3. คำเตือนจากผู้จัดทำชุดข้อมูล (ชีต README)

- Thai Disinformation & Online Scam Weekly Dataset
- Compiled 1 November 2026. Weekly panel 2018-12-30 to 2026-10-31.
- What is in it
- weekly_panel 409 weeks (Sunday–Saturday). AFNC verdict counts for every week; ACSC scam cases and losses for the 48 weeks with a published figure (2025-11-09 to 2026-10-24).
- afnc_items 17,726 Anti-Fake News Center posts, one row per post, including 14,458 verdicts.
- acsc_weekly 48 ACSC weekly briefings with source articles.
- data_dictionary Every column explained.
- Sources
- Anti-Fake News Center Thailand (Ministry of Digital Economy and Society) Official open-data export at opendata.antifakenewscenter.com, downloaded 1 Nov 2026. No licence is stated on the portal.
- Anti Online Scam Operation Center (ACSC), Royal Thai Police Weekly briefings on cases filed via Thaipoliceonline, compiled from Thai news reports and the Royal Thai Police press-release site (saranitet.police.go.th), one URL per row. Not published as open data. The centre was renamed ศตฉอ.ตร. in October 2026.
- Things to know before analysing
- 1 AFNC counts are verdicts the centre chose to publish, not the amount of fake news circulating.
- 2 ACSC figures are reported cases, which undercount scams. Some losses are rounded in the news; see acsc_loss_precision.
- 3 Weeks without an ACSC figure are blank, not zero. Do not fill them with 0.
- 4 2019 is sparse: the AFNC opened on 1 Nov 2019, and earlier posts are few.
- 5 view_count is a snapshot taken on 1 Nov 2026, so older posts have had longer to collect views.
- 6 Dates are Gregorian (CE). The source data used Buddhist Era dates (BE = CE + 543).
- 7 ACSC weekly briefings began with the week of 9-15 Nov 2025. Weeks with no figure found: 14-20 Jun 2026 and 26 Jul-1 Aug 2026. 25-31 Oct 2026 had not been announced when this was compiled.
- 8 16-22 Aug 2026 is flagged: the published 79,311 cases and 2,775 million baht look like an error in the release. Exclude it or show it with a note.
- 9 From 9-15 Aug 2026 the news gave losses rounded to the million; earlier weeks are exact to the baht.
- 10 The briefings' stated 'change vs last week' often differs from the gap between consecutive weekly totals, because ACSC compares against revised figures. acsc_weekly keeps the stated changes; recompute changes from the totals for charts.
