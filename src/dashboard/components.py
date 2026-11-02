"""Small layout pieces: KPI tiles, chart cards, tables and notes."""
from __future__ import annotations

from dash import dash_table, dcc, html

from src.dashboard import theme as t
from src.dashboard.figures import GRAPH_CONFIG

SOURCE_AFNC = "ศูนย์ต่อต้านข่าวปลอม (AFNC) ข้อมูล ณ 1 พ.ย. 2026"
SOURCE_ACSC = "ศูนย์ปฏิบัติการต่อต้านการหลอกลวงออนไลน์ (ACSC) สำนักงานตำรวจแห่งชาติ"
SOURCE_REL = f"{SOURCE_AFNC} และ {SOURCE_ACSC}"
WIDE_COLUMNS = ("title", "title_link")
DATE_COLUMNS = ("date", "week_label")


def kpi(label: str, value: str, note: str = "", hero: bool = False, span: int = 3) -> html.Div:
    return html.Div(
        className=f"kpi span-{span}{' kpi--hero' if hero else ''}",
        children=[
            html.Div(label, className="kpi__label"),
            html.Div(value, className="kpi__value"),
            html.Div(note, className="kpi__note"),
        ],
    )


def chart_card(
    title: str, subtitle, graph_id: str, source: str, span: int, height: int = 320, hint: str = "", extra=None,
    subtitle_id: str | None = None, fill: bool = False,
) -> html.Section:
    head = [html.H3(title, className="card__title")]
    if subtitle_id:
        head.append(html.P(subtitle, id=subtitle_id, className="card__subtitle"))
    elif subtitle:
        head.append(html.P(subtitle, className="card__subtitle"))
    return html.Section(
        className=f"card span-{span}{' card--fill' if fill else ''}",
        children=[
            html.Header(className="card__head", children=[html.Div(head)] + ([extra] if extra is not None else [])),
            dcc.Graph(id=graph_id, config=GRAPH_CONFIG, style={"height": f"{height}px"}, className="card__chart"),
            html.Footer(className="card__foot", children=[html.Span(f"แหล่งข้อมูล: {source}"), html.Span(hint, className="card__hint")]),
        ],
    )


def data_table(table_id: str, columns: list[dict], page_size: int = 10) -> html.Div:
    return html.Div(children=[
        dash_table.DataTable(
            id=table_id, columns=columns, data=[], page_current=0, page_size=page_size, page_count=0,
            page_action="custom", sort_action="custom", sort_mode="single", sort_by=[],
            markdown_options={"link_target": "_blank"}, cell_selectable=False,
            style_as_list_view=True,
            style_table={"overflowX": "auto"},
            style_cell_conditional=[{"if": {"column_id": column}, "minWidth": "300px"} for column in WIDE_COLUMNS]
            + [{"if": {"column_id": column}, "minWidth": "118px", "whiteSpace": "nowrap"} for column in DATE_COLUMNS],
            style_header={"backgroundColor": "transparent", "color": t.INK_MUTED, "fontWeight": 500, "border": "none", "borderBottom": f"1px solid {t.HAIRLINE}", "fontFamily": t.FONT, "fontSize": "13px", "padding": "10px 12px"},
            style_cell={"backgroundColor": "transparent", "color": t.INK, "fontFamily": t.FONT, "fontSize": "14px", "padding": "11px 12px", "border": "none", "borderBottom": f"1px solid {t.HAIRLINE}", "textAlign": "left", "whiteSpace": "normal", "height": "auto", "minWidth": "90px"},
        ),
        html.Div("ไม่พบข้อมูล", id=f"{table_id}-empty", className="table-empty", style={"display": "none"}),
    ])


def table_card(title: str, subtitle: str, table, source: str) -> html.Section:
    return html.Section(
        className="card span-12",
        children=[
            html.Header(className="card__head", children=[html.Div([html.H3(title, className="card__title"), html.P(subtitle, className="card__subtitle")])]),
            table,
            html.Footer(className="card__foot", children=[html.Span(f"แหล่งข้อมูล: {source}")]),
        ],
    )


def note_card(title: str, items: list, span: int = 12, tone: str = "") -> html.Section:
    return html.Section(
        className=f"card card--note {tone} span-{span}",
        children=[html.H3(title, className="card__title"), html.Ul([html.Li(item) for item in items], className="note-list")],
    )


def notice(text: str) -> html.Div:
    return html.Div(text, className="notice")


def field(label: str, control, hint: str = "") -> html.Div:
    children = [html.Label(label, className="field__label"), control]
    if hint:
        children.append(html.Div(hint, className="field__hint"))
    return html.Div(children, className="field")


def active_chips(labels: list[str]) -> list:
    if not labels:
        return [html.Span("ยังไม่ได้เลือกตัวกรอง คลิกแท่งหรือจุดบนกราฟเพื่อกรองได้", className="chips__empty")]
    return [html.Span(label, className="chip") for label in labels]
