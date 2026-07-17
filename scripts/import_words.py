#!/usr/bin/env python3
"""Import vocabulary from CSV or JSON files into the database.

Usage:
    python scripts/import_words.py data/raw/sample_en.csv
    python scripts/import_words.py data/raw/words.json

Supported formats:
    - CSV: columns = text, language, ipa, cefr, frequency, meanings, tags
    - JSON: array of word objects (same fields)

Import rules:
    - Detects file format by extension (.csv or .json)
    - Looks up language code and converts to language_id
    - Skips if word already exists (text + language duplicate check)
    - Reports summary of imported, skipped, and failed rows
"""

import csv
import json
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.init_database import get_db, DB_PATH

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def get_language_map(conn):
    """Return dict of {code: id} for quick lookup."""
    rows = conn.execute("SELECT code, id FROM languages").fetchall()
    return {row["code"]: row["id"] for row in rows}


def parse_meanings(raw):
    """Parse meanings field from JSON string; return JSON string for DB."""
    if not raw or raw.strip() == "":
        return "[]"
    try:
        parsed = json.loads(raw) if isinstance(raw, str) else raw
        if isinstance(parsed, list):
            return json.dumps(parsed, ensure_ascii=False)
        return "[]"
    except json.JSONDecodeError:
        log.warning("  Could not parse meanings JSON, using empty array")
        return "[]"


def parse_tags(raw):
    """Parse tags field: JSON array or comma-separated string."""
    if not raw or raw.strip() == "":
        return "[]"
    try:
        raw_str = raw.strip()
        if raw_str.startswith("["):
            parsed = json.loads(raw_str)
        else:
            # Comma-separated: "A1,greeting"
            parsed = [t.strip() for t in raw_str.split(",") if t.strip()]
        return json.dumps(parsed, ensure_ascii=False)
    except json.JSONDecodeError:
        log.warning("  Could not parse tags, using empty array")
        return "[]"


def word_exists(conn, text, language_id):
    """Check if a word already exists for this language."""
    row = conn.execute(
        "SELECT id FROM words WHERE text = ? AND language_id = ?",
        (text, language_id),
    ).fetchone()
    return row is not None


def import_csv(conn, file_path, lang_map):
    """Import words from a CSV file."""
    stats = {"imported": 0, "skipped": 0, "failed": 0, "total": 0}

    with open(file_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):  # row 1 = header
            stats["total"] += 1
            text = row.get("text", "").strip()
            lang_code = row.get("language", "").strip().lower()
            ipa = row.get("ipa", "").strip() or None
            cefr = row.get("cefr", "").strip().upper() or None

            # Parse frequency: can be empty
            freq_raw = row.get("frequency", "").strip()
            frequency = int(freq_raw) if freq_raw.isdigit() else None

            meanings = parse_meanings(row.get("meanings", ""))
            tags = parse_tags(row.get("tags", ""))

            # Validate required fields
            if not text:
                log.warning("  Row %d: empty text, skipping", row_num)
                stats["failed"] += 1
                continue
            if lang_code not in lang_map:
                log.warning(
                    "  Row %d: unknown language '%s', skipping",
                    row_num,
                    lang_code,
                )
                stats["failed"] += 1
                continue

            language_id = lang_map[lang_code]

            # Skip duplicates
            if word_exists(conn, text, language_id):
                log.info("  Row %d: '%s' (%s) already exists, skipping", row_num, text, lang_code)
                stats["skipped"] += 1
                continue

            # Insert
            conn.execute(
                """INSERT INTO words
                   (language_id, text, ipa, cefr, frequency, meanings, tags)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (language_id, text, ipa, cefr, frequency, meanings, tags),
            )
            stats["imported"] += 1
            log.info("  Row %d: imported '%s' (%s)", row_num, text, lang_code)

    conn.commit()
    return stats


def import_json(conn, file_path, lang_map):
    """Import words from a JSON file."""
    stats = {"imported": 0, "skipped": 0, "failed": 0, "total": 0}

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    words = data if isinstance(data, list) else [data]
    stats["total"] = len(words)

    for i, word in enumerate(words):
        text = word.get("text", "").strip()
        lang_code = word.get("language", "").strip().lower()

        if not text:
            log.warning("  Item %d: empty text, skipping", i + 1)
            stats["failed"] += 1
            continue
        if lang_code not in lang_map:
            log.warning("  Item %d: unknown language '%s', skipping", i + 1, lang_code)
            stats["failed"] += 1
            continue

        language_id = lang_map[lang_code]

        if word_exists(conn, text, language_id):
            log.info("  Item %d: '%s' (%s) already exists, skipping", i + 1, text, lang_code)
            stats["skipped"] += 1
            continue

        conn.execute(
            """INSERT INTO words
               (language_id, text, ipa, cefr, frequency, meanings, audio, tags)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                language_id,
                text,
                word.get("ipa", "").strip() or None,
                word.get("cefr", "").strip().upper() or None,
                word.get("frequency"),
                parse_meanings(word.get("meanings", "[]")),
                parse_meanings(word.get("audio", "[]")),
                parse_tags(word.get("tags", "[]")),
            ),
        )
        stats["imported"] += 1
        log.info("  Item %d: imported '%s' (%s)", i + 1, text, lang_code)

    conn.commit()
    return stats


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/import_words.py <file.csv|file.json>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        log.error("File not found: %s", file_path)
        sys.exit(1)

    # Detect format
    ext = file_path.suffix.lower()
    if ext not in (".csv", ".json"):
        log.error("Unsupported format: %s (use .csv or .json)", ext)
        sys.exit(1)

    log.info("Importing from: %s", file_path)
    if DB_PATH.exists():
        log.info("Database: %s (%d bytes)", DB_PATH, DB_PATH.stat().st_size)
    else:
        log.error("Database not found. Run init_database.py first.")
        sys.exit(1)

    conn = get_db()
    lang_map = get_language_map(conn)
    log.info("Available languages: %s", ", ".join(f"{k} ({v})" for k, v in lang_map.items()))

    if ext == ".csv":
        stats = import_csv(conn, file_path, lang_map)
    else:
        stats = import_json(conn, file_path, lang_map)

    conn.close()

    # Print summary
    print()
    print("=" * 50)
    print("IMPORT SUMMARY")
    print("=" * 50)
    print(f"  Total rows : {stats['total']}")
    print(f"  Imported   : {stats['imported']}")
    print(f"  Skipped    : {stats['skipped']} (already exist)")
    print(f"  Failed     : {stats['failed']} (validation errors)")
    print("=" * 50)


if __name__ == "__main__":
    main()
