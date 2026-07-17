-- 001_initial_schema.sql
-- Phase 2: Create initial database schema
-- Up: applies the schema

CREATE TABLE IF NOT EXISTS languages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    code        TEXT    NOT NULL UNIQUE,  -- en, es, fr
    name        TEXT    NOT NULL          -- English, Spanish, French
);

CREATE TABLE IF NOT EXISTS words (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    language_id INTEGER NOT NULL REFERENCES languages(id),
    text        TEXT    NOT NULL,         -- the word itself
    ipa         TEXT,                     -- pronunciation, e.g. /həˈloʊ/
    cefr        TEXT,                     -- A1, A2, B1, B2, C1, C2
    frequency   INTEGER,                  -- usage frequency rank
    meanings    TEXT    DEFAULT '[]',     -- JSON array of meaning objects
    audio       TEXT    DEFAULT '[]',     -- JSON array of audio objects
    tags        TEXT    DEFAULT '[]',     -- JSON array of tag strings
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_words_language ON words(language_id);
CREATE INDEX idx_words_text     ON words(text);
CREATE INDEX idx_words_cefr     ON words(cefr);

-- Migration tracking table
CREATE TABLE IF NOT EXISTS _migrations (
    version     INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL,
    applied_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);
