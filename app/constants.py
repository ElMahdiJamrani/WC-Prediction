import json
import os

def _load_country_codes():
    path = os.path.join(os.path.dirname(__file__), 'country_codes_generated.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

COUNTRY_CODES = _load_country_codes()

def flag_url(team_name, width=80):
    code = COUNTRY_CODES.get(team_name)
    if not code:
        return None
    return f"https://flagcdn.com/w{width}/{code.lower()}.png"