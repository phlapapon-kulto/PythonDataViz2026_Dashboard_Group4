"""KPI, weekly frames and Pearson statistics for Tab 3.

Correlation here is description, not explanation. Both series fell during the
ACSC window and AFNC moved posts between categories part-way through it, so
sensitivity_table() reports the same statistic under other reasonable definitions.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import NormalDist

import numpy as np
import pandas as pd

from src.config import FALSE_VERDICT_GROUPS

SCOPE_CORE = "core"
SCOPE_EXTENDED = "extended"
MIN_PAIRS = 3  # fewer points than this give no usable r
LOW_SAMPLE = 10  # below this a trend line and a firm reading are withheld
RELABEL_MONTH = "2026-02"  # first month AFNC published verdicts as อาชญากรรมออนไลน์ at volume


@dataclass(frozen=True)
class RelFilters:
    week_from: str | None = None
    week_to: str | None = None
    year_from: int | None = None
    year_to: int | None = None
    scope: str = SCOPE_CORE
    topic: str | None = None
    cases_min: float | None = None
    cases_max: float | None = None
    loss_min: float | None = None
    loss_max: float | None = None
    include_suspect: bool = False
    exact_loss_only: bool = False


@dataclass(frozen=True)
class Correlation:
    r: float | None
    n: int
    status: str  # ok | insufficient | no_variance
    reason: str
    ci_low: float | None = None
    ci_high: float | None = None

    @property
    def direction(self) -> str:
        if self.r is None:
            return "ไม่สามารถระบุ"
        if abs(self.r) < 0.1:
            return "ไม่มีทิศทางชัดเจน"
        return "ทิศทางเดียวกัน" if self.r > 0 else "ทิศทางตรงข้าม"

    @property
    def strength(self) -> str:
        if self.r is None:
            return "N/A"
        size = abs(self.r)
        if size < 0.1:
            return "แทบไม่สัมพันธ์"
        if size < 0.3:
            return "อ่อน"
        if size < 0.5:
            return "ปานกลาง"
        if size < 0.7:
            return "ค่อนข้างแรง"
        return "แรง"


def pearson(x: pd.Series, y: pd.Series) -> Correlation:
    """Pearson r on complete pairs, with a Fisher z 95% interval.

    The interval assumes independent observations. Weekly counts are autocorrelated,
    so read it as a lower bound on the uncertainty.
    """
    frame = pd.DataFrame({"x": pd.to_numeric(x, errors="coerce"), "y": pd.to_numeric(y, errors="coerce")}).dropna()
    n = len(frame)
    if n < MIN_PAIRS:
        return Correlation(None, n, "insufficient", f"มีคู่ข้อมูลครบเพียง {n} สัปดาห์ ต้องมีอย่างน้อย {MIN_PAIRS}")
    if frame["x"].nunique() < 2 or frame["y"].nunique() < 2:
        return Correlation(None, n, "no_variance", "ตัวแปรหนึ่งมีค่าคงที่ จึงคำนวณความสัมพันธ์ไม่ได้")
    r = float(np.corrcoef(frame["x"].astype(float), frame["y"].astype(float))[0, 1])
    low, high = None, None
    if n > 3 and abs(r) < 1:
        z = math.atanh(r)
        margin = NormalDist().inv_cdf(0.975) / math.sqrt(n - 3)
        low, high = math.tanh(z - margin), math.tanh(z + margin)
    return Correlation(r, n, "ok", "", low, high)


def trend_line(x: pd.Series, y: pd.Series) -> tuple[list[float], list[float]] | None:
    """Least-squares line for a scatter plot, or None when the sample is too small."""
    frame = pd.DataFrame({"x": pd.to_numeric(x, errors="coerce"), "y": pd.to_numeric(y, errors="coerce")}).dropna()
    if len(frame) < LOW_SAMPLE or frame["x"].nunique() < 2:
        return None
    slope, intercept = np.polyfit(frame["x"].astype(float), frame["y"].astype(float), 1)
    ends = [float(frame["x"].min()), float(frame["x"].max())]
    return ends, [slope * value + intercept for value in ends]


def weekly_frame(panel: pd.DataFrame, items: pd.DataFrame, scope: str = SCOPE_CORE, topic: str | None = None) -> pd.DataFrame:
    """The final panel with false_count recounted from posts for this scope and topic."""
    in_scope = items["is_finance_extended"] if scope == SCOPE_EXTENDED else items["is_finance_core"]
    mask = in_scope & items["verdict_group"].isin(FALSE_VERDICT_GROUPS)
    if topic:
        mask &= items["finance_topic_id"] == topic
    counts = items[mask].groupby("week_start").size()
    frame = panel.copy()
    frame["false_count"] = frame["week_start"].map(counts).fillna(0).astype(int)
    return frame


def apply_filters(frame: pd.DataFrame, f: RelFilters) -> pd.DataFrame:
    """Keep the weeks in range, then mark which ones may enter the statistics.

    cases_used and loss_used are blank for any week that must not be counted, so a
    not-reported week can never become a zero.
    """
    mask = pd.Series(True, index=frame.index)
    if f.week_from:
        mask &= frame["week_start"] >= pd.Timestamp(f.week_from)
    if f.week_to:
        mask &= frame["week_start"] <= pd.Timestamp(f.week_to)
    if f.year_from is not None:
        mask &= frame["week_start"].dt.year >= f.year_from
    if f.year_to is not None:
        mask &= frame["week_start"].dt.year <= f.year_to
    if f.cases_min is not None:
        mask &= frame["cases"] >= f.cases_min
    if f.cases_max is not None:
        mask &= frame["cases"] <= f.cases_max
    if f.loss_min is not None:
        mask &= frame["loss_baht"] >= f.loss_min
    if f.loss_max is not None:
        mask &= frame["loss_baht"] <= f.loss_max
    out = frame[mask.fillna(False).astype(bool)].copy()

    usable = out["acsc_reported"] & (f.include_suspect | ~out["excluded_from_stats_by_default"])
    out["cases_used"] = pd.to_numeric(out["cases"], errors="coerce").where(usable)
    loss_ok = usable & ((out["loss_precision"] == "exact") if f.exact_loss_only else True)
    out["loss_used"] = pd.to_numeric(out["loss_baht"], errors="coerce").where(loss_ok)
    return out


def relationship_kpis(frame: pd.DataFrame) -> dict:
    cases, loss = frame["cases_used"], frame["loss_used"]
    both = frame[cases.notna() & loss.notna() & (cases > 0)]
    total_cases = float(both["cases_used"].sum())
    used_weeks = frame[cases.notna() | loss.notna()]
    return {
        "weeks": len(frame),
        "weeks_reported": int(frame["acsc_reported"].sum()),
        "weeks_used": len(used_weeks),
        "false_total": int(frame["false_count"].sum()),
        "false_per_week": float(used_weeks["false_count"].mean()) if len(used_weeks) else None,
        "cases_per_week": float(cases.mean()) if cases.notna().any() else None,
        "loss_per_week": float(loss.mean()) if loss.notna().any() else None,
        "loss_per_case": float(both["loss_used"].sum()) / total_cases if total_cases > 0 else None,
    }


def consecutive_changes(frame: pd.DataFrame) -> pd.DataFrame:
    """Week-to-week differences, only between weeks that are exactly seven days apart."""
    ordered = frame.sort_values("week_start")
    gap = ordered["week_start"].diff() == pd.Timedelta(days=7)
    changes = pd.DataFrame({
        "false_count": ordered["false_count"].diff(),
        "cases_used": ordered["cases_used"].diff(),
        "loss_used": ordered["loss_used"].diff(),
    })
    return changes[gap]


def sensitivity_table(panel: pd.DataFrame, items: pd.DataFrame) -> pd.DataFrame:
    """The same two correlations under each reasonable reading of the data."""
    window = panel[panel["in_acsc_window"]]
    core = weekly_frame(window, items, SCOPE_CORE)
    extended = weekly_frame(window, items, SCOPE_EXTENDED)
    before = pd.Timestamp(f"{RELABEL_MONTH}-01")

    cases: list[tuple[str, str, pd.DataFrame]] = [
        ("brd", "นิยาม BRD: หมวดการเงิน-หุ้น ตัดสัปดาห์น่าสงสัย", apply_filters(core, RelFilters())),
        ("with_suspect", "รวมสัปดาห์น่าสงสัย 16–22 ส.ค. 2026", apply_filters(core, RelFilters(include_suspect=True))),
        ("exact", "ใช้เฉพาะความเสียหายที่แม่นยำถึงบาท", apply_filters(core, RelFilters(exact_loss_only=True))),
        ("extended", "ขอบเขตข่าวการเงินแบบขยาย", apply_filters(extended, RelFilters())),
        ("before_relabel", "เฉพาะก่อน AFNC เริ่มลงคำตัดสินหมวดอาชญากรรมออนไลน์", apply_filters(core[core["week_start"] < before], RelFilters())),
    ]
    rows = []
    for key, label, frame in cases:
        with_cases, with_loss = pearson(frame["false_count"], frame["cases_used"]), pearson(frame["false_count"], frame["loss_used"])
        rows.append({"key": key, "label": label, "r_cases": with_cases.r, "n_cases": with_cases.n, "r_loss": with_loss.r, "n_loss": with_loss.n})

    changes = consecutive_changes(apply_filters(core, RelFilters()))
    with_cases, with_loss = pearson(changes["false_count"], changes["cases_used"]), pearson(changes["false_count"], changes["loss_used"])
    rows.append({"key": "changes", "label": "การเปลี่ยนแปลงรายสัปดาห์ (ตัดผลของแนวโน้มระยะยาว)", "r_cases": with_cases.r, "n_cases": with_cases.n, "r_loss": with_loss.r, "n_loss": with_loss.n})
    return pd.DataFrame(rows)
