"""Export the default view as a static page, for hosts that cannot run Python.

Run with: python -m src.dashboard.export_static
Tabs and tooltips work in the browser. Click-to-filter needs the Python server.
"""
from __future__ import annotations

import html as markup
import json
import shutil
from pathlib import Path

import pandas as pd
import plotly
from dash import dash_table, dcc
from dash.development.base_component import Component

from src.analytics import ai_risk_analysis as ai
from src.analytics import financial_news_analysis as news
from src.analytics import scam_correlation_analysis as rel
from src.config import ROOT
from src.dashboard import figures as fig
from src.dashboard import narrative as n
from src.dashboard import state as s
from src.dashboard import theme as t
from src.dashboard.app import ASSETS, TITLE, defaults_for
from src.dashboard.callbacks import dash_if_blank, week_status
from src.dashboard.data_store import load_store
from src.dashboard.layout import TABS, tab_ai, tab_news, tab_rel
from src.data_cleaning.clean_ai_incidents import HARM_TH, REGION_TH

OUT = ROOT / "public"
SKIPPED = (dcc.RadioItems, dcc.Store)
ROWS = 10


def render(node, slots: dict, tables: dict) -> str:
    """Turn a Dash layout tree into HTML, filling callback outputs from `slots`."""
    if node is None:
        return ""
    if isinstance(node, (list, tuple)):
        return "".join(render(child, slots, tables) for child in node)
    if not isinstance(node, Component):
        return markup.escape(str(node))
    if isinstance(node, SKIPPED):
        return ""
    node_id = getattr(node, "id", None)
    if isinstance(node, dcc.Graph):
        return f'<div class="card__chart plot" id="{node_id}" style="height:{node.style["height"]}"></div>'
    if isinstance(node, dash_table.DataTable):
        return tables[node_id]
    if isinstance(node_id, str) and node_id.endswith("-empty"):
        return ""
    tag = type(node).__name__.lower()
    children = slots.get(node_id, getattr(node, "children", None))
    attributes = f' id="{node_id}"' if node_id else ""
    if getattr(node, "className", None):
        attributes += f' class="{node.className}"'
    return f"<{tag}{attributes}>{render(children, slots, tables)}</{tag}>"


def static_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{markup.escape(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f'<div class="static-wrap"><table class="sensitivity"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def clean(value) -> str:
    return markup.escape(str(value))


def ai_view(store, defaults) -> tuple[dict, dict, dict]:
    incidents, end = store.incidents, store.ai_end
    f = s.ai_filters(defaults["years"], [], [], [], None, None)
    growth = ai.annual_growth(incidents, f, end)
    slots = {"ai-kpis": n.ai_kpis(incidents, growth), "ai-insight": n.ai_insight(incidents, incidents, [], growth)}
    figures = {
        "ai-trend": fig.ai_yearly(ai.yearly_counts(incidents), (None, None), end),
        "ai-top-domains": fig.top_domains(ai.top_risk_domains(incidents, 5), []),
        "ai-treemap": fig.risk_treemap(ai.risk_tree(incidents), [], None),
        "ai-region-chart": fig.region_bars(ai.region_counts(incidents), [], REGION_TH),
        "ai-harm-chart": fig.harm_bars(ai.harm_counts(incidents), [], HARM_TH),
    }
    latest = incidents.sort_values("date", ascending=False).head(ROWS)
    rows = [
        [clean(r.incident_id), t.th_date(r.date), clean(r.title), clean(r.risk_domain_th if pd.notna(r.risk_domain_th) else "ยังไม่จำแนก"),
         clean(REGION_TH.get(r.location_region, "—")), dash_if_blank(r.injuries, t.fmt_int), dash_if_blank(r.lives_lost, t.fmt_int)]
        for r in latest.itertuples()
    ]
    tables = {"ai-table": static_table(["ID", "วันที่เกิดเหตุ", "เหตุการณ์", "ประเภทความเสี่ยง", "ภูมิภาค", "บาดเจ็บ", "เสียชีวิต"], rows)}
    return slots, figures, tables


def news_view(store, defaults) -> tuple[dict, dict, dict]:
    items = store.news
    f = s.news_filters(defaults["years"], news.SCOPE_CORE, [], defaults["news_start"], defaults["news_end"], "", None, None, None)
    filtered = news.filter_news(items, f)
    kpi = news.news_kpis(filtered)
    categories = news.false_by_category(news.filter_news(items, f, frozenset({"scope", "topic", "post"})))
    slots = {"news-kpis": n.news_kpis(kpi, news.SCOPE_CORE), "news-insight": n.news_insight(categories, filtered, news.SCOPE_CORE)}
    figures = {
        "news-category-chart": fig.category_bars(categories, news.FINANCE_CORE_CATEGORY),
        "news-verdict-chart": fig.verdict_donut(news.verdict_distribution(filtered), [], t.fmt_pct(kpi["fake_pct"]), "ข่าวปลอม"),
        "news-trend": fig.news_trend(news.monthly_trend(filtered), None, True),
        "news-topic-chart": fig.topic_bars(news.false_by_topic(filtered), None),
        "news-top-chart": fig.top_viewed_bars(news.top_viewed(filtered), None),
    }
    latest = filtered.sort_values("date", ascending=False).head(ROWS)
    rows = [
        [t.th_date(r.date), f'<a href="{clean(r.url)}" target="_blank" rel="noopener">{clean(r.title_clean)}</a>', clean(r.category_th), t.VERDICT_TH[r.verdict_group], t.fmt_int(r.view_count)]
        for r in latest.itertuples()
    ]
    return slots, figures, {"news-table": static_table(["วันที่เผยแพร่", "หัวข้อข่าว", "หมวดหมู่", "ผลการตรวจสอบ", "ยอดเข้าชม"], rows)}


def rel_view(store, defaults) -> tuple[dict, dict, dict]:
    f = s.rel_filters(defaults["years"], defaults["rel_start"], defaults["rel_end"], "core", None, s.CASES_SLIDER, s.LOSS_SLIDER, [])
    frame = rel.apply_filters(rel.weekly_frame(store.panel, store.news), f)
    with_cases, with_loss = rel.pearson(frame["false_count"], frame["cases_used"]), rel.pearson(frame["false_count"], frame["loss_used"])
    changes = rel.consecutive_changes(frame)
    slots = {
        "rel-kpis": n.rel_kpis(rel.relationship_kpis(frame), None),
        "rel-insight": n.rel_insight(with_cases, with_loss, rel.pearson(changes["false_count"], changes["cases_used"])),
        "rel-r-cases": n.correlation_line(with_cases), "rel-r-loss": n.correlation_line(with_loss),
        "rel-sensitivity": n.sensitivity_rows(rel.sensitivity_table(store.panel, store.news)),
    }
    figures = {
        "rel-trend": fig.weekly_comparison(frame, None, False),
        "rel-scatter-cases": fig.scatter(frame, "cases_used", 1, "คดีหลอกลวงออนไลน์ (คดีต่อสัปดาห์)", "คดี %{y:,.0f} คดี", rel.trend_line(frame["false_count"], frame["cases_used"]), None),
        "rel-scatter-loss": fig.scatter(frame, "loss_used", 1e6, "มูลค่าความเสียหาย (ล้านบาทต่อสัปดาห์)", "ความเสียหาย %{y:,.1f} ล้านบาท", rel.trend_line(frame["false_count"], frame["loss_used"]), None),
    }
    weeks = frame.sort_values("week_start", ascending=False)
    rows = [
        [t.th_week(r.week_start), clean(r.false_count), dash_if_blank(r.cases, t.fmt_int), dash_if_blank(r.loss_baht, t.fmt_million), dash_if_blank(r.loss_per_case_baht, t.fmt_int),
         {"exact": "ถึงบาท", "rounded": "ปัดเศษ"}.get(r.loss_precision, "—"), week_status(r)]
        for r in weeks.itertuples()
    ]
    return slots, figures, {"rel-table": static_table(["สัปดาห์", "ข่าวเท็จการเงิน", "คดี", "ความเสียหาย (ล้านบาท)", "เฉลี่ยต่อคดี (บาท)", "ความแม่นยำ", "สถานะ"], rows)}


PAGE = """<!doctype html>
<html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title><link rel="stylesheet" href="__FONT__"><link rel="stylesheet" href="style.css">
<style>
.static-note{background:#fff7dd;border:1px solid var(--orange);border-radius:12px;padding:10px 14px;font-size:14px;margin-bottom:14px}
.card__hint,.chips{display:none}.static-wrap{overflow-x:auto}.static-wrap td a{color:var(--blue-ink);text-decoration:none}
.sidebar{justify-content:flex-start}.sidebar__note{font-size:13px;color:#b6c0ce;border-top:1px solid rgba(255,255,255,.12);padding-top:14px}
</style></head><body><div class="shell"><div id="scrim" class="scrim"></div>
<aside id="sidebar" class="sidebar"><div class="brand"><div class="brand__kicker">Digital Threat Intelligence</div>
<div class="brand__name">ภัยดิจิทัลยุค AI</div><button id="menu-close" class="menu-close">ปิด</button></div>
<nav class="nav">__NAV__</nav><div class="sidebar__note">ข้อมูลทุกค่าคำนวณจาก Dataset ของโครงการ วันที่ทั้งหมดเป็น ค.ศ.</div></aside>
<main class="main"><header class="masthead"><div class="masthead__top"><button id="menu-open" class="menu-open">เมนู</button>
<div class="masthead__title">ภัยดิจิทัลยุค AI: วิเคราะห์ความเสี่ยงจากปัญญาประดิษฐ์ ข่าวปลอม และการหลอกลวงออนไลน์</div></div>
<div id="tab-kicker" class="masthead__kicker"></div><h1 id="tab-question" class="masthead__question"></h1><div id="data-period" class="masthead__period"></div></header>
<div class="static-note">หน้านี้เป็นเวอร์ชันเผยแพร่แบบคงที่ เปลี่ยนแท็บและชี้กราฟเพื่อดูค่าได้ ส่วนการคลิกกราฟเพื่อกรองข้อมูลใช้ได้เมื่อรัน python app.py</div>
__PAGES__<footer class="colophon"><span>Python Data Visualization 2026 · Group 4</span><span>ตารางแสดงรายการล่าสุดบางส่วน</span></footer></main></div>
<script src="plotly.min.js"></script><script>
const FIGURES=__FIGURES__,TABS=__TABS__,PLOTS=__PLOTS__,config={displayModeBar:false,scrollZoom:false,doubleClick:false,responsive:true},drawn=new Set();
const sidebar=document.getElementById("sidebar"),scrim=document.getElementById("scrim");
function closeMenu(){sidebar.classList.remove("sidebar--open")}
function show(key){for(const k of Object.keys(TABS)){document.getElementById("page-"+k).classList.toggle("page--hidden",k!==key);document.getElementById("nav-"+k).classList.toggle("nav__item--active",k===key)}
document.getElementById("tab-kicker").textContent=TABS[key].kicker;document.getElementById("tab-question").textContent=TABS[key].question;document.getElementById("data-period").textContent=TABS[key].period;
closeMenu();for(const id of PLOTS[key]){if(!drawn.has(id)){drawn.add(id);Plotly.newPlot(id,FIGURES[id].data,FIGURES[id].layout,config)}}}
for(const k of Object.keys(TABS))document.getElementById("nav-"+k).addEventListener("click",()=>{show(k);scrollTo(0,0)});
document.getElementById("menu-open").addEventListener("click",()=>sidebar.classList.add("sidebar--open"));
document.getElementById("menu-close").addEventListener("click",closeMenu);scrim.addEventListener("click",closeMenu);show("ai");
</script></body></html>
"""


def main() -> None:
    store = load_store()
    defaults = defaults_for(store)
    views = {"ai": ai_view(store, defaults), "news": news_view(store, defaults), "rel": rel_view(store, defaults)}
    layouts = {"ai": tab_ai(store), "news": tab_news(), "rel": tab_rel()}
    pages, figures, plots = "", {}, {}
    for key, (slots, tab_figures, tables) in views.items():
        pages += render(layouts[key], slots, tables)
        plots[key] = list(tab_figures)
        figures |= {name: json.loads(figure.to_json()) for name, figure in tab_figures.items()}

    incidents, items = store.incidents, store.news
    periods = {
        "ai": f"ข้อมูล {t.th_date(incidents['date'].min())} ถึง {t.th_date(incidents['date'].max())} · {len(incidents):,} เหตุการณ์ทั่วโลก",
        "news": f"ข้อมูล {t.th_date(items['date'].min())} ถึง {t.th_date(items['date'].max())} · {len(items):,} โพสต์ของ AFNC",
        "rel": f"ข้อมูล ACSC สัปดาห์ {t.th_week(store.acsc['week_start'].min())} ถึง {t.th_week(store.acsc['week_start'].max())} · {len(store.acsc)} สัปดาห์ที่มีตัวเลข",
    }
    tabs = {key: {**TABS[key], "period": periods[key]} for key in TABS}
    labels = {"ai": ("01", "ความเสี่ยงจาก AI"), "news": ("02", "ข่าวปลอมด้านการเงิน"), "rel": ("03", "ข่าวเท็จกับคดีหลอกลวง")}
    nav = "".join(
        f'<button id="nav-{key}" class="nav__item"><span class="nav__number">{number}</span><span>{label}</span></button>'
        for key, (number, label) in labels.items()
    )
    as_script = lambda value: json.dumps(value, ensure_ascii=False).replace("</", "<\\/")
    page = PAGE
    for token, value in {
        "__TITLE__": TITLE, "__FONT__": t.FONT_URL, "__NAV__": nav, "__PAGES__": pages,
        "__FIGURES__": as_script(figures), "__TABS__": as_script(tabs), "__PLOTS__": as_script(plots),
    }.items():
        page = page.replace(token, value)

    OUT.mkdir(exist_ok=True)
    (OUT / "index.html").write_text(page, encoding="utf-8", newline="\n")
    shutil.copy(ASSETS / "style.css", OUT / "style.css")
    shutil.copy(Path(plotly.__file__).parent / "package_data" / "plotly.min.js", OUT / "plotly.min.js")
    print(f"wrote {OUT / 'index.html'} ({(OUT / 'index.html').stat().st_size / 1e3:.0f} KB)")


if __name__ == "__main__":
    main()
