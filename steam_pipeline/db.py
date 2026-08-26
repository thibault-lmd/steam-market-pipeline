"""Database access. Every SQL statement in the project lives here."""

import psycopg

from .config import DATABASE_URL


def load_tracked_apps(conn: psycopg.Connection, limit: int | None = None) -> list[int]:
    """Return active appids, ordered so every run processes them in the same order.

    Without ORDER BY, Postgres is free to return rows in a different order
    each time, which turns "the 47th game crashes" into an unreproducible bug.
    """
    query = "SELECT appid FROM tracked_apps WHERE is_active ORDER BY appid"
    params: tuple = ()
    if limit is not None:
        query += " LIMIT %s"
        params = (limit,)
    rows = conn.execute(query, params).fetchall()
    return [row[0] for row in rows]

def upsert(conn: psycopg.Connection, game: dict) -> dict:
    """Insert or update a game record."""
    row = conn.execute(
        """
        INSERT INTO games (appid, name, release_date, developer, publisher, is_free)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (appid) DO UPDATE SET
            name = EXCLUDED.name,
            release_date = EXCLUDED.release_date,
            developer = EXCLUDED.developer,
            publisher = EXCLUDED.publisher,
            is_free = EXCLUDED.is_free
        RETURNING *
        """,
        (
            game["appid"],
            game["name"],
            game["release_date"],
            ", ".join(game["developers"]) or None,
            ", ".join(game["publishers"]) or None,
            game["is_free"],
        ),
    ).fetchone()
    return row

def seed_game(conn: psycopg.Connection, appid: int, name: str) -> None:
    """Insert a placeholder game record for a tracked app."""
    conn.execute(
        """
        INSERT INTO games (appid, name)
        VALUES (%s, %s)
        ON CONFLICT (appid) DO NOTHING
        """,
        (appid, name),
    )

def add_tracked_app(conn: psycopg.Connection, appid: int, source: str) -> None:
    """Insert a new tracked app. Updates source on conflict; never touches is_active."""

    conn.execute(
        """
        INSERT INTO tracked_apps (appid, source)
        VALUES (%s, %s)
        ON CONFLICT (appid) DO UPDATE SET
        source = EXCLUDED.source

        """,
        (appid, source),
    )

def connect() -> psycopg.Connection:
    """Open a connection. Not a context manager: run.py controls its own commits."""
    return psycopg.connect(DATABASE_URL)


def open_run(conn: psycopg.Connection) -> int:
    """Create the run row and return its id.

    Commits immediately so a later crash still leaves a trace of the attempt.
    """
    row = conn.execute("INSERT INTO ingestion_runs DEFAULT VALUES RETURNING run_id").fetchone()
    conn.commit()
    return row[0]


def close_run(
    conn: psycopg.Connection,
    run_id: int,
    status: str,
    games_processed: int,
    error_message: str | None = None,
) -> None:
    """Mark a run finished, 'success' or 'failed'.

    After an error, call conn.rollback() first: an aborted transaction
    refuses every further command, including this UPDATE.
    """
    conn.execute(
        """
        UPDATE ingestion_runs
           SET status          = %s,
               finished_at     = now(),
               games_processed = %s,
               error_message   = %s
         WHERE run_id = %s
        """,
        (status, games_processed, error_message, run_id),
    )
    conn.commit()