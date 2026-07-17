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
| TTS | Edge TTS — en:JennyNeural / es:AlvaroNeural / fr:DeniseNeural |
| Anki GUID | Stable: md5(text + lang) |
| Import | Skip duplicates; Audio: skip if file exists |

## Repository State
| Metric | Value |
|--------|-------|
| Total words | 31 (en:6, es:13, fr:12) |
| With definitions | 31 (100%) |
| With IPA | 27 (87%) |
| With audio | 31 (100%) |
| Anki decks | 10 (all languages × levels) |

## Completed Phases
1. ✅ Project Initialization
2. ✅ Database Design
3. ✅ Importer
4. ✅ Dictionary Pipeline
5. ✅ Audio Generation
6. ✅ Anki Export — 10 .apkg decks, audio embedded, stable GUIDs

## Current Phase
### Phase 7 — Cloudflare R2 (next)
Upload audio + exports to R2 bucket. Incremental upload.
Script: scripts/upload_r2.py

## Phase Order
7. Cloudflare R2 upload ← next
8. Website (Astro)
9. API (Cloudflare Workers, optional)
10. Automation (GitHub Actions)

## Git Config
Remote: https://github.com/Liviruy/Language-Hub.git | Branch: main
