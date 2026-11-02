"""Record what the raw files contain before anything is cleaned."""
from __future__ import annotations

import pandas as pd
from openpyxl import load_workbook

from src.config import AIID_HEADER_ROW, RAW_DIR, THAI_WORKBOOK
from src.data_cleaning.common import QualityLog, aiid_snapshots, require_file


def sheet_inventory(path) -> list[dict]:
    workbook = load_workbook(path, read_only=True)
    sheets = [{"sheet": ws.title, "state": ws.sheet_state, "rows": ws.max_row, "columns": ws.max_column} for ws in workbook.worksheets]
    workbook.close()
    return sheets


def column_profile(df: pd.DataFrame) -> list[dict]:
    return [
        {
            "column": str(column),
            "dtype": str(df[column].dtype),
            "missing": int(df[column].isna().sum()),
            "missing_pct": round(float(df[column].isna().mean()) * 100, 1),
            "unique": int(df[column].nunique(dropna=True)),
        }
        for column in df.columns
    ]


def run(log: QualityLog) -> None:
    require_file(THAI_WORKBOOK)
    files = [{"file": p.name, "size_bytes": p.stat().st_size, "sheets": sheet_inventory(p)} for p in aiid_snapshots()]
    files.append({"file": THAI_WORKBOOK.name, "size_bytes": THAI_WORKBOOK.stat().st_size, "sheets": sheet_inventory(THAI_WORKBOOK)})
    log.fact("inspection", "raw_dir", RAW_DIR.name)
    log.fact("inspection", "files", files)

    profiles = {"Incidents": column_profile(pd.read_excel(aiid_snapshots()[-1], sheet_name="Incidents", header=AIID_HEADER_ROW))}
    for sheet in ("afnc_items", "acsc_weekly", "weekly_panel"):
        profiles[sheet] = column_profile(pd.read_excel(THAI_WORKBOOK, sheet_name=sheet))
    log.fact("inspection", "profiles", profiles)
    notes = pd.read_excel(THAI_WORKBOOK, sheet_name="README", header=None).dropna(how="all").fillna("")
    log.fact("inspection", "source_readme", [" ".join(str(v) for v in row if v != "") for row in notes.values.tolist()])
