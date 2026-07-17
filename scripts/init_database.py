#!/usr/bin/env python3
"""Initialize the Language Hub database.

Usage:
    python scripts/init_database.py

This script:
1. Creates database/language.db if it does not exist
2. Runs all pending migrations in scripts/migrations/
3. Seeds initial data (languages)
"""

import sqlite3
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "database" / "language.db"
MIGRATIONS_DIR = PROJECT_ROOT / "scripts" / "migrations"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def get_applied_migrations(conn):
    try:
        rows = conn.execute("SELECT version FROM _migrations").fetchall()
        return {row["version"] for row in rows}
    except sqlite3.OperationalError:
        return set()


def get_available_migrations():
    migrations = []
    for f in sorted(MIGRATIONS_DIR.glob("*.sql")):
        parts = f.stem.split("_", 1)
        version = int(parts[0])
        name = parts[1] if len(parts) > 1 else f.stem
        migrations.append((version, name, f))
    return migrations


def apply_migration(conn, version, name, path):
    sql = path.read_text(encoding="utf-8")
    log.info("Applying migration %03d: %s...", version, name)
    conn.executescript(sql)
    conn.execute(
        "INSERT INTO _migrations (version, name) VALUES (?, ?)",
        (version, name),
    )
    conn.commit()
    log.info("Migration %03d applied successfully.", version)


def seed_languages(conn):
    count = conn.execute("SELECT COUNT(*) FROM languages").fetchone()[0]
    if count == 0:
        languages = [("en", "English"), ("es", "Spanish"), ("fr", "French")]
        conn.executemany(
            "INSERT INTO languages (code, name) VALUES (?, ?)", languages
        )
        conn.commit()
        log.info("Seeded %d languages.", len(languages))
    else:
        log.info("Languages table already has %d entries, skipping seed.", count)


def main():
    log.info("Initializing database at %s", DB_PATH)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_db()
    applied = get_applied_migrations(conn)
    available = get_available_migrations()
    for version, name, path in available:
        if version not in applied:
            apply_migration(conn, version, name, path)
        else:
            log.debug("Migration %03d already applied, skipping.", version)
    seed_languages(conn)
    conn.close()
    log.info("Database initialization complete.")


if __name__ == "__main__":
    main()
