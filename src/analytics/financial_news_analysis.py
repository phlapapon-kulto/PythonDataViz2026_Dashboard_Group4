"""KPI and chart data for Tab 2. Pure functions over afnc_items_clean."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.config import DISTORTED, FAKE, FALSE_VERDICT_GROUPS, FINANCE_CORE_CATEGORY, TRUE, UNVERIFIED, VALID_VERDICT_GROUPS

SCOPE_CORE = "finance_core"
SCOPE_EXTENDED = "finance_extended"
SCOPE_ALL = "all"
FINANCE_SCOPES = (SCOPE_CORE, SCOPE_EXTENDED)


@dataclass(frozen=True)
class NewsFilters:
    scope: str = SCOPE_CORE  # a scope constant, or one AFNC category_th value
    verdicts: tuple[str, ...] = ()
    date_from: str | None = None
    date_to: str | None = None
    year_from: int | None = None
    year_to: int | None = None
    keyword: str = ""
    month: str | None = None
    topic: str | None = None
    post_id: int | None = None


def scope_mask(df: pd.DataFrame, scope: str) -> pd.Series:
    if scope == SCOPE_CORE:
        return df["is_finance_core"]
    if scope == SCOPE_EXTENDED:
        return df["is_finance_extended"]
    if scope == SCOPE_ALL:
        return pd.Series(True, index=df.index)
    return df["category_th"] == scope


def filter_news(df: pd.DataFrame, f: NewsFilters, ignore: frozenset[str] = frozenset()) -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)
    if "scope" not in ignore:
        mask &= scope_mask(df, f.scope)
    if f.verdicts and "verdicts" not in ignore:
        mask &= df["verdict_group"].isin(f.verdicts)
    if "dates" not in ignore:
        if f.date_from:
            mask &= df["date"] >= pd.Timestamp(f.date_from)
        if f.date_to:
            mask &= df["date"] <= pd.Timestamp(f.date_to)
        if f.year_from is not None:
            mask &= df["year"] >= f.year_from
        if f.year_to is not None:
            mask &= df["year"] <= f.year_to
    if f.month and "month" not in ignore:
        mask &= df["month"] == f.month
    keyword = f.keyword.strip().lower()
    if keyword and "keyword" not in ignore:
        mask &= df["search_text"].str.contains(keyword, regex=False)
    if f.topic and "topic" not in ignore:
        mask &= df["finance_topic_id"] == f.topic
    if f.post_id and "post" not in ignore:
        mask &= df["post_id"] == f.post_id
    return df[mask]


def news_kpis(df: pd.DataFrame) -> dict:
    groups = df["verdict_group"].value_counts()
    fake = int(groups.get(FAKE, 0))
    with_verdict = int(df["verdict_group"].isin(VALID_VERDICT_GROUPS).sum())
    views = pd.to_numeric(df.loc[df["view_count_valid"], "view_count"], errors="coerce").dropna()
    return {
        "posts": int(df["post_id"].nunique()),
        "fake": fake,
        "distorted": int(groups.get(DISTORTED, 0)),
        "true": int(groups.get(TRUE, 0)),
        "unverified": int(groups.get(UNVERIFIED, 0)),
        "with_verdict": with_verdict,
        "fake_pct": fake / with_verdict * 100 if with_verdict else None,
        "views_mean": float(views.mean()) if len(views) else None,
        "views_median": float(views.median()) if len(views) else None,
        "views_n": len(views),
    }


def verdict_distribution(df: pd.DataFrame) -> pd.DataFrame:
    order = [FAKE, DISTORTED, TRUE, UNVERIFIED]
    counts = df["verdict_group"].value_counts()
    rows = [{"verdict_group": g, "posts": int(counts.get(g, 0))} for g in order if counts.get(g, 0) > 0]
    return pd.DataFrame(rows, columns=["verdict_group", "posts"])


def false_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Fake and distorted posts per AFNC category, largest first."""
    false_posts = df[df["verdict_group"].isin(FALSE_VERDICT_GROUPS)]
    table = false_posts.pivot_table(index="category_th", columns="verdict_group", values="post_id", aggfunc="count", fill_value=0)
    table = table.reindex(columns=[FAKE, DISTORTED], fill_value=0)
    table["total"] = table.sum(axis=1)
    all_posts = df[df["verdict_group"].isin(VALID_VERDICT_GROUPS)].groupby("category_th").size()
    table["false_share_pct"] = table["total"] / all_posts.reindex(table.index) * 100
    return table.sort_values(["total", FAKE], ascending=False).reset_index()


def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Months across the whole selected span, so a month with no post plots as zero."""
    if df.empty:
        return pd.DataFrame(columns=["month", FAKE, DISTORTED, TRUE, UNVERIFIED])
    table = df.pivot_table(index="month", columns="verdict_group", values="post_id", aggfunc="count", fill_value=0)
    months = pd.period_range(table.index.min(), table.index.max(), freq="M").strftime("%Y-%m")
    table = table.reindex(months, fill_value=0).reindex(columns=[FAKE, DISTORTED, TRUE, UNVERIFIED], fill_value=0)
    return table.rename_axis("month").reset_index()


def false_by_topic(df: pd.DataFrame) -> pd.DataFrame:
    false_posts = df[df["verdict_group"].isin(FALSE_VERDICT_GROUPS) & df["finance_topic_id"].notna()]
    grouped = false_posts.groupby(["finance_topic_id", "finance_topic"]).size().rename("posts").reset_index()
    return grouped.sort_values("posts", ascending=False)


def top_viewed(df: pd.DataFrame, n: int = 8) -> pd.DataFrame:
    valid = df[df["view_count_valid"]]
    columns = ["post_id", "title_clean", "date", "category_th", "verdict_group", "view_count", "url"]
    return valid.nlargest(n, "view_count")[columns]


def scope_is_finance(scope: str) -> bool:
    return scope in FINANCE_SCOPES or scope == FINANCE_CORE_CATEGORY
