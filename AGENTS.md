# Language Hub — Agent Context

## Project Overview

Personal multilingual language learning platform. Database-first, automation-driven.

## Tech Stack

Python 3.12+ | SQLite | Astro | Cloudflare R2 | genanki | Edge TTS | GitHub Actions

## Design Decisions (Approved)

| Decision | Choice |
|----------|--------|
| Database schema | Single `words` table with JSON fields |
| Dictionary | FreeDictionary (en) + Wiktionary (es/fr) |
| TTS | Edge TTS — en:JennyNeural / es:AlvaroNeural / fr:DeniseNeural |
| Anki GUID | Stable hash(word_text + language_code) |
| Import duplicates | Skip; Audio: skip if exists |
| Audio storage | `data/audio/{lang}/{word}.mp3`; DB records JSON path |

## Repository State

| Metric | Value |
|--------|-------|
| Total words | 31 (en:6, es:13, fr:12) |
| With definitions | 31 (100%) |
| With IPA | 27 (87%) |
| With audio | 31 (100%) |
| Audio files | 36 mp3 (278 KB) |

## Completed Phases

### Phase 1 ✅ — Project Initialization
### Phase 2 ✅ — Database Design
### Phase 3 ✅ — Importer
### Phase 4 ✅ — Dictionary Pipeline
### Phase 5 ✅ — Audio Generation
Script: `scripts/generate_audio.py` — Edge TTS, all 31 words, 0 failures.

## Current Phase

### Phase 6 — Anki Export (next)
Goal: Generate .apkg flashcard decks per language/level.
Script: `scripts/export_anki.py`
Requirements: custom note model, media support, stable GUID, deck hierarchy.

## Phase Order
6. Anki export (genanki) ← next
7. Cloudflare R2 upload
8. Website (Astro)
9. API (Cloudflare Workers, optional)
10. Automation (GitHub Actions)

## Agent Workflow
1. Read AGENTS.md + TASKS.md + relevant doc
2. Present plan → wait for approval
3. Implement → test → validate
4. Commit + push
5. Update AGENTS.md + TASKS.md

## Git Config
- Remote: https://github.com/Liviruy/Language-Hub.git | Branch: main
