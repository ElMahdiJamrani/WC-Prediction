import pycountry
import json

# Load your team list from the Elo ratings file (already has all 326 teams)
with open('models/team_elo_ratings.json', 'r', encoding='utf-8') as f:
    elo_ratings = json.load(f)

team_list = sorted(elo_ratings.keys())

# Manual overrides for teams pycountry can't auto-match
# (UK nations, historical countries, common naming differences)
MANUAL_OVERRIDES = {
    'England': 'GB', 'Scotland': 'GB', 'Wales': 'GB', 'Northern Ireland': 'GB',
    'South Korea': 'KR', 'North Korea': 'KP',
    'Ivory Coast': 'CI', "Côte d'Ivoire": 'CI',
    'DR Congo': 'CD', 'Congo': 'CG',
    'United States': 'US', 'USA': 'US',
    'Russia': 'RU', 'Iran': 'IR', 'Syria': 'SY',
    'Bolivia': 'BO', 'Venezuela': 'VE', 'Vietnam': 'VN',
    'Laos': 'LA', 'Brunei': 'BN', 'Czechia': 'CZ', 'Czech Republic': 'CZ',
    # New additions:
    'Republic of Ireland': 'IE',
    'Turkey': 'TR',
    'Cape Verde': 'CV',
    'Macau': 'MO',
}

country_codes = {}
unmatched = []

for team in team_list:
    if team in MANUAL_OVERRIDES:
        country_codes[team] = MANUAL_OVERRIDES[team]
        continue

    # Try exact name match first
    match = pycountry.countries.get(name=team)

    # Try "fuzzy search" if exact match fails
    if not match:
        try:
            results = pycountry.countries.search_fuzzy(team)
            match = results[0] if results else None
        except LookupError:
            match = None

    if match:
        country_codes[team] = match.alpha_2
    else:
        unmatched.append(team)

# Save the generated mapping
with open('app/country_codes_generated.json', 'w', encoding='utf-8') as f:
    json.dump(country_codes, f, indent=2, ensure_ascii=False)

print(f"Matched: {len(country_codes)} teams")
print(f"Unmatched: {len(unmatched)} teams")
print("\nUnmatched teams (will fall back to no flag):")
for team in unmatched:
    print(f"  - {team}")