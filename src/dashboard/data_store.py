"""Load the processed datasets once and expose them to the callbacks."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import pandas as pd

from src.config import (
    ACSC_WEEKLY_CLEAN,
    AFNC_ITEMS_CLEAN,
    AI_INCIDENTS_CLEAN,
    QUALITY_METADATA,
    WEEKLY_PANEL_FINAL,
)
from src.data_cleaning.common import load_quality_metadata

REQUIRED = {
    AI_INCIDENTS_CLEAN: ["incident_id", "date", "year", "month", "risk_domain", "location_region", "harm_domain", "injuries", "lives_lost"],
    AFNC_ITEMS_CLEAN: ["post_id", "date", "week_start", "month", "verdict_group", "category_th", "title_clean", "is_finance_core", "is_finance_extended", "view_count"],
    WEEKLY_PANEL_FINAL: ["week_start", "afnc_false_finance_core", "acsc_reported", "cases", "loss_baht", "reporting_status", "in_acsc_window"],
    ACSC_WEEKLY_CLEAN: ["week_start", "cases", "loss_baht", "quality_status"],
}
RUN_HINT = "รันคำสั่ง python run_pipeline.py เพื่อสร้างข้อมูลใหม่จากโฟลเดอร์ datasets/"


class DataNotReady(RuntimeError):
    """A processed file or required column is missing; shown on an error page (FR-13)."""


@dataclass(frozen=True)
class DataStore:
    incidents: pd.DataFrame
    news: pd.DataFrame
    panel: pd.DataFrame
    acsc: pd.DataFrame
    quality: dict

    @property
    def ai_end(self) -> pd.Timestamp:
        return self.incidents["date"].max()


def _read(path, **kwargs) -> pd.DataFrame:
    if not path.exists():
        raise DataNotReady(f"ไม่พบไฟล์ {path.name} {RUN_HINT}")
    df = pd.read_csv(path, encoding="utf-8-sig", low_memory=False, **kwargs)
    missing = [c for c in REQUIRED[path] if c not in df.columns]
    if missing:
        raise DataNotReady(f"ไฟล์ {path.name} ไม่มีคอลัมน์ {', '.join(missing)} {RUN_HINT}")
    return df


@lru_cache(maxsize=1)
def load_store() -> DataStore:
    incidents = _read(AI_INCIDENTS_CLEAN, parse_dates=["date"])
    incidents["injuries"] = incidents["injuries"].astype("Int64")
    incidents["lives_lost"] = incidents["lives_lost"].astype("Int64")

    news = _read(AFNC_ITEMS_CLEAN, parse_dates=["date", "week_start", "published_bkk"])
    news["search_text"] = (news["title"].fillna("") + " " + news["topic_tags"].fillna("")).str.lower()

    panel = _read(WEEKLY_PANEL_FINAL, parse_dates=["week_start", "week_end", "week_start_raw"])
    acsc = _read(ACSC_WEEKLY_CLEAN, parse_dates=["week_start", "week_start_raw", "week_end"])

    if not QUALITY_METADATA.exists():
        raise DataNotReady(f"ไม่พบไฟล์ {QUALITY_METADATA.name} {RUN_HINT}")
    return DataStore(incidents, news, panel, acsc, load_quality_metadata())
