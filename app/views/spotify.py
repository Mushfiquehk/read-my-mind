"""Includes an implementation of the Spotify Auth flow"""

# from datetime import datetime, timedelta
import random
from typing import List
# import base64
import requests
from flask import (
    Blueprint,
    current_app,
)
# render_template,
#     jsonify,
#     redirect,
#     request,
#     url_for,
# )
# from requests import PreparedRequest

spotify = Blueprint("spotify", __name__)
state = random.randint(0, 100000000)


# @spotify.route("/login", methods=["GET"])
# def login():
#     """Request user authorization"""
#     redirect_url = "https://accounts.spotify.com/authorize?"
#     scope = "user-read-private user-read-email user-top-read"
#     payload = {
#         "response_type": "code",
#         "client_id": current_app.config["SPOTIFY_CLIENT_ID"],
#         "scope": scope,
#         "redirect_uri": "http://localhost:5000/callback",
#         "state": state,
#     }
#     auth_req = PreparedRequest()
#     auth_req.prepare_url(redirect_url, payload)
#     return redirect(auth_req.url, code=302)


# @spotify.route("/callback", methods=["GET", "POST"])
# def callback():
#     """Callback requests the access token after the user permits"""
#     code = request.args.get("code")
#     state = request.args.get("state")
#     assert state == state, "State mismatch"

#     auth_url = "https://accounts.spotify.com/api/token"
#     headers = {
#         "content-type": "application/x-www-form-urlencoded",
#     }

#     response = requests.post(
#         auth_url,
#         data={
#             "grant_type": "authorization_code",
#             "code": code,
#             "redirect_uri": "http://localhost:5000/callback",
#             "client_id": current_app.config["SPOTIFY_CLIENT_ID"],
#             "client_secret": current_app.config["SPOTIFY_CLIENT_SECRET"],
#         },
#         headers=headers,
#         timeout=10,
#     )
#     payload = response.json()
#     payload["expires_at"] = datetime.now() + timedelta(seconds=payload["expires_in"])

#     collection = current_app.config["ACCESS_TOKENS_COLLECTION"]
#     collection.access_tokens.insert_one(payload)

#     return redirect("/")


# @spotify.route("/refresh_token", methods=["GET"])
# def refresh_token():
#     """Refresh the access token"""
#     collection = current_app.config["ACCESS_TOKENS_COLLECTION"]
#     token_doc = collection.find_one(sort=[("_id", -1)])

#     if not token_doc or "refresh_token" not in token_doc:
#         return jsonify({"error": "No refresh token found in the database"}), 400

#     refresh_token = token_doc["refresh_token"]

#     client_id = current_app.config["SPOTIFY_CLIENT_ID"]
#     client_secret = current_app.config["SPOTIFY_CLIENT_SECRET"]
#     auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

#     headers = {
#         "content-type": "application/x-www-form-urlencoded",
#         "Authorization": f"Basic {auth_header}",
#     }

#     data = {"grant_type": "refresh_token", "refresh_token": refresh_token}

#     response = requests.post(
#         "https://accounts.spotify.com/api/token", headers=headers, data=data, timeout=10
#     )

#     if response.status_code == 200:
#         token_data = response.json()
#         access_token = token_data["access_token"]
#         new_refresh_token = token_data.get("refresh_token", refresh_token)
#         expires_in = token_data["expires_in"]

#         expires_at = datetime.now() + timedelta(seconds=expires_in)

#         # Update the token in the database
#         collection.update_one(
#             {"refresh_token": refresh_token},
#             {
#                 "$set": {
#                     "access_token": access_token,
#                     "refresh_token": new_refresh_token,
#                     "expires_at": expires_at,
#                     "expires_in": expires_in,
#                 }
#             },
#             upsert=True,
#         )

#         return redirect(url_for("main.home"))
#     else:
#         return jsonify({"error": "Failed to refresh token"}), response.status_code


def get_spotify_profile():
    """Get the Spotify profile image from user's profile"""
    endpoint = "https://api.spotify.com/v1/me"
    collection = current_app.config["ACCESS_TOKENS_COLLECTION"]
    access_token = collection.find_one(sort=[("_id", -1)])
    headers = {"Authorization": f"Bearer {access_token.get("access_token")}"}
    response = requests.get(endpoint, headers=headers, timeout=10)

    if response.ok:
        return response.json()

    return None


def get_top_artists():
    """Get my top 5 artists"""
    artists = get_spotify_data(
        "https://api.spotify.com/v1/me/top/artists?time_range=short_term&limit=5&offset=0"
    )
    return artists


def get_on_repeats():
    """Get my current top 5 tracks"""
    shows = get_spotify_data(
        "https://api.spotify.com/v1/me/top/tracks?time_range=short_term&limit=5&offset=0"
    )
    return shows


def get_top_songs():
    """Get my top 5 songs"""
    songs = get_spotify_data(
        "https://api.spotify.com/v1/me/top/tracks?time_range=long_term&limit=5&offset=0"
    )
    return songs


def get_spotify_data(url: str) -> List[dict]:
    '''Get using correct spotify credentials'''
    collection = current_app.config["ACCESS_TOKENS_COLLECTION"]
    access_token = collection.find_one(sort=[("_id", -1)])
    headers = {"Authorization": f"Bearer {access_token.get("access_token")}"}
    response = requests.get(url, headers=headers, timeout=5)
    data = response['items']

    return data
