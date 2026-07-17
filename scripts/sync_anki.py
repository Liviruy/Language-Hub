#!/usr/bin/env python3
"""Sync words from DB to Anki via AnkiConnect.
Adds new cards, UPDATES existing cards, handles Unknown->Uncategorized rename."""

import hashlib, json, logging, re, sys, time
from pathlib import Path
import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.init_database import get_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

ANKI_URL = "http://localhost:8765"
LANG_NAMES = {"en":"English","es":"Spanish","fr":"French"}
AUDIO_DIR = PROJECT_ROOT / "data" / "audio"

def a(action, params=None):
    try:
        r = requests.post(ANKI_URL, json={"action":action,"version":6,"params":params or {}}, timeout=10).json()
        return r.get("result") if not r.get("error") else None
    except: return None

def fmt(mj):
    try: ms = json.loads(mj) if mj and mj != "[]" else []
    except: ms = []
    parts = []
    for m in ms:
        pos, defn, tr, exs = m.get("pos",""), m.get("definition",""), m.get("translation",""), m.get("examples",[])
        h = f"<div>{'<b>'+pos+'</b> ' if pos else ''}{defn}{' <span style=\"color:#666\">（'+tr+'）</span>' if tr else ''}"
        for e in exs[:2]: h += f"<br><i>— {e}</i>"
        h += "</div>"
        parts.append(h)
    return "\n".join(parts)

def guid(text, lang):
    return hashlib.md5(f"{text}_{lang}".lower().strip().encode()).hexdigest()

def store_audio(word, lang):
    safe = re.sub(r"[^\w\s-]", "", word).strip().replace(" ", "_").lower()[:100]
    ap = AUDIO_DIR / lang / f"{safe}.mp3"
    if not ap.exists(): return ""
    fn = f"lh_{lang}_{safe}.mp3"
    return f"[sound:{fn}]" if a("storeMediaFile", {"filename":fn,"path":str(ap.resolve()),"skipHash":"exists"}) is not None else ""

def main():
    conn = get_db()
    rows = conn.execute("""SELECT w.text,l.code as lang,w.ipa,w.meanings,w.cefr,w.tags FROM words w JOIN languages l ON w.language_id=l.id WHERE w.meanings IS NOT NULL AND w.meanings!='[]' ORDER BY l.code,w.cefr,w.text""").fetchall()
    conn.close()
    if not rows: return log.warning("No words.")
    if not a("version"): log.error("Open Anki first."); sys.exit(1)
    log.info("Anki connected")
    if "Language Hub Card" not in (a("modelNames") or []):
        a("createModel", {"modelName":"Language Hub Card","inOrderFields":["word","ipa","meanings","audio_tag"],"css":".front{font-size:48px;text-align:center;padding:40px 20px}.back{font-size:18px;line-height:1.6}.word{font-size:32px;font-weight:bold}.ipa{font-size:20px;color:#666;font-family:monospace}","cardTemplates":[{"Name":"Language Hub Card","Front":"<div class=\"front\">{{word}}</div>","Back":"<div class=\"back\"><div class=\"word\">{{word}}</div><div class=\"ipa\">{{ipa}}</div><hr><div class=\"meanings\">{{meanings}}</div><div class=\"audio\">{{audio_tag}}</div></div>"}]})
    
    # Delete old Unknown decks
    all_decks = a("deckNames") or []
    for d in all_decks:
        if "::Unknown" in d or d.endswith(" Unknown"):
            log.info("Removing old deck: %s", d)
            a("deleteDeck", {"decks":[d],"cardsToo":True})
    
    log.info("Syncing %d word(s)...", len(rows))
    stats = {"added":0,"updated":0,"skipped":0}
    
    for row in rows:
        text, lang = row["text"], row["lang"]
        level = (row["cefr"] or "Uncategorized").strip().upper() or "Uncategorized"
        deck = f"Language Hub::{LANG_NAMES.get(lang,lang)}::{level}"
        if deck not in (a("deckNames") or []): a("createDeck", {"deck":deck})
        
        tags = []
        try: tags = json.loads(row["tags"]) if row["tags"] and row["tags"] != "[]" else []
        except: pass
        
        audio_tag = store_audio(text, lang)
        fields = {"word":text,"ipa":row["ipa"] or "","meanings":fmt(row["meanings"]),"audio_tag":audio_tag}
        nd = {"deckName":deck,"modelName":"Language Hub Card","fields":fields,"tags":tags,"options":{"allowDuplicate":False,"duplicateScope":"deck"}}
        
        can_add = a("canAddNotes", {"notes":[nd]})
        if can_add and can_add[0]:
            a("addNote", {"note":{**nd,"guid":guid(text,lang)}})
            stats["added"] += 1
            log.info("  ✅ Added: %s", text)
        else:
            # Find existing and update
            cards = a("findCards", {"query":f'"deck:{deck}" "{text}"'}) or []
            if cards:
                ci = a("cardsInfo", {"cards":cards[:1]})
                if ci:
                    a("updateNoteFields", {"note":{"id":ci[0]["note"],"fields":fields}})
                    stats["updated"] += 1
                    log.info("  🔄 Updated: %s", text)
                else: stats["skipped"] += 1
            else: stats["skipped"] += 1
        time.sleep(0.05)
    
    print(f"\nTotal: {len(rows)} | Added: {stats['added']} | Updated: {stats['updated']} | Skipped: {stats['skipped']}")
    print("Check Anki!")

if __name__ == "__main__":
    main()
