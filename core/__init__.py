import logging
import os

from dotenv import load_dotenv
from flask import Flask

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    datefmt="%Y-%m-%d",
    format="%(levelname)s - %(message)s"
)


def register_blueprints(app):
    """
    Register flask blueprints here.

    Flask blueprints enable more modular HTML / code development
    """

    from core.home.home import index_bp
    app.register_blueprint(index_bp)


def create_app(env=''):
    """
    Create APP!
    """

    app = Flask(__name__)

    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        raise RuntimeError("SECRET_KEY environment variable is not set")
    app.secret_key = secret_key

    register_blueprints(app)

    return app
