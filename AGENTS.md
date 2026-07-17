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
| Import | Skip duplicates; Audio: skip if file exists |
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

## Completed Phases
1. ✅ Project Initialization
2. ✅ Database Design
3. ✅ Importer
4. ✅ Dictionary Pipeline
5. ✅ Audio Generation
6. ✅ Anki Export
7. ✅ Cloudflare R2 — bucket created, 41 files uploaded incrementally

## Current Phase
### Phase 8 — Website (next)
Goal: Build an Astro dictionary website with search, word pages, audio.

## Phase Order
8. Website (Astro) ← next
9. API (Cloudflare Workers, optional)
10. Automation (GitHub Actions)
