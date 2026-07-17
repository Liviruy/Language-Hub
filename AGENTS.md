# Language Hub — Agent Context

## Project Overview

Personal multilingual language learning platform. Database-first, automation-driven.

## Tech Stack

Python 3.12+ | SQLite | Astro | Cloudflare R2 | genanki | Edge TTS | GitHub Actions

## Design Decisions (Approved)

| Decision | Choice |
|----------|--------|
| Database schema | Single `words` table with JSON fields for meanings/audio/tags |
| Dictionary source | Wiktionary API (free, covers en/es/fr) |
| TTS | Edge TTS (fallback Google) |
| Anki GUID | Stable: hash(word_text + language_code) |
| Audio | Skip if exists (cache based on DB record) |
| Import duplicates | Skip silently (do not overwrite) |
| CSV columns | text, language (en/es/fr), ipa, cefr, frequency, meanings (JSON), tags |

## Completed Phases

### Phase 1 ✅ — Project Initialization
Directory structure, .gitignore, requirements.txt, .venv/ with all deps.

### Phase 2 ✅ — Database Design
database/language.db with migration system. Tables: languages + words (JSON fields).
scripts/init_database.py — auto-runs migrations, seeds languages.

### Phase 3 ✅ — Importer
scripts/import_words.py — import CSV/JSON into words table. Skip duplicates.
Sample files: data/raw/sample_{en,es,fr}.csv (8 words total imported).

## Current Phase

### Phase 4 — Dictionary Pipeline (next)
Goal: Auto-enrich words with Wiktionary data (IPA, definitions, examples, CEFR).

Scripts to create:
- scripts/dictionary_pipeline.py — query Wiktionary API for each word missing data
- tests/test_dictionary.py

## Phase Order

4. Dictionary pipeline (Wiktionary API) ← next
5. Audio generation (Edge TTS)
6. Anki export (genanki)
7. Cloudflare R2 upload
8. Website (Astro)
9. API (Cloudflare Workers, optional)
10. Automation (GitHub Actions)

## Agent Workflow

1. Read AGENTS.md + TASKS.md + relevant doc
2. Present plan → wait for human approval
3. Implement (code + test)
4. Validate (run without errors)
5. Commit + push
6. Update AGENTS.md + TASKS.md

## Git Config

- Remote: https://github.com/Liviruy/Language-Hub.git
- Branch: main
- CWD: E:\Language-Hub
