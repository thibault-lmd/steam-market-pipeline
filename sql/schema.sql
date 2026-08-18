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

CREATE TABLE genres (
    genre_id      INTEGER PRIMARY KEY,
    name          TEXT NOT NULL UNIQUE
);

CREATE TABLE game_genres (
    appid         INTEGER NOT NULL REFERENCES games(appid) ON DELETE CASCADE,
    genre_id      INTEGER NOT NULL REFERENCES genres(genre_id) ON DELETE CASCADE,
    PRIMARY KEY (appid, genre_id)
);

CREATE TABLE ingestion_runs (
    run_id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at     TIMESTAMPTZ,
    status          TEXT NOT NULL DEFAULT 'running'
                        CHECK (status IN ('running', 'success', 'failed')),
    games_processed INTEGER NOT NULL DEFAULT 0,
    error_message   TEXT
);

CREATE TABLE ingestion_errors (
    error_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id      INTEGER NOT NULL REFERENCES ingestion_runs(run_id) ON DELETE CASCADE,
    appid       INTEGER,
    endpoint    TEXT NOT NULL,         
    http_status SMALLINT,
    message     TEXT,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ON ingestion_errors (run_id);

CREATE TABLE price_history (
    appid            INTEGER NOT NULL REFERENCES games(appid) ON DELETE CASCADE,
    run_id           INTEGER NOT NULL REFERENCES ingestion_runs(run_id) ON DELETE CASCADE,
    is_free          BOOLEAN NOT NULL,
    initial_price    NUMERIC(10, 2),
    final_price      NUMERIC(10, 2),
    discount_percent SMALLINT CHECK (discount_percent BETWEEN 0 AND 100),
    currency         TEXT,
    recorded_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (appid, run_id)
);

CREATE TABLE review_history (
    appid            INTEGER NOT NULL REFERENCES games(appid) ON DELETE CASCADE,
    run_id           INTEGER NOT NULL REFERENCES ingestion_runs(run_id) ON DELETE CASCADE,
    total_positive   INTEGER NOT NULL,
    total_negative   INTEGER NOT NULL,
    total_reviews    INTEGER GENERATED ALWAYS AS (total_positive + total_negative) STORED,
    review_score     SMALLINT CHECK (review_score BETWEEN 0 AND 9),
    review_score_desc TEXT,   
    recorded_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (appid, run_id)
);

CREATE TABLE tracked_apps (
    appid       INTEGER PRIMARY KEY REFERENCES games(appid) ON DELETE CASCADE,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    added_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    source      TEXT   
);

CREATE TABLE player_count_history (
    appid         INTEGER NOT NULL REFERENCES games(appid) ON DELETE CASCADE,
    run_id        INTEGER NOT NULL REFERENCES ingestion_runs(run_id) ON DELETE CASCADE,
    player_count  INTEGER NOT NULL,
    recorded_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (appid, run_id)
);

CREATE TABLE tags (
    tag_id  INTEGER PRIMARY KEY,
    name    TEXT NOT NULL UNIQUE
);

CREATE TABLE game_tags (
    appid   INTEGER NOT NULL REFERENCES games(appid) ON DELETE CASCADE,
    tag_id  INTEGER NOT NULL REFERENCES tags(tag_id) ON DELETE CASCADE,
    votes   INTEGER,
    PRIMARY KEY (appid, tag_id)
);