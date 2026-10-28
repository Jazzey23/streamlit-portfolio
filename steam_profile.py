"""Read public Steam interests without exposing credentials in UI errors."""

import re
from datetime import datetime, timezone

import requests
import streamlit as st


class SteamError(Exception):
    """A safe, visitor-facing error."""


def steam_request(endpoint, api_key, **params):
    try:
        response = requests.get(
            f"https://api.steampowered.com/{endpoint}/",
            params={"key": api_key, **params},
            timeout=12,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict) or not isinstance(payload.get("response"), dict):
            raise ValueError("Unexpected response")
        return payload["response"]
    except (requests.RequestException, ValueError):
        # Request exceptions can contain the full URL, including the API key.
        raise SteamError("Steam is unavailable right now. Please try again later.") from None


@st.cache_data(ttl=900, show_spinner=False, max_entries=8)
def load_steam_profile(steam_id, api_key):
    profile = steam_request("ISteamUser/GetPlayerSummaries/v2", api_key, steamids=steam_id)
    players = profile.get("players", [])
    if not players:
        raise SteamError("This Steam profile could not be found. Check the configured Steam ID.")
    library = steam_request(
        "IPlayerService/GetOwnedGames/v1", api_key,
        steamid=steam_id, include_appinfo=1, include_played_free_games=1,
    )
    return {"player": players[0], "library": library, "updated": datetime.now(timezone.utc)}


def render_steam_interests():
    st.subheader("Steam")
    st.write("Here are games I play.")
    try:
        api_key = str(st.secrets.get("STEAM_API_KEY", "")).strip()
        steam_id = str(st.secrets.get("STEAM_ID", "")).strip()
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        api_key, steam_id = "", ""
    if not api_key or not steam_id:
        st.info("Steam interests will appear once the account is connected.")
        return
    if not re.fullmatch(r"\d{17}", steam_id):
        st.info("Steam needs a 17-digit SteamID64 to display this profile.")
        return
    try:
        with st.spinner("Loading Steam interests…"):
            data = load_steam_profile(steam_id, api_key)
    except SteamError as error:
        st.info(str(error))
        return

    with st.container(border=True):
        name, link = st.columns([3, 1])
        name.caption("MY STEAM PROFILE")
        name.text(data["player"].get("personaname", "Steam player"))
        link.link_button("Steam profile ↗", f"https://steamcommunity.com/profiles/{steam_id}", use_container_width=True)
        library = data["library"]
        if "games" not in library and "game_count" not in library:
            st.info("Game details aren’t available. They may be private; set Steam’s Game details visibility to Public to share them here.")
            return
        games = library.get("games", [])
        if not games:
            st.info("Steam returned no games to display yet.")
            return
        played = [game for game in games if game.get("playtime_forever", 0) > 0]
        count, explored, total = st.columns(3)
        count.metric("In my library", library.get("game_count", len(games)))
        explored.metric("Games played", len(played))
        total.metric("Recorded playtime", f"{sum(g.get('playtime_forever', 0) for g in games) / 60:,.0f} hrs")
        if played:
            st.divider()
            st.markdown("**The games I keep coming back to**")
            st.caption("My top three by all-time recorded playtime.")
            ranked = sorted(played, key=lambda game: game.get("playtime_forever", 0), reverse=True)
            for rank, (column, game) in enumerate(zip(st.columns(min(3, len(ranked))), ranked[:3]), start=1):
                with column, st.container(border=True):
                    st.caption(f"0{rank} / MOST PLAYED")
                    st.text(game.get("name", "Unknown game"))
                    st.metric("Hours played", f"{game['playtime_forever'] / 60:,.1f}")
                    app_id = game.get("appid")
                    if isinstance(app_id, int) and app_id > 0:
                        st.link_button("Explore game ↗", f"https://store.steampowered.com/app/{app_id}/")
            with st.expander("Explore my library"):
                query = st.text_input("Find a game", placeholder="Search by game title", key="steam_game_search")
                matches = [game for game in sorted(games, key=lambda g: g.get("playtime_forever", 0), reverse=True)
                           if query.casefold() in game.get("name", "Unknown game").casefold()]
                if matches:
                    st.dataframe(
                        [{"Game": game.get("name", "Unknown game"),
                          "Hours played": round(game.get("playtime_forever", 0) / 60, 1)} for game in matches],
                        hide_index=True, width="stretch",
                    )
                    st.caption(f"{len(matches)} games shown · Sorted by recorded playtime")
                else:
                    st.info("No games match that title. Try another search.")
        else:
            st.caption("No public playtime is available to rank games yet.")
        st.caption(f"Fetched {data['updated']:%d %b %Y, %H:%M} UTC · Updates on a page rerun after 15 minutes.")
