"""Response-policy coverage for browser framing defenses."""

import pytest
from flask import make_response


FRAME_ANCESTORS_POLICY = "frame-ancestors 'none'"


def assert_not_frameable(response):
    assert FRAME_ANCESTORS_POLICY in response.headers.getlist(
        'Content-Security-Policy',
    )
    assert response.headers['X-Frame-Options'] == 'DENY'


@pytest.mark.parametrize(('path', 'expected_status'), [
    ('/', 200),
    ('/services/data-migration-rescue', 200),
    ('/missing', 404),
])
def test_public_pages_and_not_found_errors_cannot_be_framed(
    app_factory,
    path,
    expected_status,
):
    response = app_factory().test_client().get(path)

    assert response.status_code == expected_status
    assert_not_frameable(response)


def test_server_error_pages_cannot_be_framed(app_factory):
    app = app_factory()

    @app.get('/_force-server-error')
    def force_server_error():
        raise RuntimeError('intentional test error')

    app.config.update(TESTING=False, PROPAGATE_EXCEPTIONS=False)
    response = app.test_client().get('/_force-server-error')

    assert response.status_code == 500
    assert_not_frameable(response)


def test_existing_content_security_policy_is_preserved(app_factory):
    app = app_factory()

    @app.get('/_custom-content-policy')
    def custom_content_policy():
        response = make_response('policy composition')
        response.headers['Content-Security-Policy'] = "default-src 'none'"
        return response

    response = app.test_client().get('/_custom-content-policy')

    assert response.headers.getlist('Content-Security-Policy') == [
        "default-src 'none'",
        FRAME_ANCESTORS_POLICY,
    ]
    assert_not_frameable(response)
