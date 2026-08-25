"""Parser for the JSON file given by the Steam API, and gives readable lines for the database."""

from datetime import date

MONTHS = {
    "jan": 1, "janv": 1, "janvier": 1, "january": 1,
    "fev": 2, "févr": 2, "février": 2, "feb": 2, "february": 2,
    "mar": 3, "mars": 3, "march": 3,
    "avr": 4, "avril": 4, "apr": 4, "april": 4,
    "mai": 5, "may": 5,
    "juin": 6, "jun": 6, "june": 6,
    "juil": 7, "juillet": 7, "jul": 7, "july": 7,
    "aout": 8, "août": 8, "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "septembre": 9, "september": 9,
    "oct": 10, "octobre": 10, "october": 10,
    "nov": 11, "novembre": 11, "november": 11,
    "dec": 12, "déc": 12, "décembre": 12, "december": 12,
}

def parse_release_date(date_str, coming_soon=False):
    """Parse the release date string from the Steam API into a date object."""

    if coming_soon:
        return None
    

    without_commas = date_str.replace(",", "")
    without_commas = without_commas.lower()
    words = without_commas.split()
    day = int(words[0])
    month = MONTHS.get(words[1], None)
    if month is None:
        return None
    year = int(words[2])
    return date(year, month, day)

def parse_game(appdetails: dict) -> dict:
    """Parse the game details from the Steam API into a dictionary for the database."""

    game = {}
    game["appid"] = appdetails.get("steam_appid")
    game["name"] = appdetails.get("name")
    game["release_date"] = parse_release_date(appdetails.get("release_date", {}).get("date", ""), appdetails.get("release_date", {}).get("coming_soon", False))
    game["developer"] = appdetails.get("developer", [None])[0]
    game["publisher"] = appdetails.get("publisher", [None])[0]
    game["is_free"] = appdetails.get("is_free", False)
    game["first_seen_at"] = date.today()

    return game
