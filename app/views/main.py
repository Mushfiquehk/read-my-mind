""""""

from datetime import datetime, timedelta
import random
import base64

from flask import render_template, jsonify, redirect, Blueprint, request, current_app, url_for
import requests
from requests import PreparedRequest

main = Blueprint("main", __name__)
state = random.randint(0, 100000000)


@main.route("/login", methods=["GET"])
def login():
    """Request user authorization"""
    redirect_url = "https://accounts.spotify.com/authorize?"
    scope = "user-read-private user-read-email user-top-read"
    payload = {
        "response_type": "code",
        "client_id": current_app.config["SPOTIFY_CLIENT_ID"],
        "scope": scope,
        "redirect_uri": "http://localhost:5000/callback",
        "state": state,
    }
    auth_req = PreparedRequest()
    auth_req.prepare_url(redirect_url, payload)
    return redirect(auth_req.url, code=302)


@main.route("/callback", methods=["GET", "POST"])
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
    payload["expires_at"] = datetime.now() + timedelta(seconds=payload["expires_in"])

    collection = current_app.config["ACCESS_TOKENS_COLLECTION"]
    collection.access_tokens.insert_one(payload)

    return redirect("/")


@main.route("/refresh_token", methods=["GET"])
def refresh_token():
    collection = current_app.config["ACCESS_TOKENS_COLLECTION"]
    token_doc = collection.find_one(sort=[("_id", -1)])
    
    if not token_doc or 'refresh_token' not in token_doc:
        return jsonify({"error": "No refresh token found in the database"}), 400
    
    refresh_token = token_doc['refresh_token']

    client_id = current_app.config["SPOTIFY_CLIENT_ID"]
    client_secret = current_app.config["SPOTIFY_CLIENT_SECRET"]
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {auth_header}"
    }

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers=headers,
        data=data,
        timeout=10
    )

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]
        new_refresh_token = token_data.get("refresh_token", refresh_token)
        expires_in = token_data["expires_in"]

        # Calculate expiration time
        expires_at = datetime.now() + timedelta(seconds=expires_in)

        # Update the token in the database
        collection.update_one(
            {"refresh_token": refresh_token},
            {"$set": {
                "access_token": access_token,
                "refresh_token": new_refresh_token,
                "expires_at": expires_at,
                "expires_in": expires_in
            }},
            upsert=True
        )

        # Prepare token_data to pass to the home route
        token_data = {
            "expires_at": expires_at.isoformat(),
            "is_valid": True,
            "refresh_token": new_refresh_token
        }

        # Redirect to home route with token_data
        return redirect(url_for('main.home', token_data=token_data))
    else:
        return jsonify({"error": "Failed to refresh token"}), response.status_code


@main.route("/token_status", methods=["GET"])
def token_status():
    """Token status"""
    collection = current_app.config["ACCESS_TOKENS_COLLECTION"]
    access_token = collection.find_one(sort=[("_id", -1)])
    if access_token:
        expiration_time = access_token.get(
            "expires_at",
            access_token["_id"].generation_time.replace(tzinfo=None)
            + timedelta(seconds=access_token["expires_in"]),
        )
        is_valid = expiration_time > datetime.now()
        return jsonify(
            {"expires_at": expiration_time.isoformat(), "is_valid": is_valid}
        )
    return jsonify({"is_valid": False})


@main.route("/", methods=["GET"])
def home():
    """Home page"""
    token_data = request.args.get('token_data')
    if not token_data:
        collection = current_app.config["ACCESS_TOKENS_COLLECTION"]
        access_token = collection.find_one(sort=[("_id", -1)])
        if access_token:
            expiration_time = access_token.get(
                "expires_at",
                access_token["_id"].generation_time.replace(tzinfo=None)
                + timedelta(seconds=access_token["expires_in"]),
            )
            print(expiration_time > datetime.now())
            token_data = {
                "expires_at": expiration_time.isoformat(),
                "is_valid": expiration_time > datetime.now(),
                "refresh_token": access_token.get("refresh_token")
            }
    else:
        token_data = eval(token_data)  # Convert string representation back to dictionary
    
    return render_template("pages/index.html", token_data=token_data)
