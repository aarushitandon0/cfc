"""Loads the generated synthetic dataset (data/seed/output/*.json) into
whichever Repository backend is active (DB_BACKEND=local|firestore).

Run: python -m data.seed.seed
"""

from __future__ import annotations

import json
from pathlib import Path

from api.db.repository import get_repository

OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def main() -> None:
    repo = get_repository()
    repo.clear_all()

    centres = json.loads((OUTPUT_DIR / "centres.json").read_text(encoding="utf-8"))
    stock_items = json.loads((OUTPUT_DIR / "stock_items.json").read_text(encoding="utf-8"))
    daily_logs = json.loads((OUTPUT_DIR / "daily_logs.json").read_text(encoding="utf-8"))

    for centre in centres:
        repo.upsert_centre(centre)
    for item in stock_items:
        repo.upsert_stock_item(item)
    for log in daily_logs:
        repo.upsert_daily_log(log)

    print(f"seeded {len(centres)} centres, {len(stock_items)} stock items, {len(daily_logs)} daily logs")


if __name__ == "__main__":
    main()
