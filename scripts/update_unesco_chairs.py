#!/usr/bin/env python3
"""Refresh the active UNITWIN/UNESCO Chairs CSV from the UNESCO DataHub."""

from __future__ import annotations

import csv
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "unesco_chairs.csv"
API = "https://data.unesco.org/api/explore/v2.1/catalog/datasets/fli001/records"
WHERE = 'type="Chair" AND year_closure is null'
MIN_ROWS = 500


def clean_label(value: str) -> str:
    text = str(value).replace("\u202f", " ").replace("\u00a0", " ").replace("\u200b", "")
    return re.sub(r"\s+", " ", text).strip()


def choice_name(code: str) -> str:
    return "c_" + re.sub(r"[^A-Za-z0-9_]", "_", code)


def fetch_chairs() -> list[dict]:
    records: list[dict] = []
    offset = 0
    limit = 100
    total = None
    while True:
        query = urllib.parse.urlencode(
            {"where": WHERE, "limit": limit, "offset": offset}
        )
        request = urllib.request.Request(
            f"{API}?{query}",
            headers={"User-Agent": "unesco-chairs-csv"},
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.load(response)
        total = int(payload.get("total_count") or 0)
        batch = payload.get("results") or []
        records.extend(batch)
        offset += limit
        if not batch or offset >= total:
            break
    if total is not None and len(records) != total:
        raise SystemExit(f"Expected {total} records from the DataHub, received {len(records)}")
    return records


def build_rows(records: list[dict]) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    seen: set[str] = set()
    for record in records:
        code = str(record.get("fli001_id") or "").strip()
        if not code:
            continue
        name = choice_name(code)
        if name in seen:
            continue
        seen.add(name)
        label = clean_label(record.get("title_en") or record.get("title_fr") or code)
        if not label:
            label = code
        rows.append((name, label))
    rows.sort(key=lambda item: (item[1].casefold(), item[0]))
    if len(rows) < MIN_ROWS:
        raise SystemExit(
            f"Refusing to replace the CSV: only {len(rows)} chairs were returned "
            f"(minimum {MIN_ROWS})."
        )
    return rows


def write_csv(rows: list[tuple[str, str]]) -> None:
    temporary = OUT.with_suffix(".csv.tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["name", "label"])
        writer.writerows(rows)
    temporary.replace(OUT)


def main() -> None:
    rows = build_rows(fetch_chairs())
    write_csv(rows)
    print(f"Wrote {len(rows)} chairs to {OUT.name}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Update failed: {error}", file=sys.stderr)
        raise
