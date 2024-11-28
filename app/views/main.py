"""Main views"""

from datetime import datetime, timedelta

from flask import Blueprint, current_app, render_template

from .spotify import get_spotify_profile, get_top_artists, get_top_songs, get_on_repeats

main = Blueprint("main", __name__)


@main.route("/", methods=["GET"])
def home():
    """Home page

    Displays a spotify style page with a profile image at the top right corner
    in a circle border with shadows. It has the brand name next to it with the words MK.

    The main content is set within a centered container. The container is divided into sections.
    Each section has a Spotify  style heading and square tabs like spotify has.

    The first section is for top_artists then one for top_tracks and one for lastly on_repeats.
    I want the project set up in a way that I can change this setup to where I have
    a filter button above the slicers which I can click to show either top tracks or
    top artists or on_repeats in that section
    """

    # get acces_token to request my profile info
    collection = current_app.config["ACCESS_TOKENS_COLLECTION"]
    access_token = collection.find_one(sort=[("_id", -1)])
    token_data = {}
    if access_token:
        expiration_time = access_token.get(
            "expires_at",
            access_token["_id"].generation_time.replace(tzinfo=None)
            + timedelta(seconds=access_token["expires_in"]),
        )

        token_data = {
            "expires_at": expiration_time.isoformat(),
            "is_valid": expiration_time > datetime.now(),
        }

    try:
        _ = token_data["is_valid"]
        profile = get_spotify_profile()
        spotify_profile_image = profile["images"][0]["url"]
    except IndexError:
        spotify_profile_image = None
    except TypeError:
        spotify_profile_image = None

    projects = [
        {
            "title": "This Website",
            "description": "Everything I do and everything I am into",
            "url": "https://github.com/Mushfiquehk/read-my-mind",
        },
        {
            "title": "E-Commerce",
            "description": "Online retail storefront with item and order function",
            "url": "https://github.com/Mushfiquehk/Stork-Distribution.git",
        },
    ]

    return render_template(
        "pages/index.html",
        token_data=token_data,
        spotify_profile_image=spotify_profile_image,
        projects=projects,
        top_artists=get_top_artists(),
        top_tracks=get_top_songs(),
        on_repeats=get_on_repeats(),
    )
