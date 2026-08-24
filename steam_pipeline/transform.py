"""Parser for the JSON file given by the Steam API, and gives readable lines for the database."""

dic = {
    "mai": 5,
    "aug": 8,
    }

def parse_release_date(date_str, coming_soon=False):
    """Parse the release date string from the Steam API into a date object."""

    without_commas = date_str.replace(",", "")
    without_commas = without_commas.lower()
    words = without_commas.split()

    


    if coming_soon:
        return None

