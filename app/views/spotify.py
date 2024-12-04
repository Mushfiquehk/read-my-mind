"""Includes an implementation of the Spotify Auth flow

THe app is connected to a MongoDB database to store the access tokens
and refresh tokens. The app uses the Spotify API to get the user's
and store the user's top artists, songs, and tracks.

This script also includes read functions to get the user's top artists,
songs, and tracks.
"""

from datetime import datetime, timedelta
import random
from typing import List
import base64
import requests
from flask import (
    Blueprint,
    current_app,
    jsonify,
    redirect,
    request,
    url_for,
)
from requests import PreparedRequest
from pymongo.cursor import Cursor

spotify = Blueprint("spotify", __name__)
state = random.randint(0, 100000000)


@spotify.route("/login", methods=["GET"])
def login():
    """Request user authorization"""
    domain = current_app.config["DOMAIN"]
    redirect_url = "https://accounts.spotify.com/authorize?"
    scope = "user-read-private user-read-email user-top-read"
    payload = {
        "response_type": "code",
        "client_id": current_app.config["SPOTIFY_CLIENT_ID"],
        "scope": scope,
        "redirect_uri": f"http://{domain}:5000/callback",
        "state": state,
    }
    auth_req = PreparedRequest()
    auth_req.prepare_url(redirect_url, payload)
    return redirect(auth_req.url, code=302)


@spotify.route("/callback", methods=["GET", "POST"])
def callback():
    """Callback requests the access token after the user permits"""
    code = request.args.get("code")
    state = request.args.get("state")
    assert state == state, "State mismatch"

    auth_url = "https://accounts.spotify.com/api/token"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
    }

    response = requests.post(
        auth_url,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "http://localhost:5000/callback",
            "client_id": current_app.config["SPOTIFY_CLIENT_ID"],
            "client_secret": current_app.config["SPOTIFY_CLIENT_SECRET"],
        },
        headers=headers,
        timeout=10,
    )
    payload = response.json()
    payload["expires_at"] = datetime.now(
    ) + timedelta(seconds=payload["expires_in"])

    collection = current_app.config["ACCESS_TOKENS_COLLECTION"]
    collection.access_tokens.insert_one(payload)

    return redirect("/")


@spotify.route("/refresh_token", methods=["GET"])
def refresh_token():
    """Refresh the access token"""
    collection = current_app.config["ACCESS_TOKENS_COLLECTION"]
    token_doc = collection.find_one(sort=[("_id", -1)])

    if not token_doc or "refresh_token" not in token_doc:
        return jsonify({"error": "No refresh token found in the database"}), 400

    refresh_token = token_doc["refresh_token"]

    client_id = current_app.config["SPOTIFY_CLIENT_ID"]
    client_secret = current_app.config["SPOTIFY_CLIENT_SECRET"]
    auth_header = base64.b64encode(
        f"{client_id}:{client_secret}".encode()).decode()

    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {auth_header}",
    }

    data = {"grant_type": "refresh_token", "refresh_token": refresh_token}

    response = requests.post(
        "https://accounts.spotify.com/api/token", headers=headers, data=data, timeout=10
    )

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]
        new_refresh_token = token_data.get("refresh_token", refresh_token)
        expires_in = token_data["expires_in"]

        expires_at = datetime.now() + timedelta(seconds=expires_in)

        # Update the token in the database
        collection.update_one(
            {"refresh_token": refresh_token},
            {
                "$set": {
                    "access_token": access_token,
                    "refresh_token": new_refresh_token,
                    "expires_at": expires_at,
                    "expires_in": expires_in,
                }
            },
            upsert=True,
        )

        return redirect(url_for("main.home"))
    else:
        return jsonify({"error": "Failed to refresh token"}), response.status_code


def get_spotify_data(url: str) -> List[dict]:
    '''Get using correct spotify credentials'''
    collection = current_app.config["ACCESS_TOKENS_COLLECTION"]
    access_token = collection.find_one(sort=[("_id", -1)]).get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers, timeout=5)
    
    if response.ok:
        print(response.json())
        data = response.json()['items']
        return data
    
    return []


def get_spotify_profile():
    """Get the Spotify profile image from user's profile
    and store in the database"""
    endpoint = "https://api.spotify.com/v1/me"
    collection = current_app.config["ACCESS_TOKENS_COLLECTION"]
    access_token = collection.find_one(sort=[("_id", -1)]).get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(endpoint, headers=headers, timeout=10)

    if not response.ok:
        return jsonify({"error": "Failed to get profile"}), response.status_code
    
    profile = response.json()
    profile_collection = current_app.config["SPOTIFY_DB"].profile
    profile_collection.insert_one(profile)
    
    return profile
    
def read_spotify_profile():
    """Read the Spotify profile from the database"""
    profile_collection = current_app.config["SPOTIFY_DB"].profile
    profile = profile_collection.find_one()
    return profile
        
def get_top_artists():
    """Get my top 5 artists and store them in the database"""
    artists = get_spotify_data(
        "https://api.spotify.com/v1/me/top/artists?time_range=medium_term&limit=5&offset=0"
    )

    artists_collection = current_app.config["SPOTIFY_DB"].artists

    # tag the artists with the current date and rank
    rank = 1
    for artist in artists:
        artist["date"] = datetime.now()
        artist["rank"] = rank
        rank += 1

    artists_collection.insert_many(artists)
    
    return artists


def read_top_artists():
    """Read the top 5 artists from the database"""
    artists_collection = current_app.config["SPOTIFY_DB"].artists
    cursor: Cursor = artists_collection.find().sort("date", -1).limit(5)
    cursor = cursor.sort("rank")
    
    # keep on artist name, image and genres
    artists = []
    for artist in cursor:
        artists.append(artist)
    return artists


def get_on_repeats():
    """Get my short term top 5 tracks and store them in the database"""
    on_repeats = get_spotify_data(
        "https://api.spotify.com/v1/me/top/tracks?time_range=short_term&limit=5&offset=0"
    )

    on_repeats_collection = current_app.config["SPOTIFY_DB"].on_repeats

    # tag the tracks with the current date
    for track in on_repeats:
        track["date"] = datetime.now()

    on_repeats_collection.insert_many(on_repeats)
    
    return on_repeats


def read_on_repeats():
    """Read the top 5 tracks from the database"""
    on_repeats_collection = current_app.config["SPOTIFY_DB"].on_repeats
    on_repeats = on_repeats_collection.find().sort("date", -1).limit(5)
    return on_repeats


def get_top_songs():
    """Get my long term top 5 songs"""
    songs = get_spotify_data(
        "https://api.spotify.com/v1/me/top/tracks?time_range=long_term&limit=5&offset=0"
    )
    
    songs_collection = current_app.config["SPOTIFY_DB"].songs
    
    # tag the songs with the current date
    for song in songs:
        song["date"] = datetime.now()
        
    songs_collection.insert_many(songs)
    
    return songs
    

def read_top_songs() -> Cursor:
    """Read the top 5 songs from the database"""
    songs_collection = current_app.config["SPOTIFY_DB"].songs
    cursor = songs_collection.find().sort("date", -1).limit(5)
            
    return cursor
    