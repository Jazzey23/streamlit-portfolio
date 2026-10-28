"""Server-side Spotify listening highlights using an owner refresh token."""
import requests
import streamlit as st


class SpotifyError(Exception):
    pass


@st.cache_data(ttl=900, show_spinner=False, max_entries=12)
def load_spotify(client_id, client_secret, refresh_token, time_range):
    try:
        response = requests.post('https://accounts.spotify.com/api/token',
            auth=(client_id, client_secret),
            data={'grant_type': 'refresh_token', 'refresh_token': refresh_token}, timeout=12)
        if response.status_code in (400, 401):
            raise SpotifyError('Spotify needs to be reconnected. Check the app credentials and renew the refresh token.')
        response.raise_for_status()
        token = response.json()['access_token']
        result = {}
        for kind in ('artists', 'tracks'):
            response = requests.get(f'https://api.spotify.com/v1/me/top/{kind}',
                headers={'Authorization': f'Bearer {token}'},
                params={'time_range': time_range, 'limit': 5}, timeout=12)
            if response.status_code == 403:
                raise SpotifyError('Spotify denied access. Authorize user-top-read and check that this account has access to your Spotify app.')
            if response.status_code == 429:
                raise SpotifyError('Spotify’s request limit was reached. Please try again later.')
            response.raise_for_status()
            result[kind] = response.json()['items']
        return result
    except (requests.RequestException, ValueError, KeyError):
        raise SpotifyError('Spotify is unavailable right now. Please try again later.') from None


def render_spotify():
    st.divider()
    st.subheader('A soundtrack for the everyday')
    st.write('The artists and tracks I’ve been coming back to, on Spotify.')
    try:
        credentials = [str(st.secrets.get(key, '')).strip() for key in
                       ('SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET', 'SPOTIPY_REFRESH_TOKEN')]
    except FileNotFoundError:
        credentials = ['', '', '']
    if not all(credentials):
        st.info('Listening highlights will appear once Spotify is connected.')
        return
    period = st.selectbox('Listening window', ['Last 4 weeks', 'Last 6 months', 'Last year'], key='spotify_period')
    ranges = {'Last 4 weeks': 'short_term', 'Last 6 months': 'medium_term', 'Last year': 'long_term'}
    try:
        with st.spinner('Loading Spotify highlights…'):
            data = load_spotify(*credentials, ranges[period])
    except SpotifyError as error:
        st.info(str(error))
        return
    for column, kind, title in zip(st.columns(2, gap='large'), ('artists', 'tracks'), ('Favorite artists', 'Top tracks')):
        with column, st.container(border=True):
            st.subheader(title)
            if not data[kind]:
                st.caption('Not enough listening history for this window yet.')
            for index, item in enumerate(data[kind], 1):
                st.text(f"{index:02d}  {item['name']}")
                if kind == 'tracks':
                    st.caption(', '.join(artist['name'] for artist in item.get('artists', [])))
                url = item.get('external_urls', {}).get('spotify', '')
                if url.startswith('https://open.spotify.com/'):
                    st.link_button('Open in Spotify ↗', url)
                if index < len(data[kind]):
                    st.divider()
    st.caption('Source: Spotify · Ranked by listening affinity, not play counts. Time windows are approximate. Updates on a page rerun after 15 minutes.')
