"""Throwaway script: records real Steam API responses as test fixtures.

Run once: python fetch_fixtures.py
Saves raw JSON, unparsed, so transform.py tests exercise the real response
shape instead of a hand-written guess at it. Delete once fixtures exist
and are committed - re-run only if the API shape changes.
"""

import json
import time
from pathlib import Path

import httpx

from steam_pipeline.config import COUNTRY_CODE, LANGUAGE, REQUEST_DELAY, STEAM_API_BASE, STEAM_STORE_BASE

FIXTURES_DIR = Path(__file__).parent / "tests" / "fixtures"

FETCHES = [
    ("appdetails_292030", f"{STEAM_STORE_BASE}/api/appdetails", {"appids": 292030, "cc": COUNTRY_CODE, "l": LANGUAGE}),
    ("appdetails_730", f"{STEAM_STORE_BASE}/api/appdetails", {"appids": 730, "cc": COUNTRY_CODE, "l": LANGUAGE}),
    ("appdetails_invalid", f"{STEAM_STORE_BASE}/api/appdetails", {"appids": 999999999, "cc": COUNTRY_CODE, "l": LANGUAGE}),
    ("appreviews_292030", f"{STEAM_STORE_BASE}/appreviews/292030", {"json": 1, "num_per_page": 0, "language": "all"}),
    ("players_292030", f"{STEAM_API_BASE}/ISteamUserStats/GetNumberOfCurrentPlayers/v1/", {"appid": 292030}),
]


def main() -> None:
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    for i, (name, url, params) in enumerate(FETCHES):
        if i > 0:
            time.sleep(REQUEST_DELAY)  # stay under the ~200 req/5min store limit

        response = httpx.get(url, params=params)
        response.raise_for_status()

        out_path = FIXTURES_DIR / f"{name}.json"
        out_path.write_text(json.dumps(response.json(), indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"saved {out_path}")


if __name__ == "__main__":
    main()
