# Development Roadmap

## Phase 1 — Project Initialization
- [ ] Create directory structure
- [ ] Configure Python virtual environment
- [ ] Create requirements.txt
- [ ] Setup .gitignore
- [ ] Verify repository works

## Phase 2 — Database Design
- [ ] Design normalized schema
- [ ] Create init_database.py
- [ ] Create migration system
- [ ] Seed language data

## Phase 3 — Importer
- [ ] CSV importer
- [ ] JSON importer
- [ ] Validation & error reporting

## Phase 4 — Dictionary Pipeline
- [ ] Provider interface
- [ ] IPA, definitions, examples
- [ ] CEFR / frequency

## Phase 5 — Audio
- [ ] Edge TTS integration
- [ ] Cache system (no regeneration)
- [ ] R2 upload

## Phase 6 — Anki Export
- [ ] Custom note model
- [ ] Deck hierarchy per language
- [ ] Incremental updates (stable GUID)

## Phase 7 — Cloudflare
- [ ] R2 bucket config
- [ ] Incremental upload

## Phase 8 — Website
- [ ] Astro project
- [ ] Search, word page, dark mode

## Phase 9 — API
- [ ] Cloudflare Workers REST API

## Phase 10 — Automation
- [ ] GitHub Actions: Build -> Export -> Upload -> Deploy
