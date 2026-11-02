"""Checks the pipeline must pass before its output can be used."""
from __future__ import annotations

import pandas as pd

from src.config import FALSE_VERDICT_GROUPS, SUSPECT_WEEK
from src.data_cleaning.common import QualityLog


def run(incidents: pd.DataFrame, items: pd.DataFrame, acsc: pd.DataFrame, final: pd.DataFrame, log: QualityLog) -> list[dict]:
    checks = [
        ("Incident ID ไม่ซ้ำ", incidents["incident_id"].is_unique),
        ("post_id ไม่ซ้ำ", items["post_id"].is_unique),
        ("วันที่เหตุการณ์ AI แปลงได้ทุกแถว", incidents["date"].notna().all()),
        ("วันที่โพสต์ AFNC แปลงได้ทุกแถว", items["date"].notna().all()),
        ("week_start ของ AFNC เป็นวันอาทิตย์ทุกแถว", (items["week_start"].dt.dayofweek == 6).all()),
        ("week_start ของ ACSC เป็นวันอาทิตย์หลังจัดแนว", (acsc["week_start"].dt.dayofweek == 6).all()),
        ("week_start ของ panel ไม่ซ้ำ", final["week_start"].is_unique),
        ("ACSC ทุกแถวจับคู่กับ panel ได้", int(final["acsc_reported"].sum()) == len(acsc)),
        ("สัปดาห์ที่ไม่รายงานไม่มีค่าคดี", final.loc[~final["acsc_reported"], "cases"].isna().all()),
        ("สัปดาห์ที่ไม่รายงานไม่มีค่าความเสียหาย", final.loc[~final["acsc_reported"], "loss_baht"].isna().all()),
        ("ไม่มีจำนวนคดีหรือความเสียหายติดลบ", bool((acsc["cases"] >= 0).all() and (acsc["loss_baht"] >= 0).all())),
        ("ไม่มีการแปลงค่าว่างเป็นศูนย์ในผู้บาดเจ็บ", int(incidents["injuries"].isna().sum()) > 0),
        ("คงสัปดาห์น่าสงสัยไว้พร้อมธง", bool(final.loc[final["week_start"] == pd.Timestamp(SUSPECT_WEEK), "excluded_from_stats_by_default"].all())),
        ("ข่าวการเงินหมวดหลักเป็นส่วนย่อยของขอบเขตขยาย", items.loc[items["is_finance_core"], "is_finance_extended"].all()),
        ("นับข่าวเท็จหมวดหลักตรงกับผลรวมรายสัปดาห์", int(final["afnc_false_finance_core"].sum()) == int((items["is_finance_core"] & items["verdict_group"].isin(FALSE_VERDICT_GROUPS)).sum())),
    ]
    results = [{"check": name, "passed": bool(passed)} for name, passed in checks]
    log.fact("validation", "results", results)
    failed = [r["check"] for r in results if not r["passed"]]
    if failed:
        raise ValueError(f"Validation failed: {failed}")
    return results
