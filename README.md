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

| Path | Contents |
|---|---|
| `sql/schema.sql` | Database schema, applied at volume creation |
| `steam_pipeline/` | Pipeline code (config, API client, transforms, loader) |
| `.env` | Local secrets, never committed |