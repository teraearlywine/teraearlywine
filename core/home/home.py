# Set up home blueprint
from flask import Blueprint, render_template, request, url_for, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash


index_bp = Blueprint(
    name='index',  # Blueprint name for endpoint. endpoint -> 'users.login', 'users.update', 'users.delete_account'
    import_name=__name__, 
    template_folder='templates', 
    static_folder='assets',
    static_url_path='/static/assets',   # URL path to serve static files
    url_prefix='/'
)


@index_bp.route("/")
def index():
    """

    Browser home page for www.teraearlywine.com
    """
    return render_template('home/home.html')


@index_bp.route("/projects")
def projects():
    """

    Browser about page for www.teraearlywine.com
    """
    return render_template('home/projects.html')
