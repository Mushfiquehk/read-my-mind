"""Create and configure an instance of the Flask application."""

from flask import Flask
from .config import Config
from .views.main import main
from .views.spotify import spotify
from .views.wrapped import wrapped


def create_app(config_class=Config):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)

    Config.init_app(app)
    app.config.from_object(config_class)

    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(spotify, url_prefix="/spotify")
    app.register_blueprint(wrapped, url_prefix="/wrapped")    

    return app
