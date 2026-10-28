"""Public GitHub profile for the portfolio."""
import re
import requests
import streamlit as st


@st.cache_data(ttl=900, show_spinner=False)
def load_github(username):
    try:
        responses = [requests.get(f'https://api.github.com/users/{username}{suffix}', timeout=12,
                     headers={'Accept': 'application/vnd.github+json'})
                     for suffix in ['', '/repos?sort=updated&per_page=100&type=owner']]
        for response in responses:
            response.raise_for_status()
        return responses[0].json(), responses[1].json()
    except (requests.RequestException, ValueError):
        return None, []


def render_github():
    st.caption('ON GITHUB')
    st.subheader('What I’m building')
    st.write('Code, experiments, and the projects I’m learning from.')
    username = str(st.secrets.get('GITHUB_USERNAME', '')).strip()
    with st.spinner('Loading GitHub projects…'):
        profile, repos = load_github(username)
    if profile is None:
        st.info('GitHub is unavailable or its request limit was reached. Please try again later.')
        return
    st.text(profile.get('name') or username)
    st.link_button('View GitHub profile ↗', f'https://github.com/{username}')
    count, followers = st.columns(2)
    count.metric('Public repositories', profile.get('public_repos', 0))
    followers.metric('Followers', profile.get('followers', 0))
    originals = [repo for repo in repos if not repo.get('fork')]
    for repo in originals[:3]:
        with st.container(border=True):
            st.text(repo['name'])
            st.write(repo.get('description') or 'No description added yet.')
            st.caption(f"{repo.get('language') or 'Language not specified'} · ★ {repo.get('stargazers_count', 0)}")
            st.link_button('View repository ↗', f"https://github.com/{username}/{repo['name']}")
    if not originals:
        st.caption('No original public repositories to show yet.')
    st.caption('Most recently updated original repositories from up to 100 public repositories. Cached for 15 minutes.')
