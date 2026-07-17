#!/usr/bin/env python3
"""Export words from database to docs/words.json for API and website use."""

import json, sqlite3, sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.init_database import get_db

conn = get_db()
conn.row_factory = sqlite3.Row
rows = conn.execute("""
    SELECT w.text, l.code as lang, l.name as lang_name,
           w.ipa, w.cefr, w.meanings, w.audio, w.tags
    FROM words w JOIN languages l ON w.language_id = l.id
    ORDER BY l.code, w.cefr, w.text
""").fetchall()

words = []
for r in rows:
    words.append({
        "text": r["text"],
        "lang": r["lang"],
        "lang_name": r["lang_name"],
        "ipa": r["ipa"] or "",
        "cefr": r["cefr"] or "",
        "meanings": json.loads(r["meanings"]) if r["meanings"] and r["meanings"] != "[]" else [],
        "audio": json.loads(r["audio"]) if r["audio"] and r["audio"] != "[]" else [],
        "tags": json.loads(r["tags"]) if r["tags"] and r["tags"] != "[]" else [],
    })

output = json.dumps({"words": words, "total": len(words)}, ensure_ascii=False, indent=2)
output_path = PROJECT_ROOT / "docs" / "words.json"
output_path.write_text(output, encoding="utf-8")
print(f"Exported {len(words)} words to {output_path}")
conn.close()
