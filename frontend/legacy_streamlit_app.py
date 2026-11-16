from base64 import b64encode
from html import escape
import os
from pathlib import Path
import streamlit as st
import pandas as pd
import requests
from urllib.parse import quote

st.set_page_config(page_title="Deadlock Tourney Seeder",layout="wide")

API_BASE_URL = os.getenv("DEADLOCK_SEEDER_API_URL", "").rstrip("/")

RANK_OPTIONS = {
    "Unranked"  : 0,
    "Initiate"  : 1,
    "Seeker"    : 2,
    "Acolyte"   : 3,
    "Sentinel"  : 4,
    "Mystic"    : 5,
    "Ritualist" : 6,
    "Emissary"  : 7,
    "Oracle"    : 8,
    "Phantom"   : 9,
    "Ascendant" : 10,
    "Eternus"   : 11
}

SUBRANK_OPTIONS = {
    "I"     : 1,
    "II"    : 2,
    "III"   : 3,
    "IV"    : 4,
    "V"     : 5,
    "VI"    : 6
}

RANK_ASSET_URL = "https://api.deadlock-api.com/v1/assets/ranks/{rank}/{subrank}/image"
OBSCURUS_RANK_ASSET_URL = "https://assets-bucket.deadlock-api.com/assets-api-res/images/ranks/rank00_lg.webp"
PLACEHOLDER_AVATAR_PATH = (
    Path(__file__).resolve().parents[1] / "assets" / "profile_avatar_placeholder_large.png"
)
PLACEHOLDER_AVATAR_SRC = (
    "data:image/png;base64,"
    + b64encode(PLACEHOLDER_AVATAR_PATH.read_bytes()).decode("ascii")
)

#################################### HELPER METHODS ########################################

# Gets the image link for a player's rank.
def _get_rank_asset_url(player):
    rank = player.get("rank")
    if rank in ("Unranked", "Obscurus"):
        return OBSCURUS_RANK_ASSET_URL

    rank_num = RANK_OPTIONS.get(rank)
    subrank = player.get("subrank")
    if isinstance(subrank, str):
        subrank_num = SUBRANK_OPTIONS.get(subrank.strip().upper())
    elif isinstance(subrank, int) and subrank in SUBRANK_OPTIONS.values():
        subrank_num = subrank
    else:
        subrank_num = None

    if rank_num is None or subrank_num is None:
        return None

    return RANK_ASSET_URL.format(rank=rank_num, subrank=subrank_num)

# Renders the generated teams in the Streamlit app.
def render_teams(teams):
    _render_team("Team A", teams.get("team_A", []))
    _render_team("Team B", teams.get("team_B", []))

# Renders a single team given a name and player list.
def _render_team(team_name, players):
    st.markdown(
        f"<h3 style='text-align:center'>{escape(team_name)}</h3>",
        unsafe_allow_html=True,
    )
    player_markup = "".join(_render_player(player) for player in players)
    st.markdown(
        '<div style="display:flex; flex-wrap:wrap; justify-content:center; '
        f'align-items:flex-start; gap:0.75rem">{player_markup}</div>',
        unsafe_allow_html=True,
    )

# Renders the username, avatar, and rank for a given player.
def _render_player(player):
    image_markup = []
    rank_asset_url = _get_rank_asset_url(player)
    profile_pic = player.get("profile_pic")

    if rank_asset_url:
        image_markup.append(
            f'<img src="{escape(rank_asset_url, quote=True)}" alt="Rank badge" '
            'style="width:64px; height:64px; object-fit:contain">'
        )

    avatar_src = profile_pic or PLACEHOLDER_AVATAR_SRC
    avatar_alt = "Profile picture" if profile_pic else "Default profile avatar"
    avatar_markup = (
        f'<img src="{escape(str(avatar_src), quote=True)}" alt="{avatar_alt}" '
        'style="width:112px; height:112px; border-radius:10%; object-fit:cover;">'
    )
    
    steam_id = player.get("steamID")
    if steam_id:
        profile_url = f"https://statlocker.gg/profile/{quote(str(steam_id), safe='')}/"
        image_markup.append(
            f'<a href="{escape(profile_url, quote=True)}" target="_blank" '
            f'rel="noopener noreferrer">{avatar_markup}</a>'
        )
    else:
        image_markup.append(avatar_markup)


    name = escape(str(player.get("name") or "Player"))
    rank = player.get("rank", "Unranked")
    rank_label = rank if rank in ("Unranked", "Obscurus") else f"{rank} {player.get('subrank', '')}"
    return (
        '<div style="width:140px; display:flex; flex-direction:column; align-items:center; '
        'gap:0.25rem; text-align:center">'
        f'{"".join(image_markup)}'
        f'<div style="font-weight:600; overflow-wrap:anywhere">{name}</div>'
        f'<div style="opacity:0.75">{escape(str(rank_label))}</div>'
        '</div>'
    )


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
                rank = list(RANK_OPTIONS.keys())[0]

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
        "rank" : pd.Series(dtype=pd.CategoricalDtype(categories=RANK_OPTIONS.keys())),
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