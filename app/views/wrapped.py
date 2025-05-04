"""These views contain the routes to the Wrapped Predictions

I want to create page that has a similar look and feel to the spotify
wrapped reveal page where I show my predictions for this year's spotify wrapped

There will be two routes:
1. /wrapped/artists
2. /wrapped/tracks

The first route will display the top 5 artists from the database
The second route will display the top 5 tracks from the database

The title will be "Spotify Wrapped 2025 (Predictions)"
"""

from datetime import datetime

from flask import Blueprint, render_template
from .spotify import read_top_artists, read_top_songs, read_on_repeats


wrapped = Blueprint("wrapped", __name__)


def get_top_genre(artist_data) -> str:
    """Return the most common genre from the artist data"""
    genres = {}
    for artist in artist_data:
        for genre in artist["genres"]:
            genres[genre] = genres.get(genre, 0) + 1
    return max(genres, key=genres.get).capitalize()


@wrapped.route("", methods=["GET"])
def current_wrapped():
    """Display the top 5 artists and top 5 songs from the database

    Also shows the image of the top artist
    """

    top_songs = read_top_songs()
    top_songs.reverse()

    top_artists = read_top_artists()
    top_artists.reverse()
    number_one_artist = top_artists[0]["name"]
    image_url = top_artists[0]["images"][-1]["url"]
    top_genre = get_top_genre(top_artists)

    year = datetime.now().year

    return render_template("pages/wrapped.html",
                           title=f"Spotify Wrapped {year} (Predictions)",
                           number_one_artist=number_one_artist,
                           artists=top_artists,
                           songs=top_songs,
                           genre=top_genre,
                           year=year,
                           image_url=image_url)


@wrapped.route("/my_recommendations", methods=["GET"])
def my_recommendations():
    """Display the top 5 tracks from the database"""
    top_tracks = read_on_repeats()
    year = datetime.now().year
    return render_template("pages/wrapped_tracks.html",
                           title=f"Spotify Wrapped {year} (Predictions)",
                           items=top_tracks, type="on_repeat")
