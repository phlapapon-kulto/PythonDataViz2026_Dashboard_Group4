"""Rebuild every processed dataset and report from the raw files in datasets/."""
from __future__ import annotations

import sys
import time

from src.data_cleaning import clean_ai_incidents, clean_fake_news, clean_scam_data, inspect_data, validate_data
from src.data_cleaning.common import MissingSourceError, QualityLog, ensure_output_dirs
from src.data_integration import build_weekly_panel
from src.reporting import build_reports


def main() -> int:
    started = time.perf_counter()
    ensure_output_dirs()
    log = QualityLog()
    try:
        print("1/5 inspecting raw files")
        inspect_data.run(log)
        print("2/5 cleaning AI incidents")
        incidents = clean_ai_incidents.run(log)
        print("3/5 cleaning AFNC posts and ACSC weeks")
        items = clean_fake_news.run(log)
        acsc, panel = clean_scam_data.run(log)
        print("4/5 building weekly panel")
        final = build_weekly_panel.run(items, acsc, panel, log)
        print("5/5 validating and writing reports")
        validate_data.run(incidents, items, acsc, final, log)
        log.save()
        build_reports.run(log, items, final)
    except MissingSourceError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"done in {time.perf_counter() - started:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
