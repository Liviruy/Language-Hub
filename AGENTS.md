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

## Repository Docs

| File | Purpose |
|------|---------|
| README.md | Project intro |
| PROJECT_PLAN.md | Overall plan |
| ARCHITECTURE.md | System architecture |
| DATABASE.md | Database design |
| ROADMAP.md | Roadmap with flow |
| AGENT_RULES.md | AI agent rules |
| TASKS.md | Current tasks |
| CHANGELOG.md | Version history |
| AGENTS.md | This file — agent context |

## Completed Phases

### Phase 1 ✅ — Project Initialization
- Directory structure: data/(raw,processed,audio,images), database, docs, exports, scripts/(migrations), tests, website
- .gitignore (Python/DB/IDE/OS/venv)
- requirements.txt (requests, edge-tts, genanki, boto3, pytest, sqlite-utils, python-dotenv)
- Virtual env .venv/ with all deps installed
- Pushed to GitHub

### Phase 2 ✅ — Database Design
- Database: `database/language.db` created (36 KB)
- Schema: `languages` + `words` (with JSON fields meanings/audio/tags) + `_migrations`
- Indexes: idx_words_language, idx_words_text, idx_words_cefr
- Migration system: `scripts/migrations/001_initial_schema.sql`
- Init script: `scripts/init_database.py` (auto-runs pending migrations, seeds languages)
- Verify script: `scripts/verify_db.py`
- Seeded languages: en (English), es (Spanish), fr (French)

## Current Phase

### Phase 3 — Importer (next)
Goal: Import vocabulary from CSV/JSON files into the database.

Upcoming scripts:
- `scripts/import_words.py` — read CSV/JSON and insert into words table
- Tests for import logic

See ROADMAP.md for full details.

## Phase Order

3. Importer ← next
4. Dictionary pipeline (Wiktionary API)
5. Audio generation (Edge TTS)
6. Anki export (genanki)
7. Cloudflare R2 upload
8. Website (Astro)
9. API (Cloudflare Workers, optional)
10. Automation (GitHub Actions)

## Agent Workflow

1. Read AGENTS.md + TASKS.md + relevant doc → understand state
2. Present plan → wait for approval
3. Implement (code + test)
4. Validate (run without errors)
5. Commit + push
6. Update AGENTS.md + TASKS.md

## Git Config

- Remote: https://github.com/Liviruy/Language-Hub.git
- Branch: main
- CWD: E:\Language-Hub
