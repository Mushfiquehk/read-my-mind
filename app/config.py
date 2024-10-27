"""Configuration for the Flask application."""

import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "your-secret-key"

    db_pass = os.environ["MDB_PWD"]
    db_user = os.environ["MDB_USER"]
    cluster_name = "Cluster0"
    db_cluster = os.environ["MDB_CLUSTER"]
    mongodb_uri = (
        f"mongodb+srv://{db_user}:{db_pass}@{db_cluster}/"
      + f"?retryWrites=true&w=majority&appName={cluster_name}"
    )
    SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")

    @staticmethod
    def init_app(app):
        mdb_client = MongoClient(Config.mongodb_uri, server_api=ServerApi("1"))
        app.config["MDB_CLIENT"] = mdb_client
        app.config["SPOTIFY_DB"] = mdb_client.spotify
        app.config["ACCESS_TOKENS_COLLECTION"] = mdb_client.spotify.access_tokens

        # Ensure indexes for better query performance
        app.config["ACCESS_TOKENS_COLLECTION"].create_index([("expires_at", -1)])

        # Add Spotify credentials to app config
        app.config["SPOTIFY_CLIENT_ID"] = Config.SPOTIFY_CLIENT_ID
        app.config["SPOTIFY_CLIENT_SECRET"] = Config.SPOTIFY_CLIENT_SECRET

        # db_user = os.environ["DB_USER"]
        # db_host = os.environ["DB_HOST"]
        # db_name = "spotify"
        # mssql_conn_str = f"mssql+pyodbc://{db_user}:{db_pass}@{db_host}/
        #                  {db_name}?driver=ODBC+Driver+17+for+SQL+Server"
        # app.config["SQLALCHEMY_DATABASE_URI"] = mssql_conn_str
        # db = SQLAlchemy(app)
