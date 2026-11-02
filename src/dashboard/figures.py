"""Plotly figure builders. Each takes prepared data and returns a figure.

Chart titles live in the card header. Every figure here supplies axis units, a
tooltip and an empty state. Clickable marks carry their filter key in customdata.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from src.analytics.ai_risk_analysis import MISSING
from src.analytics.scam_correlation_analysis import RELABEL_MONTH
from src.config import DISTORTED, FAKE, SUSPECT_WEEK, TRUE
from src.dashboard import theme as t

EMPTY_TITLE = "ไม่พบข้อมูล"
GRAPH_CONFIG = {"displayModeBar": False, "scrollZoom": False, "doubleClick": False, "responsive": True}
BAR_ROW_PX = 46


def base_layout(**overrides) -> dict:
    axis = dict(
        gridcolor=t.HAIRLINE, zeroline=False, showline=False, ticks="",
        tickfont=dict(color=t.INK_MUTED, size=12), title=dict(font=dict(color=t.INK_MUTED, size=12)),
    )
    layout = dict(
        font=dict(family=t.FONT, color=t.INK, size=13),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=4, r=12, t=8, b=8), showlegend=False, dragmode=False,
        hoverlabel=dict(bgcolor=t.INK, bordercolor=t.INK, font=dict(family=t.FONT, color="#FFFFFF", size=13), align="left"),
        xaxis=dict(axis), yaxis=dict(axis),
    )
    layout.update(overrides)
    return layout


def empty_figure(hint: str = "ลองปรับตัวกรอง หรือกดล้างตัวกรองทั้งหมด") -> go.Figure:
    figure = go.Figure()
    figure.update_layout(**base_layout(
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        annotations=[dict(
            text=f"<b>{EMPTY_TITLE}</b><br><span style='font-size:13px;color:{t.INK_MUTED}'>{hint}</span>",
            x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False, font=dict(size=17, color=t.INK), align="center",
        )],
    ))
    return figure


def _shorten(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _row_labels(labels: list[str], limit: int = 90) -> list[dict]:
    """Category names sit above their bars, so long Thai labels survive a phone width."""
    return [
        dict(
            x=0, y=i, xref="paper", yref="y", xanchor="left", yanchor="bottom", yshift=9,
            text=_shorten(label, limit), showarrow=False, font=dict(size=13, color=t.INK), align="left",
        )
        for i, label in enumerate(labels)
    ]


def _bar_layout(rows: int, labels: list[str], x_title: str, max_value: float, label_limit: int = 90) -> dict:
    return base_layout(
        barmode="stack", bargap=0.72, hovermode="y unified", hoverdistance=60,
        margin=dict(l=4, r=60, t=20, b=44),
        xaxis=dict(
            title=dict(text=x_title, font=dict(color=t.INK_MUTED, size=12)), gridcolor=t.HAIRLINE, zeroline=False,
            range=[0, max_value * 1.04 if max_value else 1], tickfont=dict(color=t.INK_MUTED, size=12), fixedrange=True,
            tickformat="~s",
        ),
        yaxis=dict(
            showticklabels=False, showgrid=False, zeroline=False, range=[rows - 0.45, -0.75], fixedrange=True,
            type="linear", tickvals=list(range(rows)),
        ),
        annotations=_row_labels(labels, label_limit),
    )


def hbar(
    labels: list[str], values: list, keys: list, selected: list, color: str, unit: str, x_title: str,
    hover_extra: list[str] | None = None, label_limit: int = 90,
) -> go.Figure:
    """Horizontal bars for one series. Selection dims the other bars, so they stay clickable."""
    if not labels:
        return empty_figure()
    colors = [color if not selected or key in selected else t.DIMMED for key in keys]
    extra = hover_extra or [""] * len(labels)
    positions = list(range(len(labels)))
    figure = go.Figure(go.Bar(
        y=positions, x=values, orientation="h", marker=dict(color=colors, cornerradius=4), customdata=keys,
        text=[f"{value:,}" for value in values], textposition="outside", cliponaxis=False,
        textfont=dict(color=t.INK, size=13),
        hovertext=[f"<b>{value:,} {unit}</b><br>{label}{tail}" for value, label, tail in zip(values, labels, extra)],
        hovertemplate="%{hovertext}<extra></extra>",
    ))
    figure.update_layout(**_bar_layout(len(labels), labels, x_title, max(values), label_limit))
    figure.update_layout(hovermode="y", hoverdistance=-1)
    return figure


def top_domains(data: pd.DataFrame, selected: list) -> go.Figure:
    extra = [f"<br>{row.risk_domain}<br>{row.share_pct:.1f}% ของเหตุการณ์ที่จำแนกแล้ว" for row in data.itertuples()]
    return hbar(
        data["risk_domain_th"].tolist(), data["incidents"].tolist(), data["risk_domain"].tolist(), selected,
        t.BLUE, "เหตุการณ์", "จำนวนเหตุการณ์ (รายการ)", extra,
    )


def region_bars(data: pd.DataFrame, selected: list, names: dict) -> go.Figure:
    labels = [names.get(region, region) for region in data["region"]]
    extra = [f"<br>{region}" for region in data["region"]]
    return hbar(labels, data["incidents"].tolist(), data["region"].tolist(), selected, t.BLUE, "เหตุการณ์", "จำนวนเหตุการณ์ (รายการ)", extra)


def harm_bars(data: pd.DataFrame, selected: list, names: dict) -> go.Figure:
    labels = [names.get(harm, harm) for harm in data["harm"]]
    extra = [f"<br>Harm Domain = {harm}" for harm in data["harm"]]
    return hbar(labels, data["incidents"].tolist(), data["harm"].tolist(), selected, t.ORANGE, "เหตุการณ์", "จำนวนเหตุการณ์ (รายการ)", extra)


def _mark_band(figure: go.Figure, start, end) -> None:
    figure.add_vrect(x0=start, x1=end, fillcolor=t.YELLOW, opacity=0.35, line_width=0, layer="below")


def ai_yearly(data: pd.DataFrame, years: tuple[int | None, int | None], data_end: pd.Timestamp) -> go.Figure:
    """Yearly line. The last year is drawn dashed because it stops before December."""
    if data["incidents"].sum() == 0:
        return empty_figure()
    partial_year = data_end.year if (data_end.month, data_end.day) != (12, 31) else None
    complete = data[data["year"] != partial_year]
    partial = data[data["year"] == partial_year]

    figure = go.Figure(go.Scatter(
        x=complete["year"], y=complete["incidents"], mode="lines+markers",
        line=dict(color=t.BLUE, width=2), marker=dict(size=8, color=t.BLUE, line=dict(color=t.SURFACE, width=2)),
        customdata=[f"year:{y}" for y in complete["year"]],
        hovertemplate="<b>%{y:,} เหตุการณ์</b><br>ปี %{x}<extra></extra>",
    ))
    if len(partial) and len(complete):
        last = complete.iloc[-1]
        point = partial.iloc[0]
        figure.add_scatter(
            x=[last["year"], point["year"]], y=[last["incidents"], point["incidents"]], mode="lines",
            line=dict(color=t.BLUE, width=2, dash="dot"), hoverinfo="skip",
        )
        figure.add_scatter(
            x=[point["year"]], y=[point["incidents"]], mode="markers",
            marker=dict(size=10, color=t.SURFACE, line=dict(color=t.BLUE, width=2)),
            customdata=[f"year:{point['year']}"],
            hovertemplate=f"<b>%{{y:,}} เหตุการณ์</b><br>ปี %{{x}} ถึง {t.th_date(data_end)} ยังไม่ครบปี<extra></extra>",
        )
    peak = data.loc[data["incidents"].idxmax()]
    annotations = [dict(x=peak["year"], y=peak["incidents"], text=f"<b>{peak['incidents']:,}</b>", showarrow=False, yshift=14, font=dict(size=13, color=t.INK))]
    if len(partial):
        point = partial.iloc[0]
        annotations.append(dict(
            x=point["year"], y=point["incidents"], text=f"{point['incidents']:,}<br>ถึง {t.th_date(data_end)}",
            showarrow=False, xshift=-12, yshift=-26, xanchor="right", font=dict(size=12, color=t.INK_SOFT), align="right",
        ))
    figure.update_layout(**base_layout(
        hovermode="x", hoverdistance=40, margin=dict(l=4, r=12, t=22, b=44), annotations=annotations,
        xaxis=dict(
            title=dict(text="ปีที่เกิดเหตุ (ค.ศ.)", font=dict(color=t.INK_MUTED, size=12)), showgrid=False,
            tickmode="linear", dtick=2, tickfont=dict(color=t.INK_MUTED, size=12), fixedrange=True, range=[data["year"].min() - 0.4, data["year"].max() + 0.4],
        ),
        yaxis=dict(
            title=dict(text="จำนวนเหตุการณ์ (รายการ)", font=dict(color=t.INK_MUTED, size=12)), gridcolor=t.HAIRLINE,
            zeroline=False, rangemode="tozero", tickfont=dict(color=t.INK_MUTED, size=12), fixedrange=True,
        ),
    ))
    low, high = years
    if low is not None or high is not None:
        _mark_band(figure, (low or data["year"].min()) - 0.4, (high or data["year"].max()) + 0.4)
    return figure


def ai_monthly(data: pd.DataFrame, selected_month: str | None) -> go.Figure:
    if data.empty:
        return empty_figure()
    months = pd.to_datetime(data["month"] + "-01")
    figure = go.Figure(go.Scatter(
        x=months, y=data["incidents"], mode="lines+markers", line=dict(color=t.BLUE, width=2),
        marker=dict(size=7, color=t.BLUE, line=dict(color=t.SURFACE, width=1)), customdata=[f"month:{m}" for m in data["month"]],
        text=[t.th_month(m) for m in data["month"]], hovertemplate="<b>%{y:,} เหตุการณ์</b><br>%{text}<extra></extra>",
    ))
    figure.update_layout(**base_layout(
        hovermode="x", hoverdistance=40, margin=dict(l=4, r=12, t=14, b=44),
        xaxis=dict(title=dict(text="เดือนที่เกิดเหตุ", font=dict(color=t.INK_MUTED, size=12)), showgrid=False, tickfont=dict(color=t.INK_MUTED, size=12), tickformat="%Y", fixedrange=True),
        yaxis=dict(title=dict(text="จำนวนเหตุการณ์ (รายการ)", font=dict(color=t.INK_MUTED, size=12)), gridcolor=t.HAIRLINE, zeroline=False, rangemode="tozero", tickfont=dict(color=t.INK_MUTED, size=12), fixedrange=True),
    ))
    if selected_month:
        start = pd.Timestamp(f"{selected_month}-01")
        _mark_band(figure, start - pd.Timedelta(days=15), start + pd.Timedelta(days=15))
    return figure


def _tile_color(row, selected_domains: list, selected_subdomain: str | None) -> str:
    base = t.UNCLASSIFIED_COLOR if row.domain == MISSING else t.DOMAIN_COLOR.get(row.domain, t.DIMMED)
    if not selected_domains and not selected_subdomain:
        return base
    if selected_subdomain:
        return base if row.subdomain == selected_subdomain else t.DIMMED
    return base if row.domain in selected_domains else t.DIMMED


def risk_treemap(tree: pd.DataFrame, selected_domains: list, selected_subdomain: str | None) -> go.Figure:
    if tree.empty:
        return empty_figure()
    colors = [_tile_color(row, selected_domains, selected_subdomain) for row in tree.itertuples()]
    text_colors = [t.INK if color in t.LIGHT_TILES else "#FFFFFF" for color in colors]
    figure = go.Figure(go.Treemap(
        ids=tree["id"], labels=tree["label"], parents=tree["parent"], values=tree["incidents"], branchvalues="total",
        customdata=tree["english"], maxdepth=2, root=dict(color="rgba(0,0,0,0)"),
        marker=dict(colors=colors, line=dict(color=t.SURFACE, width=2), pad=dict(t=26, l=3, r=3, b=3)),
        textfont=dict(family=t.FONT, size=13, color=text_colors),
        texttemplate="%{label}<br><b>%{value:,}</b>", textposition="top left",
        hovertemplate="<b>%{value:,} เหตุการณ์</b><br>%{label}<br>%{customdata}<extra></extra>",
        pathbar=dict(visible=False), tiling=dict(pad=2),
    ))
    figure.update_layout(**base_layout(margin=dict(l=0, r=0, t=0, b=0)))
    return figure


def category_bars(data: pd.DataFrame, selected: str | None) -> go.Figure:
    """Fake and distorted posts per AFNC category, stacked so the total reads from the tip."""
    if data.empty or data["total"].sum() == 0:
        return empty_figure("กราฟนี้นับเฉพาะข่าวปลอมและข่าวบิดเบือน")
    data = data.reset_index(drop=True)
    labels = data["category_th"].tolist()
    positions = list(range(len(labels)))
    keys = labels
    active = [not selected or key == selected for key in keys]
    figure = go.Figure()
    for group in (FAKE, DISTORTED):
        figure.add_bar(
            y=positions, x=data[group], orientation="h", name=t.VERDICT_TH[group], customdata=keys, showlegend=False,
            marker=dict(color=[t.VERDICT_COLOR[group] if on else t.DIMMED for on in active], cornerradius=3),
            hovertemplate=f"<b>%{{x:,}} รายการ</b> {t.VERDICT_TH[group]}<extra></extra>",
        )
        # A separate empty trace keeps the legend swatch in colour when bars are dimmed.
        figure.add_bar(x=[None], y=[None], name=t.VERDICT_TH[group], marker=dict(color=t.VERDICT_COLOR[group]), hoverinfo="skip")
    figure.update_layout(**_bar_layout(len(labels), labels, "จำนวนข่าวเท็จ (รายการ)", float(data["total"].max())))
    figure.update_layout(
        showlegend=True, legend=dict(orientation="h", x=0, y=1.08, font=dict(size=12, color=t.INK_SOFT), traceorder="normal"),
        hovermode="y", hoverdistance=-1, margin=dict(l=4, r=60, t=34, b=44),
    )
    figure.add_scatter(
        x=data["total"], y=positions, mode="text", text=[f"{value:,}" for value in data["total"]],
        textposition="middle right", textfont=dict(size=13, color=t.INK), hoverinfo="skip", showlegend=False, cliponaxis=False,
    )
    return figure


def verdict_donut(data: pd.DataFrame, selected: list, centre_value: str, centre_label: str) -> go.Figure:
    if data.empty:
        return empty_figure()
    groups = data["verdict_group"].tolist()
    colors = [t.VERDICT_COLOR[g] if not selected or g in selected else t.DIMMED for g in groups]
    figure = go.Figure(go.Pie(
        labels=[t.VERDICT_TH[g] for g in groups], values=data["posts"], customdata=groups, hole=0.7, sort=False,
        direction="clockwise", marker=dict(colors=colors, line=dict(color=t.SURFACE, width=2)), textinfo="none",
        hovertemplate="<b>%{value:,} รายการ</b><br>%{label} · %{percent}<extra></extra>",
    ))
    figure.update_layout(**base_layout(
        margin=dict(l=8, r=8, t=8, b=8), showlegend=True,
        legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.04, font=dict(size=12, color=t.INK_SOFT)),
        annotations=[dict(
            text=f"<b style='font-size:30px'>{centre_value}</b><br><span style='font-size:12px;color:{t.INK_MUTED}'>{centre_label}</span>",
            x=0.5, y=0.52, xref="paper", yref="paper", showarrow=False, font=dict(color=t.INK),
        )],
    ))
    return figure


def news_trend(data: pd.DataFrame, selected_month: str | None, show_relabel: bool) -> go.Figure:
    if data.empty:
        return empty_figure()
    months = pd.to_datetime(data["month"] + "-01")
    labels = [t.th_month(m) for m in data["month"]]
    figure = go.Figure()
    for group in (FAKE, DISTORTED, TRUE):
        if data[group].sum() == 0:
            continue
        figure.add_scatter(
            x=months, y=data[group], mode="lines", name=t.VERDICT_TH[group], customdata=data["month"], text=labels,
            line=dict(color=t.VERDICT_COLOR[group], width=2),
            hovertemplate=f"<b>%{{y:,}} รายการ</b> {t.VERDICT_TH[group]}<extra></extra>",
        )
    figure.update_layout(**base_layout(
        hovermode="x unified", hoverdistance=60, showlegend=True, margin=dict(l=4, r=12, t=32, b=44),
        legend=dict(orientation="h", x=0, y=1.12, font=dict(size=12, color=t.INK_SOFT)),
        xaxis=dict(
            title=dict(text="เดือนที่เผยแพร่", font=dict(color=t.INK_MUTED, size=12)), showgrid=False,
            tickfont=dict(color=t.INK_MUTED, size=12), hoverformat="เดือน %m/%Y", fixedrange=True,
        ),
        yaxis=dict(
            title=dict(text="จำนวนข่าว (รายการต่อเดือน)", font=dict(color=t.INK_MUTED, size=12)), gridcolor=t.HAIRLINE,
            zeroline=False, rangemode="tozero", tickfont=dict(color=t.INK_MUTED, size=12), fixedrange=True,
        ),
    ))
    relabel = pd.Timestamp(f"{RELABEL_MONTH}-01")
    if show_relabel and months.min() <= relabel <= months.max():
        figure.add_vline(x=relabel, line_width=1, line_color=t.INK_SOFT)
        figure.add_annotation(
            x=relabel, y=1, yref="paper", text=f"{t.th_month(RELABEL_MONTH)} AFNC เริ่มลงคำตัดสิน<br>หมวดอาชญากรรมออนไลน์", showarrow=False,
            xanchor="right", yanchor="bottom", align="right", font=dict(size=11, color=t.INK_SOFT),
        )
    if selected_month:
        start = pd.Timestamp(f"{selected_month}-01")
        _mark_band(figure, start - pd.Timedelta(days=15), start + pd.Timedelta(days=15))
    return figure


def topic_bars(data: pd.DataFrame, selected: str | None) -> go.Figure:
    if data.empty:
        return empty_figure("กราฟนี้แสดงเฉพาะข่าวในขอบเขตการเงิน")
    return hbar(
        data["finance_topic"].tolist(), [int(v) for v in data["posts"]], data["finance_topic_id"].tolist(),
        [selected] if selected else [], t.PINK, "รายการ", "ข่าวปลอม + ข่าวบิดเบือน (รายการ)",
    )


def top_viewed_bars(data: pd.DataFrame, selected: int | None) -> go.Figure:
    if data.empty:
        return empty_figure()
    labels = data["title_clean"].tolist()
    extra = [
        f"<br>{t.th_date(row.date)} · {row.category_th} · {t.VERDICT_TH.get(row.verdict_group, '')}"
        for row in data.itertuples()
    ]
    return hbar(
        labels, [int(v) for v in data["view_count"]], [int(p) for p in data["post_id"]], [selected] if selected else [],
        t.BLUE, "ครั้ง", "ยอดเข้าชมสะสม ณ 1 พ.ย. 2026 (ครั้ง)", extra, label_limit=52,
    )


def weekly_comparison(frame: pd.DataFrame, selected_week: str | None, include_suspect: bool) -> go.Figure:
    """Three stacked panels on one time axis, never a dual-axis chart."""
    if frame.empty:
        return empty_figure("ข้อมูล ACSC เริ่มสัปดาห์ 9–15 พ.ย. 2025 ลองขยายช่วงเวลา")
    weeks = frame["week_start"]
    keys = weeks.dt.strftime("%Y-%m-%d").tolist()
    labels = [t.th_week(w) for w in weeks]
    if include_suspect:
        cases = pd.to_numeric(frame["cases"], errors="coerce")
        loss = pd.to_numeric(frame["loss_baht"], errors="coerce")
    else:
        cases, loss = frame["cases_used"], frame["loss_used"].where(frame["cases_used"].notna())
    # Blank weeks stay blank: the line breaks instead of bridging an unreported week.
    figure = go.Figure()
    figure.add_bar(
        x=weeks, y=frame["false_count"], name="ข่าวเท็จด้านการเงิน", customdata=keys, text=labels,
        marker=dict(color=t.PINK, cornerradius=2), textposition="none",
        hovertemplate="ข่าวเท็จ <b>%{y:,}</b> รายการ<extra></extra>", yaxis="y",
    )
    figure.add_scatter(
        x=weeks, y=cases, mode="lines+markers", name="คดีหลอกลวงออนไลน์", customdata=keys, connectgaps=False,
        line=dict(color=t.BLUE, width=2), marker=dict(size=7, color=t.BLUE, line=dict(color=t.SURFACE, width=1)),
        hovertemplate="คดี <b>%{y:,.0f}</b> คดี<extra></extra>", yaxis="y2",
    )
    figure.add_bar(
        x=weeks, y=loss / 1e6, name="มูลค่าความเสียหาย", customdata=keys,
        marker=dict(color=t.ORANGE, cornerradius=2),
        hovertemplate="ความเสียหาย <b>%{y:,.1f}</b> ล้านบาท<extra></extra>", yaxis="y3",
    )
    axis_text = dict(color=t.INK_MUTED, size=12)
    panels = [
        ("ข่าวเท็จด้านการเงิน (รายการต่อสัปดาห์)", 1.0),
        ("คดีหลอกลวงออนไลน์ (คดีต่อสัปดาห์)", 0.655),
        ("มูลค่าความเสียหาย (ล้านบาทต่อสัปดาห์)", 0.31),
    ]
    annotations = [
        dict(text=f"<b>{text}</b>", x=0, y=y, xref="paper", yref="paper", xanchor="left", yanchor="bottom", showarrow=False, font=dict(size=12, color=t.INK_SOFT))
        for text, y in panels
    ]
    step = "2MS" if (weeks.max() - weeks.min()).days > 150 else "MS"
    ticks = pd.date_range(weeks.min().to_period("M").to_timestamp(), weeks.max(), freq=step)
    suspect = pd.Timestamp(SUSPECT_WEEK)
    if not include_suspect and (weeks == suspect).any():
        published = int(frame.loc[weeks == suspect, "cases"].iloc[0])
        annotations.append(dict(
            x=suspect, y=0.655, xref="x", yref="paper", yanchor="top", showarrow=False, yshift=-2,
            text=f"{t.th_week(suspect)} ตัดออก: ประกาศ {published:,} คดี", font=dict(size=11, color=t.INK_SOFT),
        ))
    figure.update_layout(**base_layout(
        hovermode="x unified", hoversubplots="axis", hoverdistance=60, barmode="overlay", bargap=0.3,
        margin=dict(l=4, r=12, t=22, b=42), annotations=annotations,
        xaxis=dict(
            anchor="y3", showgrid=False, tickfont=axis_text, tickmode="array", tickvals=ticks,
            ticktext=[f"{t.MONTH_TH[m.month - 1]} {m.year}" for m in ticks], hoverformat="สัปดาห์เริ่ม %d/%m/%Y", fixedrange=True,
        ),
        yaxis=dict(domain=[0.72, 1], gridcolor=t.HAIRLINE, zeroline=False, tickfont=axis_text, rangemode="tozero", fixedrange=True, nticks=4),
        yaxis2=dict(domain=[0.38, 0.65], gridcolor=t.HAIRLINE, zeroline=False, tickfont=axis_text, fixedrange=True, nticks=4, tickformat=","),
        yaxis3=dict(domain=[0.04, 0.305], gridcolor=t.HAIRLINE, zeroline=False, tickfont=axis_text, rangemode="tozero", fixedrange=True, nticks=4),
    ))
    blank = ~frame["acsc_reported"] | (frame["excluded_from_stats_by_default"] & (not include_suspect))
    gaps = frame.loc[blank & frame["in_acsc_window"], "week_start"]
    half_week = pd.Timedelta(days=3.5)
    for week in gaps:
        figure.add_vrect(x0=week - half_week, x1=week + half_week, fillcolor=t.DIMMED, opacity=0.55, line_width=0, layer="below")
    if selected_week:
        week = pd.Timestamp(selected_week)
        _mark_band(figure, week - half_week, week + half_week)
    return figure


def scatter(
    frame: pd.DataFrame, y_column: str, y_scale: float, y_title: str, y_hover: str, line, selected_week: str | None,
) -> go.Figure:
    data = frame[frame[y_column].notna()]
    if data.empty:
        return empty_figure("ไม่มีสัปดาห์ที่มีข้อมูลครบทั้งสองตัวแปร")
    keys = data["week_start"].dt.strftime("%Y-%m-%d").tolist()
    y_values = data[y_column].astype(float) / y_scale
    rounded = data["loss_precision"].eq("rounded") if y_column == "loss_used" else pd.Series(False, index=data.index)
    colors = [t.PINK if key == selected_week else t.BLUE for key in keys]
    sizes = [14 if key == selected_week else 10 for key in keys]
    symbols = ["circle-open" if flag else "circle" for flag in rounded]
    figure = go.Figure(go.Scatter(
        x=data["false_count"], y=y_values, mode="markers", customdata=keys,
        text=[t.th_week(w) for w in data["week_start"]],
        marker=dict(size=sizes, color=colors, symbol=symbols, opacity=0.8, line=dict(color=t.BLUE, width=1.5)),
        hovertemplate=f"<b>%{{text}}</b><br>ข่าวเท็จ %{{x:,}} รายการ<br>{y_hover}<extra></extra>",
    ))
    if line:
        figure.add_scatter(x=line[0], y=[v / y_scale for v in line[1]], mode="lines", line=dict(color=t.INK, width=1.5), hoverinfo="skip")
    figure.update_layout(**base_layout(
        hovermode="closest", hoverdistance=24, margin=dict(l=4, r=12, t=10, b=44),
        xaxis=dict(title=dict(text="ข่าวเท็จด้านการเงิน (รายการต่อสัปดาห์)", font=dict(color=t.INK_MUTED, size=12)), gridcolor=t.HAIRLINE, zeroline=False, tickfont=dict(color=t.INK_MUTED, size=12), fixedrange=True, rangemode="tozero"),
        yaxis=dict(title=dict(text=y_title, font=dict(color=t.INK_MUTED, size=12)), gridcolor=t.HAIRLINE, zeroline=False, tickfont=dict(color=t.INK_MUTED, size=12), fixedrange=True),
    ))
    return figure
