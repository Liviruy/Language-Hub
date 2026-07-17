import hashlib, json, logging, re, sys, time, requests
from pathlib import Path
p = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(p))
from scripts.init_database import get_db
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

def req(action, params=None):
    try:
        r = requests.post("http://localhost:8765", json={"action":action,"version":6,"params":params or {}}, timeout=10).json()
        return r.get("result") if not r.get("error") else None
    except:
        return None

def fmt(mj):
    try: ms = json.loads(mj) if mj and mj != "[]" else []
    except: ms = []
    parts = []
    for m in ms:
        pos = m.get("pos",""); defn = m.get("definition","")
        tr = m.get("translation",""); exs = m.get("examples",[])
        h = "<div>"
        if pos: h += "<b>" + pos + "</b> "
        h += defn
        if tr: h += " (" + tr + ")"
        for e in exs[:2]:
            if isinstance(e, dict):
                et = e.get("text",""); etr = e.get("translation","")
                h += "<br><i>-- " + et + "</i>"
                if etr: h += " (" + etr + ")"
            elif isinstance(e, str):
                h += "<br><i>-- " + e + "</i>"
        h += "</div>"
        parts.append(h)
    return "\n".join(parts)

def main():
    conn = get_db()
    sql = "select w.text,l.code,w.ipa,w.meanings,w.cefr,w.tags from words w join languages l on w.language_id=l.id where w.meanings is not null and w.meanings!='[]' order by l.code,w.cefr,w.text"
    rows = conn.execute(sql).fetchall()
    conn.close()
    if not rows: log.warning("No words"); return
    if not req("version"): log.error("Cannot connect to Anki"); sys.exit(1)
    log.info("Connected to Anki")

    if "Language Hub Card" not in (req("modelNames") or []):
        req("createModel", {"modelName":"Language Hub Card","inOrderFields":["word","ipa","meanings","audio_tag"],"css":".front{font-size:48px;text-align:center;padding:40px 20px}","cardTemplates":[{"Name":"Language Hub Card","Front":"<div class=front>{{word}}</div>","Back":"<div class=back><div class=word>{{word}}</div><div class=ipa>{{ipa}}</div><hr><div class=meanings>{{meanings}}</div><div class=audio>{{audio_tag}}</div></div>"}]})

    for d in (req("deckNames") or []):
        if "Unknown" in d:
            log.info("Deleting old deck: " + d)
            req("deleteDecks", {"decks":[d],"cardsToo":True})

    lang_names = {"en":"English","es":"Spanish","fr":"French"}
    audio_dir = p / "data" / "audio"
    log.info("Processing " + str(len(rows)) + " words...")
    added = updated = skipped = 0

    for row in rows:
        text = row[0]; lang = row[1]
        level = (row[4] or "Uncategorized").strip().upper() or "Uncategorized"
        deck = "Language Hub::" + lang_names.get(lang, lang) + "::" + level
        if deck not in (req("deckNames") or []): req("createDeck", {"deck":deck})

        try: tags = json.loads(row[5]) if row[5] and row[5] != "[]" else []
        except: tags = []

        safe = re.sub(r"[^\w\s-]", "", text).strip().replace(" ", "_").lower()[:100]
        ap = audio_dir / lang / (safe + ".mp3")
        audio_tag = ""
        if ap.exists():
            aname = "lh_" + lang + "_" + safe + ".mp3"
            r2 = req("storeMediaFile", {"filename":aname,"path":str(ap.resolve()),"skipHash":"exists"})
            if r2 is not None: audio_tag = "[sound:" + aname + "]"

        fields = {"word":text,"ipa":row[2] or "","meanings":fmt(row[3]),"audio_tag":audio_tag}
        nd = {"deckName":deck,"modelName":"Language Hub Card","fields":fields,"tags":tags,"options":{"allowDuplicate":False,"duplicateScope":"deck"}}
        can = req("canAddNotes", {"notes":[nd]})

        if can and can[0]:
            guid = hashlib.md5((text + "_" + lang).lower().strip().encode()).hexdigest()
            req("addNote", {"note":{**nd,"guid":guid}})
            added += 1
            log.info("Added: " + text)
        else:
            q = chr(100) + chr(101) + chr(99) + chr(107) + chr(58) + chr(34) + deck + chr(34) + chr(32) + text
            cards = req("findCards", {"query":q}) or []
            if cards:
                ci = req("cardsInfo", {"cards":cards[:1]})
                if ci:
                    req("updateNoteFields", {"note":{"id":ci[0]["note"],"fields":fields}})
                    updated += 1
                    log.info("Updated: " + text)
                else: skipped += 1
            else: skipped += 1
        time.sleep(0.05)

    print("Total: " + str(len(rows)) + " | Added: " + str(added) + " | Updated: " + str(updated) + " | Skipped: " + str(skipped))

if __name__ == "__main__":
    main()
