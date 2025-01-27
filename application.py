"""

"""


from flask import Flask
from app.config import Config
from app.views.main import main
from app.views.spotify import spotify
from app.views.wrapped import wrapped


def create_app(config_class=Config):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__,
                template_folder="app/templates",
                static_folder="app/static")

    Config.init_app(app)
    app.config.from_object(config_class)

    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(spotify, url_prefix="/spotify")
    app.register_blueprint(wrapped, url_prefix="/wrapped")

    return app

application = create_app()

if __name__ == "__main__":
    application.run(debug=False)
