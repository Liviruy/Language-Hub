# Language Hub — Agent Context

## Project Overview
Personal multilingual language learning platform. Database-first, automation-driven.

## Tech Stack
Python 3.12+ | SQLite | Astro | Cloudflare R2/Wrangler | genanki | Edge TTS | GitHub Actions

## Repository State
| Metric | Value |
|--------|-------|
| Total words | 31 (en:6, es:13, fr:12) |
| With audio | 31 (100%) |
| Anki decks | 10 .apkg |
| R2 files | 41 |
| API endpoints | 37 static endpoints (list + by language + per word) |

## Completed Phases
1-7. ✅ All complete
8. ✅ Website — Astro page on blog (Firefly theme), search + filters + audio
9. ✅ API — Static JSON endpoints via Astro API routes
   - GET /api/language-hub/words.json — all words
   - GET /api/language-hub/words/{en|es|fr}.json — by language
   - GET /api/language-hub/word/{word}.json — single word lookup

## Current Phase
### Phase 10 — Automation (next)
Goal: GitHub Actions CI/CD pipeline.

Pipeline:
- git push → build scripts → enrich dictionary → generate audio → export anki → upload R2 → rebuild website → deploy

## Phase Order
10. Automation (GitHub Actions) ← next
