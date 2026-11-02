"""Static page structure: sidebar, masthead and the three tabs."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from dash import dcc, html

from src.analytics import ai_risk_analysis as ai
from src.analytics.ai_risk_analysis import MISSING
from src.analytics.financial_news_analysis import SCOPE_ALL, SCOPE_CORE, SCOPE_EXTENDED
from src.analytics.scam_correlation_analysis import RELABEL_MONTH
from src.config import EXTENDED_SCOPE_REVIEW, FINANCE_CORE_CATEGORY, SUSPECT_WEEK
from src.dashboard import components as c
from src.dashboard import state as s
from src.dashboard import theme as t
from src.dashboard.data_store import DataStore
from src.data_cleaning.clean_ai_incidents import HARM_TH, REGION_TH, RISK_DOMAIN_TH
from src.data_cleaning.clean_fake_news import OTHER_TOPIC, TOPIC_RULES
from src.data_cleaning.common import snapshot_date

TABS = {
    "ai": {
        "kicker": "01 · AI Risk Analysis",
        "question": "AI ก่อให้เกิดความเสี่ยงแบบใดมากที่สุด และแนวโน้มเปลี่ยนไปอย่างไร",
    },
    "news": {
        "kicker": "02 · Financial Fake News Analysis",
        "question": "ข่าวปลอมและข่าวบิดเบือนในไทยพบมากในประเด็นใด โดยเฉพาะการเงินและการลงทุน",
    },
    "rel": {
        "kicker": "03 · Fake News & Online Scam Relationship",
        "question": "เมื่อข่าวเท็จด้านการเงินถูกตรวจสอบมากขึ้น คดีและความเสียหายเปลี่ยนไปทิศทางเดียวกันหรือไม่",
    },
}

AI_TABLE_COLUMNS = [
    {"name": "ID", "id": "incident_id"}, {"name": "วันที่เกิดเหตุ", "id": "date"}, {"name": "เหตุการณ์", "id": "title"},
    {"name": "ประเภทความเสี่ยง", "id": "risk_domain_th"}, {"name": "ภูมิภาค", "id": "region_th"},
    {"name": "บาดเจ็บ", "id": "injuries"}, {"name": "เสียชีวิต", "id": "lives_lost"},
]
NEWS_TABLE_COLUMNS = [
    {"name": "วันที่เผยแพร่", "id": "date"}, {"name": "หัวข้อข่าว", "id": "title_link", "presentation": "markdown"},
    {"name": "หมวดหมู่", "id": "category_th"}, {"name": "ผลการตรวจสอบ", "id": "verdict_th_display"},
    {"name": "ยอดเข้าชม", "id": "view_count"},
]
REL_TABLE_COLUMNS = [
    {"name": "สัปดาห์", "id": "week_label"}, {"name": "ข่าวเท็จการเงิน", "id": "false_count"}, {"name": "คดี", "id": "cases_display"},
    {"name": "ความเสียหาย (ล้านบาท)", "id": "loss_display"}, {"name": "เฉลี่ยต่อคดี (บาท)", "id": "per_case_display"},
    {"name": "ความแม่นยำ", "id": "precision_display"}, {"name": "สถานะ", "id": "status_display"},
]


def year_marks() -> dict:
    marks = {year: {"label": str(year)} for year in range(s.YEAR_SLIDER_MIN + 2, s.YEAR_SLIDER_MAX + 1, 4)}
    marks[s.YEAR_SLIDER_MIN] = {"label": f"≤{s.YEAR_SLIDER_MIN}"}
    marks[s.YEAR_SLIDER_MAX] = {"label": str(s.YEAR_SLIDER_MAX)}
    return marks


def count_options(series, labels: dict | None = None) -> list[dict]:
    counts = series.value_counts()
    labels = labels or {}
    options = [{"label": f"{labels.get(value, value)} ({count:,})", "value": value} for value, count in counts.items()]
    missing = int(series.isna().sum())
    if missing:
        options.append({"label": f"ไม่มีข้อมูลในแหล่ง ({missing:,})", "value": MISSING})
    return options


def news_scope_options(store: DataStore) -> list[dict]:
    news = store.news
    options = [
        {"label": f"การเงิน: หมวดหลัก ({int(news['is_finance_core'].sum()):,})", "value": SCOPE_CORE},
        {"label": f"การเงิน: ขอบเขตขยาย ({int(news['is_finance_extended'].sum()):,})", "value": SCOPE_EXTENDED},
        {"label": f"ทุกหมวด ({len(news):,})", "value": SCOPE_ALL},
    ]
    counts = news["category_th"].value_counts()
    options += [{"label": f"{name} ({count:,})", "value": name} for name, count in counts.items() if name != FINANCE_CORE_CATEGORY]
    return options


def topic_options() -> list[dict]:
    rules = [{"label": r["topic_th"], "value": r["topic_id"]} for r in TOPIC_RULES]
    return rules + [{"label": OTHER_TOPIC["topic_th"], "value": OTHER_TOPIC["topic_id"]}]


def date_range(component_id: str, start: str, end: str) -> dcc.DatePickerRange:
    return dcc.DatePickerRange(
        id=component_id, start_date=start, end_date=end, min_date_allowed=start, max_date_allowed=end,
        display_format="D MMM YYYY", first_day_of_week=0, className="date-range",
    )


def cset_coverage(incidents: pd.DataFrame) -> dict:
    """How much of the database carries region and harm codes."""
    coded = incidents[incidents["location_region"].notna()]
    return {
        "count": len(coded),
        "pct": len(coded) / len(incidents) * 100,
        "next_year": int(coded["year"].max()) + 1,
    }


def source_ai(store: DataStore) -> str:
    stamp = snapshot_date(Path(store.quality["facts"]["ai"]["source_file"]))
    return f"AI Incident Database (snapshot {t.th_date(stamp)})"


def extended_review() -> str:
    """The hand-read sample that measures how precise the extended scope is."""
    if not EXTENDED_SCOPE_REVIEW.exists():
        return "ขอบเขตขยายยังไม่มีผลการสุ่มตรวจ"
    review = pd.read_csv(EXTENDED_SCOPE_REVIEW, encoding="utf-8-sig")
    hits = int(review["relevant_to_finance"].sum())
    return f"สุ่มตรวจ {len(review)} รายการ ตรงประเด็น {hits} รายการ ({hits / len(review) * 100:.1f}%)"


def sidebar(store: DataStore, defaults: dict) -> html.Aside:
    incidents = store.incidents
    coverage = cset_coverage(incidents)
    domain_counts = incidents["risk_domain"].value_counts()
    domain_options = [
        {"label": f"{RISK_DOMAIN_TH[d]} ({n:,})", "value": d} for d, n in domain_counts.items()
    ] + [{"label": f"ยังไม่จำแนก ({int(incidents['risk_domain'].isna().sum()):,})", "value": MISSING}]

    ai_panel = html.Div(id="filters-ai", className="filters", children=[
        html.Div("ตัวกรอง AI Risk", className="filters__title"),
        c.field("ภูมิภาค", dcc.Dropdown(id="ai-regions", options=count_options(incidents["location_region"], REGION_TH), value=[], multi=True, placeholder="ทุกภูมิภาค"),
                f"มีข้อมูลเฉพาะ {coverage['count']:,} เหตุการณ์ และไม่มีตั้งแต่ปี {coverage['next_year']}"),
        c.field("ประเภทความเสี่ยง", dcc.Dropdown(id="ai-domains", options=domain_options, value=[], multi=True, placeholder="ทุกประเภท")),
        c.field("Harm Domain", dcc.Dropdown(id="ai-harm", options=count_options(incidents["harm_domain"], HARM_TH), value=[], multi=True, placeholder="ทุกค่า")),
    ])
    news_panel = html.Div(id="filters-news", className="filters", children=[
        html.Div("ตัวกรองข่าว", className="filters__title"),
        c.field("หมวดข่าว", dcc.Dropdown(id="news-scope", options=news_scope_options(store), value=SCOPE_CORE, clearable=False)),
        c.field("ผลการตรวจสอบ", dcc.Dropdown(
            id="news-verdicts", multi=True, value=[], placeholder="ทุกผลตรวจสอบ",
            options=[{"label": label, "value": key} for key, label in t.VERDICT_TH.items()],
        )),
        c.field("ช่วงวันที่เผยแพร่", date_range("news-dates", defaults["news_start"], defaults["news_end"])),
        c.field("ค้นหาคำสำคัญ", dcc.Input(id="news-keyword", type="search", debounce=0.5, value="", placeholder="หัวข้อหรือแท็ก เช่น ก.ล.ต.", className="text-input")),
    ])
    rel_panel = html.Div(id="filters-rel", className="filters", children=[
        html.Div("ตัวกรองความสัมพันธ์", className="filters__title"),
        c.field("ช่วงสัปดาห์", date_range("rel-dates", defaults["rel_start"], defaults["rel_end"])),
        c.field("ขอบเขตข่าวการเงิน", dcc.RadioItems(
            id="rel-scope", value="core", className="radio",
            options=[{"label": "หมวดหลัก", "value": "core"}, {"label": "ขอบเขตขยาย", "value": "extended"}],
        )),
        c.field("ประเด็นข่าวการเงิน", dcc.Dropdown(id="rel-topic", options=topic_options(), value=None, placeholder="ทุกประเด็น")),
        c.field("จำนวนคดีต่อสัปดาห์", dcc.RangeSlider(
            id="rel-cases", min=s.CASES_SLIDER[0], max=s.CASES_SLIDER[1], step=100, value=list(s.CASES_SLIDER), updatemode="mouseup", allow_direct_input=False,
            marks={5000: "5,000", 6000: "6,000", 7000: "7,000", 8000: "≥8,000"},
        )),
        c.field("ความเสียหาย (ล้านบาท)", dcc.RangeSlider(
            id="rel-loss", min=s.LOSS_SLIDER[0], max=s.LOSS_SLIDER[1], step=10, value=list(s.LOSS_SLIDER), updatemode="mouseup", allow_direct_input=False,
            marks={100: "100", 300: "300", 500: "500", 700: "≥700"},
        )),
        c.field("การจัดการข้อมูล", dcc.Checklist(
            id="rel-options", value=[], className="check",
            options=[
                {"label": f"รวมสัปดาห์น่าสงสัย {t.th_week(SUSPECT_WEEK)}", "value": s.OPT_SUSPECT},
                {"label": "ใช้เฉพาะความเสียหายที่แม่นยำถึงบาท", "value": s.OPT_EXACT},
            ],
        )),
    ])

    def nav_button(key: str, number: str, label: str) -> html.Button:
        return html.Button(id=f"nav-{key}", className="nav__item", n_clicks=0, children=[html.Span(number, className="nav__number"), html.Span(label)])

    return html.Aside(id="sidebar", className="sidebar", children=[
        html.Div(className="brand", children=[
            html.Div("Digital Threat Intelligence", className="brand__kicker"),
            html.Div("ภัยดิจิทัลยุค AI", className="brand__name"),
            html.Button("ปิด", id="menu-close", className="menu-close", n_clicks=0),
        ]),
        html.Nav(className="nav", children=[
            nav_button("ai", "01", "ความเสี่ยงจาก AI"),
            nav_button("news", "02", "ข่าวปลอมด้านการเงิน"),
            nav_button("rel", "03", "ข่าวเท็จกับคดีหลอกลวง"),
        ]),
        html.Div(className="filters filters--global", children=[
            html.Div("ช่วงเวลาร่วมทุกแท็บ", className="filters__title"),
            c.field("ปี (ค.ศ.)", dcc.RangeSlider(
                id="global-years", min=s.YEAR_SLIDER_MIN, max=s.YEAR_SLIDER_MAX, step=1, value=defaults["years"],
                marks=year_marks(), updatemode="mouseup", allow_direct_input=False,
            )),
        ]),
        ai_panel, news_panel, rel_panel,
        html.Button("ล้างตัวกรองทั้งหมด", id="reset-all", className="reset", n_clicks=0),
    ])


def masthead(store: DataStore) -> html.Header:
    return html.Header(className="masthead", children=[
        html.Div(className="masthead__top", children=[
            html.Button("เมนูและตัวกรอง", id="menu-open", className="menu-open", n_clicks=0),
            html.Div("ภัยดิจิทัลยุค AI: วิเคราะห์ความเสี่ยงจากปัญญาประดิษฐ์ ข่าวปลอม และการหลอกลวงออนไลน์", className="masthead__title"),
        ]),
        html.Div(id="tab-kicker", className="masthead__kicker"),
        html.H1(id="tab-question", className="masthead__question"),
        html.Div(id="data-period", className="masthead__period"),
    ])


def tab_ai(store: DataStore) -> html.Div:
    source = source_ai(store)
    incidents = store.incidents
    coverage = cset_coverage(incidents)
    before = ai.incidents_before_trend(incidents)
    return html.Div(id="page-ai", className="page", children=[
        html.Div(id="ai-insight", className="insight"),
        html.Div(id="ai-active", className="chips"),
        html.Div(id="ai-coverage"),
        html.Div(id="ai-kpis", className="bento"),
        html.Div(className="bento", children=[
            c.chart_card(
                "แนวโน้มเหตุการณ์ AI ตามเวลา",
                f"นับ Incident ID ไม่ซ้ำตามวันที่เกิดเหตุ กราฟเริ่มปี {ai.FIRST_TREND_YEAR} ส่วน {before} เหตุการณ์ก่อนหน้ายังนับใน KPI",
                "ai-trend", source, 7, 340,
                hint="คลิกจุดเพื่อกรองตามช่วงเวลา",
                extra=dcc.RadioItems(id="ai-granularity", value="year", className="segment", options=[{"label": "รายปี", "value": "year"}, {"label": "รายเดือน", "value": "month"}]),
            ),
            c.chart_card("5 อันดับประเภทความเสี่ยง", "เฉพาะเหตุการณ์ที่จำแนกแล้ว", "ai-top-domains", source, 5, 340, hint="คลิกแท่งเพื่อกรอง"),
            c.chart_card("การกระจายความเสี่ยง", "พื้นที่ของกล่องแทนจำนวนเหตุการณ์ แยกประเภทหลักและกลุ่มย่อย", "ai-treemap", source, 8, 440, hint="คลิกกล่องเพื่อกรอง", fill=True),
            html.Div(className="stack span-4", children=[
                c.chart_card("ภูมิภาคที่เกิดเหตุ", "เฉพาะเหตุการณ์ที่ CSET ลงรหัสภูมิภาค", "ai-region-chart", source, 12, 350, hint="คลิกแท่งเพื่อกรอง"),
                c.chart_card("Harm Domain", "เฉพาะเหตุการณ์ที่ CSET ลงรหัส", "ai-harm-chart", source, 12, 190, hint="คลิกแท่งเพื่อกรอง"),
            ]),
            c.table_card("รายการเหตุการณ์", "ตรงกับตัวกรองทั้งหมด เรียงได้โดยคลิกหัวตาราง", c.data_table("ai-table", AI_TABLE_COLUMNS, 8), source),
            c.note_card("ขอบเขตและข้อจำกัดของข้อมูล", [
                "เป็นเหตุการณ์ระดับโลกที่ถูกรายงานและบันทึกในฐานข้อมูล ไม่ใช่จำนวนเหตุการณ์ทั้งหมดที่เกิดขึ้น และไม่มีแถวใดที่ระบุ Country Code เป็นไทย",
                "ใช้ snapshot ล่าสุดเพียงไฟล์เดียว แต่ละไฟล์คือฐานข้อมูลทั้งชุด ณ วันดาวน์โหลด จึงไม่นำมาบวกกัน",
                f"ภูมิภาค Harm Domain ผู้บาดเจ็บ และผู้เสียชีวิต มาจาก CSET ซึ่งลงรหัสไว้ {coverage['pct']:.1f}% ของเหตุการณ์ ค่าว่างไม่ได้แปลว่าไม่มีผลกระทบ",
                f"ปี {store.ai_end.year} มีข้อมูลถึง {t.th_date(store.ai_end)} และยังจำแนกความเสี่ยงไม่ครบ จึงยังเทียบกับปีเต็มไม่ได้",
            ]),
        ]),
    ])


def tab_news() -> html.Div:
    return html.Div(id="page-news", className="page", children=[
        html.Div(id="news-insight", className="insight"),
        html.Div(id="news-active", className="chips"),
        html.Div(id="news-kpis", className="bento"),
        html.Div(className="bento", children=[
            c.chart_card("ข่าวเท็จแยกตามหมวด AFNC", "จำนวนข่าวปลอมและข่าวบิดเบือนของทุกหมวด เพื่อเทียบหมวดการเงินกับหมวดอื่น", "news-category-chart", c.SOURCE_AFNC, 7, 500, hint="คลิกแท่งเพื่อดูหมวดนั้น"),
            c.chart_card("สัดส่วนผลการตรวจสอบ", "ในขอบเขตข่าวที่เลือก", "news-verdict-chart", c.SOURCE_AFNC, 5, 500, hint="คลิกส่วนของวงเพื่อกรอง"),
            c.chart_card("แนวโน้มข่าวรายเดือน", "จำนวนโพสต์ต่อเดือน แยกตามผลการตรวจสอบ", "news-trend", c.SOURCE_AFNC, 7, 340, hint="คลิกเดือนเพื่อกรอง"),
            c.chart_card("ประเด็นข่าวเท็จด้านการเงิน", "จัดกลุ่มจากหัวข้อและแท็กด้วยกฎคำสำคัญ", "news-topic-chart", c.SOURCE_AFNC, 5, 340, hint="คลิกแท่งเพื่อกรอง"),
            c.chart_card("ข่าวที่มียอดเข้าชมสูงสุด", "ยอดเข้าชมสะสม ไม่ได้บ่งบอกว่าผู้อ่านเชื่อข่าวนั้น", "news-top-chart", c.SOURCE_AFNC, 12, 470, hint="คลิกแท่งเพื่อดูข่าวนั้น"),
            c.table_card("รายการข่าว", "ค้นหาได้จากช่องคำสำคัญ เรียงได้โดยคลิกหัวตาราง คลิกหัวข้อเพื่อเปิดโพสต์ต้นฉบับ", c.data_table("news-table", NEWS_TABLE_COLUMNS, 10), c.SOURCE_AFNC),
            c.note_card("ขอบเขตและข้อจำกัดของข้อมูล", [
                "ตัวเลขคือคำตัดสินที่ AFNC เลือกเผยแพร่ ไม่ใช่ปริมาณข่าวปลอมทั้งหมดในสังคม",
                f"ขอบเขตหลักใช้หมวด การเงิน-หุ้น ส่วนขอบเขตขยายเพิ่มข่าวหมวดอื่นที่มีคำสำคัญการเงินในหัวข้อหรือแท็ก {extended_review()}",
                f"ตั้งแต่ {t.th_month(RELABEL_MONTH)} AFNC ลงคำตัดสินในหมวดอาชญากรรมออนไลน์ ซึ่งมีข่าวลงทุนและสินเชื่อปนอยู่ หมวดการเงิน-หุ้นจึงอาจลดลงเกินจริงในช่วงท้าย",
                "ยอดเข้าชมเป็นค่าสะสม ณ 1 พ.ย. 2026 โพสต์เก่าจึงมีเวลาสะสมนานกว่า และปี 2019 มีข้อมูลน้อยเพราะศูนย์เปิดเมื่อ 1 พ.ย. 2019",
            ]),
        ]),
    ])


def tab_rel() -> html.Div:
    return html.Div(id="page-rel", className="page", children=[
        html.Div(id="rel-insight", className="insight"),
        html.Div(id="rel-active", className="chips"),
        html.Div(id="rel-kpis", className="bento"),
        html.Div(className="bento", children=[
            c.chart_card(
                "เปรียบเทียบรายสัปดาห์", "แยกสามแผงบนแกนเวลาเดียวกัน แถบเทาคือสัปดาห์ที่ไม่มีตัวเลขหรือถูกตัดออก ไม่ใช่ศูนย์ และแกนจำนวนคดีไม่ได้เริ่มที่ศูนย์",
                "rel-trend", c.SOURCE_REL, 12, 520, hint="คลิกสัปดาห์เพื่อดูรายละเอียด",
            ),
            c.chart_card("ข่าวเท็จด้านการเงิน กับ จำนวนคดี", "", "rel-scatter-cases", c.SOURCE_REL, 6, 340, hint="แต่ละจุดคือหนึ่งสัปดาห์", subtitle_id="rel-r-cases"),
            c.chart_card("ข่าวเท็จด้านการเงิน กับ มูลค่าความเสียหาย", "", "rel-scatter-loss", c.SOURCE_REL, 6, 340, hint="จุดกลวงคือความเสียหายแบบปัดเศษ", subtitle_id="rel-r-loss"),
            html.Section(className="card span-7", children=[
                html.Header(className="card__head", children=[
                    html.H3("ผลลัพธ์เปลี่ยนไปอย่างไรเมื่อเปลี่ยนนิยาม", className="card__title"),
                    html.P("Pearson r ของช่วง ACSC ทั้งหมด ค่านี้ไม่เปลี่ยนตามตัวกรอง", className="card__subtitle"),
                ]),
                html.Div(id="rel-sensitivity"),
                html.Footer(className="card__foot", children=[html.Span(f"แหล่งข้อมูล: {c.SOURCE_REL}")]),
            ]),
            c.note_card("อ่านผลอย่างไรให้ถูกต้อง", [
                "ค่า r บอกว่าตัวเลขสองชุดขึ้นลงพร้อมกันแค่ไหน ไม่ได้บอกว่าข่าวเท็จทำให้เกิดคดี หรือคดีทำให้เกิดข่าวเท็จ",
                "ทั้งสองชุดลดลงในช่วงเดียวกัน จึงให้ r เป็นบวกได้แม้จะไม่ขยับตามกันรายสัปดาห์",
                "ข่าวเท็จคือจำนวนที่ AFNC เลือกตรวจ และคดีคือจำนวนที่มีผู้แจ้ง ไม่ใช่ปริมาณจริงทั้งหมด",
                "ช่วงความเชื่อมั่นสมมติว่าแต่ละสัปดาห์เป็นอิสระต่อกัน ข้อมูลรายสัปดาห์ไม่เป็นเช่นนั้น ความไม่แน่นอนจริงจึงกว้างกว่าที่แสดง",
            ], span=5, tone="card--ink"),
            c.table_card("ข้อมูลรายสัปดาห์", "สัปดาห์ที่ไม่มีรายงานแสดงเป็นขีด ไม่ใช่ศูนย์", c.data_table("rel-table", REL_TABLE_COLUMNS, 10), c.SOURCE_REL),
        ]),
    ])


def build_layout(store: DataStore, defaults: dict) -> html.Div:
    stores = [
        dcc.Store(id="active-tab", data="ai"),
        dcc.Store(id="ai-subdomain", data=None), dcc.Store(id="ai-month", data=None),
        dcc.Store(id="news-month", data=None), dcc.Store(id="news-topic", data=None), dcc.Store(id="news-post", data=None),
        dcc.Store(id="rel-week", data=None),
    ]
    return html.Div(className="shell", children=[
        *stores,
        html.Div(id="scrim", className="scrim", n_clicks=0),
        sidebar(store, defaults),
        html.Main(className="main", children=[
            masthead(store), tab_ai(store), tab_news(), tab_rel(),
            html.Footer(className="colophon", children=[
                html.Span("Python Data Visualization 2026 · Group 4"),
                html.Span("วันที่ทั้งหมดเป็น ค.ศ. ตัวเลขทุกค่าคำนวณจาก Dataset ในโฟลเดอร์ datasets/"),
            ]),
        ]),
    ])


def error_layout(message: str) -> html.Div:
    return html.Div(className="error-page", children=[
        html.H1("ยังเปิด Dashboard ไม่ได้"), html.P(message),
    ])
