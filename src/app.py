import streamlit as st
import seeder

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

#################################### HELPER METHODS ########################################

# Renders a player card with name and rank/URL inputs."""
def render_player_card(index, column):
    curr_expander = column.expander(f"Player {index+1}", expanded=True)
    with curr_expander:

        curr_expander.text_input(label="Name", key=f"player_name_{index}")
        missing_steam = curr_expander.checkbox(label="This player has no Steam ID, or they are unranked", key=f"player_hasSteam_{index}")

        if missing_steam:
            curr_expander.selectbox(label="Rank", options=RANK_OPTIONS, key=f"player_rank_{index}")
        else:
            curr_expander.text_input(label="Steam ID", key=f"player_steamID_{index}")

def render_teams(teams):
    st.subheader(f"Team A (Estimated MMR: {teams['total_mmr_A']})")
    for player in teams.get("team_A"):
        st.write(f"{player['name']} (Rank: {player['rank']})")

    st.subheader(f"Team B (Estimated MMR: {teams['total_mmr_B']})")
    for player in teams.get("team_B"):
        st.write(f"{player['name']} (Rank: {player['rank']})")

def generate_player_data(num_of_players):
    player_list = []
    
    for i in range(num_of_players):
        player_info = {
            "name": st.session_state.get(f"player_name_{i}"),
            "missing_steam" : st.session_state.get(f"player_hasSteam_{i}")
        }

        if player_info["missing_steam"]:
            player_info["rank"] = st.session_state.get(f"player_rank_{i}")
        else:
            player_info["steamID"] = st.session_state.get(f"player_steamID_{i}")

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

    left_col, right_col = st.columns(2)

    for i in range(num_of_players):
        current_col = left_col if i % 2 == 0 else right_col
        render_player_card(index=i, column=current_col)

    if st.button("Begin Match Seeding", type="primary"):
        with st.spinner("Please wait..."):

            player_list = generate_player_data(num_of_players)
            teams = seeder.generate_teams(player_list)
            render_teams(teams)

if __name__ == "__main__":
    main()