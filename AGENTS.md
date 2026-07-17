# Language Hub — Agent Context

## Project Overview

Personal multilingual language learning platform. Database-first, automation-driven.

## Tech Stack

Python 3.12+ | SQLite | Astro | Cloudflare R2 | genanki | Edge TTS | GitHub Actions

## Design Decisions (Approved)

| Decision | Choice |
|----------|--------|
| Database schema | Single `words` table with JSON fields for meanings/audio/tags |
| Dictionary source | FreeDictionary (en) + Wiktionary (es/fr) — multi-provider fallback |
| TTS | Edge TTS (fallback Google) |
| Anki GUID | Stable: hash(word_text + language_code) |
| Audio | Skip if exists (cache based on DB record) |
| Import duplicates | Skip silently |

## Repository State

| Metric | Value |
|--------|-------|
| Total words | 31 (en:6, es:13, fr:12) |
| With definitions | 31 (100%) |
| With IPA | 27 (87%) |
| Sample files | sample_en.csv(4) sample_es.csv(10) sample_fr.csv(10) |

## Completed Phases

### Phase 1 ✅ — Project Initialization
### Phase 2 ✅ — Database Design
### Phase 3 ✅ — Importer
### Phase 4 ✅ — Dictionary Pipeline

## Current Phase

### Phase 5 — Audio Generation (next)
Goal: Generate pronunciation audio via Edge TTS.
Script: `scripts/generate_audio.py`
Covers: en, es, fr voices
Storage: local data/audio/, future R2

## Phase Order
5. Audio generation (Edge TTS) ← next
6. Anki export (genanki)
7. Cloudflare R2 upload
8. Website (Astro)
9. API (Cloudflare Workers, optional)
10. Automation (GitHub Actions)

## Git Config
- Remote: https://github.com/Liviruy/Language-Hub.git
- Branch: main | CWD: E:\Language-Hub
