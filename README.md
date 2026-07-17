# Language Hub

> Personal multilingual language learning platform

Supported languages: **English** · **Spanish** · **French**

## Overview

Language Hub is a database-first, automation-driven language learning platform.
Everything — Anki decks, website, audio assets — is generated automatically
from a single SQLite database.

## Principles

- **Database First** — single source of truth
- **Automation First** — manual editing not needed after pipeline is built
- **Git Version Control** — full traceability
- **Reproducible** — rebuild everything from scratch

## Tech Stack

| Layer      | Technology      |
|------------|-----------------|
| Language   | Python 3.12+    |
| Database   | SQLite          |
| Website    | Astro           |
| Storage    | Cloudflare R2   |
| Anki       | genanki         |
| TTS        | Edge TTS        |
| CI/CD      | GitHub Actions  |

## Repository

- \data/\ — raw & processed language data, audio, images
- \database/\ — SQLite database
- \scripts/\ — Python pipeline scripts
- \xports/\ — generated Anki decks
- \website/\ — Astro dictionary website
- \docs/\ — documentation
