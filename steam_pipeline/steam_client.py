"""API calls to the Steam API, and returns JSON raw data."""

import httpx

from .config import COUNTRY_CODE, LANGUAGE, STEAM_STORE_BASE


def extract_json(appid: int) -> dict | None:
    """Fetch raw appdetails JSON for a single appid from the Steam API."""
    url = f"{STEAM_STORE_BASE}/api/appdetails"
    params = {"appids": appid, "cc": COUNTRY_CODE, "l": LANGUAGE}

    response = httpx.get(url, params=params)
    response.raise_for_status()

    rjson = response.json()
    entry = rjson[str(appid)]

    if not entry["success"]:
        return None

    return entry["data"]


