# Language Hub — Agent Context

## Project Overview

Personal multilingual language learning platform. Database-first, automation-driven.
Database is the single source of truth; everything else (Anki, website, audio) is generated from it.

## Tech Stack

- Python 3.12+ | SQLite | Astro | Cloudflare R2 | genanki | Edge TTS | GitHub Actions
- Virtual env: \.venv/\ | Dependencies: equirements.txt
## Design Decisions (Approved)

| Decision | Choice |
|----------|--------|
| Database schema | Single \words\ table with JSON fields for meanings/audio/tags (not full normalization) |
| Dictionary source | Wiktionary API (free, covers en/es/fr) |
| TTS | Edge TTS (fallback Google) |
| Anki generation | genanki with stable GUID (hash of word_text + language_code) |
| Audio regeneration | Skip if already exists (cache based on database record) |

## Repository Documents

| File | Purpose |
|------|---------|
| README.md | Project intro |
| PROJECT_PLAN.md | Overall plan & specs |
| ARCHITECTURE.md | System architecture |
| DATABASE.md | Database schema |
| ROADMAP.md | Full roadmap with flow explanation |
| AGENT_RULES.md | AI agent working rules |
| TASKS.md | Current task checklist |
| CHANGELOG.md | Version history |

## Completed Phases

### Phase 1 — Project Initialization ✅

- Directory structure created (data/raw, data/processed, data/audio, data/images, database, docs, exports, scripts, tests, website)
- .gitignore configured (Python/DB/IDE/OS/venv patterns)
- requirements.txt with all dependencies
- Python virtual environment .venv/ created, all deps installed
- Verified: Python 3.13, all imports OK, pytest 9.1.1
- Pushed to GitHub

## Current Phase

### Phase 2 — Database Design (in progress)

Goal: Create \database/language.db\ with migration system.

**Tables:**
- \languages\ — id, code (en/es/fr), name
- \words\ — id, language_id (FK), text, ipa, cefr, frequency, meanings (JSON), audio (JSON), tags (JSON), created_at, updated_at

**Migrations:** \scripts/migrations/001_initial_schema.sql\ — schema SQL
Migration tracker table: \_migrationsInit script: \scripts/init_database.py
## Phase Order (not started)

3. Importer (CSV/JSON to DB)
4. Dictionary pipeline (Wiktionary API)
5. Audio generation (Edge TTS)
6. Anki export (genanki)
7. Cloudflare R2 upload
8. Website (Astro)
9. API (Cloudflare Workers, optional)
10. Automation (GitHub Actions)

## Agent Workflow

1. Read AGENTS.md + TASKS.md + relevant doc to understand current state
2. Present plan before coding
3. Wait for human approval
4. Implement (code + test)
5. Validate (run without errors)
6. Commit and push
7. Mark tasks complete, update AGENTS.md

## Git Config

- Remote: https://github.com/Liviruy/Language-Hub.git
- Branch: main (up-to-date with origin/main)
- Docs directory: E:\Language-Hub
