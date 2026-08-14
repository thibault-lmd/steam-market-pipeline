-- Steam market pipeline — database schema

CREATE TABLE games (
    appid         INTEGER PRIMARY KEY,
    name          TEXT NOT NULL,
    release_date  DATE,
    developer     TEXT,
    publisher     TEXT,
    is_free       BOOLEAN NOT NULL DEFAULT FALSE,
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT now()
);