# Architecture

## Overview

Database-First architecture. SQLite is the single source of truth. All downstream artifacts are generated from it.

\language.db (SQLite)
    |
    v
Python Scripts ---> Anki Exports
    |            ---> Cloudflare R2 (audio/images)
    v
Website (Astro)
    | (future)
    v
API (Cloudflare Workers)
\
## Design Principles

1. Database First — design schema before anything else
2. Automation First — everything generated, no manual steps
3. Git Version Control — schema migrations in git
4. Reproducible — fresh clone builds everything
5. Open Source Friendly
6. AI Friendly — structured, deterministic

## Tech Stack

| Component  | Technology         | Purpose              |
|------------|--------------------|----------------------|
| Language   | Python 3.12+       | Pipeline scripts     |
| Database   | SQLite             | Single source of truth|
| TTS        | Edge TTS           | Audio generation     |
| Storage    | Cloudflare R2      | Asset hosting        |
| Anki       | genanki            | Flashcard export     |
| Website    | Astro              | Static dictionary    |
| CI/CD      | GitHub Actions     | Automated pipeline   |

## Key Decisions

- SQLite over PostgreSQL — simplicity, single file, sufficient for personal use
- genanki over AnkiConnect — batch deterministic generation
- Edge TTS over cloud TTS — free, configurable voices
- Astro static over SSR — simpler deploy, no server
- R2 over S3 — Cloudflare ecosystem, no egress fees
