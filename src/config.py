"""Paths and constants shared by the pipeline, analytics and dashboard."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = ROOT / "datasets"
DATA_DIR = ROOT / "data"
INTERMEDIATE_DIR = DATA_DIR / "intermediate"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = ROOT / "reports"

THAI_WORKBOOK = RAW_DIR / "thai-disinfo-scam-dataset.xlsx"
AIID_PATTERN = "AIID_Excel_Export-*.xlsx"
# handoff.md names this export, but the repository has nothing later than 20261019.
AIID_FILE_NAMED_IN_DOCS = "AIID_Excel_Export-20261026.xlsx"
AIID_HEADER_ROW = 2  # rows 0-1 are a title and a group banner, not column names

AI_INCIDENTS_CLEAN = PROCESSED_DIR / "ai_incidents_clean.csv"
AFNC_ITEMS_CLEAN = PROCESSED_DIR / "afnc_items_clean.csv"
ACSC_WEEKLY_CLEAN = PROCESSED_DIR / "acsc_weekly_clean.csv"
WEEKLY_PANEL_CLEAN = PROCESSED_DIR / "weekly_panel_clean.csv"
WEEKLY_PANEL_FINAL = PROCESSED_DIR / "weekly_panel_final.csv"

VERDICT_MAPPING = INTERMEDIATE_DIR / "verdict_mapping.csv"
FINANCIAL_TOPIC_RULES = INTERMEDIATE_DIR / "financial_topic_rules.csv"
QUALITY_METADATA = INTERMEDIATE_DIR / "data_quality_metadata.json"
SNAPSHOT_AUDIT = INTERMEDIATE_DIR / "aiid_snapshot_audit.csv"
PANEL_RECONCILIATION = INTERMEDIATE_DIR / "panel_reconciliation.csv"
EXTENDED_SCOPE_REVIEW = INTERMEDIATE_DIR / "extended_scope_review_sample.csv"

# Verdict groups used across the whole project.
FAKE = "Fake"
DISTORTED = "Distorted"
TRUE = "True"
OTHER = "Other"
UNVERIFIED = "Unverified"
VALID_VERDICT_GROUPS = (FAKE, DISTORTED, TRUE, OTHER)
FALSE_VERDICT_GROUPS = (FAKE, DISTORTED)

FINANCE_CORE_CATEGORY = "การเงิน-หุ้น"
ONLINE_CRIME_CATEGORY = "อาชญากรรมออนไลน์"

# Weeks the source itself says must not be read as normal weeks.
SUSPECT_WEEK = "2026-08-16"
