import pickle
import json
import pandas as pd
import numpy as np
from scipy.stats import poisson as poisson_dist
import streamlit as st

MAX_GOALS = 6

@st.cache_resource
def load_model():
    with open('models/poisson_model.pkl', 'rb') as f:
        return pickle.load(f)

@st.cache_resource
def load_elo_ratings():
    with open('models/team_elo_ratings.json', 'r') as f:
        return json.load(f)

def predict_expected_goals(model, home_elo, away_elo,
                           home_avg_scored=1.3, home_avg_conceded=1.1,
                           away_avg_scored=1.1, away_avg_conceded=1.3,
                           tournament_weight=2.0):
    """
    Returns (lambda_home, lambda_away) expected goal rates.
    Uses all 8 features from the retrained Poisson model.
    Defaults represent average international team form when no form data available.
    """
    home_input = pd.DataFrame([{
        'team_elo':          home_elo,
        'opp_elo':           away_elo,
        'is_home':           1,
        'avg_scored':        home_avg_scored,
        'avg_conceded':      home_avg_conceded,
        'opp_avg_scored':    away_avg_scored,
        'opp_avg_conceded':  away_avg_conceded,
        'tournament_weight': tournament_weight
    }])
    away_input = pd.DataFrame([{
        'team_elo':          away_elo,
        'opp_elo':           home_elo,
        'is_home':           0,
        'avg_scored':        away_avg_scored,
        'avg_conceded':      away_avg_conceded,
        'opp_avg_scored':    home_avg_scored,
        'opp_avg_conceded':  home_avg_conceded,
        'tournament_weight': tournament_weight
    }])
    return model.predict(home_input)[0], model.predict(away_input)[0]
def simulate_match(model, home_team, away_team, elo_ratings,
                   form_data=None, tournament_weight=2.0, rng=None):
    """
    Simulates ONE match using the full 8-feature Poisson model.
    form_data: optional dict mapping team -> (avg_scored, avg_conceded)
    """
    if rng is None:
        rng = np.random.default_rng()

    home_elo = elo_ratings.get(home_team, 1500)
    away_elo = elo_ratings.get(away_team, 1500)

    # Use form data if available, otherwise use defaults
    if form_data and home_team in form_data:
        h_scored, h_conceded = form_data[home_team]
    else:
        h_scored, h_conceded = 1.3, 1.1

    if form_data and away_team in form_data:
        a_scored, a_conceded = form_data[away_team]
    else:
        a_scored, a_conceded = 1.1, 1.3

    lambda_home, lambda_away = predict_expected_goals(
        model, home_elo, away_elo,
        home_avg_scored=h_scored,
        home_avg_conceded=h_conceded,
        away_avg_scored=a_scored,
        away_avg_conceded=a_conceded,
        tournament_weight=tournament_weight
    )

    return int(rng.poisson(lambda_home)), int(rng.poisson(lambda_away))

def build_score_matrix(lambda_home, lambda_away, max_goals=MAX_GOALS):
    """Returns a (max_goals+1) x (max_goals+1) probability matrix."""
    matrix = np.zeros((max_goals + 1, max_goals + 1))
    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            matrix[h, a] = poisson_dist.pmf(h, lambda_home) * poisson_dist.pmf(a, lambda_away)
    return matrix

def win_draw_loss(score_matrix):
    """Returns (p_home_win, p_draw, p_away_win) from a score matrix."""
    max_goals = score_matrix.shape[0] - 1
    p_home, p_draw, p_away = 0, 0, 0
    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            p = score_matrix[h, a]
            if h > a:
                p_home += p
            elif h == a:
                p_draw += p
            else:
                p_away += p
    return p_home, p_draw, p_away
from itertools import combinations

def simulate_group(model, team_names, elo_ratings, rng=None):
    """
    Simulates a full round-robin group (each team plays each other once).
    Returns a sorted list of dicts, one per team, ranked by:
    points -> goal difference -> goals scored (FIFA tiebreaker order).
    """
    if rng is None:
        rng = np.random.default_rng()

    stats = {team: {'points': 0, 'goals_for': 0, 'goals_against': 0, 'played': 0} for team in team_names}

    for home, away in combinations(team_names, 2):
        h_goals, a_goals = simulate_match(model, home, away, elo_ratings, rng=rng)

        stats[home]['goals_for'] += h_goals
        stats[home]['goals_against'] += a_goals
        stats[away]['goals_for'] += a_goals
        stats[away]['goals_against'] += h_goals
        stats[home]['played'] += 1
        stats[away]['played'] += 1

        if h_goals > a_goals:
            stats[home]['points'] += 3
        elif h_goals < a_goals:
            stats[away]['points'] += 3
        else:
            stats[home]['points'] += 1
            stats[away]['points'] += 1

    standings = []
    for team, s in stats.items():
        standings.append({
            'team': team,
            'played': s['played'],
            'points': s['points'],
            'goals_for': s['goals_for'],
            'goals_against': s['goals_against'],
            'goal_diff': s['goals_for'] - s['goals_against'],
        })

    standings.sort(key=lambda x: (-x['points'], -x['goal_diff'], -x['goals_for']))
    return standings
def simulate_all_groups(model, groups_dict, elo_ratings, rng=None):
    """
    Simulates all groups in groups_dict (e.g. {'A': [...], 'B': [...], ...}).
    Returns a dict: {group_letter: standings_list}, where standings_list
    is already sorted 1st->4th by simulate_group().
    """
    if rng is None:
        rng = np.random.default_rng()

    all_standings = {}
    for group_letter, team_names in groups_dict.items():
        standings = simulate_group(model, team_names, elo_ratings, rng)
        all_standings[group_letter] = standings
    return all_standings
def rank_third_place_teams(all_standings):
    """
    Takes the dict of {group_letter: standings_list} from simulate_all_groups,
    extracts the 3rd-placed team from each group, ranks all 12 against each
    other, and returns the top 8 (qualifiers) and bottom 4 (eliminated).
    """
    third_placed = []
    for group_letter, standings in all_standings.items():
        team_data = standings[2].copy()  # index 2 = 3rd place (0-indexed)
        team_data['group'] = group_letter
        third_placed.append(team_data)

    third_placed.sort(key=lambda x: (-x['points'], -x['goal_diff'], -x['goals_for']))

    qualifiers = third_placed[:8]
    eliminated = third_placed[8:]

    return qualifiers, eliminated
def build_round_of_32(group_results, qualifiers_third, rng=None):
    """
    Official FIFA 2026 World Cup Round of 32 bracket.

    Slot definitions (Match 73 → Match 88):
      M73: 2A vs 2B  |  M74: 1E vs 3RD  |  M75: 1F vs 2C  |  M76: 1C vs 2F
      M77: 1I vs 3RD |  M78: 2E vs 2I   |  M79: 1A vs 3RD |  M80: 1L vs 3RD
      M81: 1D vs 3RD |  M82: 1G vs 3RD  |  M83: 2K vs 2L  |  M84: 1H vs 2J
      M85: 1B vs 3RD |  M86: 1J vs 2H   |  M87: 1K vs 3RD |  M88: 2D vs 2G

    3RD slots filled greedily: best-ranked 3rd-place team first,
    skipping any that would cause a same-group rematch.
    """
    winners    = {g: r[0]['team'] for g, r in group_results.items()}
    runners_up = {g: r[1]['team'] for g, r in group_results.items()}
    thirds     = list(qualifiers_third)  # sorted best→worst, each has 'team' & 'group'

    SLOTS = [
        ("2A","2B"),  ("1E","3RD"), ("1F","2C"),  ("1C","2F"),
        ("1I","3RD"), ("2E","2I"),  ("1A","3RD"), ("1L","3RD"),
        ("1D","3RD"), ("1G","3RD"), ("2K","2L"),  ("1H","2J"),
        ("1B","3RD"), ("1J","2H"),  ("1K","3RD"), ("2D","2G"),
    ]

    def resolve(slot):
        return winners[slot[1]] if slot.startswith("1") else runners_up[slot[1]]

    def pick_third(forbidden_group):
        for idx, t in enumerate(thirds):
            if t['group'] != forbidden_group:
                return thirds.pop(idx)['team']
        return thirds.pop(0)['team']   # fallback

    pairings = []
    for home_slot, away_slot in SLOTS:
        if away_slot == "3RD":
            home_team = resolve(home_slot)
            away_team = pick_third(forbidden_group=home_slot[1])
        elif home_slot == "3RD":
            away_team = resolve(away_slot)
            home_team = pick_third(forbidden_group=away_slot[1])
        else:
            home_team = resolve(home_slot)
            away_team = resolve(away_slot)
        pairings.append((home_team, away_team))

    return pairings  # 16 × (home, away) in official bracket order M73→M88


def _build_round_of_32_OLD(group_results, qualifiers_third, rng=None):
    """
    OLD version (randomized). Kept for reference only — not called anywhere.
    Builds Round of 32 pairings respecting FIFA's real constraint:
    no team can face a group-stage opponent in the Round of 32.

    group_results: dict {group_letter: standings_list} from simulate_all_groups
    qualifiers_third: list of qualifying 3rd-place team dicts (with 'group' key)

    NOTE: This is a constraint-respecting approximation of FIFA's official
    Annex C allocation table, not a reproduction of the exact published table
    (which lists 495 precomputed scenarios). It enforces the same real rule
    FIFA uses (no group-stage rematches) using randomized valid pairing.
    """
    if rng is None:
        rng = np.random.default_rng()

    winners = [(g, results[0]['team']) for g, results in group_results.items()]
    runnersup = [(g, results[1]['team']) for g, results in group_results.items()]
    thirds = [(t['group'], t['team']) for t in qualifiers_third]

    def same_group(pair1, pair2):
        return pair1[0] == pair2[0]

    def try_pairing(pool_a, pool_b, max_attempts=200):
        """Randomly pair pool_a with pool_b, avoiding same-group matchups."""
        for _ in range(max_attempts):
            shuffled_b = list(pool_b)
            rng.shuffle(shuffled_b)
            pairing = list(zip(pool_a, shuffled_b))
            if all(not same_group(a, b) for a, b in pairing):
                return pairing
        return list(zip(pool_a, shuffled_b))  # fallback: best-effort after max attempts

    # Step 1: pair winners with third-placed teams (8 winners get this fate)
    winners_shuffled = list(winners)
    rng.shuffle(winners_shuffled)
    winners_vs_third = winners_shuffled[:8]
    winners_vs_runnersup = winners_shuffled[8:]

    pairing_1 = try_pairing(winners_vs_third, thirds)

    # Step 2: remaining 4 winners face runners-up (avoiding same group + already-used runners-up)
    used_runnersup_groups = set()
    pairing_2 = try_pairing(winners_vs_runnersup, runnersup)
    for _, (g, _) in pairing_2:
        used_runnersup_groups.add(g)

    # Step 3: remaining runners-up pair against each other
    remaining_runnersup = [r for r in runnersup if r[0] not in used_runnersup_groups]
    rng.shuffle(remaining_runnersup)
    pairing_3 = []
    for i in range(0, len(remaining_runnersup) - 1, 2):
        pairing_3.append((remaining_runnersup[i], remaining_runnersup[i + 1]))

    all_pairings = pairing_1 + pairing_2 + pairing_3
    # Return just team names, group info no longer needed downstream
    return [(a[1], b[1]) for a, b in all_pairings]
def simulate_knockout_round(model, pairings, elo_ratings, rng=None):
    """
    Simulates one knockout round. pairings is a list of (team_a, team_b) tuples.
    Draws are resolved with a coin flip (representing penalty shootouts).
    Returns: (winners list, results list of dicts with full match detail)
    """
    if rng is None:
        rng = np.random.default_rng()

    winners = []
    results = []

    for team_a, team_b in pairings:
        goals_a, goals_b = simulate_match(model, team_a, team_b, elo_ratings, rng=rng)

        went_to_penalties = False
        if goals_a > goals_b:
            winner = team_a
        elif goals_b > goals_a:
            winner = team_b
        else:
            # Draw -> simulate penalties as a coin flip
            went_to_penalties = True
            winner = team_a if rng.random() < 0.5 else team_b

        winners.append(winner)
        results.append({
            'team_a': team_a, 'team_b': team_b,
            'goals_a': goals_a, 'goals_b': goals_b,
            'winner': winner, 'penalties': went_to_penalties
        })

    return winners, results


def simulate_full_knockout(model, ro32_pairings, elo_ratings, rng=None):
    if rng is None:
        rng = np.random.default_rng()

    round_names = ['Round of 32', 'Round of 16', 'Quarter-finals', 'Semi-finals', 'Final']
    all_rounds = {}

    current_pairings = ro32_pairings
    for round_name in round_names:
        winners, results = simulate_knockout_round(model, current_pairings, elo_ratings, rng=rng)
        all_rounds[round_name] = results

        # Only build next round's pairings if there IS a next round
        if round_name != 'Final':
            current_pairings = [(winners[i], winners[i + 1]) for i in range(0, len(winners), 2)]

    champion = all_rounds['Final'][0]['winner']
    return all_rounds, champion