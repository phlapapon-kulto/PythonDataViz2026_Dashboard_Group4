"""Dash callbacks. They parse Dash events, call analytics and hand back figures."""
from __future__ import annotations

import pandas as pd
from dash import Input, Output, State, ctx
from dash.exceptions import PreventUpdate

from src.analytics import ai_risk_analysis as ai
from src.analytics import financial_news_analysis as news
from src.analytics import scam_correlation_analysis as rel
from src.dashboard import components as c
from src.dashboard import figures as fig
from src.dashboard import narrative as n
from src.dashboard import state as s
from src.dashboard import theme as t
from src.dashboard.data_store import DataStore
from src.dashboard.layout import TABS, cset_coverage
from src.data_cleaning.clean_ai_incidents import HARM_TH, REGION_TH

CLICK_GRAPHS = [
    "ai-top-domains", "ai-treemap", "ai-trend", "ai-region-chart", "ai-harm-chart",
    "news-category-chart", "news-verdict-chart", "news-trend", "news-topic-chart", "news-top-chart",
    "rel-trend", "rel-scatter-cases", "rel-scatter-loss",
]

# Every piece of filter state and the component property that holds it.
BINDINGS = {
    "years": ("global-years", "value"),
    "ai_regions": ("ai-regions", "value"), "ai_domains": ("ai-domains", "value"), "ai_harm": ("ai-harm", "value"),
    "ai_subdomain": ("ai-subdomain", "data"), "ai_month": ("ai-month", "data"),
    "news_scope": ("news-scope", "value"), "news_verdicts": ("news-verdicts", "value"),
    "news_start": ("news-dates", "start_date"), "news_end": ("news-dates", "end_date"),
    "news_keyword": ("news-keyword", "value"), "news_month": ("news-month", "data"),
    "news_topic": ("news-topic", "data"), "news_post": ("news-post", "data"),
    "rel_start": ("rel-dates", "start_date"), "rel_end": ("rel-dates", "end_date"),
    "rel_scope": ("rel-scope", "value"), "rel_topic": ("rel-topic", "value"), "rel_cases": ("rel-cases", "value"),
    "rel_loss": ("rel-loss", "value"), "rel_options": ("rel-options", "value"), "rel_week": ("rel-week", "data"),
}

AI_INPUTS = ["years", "ai_regions", "ai_domains", "ai_harm", "ai_subdomain", "ai_month"]
NEWS_INPUTS = ["years", "news_scope", "news_verdicts", "news_start", "news_end", "news_keyword", "news_month", "news_topic", "news_post"]
REL_INPUTS = ["years", "rel_start", "rel_end", "rel_scope", "rel_topic", "rel_cases", "rel_loss", "rel_options", "rel_week"]


def inputs_for(keys: list[str]) -> list[Input]:
    return [Input(*BINDINGS[key]) for key in keys]


def visible_empty(rows: int) -> dict:
    return {"display": "none"} if rows else {"display": "block"}


def sort_page(df: pd.DataFrame, sort_by: list, page: int, size: int, default: str, ascending: bool = False) -> tuple[pd.DataFrame, int]:
    """Server-side sort and paging, so a filter never ships 17,000 rows to the browser."""
    if sort_by:
        column, ascending = sort_by[0]["column_id"], sort_by[0]["direction"] == "asc"
    else:
        column = default
    ordered = df.sort_values(column, ascending=ascending, na_position="last", kind="stable")
    pages = max(1, -(-len(ordered) // size))
    return ordered.iloc[page * size: (page + 1) * size], pages


def register_callbacks(app, store: DataStore, defaults: dict) -> None:
    incidents, items, panel = store.incidents, store.news, store.panel
    sensitivity = rel.sensitivity_table(panel, items)
    titles = dict(zip(items["post_id"], items["title_clean"].str.slice(0, 40)))
    coverage = cset_coverage(incidents)

    app.clientside_callback(
        """
        function(open, close, scrim, ai, newsTab, relTab, current) {
            const trigger = dash_clientside.callback_context.triggered.map(t => t.prop_id)[0] || "";
            return trigger.startsWith("menu-open") ? "sidebar sidebar--open" : "sidebar";
        }
        """,
        Output("sidebar", "className"),
        Input("menu-open", "n_clicks"), Input("menu-close", "n_clicks"), Input("scrim", "n_clicks"),
        Input("nav-ai", "n_clicks"), Input("nav-news", "n_clicks"), Input("nav-rel", "n_clicks"),
        State("sidebar", "className"),
        prevent_initial_call=True,
    )

    @app.callback(
        Output("active-tab", "data"),
        Input("nav-ai", "n_clicks"), Input("nav-news", "n_clicks"), Input("nav-rel", "n_clicks"),
        prevent_initial_call=True,
    )
    def choose_tab(*_):
        return ctx.triggered_id.removeprefix("nav-")

    @app.callback(
        [Output(f"nav-{key}", "className") for key in TABS]
        + [Output(f"page-{key}", "className") for key in TABS]
        + [Output(f"filters-{key}", "className") for key in TABS]
        + [Output("tab-kicker", "children"), Output("tab-question", "children"), Output("data-period", "children")],
        Input("active-tab", "data"),
    )
    def show_tab(active):
        nav = ["nav__item nav__item--active" if key == active else "nav__item" for key in TABS]
        pages = ["page" if key == active else "page page--hidden" for key in TABS]
        panels = ["filters" if key == active else "filters filters--hidden" for key in TABS]
        return [*nav, *pages, *panels, TABS[active]["kicker"], TABS[active]["question"], period_text(active)]

    def period_text(active: str) -> str:
        if active == "ai":
            return f"ข้อมูล {t.th_date(incidents['date'].min())} ถึง {t.th_date(incidents['date'].max())} · {len(incidents):,} เหตุการณ์ทั่วโลก"
        if active == "news":
            return f"ข้อมูล {t.th_date(items['date'].min())} ถึง {t.th_date(items['date'].max())} · {len(items):,} โพสต์ของ AFNC"
        reported = int(panel["acsc_reported"].sum())
        return f"ข้อมูล ACSC สัปดาห์ {t.th_week(store.acsc['week_start'].min())} ถึง {t.th_week(store.acsc['week_start'].max())} · {reported} สัปดาห์ที่มีตัวเลข"

    @app.callback(
        [Output(*BINDINGS[key]) for key in BINDINGS] + [Output(g, "clickData") for g in CLICK_GRAPHS],
        [Input("reset-all", "n_clicks")] + [Input(g, "clickData") for g in CLICK_GRAPHS],
        [State(*BINDINGS[key]) for key in BINDINGS],
        prevent_initial_call=True,
    )
    def on_interaction(_, *values):
        """All chart clicks and Reset meet here, so filter state has one writer."""
        clicks = dict(zip(CLICK_GRAPHS, values[: len(CLICK_GRAPHS)]))
        state = dict(zip(BINDINGS, values[len(CLICK_GRAPHS):]))
        trigger = ctx.triggered_id
        if trigger == "reset-all":
            state = dict(defaults)
        else:
            key = s.click_key(clicks.get(trigger))
            if key is None:
                raise PreventUpdate
            state = s.apply_click(state, trigger, key)
        return [state[key] for key in BINDINGS] + [None] * len(CLICK_GRAPHS)

    @app.callback(
        Output("ai-kpis", "children"), Output("ai-insight", "children"), Output("ai-active", "children"), Output("ai-coverage", "children"),
        Output("ai-trend", "figure"), Output("ai-top-domains", "figure"), Output("ai-treemap", "figure"),
        Output("ai-region-chart", "figure"), Output("ai-harm-chart", "figure"), Output("ai-table", "page_current"),
        Input("active-tab", "data"), *inputs_for(AI_INPUTS), Input("ai-granularity", "value"),
    )
    def render_ai(active, years, regions, domains, harm, subdomain, month, granularity):
        if active != "ai":
            raise PreventUpdate
        f = s.ai_filters(years, regions, domains, harm, subdomain, month)
        filtered = ai.filter_incidents(incidents, f)
        growth = ai.annual_growth(ai.filter_incidents(incidents, f, frozenset({"years", "month"})), f, store.ai_end)

        if granularity == "month":
            trend = fig.ai_monthly(ai.monthly_counts(ai.filter_incidents(incidents, f, frozenset({"month"}))), month)
        else:
            trend = fig.ai_yearly(
                ai.yearly_counts(ai.filter_incidents(incidents, f, frozenset({"years", "month"}))),
                (f.year_from, f.year_to), store.ai_end,
            )
        without_domain = ai.filter_incidents(incidents, f, frozenset({"domains"}))
        warning = n.ai_coverage_warning(regions, harm, coverage)
        return (
            n.ai_kpis(filtered, growth),
            n.ai_insight(filtered, without_domain, domains, growth),
            c.active_chips(n.ai_chips(years, regions, domains, harm, subdomain, month)),
            [c.notice(warning)] if warning else [],
            trend,
            fig.top_domains(ai.top_risk_domains(without_domain, 5, tuple(domains or ())), domains or []),
            fig.risk_treemap(ai.risk_tree(without_domain), domains or [], subdomain),
            fig.region_bars(ai.region_counts(ai.filter_incidents(incidents, f, frozenset({"regions"}))), regions or [], REGION_TH),
            fig.harm_bars(ai.harm_counts(ai.filter_incidents(incidents, f, frozenset({"harm"}))), harm or [], HARM_TH),
            0,
        )

    @app.callback(
        Output("ai-table", "data"), Output("ai-table", "page_count"), Output("ai-table-empty", "style"),
        Input("active-tab", "data"), *inputs_for(AI_INPUTS), Input("ai-table", "page_current"), Input("ai-table", "sort_by"),
        State("ai-table", "page_size"),
    )
    def ai_table(active, years, regions, domains, harm, subdomain, month, page, sort_by, size):
        if active != "ai":
            raise PreventUpdate
        filtered = ai.filter_incidents(incidents, s.ai_filters(years, regions, domains, harm, subdomain, month)).copy()
        filtered["region_th"] = filtered["location_region"].map(REGION_TH)
        rows, pages = sort_page(filtered, sort_by, page or 0, size, "date")
        shown = pd.DataFrame({
            "incident_id": rows["incident_id"].astype(int),
            "date": [t.th_date(d) for d in rows["date"]],
            "title": rows["title"],
            "risk_domain_th": rows["risk_domain_th"].fillna("ยังไม่จำแนก"),
            "region_th": rows["region_th"].fillna("—"),
            "injuries": [dash_if_blank(v, t.fmt_int) for v in rows["injuries"]],
            "lives_lost": [dash_if_blank(v, t.fmt_int) for v in rows["lives_lost"]],
        })
        return shown.to_dict("records"), pages, visible_empty(len(filtered))

    @app.callback(
        Output("news-kpis", "children"), Output("news-insight", "children"), Output("news-active", "children"),
        Output("news-category-chart", "figure"), Output("news-verdict-chart", "figure"), Output("news-trend", "figure"),
        Output("news-topic-chart", "figure"), Output("news-top-chart", "figure"), Output("news-table", "page_current"),
        Input("active-tab", "data"), *inputs_for(NEWS_INPUTS),
    )
    def render_news(active, years, scope, verdicts, start, end, keyword, month, topic, post):
        if active != "news":
            raise PreventUpdate
        f = s.news_filters(years, scope, verdicts, start, end, keyword, month, topic, post)
        filtered = news.filter_news(items, f)
        kpi = news.news_kpis(filtered)

        categories = news.false_by_category(news.filter_news(items, f, frozenset({"scope", "topic", "post"})))
        selected_category = news.FINANCE_CORE_CATEGORY if scope == news.SCOPE_CORE else scope
        if scope in (news.SCOPE_EXTENDED, news.SCOPE_ALL):
            selected_category = None
        without_verdict = news.filter_news(items, f, frozenset({"verdicts"}))
        centre = t.fmt_pct(kpi["fake_pct"])
        return (
            n.news_kpis(kpi, scope),
            n.news_insight(categories, news.filter_news(items, f, frozenset({"topic", "post"})), scope),
            c.active_chips(n.news_chips(years, scope, verdicts, start, end, defaults, keyword, month, topic, post, titles)),
            fig.category_bars(categories, selected_category),
            fig.verdict_donut(news.verdict_distribution(without_verdict), verdicts or [], centre, "ข่าวปลอม"),
            fig.news_trend(
                news.monthly_trend(news.filter_news(items, f, frozenset({"month"}))), month, news.scope_is_finance(scope),
            ),
            fig.topic_bars(
                news.false_by_topic(news.filter_news(items, f, frozenset({"topic"}))) if news.scope_is_finance(scope) else pd.DataFrame(),
                topic,
            ),
            fig.top_viewed_bars(news.top_viewed(news.filter_news(items, f, frozenset({"post"}))), post),
            0,
        )

    @app.callback(
        Output("news-table", "data"), Output("news-table", "page_count"), Output("news-table-empty", "style"),
        Input("active-tab", "data"), *inputs_for(NEWS_INPUTS), Input("news-table", "page_current"), Input("news-table", "sort_by"),
        State("news-table", "page_size"),
    )
    def news_table(active, years, scope, verdicts, start, end, keyword, month, topic, post, page, sort_by, size):
        if active != "news":
            raise PreventUpdate
        f = s.news_filters(years, scope, verdicts, start, end, keyword, month, topic, post)
        filtered = news.filter_news(items, f)
        sort_map = {"title_link": "title_clean", "verdict_th_display": "verdict_group"}
        sort_by = [{**rule, "column_id": sort_map.get(rule["column_id"], rule["column_id"])} for rule in sort_by or []]
        rows, pages = sort_page(filtered, sort_by, page or 0, size, "date")
        rows = rows.assign(
            date=[t.th_date(d) for d in rows["date"]],
            title_link=[f"[{escape_md(title)}]({url})" for title, url in zip(rows["title_clean"], rows["url"])],
            verdict_th_display=rows["verdict_group"].map(t.VERDICT_TH),
        )
        shown = rows[["date", "title_link", "category_th", "verdict_th_display", "view_count"]]
        return shown.astype(object).to_dict("records"), pages, visible_empty(len(filtered))

    def rel_frame(years, start, end, scope, topic, cases, loss, options) -> tuple[pd.DataFrame, rel.RelFilters]:
        f = s.rel_filters(years, start, end, scope, topic, cases, loss, options)
        return rel.apply_filters(rel.weekly_frame(panel, items, f.scope, f.topic), f), f

    @app.callback(
        Output("rel-kpis", "children"), Output("rel-insight", "children"), Output("rel-active", "children"),
        Output("rel-trend", "figure"), Output("rel-scatter-cases", "figure"), Output("rel-scatter-loss", "figure"),
        Output("rel-r-cases", "children"), Output("rel-r-loss", "children"), Output("rel-sensitivity", "children"),
        Output("rel-table", "page_current"),
        Input("active-tab", "data"), *inputs_for(REL_INPUTS),
    )
    def render_rel(active, years, start, end, scope, topic, cases, loss, options, week):
        if active != "rel":
            raise PreventUpdate
        frame, f = rel_frame(years, start, end, scope, topic, cases, loss, options)
        with_cases = rel.pearson(frame["false_count"], frame["cases_used"])
        with_loss = rel.pearson(frame["false_count"], frame["loss_used"])
        changes = rel.consecutive_changes(frame)
        change_r = rel.pearson(changes["false_count"], changes["cases_used"])

        selected = frame[frame["week_start"] == pd.Timestamp(week)] if week else frame.iloc[0:0]
        week_row = selected.iloc[0] if len(selected) else None
        return (
            n.rel_kpis(rel.relationship_kpis(frame), week_row),
            n.rel_insight(with_cases, with_loss, change_r),
            c.active_chips(n.rel_chips(years, start, end, defaults, scope, topic, cases, loss, options, week)),
            fig.weekly_comparison(frame, week, f.include_suspect),
            fig.scatter(
                frame, "cases_used", 1, "คดีหลอกลวงออนไลน์ (คดีต่อสัปดาห์)", "คดี %{y:,.0f} คดี",
                rel.trend_line(frame["false_count"], frame["cases_used"]), week,
            ),
            fig.scatter(
                frame, "loss_used", 1e6, "มูลค่าความเสียหาย (ล้านบาทต่อสัปดาห์)", "ความเสียหาย %{y:,.1f} ล้านบาท",
                rel.trend_line(frame["false_count"], frame["loss_used"]), week,
            ),
            n.correlation_line(with_cases), n.correlation_line(with_loss),
            n.sensitivity_rows(sensitivity),
            0,
        )

    @app.callback(
        Output("rel-table", "data"), Output("rel-table", "page_count"), Output("rel-table-empty", "style"),
        Input("active-tab", "data"), *inputs_for(REL_INPUTS), Input("rel-table", "page_current"), Input("rel-table", "sort_by"),
        State("rel-table", "page_size"),
    )
    def rel_table(active, years, start, end, scope, topic, cases, loss, options, week, page, sort_by, size):
        if active != "rel":
            raise PreventUpdate
        frame, _ = rel_frame(years, start, end, scope, topic, cases, loss, options)
        if week:
            frame = frame[frame["week_start"] == pd.Timestamp(week)]
        sort_map = {"week_label": "week_start", "cases_display": "cases", "loss_display": "loss_baht", "per_case_display": "loss_per_case_baht", "status_display": "reporting_status", "precision_display": "loss_precision"}
        sort_by = [{**rule, "column_id": sort_map.get(rule["column_id"], rule["column_id"])} for rule in sort_by or []]
        rows, pages = sort_page(frame, sort_by, page or 0, size, "week_start")
        table = pd.DataFrame({
            "week_label": [t.th_week(w) for w in rows["week_start"]],
            "false_count": rows["false_count"].to_numpy(),
            "cases_display": [dash_if_blank(v, t.fmt_int) for v in rows["cases"]],
            "loss_display": [dash_if_blank(v, t.fmt_million) for v in rows["loss_baht"]],
            "per_case_display": [dash_if_blank(v, t.fmt_int) for v in rows["loss_per_case_baht"]],
            "precision_display": rows["loss_precision"].map({"exact": "ถึงบาท", "rounded": "ปัดเศษ"}).fillna("—").to_numpy(),
            "status_display": [week_status(row) for row in rows.itertuples()],
        })
        return table.to_dict("records"), pages, visible_empty(len(frame))


def escape_md(text: str) -> str:
    return text.replace("[", "\\[").replace("]", "\\]")


def dash_if_blank(value, formatter) -> str:
    return "—" if pd.isna(value) else formatter(value)


STATUS_TH = {
    "reported": "มีรายงาน",
    "before_acsc_briefings": "ก่อน ACSC เริ่มรายงาน",
    "no_figure_found": "ไม่พบตัวเลข",
    "not_yet_announced": "ยังไม่ประกาศ",
}
QUALITY_TH = {
    "suspect": "น่าสงสัย ตัดออกจากสถิติ",
    "eight_day_period": "ช่วงรายงาน 8 วัน",
    "rounded_case_count": "ตัวเลขปัดเป็น 5,000",
    "comparison_note": "ค่าเปรียบเทียบอ้างสัปดาห์น่าสงสัย",
}


def week_status(row) -> str:
    return QUALITY_TH.get(row.quality_status, STATUS_TH[row.reporting_status])
