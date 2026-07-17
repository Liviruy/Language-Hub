# Project Plan

> Language Hub — Personal multilingual language learning platform

## Project Goal

Build a long-term, self-hosted language learning platform centered around a single database.

Supported languages: English, Spanish, French

Future: German, Japanese, Korean, others

The database should become the single source of truth. Everything else should be generated automatically from it: Anki, Website, API, Cloudflare R2 resources.

## Design Principles

1. Database First
2. Automation First
3. Git Version Control
4. Reproducible
5. Open Source Friendly
6. AI Friendly

No manual editing after the pipeline is completed.

## Tech Stack

| Category       | Technology                    |
|----------------|-------------------------------|
| Language       | Python 3.12+                  |
| Database       | SQLite (language.db)          |
| Version Control| Git + GitHub                  |
| Storage        | Cloudflare R2                 |
| Website        | Astro (Cloudflare Pages)      |
| API            | Cloudflare Workers (future)   |
| Anki           | genanki                        |

## Repository Structure

\Language-Hub/
  data/raw/
  data/processed/
  data/audio/
  data/images/
  database/language.db
  scripts/
  exports/
  website/
  docs/
  tests/
  requirements.txt
  README.md
\
## Development Roadmap

Phase 1 — Project Initialization
Phase 2 — Database Design
Phase 3 — Importer
Phase 4 — Dictionary Pipeline
Phase 5 — Audio
Phase 6 — Anki Export
Phase 7 — Cloudflare
Phase 8 — Website
Phase 9 — API
Phase 10 — Automation

## Coding Standards

Python: PEP8, type hints, docstrings, logging, unit tests. No hard-coded paths, use pathlib.

## AI Coding Rules

The AI agent MUST NOT generate the entire project at once. Each phase: Design -> Approval -> Implement -> Test -> Commit -> Validate before next phase.
