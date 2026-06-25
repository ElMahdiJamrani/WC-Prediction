import json
from world_cup_groups import GROUPS

with open('models/team_elo_ratings.json', 'r', encoding='utf-8') as f:
    elo_ratings = json.load(f)

all_wc_teams = [team for group in GROUPS.values() for team in group]

print(f"Total teams in groups: {len(all_wc_teams)}")
missing = [t for t in all_wc_teams if t not in elo_ratings]
print(f"Missing from Elo ratings: {len(missing)}")
for team in missing:
    print(f"  - '{team}'")