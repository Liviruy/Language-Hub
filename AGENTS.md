# Language Hub — Agent Context

## Project Overview
Personal multilingual language learning platform. Database-first, automation-driven.

## Tech Stack
Python 3.12+ | SQLite | Astro | Cloudflare R2/Wrangler | genanki | Edge TTS | GitHub Actions

## Completed Phases
1. ✅ Project Initialization
2. ✅ Database Design
3. ✅ Importer
4. ✅ Dictionary Pipeline
5. ✅ Audio Generation
6. ✅ Anki Export
7. ✅ Cloudflare R2
8. ✅ Website
9. ✅ API
10. ✅ Automation — GitHub Actions pipeline.yml

## Pipeline (auto-runs on git push)
git push → Install deps → Import words → Dictionary → Audio → Anki → R2 upload → Export words.json

## Before pipeline runs — configure GitHub Secrets
Go to GitHub repo → Settings → Secrets and variables → Actions
Add:
- R2_ACCOUNT_ID
- R2_ACCESS_KEY
- R2_SECRET_KEY
- R2_BUCKET (default: language-hub)

## Repository State
| Metric | Value |
|--------|-------|
| Total words | 31 (en:6, es:13, fr:12) |
| With audio | 31 (100%) |
| Anki decks | 10 .apkg |
| R2 files | 41 |
| API endpoints | 37 |
