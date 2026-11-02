"""Clean Anti-Fake News Center posts and classify financial news.

Two finance scopes are produced because one is not enough:

* core: the AFNC category การเงิน-หุ้น. This is the BRD's primary definition and
  it reproduces weekly_panel.afnc_false_finance exactly.
* extended: core, plus verdict posts in other categories whose title or tags use
  specific finance terms. From February 2026 AFNC files many investment and loan
  impersonation posts under อาชญากรรมออนไลน์, so the core scope alone undercounts
  the most recent months.

The `content` column is kept out of the matching rule on purpose. It is cut to 500
characters in the workbook and matches boilerplate far more often than the subject
of the post, so a content-only hit is recorded but never decides the scope.
"""
from __future__ import annotations

import re

import pandas as pd

from src.config import (
    AFNC_ITEMS_CLEAN,
    DISTORTED,
    FAKE,
    FINANCE_CORE_CATEGORY,
    FINANCIAL_TOPIC_RULES,
    OTHER,
    THAI_WORKBOOK,
    TRUE,
    UNVERIFIED,
    VERDICT_MAPPING,
)
from src.data_cleaning.common import QualityLog, require_columns, require_file, write_csv

REQUIRED_COLUMNS = [
    "post_id", "published_bkk", "date", "week_start", "year", "month", "item_type",
    "verdict_th", "category_th", "title", "content", "topic_tags", "view_count",
]

VERDICT_GROUPS = {"ข่าวปลอม": FAKE, "ข่าวบิดเบือน": DISTORTED, "ข่าวจริง": TRUE}

# Evaluated top to bottom; the first match sets the topic. These terms were narrowed
# after reading random samples: a bare "ธ." also hits สธ./ศธ., and a bare กลต hits สากลตาม.
TOPIC_RULES = [
    {
        "topic_id": "loan",
        "topic_th": "สินเชื่อและเงินกู้",
        "pattern": r"สินเชื่อ|เงินกู้|กู้เงิน|ปล่อยกู้|ยื่นกู้|ให้กู้|กู้ง่าย|กู้ยืม|ลงทะเบียนกู้|เงินด่วน|ให้ยืม|ยืมเงิน|รวมหนี้",
        "note": "ข้อเสนอกู้เงินหรือสินเชื่อ แม้จะอ้างชื่อธนาคาร",
    },
    {
        "topic_id": "investment",
        "topic_th": "ชวนลงทุน หุ้น กองทุน",
        "pattern": (
            r"ลงทุน|หุ้น|ปันผล|กองทุน|เทรด|เปิดพอร์ต|พอร์ตการลงทุน|ตลาดหลักทรัพย์|หลักทรัพย์|ก\.ล\.ต"
            r"|(?<![ก-๙])กลต(?![ก-๙])|SET|SET50|คริปโต|บิตคอยน์|Bitcoin|Forex|ฟอเร็กซ์|ออมทอง"
        ),
        "note": "ชักชวนลงทุน หรืออ้างหน่วยงานกำกับตลาดทุน",
    },
    {
        "topic_id": "bank",
        "topic_th": "แอบอ้างธนาคารและบัญชี",
        "pattern": (
            r"ธนาคาร|ธ\.ก\.ส|ธ\.\s?(?:ออมสิน|กรุงไทย|กรุงเทพ|กสิกร|ไทยพาณิชย์|ทหารไทย|อิสลาม|อาคารสงเคราะห์)"
            r"|ออมสิน|(?<![ก-๙])ธกส(?![ก-๙])|(?<![ก-๙])ธอส(?![ก-๙])|กรุงไทย|กสิกร|ไทยพาณิชย์|ธปท|แบงก์ชาติ|แบงค์ชาติ"
            r"|บัตรเครดิต|ATM|เอทีเอ็ม|บัญชีม้า"
        ),
        "note": "แอบอ้างธนาคาร บัตร หรือบัญชี โดยไม่ได้ชวนกู้หรือลงทุนโดยตรง",
    },
]
OTHER_TOPIC = {"topic_id": "other_finance", "topic_th": "การเงินอื่น ๆ"}

# Terms that look financial but are not about personal finance or investment.
NON_FINANCE_PATTERN = (
    r"พาวเวอร์แบงค์|พาวเวอร์แบงก์|Power ?Bank|World Bank"
    r"|ธนาคาร(?:โลก|เลือด|น้ำ|ขยะ|อาหาร|ต้นไม้|ผลผลิต|ปู|สัตว์น้ำ|โค|ข้าว|ความรู้|เวลา|ดวงตา|เซลล์|นม)"
    r"|ไม่ต้องลงทุน|นักลงทุนต่างชาติ|กองทุน(?:น้ำมัน|เงินทดแทน|หมู่บ้าน|ยุติธรรม|สื่อ)"
    r"|หนี้สาธารณะ|รัฐบาลกู้เงิน|ไทยกู้เงิน|กู้เงิน พ\.ร\.ก|สัญญากู้|COVID|โควิด"
)

# Categories that may join the extended scope. Health and disaster posts mention
# banks only in passing, so they are never counted as financial news.
EXTENDED_ELIGIBLE_CATEGORIES = (
    "อาชญากรรมออนไลน์", "นโยบายรัฐบาล-ข่าวสาร", "เศรษฐกิจ", "ข่าวอื่นๆ", "ความสงบและความมั่นคง",
)

TITLE_PREFIX = re.compile(r"^\s*(ข่าวปลอม\s*อย่าแชร์\s*!?\s*|ข่าวปลอม\s+|ข่าวบิดเบือน\s+|ข่าวจริง\s+)")


def strip_verdict_prefix(title: str) -> str:
    """Older AFNC titles repeat the verdict; charts read better without it."""
    return TITLE_PREFIX.sub("", title).strip() or title


def assign_topic(text: str) -> tuple[str, str]:
    """Return (topic_id, matched term) for a title-plus-tags string."""
    for rule in TOPIC_RULES:
        match = re.search(rule["pattern"], text, flags=re.IGNORECASE)
        if match:
            return rule["topic_id"], match.group(0)
    return OTHER_TOPIC["topic_id"], ""


def classify_finance(df: pd.DataFrame) -> pd.DataFrame:
    """Add scope flags, topic and a reason that can be read row by row."""
    text = df["title"].fillna("") + " " + df["topic_tags"].fillna("")
    topics = text.map(assign_topic)
    df["finance_topic_id"] = topics.map(lambda t: t[0])
    df["finance_keyword"] = topics.map(lambda t: t[1])

    title_only = df["title"].fillna("").map(assign_topic).map(lambda t: t[0] != OTHER_TOPIC["topic_id"])
    keyword_hit = df["finance_topic_id"] != OTHER_TOPIC["topic_id"]
    excluded = text.str.contains(NON_FINANCE_PATTERN, case=False, regex=True)
    pattern_all = "|".join(rule["pattern"] for rule in TOPIC_RULES)
    df["content_only_keyword"] = (
        ~keyword_hit & df["content"].fillna("").str.contains(pattern_all, case=False, regex=True)
    )

    df["is_finance_core"] = df["category_th"] == FINANCE_CORE_CATEGORY
    joins_extended = (
        ~df["is_finance_core"]
        & df["verdict_group"].ne(UNVERIFIED)
        & df["category_th"].isin(EXTENDED_ELIGIBLE_CATEGORIES)
        & keyword_hit
        & ~excluded
    )
    df["is_finance_extended"] = df["is_finance_core"] | joins_extended

    df["finance_match_field"] = "none"
    df.loc[df["is_finance_core"], "finance_match_field"] = "category"
    df.loc[joins_extended & title_only, "finance_match_field"] = "title"
    df.loc[joins_extended & ~title_only, "finance_match_field"] = "tags"

    df["classification_reason"] = "ไม่เข้าเกณฑ์ข่าวการเงิน"
    df.loc[df["is_finance_core"], "classification_reason"] = "หมวด AFNC = การเงิน-หุ้น"
    df.loc[joins_extended, "classification_reason"] = (
        "คำสำคัญ '" + df.loc[joins_extended, "finance_keyword"] + "' ใน "
        + df.loc[joins_extended, "finance_match_field"] + " (หมวด " + df.loc[joins_extended, "category_th"] + ")"
    )

    labels = {r["topic_id"]: r["topic_th"] for r in TOPIC_RULES} | {OTHER_TOPIC["topic_id"]: OTHER_TOPIC["topic_th"]}
    df["finance_topic"] = df["finance_topic_id"].map(labels)
    df.loc[~df["is_finance_extended"], ["finance_topic_id", "finance_topic", "finance_keyword"]] = pd.NA
    return df


def verdict_mapping_table(df: pd.DataFrame) -> pd.DataFrame:
    counts = df["verdict_th"].fillna("(ว่าง)").value_counts()
    rows = [
        {"verdict_th": label, "verdict_group": group, "rows": int(counts.get(label, 0))}
        for label, group in VERDICT_GROUPS.items()
    ]
    rows.append({"verdict_th": "(ค่าอื่น)", "verdict_group": OTHER, "rows": 0})
    rows.append({"verdict_th": "(ว่าง)", "verdict_group": UNVERIFIED, "rows": int(counts.get("(ว่าง)", 0))})
    return pd.DataFrame(rows)


def topic_rules_table() -> pd.DataFrame:
    rows = [{"priority": i + 1, **rule} for i, rule in enumerate(TOPIC_RULES)]
    rows.append({"priority": len(rows) + 1, **OTHER_TOPIC, "pattern": "(ไม่ตรงกฎข้างบน)", "note": "ข่าวในขอบเขตการเงินที่ไม่ตรงกฎใด"})
    rows.append({
        "priority": "exclude", "topic_id": "excluded", "topic_th": "ตัดออกจากขอบเขตขยาย",
        "pattern": NON_FINANCE_PATTERN, "note": "คำที่ดูเหมือนการเงินแต่ไม่เกี่ยวกับการเงินส่วนบุคคลหรือการลงทุน",
    })
    return pd.DataFrame(rows)


def clean(log: QualityLog) -> pd.DataFrame:
    require_file(THAI_WORKBOOK)
    raw = pd.read_excel(THAI_WORKBOOK, sheet_name="afnc_items")
    require_columns(raw, REQUIRED_COLUMNS, "thai-disinfo-scam-dataset.xlsx / afnc_items")
    log.step("afnc", "read afnc_items", len(raw), len(raw), "One row per post")

    df = raw.copy()
    log.fact("afnc", "post_id_nulls", int(df["post_id"].isna().sum()))
    log.fact("afnc", "post_id_duplicates", int(df["post_id"].duplicated().sum()))
    if df["post_id"].isna().any() or df["post_id"].duplicated().any():
        raise ValueError("post_id must be present and unique before counting")

    df["published_bkk"] = pd.to_datetime(df["published_bkk"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["week_start"] = pd.to_datetime(df["week_start"], errors="coerce")
    sunday = df["date"] - pd.to_timedelta((df["date"].dt.dayofweek + 1) % 7, unit="D")
    log.fact("afnc", "unparseable_dates", int(df["published_bkk"].isna().sum() + df["date"].isna().sum()))
    log.fact("afnc", "date_disagrees_with_published", int((df["published_bkk"].dt.normalize() != df["date"]).sum()))
    log.fact("afnc", "week_start_disagrees_with_date", int((sunday != df["week_start"]).sum()))
    log.fact("afnc", "week_start_not_sunday", int((df["week_start"].dt.dayofweek != 6).sum()))
    log.fact("afnc", "date_min", df["date"].min().date().isoformat())
    log.fact("afnc", "date_max", df["date"].max().date().isoformat())

    unexpected = sorted(set(df["verdict_th"].dropna()) - set(VERDICT_GROUPS))
    log.fact("afnc", "unexpected_verdict_values", unexpected)
    df["verdict_group"] = df["verdict_th"].map(VERDICT_GROUPS)
    df.loc[df["verdict_th"].notna() & df["verdict_group"].isna(), "verdict_group"] = OTHER
    df["verdict_group"] = df["verdict_group"].fillna(UNVERIFIED)
    write_csv(verdict_mapping_table(df), VERDICT_MAPPING)
    write_csv(topic_rules_table(), FINANCIAL_TOPIC_RULES)

    df["view_count"] = pd.to_numeric(df["view_count"], errors="coerce").astype("Int64")
    df["view_count_valid"] = df["view_count"].notna() & (df["view_count"] >= 0)
    log.fact("afnc", "invalid_view_counts", int((~df["view_count_valid"]).sum()))
    log.fact("afnc", "view_count_max", int(df["view_count"].max()))

    df["title_clean"] = df["title"].fillna("").map(strip_verdict_prefix)
    # Reposts are real publications with their own post_id, so they stay in every count.
    df = df.sort_values(["published_bkk", "post_id"])
    df["repost_number"] = df.groupby(["title_clean", "verdict_group"]).cumcount() + 1
    df["is_repost"] = df["repost_number"] > 1
    log.fact("afnc", "same_title_reposts_kept", int(df["is_repost"].sum()))

    df = classify_finance(df)
    log.fact("afnc", "rows_clean", len(df))
    log.fact("afnc", "finance_core_rows", int(df["is_finance_core"].sum()))
    log.fact("afnc", "finance_extended_rows", int(df["is_finance_extended"].sum()))
    log.fact("afnc", "finance_extended_by_field", df["finance_match_field"].value_counts().to_dict())
    log.fact("afnc", "content_only_hits_not_counted", int(df["content_only_keyword"].sum()))
    log.fact("afnc", "verdict_counts", df["verdict_group"].value_counts().to_dict())
    log.fact("afnc", "content_max_length_in_workbook", int(df["content"].str.len().max()))
    log.step("afnc", "add verdict groups and finance scopes", len(raw), len(df), "No rows removed; reposts kept")

    out = df[[
        "post_id", "published_bkk", "date", "week_start", "year", "month", "item_type",
        "verdict_th", "verdict_en", "verdict_group", "verdict_source", "category_th", "category_en",
        "title", "title_clean", "topic_tags", "view_count", "view_count_valid",
        "is_finance_core", "is_finance_extended", "finance_topic_id", "finance_topic", "finance_keyword",
        "finance_match_field", "content_only_keyword", "classification_reason",
        "repost_number", "is_repost", "url",
    ]].sort_values("post_id")
    write_csv(out, AFNC_ITEMS_CLEAN)
    return out


def run(log: QualityLog) -> pd.DataFrame:
    return clean(log)
