#!/usr/bin/env python3
"""Dictionary pipeline: auto-enrich words with multiple API providers.

Usage:
    python scripts/dictionary_pipeline.py
    python scripts/dictionary_pipeline.py --language en
    python scripts/dictionary_pipeline.py --word develop

Providers:
    1. FreeDictionary (English) ✓ IPA + definitions + examples
    2. Wiktionary (Spanish) ✓ definitions via MediaWiki extract
    3. Wiktionary (French) ✓ definitions + IPA via MediaWiki extract

Tried in order until one succeeds.
"""

import json, logging, re, sys, time
from pathlib import Path
import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.init_database import get_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

REQUEST_DELAY = 0.3
MAX_FRENCH_DEFS = 10  # cap to avoid capturing too many paragraphs
HEADERS = {"User-Agent": "LanguageHub/1.0 (pipeline; https://github.com/Liviruy/Language-Hub)"}


def get_extract(word, subdomain):
    try:
        params = {"action": "query", "titles": word, "prop": "extracts",
                  "explaintext": "1", "format": "json"}
        r = requests.get(f"https://{subdomain}.wiktionary.org/w/api.php",
                         params=params, headers=HEADERS, timeout=15)
        for p in r.json()["query"]["pages"].values():
            if "extract" in p:
                return p["extract"]
    except Exception:
        return None


def parse_spanish(extract):
    meanings, pos = [], ""
    for k, v in {"sustantivo": "noun", "verbo": "verb", "adjetivo": "adjective",
                 "adverbio": "adverb", "interjecci": "interjection"}.items():
        pass  # built inline below
    pm = {"sustantivo": "noun", "verbo": "verb", "adjetivo": "adjective",
          "adverbio": "adverb", "interjecci": "interjection"}
    lines = extract.split("\n"); i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s: i += 1; continue
        m = re.match(r"^=+\s*(.+?)\s*=+$", s)
        if m:
            low = m.group(1).lower()
            for k, v in pm.items():
                if k in low: pos = v; break
            i += 1; continue
        num = re.match(r"^(\d+)\s*$", s)
        if num and pos:
            parts = []; i += 1
            while i < len(lines):
                nl = lines[i].strip()
                if not nl or re.match(r"^\d+\s*$", nl) or re.match(r"^=+", nl): break
                if not any(nl.startswith(x) for x in ("Sin", "Relac", "Ámbit")): parts.append(nl)
                i += 1
            d = re.sub(r"\s+", " ", " ".join(parts)).strip()
            if len(d) > 5: meanings.append({"pos": pos, "definition": d, "translation": "", "examples": []})
            continue
        inline = re.match(r"^(\d+)[\.\s]\s+(.+)", s)
        if inline and pos:
            parts = [inline.group(2).strip()]; i += 1
            while i < len(lines):
                nl = lines[i].strip()
                if not nl or re.match(r"^\d+[\.\s]", nl) or re.match(r"^=+", nl): i -= 1; break
                if not any(nl.startswith(x) for x in ("Sin", "Relac", "Ámbit")): parts.append(nl)
                i += 1
            d = re.sub(r"\s+", " ", " ".join(parts)).strip()
            if len(d) > 5: meanings.append({"pos": pos, "definition": d, "translation": "", "examples": []})
        i += 1
    return meanings


def parse_french(extract):
    meanings, pos = [], ""
    pm = {"nom": "noun", "verbe": "verb", "adjectif": "adjective",
          "adverbe": "adverb", "interjection": "interjection"}
    for line in extract.split("\n"):
        s = line.strip()
        if not s: continue
        m = re.match(r"^=+\s*(.+?)\s*=+$", s)
        if m:
            low = m.group(1).lower()
            for k, v in pm.items():
                if k in low: pos = v; break
            continue
        if pos and not s.startswith("==") and len(s) > 20 and "Note" not in s:
            d = re.sub(r"\s+", " ", s).strip()
            if len(d) > 10 and not any(x["definition"] == d for x in meanings):
                meanings.append({"pos": pos, "definition": d, "translation": "", "examples": []})
                if len(meanings) >= MAX_FRENCH_DEFS:
                    break
    return meanings


def lookup_en(word):
    try:
        r = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}", headers=HEADERS, timeout=10)
        if r.status_code != 200: return None
        entry = r.json()[0]
        ipa = ""
        for p in entry.get("phonetics", []):
            t = p.get("text", "")
            if t and "/" in t: ipa = t; break
        meanings = []
        for m in entry.get("meanings", []):
            pos = m.get("partOfSpeech", "")
            for d in m.get("definitions", []):
                defn = d.get("definition", "").strip()
                if not defn: continue
                ex = d.get("example")
                exs = [ex] if isinstance(ex, str) else (ex if isinstance(ex, list) else [])
                if exs == [None]: exs = []
                meanings.append({"pos": pos, "definition": defn, "translation": "", "examples": exs})
        return {"ipa": ipa, "meanings": meanings} if meanings else None
    except Exception:
        return None


def lookup_es(word):
    e = get_extract(word, "es")
    if not e: return None
    m = parse_spanish(e)
    return {"ipa": "", "meanings": m} if m else None


def lookup_fr(word):
    e = get_extract(word, "fr")
    if not e: return None
    ipa = ""
    ipa_m = re.search(r"\\([a-zɛəeøɔoœyuiɑ̃ɛ̃ɔ̃œ̃ .\047-]+)\\", e[:500])
    if ipa_m: ipa = f"/{ipa_m.group(1)}/"
    m = parse_french(e)
    return {"ipa": ipa, "meanings": m} if m else None


PROVIDERS = {
    "en": [("FreeDictionary", lookup_en), ("Wiktionary", lookup_es)],
    "es": [("Wiktionary", lookup_es)],
    "fr": [("Wiktionary", lookup_fr)],
}


def get_words(conn, language=None, word=None):
    if word:
        return conn.execute(
            "SELECT w.id, w.text, l.code FROM words w JOIN languages l ON w.language_id = l.id WHERE w.text = ?",
            (word,)).fetchall()
    q = "SELECT w.id, w.text, l.code FROM words w JOIN languages l ON w.language_id = l.id WHERE (w.ipa IS NULL OR w.ipa = '' OR w.meanings = '[]')"
    p = []
    if language:
        q += " AND l.code = ?"; p.append(language)
    q += " ORDER BY l.code, w.text"
    return conn.execute(q, p).fetchall()


def update(conn, wid, ipa, meanings):
    ex = conn.execute("SELECT meanings FROM words WHERE id = ?", (wid,)).fetchone()
    if not ex: return False
    try:
        em = json.loads(ex["meanings"]) if ex["meanings"] and ex["meanings"] != "[]" else []
    except Exception:
        em = []
    if not em and meanings:
        conn.execute("UPDATE words SET ipa = ?, meanings = ? WHERE id = ?",
                     (ipa or None, json.dumps(meanings, ensure_ascii=False), wid))
        return True
    return False


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", "-l")
    parser.add_argument("--word", "-w")
    args = parser.parse_args()

    conn = get_db()
    rows = get_words(conn, args.language, args.word)
    if not rows:
        log.info("No words need enrichment."); conn.close(); return

    log.info("Found %d word(s) to enrich", len(rows))
    stats = {"found": 0, "not_found": 0, "skipped": 0, "total": len(rows)}

    for row in rows:
        word, lang = row["text"], row["code"]
        log.info("[%s] %s...", lang, word)
        result, used = None, ""
        for name, fn in PROVIDERS.get(lang, []):
            result = fn(word)
            if result: used = name; break
            time.sleep(REQUEST_DELAY)
        if result and result.get("meanings"):
            if update(conn, row["id"], result.get("ipa", ""), result["meanings"]):
                stats["found"] += 1
                log.info("  ✅ %s: %d def(s), IPA: %s", used, len(result["meanings"]), result.get("ipa") or "N/A")
            else:
                stats["skipped"] += 1
                log.info("  ⏭️  Already has data")
        else:
            stats["not_found"] += 1
            log.info("  ❌ Not found")
        conn.commit(); time.sleep(REQUEST_DELAY)
    conn.close()
    print(f"\n{'='*50}\nDICTIONARY PIPELINE SUMMARY\n{'='*50}")
    print(f"  Total    : {stats['total']}")
    print(f"  Enriched : {stats['found']}")
    print(f"  Skipped  : {stats['skipped']}")
    print(f"  Missed   : {stats['not_found']}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
