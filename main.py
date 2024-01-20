import streamsync as ss
import requests
import base64
import urllib.parse
import pandas as pd

CLIENT_ID = "39eacaef81dc4c34a46df1a38e7cbbe3"
CLIENT_SECRET = "b46a033c48da4a4e9642be30d8d49905"
REDIRECT_URI = "http://localhost:3006/#auth/callback"

# Spotify URLs
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

initial_state = ss.init_state({
    "show_login": True,
    "show_user": False,
    "username": ""
})

initial_state.import_frontend_module("oauth_redirect", "/static/oauth_redirect.js")

def check_session(state, session):
    # Check if the access_token exists in session
    if("access_token" in session['cookies']):
        state["show_login"] = False
        state["show_user"] = True


def session_inspector(state, session):
    state["session"] = session
    print(repr(session))

def show_name(state, session):
    user_profile_url = "https://api.spotify.com/v1/me"
    headers = {
        "Authorization": f"Bearer {session['cookies']['access_token']}"
    }

    response = requests.get(user_profile_url, headers=headers)
    response.raise_for_status()
    user_data = response.json()
    state["username"] = user_data["display_name"]
    
def handle_hashchange(state, payload, session):
    if(payload["page_key"] == "auth"):
        session['cookies']['access_token'] = payload["route_vars"]["#access_token"]
    check_session(state, session)
    show_name(state, session)

def login_to_spotify(state):
    scope = "user-read-private user-read-email"
    auth_url = f"{SPOTIFY_AUTH_URL}?response_type=token&client_id={CLIENT_ID}&scope={urllib.parse.quote(scope)}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
    state.open_url(auth_url)

# A function that request user's playlists and store them in a pandas dataframe
def get_playlists(state, session):
    playlists_url = "https://api.spotify.com/v1/me/playlists"
    headers = {
        "Authorization": f"Bearer {session['cookies']['access_token']}"
    }
    response = requests.get(playlists_url, headers=headers)
    response.raise_for_status()
    playlists_data = response.json()
    df = pd.DataFrame.from_dict(playlists_data["items"])
    df.reset_index(drop=True, inplace=True)
    state["playlists"] = df
    print(df)
    
