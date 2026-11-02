"""KPI formulas on tiny hand-made frames, per handoff section 15.3.

The expected values are worked out by hand, so these tests catch a wrong formula
rather than just repeating what the code does.
"""
from __future__ import annotations

import pandas as pd
import pytest

from src.analytics import ai_risk_analysis as ai
from src.analytics import financial_news_analysis as news
from src.analytics import scam_correlation_analysis as rel


def test_incident_count_uses_unique_ids(small_incidents):
    doubled = pd.concat([small_incidents, small_incidents])
    assert ai.count_incidents(doubled) == 6


def test_casualty_count_needs_a_positive_value(small_incidents):
    result = ai.casualty_summary(small_incidents)
    assert result["positive"] == 2
    assert result["coded"] == 3
    assert result["total"] == 6


def test_blank_casualty_values_are_not_counted_as_coded(small_incidents):
    blank = small_incidents[small_incidents["injuries"].isna()]
    assert ai.casualty_summary(blank) == {"positive": 0, "coded": 0, "total": 3, "coded_pct": 0.0}


def test_growth_formula():
    assert ai.growth_pct(460, 310) == pytest.approx(48.387, abs=0.001)
    assert ai.growth_pct(5, 10) == -50


def test_growth_is_na_when_previous_year_is_zero():
    assert ai.growth_pct(5, 0) is None


def test_default_growth_skips_the_partial_year(small_incidents):
    end = pd.Timestamp("2026-10-07")
    result = ai.annual_growth(small_incidents, ai.AiFilters(), end)
    assert (result["year"], result["previous_year"]) == (2025, 2024)
    assert (result["current"], result["previous"]) == (3, 2)
    assert result["pct"] == 50
    assert result["same_period"] is False


def test_partial_year_alone_compares_the_same_period(small_incidents):
    end = pd.Timestamp("2026-03-01")
    result = ai.annual_growth(small_incidents, ai.AiFilters(year_from=2026, year_to=2026), end)
    assert result["same_period"] is True
    assert (result["current"], result["previous"]) == (1, 1)


def test_risk_domain_count_ignores_blanks(small_incidents):
    assert ai.count_risk_domains(small_incidents) == 2


def test_top_domains_keeps_a_selected_domain_outside_the_cut(small_incidents):
    assert ai.top_risk_domains(small_incidents, 1)["risk_domain"].tolist() == ["A"]
    assert ai.top_risk_domains(small_incidents, 1, ("B",))["risk_domain"].tolist() == ["A", "B"]


def test_treemap_shows_unclassified_separately(small_incidents):
    tree = ai.risk_tree(small_incidents)
    assert tree.loc[tree["id"] == ai.MISSING, "incidents"].item() == 1
    roots = tree[tree["parent"] == ""]
    assert roots["incidents"].sum() == 6


def test_fake_percentage_excludes_posts_without_a_verdict(small_news):
    kpi = news.news_kpis(small_news)
    assert kpi["with_verdict"] == 5
    assert kpi["fake_pct"] == pytest.approx(60.0)


def test_fake_percentage_is_na_with_no_verdicts(small_news):
    assert news.news_kpis(small_news[small_news["verdict_group"] == "Unverified"])["fake_pct"] is None


def test_average_views_skips_invalid_rows(small_news):
    kpi = news.news_kpis(small_news)
    assert kpi["views_n"] == 5
    assert kpi["views_mean"] == pytest.approx((100 + 300 + 400 + 500 + 600) / 5)


def test_finance_scope_counts(small_news):
    core = news.filter_news(small_news, news.NewsFilters(scope=news.SCOPE_CORE))
    extended = news.filter_news(small_news, news.NewsFilters(scope=news.SCOPE_EXTENDED))
    assert len(core) == 4
    assert len(extended) == 5


def test_false_by_category_stacks_fake_and_distorted(small_news):
    table = news.false_by_category(small_news).set_index("category_th")
    assert table.loc["การเงิน-หุ้น", "total"] == 3
    assert table.loc["การเงิน-หุ้น", "false_share_pct"] == pytest.approx(75.0)
    assert "คลังความรู้" not in table.index


def test_average_loss_per_case_is_total_over_total(small_weeks):
    frame = rel.apply_filters(small_weeks, rel.RelFilters())
    kpi = rel.relationship_kpis(frame)
    assert kpi["loss_per_case"] == pytest.approx((100 + 200 + 300 + 500) / (10 + 20 + 30 + 40))


def test_average_loss_per_case_skips_zero_case_weeks():
    weeks = pd.DataFrame({
        "week_start": pd.to_datetime(["2026-01-04", "2026-01-11"]), "false_count": [1, 2], "acsc_reported": [True, True],
        "cases": [0.0, 10.0], "loss_baht": [50.0, 100.0], "loss_precision": ["exact", "exact"],
        "excluded_from_stats_by_default": [False, False],
    })
    assert rel.relationship_kpis(rel.apply_filters(weeks, rel.RelFilters()))["loss_per_case"] == 10


def test_pearson_perfect_line():
    result = rel.pearson(pd.Series([1, 2, 3, 4]), pd.Series([2, 4, 6, 8]))
    assert result.r == pytest.approx(1.0)
    assert result.n == 4
    assert result.direction == "ทิศทางเดียวกัน"


def test_pearson_matches_a_hand_calculation():
    # x = 1,2,3,4,5  y = 2,4,5,4,5  gives r = 6 / sqrt(10 * 6)
    result = rel.pearson(pd.Series([1, 2, 3, 4, 5]), pd.Series([2, 4, 5, 4, 5]))
    assert result.r == pytest.approx(6 / (10 * 6) ** 0.5)


def test_pearson_uses_complete_pairs_only():
    result = rel.pearson(pd.Series([1, 2, 3, None, 5]), pd.Series([2, 4, None, 8, 10]))
    assert result.n == 3
    assert result.r == pytest.approx(1.0)


def test_pearson_na_with_too_few_points():
    result = rel.pearson(pd.Series([1, 2]), pd.Series([3, 4]))
    assert result.r is None and result.status == "insufficient" and result.n == 2


def test_pearson_na_without_variance():
    result = rel.pearson(pd.Series([3, 3, 3, 3]), pd.Series([1, 2, 3, 4]))
    assert result.r is None and result.status == "no_variance"


def test_correlation_strength_labels():
    assert rel.Correlation(0.05, 40, "ok", "").strength == "แทบไม่สัมพันธ์"
    assert rel.Correlation(-0.25, 40, "ok", "").strength == "อ่อน"
    assert rel.Correlation(0.4, 40, "ok", "").strength == "ปานกลาง"
    assert rel.Correlation(0.54, 40, "ok", "").strength == "ค่อนข้างแรง"
    assert rel.Correlation(-0.8, 40, "ok", "").strength == "แรง"


def test_trend_line_needs_enough_points():
    assert rel.trend_line(pd.Series([1, 2, 3]), pd.Series([1, 2, 3])) is None
    x = pd.Series(range(12))
    ends, values = rel.trend_line(x, x * 2 + 1)
    assert ends == [0, 11]
    assert values == pytest.approx([1, 23])


def test_monthly_counts_start_at_the_trend_year():
    df = pd.DataFrame({"incident_id": [1, 2, 3], "year": [1983, 2013, 2013], "month": ["1983-09", "2013-01", "2013-03"]})
    months = ai.monthly_counts(df)
    assert months["month"].tolist() == ["2013-01", "2013-02", "2013-03"]
    assert months["incidents"].tolist() == [1, 0, 1]


def test_monthly_counts_fall_back_when_only_old_years_are_selected():
    df = pd.DataFrame({"incident_id": [1], "year": [1983], "month": ["1983-09"]})
    assert ai.monthly_counts(df)["month"].tolist() == ["1983-09"]
