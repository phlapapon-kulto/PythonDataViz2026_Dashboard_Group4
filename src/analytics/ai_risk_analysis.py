"""KPI and chart data for Tab 1. Pure functions over ai_incidents_clean."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

MISSING = "__missing__"  # filter option for rows where the source has no value
FIRST_TREND_YEAR = 2013  # earlier years hold a few incidents each; they stay in every KPI


@dataclass(frozen=True)
class AiFilters:
    year_from: int | None = None
    year_to: int | None = None
    month: str | None = None
    regions: tuple[str, ...] = ()
    domains: tuple[str, ...] = ()
    subdomain: str | None = None
    harm: tuple[str, ...] = ()


def _matches(series: pd.Series, selected: tuple[str, ...]) -> pd.Series:
    mask = series.isin([s for s in selected if s != MISSING])
    if MISSING in selected:
        mask = mask | series.isna()
    return mask


def filter_incidents(df: pd.DataFrame, f: AiFilters, ignore: frozenset[str] = frozenset()) -> pd.DataFrame:
    """Apply every filter except those named in `ignore`.

    A chart ignores its own dimension so its other bars stay visible and clickable.
    """
    mask = pd.Series(True, index=df.index)
    if "years" not in ignore:
        if f.year_from is not None:
            mask &= df["year"] >= f.year_from
        if f.year_to is not None:
            mask &= df["year"] <= f.year_to
    if f.month and "month" not in ignore:
        mask &= df["month"] == f.month
    if f.regions and "regions" not in ignore:
        mask &= _matches(df["location_region"], f.regions)
    if f.domains and "domains" not in ignore:
        mask &= _matches(df["risk_domain"], f.domains)
    if f.subdomain and "domains" not in ignore:
        mask &= df["risk_subdomain"] == f.subdomain
    if f.harm and "harm" not in ignore:
        mask &= _matches(df["harm_domain"], f.harm)
    return df[mask]


def count_incidents(df: pd.DataFrame) -> int:
    return int(df["incident_id"].nunique())


def count_risk_domains(df: pd.DataFrame) -> int:
    return int(df["risk_domain"].nunique(dropna=True))


def casualty_summary(df: pd.DataFrame) -> dict:
    """positive needs Injuries > 0 or Lives Lost > 0; a blank never counts as zero."""
    injuries = pd.to_numeric(df["injuries"], errors="coerce")
    lives = pd.to_numeric(df["lives_lost"], errors="coerce")
    coded = injuries.notna() | lives.notna()
    positive = (injuries > 0) | (lives > 0)
    total = count_incidents(df)
    coded_count = int(df.loc[coded, "incident_id"].nunique())
    return {
        "positive": int(df.loc[positive, "incident_id"].nunique()),
        "coded": coded_count,
        "total": total,
        "coded_pct": coded_count / total * 100 if total else None,
    }


def growth_pct(current: int, previous: int) -> float | None:
    """(N_t - N_t-1) / N_t-1 * 100, or None when the previous count is zero."""
    return None if previous == 0 else (current - previous) / previous * 100


def annual_growth(df: pd.DataFrame, f: AiFilters, data_end: pd.Timestamp) -> dict:
    """Year-over-year change for the selected window.

    `df` must not have the year filter applied. The last year in the data stops
    before December, so comparing it with a full previous year would show a fall
    that did not happen. By default the KPI therefore uses the latest complete year.
    When that partial year is chosen on its own, both years stop on the same date.
    """
    last_full_year = data_end.year - 1 if (data_end.month, data_end.day) != (12, 31) else data_end.year
    year_to = min(f.year_to or data_end.year, data_end.year)
    same_period = f.year_from == f.year_to == data_end.year and last_full_year < data_end.year
    year = data_end.year if same_period else min(year_to, last_full_year)

    current, previous = df[df["year"] == year], df[df["year"] == year - 1]
    if same_period:
        current = current[current["date"] <= data_end]
        previous = previous[previous["date"] <= data_end - pd.DateOffset(years=1)]
    n_current, n_previous = count_incidents(current), count_incidents(previous)
    return {
        "year": year,
        "previous_year": year - 1,
        "current": n_current,
        "previous": n_previous,
        "pct": growth_pct(n_current, n_previous),
        "same_period": same_period,
    }


def top_risk_domains(df: pd.DataFrame, n: int = 5, keep: tuple[str, ...] = ()) -> pd.DataFrame:
    """Top n classified domains, plus any selected domain that fell outside them."""
    classified = df[df["risk_domain"].notna()]
    grouped = (
        classified.groupby(["risk_domain", "risk_domain_th"]).agg(incidents=("incident_id", "nunique")).reset_index()
    ).sort_values(["incidents", "risk_domain"], ascending=[False, True])
    shown = grouped.head(n)
    extra = grouped[grouped["risk_domain"].isin(keep) & ~grouped["risk_domain"].isin(shown["risk_domain"])]
    result = pd.concat([shown, extra]).copy()
    total = int(grouped["incidents"].sum())
    result["share_pct"] = result["incidents"] / total * 100 if total else 0.0
    return result


def yearly_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Every year from FIRST_TREND_YEAR on. A year with no record shows 0: nothing was recorded."""
    counts = df.groupby("year")["incident_id"].nunique()
    last_year = int(df["year"].max()) if len(df) else FIRST_TREND_YEAR
    years = range(FIRST_TREND_YEAR, max(last_year, FIRST_TREND_YEAR) + 1)
    return pd.DataFrame({"year": list(years), "incidents": [int(counts.get(y, 0)) for y in years]})


def monthly_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Months from FIRST_TREND_YEAR on, unless only earlier years were selected."""
    recent = df[df["year"] >= FIRST_TREND_YEAR]
    counts = (recent if len(recent) else df).groupby("month")["incident_id"].nunique().sort_index()
    if counts.empty:
        return pd.DataFrame({"month": [], "incidents": []})
    months = pd.period_range(counts.index[0], counts.index[-1], freq="M").strftime("%Y-%m")
    return pd.DataFrame({"month": list(months), "incidents": [int(counts.get(m, 0)) for m in months]})


def incidents_before_trend(df: pd.DataFrame) -> int:
    return count_incidents(df[df["year"] < FIRST_TREND_YEAR])


def risk_tree(df: pd.DataFrame) -> pd.DataFrame:
    """Treemap rows: one per domain and one per subdomain, plus an unclassified block."""
    rows = []
    for (domain, domain_th), group in df[df["risk_domain"].notna()].groupby(["risk_domain", "risk_domain_th"]):
        rows.append({
            "id": domain, "parent": "", "label": domain_th, "english": domain,
            "incidents": count_incidents(group), "domain": domain, "subdomain": None,
        })
        with_sub = group[group["risk_subdomain"].notna()]
        for (sub, sub_th), part in with_sub.groupby(["risk_subdomain", "risk_subdomain_th"]):
            rows.append({
                "id": f"{domain}/{sub}", "parent": domain, "label": sub_th, "english": sub,
                "incidents": count_incidents(part), "domain": domain, "subdomain": sub,
            })
        unlabeled = count_incidents(group[group["risk_subdomain"].isna()])
        if unlabeled:
            rows.append({
                "id": f"{domain}/{MISSING}", "parent": domain, "label": "ไม่ระบุกลุ่มย่อย", "english": "Not specified",
                "incidents": unlabeled, "domain": domain, "subdomain": None,
            })
    unclassified = count_incidents(df[df["risk_domain"].isna()])
    if unclassified:
        rows.append({
            "id": MISSING, "parent": "", "label": "ยังไม่จำแนก", "english": "Not yet classified",
            "incidents": unclassified, "domain": MISSING, "subdomain": None,
        })
    return pd.DataFrame(rows, columns=["id", "parent", "label", "english", "incidents", "domain", "subdomain"])


def region_counts(df: pd.DataFrame) -> pd.DataFrame:
    coded = df[df["location_region"].notna()]
    counts = coded.groupby("location_region")["incident_id"].nunique().sort_values(ascending=False)
    return pd.DataFrame({"region": counts.index, "incidents": counts.values})


def harm_counts(df: pd.DataFrame) -> pd.DataFrame:
    coded = df[df["harm_domain"].notna()]
    counts = coded.groupby("harm_domain")["incident_id"].nunique()
    order = [h for h in ("yes", "maybe", "no") if h in counts.index]
    return pd.DataFrame({"harm": order, "incidents": [int(counts[h]) for h in order]})
