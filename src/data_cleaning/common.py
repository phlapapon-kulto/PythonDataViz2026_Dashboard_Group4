"""Helpers shared by the cleaning scripts: schema checks, CSV output, the audit log."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

from src.config import AIID_PATTERN, INTERMEDIATE_DIR, PROCESSED_DIR, QUALITY_METADATA, RAW_DIR


class MissingSourceError(RuntimeError):
    """A raw file, sheet or required column is not where the pipeline expects it."""


def aiid_snapshots() -> list[Path]:
    """Every AIID export, oldest first, ordered by the date in the file name."""
    paths = sorted(RAW_DIR.glob(AIID_PATTERN), key=snapshot_date)
    if not paths:
        raise MissingSourceError(f"No {AIID_PATTERN} found in {RAW_DIR}")
    return paths


def snapshot_date(path: Path) -> str:
    match = re.search(r"(\d{8})", path.name)
    if not match:
        raise MissingSourceError(f"No date in file name: {path.name}")
    return match.group(1)


def require_columns(df: pd.DataFrame, columns: list[str], source: str) -> None:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise MissingSourceError(f"{source} is missing required columns: {missing}")


def require_file(path: Path) -> Path:
    if not path.exists():
        raise MissingSourceError(f"Required file not found: {path}")
    return path


def write_csv(df: pd.DataFrame, path: Path) -> None:
    # utf-8-sig keeps Thai text readable in Excel; a fixed line ending keeps the
    # file byte-identical whichever operating system rebuilds it.
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig", lineterminator="\n")


def ensure_output_dirs() -> None:
    INTERMEDIATE_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


class QualityLog:
    """Records every row-count change and finding so the reports never hand-type a number."""

    def __init__(self) -> None:
        self.steps: list[dict] = []
        self.facts: dict[str, dict] = {}

    def step(self, dataset: str, action: str, before: int, after: int, reason: str) -> None:
        self.steps.append(
            {"dataset": dataset, "action": action, "rows_before": before, "rows_after": after, "reason": reason}
        )

    def fact(self, dataset: str, key: str, value) -> None:
        self.facts.setdefault(dataset, {})[key] = value

    def save(self) -> None:
        QUALITY_METADATA.parent.mkdir(parents=True, exist_ok=True)
        payload = {"steps": self.steps, "facts": self.facts}
        QUALITY_METADATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def load_quality_metadata() -> dict:
    return json.loads(QUALITY_METADATA.read_text(encoding="utf-8"))
