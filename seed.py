"""One-off script to populate the initial tracked apps: python seed.py

Inserts into `games` before `tracked_apps`, because tracked_apps.appid
references games(appid). Safe to re-run: games uses DO NOTHING so a
re-seed never overwrites a name already refreshed from the API with this
placeholder, and tracked_apps uses DO NOTHING because there is nothing
here worth updating on a repeat run.
"""

from steam_pipeline.db import add_tracked_app, connect, seed_game

# (appid, placeholder name) - real names/dates/publishers come from
# appdetails later; this is just enough to satisfy the FK.
SEED_APPS = [
    (730, "Counter-Strike 2"),
    (570, "Dota 2"),
    (440, "Team Fortress 2"),
    (292030, "The Witcher 3: Wild Hunt"),
    (1245620, "Elden Ring"),
]


def main() -> None:
    conn = connect()
    try:
        for appid, name in SEED_APPS:
            seed_game(conn, appid, name)
            add_tracked_app(conn, appid, "manual")
        conn.commit()
        print(f"seeded {len(SEED_APPS)} apps into games/tracked_apps")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
