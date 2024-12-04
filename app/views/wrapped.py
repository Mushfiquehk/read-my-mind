"""These views contain the routes to the Wrapped Predictions

I want to create page that has a similar look and feel to the spotify wrapped reveal page where I show my predictions for this year's spotify wrapped

There will be two routes:
1. /wrapped/artists
2. /wrapped/tracks

The first route will display the top 5 artists from the database
The second route will display the top 5 tracks from the database

The title will be "Spotify Wrapped 2025 (Predictions)"
"""

from datetime import datetime

from flask import Blueprint, render_template
from .spotify import read_top_artists, read_top_songs
from .spotify import get_top_artists, get_top_songs, get_on_repeats


wrapped = Blueprint("wrapped", __name__)


@wrapped.route("/artists", methods=["GET"])
def artists():
    """Display the top 5 artists from the database"""
    # top_artists = get_top_artists()
    top_artists = read_top_artists()
    year = datetime.now().year
    return render_template("pages/wrapped.html",
                           title=f"Spotify Wrapped {year} (Predictions)",
                           items=top_artists, type="artists")


@wrapped.route("/tracks", methods=["GET"])
def tracks():
    """Display the top 5 tracks from the database"""
    # top_tracks = get_top_songs()
    top_tracks = read_top_songs()
    year = datetime.now().year
    return render_template("pages/wrapped_tracks.html",
                           title=f"Spotify Wrapped {year} (Predictions)",
                           items=top_tracks, type="tracks")


@wrapped.route("/on_repeat", methods=["GET"])
def on_repeat():
    """Display the top 5 tracks from the database"""
    top_tracks = get_on_repeats()
    year = datetime.now().year
    return render_template("pages/wrapped_tracks.html",
                           title=f"Spotify Wrapped {year} (Predictions)",
                           items=top_tracks, type="on_repeat")
    