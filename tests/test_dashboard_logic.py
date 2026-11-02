"""Interaction rules and figure builders, tested without a browser."""
from __future__ import annotations

import pandas as pd
import pytest

from src.analytics import ai_risk_analysis as ai
from src.analytics import financial_news_analysis as news
from src.analytics import scam_correlation_analysis as rel
from src.dashboard import figures as fig
from src.dashboard import narrative as n
from src.dashboard import state as s
from src.dashboard.app import create_app, defaults_for
from src.dashboard.callbacks import BINDINGS, CLICK_GRAPHS
from src.dashboard.data_store import DataNotReady


@pytest.fixture
def state():
    return s.default_state("2019-01-05", "2026-10-31", "2025-11-09", "2026-10-31")


def click(key):
    return {"points": [{"customdata": key}]}


def test_toggle_adds_then_removes():
    assert s.toggle([], "a") == ["a"]
    assert s.toggle(["a"], "a") == []
    assert s.toggle(["a"], "b") == ["a", "b"]


def test_click_key_reads_custom_data_and_treemap_ids():
    assert s.click_key(click("x")) == "x"
    assert s.click_key({"points": [{"customdata": ["x", 1]}]}) == "x"
    assert s.click_key({"points": [{"id": "A/B"}]}) == "A/B"
    assert s.click_key(None) is None
    assert s.click_key({"points": []}) is None


@pytest.mark.parametrize("source,field,key", [
    ("ai-top-domains", "ai_domains", "Misinformation"),
    ("ai-region-chart", "ai_regions", "Asia"),
    ("ai-harm-chart", "ai_harm", "yes"),
    ("news-verdict-chart", "news_verdicts", "Fake"),
])
def test_second_click_clears_list_filters(state, source, field, key):
    once = s.apply_click(state, source, key)
    assert once[field] == [key]
    assert s.apply_click(once, source, key)[field] == []


@pytest.mark.parametrize("source,field,key", [
    ("news-trend", "news_month", "2023-05"),
    ("news-topic-chart", "news_topic", "loan"),
    ("news-top-chart", "news_post", 123),
    ("rel-trend", "rel_week", "2026-01-04"),
    ("rel-scatter-cases", "rel_week", "2026-01-04"),
    ("rel-scatter-loss", "rel_week", "2026-01-04"),
])
def test_second_click_clears_single_filters(state, source, field, key):
    once = s.apply_click(state, source, key)
    assert once[field] == key
    assert s.apply_click(once, source, key)[field] is None


def test_clicks_do_not_change_the_previous_state(state):
    s.apply_click(state, "ai-top-domains", "Misinformation")
    assert state["ai_domains"] == []


def test_year_click_sets_the_shared_year_and_toggles_off(state):
    once = s.apply_click(state, "ai-trend", "year:2024")
    assert once["years"] == [2024, 2024]
    assert s.apply_click(once, "ai-trend", "year:2024")["years"] == [s.YEAR_SLIDER_MIN, s.YEAR_SLIDER_MAX]


def test_month_click_stays_inside_the_tab(state):
    once = s.apply_click(state, "ai-trend", "month:2024-03")
    assert once["ai_month"] == "2024-03"
    assert once["years"] == state["years"]


def test_treemap_subdomain_click_selects_its_parent_and_undoes_cleanly(state):
    once = s.apply_click(state, "ai-treemap", "Domain/Sub")
    assert (once["ai_domains"], once["ai_subdomain"]) == (["Domain"], "Sub")
    twice = s.apply_click(once, "ai-treemap", "Domain/Sub")
    assert (twice["ai_domains"], twice["ai_subdomain"]) == ([], None)


def test_treemap_domain_click_toggles_the_domain(state):
    once = s.apply_click(state, "ai-treemap", "Domain")
    assert once["ai_domains"] == ["Domain"]
    assert s.apply_click(once, "ai-treemap", "Domain")["ai_domains"] == []


def test_category_click_switches_scope_and_clears_finance_only_filters(state):
    state["news_topic"] = "loan"
    once = s.apply_click(state, "news-category-chart", "ผลิตภัณฑ์สุขภาพ")
    assert once["news_scope"] == "ผลิตภัณฑ์สุขภาพ"
    assert once["news_topic"] is None
    assert s.apply_click(once, "news-category-chart", "ผลิตภัณฑ์สุขภาพ")["news_scope"] == news.SCOPE_CORE


def test_finance_category_click_maps_to_core_scope(state):
    assert s.apply_click(state, "news-category-chart", "การเงิน-หุ้น")["news_scope"] == news.SCOPE_CORE


def test_slider_ends_mean_no_limit():
    f = s.rel_filters([s.YEAR_SLIDER_MIN, s.YEAR_SLIDER_MAX], None, None, "core", None, s.CASES_SLIDER, s.LOSS_SLIDER, [])
    assert (f.year_from, f.year_to, f.cases_min, f.cases_max, f.loss_min, f.loss_max) == (None, None, None, None, None, None)


def test_loss_slider_is_converted_to_baht():
    f = s.rel_filters([s.YEAR_SLIDER_MIN, s.YEAR_SLIDER_MAX], None, None, "core", None, s.CASES_SLIDER, [200, 500], [])
    assert (f.loss_min, f.loss_max) == (2e8, 5e8)


def test_default_state_shows_every_incident(store, state):
    filtered = ai.filter_incidents(store.incidents, s.ai_filters(state["years"], [], [], [], None, None))
    assert ai.count_incidents(filtered) == 1749


def test_shared_year_reaches_all_three_tabs(store):
    years = [2024, 2024]
    assert (ai.filter_incidents(store.incidents, s.ai_filters(years, [], [], [], None, None))["year"] == 2024).all()
    f = s.news_filters(years, news.SCOPE_ALL, [], None, None, "", None, None, None)
    assert (news.filter_news(store.news, f)["year"] == 2024).all()
    g = s.rel_filters(years, None, None, "core", None, s.CASES_SLIDER, s.LOSS_SLIDER, [])
    frame = rel.apply_filters(rel.weekly_frame(store.panel, store.news), g)
    assert (frame["week_start"].dt.year == 2024).all()
    assert rel.pearson(frame["false_count"], frame["cases_used"]).r is None


def test_kpi_and_table_filters_agree_on_real_data(store):
    f = s.ai_filters([2023, 2025], [], ["Misinformation"], [], None, None)
    filtered = ai.filter_incidents(store.incidents, f)
    expected = store.incidents[store.incidents["year"].between(2023, 2025) & (store.incidents["risk_domain"] == "Misinformation")]
    assert ai.count_incidents(filtered) == len(expected)


def test_a_chart_ignores_its_own_filter(store):
    f = s.ai_filters([s.YEAR_SLIDER_MIN, s.YEAR_SLIDER_MAX], [], ["Misinformation"], [], None, None)
    without = ai.filter_incidents(store.incidents, f, frozenset({"domains"}))
    assert ai.count_incidents(without) == 1749


def test_missing_filter_option_selects_blank_rows(small_incidents):
    filtered = ai.filter_incidents(small_incidents, ai.AiFilters(regions=(ai.MISSING,)))
    assert filtered["location_region"].isna().all() and len(filtered) == 4


def test_keyword_search_is_literal(small_news):
    f = news.NewsFilters(scope=news.SCOPE_ALL, keyword="(")
    assert news.filter_news(small_news, f).empty


@pytest.mark.parametrize("figure", [
    fig.top_domains(pd.DataFrame(columns=["risk_domain_th", "incidents", "risk_domain", "share_pct"]), []),
    fig.risk_treemap(pd.DataFrame(), [], None),
    fig.category_bars(pd.DataFrame(), None),
    fig.verdict_donut(pd.DataFrame(), [], "N/A", ""),
    fig.news_trend(pd.DataFrame(), None, True),
    fig.topic_bars(pd.DataFrame(), None),
    fig.top_viewed_bars(pd.DataFrame(), None),
])
def test_empty_data_gives_a_polite_empty_figure(figure):
    assert fig.EMPTY_TITLE in figure.layout.annotations[0].text


def test_no_match_keeps_every_builder_working(store):
    f = news.NewsFilters(scope=news.SCOPE_ALL, keyword="ไม่มีคำนี้แน่นอน")
    nothing = news.filter_news(store.news, f)
    assert nothing.empty
    assert news.news_kpis(nothing)["fake_pct"] is None
    assert fig.EMPTY_TITLE in fig.category_bars(news.false_by_category(nothing), None).layout.annotations[0].text
    assert fig.EMPTY_TITLE in fig.news_trend(news.monthly_trend(nothing), None, False).layout.annotations[0].text


def test_true_only_verdict_empties_the_false_news_chart(store):
    f = news.NewsFilters(scope=news.SCOPE_ALL, verdicts=("True",))
    table = news.false_by_category(news.filter_news(store.news, f))
    assert fig.EMPTY_TITLE in fig.category_bars(table, None).layout.annotations[0].text


def test_weekly_chart_uses_one_axis_per_panel(store):
    window = store.panel[store.panel["in_acsc_window"]]
    frame = rel.apply_filters(rel.weekly_frame(window, store.news), rel.RelFilters())
    figure = fig.weekly_comparison(frame, None, False)
    assert {trace.yaxis for trace in figure.data} == {"y", "y2", "y3"}
    assert not any(getattr(axis, "overlaying", None) for axis in (figure.layout.yaxis2, figure.layout.yaxis3))


def test_weekly_chart_leaves_the_suspect_week_out_by_default(store):
    window = store.panel[store.panel["in_acsc_window"]]
    frame = rel.apply_filters(rel.weekly_frame(window, store.news), rel.RelFilters())
    line = fig.weekly_comparison(frame, None, False).data[1]
    assert max(v for v in line.y if pd.notna(v)) < 8000


def test_insight_names_the_selection_not_a_fake_100_percent(store):
    f = s.ai_filters([s.YEAR_SLIDER_MIN, s.YEAR_SLIDER_MAX], [], ["Misinformation"], [], None, None)
    filtered = ai.filter_incidents(store.incidents, f)
    without = ai.filter_incidents(store.incidents, f, frozenset({"domains"}))
    growth = ai.annual_growth(filtered, f, store.ai_end)
    text = "".join(str(getattr(p, "children", p)) for p in n.ai_insight(filtered, without, ["Misinformation"], growth))
    assert "100.0%" not in text and "13.1%" in text


def test_every_click_graph_and_binding_exists_in_the_layout(store):
    app = create_app()
    text = str(app.layout)
    for graph in CLICK_GRAPHS:
        assert graph in text
    for component, _ in BINDINGS.values():
        assert component in text


def test_app_serves_layout_and_callbacks():
    client = create_app().server.test_client()
    assert client.get("/").status_code == 200
    assert client.get("/_dash-layout").status_code == 200
    assert client.get("/_dash-dependencies").status_code == 200


def test_defaults_cover_the_data(store):
    defaults = defaults_for(store)
    assert defaults["news_start"] == "2019-01-05"
    assert defaults["news_end"] == "2026-10-31"
    assert defaults["rel_start"] == "2025-11-09"


def test_missing_processed_file_gives_a_helpful_error(tmp_path):
    from src.dashboard.data_store import _read
    with pytest.raises(DataNotReady, match="run_pipeline"):
        _read(tmp_path / "nope.csv")
