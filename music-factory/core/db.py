"""Schema e conexão do catálogo. Zero dependências externas."""

import sqlite3
from pathlib import Path

DEFAULT_DB = "~/.music-factory/factory.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS tracks (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    slug          TEXT UNIQUE NOT NULL,
    niche         TEXT NOT NULL,
    title         TEXT NOT NULL,
    theme         TEXT,
    mood          TEXT DEFAULT 'retain',
    style_prompt  TEXT,
    exclude_styles TEXT,
    lyrics_path   TEXT,
    duration_sec  INTEGER,
    duration_estimated INTEGER DEFAULT 1,
    status        TEXT DEFAULT 'draft',
    audio_path    TEXT,
    video_url     TEXT,
    vph           REAL DEFAULT 0,
    created_at    TEXT NOT NULL,
    published_at  TEXT
);

CREATE TABLE IF NOT EXISTS playlists (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    slug         TEXT UNIQUE NOT NULL,
    niche        TEXT NOT NULL,
    title        TEXT,
    target_sec   INTEGER,
    total_sec    INTEGER,
    status       TEXT DEFAULT 'planned',
    created_at   TEXT NOT NULL,
    published_at TEXT,
    video_url    TEXT
);

CREATE TABLE IF NOT EXISTS playlist_tracks (
    playlist_id INTEGER NOT NULL REFERENCES playlists(id) ON DELETE CASCADE,
    track_id    INTEGER NOT NULL REFERENCES tracks(id),
    position    INTEGER NOT NULL,
    start_sec   INTEGER NOT NULL,
    PRIMARY KEY (playlist_id, position)
);

-- anti-repetição de faixa
CREATE TABLE IF NOT EXISTS usage (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    track_id    INTEGER NOT NULL REFERENCES tracks(id),
    playlist_id INTEGER REFERENCES playlists(id),
    used_at     TEXT NOT NULL
);

-- anti-repetição de tema (versículo/assunto)
CREATE TABLE IF NOT EXISTS theme_usage (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    niche   TEXT NOT NULL,
    theme   TEXT NOT NULL,
    used_at TEXT NOT NULL
);

-- anti-repetição de gancho de título
CREATE TABLE IF NOT EXISTS hook_usage (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    niche   TEXT NOT NULL,
    hook    TEXT NOT NULL,
    used_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tracks_niche  ON tracks(niche, status);
CREATE INDEX IF NOT EXISTS idx_usage_track   ON usage(track_id, used_at);
CREATE INDEX IF NOT EXISTS idx_theme_niche   ON theme_usage(niche, used_at);
CREATE INDEX IF NOT EXISTS idx_hook_niche    ON hook_usage(niche, used_at);
"""


def connect(db_path: str = DEFAULT_DB) -> sqlite3.Connection:
    """Abre (e cria, se preciso) o banco. Retorna conexão com row_factory."""
    path = Path(db_path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    conn.commit()
    return conn
