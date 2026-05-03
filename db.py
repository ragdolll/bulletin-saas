"""SQLite schema and connection helper for the family assistant."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "family.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS people (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    relationship TEXT,
    spouse TEXT,
    children TEXT,
    lives_in TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS places (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    place TEXT NOT NULL,
    significance TEXT,
    years TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event TEXT NOT NULL,
    date TEXT,
    people_involved TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    date_told TEXT,
    told_by TEXT,
    transcript TEXT,
    summary TEXT,
    topics TEXT
);

CREATE TABLE IF NOT EXISTS pending_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    asked_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    answer TEXT,
    answered_by TEXT
);
"""


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)
