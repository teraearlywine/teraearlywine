import pytest

from core import create_app


CONFIG_ENVIRONMENT_VARIABLES = (
    'BOOKING_URL',
    'CONTACT_BROKER_SECRET',
    'CONTACT_BROKER_SECRET_SECRET_ID',
    'CONTACT_BROKER_URL',
    'CONTACT_EMAIL',
    'CONTACT_TURNSTILE_SITE_KEY',
    'GOOGLE_ANALYTICS_DEBUG',
    'GOOGLE_ANALYTICS_MEASUREMENT_ID',
    'SEARCH_CONSOLE_VERIFICATION',
    'SECRET_KEY',
    'SECRET_KEY_SECRET_ID',
    'SITE_URL',
)


@pytest.fixture
def app_factory(monkeypatch):
    """Build isolated Flask apps with explicit public configuration."""

    def _make_app(env='development', **configuration):
        for variable in CONFIG_ENVIRONMENT_VARIABLES:
            monkeypatch.delenv(variable, raising=False)

        configuration.setdefault('SECRET_KEY', 'test-secret-key')
        for variable, value in configuration.items():
            monkeypatch.setenv(variable, value)

        app = create_app(env)
        app.config.update(TESTING=True)
        return app

    return _make_app
