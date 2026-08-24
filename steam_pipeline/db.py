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