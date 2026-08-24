"""Parser for the JSON file given by the Steam API, and gives readable lines for the database."""

from datetime import date

MONTHS = {
    "mai": 5,
    "aug": 8,
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

    


    
