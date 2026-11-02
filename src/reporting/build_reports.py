"""Write the inspection, cleaning and integration reports from recorded results.

Every number comes from the quality log or from analytics, so a report cannot
drift away from the data it describes.
"""
from __future__ import annotations

import pandas as pd

from src.analytics.scam_correlation_analysis import RELABEL_MONTH, sensitivity_table
from src.config import EXTENDED_SCOPE_REVIEW, REPORTS_DIR, SNAPSHOT_AUDIT
from src.data_cleaning.common import QualityLog

GENERATED = "> สร้างอัตโนมัติโดย `python run_pipeline.py` ตัวเลขทุกค่ามาจากการรันจริง ห้ามแก้ไขด้วยมือ"


def table(headers: list[str], rows: list[list]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + " --- |" * len(headers)]
    lines += ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join(lines)


def write(name: str, title: str, body: list[str]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    text = "\n\n".join([f"# {title}", GENERATED, *body]) + "\n"
    (REPORTS_DIR / name).write_text(text, encoding="utf-8", newline="\n")


def inspection_report(log: QualityLog) -> None:
    facts = log.facts["inspection"]
    files = facts["files"]
    rows = [
        [f["file"], f"{f['size_bytes'] / 1e6:.1f} MB", ", ".join(f"{s['sheet']} ({s['rows']:,})" for s in f["sheets"])]
        for f in files
    ]
    body = [
        "## 1. ไฟล์และชีตที่พบ",
        f"พบ {len(files)} ไฟล์ในโฟลเดอร์ `{facts['raw_dir']}/` ตัวเลขในวงเล็บคือจำนวนแถวรวมหัวตารางตามที่ Excel รายงาน",
        table(["ไฟล์", "ขนาด", "ชีต (จำนวนแถว)"], rows),
        "## 2. โครงสร้างคอลัมน์ของชีตที่ใช้",
    ]
    names = {"Incidents": "Incidents (snapshot ล่าสุด)", "afnc_items": "afnc_items", "acsc_weekly": "acsc_weekly", "weekly_panel": "weekly_panel"}
    for key, label in names.items():
        profile = facts["profiles"][key]
        body += [f"### {label}", table(
            ["คอลัมน์", "ชนิด", "ค่าว่าง", "% ค่าว่าง", "ค่าไม่ซ้ำ"],
            [[p["column"], p["dtype"], f"{p['missing']:,}", p["missing_pct"], f"{p['unique']:,}"] for p in profile],
        )]
    body += ["## 3. คำเตือนจากผู้จัดทำชุดข้อมูล (ชีต README)", "\n".join(f"- {line}" for line in facts["source_readme"])]
    write("DATA_INSPECTION_REPORT.md", "Data Inspection Report", body)


def cleaning_report(log: QualityLog) -> None:
    ai, afnc, acsc, panel = (log.facts[k] for k in ("ai", "afnc", "acsc", "panel"))
    steps = table(
        ["ชุดข้อมูล", "ขั้นตอน", "แถวก่อน", "แถวหลัง", "เหตุผล"],
        [[s["dataset"], s["action"], f"{s['rows_before']:,}", f"{s['rows_after']:,}", s["reason"]] for s in log.steps],
    )
    audit = pd.read_csv(SNAPSHOT_AUDIT, encoding="utf-8-sig")
    audit_rows = [
        [r.snapshot, f"{r.rows:,}", f"{r.unique_incident_ids:,}", "" if pd.isna(r.new_ids_vs_previous) else int(r.new_ids_vs_previous),
         "" if pd.isna(r.removed_ids_vs_previous) else int(r.removed_ids_vs_previous), r.max_incident_date, r.without_risk_domain]
        for r in audit.itertuples()
    ]
    review = pd.read_csv(EXTENDED_SCOPE_REVIEW, encoding="utf-8-sig")
    hits = int(review["relevant_to_finance"].sum())
    body = [
        "## 1. จำนวนแถวก่อนและหลังทำความสะอาด",
        "ไม่มีการลบแถวในทุกชุดข้อมูล ไฟล์ใน `datasets/` ไม่ถูกแก้ไข ผลลัพธ์อยู่ใน `data/processed/` และ `data/intermediate/`",
        steps,
        "## 2. AI Incident Database",
        f"- ใช้ไฟล์ `{ai['source_file']}` เพราะ `{ai['file_named_in_docs']}` ที่เอกสารระบุไม่มีอยู่จริง",
        f"- Incident ID ว่าง {ai['incident_id_nulls']} แถว ซ้ำ {ai['incident_id_duplicates']} แถว",
        f"- เลข ID ที่ไม่มีในฐานข้อมูล {len(ai['unused_incident_ids'])} เลข: {ai['unused_incident_ids']} จึงมี {ai['rows_clean']:,} แถว ไม่ใช่เท่ากับ ID สูงสุด",
        f"- วันที่แปลงไม่ได้ {ai['unparseable_dates']} แถว ปีไม่ตรงกับวันที่ {ai['year_disagrees_with_date']} แถว ช่วงข้อมูล {ai['date_min']} ถึง {ai['date_max']}",
        f"- ไม่มี Risk Domain {ai['without_risk_domain']:,} แถว ไม่มี Risk Subdomain {ai['without_risk_subdomain']:,} แถว",
        f"- ไม่มี Location Region {ai['without_location_region']:,} แถว และ Harm Domain {ai['without_harm_domain']:,} แถว โดยปีสุดท้ายที่มีภูมิภาคคือ {ai['last_year_with_region']}",
        f"- ข้อมูลผู้บาดเจ็บหรือเสียชีวิตมี {ai['casualty_coded']} แถว ในจำนวนนี้มีค่ามากกว่า 0 อยู่ {ai['casualty_positive']} แถว ค่าว่างคงเป็นค่าว่าง",
        f"- แถวที่ Country Code เป็นไทย: {ai['thai_country_code_rows']} แถว จึงไม่เรียกข้อมูลนี้ว่าเหตุการณ์ในไทย",
        "- ค่าสูงสุดของผู้บาดเจ็บ เช่น 55,000 ราย คงไว้ เพราะเป็นค่าที่แหล่งข้อมูลบันทึก และเป็นตัวเลขสะสมของบางเหตุการณ์ KPI ใช้การนับเหตุการณ์ จึงไม่ถูกค่านี้ดึง",
        "### การเปรียบเทียบ Snapshot",
        f"ทั้ง {ai['snapshot_count']} ไฟล์ใช้เพื่อตรวจการเปลี่ยนแปลงเท่านั้น หากบวกแถวรวมกันจะได้ {ai['rows_if_snapshots_were_wrongly_summed']:,} แถวซึ่งผิด ไม่มี ID ใดหายไประหว่างไฟล์ ({ai['ids_removed_between_snapshots']} รายการ)",
        table(["Snapshot", "แถว", "ID ไม่ซ้ำ", "ID ใหม่", "ID ที่หาย", "วันที่เหตุการณ์ล่าสุด", "ไม่มี Risk Domain"], audit_rows),
        "## 3. AFNC",
        f"- post_id ว่าง {afnc['post_id_nulls']} แถว ซ้ำ {afnc['post_id_duplicates']} แถว ช่วงข้อมูล {afnc['date_min']} ถึง {afnc['date_max']}",
        f"- วันที่ไม่ตรงกับเวลาเผยแพร่ {afnc['date_disagrees_with_published']} แถว และ week_start ไม่ตรงกับวันที่ {afnc['week_start_disagrees_with_date']} แถว",
        f"- จำนวนตามกลุ่มผลตรวจสอบ: {afnc['verdict_counts']} และไม่มีค่า verdict นอกเหนือจากที่แมปไว้ ({afnc['unexpected_verdict_values']})",
        f"- โพสต์ซ้ำชื่อเดิม {afnc['same_title_reposts_kept']:,} รายการถูกคงไว้ เพราะมี post_id ของตัวเอง และทำเครื่องหมายใน `is_repost`",
        f"- ยอดเข้าชมไม่ถูกต้อง {afnc['invalid_view_counts']} แถว ค่าสูงสุด {afnc['view_count_max']:,} คงไว้",
        f"- ข้อความ `content` ในไฟล์ถูกตัดที่ {afnc['content_max_length_in_workbook']} ตัวอักษร จึงไม่ใช้ตัดสินขอบเขตข่าวการเงิน รายการที่ตรงเฉพาะใน content มี {afnc['content_only_hits_not_counted']:,} รายการ ไม่นับ และไม่เก็บคอลัมน์นี้ใน processed เพื่อลดขนาดไฟล์",
        f"- ขอบเขตหลัก {afnc['finance_core_rows']:,} รายการ ขอบเขตขยาย {afnc['finance_extended_rows']:,} รายการ แยกตามที่มา: {afnc['finance_extended_by_field']}",
        f"- สุ่มอ่านขอบเขตขยายนอกหมวดหลัก {len(review)} รายการ (seed 2026) ตรงประเด็น {hits} รายการ ({hits / len(review) * 100:.1f}%) ผลอยู่ใน `data/intermediate/extended_scope_review_sample.csv`",
        "## 4. ACSC",
        f"- week_end ที่ไม่ใช่วันเสาร์ {acsc['week_end_not_saturday']} แถว ใช้ week_end ลบ 6 วันเป็นคีย์สัปดาห์",
        f"- สัปดาห์ที่ปรับแนว: {acsc['weeks_realigned_to_sunday']}",
        f"- สัปดาห์ซ้ำ {acsc['week_key_duplicates']} แถว ค่าติดลบ คดี {acsc['negative_cases']} ความเสียหาย {acsc['negative_loss']} สัปดาห์ที่รายงานศูนย์ {acsc['zero_case_weeks']}",
        f"- ความแม่นยำของความเสียหาย: {acsc['loss_precision_counts']}",
        f"- สถานะคุณภาพ: {acsc['quality_status_counts']} สัปดาห์น่าสงสัยคงไว้ในข้อมูล แต่ไม่นำเข้าสถิติโดยค่าเริ่มต้น",
        "## 5. Weekly Panel ที่ให้มา",
        f"- {panel['rows']} สัปดาห์ ช่วง {panel['week_min']} ถึง {panel['week_max']} สัปดาห์ซ้ำ {panel['week_start_duplicates']} ไม่ใช่วันอาทิตย์ {panel['week_start_not_sunday']} ไม่ต่อเนื่อง {panel['weeks_not_consecutive']}",
        "## 6. ผลการตรวจสอบหลังทำความสะอาด",
        table(["รายการตรวจ", "ผล"], [[r["check"], "PASS" if r["passed"] else "FAIL"] for r in log.facts["validation"]["results"]]),
    ]
    write("DATA_CLEANING_REPORT.md", "Data Cleaning Report", body)


def integration_report(log: QualityLog, items: pd.DataFrame, final: pd.DataFrame) -> None:
    facts = log.facts["integration"]
    sensitivity = sensitivity_table(final, items)
    months = sorted(set(facts["online_crime_verdicts_by_month"]) | set(facts["core_finance_by_month_2025_11_on"]))
    relabel = [
        [m, facts["core_finance_by_month_2025_11_on"].get(m, 0), facts["online_crime_verdicts_by_month"].get(m, 0)]
        for m in months
    ]
    def fmt(value) -> str:
        return "N/A" if pd.isna(value) else f"{value:+.3f}"
    body = [
        "## 1. กติกาการเชื่อมข้อมูล",
        "- คีย์คือ `week_start` วันอาทิตย์ สัปดาห์อาทิตย์ถึงเสาร์ตามที่ ACSC รายงาน",
        "- สร้าง panel ใหม่จาก `afnc_items` และ `acsc_weekly` แล้วใช้ `weekly_panel` เป็นตัวตรวจ ไม่ถือเป็นแหล่งที่ถูกต้องโดยอัตโนมัติ",
        "- ข่าวเท็จคือ ข่าวปลอม + ข่าวบิดเบือน ตรงกับนิยาม `afnc_false_finance` ของ panel",
        "- ใช้ left join บนสัปดาห์ทั้งหมด และตรวจแบบ one-to-one แถวจึงเพิ่มไม่ได้",
        "## 2. ผลการจับคู่",
        table(["รายการ", "ค่า"], [
            ["สัปดาห์ใน spine", facts["spine_weeks"]],
            ["สัปดาห์ใน weekly_panel", facts["panel_weeks"]],
            ["แถว ACSC", facts["acsc_rows"]],
            ["แถว ACSC ที่จับคู่ได้", facts["acsc_weeks_matched"]],
            ["แถว ACSC ที่จับคู่ไม่ได้", facts["acsc_rows_unmatched"]],
            ["จับคู่ได้ถ้าใช้ week_start ดิบ (ผิด)", facts["matched_if_raw_week_start_were_used"]],
            ["เซลล์ที่ต่างจาก weekly_panel", facts["panel_cell_differences"]],
        ]),
        f"สถานะรายงาน: {facts['reporting_status_counts']}",
        f"สัปดาห์ในช่วง ACSC ที่ไม่มีตัวเลข: {', '.join(facts['weeks_without_figure_in_window'])} คงเป็นค่าว่าง ไม่เติมศูนย์",
        "## 3. การย้ายหมวดข่าวที่กระทบการตีความ",
        f"คำตัดสินรายการแรกในหมวดอาชญากรรมออนไลน์อยู่ในเดือน {facts['online_crime_verdict_first_month']} และเพิ่มเป็นจำนวนมากตั้งแต่ {RELABEL_MONTH} ขณะที่หมวดการเงิน-หุ้นลดลงอย่างรวดเร็ว และจำนวนคำตัดสินรวมต่อเดือนยังคงเดิม รูปแบบนี้สอดคล้องกับการจัดหมวดใหม่ แต่ไม่พบเอกสารยืนยันจากแหล่งข้อมูล",
        table(["เดือน", "โพสต์หมวดการเงิน-หุ้น", "คำตัดสินหมวดอาชญากรรมออนไลน์"], relabel),
        "## 4. Pearson correlation ภายใต้นิยามต่าง ๆ",
        table(
            ["นิยาม", "r กับคดี", "n", "r กับความเสียหาย", "n"],
            [[r.label, fmt(r.r_cases), r.n_cases, fmt(r.r_loss), r.n_loss] for r in sensitivity.itertuples()],
        ),
        "แถวแรกคือคำตอบตามนิยาม BRD แถวอื่นใช้ประเมินความมั่นคงของคำตอบ ค่าเป็นบวกในแถวแรกมาจากแนวโน้มระยะยาวที่ลดลงพร้อมกัน เมื่อดูก่อนการเปลี่ยนหมวดหรือดูการเปลี่ยนแปลงรายสัปดาห์ ความสัมพันธ์เชิงบวกหายไป จึงสรุปเป็นเหตุและผลไม่ได้",
    ]
    write("DATA_INTEGRATION_REPORT.md", "Data Integration Report", body)


def run(log: QualityLog, items: pd.DataFrame, final: pd.DataFrame) -> None:
    inspection_report(log)
    cleaning_report(log)
    integration_report(log, items, final)
