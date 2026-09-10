import logging
import mimetypes
import os
from urllib.parse import quote, urlsplit, urlunsplit

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request

from core.config import config as app_config
from core.secrets import load_secret
from core.static_assets import register_static_assets

load_dotenv()


def _validated_https_url(value, setting_name, logger):
    """Return an absolute HTTPS URL or hide the unsafe configuration."""
    configured_url = str(value or '').strip()
    if not configured_url:
        return ''

    try:
        parsed_url = urlsplit(configured_url)
        is_valid = (
            parsed_url.scheme.lower() == 'https'
            and bool(parsed_url.netloc)
            and bool(parsed_url.hostname)
            and not parsed_url.username
            and not parsed_url.password
            and not any(character.isspace() for character in configured_url)
        )
        parsed_url.port
    except ValueError:
        is_valid = False

    if not is_valid:
        logger.warning(
            '%s must be an absolute HTTPS URL; the related public link '
            'will be hidden',
            setting_name,
        )
        return ''

    return configured_url


def _warn_about_production_config(app, env):
    """Report missing production essentials without blocking startup."""
    if env != 'production':
        return

    if not app.config['SITE_URL']:
        app.logger.warning(
            'SITE_URL is not configured; canonical metadata and sitemap '
            'entries will be omitted'
        )
    if not app.config['BOOKING_URL']:
        app.logger.warning(
            'BOOKING_URL is not configured; the production conversion CTA '
            'will be hidden'
        )
    if not app.config['GOOGLE_ANALYTICS_MEASUREMENT_ID']:
        app.logger.warning(
            'GOOGLE_ANALYTICS_MEASUREMENT_ID is not configured; analytics '
            'and privacy controls will be disabled'
        )
    if not app.config['CONTACT_BROKER_URL']:
        app.logger.warning(
            'CONTACT_BROKER_URL is not configured; contact delivery is disabled'
        )
    if not app.config['CONTACT_BROKER_SECRET']:
        app.logger.warning(
            'CONTACT_BROKER_SECRET is not configured; contact delivery is disabled'
        )


def register_blueprints(app):
    """
    Register flask blueprints here.

    Flask blueprints enable more modular HTML / code development
    """

    # Some App Engine Python runtimes lack WebP in the system MIME registry.
    mimetypes.add_type('image/webp', '.webp')

    from core.home.home import index_bp  # noqa: E402
    app.register_blueprint(index_bp)


def register_error_handlers(app):
    @app.errorhandler(413)
    def request_too_large(e):
        message = 'The submitted message is too large.'
        if request.accept_mimetypes.best == 'application/json':
            return jsonify(
                {
                    'ok': False,
                    'message': message,
                    'errors': {},
                }
            ), 413
        return message, 413

    @app.errorhandler(404)
    def not_found(e):
        return render_template('home/404.html', analytics_page_path='/404'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('home/500.html', analytics_page_path='/500'), 500


def register_canonical_redirect(app, env):
    """Consolidate public domain variants without redirecting local previews."""
    site = urlsplit(app.config['SITE_URL'])
    if env != 'production' or not site.hostname:
        return

    public_hosts = {site.hostname, site.hostname.removeprefix('www.')}
    on_app_engine = os.environ.get('GAE_ENV') == 'standard'

    @app.before_request
    def canonical_redirect():
        if urlsplit(request.host_url).hostname not in public_hosts:
            return None

        # App Engine sets this header at its TLS-terminating frontend.
        # Never trust forwarded scheme headers on a standalone/local server.
        scheme = request.scheme
        if on_app_engine:
            scheme = request.headers.get('X-Forwarded-Proto', scheme)
        if scheme == site.scheme and request.host.lower() == site.netloc.lower():
            return None

        target = urlunsplit((
            site.scheme,
            site.netloc,
            quote(request.path, safe='/'),
            request.query_string.decode('latin-1'),
            '',
        ))
        # Preserve method/body for contact submissions as well as GET requests.
        return redirect(target, code=308)


def create_app(env=''):
    """
    Create APP!
    """

    app = Flask(__name__)

    env = env or os.environ.get('FLASK_ENV', 'production')
    app.config.from_object(app_config.get(env, app_config['default']))
    app.config['GOOGLE_ANALYTICS_MEASUREMENT_ID'] = os.environ.get(
        'GOOGLE_ANALYTICS_MEASUREMENT_ID',
        '',
    ).strip()
    app.config['GOOGLE_ANALYTICS_DEBUG'] = os.environ.get(
        'GOOGLE_ANALYTICS_DEBUG',
        '',
    ).strip().lower() in {'1', 'true', 'yes', 'on'}
    app.config['CONTACT_EMAIL'] = os.environ.get('CONTACT_EMAIL', '').strip()
    app.config['CONTACT_EMAIL'] = (
        app.config['CONTACT_EMAIL'] or 'tera@idea-factory.io'
    )
    contact_broker_url = os.environ.get('CONTACT_BROKER_URL', '').strip()
    app.config['CONTACT_DELIVERY_TIMEOUT_SECONDS'] = 15.0
    app.config['MAX_CONTENT_LENGTH'] = 32 * 1024
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600
    booking_url = os.environ.get('BOOKING_URL', '').strip()
    app.config['SEARCH_CONSOLE_VERIFICATION'] = os.environ.get(
        'SEARCH_CONSOLE_VERIFICATION',
        '',
    ).strip()
    site_url = os.environ.get('SITE_URL', '').strip()

    logging.basicConfig(
        level=app.config['LOG_LEVEL'],
        datefmt="%Y-%m-%d",
        format="%(levelname)s - %(message)s"
    )
    app.config['CONTACT_BROKER_SECRET'] = load_secret(
        'CONTACT_BROKER_SECRET',
        app.logger,
    )
    app.config['CONTACT_BROKER_URL'] = _validated_https_url(
        contact_broker_url,
        'CONTACT_BROKER_URL',
        app.logger,
    )
    app.config['BOOKING_URL'] = _validated_https_url(
        booking_url,
        'BOOKING_URL',
        app.logger,
    )
    app.config['SITE_URL'] = _validated_https_url(
        site_url,
        'SITE_URL',
        app.logger,
    )
    _warn_about_production_config(app, env)

    secret_key = load_secret('SECRET_KEY', app.logger)
    if not secret_key:
        if env == 'production':
            raise RuntimeError(
                'SECRET_KEY must be configured for production through the '
                'environment or Google Secret Manager'
            )
        else:
            secret_key = 'development-secret-key'
            app.logger.warning(
                "SECRET_KEY environment variable is not set; using the default development key"
            )
    app.config['SECRET_KEY'] = secret_key
    app.secret_key = secret_key

    register_canonical_redirect(app, env)
    register_blueprints(app)
    register_static_assets(app)
    register_error_handlers(app)

    return app
