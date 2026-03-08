# Set up home blueprint
from flask import Blueprint, render_template, redirect, url_for


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


@index_bp.route("/about-me")
def about_me():
    """
    Redirect to experience section on homepage.
    """
    return redirect(url_for('index.index') + '#experience')
