"""API calls to the Steam API, and returns the JSON raw data."""

import json 
import httpx 
from .config import COUNTRY_CODE, LANGUAGE, STEAM_API_BASE, STEAM_STORE_BASE


def extract_json(appid: int):
    