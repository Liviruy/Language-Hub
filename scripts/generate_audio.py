#!/usr/bin/env python3
"""Generate pronunciation audio for words using Edge TTS.

Usage:
    python scripts/generate_audio.py
    python scripts/generate_audio.py --language en
    python scripts/generate_audio.py --word hello

What it does:
    1. Scans database for words without audio
    2. Generates mp3 using Microsoft Edge TTS (free, neural voices)
    3. Saves to data/audio/{lang}/{word}.mp3
    4. Updates the audio field in the database
    5. Skips words that already have audio (cache)

Voice mapping:
    - en: en-US-JennyNeural (English, female, friendly)
    - es: es-ES-AlvaroNeural (Spanish, male, clear)
    - fr: fr-FR-DeniseNeural (French, female, clear)
"""

import json
import logging
import re
import sys
import asyncio
from pathlib import Path

import edge_tts

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.init_database import get_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# Voice mapping: language_code -> (voice_name, description)
VOICES = {
    "en": ("en-US-JennyNeural", "English US, female, friendly"),
    "es": ("es-ES-AlvaroNeural", "Spanish Spain, male, clear"),
    "fr": ("fr-FR-DeniseNeural", "French France, female, clear"),
}

AUDIO_DIR = PROJECT_ROOT / "data" / "audio"


def sanitize_filename(text: str) -> str:
    """Remove characters that are problematic in filenames."""
    # Keep letters, numbers, spaces, hyphens, underscores
    safe = re.sub(r'[^\w\s-]', "", text)
    safe = re.sub(r"\s+", "_", safe.strip())
    return safe.lower()[:100]  # limit length


def get_words_without_audio(conn, language=None):
    """Find words that have no audio entry in the database."""
    query = """
        SELECT w.id, w.text, l.code as lang
        FROM words w
        JOIN languages l ON w.language_id = l.id
        WHERE (w.audio IS NULL OR w.audio = '[]')
    """
    params = []
    if language:
        query += " AND l.code = ?"
        params.append(language)
    query += " ORDER BY l.code, w.text"
    return conn.execute(query, params).fetchall()


def update_audio_field(conn, word_id, file_path, voice_name):
    """Set the audio field in the database to reference the generated file."""
    audio_entry = [{
        "file_path": str(file_path),
        "voice": voice_name,
        "provider": "edge_tts",
    }]
    conn.execute(
        "UPDATE words SET audio = ? WHERE id = ?",
        (json.dumps(audio_entry, ensure_ascii=False), word_id),
    )


async def generate_audio(word: str, lang: str, voice: str, output_path: Path) -> bool:
    """Generate audio file using Edge TTS. Returns True if successful."""
    try:
        # Create directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Edge TTS sounds more natural with proper sentence framing
        text = word

        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(output_path))

        if output_path.exists() and output_path.stat().st_size > 100:
            return True
        else:
            log.warning("  Audio file too small or missing: %s", output_path)
            return False

    except Exception as e:
        log.error("  Edge TTS failed for '%s' (%s): %s", word, lang, e)
        return False


async def process_words(conn, rows):
    """Process all words that need audio generation."""
    stats = {"generated": 0, "already_exist": 0, "failed": 0, "total": len(rows)}

    for row in rows:
        word = row["text"]
        lang = row["lang"]
        voice_name = VOICES.get(lang, (None, None))[0]

        if not voice_name:
            log.warning("[%s] %s: No voice configured, skipping", lang, word)
            stats["failed"] += 1
            continue

        # Build output path: data/audio/en/hello.mp3
        safe_name = sanitize_filename(word)
        output_path = AUDIO_DIR / lang / f"{safe_name}.mp3"

        # Cache: skip if file already exists
        if output_path.exists():
            # Still ensure the DB is updated
            update_audio_field(conn, row["id"], output_path, voice_name)
            conn.commit()
            stats["already_exist"] += 1
            log.info("[%s] %s: File exists, DB updated ✅", lang, word)
            continue

        # Generate audio
        log.info("[%s] %s: Generating audio...", lang, word)
        success = await generate_audio(word, lang, voice_name, output_path)

        if success:
            update_audio_field(conn, row["id"], output_path, voice_name)
            conn.commit()
            stats["generated"] += 1
            file_size = output_path.stat().st_size
            log.info("  ✅ %s: %s (%d bytes)", word, voice_name, file_size)
        else:
            stats["failed"] += 1
            log.warning("  ❌ %s: Generation failed", word)

    return stats


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate pronunciation audio")
    parser.add_argument("--language", "-l", help="Only this language (en/es/fr)")
    parser.add_argument("--word", "-w", help="Only this specific word")
    args = parser.parse_args()

    conn = get_db()

    if args.word:
        rows = conn.execute(
            "SELECT w.id, w.text, l.code as lang FROM words w JOIN languages l ON w.language_id = l.id WHERE w.text = ?",
            (args.word,),
        ).fetchall()
    else:
        rows = get_words_without_audio(conn, args.language)

    if not rows:
        log.info("All words already have audio! ✅")
        conn.close()
        return

    log.info("Found %d word(s) without audio", len(rows))

    # Run async processing
    stats = asyncio.run(process_words(conn, rows))

    conn.close()

    print(f"\n{'='*50}")
    print(f"AUDIO GENERATION SUMMARY")
    print(f"{'='*50}")
    print(f"  Total         : {stats['total']}")
    print(f"  Generated     : {stats['generated']}")
    print(f"  Already existed: {stats['already_exist']}")
    print(f"  Failed        : {stats['failed']}")
    print(f"{'='*50}")
    file_count = len(list(AUDIO_DIR.rglob("*.mp3")))
    print(f"  Total audio files: {file_count}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
