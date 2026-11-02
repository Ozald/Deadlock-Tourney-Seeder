import os
import streamlit as st
import pandas as pd
import requests
from warnings import deprecated

st.set_page_config(page_title="Deadlock Tourney Seeder",layout="wide")

API_BASE_URL = os.getenv("DEADLOCK_SEEDER_API_URL", "").rstrip("/")

RANK_OPTIONS = [
    "Initiate",
    "Seeker",
    "Acolyte",
    "Sentinel",
    "Mystic",
    "Ritualist",
    "Emissary",
    "Oracle",
    "Phantom",
    "Ascendant",
    "Eternus"
]

SUBRANK_OPTIONS = {
    "I"     : 1,
    "II"    : 2,
    "III"   : 3,
    "IV"    : 4,
    "V"     : 5,
    "VI"    : 6
}

#################################### HELPER METHODS ########################################

# Renders a player card with name and rank/URL inputs.
@deprecated("This function is deprecated and will be removed in future versions.")
def render_player_card(index, column):
    curr_expander = column.expander(f"Player {index+1}", expanded=True)
    with curr_expander:

        curr_expander.text_input(label="Name", key=f"player_name_{index}")
        curr_expander.text_input(label="Steam ID", key=f"player_steamID_{index}")
        curr_expander.selectbox(label="Rank", options=RANK_OPTIONS, key=f"player_rank_{index}")
        curr_expander.selectbox(label="Division", options=SUBRANK_OPTIONS.keys(), key=f"player_subrank_{index}")

# Renders the generated teams in the Streamlit app.
def render_teams(teams):
    st.subheader(f"Team A")
    for player in teams.get("team_A"):
        st.write(f"{player['name']} ({player['rank']} {player['subrank']})")

    st.subheader(f"Team B")
    for player in teams.get("team_B"):
        st.write(f"{player['name']} ({player['rank']} {player['subrank']})")

# Generates a list of player data dictionaries from the provided player table.
def generate_player_data(player_table):
    player_list = []
    
    for _, row in player_table.iterrows():
        name = row.get("name")
        if not name or str(name).strip() == "":
            raise ValueError("Missing name found")

        player_info = {"name": str(name).strip()}

        # Check for Steam ID first, if not present, use rank and subrank
        steam_id = row.get("steamID")
        if not pd.isna(steam_id) and str(steam_id).strip():
            player_info["steamID"] = str(steam_id).strip()
        else:
            rank = row.get("rank")
            if pd.isna(rank) or not str(rank).strip():
                rank = RANK_OPTIONS[0]

            subrank = row.get("subrank")
            if pd.isna(subrank) or not str(subrank).strip():
                subrank = "I"

            player_info["rank"] = str(rank).strip()
            player_info["subrank"] = SUBRANK_OPTIONS.get(str(subrank).strip().upper(), 1)

        player_list.append(player_info)

    return player_list

##################################### MAIN METHODS ########################################

def main():
    st.title("Deadlock Tourney Seeder")

    st.write("""
    This site is used to provide an easier way
    to balance teams in custom matches created 
    within Deadlock.
    """)

    num_of_players = st.selectbox("Number of Players", options=[4, 6, 8, 10, 12], index=4)

    st.divider()

    # Table display
    player_schema = {
        "name" : pd.Series(dtype="string"),
        "steamID" : pd.Series(dtype="string"),
        "rank" : pd.Series(dtype=pd.CategoricalDtype(categories=RANK_OPTIONS)),
        "subrank" : pd.Series(dtype=pd.CategoricalDtype(categories=SUBRANK_OPTIONS.keys()))
    }

    player_df = pd.DataFrame(player_schema, index=range(num_of_players))
    player_table = st.data_editor(player_df)

    if st.button("Begin Match Seeding", type="primary"):
        with st.spinner("Please wait..."):

            # Generate player data and send to the API for seeding
            try:
                if not API_BASE_URL:
                    raise ValueError("Set DEADLOCK_SEEDER_API_URL to the deployed API base URL.")

                player_list = generate_player_data(player_table)

                response = requests.post(f"{API_BASE_URL}/seed", json={"player_list": player_list}, timeout=30)
                response.raise_for_status() # Raises an error for non-200 responses
                result = response.json()

                if not isinstance(result, dict) or result.get("status") != "success" or "data" not in result:
                    raise ValueError("The seeding API returned an invalid response.")

                render_teams(result["data"])

            except requests.RequestException as error:
                st.error(f"Could not seed teams through the API: {error}")

            except ValueError as error:
                st.error(str(error))

if __name__ == "__main__":
    main()