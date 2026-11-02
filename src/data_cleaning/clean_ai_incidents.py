"""Clean the AI Incident Database export.

Only the newest snapshot is analysed. Each export is the whole database on its
download date, so adding snapshots together would count the same incident up to
twelve times. The older exports are read for one purpose: the audit table that
shows how the database changed between downloads.
"""
from __future__ import annotations

import pandas as pd

from src.config import AI_INCIDENTS_CLEAN, AIID_FILE_NAMED_IN_DOCS, AIID_HEADER_ROW, RAW_DIR, SNAPSHOT_AUDIT
from src.data_cleaning.common import (
    QualityLog,
    aiid_snapshots,
    require_columns,
    snapshot_date,
    write_csv,
)

REQUIRED_COLUMNS = [
    "Incident ID", "date", "year", "title", "Risk Domain", "Risk Subdomain",
    "Harm Domain", "Injuries", "Lives Lost", "Location Region",
]

# Thai display labels written for this project. The English originals stay in the
# data and in every tooltip, so a reader can always trace back to the source term.
RISK_DOMAIN_TH = {
    "Malicious Actors & Misuse": "ผู้ไม่หวังดีและการใช้ในทางที่ผิด",
    "AI system safety, failures, and limitations": "ความปลอดภัย ความล้มเหลว และข้อจำกัดของ AI",
    "Discrimination and Toxicity": "การเลือกปฏิบัติและเนื้อหาเป็นพิษ",
    "Misinformation": "ข้อมูลเท็จ",
    "Privacy & Security": "ความเป็นส่วนตัวและความปลอดภัย",
    "Human-Computer Interaction": "ปฏิสัมพันธ์มนุษย์กับ AI",
    "Socioeconomic & Environmental Harms": "ผลกระทบเศรษฐกิจ สังคม และสิ่งแวดล้อม",
}

RISK_SUBDOMAIN_TH = {
    "Fraud, scams, and targeted manipulation": "การฉ้อโกง หลอกลวง และชักจูงแบบเจาะจง",
    "Lack of capability or robustness": "ขีดความสามารถหรือความทนทานไม่พอ",
    "False or misleading information": "ข้อมูลเท็จหรือชวนเข้าใจผิด",
    "Disinformation, surveillance, and influence at scale": "บิดเบือนข้อมูล สอดแนม และชี้นำวงกว้าง",
    "Unfair discrimination and misrepresentation": "เลือกปฏิบัติและนำเสนออย่างไม่เป็นธรรม",
    "Exposure to toxic content": "การเผชิญเนื้อหาเป็นพิษ",
    "Compromise of privacy by obtaining, leaking or correctly inferring sensitive information": "ละเมิดความเป็นส่วนตัวและข้อมูลอ่อนไหว",
    "Overreliance and unsafe use": "พึ่งพาเกินควรและใช้งานไม่ปลอดภัย",
    "Unequal performance across groups": "ประสิทธิภาพไม่เท่าเทียมระหว่างกลุ่ม",
    "AI system security vulnerabilities and attacks": "ช่องโหว่และการโจมตีระบบ AI",
    "Cyberattacks, weapon development or use, and mass harm": "โจมตีไซเบอร์ อาวุธ และอันตรายวงกว้าง",
    "Increased inequality and decline in employment quality": "ความเหลื่อมล้ำและคุณภาพงานลดลง",
    "Power centralization and unfair distribution of benefits": "รวมศูนย์อำนาจและกระจายประโยชน์ไม่เป็นธรรม",
    "Lack of transparency or interpretability": "ขาดความโปร่งใสหรืออธิบายไม่ได้",
    "Economic and cultural devaluation of human effort": "ลดคุณค่างานของมนุษย์",
    "Loss of human agency and autonomy": "สูญเสียความเป็นอิสระของมนุษย์",
    "Pollution of information ecosystem and loss of consensus reality": "มลพิษในระบบนิเวศข้อมูล",
    "AI pursuing its own goals in conflict with human goals or values": "AI มุ่งเป้าหมายที่ขัดกับมนุษย์",
    "Competitive dynamics": "พลวัตการแข่งขัน",
    "Governance failure": "ความล้มเหลวด้านธรรมาภิบาล",
    "Environmental harm": "ผลกระทบสิ่งแวดล้อม",
}

REGION_TH = {
    "North America": "อเมริกาเหนือ",
    "Global": "ทั่วโลก",
    "Europe": "ยุโรป",
    "Asia": "เอเชีย",
    "Oceania": "โอเชียเนีย",
    "Africa": "แอฟริกา",
    "South America": "อเมริกาใต้",
}

HARM_TH = {"yes": "มีอันตรายชัดเจน", "maybe": "อาจมีอันตราย", "no": "ไม่พบอันตราย"}


def read_snapshot(path, columns=None) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name="Incidents", header=AIID_HEADER_ROW, usecols=columns)


def clean_text(series: pd.Series) -> pd.Series:
    """Trim whitespace and turn empty strings into missing values."""
    return series.astype("string").str.strip().replace("", pd.NA)


def audit_snapshots(log: QualityLog) -> pd.DataFrame:
    """One row per export. Used only to document change, never to count incidents."""
    rows, previous = [], None
    for path in aiid_snapshots():
        df = read_snapshot(path, ["Incident ID", "date", "Risk Domain"])
        ids = set(df["Incident ID"])
        rows.append({
            "snapshot": snapshot_date(path),
            "file": path.name,
            "rows": len(df),
            "unique_incident_ids": len(ids),
            "new_ids_vs_previous": len(ids - previous) if previous is not None else None,
            "removed_ids_vs_previous": len(previous - ids) if previous is not None else None,
            "max_incident_date": pd.to_datetime(df["date"]).max().date().isoformat(),
            "without_risk_domain": int(df["Risk Domain"].isna().sum()),
        })
        previous = ids
    audit = pd.DataFrame(rows)
    write_csv(audit, SNAPSHOT_AUDIT)
    log.fact("ai", "snapshot_count", len(audit))
    log.fact("ai", "rows_if_snapshots_were_wrongly_summed", int(audit["rows"].sum()))
    log.fact("ai", "ids_removed_between_snapshots", int(audit["removed_ids_vs_previous"].fillna(0).sum()))
    return audit


def add_casualty_fields(df: pd.DataFrame) -> pd.DataFrame:
    """has_casualty stays missing unless the source coded the incident: blank is not zero."""
    df["injuries"] = pd.to_numeric(df["Injuries"], errors="coerce").astype("Int64")
    df["lives_lost"] = pd.to_numeric(df["Lives Lost"], errors="coerce").astype("Int64")
    coded = df["injuries"].notna() | df["lives_lost"].notna()
    positive = (df["injuries"].fillna(0) > 0) | (df["lives_lost"].fillna(0) > 0)
    df["has_casualty"] = pd.Series(pd.NA, index=df.index, dtype="boolean")
    df.loc[coded, "has_casualty"] = positive[coded]
    return df


def clean(log: QualityLog) -> pd.DataFrame:
    snapshots = aiid_snapshots()
    latest = snapshots[-1]
    raw = read_snapshot(latest)
    require_columns(raw, REQUIRED_COLUMNS, f"{latest.name} / Incidents")

    log.fact("ai", "source_file", latest.name)
    log.fact("ai", "file_named_in_docs", AIID_FILE_NAMED_IN_DOCS)
    log.fact("ai", "file_named_in_docs_exists", (RAW_DIR / AIID_FILE_NAMED_IN_DOCS).exists())
    log.step("ai", "read latest snapshot", len(raw), len(raw), "Header is on row 3; rows 1-2 are banners")

    df = raw.copy()
    id_nulls = int(df["Incident ID"].isna().sum())
    id_duplicates = int(df["Incident ID"].duplicated().sum())
    log.fact("ai", "incident_id_nulls", id_nulls)
    log.fact("ai", "incident_id_duplicates", id_duplicates)
    if id_nulls or id_duplicates:
        raise ValueError("Incident ID must be present and unique before counting")

    df["incident_id"] = df["Incident ID"].astype(int)
    expected_ids = set(range(1, df["incident_id"].max() + 1))
    log.fact("ai", "unused_incident_ids", sorted(expected_ids - set(df["incident_id"])))

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    log.fact("ai", "unparseable_dates", int(df["date"].isna().sum()))
    log.fact("ai", "year_disagrees_with_date", int((df["date"].dt.year != pd.to_numeric(df["year"])).sum()))
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.strftime("%Y-%m")
    log.fact("ai", "date_min", df["date"].min().date().isoformat())
    log.fact("ai", "date_max", df["date"].max().date().isoformat())

    df["risk_domain"] = clean_text(df["Risk Domain"])
    df["risk_subdomain"] = clean_text(df["Risk Subdomain"])
    df["risk_domain_th"] = df["risk_domain"].map(RISK_DOMAIN_TH)
    df["risk_subdomain_th"] = df["risk_subdomain"].map(RISK_SUBDOMAIN_TH)
    unmapped = sorted(set(df["risk_domain"].dropna()) - set(RISK_DOMAIN_TH))
    unmapped += sorted(set(df["risk_subdomain"].dropna()) - set(RISK_SUBDOMAIN_TH))
    if unmapped:
        raise ValueError(f"Risk labels without a Thai mapping: {unmapped}")

    df["harm_domain"] = clean_text(df["Harm Domain"])
    df["location_region"] = clean_text(df["Location Region"])
    df["country_code"] = clean_text(df["Country Code"])
    df["data_sources"] = clean_text(df["Data Sources"])
    df = add_casualty_fields(df)

    casualty_counts = df["has_casualty"].value_counts(dropna=False)
    log.fact("ai", "rows_clean", len(df))
    log.fact("ai", "without_risk_domain", int(df["risk_domain"].isna().sum()))
    log.fact("ai", "without_risk_subdomain", int(df["risk_subdomain"].isna().sum()))
    log.fact("ai", "without_location_region", int(df["location_region"].isna().sum()))
    log.fact("ai", "without_harm_domain", int(df["harm_domain"].isna().sum()))
    log.fact("ai", "casualty_coded", int(df["has_casualty"].notna().sum()))
    log.fact("ai", "casualty_positive", int(casualty_counts.get(True, 0)))
    log.fact("ai", "last_year_with_region", int(df.loc[df["location_region"].notna(), "year"].max()))
    log.fact("ai", "thai_country_code_rows", int(df["country_code"].fillna("").str.contains("TH").sum()))
    top = df.nlargest(3, "injuries")[["incident_id", "injuries", "title"]]
    log.fact("ai", "largest_injury_values_kept", top.to_dict("records"))
    log.step("ai", "clean types and labels", len(raw), len(df), "No rows removed; missing values stay missing")

    out = df[[
        "incident_id", "date", "year", "month", "title", "description",
        "risk_domain", "risk_subdomain", "risk_domain_th", "risk_subdomain_th",
        "harm_domain", "location_region", "country_code",
        "injuries", "lives_lost", "has_casualty", "data_sources", "report_count",
    ]].sort_values("incident_id")
    write_csv(out, AI_INCIDENTS_CLEAN)
    return out


def run(log: QualityLog) -> pd.DataFrame:
    audit_snapshots(log)
    return clean(log)
