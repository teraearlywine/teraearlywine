import logging
import os
import secrets

from dotenv import load_dotenv
from flask import Flask, render_template

from core.config import config as app_config

load_dotenv()


def register_blueprints(app):
    """
    Register flask blueprints here.

    Flask blueprints enable more modular HTML / code development
    """

    from core.home.home import index_bp  # noqa: E402
    app.register_blueprint(index_bp)


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return render_template('home/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('home/500.html'), 500


def create_app(env=''):
    """
    Create APP!
    """

    app = Flask(__name__)

    env = env or os.environ.get('FLASK_ENV', 'production')
    app.config.from_object(app_config.get(env, app_config['default']))

    logging.basicConfig(
        level=app.config['LOG_LEVEL'],
        datefmt="%Y-%m-%d",
        format="%(levelname)s - %(message)s"
    )

    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        if env == 'production':
            secret_key = secrets.token_hex(32)
            app.logger.warning(
                "SECRET_KEY environment variable is not set; using an ephemeral key for this process"
            )
        else:
            secret_key = 'development-secret-key'
            app.logger.warning(
                "SECRET_KEY environment variable is not set; using the default development key"
            )
    app.config['SECRET_KEY'] = secret_key
    app.secret_key = secret_key

    register_blueprints(app)
    register_error_handlers(app)

    return app
