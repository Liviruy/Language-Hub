#!/usr/bin/env python3
"""Export vocabulary from database to Anki .apkg flashcard decks.

Usage:
    python scripts/export_anki.py
    python scripts/export_anki.py --language en
    python scripts/export_anki.py --output ./my_exports

What it does:
    1. Reads words from language.db
    2. Groups them by language and CEFR level
    3. Creates Anki decks with custom note model
    4. Embeds audio in the .apkg (media support)
    5. Uses stable GUIDs (no duplicate cards on re-export)
    6. Saves to exports/{Lang}_{Level}.apkg

Deck hierarchy:
    Language Hub
    ├── English
    │   ├── A1
    │   ├── A2
    │   └── B1
    ├── Spanish
    │   ├── A1
    │   └── A2
    └── French
        ├── A1
        └── A2
"""

import hashlib
import json
import logging
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

import genanki

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.init_database import get_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

EXPORT_DIR = PROJECT_ROOT / "exports"
AUDIO_DIR = PROJECT_ROOT / "data" / "audio"

# Language display names
LANG_NAMES = {"en": "English", "es": "Spanish", "fr": "French"}

# Unique model ID (generated once, stays the same forever)
MODEL_ID = 1625012345678
# Unique deck base ID
DECK_BASE_ID = 1625098765432


def build_note_model():
    """Create the Anki note model with our custom card template.
    
    Fields:
        word        — the vocabulary word
        ipa         — pronunciation
        meanings    — formatted definitions
        audio_tag   — [sound:filename.mp3] for media playback
    
    Template:
        Front:  {{word}}
        Back:   {{word}}  {{ipa}}
                {{meanings}}
                {{audio_tag}}
    """
    model = genanki.Model(
        MODEL_ID,
        "Language Hub Card",
        fields=[
            {"name": "word"},
            {"name": "ipa"},
            {"name": "meanings"},
            {"name": "audio_tag"},
        ],
        templates=[
            {
                "name": "Language Hub Card",
                "qfmt": """
<div class="front">{{word}}</div>
""",
                "afmt": """
<div class="back">
  <div class="word">{{word}}</div>
  <div class="ipa">{{ipa}}</div>
  <hr>
  <div class="meanings">{{meanings}}</div>
  <div class="audio">{{audio_tag}}</div>
</div>

<style>
.front {
  font-size: 48px;
  text-align: center;
  padding: 40px 20px;
  font-family: sans-serif;
}
.back {
  font-size: 18px;
  font-family: sans-serif;
  line-height: 1.6;
}
.word {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 4px;
}
.ipa {
  font-size: 20px;
  color: #666;
  margin-bottom: 12px;
  font-family: monospace;
}
.meanings {
  color: #333;
}
.meaning {
  margin-bottom: 10px;
  padding: 6px 0;
  border-bottom: 1px solid #eee;
}
.pos {
  font-weight: bold;
  color: #2a7a2a;
  font-size: 14px;
  text-transform: uppercase;
}
.definition {
  font-size: 16px;
}
.examples {
  font-size: 14px;
  color: #888;
  font-style: italic;
  margin-top: 2px;
}
.audio {
  margin-top: 16px;
}
</style>
""",
            },
        ],
    )
    return model


def make_guid(text: str, lang: str) -> str:
    """Generate a stable GUID from word text + language code.
    
    This ensures that re-exporting the same word produces the same GUID,
    so Anki won't create duplicate cards.
    """
    raw = f"{text}_{lang}".lower().strip()
    return hashlib.md5(raw.encode()).hexdigest()


def format_meanings(meanings_json: str) -> str:
    """Format the JSON meanings array into HTML for Anki display."""
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

        html = '<div class="meaning">'
        if pos:
            html += f'<div class="pos">{pos}</div>'
        html += f'<div class="definition">{definition}</div>'
        if examples:
            for ex in examples[:2]:  # max 2 examples
                html += f'<div class="examples">— {ex}</div>'
        html += "</div>"
        parts.append(html)

    return "\n".join(parts)


def get_audio_filename(text: str, lang: str) -> str | None:
    """Find the audio file for a word and return its export-friendly filename.
    
    Returns None if no audio file exists.
    """
    safe = re.sub(r"[^\w\s-]", "", text).strip().replace(" ", "_").lower()[:100]
    audio_path = AUDIO_DIR / lang / f"{safe}.mp3"

    if audio_path.exists():
        # Use a unique filename for the apkg to avoid collisions across languages
        return f"{lang}_{safe}.mp3"
    return None


def group_words(conn, language=None):
    """Fetch words from DB and group by (language_code, cefr_level)."""
    query = """
        SELECT w.text, l.code as lang, w.ipa, w.meanings, w.audio, w.cefr, w.tags
        FROM words w
        JOIN languages l ON w.language_id = l.id
        WHERE w.meanings IS NOT NULL AND w.meanings != '[]'
    """
    params = []
    if language:
        query += " AND l.code = ?"
        params.append(language)
    query += " ORDER BY l.code, w.cefr, w.text"

    rows = conn.execute(query, params).fetchall()

    # Group: {(lang, cefr or "Uncategorized"): [rows]}
    groups = defaultdict(list)
    for row in rows:
        level = row["cefr"].strip().upper() if row["cefr"] and row["cefr"].strip() else "Uncategorized"
        groups[(row["lang"], level)].append(row)

    return groups


def export_group(group_key, words, model, export_dir, all_media):
    """Export a single group as an .apkg file."""
    lang, level = group_key
    lang_name = LANG_NAMES.get(lang, lang.upper())
    deck_name = f"Language Hub::{lang_name}::{level}"

    # Stable deck ID from hash of deck name
    deck_id = DECK_BASE_ID + abs(hash(deck_name)) % 1000000
    deck = genanki.Deck(deck_id, deck_name)

    media_for_this_deck = []

    for word_data in words:
        text = word_data["text"]
        ipa = word_data["ipa"] or ""
        meanings_html = format_meanings(word_data["meanings"])

        # Handle audio
        audio_tag = ""
        audio_filename = get_audio_filename(text, lang)
        if audio_filename:
            audio_tag = f"[sound:{audio_filename}]"
            # Copy audio to export dir for packaging
            src = AUDIO_DIR / lang / audio_filename.replace(f"{lang}_", "", 1)
            # Actually the src filename doesn't have the lang_ prefix
            safe_src = re.sub(r"[^\w\s-]", "", text).strip().replace(" ", "_").lower()[:100]
            src = AUDIO_DIR / lang / f"{safe_src}.mp3"
            if src.exists():
                # genanki needs absolute paths for media files
                media_for_this_deck.append(str(src.resolve()))
                all_media.add(str(src.resolve()))

        # Stable GUID
        guid = make_guid(text, lang)

        # Tags from DB
        tags = []
        try:
            tags = json.loads(word_data["tags"]) if word_data["tags"] and word_data["tags"] != "[]" else []
        except (json.JSONDecodeError, TypeError):
            tags = []

        note = genanki.Note(
            model=model,
            fields=[text, ipa, meanings_html, audio_tag],
            guid=guid,
            tags=tags,
        )
        deck.add_note(note)

    # Export
    output_file = export_dir / f"{lang_name}_{level}.apkg"
    package = genanki.Package(deck)
    package.media_files = list(media_for_this_deck)

    try:
        package.write_to_file(str(output_file))
        size_kb = output_file.stat().st_size / 1024
        word_count = len(words)
        log.info("  ✅ %s (%s): %d words → %s (%.0f KB)", lang_name, level, word_count, output_file.name, size_kb)
        return True
    except Exception as e:
        log.error("  ❌ Failed to create %s: %s", output_file.name, e)
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Export Anki decks from database")
    parser.add_argument("--language", "-l", help="Only this language (en/es/fr)")
    parser.add_argument("--output", "-o", default=str(EXPORT_DIR), help="Output directory")
    args = parser.parse_args()

    export_dir = Path(args.output)
    export_dir.mkdir(parents=True, exist_ok=True)

    conn = get_db()
    groups = group_words(conn, args.language)

    if not groups:
        log.warning("No words found to export.")
        conn.close()
        return

    log.info("Found %d language/level groups", len(groups))

    model = build_note_model()
    all_media = set()
    results = []

    # Sort groups: en, es, fr order, then A1, A2, B1 level order
    level_order = {"A1": 0, "A2": 1, "B1": 2, "B2": 3, "C1": 4, "C2": 5, "Uncategorized": 99}
    sorted_groups = sorted(
        groups.items(),
        key=lambda x: (x[0][0], level_order.get(x[0][1], 50)),
    )

    for group_key, words in sorted_groups:
        lang_name = LANG_NAMES.get(group_key[0], group_key[0])
        level = group_key[1]
        total_words = len(words)
        log.info("Exporting %s %s (%d words)...", lang_name, level, total_words)
        success = export_group(group_key, words, model, export_dir, all_media)
        results.append((lang_name, level, total_words, success))

    conn.close()

    # Summary
    total = sum(r[2] for r in results)
    success_count = sum(1 for r in results if r[3])
    print(f"\n{'='*50}")
    print(f"ANKI EXPORT SUMMARY")
    print(f"{'='*50}")
    for lang_name, level, count, ok in results:
        status = "✅" if ok else "❌"
        print(f"  {status} {lang_name} {level}: {count} words")
    print(f"{'='*50}")
    print(f"  Total decks: {len(results)} ({success_count} successful)")
    print(f"  Total words : {total}")
    print(f"  Output dir  : {export_dir}")
    print(f"{'='*50}")

    # List generated files
    apkg_files = list(export_dir.glob("*.apkg"))
    if apkg_files:
        print(f"\nGenerated files:")
        for f in sorted(apkg_files):
            print(f"  📦 {f.name} ({f.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()

