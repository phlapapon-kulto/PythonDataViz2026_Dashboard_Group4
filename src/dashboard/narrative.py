"""Text computed from filtered data: insight lines, KPI tiles and active-filter chips."""
from __future__ import annotations

import pandas as pd
from dash import html

from src.analytics import ai_risk_analysis as ai
from src.analytics import financial_news_analysis as news
from src.analytics import scam_correlation_analysis as rel
from src.analytics.ai_risk_analysis import MISSING
from src.dashboard import components as c
from src.dashboard import state as s
from src.dashboard import theme as t
from src.data_cleaning.clean_ai_incidents import HARM_TH, REGION_TH, RISK_DOMAIN_TH, RISK_SUBDOMAIN_TH
from src.data_cleaning.clean_fake_news import OTHER_TOPIC, TOPIC_RULES

TOPIC_TH = {r["topic_id"]: r["topic_th"] for r in TOPIC_RULES} | {OTHER_TOPIC["topic_id"]: OTHER_TOPIC["topic_th"]}


def mark(text: str) -> html.Mark:
    return html.Mark(text)


def year_chip(years: list[int]) -> list[str]:
    low, high = years
    if [low, high] == [s.YEAR_SLIDER_MIN, s.YEAR_SLIDER_MAX]:
        return []
    if low == high:
        return [f"ปี {low} (ทุกแท็บ)"]
    left = f"≤{low}" if low == s.YEAR_SLIDER_MIN else low
    return [f"ปี {left}–{high} (ทุกแท็บ)"]


def ai_chips(years, regions, domains, harm, subdomain, month) -> list[str]:
    chips = year_chip(years)
    if month:
        chips.append(f"เดือน {t.th_month(month)}")
    chips += [f"ความเสี่ยง: {'ยังไม่จำแนก' if d == MISSING else RISK_DOMAIN_TH.get(d, d)}" for d in domains or []]
    if subdomain:
        chips.append(f"กลุ่มย่อย: {RISK_SUBDOMAIN_TH.get(subdomain, subdomain)}")
    chips += [f"ภูมิภาค: {'ไม่มีข้อมูล' if r == MISSING else REGION_TH.get(r, r)}" for r in regions or []]
    chips += [f"Harm Domain: {'ไม่มีข้อมูล' if h == MISSING else HARM_TH.get(h, h)}" for h in harm or []]
    return chips


def news_scope_name(scope: str) -> str:
    return {
        news.SCOPE_CORE: "การเงิน หมวดหลัก", news.SCOPE_EXTENDED: "การเงิน ขอบเขตขยาย", news.SCOPE_ALL: "ทุกหมวด",
    }.get(scope, scope)


def news_chips(years, scope, verdicts, start, end, defaults, keyword, month, topic, post, titles) -> list[str]:
    chips = year_chip(years)
    if scope != news.SCOPE_CORE:
        chips.append(f"หมวด: {news_scope_name(scope)}")
    chips += [f"ผล: {t.VERDICT_TH.get(v, v)}" for v in verdicts or []]
    if start != defaults["news_start"] or end != defaults["news_end"]:
        chips.append(f"{t.th_date(start)} – {t.th_date(end)}")
    if month:
        chips.append(f"เดือน {t.th_month(month)}")
    if keyword:
        chips.append(f"คำค้น: {keyword}")
    if topic:
        chips.append(f"ประเด็น: {TOPIC_TH.get(topic, topic)}")
    if post:
        chips.append(f"ข่าว: {titles.get(post, post)}")
    return chips


def rel_chips(years, start, end, defaults, scope, topic, cases, loss, options, week) -> list[str]:
    chips = year_chip(years)
    if start != defaults["rel_start"] or end != defaults["rel_end"]:
        chips.append(f"{t.th_date(start)} – {t.th_date(end)}")
    if scope == rel.SCOPE_EXTENDED:
        chips.append("ขอบเขตขยาย")
    if topic:
        chips.append(f"ประเด็น: {TOPIC_TH.get(topic, topic)}")
    if cases != s.CASES_SLIDER:
        chips.append(f"คดี {cases[0]:,}–{cases[1]:,}")
    if loss != s.LOSS_SLIDER:
        chips.append(f"ความเสียหาย {loss[0]:,}–{loss[1]:,} ล้านบาท")
    if s.OPT_SUSPECT in (options or []):
        chips.append("รวมสัปดาห์น่าสงสัย")
    if s.OPT_EXACT in (options or []):
        chips.append("ความเสียหายแบบแม่นยำถึงบาท")
    if week:
        chips.append(f"สัปดาห์ {t.th_week(week)}")
    return chips


def ai_insight(filtered: pd.DataFrame, without_domain: pd.DataFrame, domains: list | None, growth: dict) -> list:
    """Name the leading domain, or the size of the selection when domains are chosen."""
    top = ai.top_risk_domains(without_domain, 1)
    if top.empty:
        return ["ไม่พบเหตุการณ์ที่จำแนกความเสี่ยงแล้วในตัวกรองนี้"]
    if domains:
        classified = ai.count_incidents(without_domain[without_domain["risk_domain"].notna()])
        count = ai.count_incidents(filtered)
        share = count / classified * 100 if classified else 0
        parts: list = ["ประเภทที่เลือกมี ", mark(f"{count:,} เหตุการณ์"), f" คิดเป็น {share:.1f}% ของเหตุการณ์ที่จำแนกแล้ว"]
    else:
        row = top.iloc[0]
        parts = [
            mark(row["risk_domain_th"]), " คือความเสี่ยงที่พบมากที่สุด ",
            f"{row['incidents']:,} เหตุการณ์ หรือ {row['share_pct']:.1f}% ของเหตุการณ์ที่จำแนกแล้ว",
        ]
    if growth["pct"] is not None:
        direction = "เพิ่มขึ้น" if growth["pct"] >= 0 else "ลดลง"
        scope = "ช่วงเดียวกันของ" if growth["same_period"] else ""
        parts.append(f" ปี {growth['year']} {direction} {abs(growth['pct']):.1f}% จาก{scope}ปี {growth['previous_year']}")
    return parts


def ai_kpis(filtered: pd.DataFrame, growth: dict) -> list:
    casualty = ai.casualty_summary(filtered)
    count = ai.count_incidents(filtered)
    if growth["pct"] is None:
        growth_note = f"ปี {growth['previous_year']} ไม่มีเหตุการณ์ในตัวกรองนี้"
    elif growth["same_period"]:
        growth_note = f"{growth['current']:,} เทียบ {growth['previous']:,} ช่วงเดียวกันของปี {growth['previous_year']}"
    else:
        growth_note = f"{growth['year']} เทียบ {growth['previous_year']} ({growth['current']:,} เทียบ {growth['previous']:,})"
    coded = fmt_coverage(casualty)
    return [
        c.kpi("จำนวนเหตุการณ์ AI", t.fmt_int(count), "นับ Incident ID ไม่ซ้ำ", hero=True, span=4),
        c.kpi("มีผู้บาดเจ็บหรือเสียชีวิต", t.fmt_int(casualty["positive"]) if casualty["coded"] else "N/A", coded, span=3),
        c.kpi("การเปลี่ยนแปลงรายปี", t.fmt_pct(growth["pct"], signed=True), growth_note, span=3),
        c.kpi("ประเภทความเสี่ยง", t.fmt_int(ai.count_risk_domains(filtered)), "Risk Domain ที่มีข้อมูล", span=2),
    ]


def fmt_coverage(casualty: dict) -> str:
    if not casualty["coded"]:
        return "ไม่มีข้อมูลผู้บาดเจ็บหรือเสียชีวิตในตัวกรองนี้"
    return f"จาก {casualty['coded']:,} เหตุการณ์ที่มีข้อมูล ({t.fmt_pct(casualty['coded_pct'])} ของทั้งหมด)"


def ai_coverage_warning(regions, harm, coverage: dict) -> str | None:
    if not regions and not harm:
        return None
    return (
        f"ตัวกรองนี้ใช้ข้อมูลจาก CSET ซึ่งลงรหัสไว้ {coverage['pct']:.1f}% ของเหตุการณ์ "
        f"และไม่มีข้อมูลตั้งแต่ปี {coverage['next_year']} ผลที่เห็นจึงไม่แทนเหตุการณ์ทั้งหมด"
    )


def news_insight(all_categories: pd.DataFrame, scoped: pd.DataFrame, scope: str) -> list:
    if all_categories.empty:
        return ["ไม่พบข่าวปลอมหรือข่าวบิดเบือนในตัวกรองนี้"]
    top = all_categories.iloc[0]
    parts: list = [
        "หมวดที่พบข่าวเท็จมากที่สุดคือ ", mark(top["category_th"]), f" {int(top['total']):,} รายการ",
    ]
    finance = all_categories[all_categories["category_th"] == news.FINANCE_CORE_CATEGORY]
    if len(finance):
        row = finance.iloc[0]
        rank = int(finance.index[0]) + 1
        if rank == 1:
            parts.append(f" และ {row['false_share_pct']:.1f}% ของคำตัดสินในหมวดนี้เป็นข่าวเท็จ")
        else:
            parts.append(f" ส่วนหมวดการเงิน-หุ้นอยู่อันดับ {rank} แต่ {row['false_share_pct']:.1f}% ของคำตัดสินในหมวดเป็นข่าวเท็จ")
    topics = news.false_by_topic(scoped)
    if news.scope_is_finance(scope) and len(topics):
        head = topics.iloc[0]
        parts.append(f" ประเด็นที่พบมากคือ{head['finance_topic']} {int(head['posts']):,} รายการ")
    return parts


def news_kpis(kpi: dict, scope: str) -> list:
    finance = news.scope_is_finance(scope)
    subject = "ข่าวการเงิน" if finance else "ข่าว"
    suffix = "ด้านการเงิน" if finance else ""
    views_note = f"มัธยฐาน {t.fmt_int(kpi['views_median'])} ครั้ง จาก {kpi['views_n']:,} รายการ" if kpi["views_n"] else "ไม่มียอดเข้าชม"
    return [
        c.kpi(f"{subject}ที่ตรวจสอบ", t.fmt_int(kpi["posts"]), f"post_id ไม่ซ้ำ · ขอบเขต {news_scope_name(scope)}", hero=True, span=4),
        c.kpi(f"ข่าวปลอม{suffix}", t.fmt_int(kpi["fake"]), "ผลตรวจสอบ = ข่าวปลอม", span=2),
        c.kpi(f"ข่าวบิดเบือน{suffix}", t.fmt_int(kpi["distorted"]), "ผลตรวจสอบ = ข่าวบิดเบือน", span=2),
        c.kpi("สัดส่วนข่าวปลอม", t.fmt_pct(kpi["fake_pct"]), f"จาก {kpi['with_verdict']:,} รายการที่มีผลตรวจสอบ", span=2),
        c.kpi("ยอดเข้าชมเฉลี่ย", t.fmt_int(kpi["views_mean"]), views_note, span=2),
    ]


def correlation_line(result: rel.Correlation) -> str:
    if result.r is None:
        return f"Pearson r = N/A · n = {result.n} · {result.reason}"
    interval = f" · ช่วง 95%: {t.fmt_r(result.ci_low)} ถึง {t.fmt_r(result.ci_high)}" if result.ci_low is not None else ""
    warning = " · ตัวอย่างน้อย อ่านผลด้วยความระวัง" if result.n < rel.LOW_SAMPLE else ""
    return f"Pearson r = {t.fmt_r(result.r)} · n = {result.n} · {result.direction} ระดับ{result.strength}{interval}{warning}"


def rel_insight(with_cases: rel.Correlation, with_loss: rel.Correlation, changes: rel.Correlation) -> list:
    if with_cases.r is None and with_loss.r is None:
        return ["ยังคำนวณความสัมพันธ์ไม่ได้ในช่วงนี้ เพราะมีสัปดาห์ที่มีข้อมูลครบไม่พอ"]
    parts: list = [
        "ระดับข่าวเท็จกับคดี ", mark(f"r = {t.fmt_r(with_cases.r)}"), f" (n = {with_cases.n}) และกับความเสียหาย ",
        mark(f"r = {t.fmt_r(with_loss.r)}"), f" (n = {with_loss.n})",
    ]
    if changes.r is not None:
        parts.append(
            f" แต่เมื่อดูการเปลี่ยนแปลงรายสัปดาห์ r = {t.fmt_r(changes.r)} (n = {changes.n}) "
            "จึงยังไม่พบหลักฐานว่าสองชุดนี้ขยับตามกันในระยะสั้น และสรุปเป็นเหตุและผลไม่ได้"
        )
    return parts


def rel_kpis(kpi: dict, week_row: pd.Series | None) -> list:
    if week_row is not None:
        cases, loss = week_row["cases_used"], week_row["loss_used"]
        per_case = loss / cases if pd.notna(cases) and pd.notna(loss) and cases > 0 else None
        label = t.th_week(week_row["week_start"])
        return [
            c.kpi("ข่าวเท็จด้านการเงิน", t.fmt_int(week_row["false_count"]), label, span=3),
            c.kpi("จำนวนคดีหลอกลวง", t.fmt_int(cases), label, span=3),
            c.kpi("มูลค่าความเสียหาย", f"{t.fmt_million(loss)}", f"ล้านบาท · {label}", span=3),
            c.kpi("ความเสียหายเฉลี่ยต่อคดี", t.fmt_int(per_case), f"บาทต่อคดี · {label}", span=3),
        ]
    used = f"เฉลี่ยจาก {kpi['weeks_used']} สัปดาห์ที่ใช้ได้"
    return [
        c.kpi("ข่าวเท็จด้านการเงินต่อสัปดาห์", t.fmt_one(kpi["false_per_week"]), f"{used} · รวม {kpi['false_total']:,} รายการในช่วงที่เลือก", span=3),
        c.kpi("คดีหลอกลวงต่อสัปดาห์", t.fmt_int(kpi["cases_per_week"]), used, span=3),
        c.kpi("ความเสียหายต่อสัปดาห์", t.fmt_million(kpi["loss_per_week"]), f"ล้านบาท · {used}", span=3),
        c.kpi("ความเสียหายเฉลี่ยต่อคดี", t.fmt_int(kpi["loss_per_case"]), "บาทต่อคดี · ความเสียหายรวม ÷ คดีรวม", span=3),
    ]


def sensitivity_rows(table: pd.DataFrame) -> html.Table:
    head = html.Thead(html.Tr([html.Th("นิยามที่ใช้"), html.Th("r กับคดี"), html.Th("n"), html.Th("r กับความเสียหาย"), html.Th("n")]))
    rows = []
    for row in table.itertuples():
        rows.append(html.Tr(className="is-primary" if row.key == "brd" else "", children=[
            html.Td(row.label), html.Td(t.fmt_r(row.r_cases), className="num"), html.Td(row.n_cases, className="num"),
            html.Td(t.fmt_r(row.r_loss), className="num"), html.Td(row.n_loss, className="num"),
        ]))
    return html.Table(className="sensitivity", children=[head, html.Tbody(rows)])
