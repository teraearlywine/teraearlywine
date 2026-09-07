import hashlib
import hmac
import json
import re
import shutil
import subprocess
from pathlib import Path

import httpx
import pytest

from core import create_app


PROJECT_ROOT = Path(__file__).parents[1]
MAIN_BEHAVIOR_TEST = PROJECT_ROOT / 'tests/main_behavior.test.js'
BROKER_URL = 'https://if-api.example/api/contact-deliveries'
BROKER_SECRET = 'contact-broker-test-secret'
TEST_NAME = 'Ada Lovelace'
TEST_EMAIL = 'ada@example.com'
TEST_ENGAGEMENT = 'Data Foundation Blueprint'
TEST_MESSAGE = 'I would like to discuss a trustworthy data platform.'


class StubResponse:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code
        self.request = httpx.Request('POST', 'https://upstream.example')

    def raise_for_status(self):
        if self.status_code >= 400:
            response = httpx.Response(
                self.status_code,
                request=self.request,
            )
            raise httpx.HTTPStatusError(
                'upstream request failed',
                request=self.request,
                response=response,
            )

    def json(self):
        return self.payload


def _hidden_value(document, field_name):
    match = re.search(
        rf'<input[^>]+name="{re.escape(field_name)}"[^>]+value="([^"]+)"',
        document,
    )
    assert match, f'missing hidden field {field_name}'
    return match.group(1)


def _contact_form(client):
    response = client.get('/')
    assert response.status_code == 200
    document = response.get_data(as_text=True)
    return {
        'csrf_token': _hidden_value(document, 'csrf_token'),
        'submission_id': _hidden_value(document, 'submission_id'),
        'name': TEST_NAME,
        'email': TEST_EMAIL,
        'engagement_type': TEST_ENGAGEMENT,
        'message': TEST_MESSAGE,
        'website': '',
    }, document


def _post_contact(client, form_data):
    return client.post(
        '/contact',
        data=form_data,
        headers={'Accept': 'application/json'},
    )


@pytest.fixture
def contact_app(app_factory):
    return app_factory(
        CONTACT_BROKER_URL=BROKER_URL,
        CONTACT_BROKER_SECRET=BROKER_SECRET,
    )


def test_home_renders_accessible_progressively_enhanced_contact_form(
    app_factory,
):
    client = app_factory(
        BOOKING_URL='https://calendar.example/book',
    ).test_client()
    form_data, document = _contact_form(client)

    assert '<form' in document
    assert 'method="post"' in document
    assert 'action="/contact"' in document
    assert 'data-contact-form' in document
    assert '<label for="name">Name</label>' in document
    assert '<label for="email">Email</label>' in document
    assert (
        '<label for="engagement_type">Potential engagement</label>'
        in document
    )
    assert '<label for="message">Message</label>' in document
    assert 'autocomplete="name"' in document
    assert 'autocomplete="email"' in document
    assert 'aria-live="polite"' in document
    assert 'maxlength="100"' in document
    assert 'maxlength="254"' in document
    assert 'maxlength="5000"' in document
    for engagement_type in (
        'Value / Risk Diagnostic',
        'Data Foundation Blueprint',
        'Production AI Lighthouse',
    ):
        assert engagement_type in document
    assert 'href="https://calendar.example/book"' in document
    assert form_data['csrf_token']
    assert re.fullmatch(
        r'[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}',
        form_data['submission_id'],
    )


def test_javascript_contact_form_behavior():
    node = shutil.which('node')
    if node is None:
        pytest.skip('Node.js runtime is unavailable')

    subprocess.run(
        [node, str(MAIN_BEHAVIOR_TEST)],
        cwd=PROJECT_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )


@pytest.mark.parametrize(
    ('field_name', 'field_value'),
    [
        ('name', ''),
        ('name', 'n' * 101),
        ('email', ''),
        ('email', 'not-an-email'),
        ('email', f"{'e' * 243}@example.test"),
        ('engagement_type', ''),
        ('engagement_type', 'Unlisted engagement'),
        ('message', ''),
        ('message', 'short'),
        ('message', 'm' * 5001),
    ],
)
def test_contact_rejects_invalid_fields_without_delivery(
    contact_app,
    monkeypatch,
    field_name,
    field_value,
):
    client = contact_app.test_client()
    form_data, _ = _contact_form(client)
    form_data[field_name] = field_value
    upstream_calls = []
    monkeypatch.setattr(
        'core.home.contact_delivery.httpx.post',
        lambda *args, **kwargs: upstream_calls.append((args, kwargs)),
    )

    response = _post_contact(client, form_data)

    assert response.status_code == 400
    assert response.json['ok'] is False
    assert field_name in response.json['errors']
    assert TEST_MESSAGE not in response.get_data(as_text=True)
    assert upstream_calls == []


@pytest.mark.parametrize('csrf_token', [None, 'invalid-token'])
def test_contact_enforces_csrf_without_delivery(
    contact_app,
    monkeypatch,
    csrf_token,
):
    client = contact_app.test_client()
    form_data, _ = _contact_form(client)
    if csrf_token is None:
        form_data.pop('csrf_token')
    else:
        form_data['csrf_token'] = csrf_token
    upstream_calls = []
    monkeypatch.setattr(
        'core.home.contact_delivery.httpx.post',
        lambda *args, **kwargs: upstream_calls.append((args, kwargs)),
    )

    response = _post_contact(client, form_data)

    assert response.status_code == 400
    assert response.json == {
        'errors': {},
        'message': 'Please check the highlighted fields and try again.',
        'ok': False,
    }
    assert upstream_calls == []


def test_contact_rejects_honeypot_without_echoing_or_delivery(
    contact_app,
    monkeypatch,
):
    client = contact_app.test_client()
    form_data, _ = _contact_form(client)
    form_data['website'] = 'https://spam.example/private'
    upstream_calls = []
    monkeypatch.setattr(
        'core.home.contact_delivery.httpx.post',
        lambda *args, **kwargs: upstream_calls.append((args, kwargs)),
    )

    response = _post_contact(client, form_data)

    assert response.status_code == 400
    assert response.json['ok'] is False
    assert response.json['errors'] == {}
    assert 'spam.example' not in response.get_data(as_text=True)
    assert upstream_calls == []


def test_success_sends_exact_signed_broker_payload(
    contact_app,
    monkeypatch,
):
    client = contact_app.test_client()
    form_data, _ = _contact_form(client)
    submission_id = form_data['submission_id']
    calls = []

    def post(url, **kwargs):
        calls.append((url, kwargs))
        return StubResponse({
            'submissionId': submission_id,
            'replayed': False,
        }, status_code=201)

    monkeypatch.setattr('core.home.contact_delivery.httpx.post', post)

    response = _post_contact(client, form_data)

    assert response.status_code == 200
    assert response.json['ok'] is True
    assert response.json['submission_id'] != submission_id
    assert len(calls) == 1
    broker_url, broker_request = calls[0]
    assert broker_url == BROKER_URL
    assert broker_request['json'] == {
        'email': TEST_EMAIL,
        'engagementType': TEST_ENGAGEMENT,
        'message': TEST_MESSAGE,
        'name': TEST_NAME,
        'submissionId': submission_id,
    }
    assert broker_request['timeout'] == 15.0
    timestamp = broker_request['headers']['X-Contact-Timestamp']
    canonical = json.dumps(
        broker_request['json'],
        ensure_ascii=False,
        separators=(',', ':'),
    )
    expected_signature = hmac.new(
        BROKER_SECRET.encode('utf-8'),
        f'{timestamp}.{canonical}'.encode('utf-8'),
        hashlib.sha256,
    ).hexdigest()
    assert re.fullmatch(r'\d{10}', timestamp)
    assert broker_request['headers'] == {
        'Content-Type': 'application/json',
        'X-Contact-Signature': expected_signature,
        'X-Contact-Timestamp': timestamp,
    }


def test_retry_reuses_submission_id_and_broker_confirms_both_deliveries(
    contact_app,
    monkeypatch,
):
    client = contact_app.test_client()
    form_data, _ = _contact_form(client)
    submission_id = form_data['submission_id']
    calls = []
    def post(url, **kwargs):
        calls.append((url, kwargs['json']))
        if len(calls) == 1:
            return StubResponse({'error': 'SERVICE_UNAVAILABLE'}, 503)
        return StubResponse({
            'submissionId': submission_id,
            'replayed': True,
        })

    monkeypatch.setattr('core.home.contact_delivery.httpx.post', post)

    first_response = _post_contact(client, form_data)
    second_response = _post_contact(client, form_data)

    assert first_response.status_code == 502
    assert first_response.json['ok'] is False
    assert second_response.status_code == 200
    assert second_response.json['ok'] is True
    assert calls == [
        (BROKER_URL, calls[0][1]),
        (BROKER_URL, calls[0][1]),
    ]
    assert calls[0][1]['submissionId'] == submission_id


def test_duplicate_success_reuses_receipt_without_duplicate_upstreams(
    contact_app,
    monkeypatch,
):
    client = contact_app.test_client()
    form_data, _ = _contact_form(client)
    calls = []

    def post(url, **kwargs):
        calls.append(url)
        return StubResponse({
            'submissionId': form_data['submission_id'],
            'replayed': False,
        })

    monkeypatch.setattr('core.home.contact_delivery.httpx.post', post)

    first_response = _post_contact(client, form_data)
    second_response = _post_contact(client, form_data)

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert calls == [BROKER_URL]


def test_duplicate_submission_id_rejects_changed_content(
    contact_app,
    monkeypatch,
):
    client = contact_app.test_client()
    form_data, _ = _contact_form(client)
    calls = []

    def post(url, **kwargs):
        calls.append(url)
        return StubResponse({
            'submissionId': form_data['submission_id'],
            'replayed': False,
        })

    monkeypatch.setattr('core.home.contact_delivery.httpx.post', post)

    first_response = _post_contact(client, form_data)
    changed_form_data = {**form_data, 'message': 'A different valid message.'}
    changed_response = _post_contact(client, changed_form_data)

    assert first_response.status_code == 200
    assert changed_response.status_code == 400
    assert changed_response.json == {
        'errors': {},
        'message': 'Please refresh the page and try again.',
        'ok': False,
    }
    assert calls == [BROKER_URL]


def test_timeout_returns_generic_error_without_secrets_or_submission_content(
    contact_app,
    monkeypatch,
    caplog,
):
    client = contact_app.test_client()
    form_data, _ = _contact_form(client)

    def timeout(*args, **kwargs):
        raise httpx.ReadTimeout('timed out')

    monkeypatch.setattr('core.home.contact_delivery.httpx.post', timeout)

    response = _post_contact(client, form_data)
    public_and_logged_text = response.get_data(as_text=True) + caplog.text

    assert response.status_code == 502
    assert response.json == {
        'errors': {},
        'message': 'We could not send your message right now. Please try again.',
        'ok': False,
    }
    for private_value in (
        TEST_NAME,
        TEST_EMAIL,
        TEST_MESSAGE,
        BROKER_SECRET,
    ):
        assert private_value not in public_and_logged_text


def test_broker_receipt_must_match_submission_without_echoing_response(
    contact_app,
    monkeypatch,
    caplog,
):
    client = contact_app.test_client()
    form_data, _ = _contact_form(client)
    monkeypatch.setattr(
        'core.home.contact_delivery.httpx.post',
        lambda *args, **kwargs: StubResponse({
            'submissionId': '25d39baa-b801-40de-a31c-a50db98f6051',
            'replayed': False,
            'detail': TEST_MESSAGE,
        }),
    )

    response = _post_contact(client, form_data)
    public_and_logged_text = response.get_data(as_text=True) + caplog.text

    assert response.status_code == 502
    assert response.json['ok'] is False
    assert TEST_MESSAGE not in public_and_logged_text


def test_html_delivery_failure_does_not_echo_submission_content(
    contact_app,
    monkeypatch,
):
    client = contact_app.test_client()
    form_data, _ = _contact_form(client)

    def timeout(*args, **kwargs):
        raise httpx.ReadTimeout('timed out')

    monkeypatch.setattr('core.home.contact_delivery.httpx.post', timeout)

    response = client.post('/contact', data=form_data)
    document = response.get_data(as_text=True)

    assert response.status_code == 502
    assert 'We could not send your message right now. Please try again.' in document
    for private_value in (TEST_NAME, TEST_EMAIL, TEST_MESSAGE):
        assert private_value not in document


def test_request_size_limit_returns_generic_json_without_delivery(
    contact_app,
    monkeypatch,
):
    client = contact_app.test_client()
    form_data, _ = _contact_form(client)
    form_data['message'] = 'private-content-' * 3000
    upstream_calls = []
    monkeypatch.setattr(
        'core.home.contact_delivery.httpx.post',
        lambda *args, **kwargs: upstream_calls.append((args, kwargs)),
    )

    response = _post_contact(client, form_data)

    assert response.status_code == 413
    assert response.is_json
    assert response.json == {
        'errors': {},
        'message': 'The submitted message is too large.',
        'ok': False,
    }
    assert 'private-content' not in response.get_data(as_text=True)
    assert upstream_calls == []


def test_production_requires_stable_secret_key(monkeypatch):
    for variable in (
        'SECRET_KEY',
        'SECRET_KEY_SECRET_ID',
    ):
        monkeypatch.delenv(variable, raising=False)

    with pytest.raises(RuntimeError, match='SECRET_KEY'):
        create_app('production')


def test_deployment_config_references_secret_manager_without_secret_values():
    deployment_config = (PROJECT_ROOT / 'app.yaml').read_text()

    assert 'CONTACT_BROKER_SECRET_SECRET_ID:' in deployment_config
    assert 'SECRET_KEY_SECRET_ID:' in deployment_config
    assert re.search(
        r'^\s+CONTACT_BROKER_SECRET:',
        deployment_config,
        re.MULTILINE,
    ) is None
    assert re.search(r'^\s+SECRET_KEY:', deployment_config, re.MULTILINE) is None
