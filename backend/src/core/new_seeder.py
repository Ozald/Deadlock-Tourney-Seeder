import itertools
import requests
from requests.exceptions import RequestException
import os
from pathlib import Path
from urllib.parse import quote
import random

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

UNRANKED_RAW_MMR = RANK_MMR_MAPPING["Acolyte"] + (5 * 500)

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

URL = "https://statlocker.gg/api/public/profile/"
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]

#################################### HELPER METHODS ########################################

def _get_statlocker_api_key():
    api_key = os.getenv("STATLOCKER_API_KEY", "").strip()
    if api_key:
        return api_key

    env_path = REPOSITORY_ROOT / ".env"
    if not env_path.is_file():
        return ""

    for line in env_path.read_text(encoding="utf-8").splitlines():
        name, separator, value = line.partition("=")
        if separator and name.strip() == "STATLOCKER_API_KEY":
            return value.strip().strip("\"'")

    return ""


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

    random.shuffle(player_list)

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

        # Unranked players are considered "average" players to keep balancing fair
        # "Average" = around Acolyte V
        if (rank == "Unranked"):
            rank = "Acolyte"
            subrank = 5
            raw_mmr = UNRANKED_RAW_MMR
        else:
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
        steam_id = str(player["steamID"])
        api_key = _get_statlocker_api_key()
        if not api_key:
            print("STATLOCKER_API_KEY is not set in the environment or repository .env; using unranked fallback.")
            return _seed_unranked_player(player)

        try:
            response = requests.get(
                f"{URL}{quote(steam_id, safe='')}",
                headers={"X-API-Key": api_key},
                timeout=15,
            )
            response.raise_for_status()
            profile = response.json()
        except (RequestException, ValueError):
            print("Statlocker API request failed; using unranked fallback.")
            return _seed_unranked_player(player)

        if isinstance(profile, dict):
            player["profile_pic"] = profile.get("avatarUrl")

        season = profile.get("season1") if isinstance(profile, dict) else None
        casual = season.get("casual") if isinstance(season, dict) else None
        if not isinstance(casual, dict) or not casual.get("ppScore"):
            return _seed_unranked_player(player)

        rank_num = casual.get("rankNumber")
        if not isinstance(rank_num, int):
            return _seed_unranked_player(player)

        tier_num = (rank_num // 10)
        subrank_num = rank_num % 10
        if subrank_num not in ROMAN_NUMERALS:
            return _seed_unranked_player(player)

        tier_name = RANK_TIER_MAPPING.get(tier_num, "Initiate")
        player["rank"] = tier_name
        player["subrank"] = ROMAN_NUMERALS.get(subrank_num, "I")

        last_match = profile.get("last_match") or {}
        
        if not isinstance(last_match, dict):
            last_match = {}
        raw_mmr = last_match.get("player_rank_final_flat_progress")

        if not isinstance(raw_mmr, (int, float)):
            raw_mmr = RANK_MMR_MAPPING.get(tier_name, 1000) + (subrank_num * 500)
        player["raw_mmr"] = raw_mmr

        return bell_curve_weighter(raw_score=raw_mmr)

def _seed_unranked_player(player):
    player["rank"] = "Unranked"
    player["subrank"] = "I"
    player["raw_mmr"] = UNRANKED_RAW_MMR
    return bell_curve_weighter(raw_score=UNRANKED_RAW_MMR)

def bell_curve_weighter(raw_score, min_val=1000, max_val=75000):
    normalized = max(0.0, min(1.0, (raw_score - min_val) / (max_val - min_val)))
    curved = normalized ** 3
    return int(1000 + (curved * 74000))
