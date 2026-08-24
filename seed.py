"""One-off script to populate the initial tracked apps: python seed.py

Inserts into `games` before `tracked_apps`, because tracked_apps.appid
references games(appid). Safe to re-run: games uses DO NOTHING so a
re-seed never overwrites a name already refreshed from the API with this
placeholder, and tracked_apps uses DO NOTHING because there is nothing
here worth updating on a repeat run.
"""

from steam_pipeline.db import connect

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
            conn.execute(
                """
                INSERT INTO games (appid, name)
                VALUES (%s, %s)
                ON CONFLICT (appid) DO NOTHING
                """,
                (appid, name),
            )
            conn.execute(
                """
                INSERT INTO tracked_apps (appid, source)
                VALUES (%s, 'manual')
                ON CONFLICT (appid) DO NOTHING
                """,
                (appid,),
            )
        conn.commit()
        print(f"seeded {len(SEED_APPS)} apps into games/tracked_apps")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
