"""API calls to the Steam API, and returns JSON raw data."""

import httpx
import time 

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception 
from .config import COUNTRY_CODE, LANGUAGE, STEAM_API_BASE, STEAM_STORE_BASE, REQUEST_DELAY


def _is_retryable(exception: Exception) -> bool:
    """Return True if the exception is retryable."""
    if isinstance(exception, httpx.RequestError):
        return True
    if isinstance(exception, httpx.HTTPStatusError) and exception.response.status_code in {429, 500, 502, 503, 504}:
        return True
    return False

def extract_json(appid: int) -> dict | None:
    """Fetch raw appdetails JSON for a single appid from the Steam API."""
    url = f"{STEAM_STORE_BASE}/api/appdetails"
    params = {"appids": appid, "cc": COUNTRY_CODE, "l": LANGUAGE}

    rjson = _get(url, params)
    entry = rjson[str(appid)]

    if not entry["success"]:
        return None

    return entry["data"]

def fetch_prices(appids: list[int]) -> dict[int, dict | None]:
    """Fetch price_overview for a batch of appids from the Steam API."""
    url = f"{STEAM_STORE_BASE}/api/appdetails"
    params = {
        "appids": ",".join(str(appid) for appid in appids),
        "cc": COUNTRY_CODE,
        "l": LANGUAGE,
        "filters": "price_overview",
    }

    rjson = _get(url, params)

    prices = {}
    for appid in appids:
        entry = rjson[str(appid)]
        if not entry["success"] or not entry["data"]:
            prices[appid] = None
        else:
            prices[appid] = entry["data"].get("price_overview")
    return prices

def fetch_reviews(appid: int) -> dict | None:
    """Fetch review summary for a single appid from the Steam API."""
    url = f"{STEAM_STORE_BASE}/appreviews/{appid}"
    params = {"json": 1, "num_per_page": 0, "language": "all"}

    rjson = _get(url, params)

    if not rjson["success"]:
        return None

    return rjson["query_summary"]


def fetch_player_count(appid: int) -> int | None:
    """Fetch current player count for a single appid from the Steam API."""
    url = f"{STEAM_API_BASE}/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
    params = {"appid": appid}

    try:
        rjson = _get(url, params)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        raise
    
    response = rjson["response"]

    if response["result"] != 1:
        return None

    return response["player_count"]


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10), retry=retry_if_exception(_is_retryable))
def _get(url: str, params: dict) -> dict:
    time.sleep(REQUEST_DELAY)
    response = httpx.get(url, params=params)
    response.raise_for_status()
    return response.json()

