#!/usr/bin/env python3
"""Translate empty word definitions to Chinese using Google Translate (free).

Usage:
    python scripts/fill_translations.py
    python scripts/fill_translations.py --language en

What it does:
    For words with empty "translation" fields in their meanings,
    automatically translates the English/Spanish/French definition to Chinese.
"""

import json, logging, sys, time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.init_database import get_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

LANG_CODES = {"en": "en", "es": "es", "fr": "fr"}


def get_words_to_translate(conn, language=None):
    query = """
        SELECT w.id, w.text, l.code as lang, w.meanings
        FROM words w JOIN languages l ON w.language_id = l.id
        WHERE w.meanings IS NOT NULL AND w.meanings != '[]'
    """
    params = []
    if language:
        query += " AND l.code = ?"
        params.append(language)
    query += " ORDER BY l.code, w.text"

    rows = conn.execute(query, params).fetchall()
    result = []
    for r in rows:
        meanings = json.loads(r["meanings"])
        needs_translation = any(not m.get("translation") for m in meanings)
        if needs_translation:
            result.append(r)
    return result


def translate_text(text, target="zh-CN", source="en"):
    """Translate text using Google Translate (free, no API key needed)."""
    if not text or len(text) < 3:
        return ""
    try:
        from deep_translator import GoogleTranslator
        result = GoogleTranslator(source=source, target=target).translate(text[:500])
        return result or ""
    except Exception as e:
        log.debug("Translation failed: %s", e)
        return ""


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", "-l", help="Only this language")
    args = parser.parse_args()

    conn = get_db()
    words = get_words_to_translate(conn, args.language)

    if not words:
        log.info("All words already have translations! ✅")
        conn.close()
        return

    log.info("Found %d word(s) needing translation", len(words))
    stats = {"translated": 0, "skipped": 0, "failed": 0}

    for w in words:
        word_id, text, lang = w["id"], w["text"], w["lang"]
        meanings = json.loads(w["meanings"])
        source_lang = LANG_CODES.get(lang, "en")
        changed = False

        for m in meanings:
            if not m.get("translation"):
                definition = m.get("definition", "")
                if definition and len(definition) > 5:
                    translation = translate_text(definition, source=source_lang)
                    if translation and translation != definition:
                        m["translation"] = translation
                        changed = True
                        log.info("  ✅ %s: %s... → %s", text, definition[:40], translation[:40])
                    else:
                        log.info("  ⏭️  %s: translation empty", text)
                        stats["skipped"] += 1
                time.sleep(0.3)  # rate limit

        if changed:
            conn.execute(
                "UPDATE words SET meanings = ? WHERE id = ?",
                (json.dumps(meanings, ensure_ascii=False), word_id),
            )
            conn.commit()
            stats["translated"] += 1

    conn.close()
    print(f"\n{'='*50}")
    print(f"TRANSLATION SUMMARY")
    print(f"{'='*50}")
    print(f"  Translated: {stats['translated']}")
    print(f"  Skipped   : {stats['skipped']}")
    print(f"  Failed    : {stats['failed']}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
