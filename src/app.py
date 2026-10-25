import streamlit as st

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
    curr_expander = column.expander(f"Player {index+1}", expanded=False)
    with curr_expander:

        curr_expander.text_input(label="Name", key=f"player_name_{index}")
        rank, statlocker = curr_expander.tabs(tabs=["In-Game Rank","Statlocker"])

        rank.selectbox(label="Rank", options=RANK_OPTIONS, key=f"player_rank_{index}")
        statlocker.text_input(label="URL", key=f"player_url_{index}")

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

if __name__ == "__main__":
    main()