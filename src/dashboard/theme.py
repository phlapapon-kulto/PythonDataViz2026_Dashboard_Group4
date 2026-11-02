"""Design tokens and number formatting shared by figures and components."""
from __future__ import annotations

import pandas as pd

from src.config import DISTORTED, FAKE, TRUE, UNVERIFIED

FONT_URL = "https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600&display=swap"
FONT = "Kanit, 'Leelawadee UI', Tahoma, sans-serif"

# Brand palette from BRD section 11.
BLUE = "#2391FF"
YELLOW = "#FFF83F"
ORANGE = "#FFCD54"
PINK = "#F70063"
INK = "#202938"

INK_SOFT = "#4B5563"
INK_MUTED = "#6B7280"
HAIRLINE = "#ECE7DC"
DIMMED = "#D9DEE7"
SURFACE = "#FFFFFF"

VERDICT_COLOR = {FAKE: PINK, DISTORTED: ORANGE, TRUE: BLUE, UNVERIFIED: "#B6BECB"}
VERDICT_TH = {FAKE: "ข่าวปลอม", DISTORTED: "ข่าวบิดเบือน", TRUE: "ข่าวจริง", UNVERIFIED: "ไม่มีคำตัดสิน"}

# Treemap identity colours, fixed per domain so a filter never repaints a survivor.
DOMAIN_COLOR = {
    "Malicious Actors & Misuse": PINK,
    "AI system safety, failures, and limitations": BLUE,
    "Discrimination and Toxicity": ORANGE,
    "Misinformation": YELLOW,
    "Privacy & Security": INK,
    "Human-Computer Interaction": "#9CCBFF",
    "Socioeconomic & Environmental Harms": "#FFB3CF",
}
UNCLASSIFIED_COLOR = "#E4E7EC"
LIGHT_TILES = {ORANGE, YELLOW, "#9CCBFF", "#FFB3CF", UNCLASSIFIED_COLOR, DIMMED}

MONTH_TH = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]


def th_date(value) -> str:
    if value is None or pd.isna(value):
        return "ไม่กำหนด"
    stamp = pd.Timestamp(value)
    return f"{stamp.day} {MONTH_TH[stamp.month - 1]} {stamp.year}"


def th_month(value: str) -> str:
    stamp = pd.Timestamp(f"{value}-01")
    return f"{MONTH_TH[stamp.month - 1]} {stamp.year}"


def th_week(value) -> str:
    start = pd.Timestamp(value)
    end = start + pd.Timedelta(days=6)
    if start.month == end.month:
        return f"{start.day}–{end.day} {MONTH_TH[end.month - 1]} {end.year}"
    return f"{start.day} {MONTH_TH[start.month - 1]} – {end.day} {MONTH_TH[end.month - 1]} {end.year}"


def fmt_int(value) -> str:
    return "N/A" if value is None or pd.isna(value) else f"{int(round(float(value))):,}"


def fmt_one(value) -> str:
    return "N/A" if value is None or pd.isna(value) else f"{float(value):,.1f}"


def fmt_pct(value, signed: bool = False) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{float(value):+,.1f}%" if signed else f"{float(value):,.1f}%"


def fmt_million(baht) -> str:
    return "N/A" if baht is None or pd.isna(baht) else f"{float(baht) / 1e6:,.1f}"


def fmt_r(value) -> str:
    return "N/A" if value is None or pd.isna(value) else f"{float(value):+.2f}"
