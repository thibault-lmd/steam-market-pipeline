"""Throwaway check that the database plumbing works: python check_db.py

Opens a run, closes it. No network. Delete once run.py does this for real.
"""

from steam_pipeline.db import close_run, connect, open_run


def main() -> None:
    conn = connect()
    try:
        run_id = open_run(conn)
        print(f"run {run_id} opened   -> status='running'")

        close_run(conn, run_id, "success", games_processed=0)
        print(f"run {run_id} closed   -> status='success'")
    finally:
        conn.close()


if __name__ == "__main__":
    main()