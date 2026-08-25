"""Parser for the JSON file given by the Steam API, and gives readable lines for the database."""

from datetime import date

MONTHS = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}

def parse_release_date(date_str, coming_soon=False):
    """Parse the release date string from the Steam API into a date object."""

    if coming_soon:
        return None
    

    without_commas = date_str.replace(",", "")
    without_commas = without_commas.lower()
    words = without_commas.split()
    if len(words) != 3:
        return None
    day = int(words[0])
    month = MONTHS.get(words[1], None)
    if month is None:
        return None
    year = int(words[2])
    return date(year, month, day)

def parse_game(appdetails: dict) -> dict:
    """Parse the game details from the Steam API into a dictionary for the database."""
    rel = appdetails.get("release_date", {})

    game = {}
    game["appid"] = appdetails.get("steam_appid")
    game["name"] = appdetails.get("name")
    game["release_date"] = parse_release_date(rel.get("date", ""), rel.get("coming_soon", False))
    game["developers"] = appdetails.get("developers", [])
    game["publishers"] = appdetails.get("publishers", [])
    game["is_free"] = appdetails.get("is_free", False)
    game["first_seen_at"] = date.today()
    
    return game
