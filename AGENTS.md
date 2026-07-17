# Language Hub — Agent Context

## Project Overview

Personal multilingual language learning platform. Database-first, automation-driven.

## Tech Stack

Python 3.12+ | SQLite | Astro | Cloudflare R2 | genanki | Edge TTS | GitHub Actions

## Design Decisions (Approved)

| Decision | Choice |
|----------|--------|
| Database schema | Single `words` table with JSON fields for meanings/audio/tags |
| Dictionary source | Wiktionary API + FreeDictionary API (multi-provider) |
| TTS | Edge TTS (fallback Google) |
| Anki GUID | Stable: hash(word_text + language_code) |
| Audio | Skip if exists (cache based on DB record) |
| Import duplicates | Skip silently |

## Completed Phases

### Phase 1 ✅ — Project Initialization
Dir structure, .gitignore, requirements.txt, .venv with 41 deps.

### Phase 2 ✅ — Database Design
language.db with migration system. Tables: languages + words (JSON fields).
init_database.py — auto-runs migrations, seeds en/es/fr.

### Phase 3 ✅ — Importer
import_words.py — CSV/JSON import with duplicate skip.
Sample files: sample_{en,es,fr}.csv (8 words demo).

### Phase 4 ✅ — Dictionary Pipeline
dictionary_pipeline.py — auto-enriches words via:
  - FreeDictionary (English) — IPA + definitions + examples ✅
  - Wiktionary (Spanish) — definitions via MediaWiki extract ✅
  - Wiktionary (French) — definitions + IPA via MediaWiki extract ✅
Skips words that already have data.

## Current Phase

### Phase 5 — Audio Generation (next)
Goal: Generate pronunciation audio via Edge TTS.

Scripts to create:
- scripts/generate_audio.py — scan DB for words without audio, generate mp3
- Upload to Cloudflare R2 (Phase 7)

## Phase Order

5. Audio generation (Edge TTS) ← next
6. Anki export (genanki)
7. Cloudflare R2 upload
8. Website (Astro)
9. API (Cloudflare Workers, optional)
10. Automation (GitHub Actions)

## Agent Workflow

1. Read AGENTS.md + TASKS.md + relevant doc
2. Present plan → wait for approval
3. Implement (code + test)
4. Validate (run without errors)
5. Commit + push
6. Update AGENTS.md + TASKS.md

## Git Config

- Remote: https://github.com/Liviruy/Language-Hub.git
- Branch: main
- CWD: E:\Language-Hub
