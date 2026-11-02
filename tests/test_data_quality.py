"""Checks on the real processed data, per handoff section 15.1."""
from __future__ import annotations

import pandas as pd

from src.config import AI_INCIDENTS_CLEAN, EXTENDED_SCOPE_REVIEW, FINANCIAL_TOPIC_RULES, RAW_DIR, VERDICT_MAPPING
from src.data_cleaning.clean_fake_news import assign_topic, strip_verdict_prefix


def test_incident_id_is_unique(store):
    assert store.incidents["incident_id"].is_unique
    assert store.incidents["incident_id"].notna().all()


def test_only_the_latest_snapshot_is_counted(store):
    assert store.quality["facts"]["ai"]["source_file"] == "AIID_Excel_Export-20261019.xlsx"
    assert len(store.incidents) == 1749
    assert store.quality["facts"]["ai"]["rows_if_snapshots_were_wrongly_summed"] == 20070


def test_no_incident_ids_vanish_between_snapshots(store):
    assert store.quality["facts"]["ai"]["ids_removed_between_snapshots"] == 0


def test_every_incident_date_parses_and_agrees_with_year(store):
    assert store.incidents["date"].notna().all()
    assert (store.incidents["date"].dt.year == store.incidents["year"]).all()


def test_blank_injuries_stay_blank(store):
    assert store.incidents["injuries"].isna().sum() == 1543
    assert store.incidents["lives_lost"].isna().sum() == 1543


def test_outliers_are_kept(store):
    assert store.incidents["injuries"].max() == 55000


def test_every_risk_label_has_a_thai_name(store):
    labelled = store.incidents["risk_domain"].notna()
    assert store.incidents.loc[labelled, "risk_domain_th"].notna().all()


def test_post_id_is_unique(store):
    assert store.news["post_id"].is_unique
    assert len(store.news) == 17726


def test_week_start_is_sunday_and_matches_the_post_date(store):
    news = store.news
    assert (news["week_start"].dt.dayofweek == 6).all()
    assert ((news["date"] - news["week_start"]).dt.days.between(0, 6)).all()


def test_verdict_mapping_covers_every_row(store):
    groups = set(store.news["verdict_group"])
    assert groups == {"Fake", "Distorted", "True", "Unverified"}
    mapping = pd.read_csv(VERDICT_MAPPING, encoding="utf-8-sig")
    assert mapping["rows"].sum() == len(store.news)


def test_non_verdict_posts_are_not_treated_as_fake(store):
    unverified = store.news[store.news["verdict_group"] == "Unverified"]
    assert len(unverified) == 3268
    assert unverified["verdict_th"].isna().all()


def test_every_finance_row_has_a_reason(store):
    finance = store.news[store.news["is_finance_extended"]]
    assert finance["classification_reason"].notna().all()
    assert (finance["finance_match_field"] != "none").all()
    assert finance["finance_topic"].notna().all()


def test_core_scope_is_exactly_the_afnc_finance_category(store):
    news = store.news
    assert (news["is_finance_core"] == (news["category_th"] == "การเงิน-หุ้น")).all()
    assert news["is_finance_core"].sum() == 2514


def test_core_is_inside_extended(store):
    assert store.news.loc[store.news["is_finance_core"], "is_finance_extended"].all()


def test_extended_scope_never_takes_unverified_posts(store):
    extra = store.news[store.news["is_finance_extended"] & ~store.news["is_finance_core"]]
    assert (extra["verdict_group"] != "Unverified").all()


def test_view_counts_are_valid_and_not_filled(store):
    assert store.news["view_count_valid"].all()
    assert (store.news["view_count"] >= 0).all()


def test_reposts_are_counted_not_dropped(store):
    assert store.news["is_repost"].sum() > 0
    assert len(store.news) == store.news["post_id"].nunique()


def test_acsc_has_one_row_per_sunday_week(store):
    assert store.acsc["week_start"].is_unique
    assert (store.acsc["week_start"].dt.dayofweek == 6).all()


def test_eight_day_week_is_realigned_and_tagged(store):
    row = store.acsc[store.acsc["week_start"] == pd.Timestamp("2026-05-31")].iloc[0]
    assert row["week_start_raw"] == pd.Timestamp("2026-05-30")
    assert row["days"] == 8
    assert row["quality_status"] == "eight_day_period"


def test_suspect_week_is_kept_and_flagged(store):
    row = store.acsc[store.acsc["week_start"] == pd.Timestamp("2026-08-16")].iloc[0]
    assert row["cases"] == 79311
    assert bool(row["excluded_from_stats_by_default"]) is True
    assert store.acsc["excluded_from_stats_by_default"].sum() == 1


def test_loss_precision_is_preserved(store):
    assert store.acsc["loss_precision"].value_counts().to_dict() == {"exact": 37, "rounded": 11}


def test_generated_files_exist():
    assert AI_INCIDENTS_CLEAN.exists() and FINANCIAL_TOPIC_RULES.exists() and EXTENDED_SCOPE_REVIEW.exists()


def test_raw_datasets_are_all_present():
    assert len(list(RAW_DIR.glob("AIID_Excel_Export-*.xlsx"))) == 12
    assert (RAW_DIR / "thai-disinfo-scam-dataset.xlsx").exists()


def test_topic_rules_ignore_look_alike_words():
    assert assign_topic("สธ. ปรับระยะเวลาฉีดวัคซีน")[0] == "other_finance"
    assert assign_topic("ศธ. ยกเลิกระเบียบทรงผม")[0] == "other_finance"
    assert assign_topic("ถูกตำรวจสากลตามจับ")[0] == "other_finance"
    assert assign_topic("ประกาศ 1 ธ.ค. นี้")[0] == "other_finance"


def test_topic_rules_match_real_finance_terms():
    assert assign_topic("ธ.ก.ส. เปิดให้กู้สินเชื่อ")[0] == "loan"
    assert assign_topic("ก.ล.ต. เปิดลงทุนหุ้น")[0] == "investment"
    assert assign_topic("ธ.กรุงเทพ ส่งเอกสารขอข้อมูล")[0] == "bank"


def test_verdict_prefix_is_removed_only_for_display():
    assert strip_verdict_prefix("ข่าวปลอม อย่าแชร์! ออมสินปล่อยกู้") == "ออมสินปล่อยกู้"
    assert strip_verdict_prefix("ออมสินปล่อยกู้") == "ออมสินปล่อยกู้"


def test_headline_numbers_match_a_direct_read_of_the_raw_files(store):
    """An independent path: no cleaning code, just pandas on the source workbooks."""
    raw_ai = pd.read_excel(
        RAW_DIR / "AIID_Excel_Export-20261019.xlsx", sheet_name="Incidents", header=2,
        usecols=["Incident ID", "Injuries", "Lives Lost"],
    )
    assert raw_ai["Incident ID"].nunique() == len(store.incidents)
    assert int(((raw_ai["Injuries"] > 0) | (raw_ai["Lives Lost"] > 0)).sum()) == 21

    raw_news = pd.read_excel(RAW_DIR / "thai-disinfo-scam-dataset.xlsx", sheet_name="afnc_items", usecols=["post_id", "verdict_th", "category_th"])
    finance = raw_news[raw_news["category_th"] == "การเงิน-หุ้น"]
    assert finance["post_id"].nunique() == 2514
    assert finance["verdict_th"].value_counts().to_dict() == {"ข่าวปลอม": 2339, "ข่าวจริง": 118, "ข่าวบิดเบือน": 57}
