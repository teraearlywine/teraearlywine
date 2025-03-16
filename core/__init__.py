import logging
from flask import Flask
from flask_login import LoginManager
from core.models import db, User

login_manager = LoginManager()

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

    app.secret_key = 'dev_test'  # Can be anything; 
    register_blueprints(app)
    
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception as err:
            logging.debug(f"Issue getting user_id: {err}")
            return None
    return app