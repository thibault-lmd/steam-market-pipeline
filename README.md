# steam-market-pipeline

Daily ingestion pipeline tracking price and review history for ~500 Steam games.
Python + PostgreSQL, incremental idempotent loading with run logging.

## Requirements

- Docker Desktop
- Python 3.13 or later

## First-time setup

```powershell
copy .env.example .env      # then fill in POSTGRES_PASSWORD and DATABASE_URL
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
docker compose up -d
```

`sql/schema.sql` is applied automatically when the `pgdata` volume is created,
so the tables exist after the first `docker compose up`.

## Daily use

```powershell
git pull
docker compose up -d        # PostgreSQL on localhost:5432
.venv\Scripts\Activate.ps1
```

To stop the database without losing data: `docker compose stop`.

## Resetting the database

The init scripts only run when the volume is empty. To reapply a modified
schema, destroy the volume first - this deletes all collected history:

```powershell
docker compose down -v
docker compose up -d
```

## Layout

| Path | Responsibility |
|---|---|
| `sql/schema.sql` | Database schema (11 tables), applied automatically at volume creation |
| `steam_pipeline/config.py` | Reads `.env` and exposes settings (`DATABASE_URL`, Steam API bases, `COUNTRY_CODE`, `REQUEST_DELAY`, `BATCH_SIZE`). The only module allowed to read the environment |
| `steam_pipeline/db.py` | Every SQL statement in the project. Connection handling, run bookkeeping (`open_run`/`close_run`), reading tracked apps, upserting history rows |
| `steam_pipeline/steam_client.py` | HTTP calls to the Steam Store and Steam Web API (`appdetails`, `appreviews`, `GetNumberOfCurrentPlayers`). Returns raw JSON, no parsing |
| `steam_pipeline/transform.py` | Pure parsing: turns raw Steam JSON into rows ready for `db.py`. No I/O, so it is testable without network or database |
| `steam_pipeline/run.py` | Orchestrates one ingestion run: opens a run, calls the client, transforms, loads, closes the run. Entry point via `python -m steam_pipeline.run` |
| `seed.py` | One-off script to populate `games` and `tracked_apps` with the initial list of tracked appids |
| `tests/` | Unit tests for `transform.py`, using recorded fixtures instead of live API calls |
| `.env` | Local secrets, never committed |

## Conventions

**1. Network in `steam_client.py`, not `steam_api.py`.**
The module talks to the Steam *Store* API and the Steam *Web* API, which are
two different hosts with different auth/rate-limit behavior — "client" names
the role (a client of Steam's APIs) rather than implying a single API.

**2. Parsing in `transform.py`, singular.**
The module has one job — transform raw JSON into DB-ready rows — so the
singular matches the single responsibility. Plural naming tends to invite
grab-bag utility modules over time.

**3. `run.py` lives inside the package, launched as `python -m steam_pipeline.run`.**
Running it as a module (rather than a loose root-level script) means it goes
through the same import machinery as the rest of the package — relative
imports, `__init__.py` — instead of relying on the script's directory being
on `sys.path` by accident.

**4. One-way dependencies: `run` → `{steam_client, transform, db}` → `config`; `transform` imports nothing else.**
`transform.py` touches neither `httpx` nor `psycopg` nor `config`, so its
tests run with no network and no database — pure functions in, rows out.
Keeping the dependency graph acyclic and one-directional also means any
module's tests can't accidentally depend on `run.py` having run first.

**5. History tables upsert with `ON CONFLICT (appid, run_id) DO UPDATE`; `games` upserts with `DO NOTHING` in `seed.py`.**
History rows are keyed by `(appid, run_id)`, so `DO UPDATE` lets a re-run
of a failed or partial run correct that run's rows instead of erroring or
duplicating. `games`, however, only carries the *current* description of a
game (name, developer, publisher) — a re-seed must not overwrite a name
already refreshed from the API with a hardcoded placeholder, hence
`DO NOTHING`.