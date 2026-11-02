"""Clean the ACSC weekly briefings and the supplied weekly panel.

ACSC weeks run Sunday to Saturday, but one briefing states an eight-day period
(30 May to 6 Jun 2026) and so starts on a Saturday. Joining on the raw week_start
would drop that row. week_end is a Saturday in every row, so the join key is
week_end minus six days.
"""
from __future__ import annotations

import pandas as pd

from src.config import ACSC_WEEKLY_CLEAN, SUSPECT_WEEK, THAI_WORKBOOK, WEEKLY_PANEL_CLEAN
from src.data_cleaning.common import QualityLog, require_columns, require_file, write_csv

ACSC_REQUIRED = ["week_start", "week_end", "days", "cases", "loss_baht", "loss_precision", "flag", "source_url"]
PANEL_REQUIRED = [
    "week_start", "week_end", "afnc_false_finance", "acsc_reported", "acsc_cases",
    "acsc_loss_baht", "acsc_loss_precision", "acsc_flag",
]

STATUS_OK = "ok"
STATUS_SUSPECT = "suspect"
STATUS_EIGHT_DAYS = "eight_day_period"
STATUS_ROUNDED_COUNT = "rounded_case_count"
STATUS_COMPARISON = "comparison_note"


def quality_status(row: pd.Series) -> str:
    """Translate the source's free-text flag into a value the dashboard can act on."""
    if pd.isna(row["flag"]):
        return STATUS_OK
    if row["week_key"] == pd.Timestamp(SUSPECT_WEEK):
        return STATUS_SUSPECT
    if row["days"] != 7:
        return STATUS_EIGHT_DAYS
    if "5,000" in row["flag"]:
        return STATUS_ROUNDED_COUNT
    return STATUS_COMPARISON


def clean_acsc(log: QualityLog) -> pd.DataFrame:
    require_file(THAI_WORKBOOK)
    raw = pd.read_excel(THAI_WORKBOOK, sheet_name="acsc_weekly")
    require_columns(raw, ACSC_REQUIRED, "thai-disinfo-scam-dataset.xlsx / acsc_weekly")
    log.step("acsc", "read acsc_weekly", len(raw), len(raw), "One row per weekly briefing")

    df = raw.rename(columns={"week_start": "week_start_raw"})
    df["week_start_raw"] = pd.to_datetime(df["week_start_raw"])
    df["week_end"] = pd.to_datetime(df["week_end"])
    log.fact("acsc", "week_end_not_saturday", int((df["week_end"].dt.dayofweek != 5).sum()))
    df["week_key"] = df["week_end"] - pd.Timedelta(days=6)
    moved = df[df["week_key"] != df["week_start_raw"]]
    log.fact("acsc", "weeks_realigned_to_sunday", [
        {"raw": r.week_start_raw.date().isoformat(), "aligned": r.week_key.date().isoformat(), "days": int(r.days)}
        for r in moved.itertuples()
    ])
    log.fact("acsc", "week_key_duplicates", int(df["week_key"].duplicated().sum()))
    if df["week_key"].duplicated().any():
        raise ValueError("ACSC must hold one row per week")

    for column in ("cases", "loss_baht", "loss_per_case_baht"):
        df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int64")
    log.fact("acsc", "negative_cases", int((df["cases"] < 0).sum()))
    log.fact("acsc", "negative_loss", int((df["loss_baht"] < 0).sum()))
    log.fact("acsc", "zero_case_weeks", int((df["cases"] == 0).sum()))
    log.fact("acsc", "missing_cases", int(df["cases"].isna().sum()))
    log.fact("acsc", "missing_loss", int(df["loss_baht"].isna().sum()))

    recomputed = (df["loss_baht"].astype(float) / df["cases"].astype(float)).round()
    log.fact("acsc", "loss_per_case_disagrees_with_recomputed", int((recomputed != df["loss_per_case_baht"].astype(float)).sum()))

    df["quality_status"] = df.apply(quality_status, axis=1)
    df["excluded_from_stats_by_default"] = df["quality_status"] == STATUS_SUSPECT
    log.fact("acsc", "loss_precision_counts", df["loss_precision"].value_counts().to_dict())
    log.fact("acsc", "quality_status_counts", df["quality_status"].value_counts().to_dict())
    log.fact("acsc", "week_min", df["week_key"].min().date().isoformat())
    log.fact("acsc", "week_max", df["week_key"].max().date().isoformat())
    log.fact("acsc", "rows_clean", len(df))
    log.step("acsc", "align weeks and tag quality", len(raw), len(df), "Flagged weeks are kept and tagged, not deleted")

    out = df.rename(columns={"week_key": "week_start"})[[
        "week_start", "week_start_raw", "week_end", "days", "cases", "loss_baht", "loss_precision",
        "loss_per_case_baht", "cases_change_vs_prev_week", "loss_change_vs_prev_week_baht",
        "top_type_th", "top_type_case_share_pct", "highest_loss_type_th", "highest_loss_type_loss_baht",
        "flag", "quality_status", "excluded_from_stats_by_default", "publisher", "article_date",
        "source_url", "notes",
    ]]
    write_csv(out, ACSC_WEEKLY_CLEAN)
    return out


def clean_panel(log: QualityLog) -> pd.DataFrame:
    raw = pd.read_excel(THAI_WORKBOOK, sheet_name="weekly_panel")
    require_columns(raw, PANEL_REQUIRED, "thai-disinfo-scam-dataset.xlsx / weekly_panel")
    df = raw.copy()
    df["week_start"] = pd.to_datetime(df["week_start"])
    df["week_end"] = pd.to_datetime(df["week_end"])
    log.fact("panel", "rows", len(df))
    log.fact("panel", "week_start_duplicates", int(df["week_start"].duplicated().sum()))
    log.fact("panel", "week_start_not_sunday", int((df["week_start"].dt.dayofweek != 6).sum()))
    log.fact("panel", "weeks_not_consecutive", int((df["week_start"].diff().dropna() != pd.Timedelta(days=7)).sum()))
    log.fact("panel", "week_min", df["week_start"].min().date().isoformat())
    log.fact("panel", "week_max", df["week_start"].max().date().isoformat())
    log.fact("panel", "acsc_reported_weeks", int(df["acsc_reported"].sum()))
    log.step("panel", "read weekly_panel", len(raw), len(df), "Types only; values are checked against the sources later")
    write_csv(df, WEEKLY_PANEL_CLEAN)
    return df


def run(log: QualityLog) -> tuple[pd.DataFrame, pd.DataFrame]:
    return clean_acsc(log), clean_panel(log)
