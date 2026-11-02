"""Join AFNC counts and ACSC figures on one Sunday-to-Saturday week spine.

The final panel is rebuilt from afnc_items and acsc_weekly. The supplied
weekly_panel sheet is used only as a cross-check, per BRD section 7.
"""
from __future__ import annotations

import pandas as pd

from src.config import (
    FALSE_VERDICT_GROUPS,
    PANEL_RECONCILIATION,
    WEEKLY_PANEL_FINAL,
)
from src.data_cleaning.common import QualityLog, write_csv

STATUS_REPORTED = "reported"
STATUS_BEFORE_ACSC = "before_acsc_briefings"
STATUS_NO_FIGURE = "no_figure_found"
STATUS_NOT_ANNOUNCED = "not_yet_announced"


def weekly_false_counts(items: pd.DataFrame, mask: pd.Series) -> pd.Series:
    false_items = items[mask & items["verdict_group"].isin(FALSE_VERDICT_GROUPS)]
    return false_items.groupby("week_start").size()


def reporting_status(row: pd.Series, first_week: pd.Timestamp, last_week: pd.Timestamp) -> str:
    if row["acsc_reported"]:
        return STATUS_REPORTED
    if row["week_start"] < first_week:
        return STATUS_BEFORE_ACSC
    if row["week_start"] > last_week:
        return STATUS_NOT_ANNOUNCED
    return STATUS_NO_FIGURE


def reconcile(final: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
    """Compare the rebuilt columns with the supplied panel, week by week."""
    merged = final.merge(panel, on="week_start", how="outer", suffixes=("", "_panel"), indicator=True)
    checks = {
        "afnc_false_finance_core": "afnc_false_finance",
        "cases": "acsc_cases",
        "loss_baht": "acsc_loss_baht",
    }
    rows = []
    for ours, theirs in checks.items():
        a = pd.to_numeric(merged[ours], errors="coerce").astype(float)
        b = pd.to_numeric(merged[theirs], errors="coerce").astype(float)
        differs = ~((a == b) | (a.isna() & b.isna()))
        for week in merged.loc[differs, "week_start"]:
            rows.append({"week_start": week, "column": ours, "panel_column": theirs})
    columns = ["week_start", "column", "panel_column"]
    return pd.DataFrame(rows, columns=columns), merged["_merge"].value_counts().to_dict()


def build(items: pd.DataFrame, acsc: pd.DataFrame, panel: pd.DataFrame, log: QualityLog) -> pd.DataFrame:
    spine = pd.DataFrame({
        "week_start": pd.date_range(panel["week_start"].min(), panel["week_start"].max(), freq="7D")
    })
    log.fact("integration", "spine_weeks", len(spine))
    log.fact("integration", "panel_weeks", len(panel))
    spine["week_end"] = spine["week_start"] + pd.Timedelta(days=6)

    verdict_weeks = items[items["verdict_group"].isin(("Fake", "Distorted", "True"))].groupby("week_start").size()
    spine["afnc_verdicts"] = spine["week_start"].map(verdict_weeks).fillna(0).astype(int)
    core = weekly_false_counts(items, items["is_finance_core"])
    extended = weekly_false_counts(items, items["is_finance_extended"])
    # AFNC published in the panel's weeks, so no post here is a true zero.
    spine["afnc_false_finance_core"] = spine["week_start"].map(core).fillna(0).astype(int)
    spine["afnc_false_finance_extended"] = spine["week_start"].map(extended).fillna(0).astype(int)

    acsc_columns = [
        "week_start", "week_start_raw", "days", "cases", "loss_baht", "loss_precision", "loss_per_case_baht",
        "top_type_th", "highest_loss_type_th", "flag", "quality_status",
        "excluded_from_stats_by_default", "source_url",
    ]
    before = len(spine)
    final = spine.merge(acsc[acsc_columns], on="week_start", how="left", validate="one_to_one", indicator=True)
    log.step("integration", "left join ACSC onto week spine", before, len(final), "Rows must not grow; ACSC has one row per week")
    log.fact("integration", "acsc_weeks_matched", int((final["_merge"] == "both").sum()))
    log.fact("integration", "acsc_rows", len(acsc))
    log.fact("integration", "acsc_rows_unmatched", len(acsc) - int((final["_merge"] == "both").sum()))
    final["acsc_reported"] = final["_merge"] == "both"
    final = final.drop(columns="_merge")

    first, last = acsc["week_start"].min(), acsc["week_start"].max()
    final["reporting_status"] = final.apply(reporting_status, axis=1, args=(first, last))
    final["in_acsc_window"] = (final["week_start"] >= first) & (final["week_start"] <= last + pd.Timedelta(days=7))
    final["excluded_from_stats_by_default"] = final["excluded_from_stats_by_default"].astype("boolean").fillna(False).astype(bool)

    status_counts = final["reporting_status"].value_counts().to_dict()
    log.fact("integration", "reporting_status_counts", status_counts)
    gaps = final.loc[final["reporting_status"].isin([STATUS_NO_FIGURE, STATUS_NOT_ANNOUNCED]), "week_start"]
    log.fact("integration", "weeks_without_figure_in_window", [w.date().isoformat() for w in gaps])

    differences, join_counts = reconcile(final, panel)
    write_csv(differences, PANEL_RECONCILIATION)
    log.fact("integration", "panel_cell_differences", len(differences))
    log.fact("integration", "panel_join_counts", {str(k): int(v) for k, v in join_counts.items()})

    naive = panel.merge(acsc.assign(week_start=acsc["week_start_raw"]), on="week_start", how="inner")
    log.fact("integration", "matched_if_raw_week_start_were_used", len(naive))

    # The share of the finance count that sits outside the core category shows the
    # relabelling: AFNC verdicts in this category start in 2026.
    crime = items[(items["category_th"] == "อาชญากรรมออนไลน์") & (items["verdict_group"] != "Unverified")]
    log.fact("integration", "online_crime_verdict_first_month", crime["month"].min())
    log.fact("integration", "online_crime_verdicts_by_month", crime.groupby("month").size().to_dict())
    finance = items[items["is_finance_core"]]
    log.fact("integration", "core_finance_by_month_2025_11_on", finance[finance["month"] >= "2025-11"].groupby("month").size().to_dict())

    write_csv(final, WEEKLY_PANEL_FINAL)
    return final


def run(items: pd.DataFrame, acsc: pd.DataFrame, panel: pd.DataFrame, log: QualityLog) -> pd.DataFrame:
    return build(items, acsc, panel, log)
