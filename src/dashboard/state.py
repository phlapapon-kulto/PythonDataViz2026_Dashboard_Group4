"""Filter state as plain dicts, and the rules for clicks and resets.

This module has no Dash imports, so every interaction rule can be unit tested
without a browser.
"""
from __future__ import annotations

from src.analytics.ai_risk_analysis import MISSING, AiFilters
from src.analytics.financial_news_analysis import SCOPE_CORE, NewsFilters
from src.analytics.scam_correlation_analysis import RelFilters
from src.config import FINANCE_CORE_CATEGORY

YEAR_SLIDER_MIN = 2012  # the left end of the slider means "2012 and earlier"
YEAR_SLIDER_MAX = 2026
CASES_SLIDER = [5000, 8000]  # the right end means "8,000 and above"
LOSS_SLIDER = [100, 700]  # million baht; the right end means "700 and above"
OPT_SUSPECT = "include_suspect"
OPT_EXACT = "exact_only"


def default_state(news_start: str, news_end: str, rel_start: str, rel_end: str) -> dict:
    return {
        "years": [YEAR_SLIDER_MIN, YEAR_SLIDER_MAX],
        "ai_regions": [], "ai_domains": [], "ai_harm": [], "ai_subdomain": None, "ai_month": None,
        "news_scope": SCOPE_CORE, "news_verdicts": [], "news_start": news_start, "news_end": news_end,
        "news_keyword": "", "news_month": None, "news_topic": None, "news_post": None,
        "rel_start": rel_start, "rel_end": rel_end, "rel_scope": "core", "rel_topic": None,
        "rel_cases": list(CASES_SLIDER), "rel_loss": list(LOSS_SLIDER), "rel_options": [], "rel_week": None,
    }


def toggle(values: list | None, key) -> list:
    values = list(values or [])
    if key in values:
        values.remove(key)
    else:
        values.append(key)
    return values


def click_key(click: dict | None):
    """Read the key a chart stored on the clicked mark."""
    if not click or not click.get("points"):
        return None
    point = click["points"][0]
    if point.get("id"):
        return point["id"]
    key = point.get("customdata")
    return key[0] if isinstance(key, (list, tuple)) else key


def _click_treemap(state: dict, key: str) -> None:
    if "/" not in key:
        state["ai_domains"] = toggle(state["ai_domains"], key)
        state["ai_subdomain"] = None
        return
    domain, subdomain = key.split("/", 1)
    if subdomain == MISSING:
        state["ai_domains"] = toggle(state["ai_domains"], domain)
        state["ai_subdomain"] = None
    elif state["ai_subdomain"] == subdomain:
        state["ai_subdomain"] = None
        state["ai_domains"] = [d for d in state["ai_domains"] if d != domain]
    else:
        state["ai_subdomain"] = subdomain
        state["ai_domains"] = [domain]


def _click_year(state: dict, year: int) -> None:
    state["years"] = [YEAR_SLIDER_MIN, YEAR_SLIDER_MAX] if state["years"] == [year, year] else [year, year]
    state["ai_month"] = None


def _click_ai_trend(state: dict, key: str) -> None:
    kind, value = key.split(":", 1)
    if kind == "year":
        _click_year(state, int(value))
    else:
        state["ai_month"] = None if state["ai_month"] == value else value


def _click_news_category(state: dict, category: str) -> None:
    target = SCOPE_CORE if category == FINANCE_CORE_CATEGORY else category
    state["news_scope"] = SCOPE_CORE if state["news_scope"] == target else target
    state["news_topic"] = None
    state["news_post"] = None


def apply_click(state: dict, source: str, key) -> dict:
    """Return the state after a chart click. A second click on the same mark undoes it."""
    state = dict(state)
    if source in ("ai-top-domains",):
        state["ai_domains"] = toggle(state["ai_domains"], key)
        state["ai_subdomain"] = None
    elif source == "ai-treemap":
        _click_treemap(state, str(key))
    elif source == "ai-trend":
        _click_ai_trend(state, str(key))
    elif source == "ai-region-chart":
        state["ai_regions"] = toggle(state["ai_regions"], key)
    elif source == "ai-harm-chart":
        state["ai_harm"] = toggle(state["ai_harm"], key)
    elif source == "news-category-chart":
        _click_news_category(state, key)
    elif source == "news-verdict-chart":
        state["news_verdicts"] = toggle(state["news_verdicts"], key)
    elif source == "news-trend":
        state["news_month"] = None if state["news_month"] == key else key
    elif source == "news-topic-chart":
        state["news_topic"] = None if state["news_topic"] == key else key
    elif source == "news-top-chart":
        state["news_post"] = None if state["news_post"] == key else key
    elif source in ("rel-trend", "rel-scatter-cases", "rel-scatter-loss"):
        state["rel_week"] = None if state["rel_week"] == key else key
    return state


def year_bounds(years: list[int]) -> tuple[int | None, int | None]:
    low, high = years
    return (None if low == YEAR_SLIDER_MIN else low), (None if high == YEAR_SLIDER_MAX else high)


def ai_filters(years, regions, domains, harm, subdomain, month) -> AiFilters:
    low, high = year_bounds(years)
    return AiFilters(low, high, month, tuple(regions or ()), tuple(domains or ()), subdomain, tuple(harm or ()))


def news_filters(years, scope, verdicts, start, end, keyword, month, topic, post) -> NewsFilters:
    low, high = year_bounds(years)
    return NewsFilters(
        scope=scope or SCOPE_CORE, verdicts=tuple(verdicts or ()), date_from=start, date_to=end,
        year_from=low, year_to=high, keyword=keyword or "", month=month, topic=topic, post_id=post,
    )


def rel_filters(years, start, end, scope, topic, cases, loss, options) -> RelFilters:
    low, high = year_bounds(years)
    options = options or []
    return RelFilters(
        week_from=start, week_to=end, year_from=low, year_to=high, scope=scope or "core", topic=topic or None,
        cases_min=None if cases[0] == CASES_SLIDER[0] else cases[0],
        cases_max=None if cases[1] == CASES_SLIDER[1] else cases[1],
        loss_min=None if loss[0] == LOSS_SLIDER[0] else loss[0] * 1e6,
        loss_max=None if loss[1] == LOSS_SLIDER[1] else loss[1] * 1e6,
        include_suspect=OPT_SUSPECT in options, exact_loss_only=OPT_EXACT in options,
    )
