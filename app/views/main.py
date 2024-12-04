"""Main views"""

from flask import Blueprint, render_template

from .spotify import read_spotify_profile, get_top_artists, get_top_songs, get_on_repeats

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
    profile = read_spotify_profile()
    spotify_profile_image = profile["images"][0]["url"]

    projects = [
        {
            "title": "This Website",
            "description": "Things I do and things I am into",
            "url": "https://github.com/Mushfiquehk/read-my-mind",
        },
        {
            "title": "E-Commerce",
            "description": "Online retail storefront with item and order function",
            "url": "https://github.com/Mushfiquehk/Stork-Distribution.git",
        },
        {
            "title": "Stay Tuned",
            "description": "More coming soon...",
            "url": ""
        }
    ]

    return render_template(
        "pages/index.html",
        spotify_profile_image=spotify_profile_image,
        projects=projects
    )
