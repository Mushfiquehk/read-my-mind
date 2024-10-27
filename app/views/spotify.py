''''''

import requests

from flask import Blueprint, render_template, jsonify, current_app

spotify = Blueprint('spotify', __name__)

@spotify.route('/top-artists')
def top_artists():
    """ Get my top 5 artists """
    collection = current_app.config["ACCESS_TOKENS_COLLECTION"]
    access_token = collection.find_one(sort=[("_id", -1)])
    if not access_token:
        return jsonify({"error": "No access token available"}), 400

    headers = {
        "Authorization": f"Bearer {access_token['access_token']}"
    }

    response = requests.get(
        "https://api.spotify.com/v1/me/top/artists?time_range=short_term&limit=5&offset=0",
        headers=headers,
        timeout=10,
    )
    artists = response.json()
    
    try:
        artists = artists["items"]
    except KeyError:
        return jsonify(artists), 400
    # pprint.pprint(artists["items"])
    return render_template("pages/top_artists.html", top_artists_list=artists)
