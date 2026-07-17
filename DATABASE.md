# Database Design

## Philosophy

Single SQLite database (language.db) as the single source of truth. Normalized, no duplicated text.

## Tables

### languages
- id (INTEGER PK)
- code (TEXT UNIQUE) — en, es, fr
- name (TEXT)

### words
- id (INTEGER PK)
- language_id (FK -> languages)
- text (TEXT)
- ipa (TEXT)
- frequency (INTEGER)
- cefr (TEXT) — A1-C2
- created_at (TEXT) — ISO 8601

### meanings
- id (INTEGER PK)
- word_id (FK -> words)
- part_of_speech (TEXT)
- definition (TEXT)
- translation (TEXT)

### examples
- id (INTEGER PK)
- meaning_id (FK -> meanings)
- text (TEXT)
- translation (TEXT)

### audio
- id (INTEGER PK)
- word_id (FK -> words)
- file_path (TEXT) — R2 path
- provider (TEXT) — edge_tts, google
- voice (TEXT)
- created_at (TEXT) — ISO 8601

### tags
- id (INTEGER PK)
- name (TEXT UNIQUE)

### word_tags
- word_id (FK -> words)
- tag_id (FK -> tags)
- Composite PK (word_id, tag_id)

### statistics
- id (INTEGER PK)
- word_id (FK -> words)
- review_count (INTEGER)
- correct_count (INTEGER)
- last_reviewed (TEXT) — ISO 8601

## Indexes
- words.text + words.language_id
- meanings.word_id
- audio.word_id
- tags.name (UNIQUE)

## Migrations
\scripts/migrations/
  001_initial_schema.sql
  002_add_statistics.sql
\Migration table _migrations tracks applied versions.
