# Language Hub — Agent Context

## Project Overview
Personal multilingual language learning platform. Database-first, automation-driven.

## Tech Stack
Python 3.12+ | SQLite | Astro | Cloudflare R2 | genanki | Edge TTS | GitHub Actions

## Design Decisions
| Decision | Choice |
|----------|--------|
| DB schema | Single `words` table with JSON fields |
| Dictionary | FreeDictionary (en) + Wiktionary (es/fr) |
| TTS | Edge TTS — en:Jenny / es:Alvaro / fr:Denise |
| Anki GUID | Stable md5(text + lang) |
| R2 bucket | `language-hub` (auto-created) |
| R2 structure | `audio/{lang}/{word}.mp3`, `exports/{deck}.apkg` |

## Repository State
| Metric | Value |
|--------|-------|
| Total words | 31 (en:6, es:13, fr:12) |
| With definitions | 31 (100%) |
| With audio | 31 (100%) |
| Anki decks | 10 .apkg |
| R2 files | 41 (31 audio + 10 exports) |
| Website | Live on blog: Firefly theme, /bangumi/ |

## Completed Phases
1-7. ✅ All completed
8. ✅ Website — Dictionary page on personal blog (Astro, Firefly theme)
   - Search, language filter, audio playback, dark mode

## Current Phase
### Phase 9 — API (next)
Goal: Cloudflare Workers REST API.
- GET /api/word/{text} — returns word data as JSON
- GET /api/languages — list supported languages

## Phase Order
9. API (Cloudflare Workers, optional) ← next
10. Automation (GitHub Actions)
