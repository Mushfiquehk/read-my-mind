from flask import Flask, redirect, request
from flask_sqlalchemy import SQLAlchemy
import requests
from requests import PreparedRequest
import os
import random
import pprint

app = Flask(__name__)
db_user = os.environ["DB_USER"]
db_pass = os.environ["DB_PASSWORD"]
db_host = os.environ["DB_HOST"]
db_name = "spotify"
mssql_conn_str = f"mssql+pyodbc://{db_user}:{db_pass}@{db_host}/{db_name}?driver=ODBC+Driver+17+for+SQL+Server"
app.config["SQLALCHEMY_DATABASE_URI"] = mssql_conn_str
db = SQLAlchemy(app)


# Create our database model
class AccessToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(200))
    token_type = db.Column(db.String(200))
    scope = db.Column(db.String(200))
    expires_in = db.Column(db.Integer)
    refresh_token = db.Column(db.String(200))


state = random.randint(0, 100000000)


@app.route("/login", methods=["GET"])
def login():
    redirect_url = "https://accounts.spotify.com/authorize?"
    scope = "user-read-private user-read-email"
    payload = {
        "response_type": "code",
        "client_id": os.environ["SPOTIFY_CLIENT_ID"],
        "scope": scope,
        "redirect_uri": "http://localhost:5000/callback",
        "state": state,
    }
    auth_req = PreparedRequest()
    auth_req.prepare_url(redirect_url, payload)
    return redirect(auth_req.url, code=302)


@app.route("/callback", methods=["GET", "POST"])
def callback():
    """Callback requests the access token after the user permits"""
    code = request.args.get("code")
    state = request.args.get("state")
    assert state == state, "State mismatch"

    auth_url = "https://accounts.spotify.com/api/token"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "Authorization": "Basic "
        + os.environ["SPOTIFY_CLIENT_ID"]
        + ":"
        + os.environ["SPOTIFY_CLIENT_SECRET"],
    }

    response = requests.post(
        auth_url,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "http://localhost:5000/callback",
        },
        headers=headers,
    )
    payload = response.json()
    pprint.pprint(payload)

    token = AccessToken(**payload)
    db.session.add(token)
    db.session.commit()

    return "Success"


callback_port = 5000
if __name__ == "__main__":
    app.run(debug=True, port=callback_port)
