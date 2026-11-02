"""Weekly join and correlation on real data, per handoff section 15.2."""
from __future__ import annotations

import pandas as pd
import pytest

from src.analytics import scam_correlation_analysis as rel
from src.config import PANEL_RECONCILIATION, THAI_WORKBOOK
from src.data_integration.build_weekly_panel import STATUS_NO_FIGURE, STATUS_NOT_ANNOUNCED


def test_panel_has_one_row_per_week(store):
    weeks = store.panel["week_start"]
    assert weeks.is_unique and len(weeks) == 409
    assert (weeks.dt.dayofweek == 6).all()
    assert (weeks.diff().dropna() == pd.Timedelta(days=7)).all()


def test_join_keeps_every_acsc_week(store):
    facts = store.quality["facts"]["integration"]
    assert facts["acsc_weeks_matched"] == 48
    assert facts["acsc_rows_unmatched"] == 0


def test_raw_week_start_would_have_lost_a_week(store):
    assert store.quality["facts"]["integration"]["matched_if_raw_week_start_were_used"] == 47


def test_rebuilt_panel_matches_the_supplied_sheet(store):
    assert store.quality["facts"]["integration"]["panel_cell_differences"] == 0
    assert len(pd.read_csv(PANEL_RECONCILIATION, encoding="utf-8-sig")) == 0


def test_core_count_reproduces_the_workbook_column(store):
    supplied = pd.read_excel(THAI_WORKBOOK, sheet_name="weekly_panel", usecols=["week_start", "afnc_false_finance"])
    merged = store.panel.merge(supplied, on="week_start")
    assert (merged["afnc_false_finance_core"] == merged["afnc_false_finance"]).all()
    assert merged["afnc_false_finance_core"].sum() == 2396


def test_unreported_weeks_stay_blank_not_zero(store):
    panel = store.panel
    unreported = panel[~panel["acsc_reported"]]
    assert unreported["cases"].isna().all() and unreported["loss_baht"].isna().all()
    assert (panel["cases"] == 0).sum() == 0


def test_gaps_inside_the_window_are_named(store):
    statuses = store.panel.set_index("week_start")["reporting_status"]
    assert statuses[pd.Timestamp("2026-06-14")] == STATUS_NO_FIGURE
    assert statuses[pd.Timestamp("2026-07-26")] == STATUS_NO_FIGURE
    assert statuses[pd.Timestamp("2026-10-25")] == STATUS_NOT_ANNOUNCED


def test_filtered_weeks_never_turn_blank_into_zero(store):
    frame = rel.apply_filters(rel.weekly_frame(store.panel, store.news), rel.RelFilters())
    blank = frame[~frame["acsc_reported"]]
    assert blank["cases_used"].isna().all() and blank["loss_used"].isna().all()


def default_frame(store) -> pd.DataFrame:
    window = store.panel[store.panel["in_acsc_window"]]
    return rel.apply_filters(rel.weekly_frame(window, store.news), rel.RelFilters())


def test_default_correlation_matches_numpy_on_the_same_weeks(store):
    frame = default_frame(store)
    used = frame[frame["cases_used"].notna()]
    expected = used["false_count"].astype(float).corr(used["cases_used"].astype(float))
    result = rel.pearson(frame["false_count"], frame["cases_used"])
    assert result.r == pytest.approx(expected)
    assert result.r == pytest.approx(0.538, abs=0.001)
    assert result.n == 47


def test_loss_correlation_and_sample_size(store):
    frame = default_frame(store)
    result = rel.pearson(frame["false_count"], frame["loss_used"])
    assert result.r == pytest.approx(0.572, abs=0.001)
    assert result.n == 47


def test_suspect_week_changes_the_result_as_documented(store):
    window = store.panel[store.panel["in_acsc_window"]]
    frame = rel.apply_filters(rel.weekly_frame(window, store.news), rel.RelFilters(include_suspect=True))
    result = rel.pearson(frame["false_count"], frame["cases_used"])
    assert result.n == 48
    assert result.r == pytest.approx(-0.090, abs=0.001)


def test_exact_only_applies_to_loss_not_cases(store):
    window = store.panel[store.panel["in_acsc_window"]]
    frame = rel.apply_filters(rel.weekly_frame(window, store.news), rel.RelFilters(exact_loss_only=True))
    assert rel.pearson(frame["false_count"], frame["cases_used"]).n == 47
    assert rel.pearson(frame["false_count"], frame["loss_used"]).n == 37


def test_changes_only_join_adjacent_weeks(small_weeks):
    frame = rel.apply_filters(small_weeks, rel.RelFilters())
    changes = rel.consecutive_changes(frame)
    assert changes["cases_used"].notna().sum() == 3
    assert changes["cases_used"].dropna().tolist() == [10, 10, 10]


def test_case_range_removes_blank_weeks(small_weeks):
    frame = rel.apply_filters(small_weeks, rel.RelFilters(cases_min=15, cases_max=35))
    assert frame["week_start"].dt.strftime("%m-%d").tolist() == ["01-11", "01-18"]


def test_sensitivity_table_covers_every_reading(store):
    table = rel.sensitivity_table(store.panel, store.news).set_index("key")
    assert list(table.index) == ["brd", "with_suspect", "exact", "extended", "before_relabel", "changes"]
    assert table.loc["brd", "n_cases"] == 47
    assert table.loc["before_relabel", "n_cases"] == 12
    assert table.loc["changes", "r_cases"] == pytest.approx(-0.182, abs=0.001)
