#!/usr/bin/env python3
"""Sync words from database to Anki via AnkiConnect.

Prerequisites:
    1. Anki running (open Anki app)
    2. AnkiConnect plugin installed (code: 2055492159)

Usage:
    python scripts/sync_anki.py
"""

import hashlib
import json
import logging
import re
import sys
import time
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.init_database import get_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

ANKI_CONNECT_URL = "http://localhost:8765"
REQUEST_DELAY = 0.1
LANG_NAMES = {"en": "English", "es": "Spanish", "fr": "French"}
AUDIO_DIR = PROJECT_ROOT / "data" / "audio"


def anki(action, params=None):
    payload = {"action": action, "version": 6, "params": params or {}}
    try:
        r = requests.post(ANKI_CONNECT_URL, json=payload, timeout=10).json()
        if r.get("error"):
            log.error("AnkiConnect error: %s", r["error"])
            return None
        return r.get("result")
    except requests.ConnectionError:
        log.error("Cannot connect to Anki. Open Anki first.")
        return None


def check_anki():
    v = anki("version")
    if v:
        log.info("Anki connected (v%s) ✅", v)
        return True
    return False


def ensure_model():
    if "Language Hub Card" in (anki("modelNames") or []):
        log.info("Model already exists")
        return True

    log.info("Creating note model...")
    r = anki("createModel", {
        "modelName": "Language Hub Card",
        "inOrderFields": ["word", "ipa", "meanings", "audio_tag"],
        "css": ".front{font-size:48px;text-align:center;padding:40px 20px}.back{font-size:18px;line-height:1.6}.word{font-size:32px;font-weight:bold}.ipa{font-size:20px;color:#666;font-family:monospace}",
        "cardTemplates": [{
            "Name": "Language Hub Card",
            "Front": '<div class="front">{{word}}</div>',
            "Back": '<div class="back"><div class="word">{{word}}</div><div class="ipa">{{ipa}}</div><hr><div class="meanings">{{meanings}}</div><div class="audio">{{audio_tag}}</div></div>',
        }],
    })
    if r:
        log.info("Model created ✅")
        return True
    return False


def ensure_deck(lang, level):
    name = f"Language Hub::{LANG_NAMES.get(lang, lang)}::{level}"
    if name in (anki("deckNames") or []):
        return name
    anki("createDeck", {"deck": name})
    return name


def make_guid(text, lang):
    raw = f"{text}_{lang}".lower().strip()
    return hashlib.md5(raw.encode()).hexdigest()


def fmt_meanings(meanings_json):
    try:
        meanings = json.loads(meanings_json) if meanings_json and meanings_json != "[]" else []
    except json.JSONDecodeError:
        meanings = []
    if not meanings:
        return ""
    parts = []
    for m in meanings:
        pos = m.get("pos", "")
        definition = m.get("definition", "")
        examples = m.get("examples", [])
        html = "<div>"
        if pos:
            html += f"<b>{pos}</b> "
        html += f"{definition}"
        if examples:
            for ex in examples[:2]:
                html += f"<br><i>— {ex}</i>"
        html += "</div>"
        parts.append(html)
    return "\n".join(parts)


def store_audio(word, lang):
    """Send audio file to Anki via AnkiConnect using file path."""
    safe = re.sub(r"[^\w\s-]", "", word).strip().replace(" ", "_").lower()[:100]
    audio_path = AUDIO_DIR / lang / f"{safe}.mp3"
    if not audio_path.exists():
        return ""

    filename = f"lh_{lang}_{safe}.mp3"
    result = anki("storeMediaFile", {
        "filename": filename,
        "path": str(audio_path.resolve()),
        "skipHash": "exists",
    })
    if result is not None:
        log.info("  Audio: %s", filename)
        return f"[sound:{filename}]"
    return ""


def add_note(text, lang, ipa, meanings_html, audio_tag, tags, deck_name):
    note = {
        "deckName": deck_name,
        "modelName": "Language Hub Card",
        "fields": {
            "word": text,
            "ipa": ipa,
            "meanings": meanings_html,
            "audio_tag": audio_tag,
        },
        "tags": tags,
        "options": {"allowDuplicate": False, "duplicateScope": "deck"},
    }
    result = anki("addNote", {"note": note})
    if result:
        log.info("  ✅ Added: %s", text)
        return "added"
    else:
        log.info("  ⏭️  Duplicate: %s", text)
        return "skipped"


def main():
    conn = get_db()
    rows = conn.execute("""
        SELECT w.text, l.code as lang, w.ipa, w.meanings, w.cefr, w.tags
        FROM words w JOIN languages l ON w.language_id = l.id
        WHERE w.meanings IS NOT NULL AND w.meanings != '[]'
        ORDER BY l.code, w.cefr, w.text
    """).fetchall()
    conn.close()

    if not rows:
        log.warning("No words found.")
        return

    if not check_anki():
        sys.exit(1)

    ensure_model()
    log.info("Syncing %d word(s)...", len(rows))

    stats = {"added": 0, "skipped": 0}

    for row in rows:
        lang = row["lang"]
        level = (row["cefr"] or "Uncategorized").strip().upper() or "Uncategorized"
        deck = ensure_deck(lang, level)

        tags = []
        try:
            tags = json.loads(row["tags"]) if row["tags"] and row["tags"] != "[]" else []
        except Exception:
            pass

        audio_tag = store_audio(row["text"], lang)
        meanings_html = fmt_meanings(row["meanings"])

        time.sleep(REQUEST_DELAY)
        result = add_note(row["text"], lang, row["ipa"] or "", meanings_html, audio_tag, tags, deck)
        if result == "added":
            stats["added"] += 1
        else:
            stats["skipped"] += 1

    total = len(rows)
    print(f"\n{'='*50}")
    print(f"SYNC COMPLETE")
    print(f"{'='*50}")
    print(f"  Total   : {total}")
    print(f"  Added   : {stats['added']}")
    print(f"  Skipped : {stats['skipped']}")
    print(f"{'='*50}")
    print(f"  Open Anki to see your cards!")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()

