import itertools
import requests

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

#################################### HELPER METHODS ########################################

def generate_teams(player_list):
    if not player_list:
        raise ValueError("Player list is empty.")

    if len(player_list) % 2 != 0:
        raise ValueError("Player count must be even to make balanced teams.")

    for player in player_list:
        player["mmr"] = seed_player(player)

    best_split = None       # Stores the best possible seeding for the tourney
    smallest_diff = float("inf")

    for teamA in itertools.combinations(player_list, len(player_list) // 2):
        teamB = [player for player in player_list if player not in teamA]

        sumA = sum(player["mmr"] for player in teamA)
        sumB = sum(player["mmr"] for player in teamB)

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
    if player["missing_steam"]:
        raw_mmr = RANK_MMR_MAPPING.get(player.get("rank"), 1000) + (RANK_MMR_MAPPING.get(player.get("subrank"), 1) * 500)
        player["raw_mmr"] = raw_mmr

        return bell_curve_weighter(raw_score=raw_mmr)
    else:
        steamID = player["steamID"]
        response = requests.get(f"https://api.deadlock-api.com/v1/players/{steamID}/rank").json()

        badge = response.get("badge")
        if not badge:
            player["rank"] = "Unranked"
            return 1000

        tier_num = response.get("rank")
        subrank = response.get("subrank")

        tier_name = RANK_TIER_MAPPING.get(tier_num, "Initiate")
        player["rank"] = f"{tier_name}" 
        player["subrank"] = f"{ROMAN_NUMERALS.get(subrank)}" 

        print(f"Fetched current rank for {player.get('name')}")

        raw_mmr = response["last_match"]["player_rank_final_flat_progress"]
        player["raw_mmr"] = raw_mmr

        return bell_curve_weighter(raw_score=raw_mmr)

def bell_curve_weighter(raw_score, min_val=1000, max_val=75000):
    normalized = max(0.0, min(1.0, (raw_score - min_val) / (max_val - min_val)))
    curved = normalized ** 1.8
    return int(1000 + (curved * 74000))
