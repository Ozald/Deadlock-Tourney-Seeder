import streamlit as st
import seeder
import pandas as pd

st.set_page_config(page_title="Deadlock Tourney Seeder",layout="wide")

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
def render_player_card(index, column):
    curr_expander = column.expander(f"Player {index+1}", expanded=True)
    with curr_expander:

        curr_expander.text_input(label="Name", key=f"player_name_{index}")
        missing_steam = curr_expander.checkbox(label="This player has no Steam ID, or they are unranked", key=f"player_hasSteam_{index}")

        if missing_steam:
            curr_expander.selectbox(label="Rank", options=RANK_OPTIONS, key=f"player_rank_{index}")
            curr_expander.selectbox(label="Division", options=SUBRANK_OPTIONS.keys(), key=f"player_subrank_{index}")
        else:
            curr_expander.text_input(label="Steam ID", key=f"player_steamID_{index}")

def render_teams(teams):
    st.subheader(f"Team A")
    for player in teams.get("team_A"):
        st.write(f"{player['name']} ({player['rank']} {player['subrank']})")

    st.subheader(f"Team B")
    for player in teams.get("team_B"):
        st.write(f"{player['name']} ({player['rank']} {player['subrank']})")

def generate_player_data(player_table):
    player_list = []
    
    for _, row in player_table.iterrows():
        name = row.get("name")
        if not name or str(name).strip() == "":
            raise ValueError("Missing name found")

        missing_steam = bool(row.get("missing_steam", False))

        player_info = {
            "name": str(name).strip(),
            "missing_steam" : missing_steam
        }

        if player_info["missing_steam"]:
            player_info["rank"] = row.get("rank")
            player_info["subrank"] = SUBRANK_OPTIONS[row.get("subrank")]
        else:
            steam_id = row.get("steamID")
            player_info["steamID"] = str(steam_id).strip() if steam_id else ""

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
        "missing_steam" : pd.Series(dtype="boolean"),
        "steamID" : pd.Series(dtype="string"),
        "rank" : pd.Series(dtype=pd.CategoricalDtype(categories=RANK_OPTIONS)),
        "subrank" : pd.Series(dtype=pd.CategoricalDtype(categories=SUBRANK_OPTIONS.keys()))
    }

    player_df = pd.DataFrame(player_schema, index=range(num_of_players))
    player_table = st.data_editor(player_df)

    if st.button("Begin Match Seeding", type="primary"):
        with st.spinner("Please wait..."):

            player_list = generate_player_data(player_table)
            teams = seeder.generate_teams(player_list)
            render_teams(teams)

if __name__ == "__main__":
    main()