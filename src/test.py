import random
import seeder

SAMPLE_NAMES = [
    "Viper", "Ghost", "Blitz", "Rogue", 
    "Titan", "Frost", "Drift", "Pulse", 
    "Shade", "Nexus", "Saber", "Talon"
]

RANKS = list(seeder.RANK_MMR_MAPPING.keys())

def generate_random_players(num_players=12):
    players = []

    names_pool = SAMPLE_NAMES.copy()

    for i in range(num_players):
        player = {
            "name": names_pool[i],
            "missing_steam": True,
            "rank" : random.choice(RANKS),
            "subrank" : random.randint(1, 6)
        }

        players.append(player)

    return players

def main():
    mock_players = generate_random_players(12)
    teams = seeder.generate_teams(mock_players)

    print(f"Team A")
    for player in teams.get("team_A"):
        print(f"\t{player['name']} \t({player['rank']} {player['subrank']})")

    print(f"\nTeam B")
    for player in teams.get("team_B"):
        print(f"\t{player['name']} \t({player['rank']} {player['subrank']})")

if __name__ == "__main__":
    main()