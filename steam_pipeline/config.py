"""Settings, read once at first import. The only module that reads the environment."""

import os
from pathlib import Path

from dotenv import load_dotenv

# .env sits at the project root, one level above this package.
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)


# --- Database ---

# environ[...] not getenv: fail loudly at import if it is missing.
DATABASE_URL = os.environ["DATABASE_URL"]


# --- Steam API ---

STEAM_STORE_BASE = "https://store.steampowered.com"
STEAM_API_BASE = "https://api.steampowered.com"


# --- Collection ---

# getenv always returns a string, hence the casts.
COUNTRY_CODE = os.getenv("STEAM_CC", "fr")                  # sets prices and currency
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "1.5"))    # seconds between calls
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))             # games between commits