"""Shared fixtures. Real-data tests read data/processed; KPI tests build tiny frames."""
from __future__ import annotations

import pandas as pd
import pytest

from src.dashboard.data_store import load_store


@pytest.fixture(scope="session")
def store():
    return load_store()


@pytest.fixture
def small_incidents() -> pd.DataFrame:
    """Hand-made incidents whose correct answers can be worked out on paper."""
    return pd.DataFrame({
        "incident_id": [1, 2, 3, 4, 5, 6],
        "date": pd.to_datetime(["2024-03-01", "2024-06-01", "2025-02-01", "2025-05-01", "2025-08-01", "2026-02-01"]),
        "year": [2024, 2024, 2025, 2025, 2025, 2026],
        "month": ["2024-03", "2024-06", "2025-02", "2025-05", "2025-08", "2026-02"],
        "risk_domain": ["A", "A", "B", "A", None, "B"],
        "risk_domain_th": ["ก", "ก", "ข", "ก", None, "ข"],
        "risk_subdomain": ["a1", "a2", "b1", "a1", None, "b1"],
        "risk_subdomain_th": ["ก1", "ก2", "ข1", "ก1", None, "ข1"],
        "location_region": ["Asia", None, "Europe", None, None, None],
        "harm_domain": ["yes", None, "no", None, None, None],
        "injuries": pd.array([2, 0, None, None, 0, None], dtype="Int64"),
        "lives_lost": pd.array([0, 0, None, None, 1, None], dtype="Int64"),
    })


@pytest.fixture
def small_news() -> pd.DataFrame:
    return pd.DataFrame({
        "post_id": [1, 2, 3, 4, 5, 6],
        "date": pd.to_datetime(["2025-01-05", "2025-01-06", "2025-02-02", "2025-02-03", "2025-03-02", "2025-03-03"]),
        "year": [2025] * 6,
        "month": ["2025-01", "2025-01", "2025-02", "2025-02", "2025-03", "2025-03"],
        "verdict_group": ["Fake", "Fake", "Distorted", "True", "Unverified", "Fake"],
        "category_th": ["การเงิน-หุ้น", "การเงิน-หุ้น", "การเงิน-หุ้น", "การเงิน-หุ้น", "คลังความรู้", "อาชญากรรมออนไลน์"],
        "is_finance_core": [True, True, True, True, False, False],
        "is_finance_extended": [True, True, True, True, False, True],
        "finance_topic_id": ["loan", "investment", "loan", "loan", None, "investment"],
        "finance_topic": ["สินเชื่อ", "ลงทุน", "สินเชื่อ", "สินเชื่อ", None, "ลงทุน"],
        "title_clean": ["สินเชื่อ ก", "หุ้น ข", "สินเชื่อ ค", "สินเชื่อ ง", "ความรู้", "ลงทุน จ"],
        "search_text": ["สินเชื่อ ก", "หุ้น ข", "สินเชื่อ ค", "สินเชื่อ ง", "ความรู้", "ลงทุน จ"],
        "view_count": pd.array([100, None, 300, 400, 500, 600], dtype="Int64"),
        "view_count_valid": [True, False, True, True, True, True],
        "url": ["u"] * 6,
    })


@pytest.fixture
def small_weeks() -> pd.DataFrame:
    """Six weeks: normal, zero-free figures, one unreported week and one suspect week."""
    return pd.DataFrame({
        "week_start": pd.to_datetime(["2026-01-04", "2026-01-11", "2026-01-18", "2026-01-25", "2026-02-01", "2026-02-08"]),
        "false_count": [1, 2, 3, 4, 5, 6],
        "acsc_reported": [True, True, True, True, False, True],
        "cases": [10.0, 20.0, 30.0, 40.0, None, 1000.0],
        "loss_baht": [100.0, 200.0, 300.0, 500.0, None, 9000.0],
        "loss_precision": ["exact", "exact", "exact", "rounded", None, "rounded"],
        "excluded_from_stats_by_default": [False, False, False, False, False, True],
    })
