import itertools
import requests
from requests.exceptions import RequestException

RANK_MMR_MAPPING = {
    "Initiate" : 1000,
    "Seeker" : 8000,
    "Acolyte" : 15000,
    "Sentinel": 22000,
    "Mystic" : 29000,
    "Ritualist" : 36000,
    "Emissary" : 43000,
    "Oracle" : 50000,
    "Phantom" : 57000,
    "Ascendant" : 64000,
    "Eternus" : 71000
}

RANK_TIER_MAPPING = {
    1: "Initiate",
    2: "Seeker",
    3: "Acolyte",
    4: "Sentinel",
    5: "Mystic",
    6: "Ritualist",
    7: "Emissary",
    8: "Oracle",
    9: "Phantom",
    10: "Ascendant",
    11: "Eternus"
}

ROMAN_NUMERALS = {
    1: "I", 
    2: "II", 
    3: "III", 
    4: "IV", 
    5: "V", 
    6: "VI"
}

ROMAN_TO_INT = {
    "I"     : 1,
    "II"    : 2,
    "III"   : 3,
    "IV"    : 4,
    "V"     : 5,
    "VI"    : 6
}

#################################### HELPER METHODS ########################################

def generate_teams(player_list):
    if not player_list:
        raise ValueError("Player list is empty.")

    if len(player_list) % 2 != 0:
        raise ValueError("Player count must be even to make balanced teams.")

    if len(player_list) > 12:
        raise ValueError("Maximum player limit for balancing is 12.")

    for player in player_list:
        player["weighted_mmr"] = seed_player(player)

    best_split = None       # Stores the best possible seeding for the tourney
    smallest_diff = float("inf")

    for teamA in itertools.combinations(player_list, len(player_list) // 2):
        teamB = [player for player in player_list if player not in teamA]

        sumA = sum(player["weighted_mmr"] for player in teamA)
        sumB = sum(player["weighted_mmr"] for player in teamB)

        diff = abs(sumA - sumB)

        if diff < smallest_diff:
            smallest_diff = diff
            best_split = {
                "team_A" : teamA,
                "team_B" : teamB,
                "total_mmr_A" : sumA,
                "total_mmr_B" : sumB,
                "diff" : diff
            }

            # Found best split possible
            if diff == 0:
                break

    return best_split

def seed_player(player):
    if "steamID" not in player.keys() or not player["steamID"]:
        rank = player.get("rank", "Initiate")
        subrank = player.get("subrank", 1)

        # If string, convert to integer
        if isinstance(subrank, str):
            subrank = ROMAN_TO_INT.get(subrank.upper(), 1)
        else:
            subrank = int(subrank)

        raw_mmr = RANK_MMR_MAPPING.get(rank, 1000) + (subrank * 500)
        player["subrank"] = ROMAN_NUMERALS.get(subrank, "I") 
        player["raw_mmr"] = raw_mmr

        return bell_curve_weighter(raw_score=raw_mmr)
    else:
        steamID = player["steamID"]
        try:
            response = requests.get(f"https://api.deadlock-api.com/v1/players/{steamID}/rank", timeout=5)

            if response.status_code != 200:
                raise RequestException("API Request failed.")

            response = response.json()
        except (RequestException, ValueError):
            player["rank"] = "Unranked"
            player["subrank"] = "I"
            player["raw_mmr"] = 1000

            return bell_curve_weighter(1000)
        
        badge = response.get("badge")
        if not badge:
            player["rank"] = "Unranked"
            player["subrank"] = "I"
            player["raw_mmr"] = 1000

            return bell_curve_weighter(1000)

        tier_num = response.get("rank", 1)
        subrank_num = response.get("subrank", 1)

        tier_name = RANK_TIER_MAPPING.get(tier_num, "Initiate")
        player["rank"] = tier_name
        player["subrank"] = ROMAN_NUMERALS.get(subrank_num, "I")

        last_match = response.get("last_match") or {}
        raw_mmr = last_match.get("player_rank_final_flat_progress", 1000)
        player["raw_mmr"] = raw_mmr

        return bell_curve_weighter(raw_score=raw_mmr)

def bell_curve_weighter(raw_score, min_val=1000, max_val=75000):
    normalized = max(0.0, min(1.0, (raw_score - min_val) / (max_val - min_val)))
    curved = normalized ** 1.8
    return int(1000 + (curved * 74000))
