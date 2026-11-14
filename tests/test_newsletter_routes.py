"""Run signup through the logged-out browser routes; fake only storage and email I/O."""
import re
from types import SimpleNamespace
from urllib.parse import urlsplit

import pytest

from core.home import newsletter, newsletter_store
from test_analytics_reporting import collect_elements
from test_newsletter_store import Database

EMAIL = 'reader@example.org'
SIGNUP = '/newsletter/'
PENDING = '/newsletter/check-email/'
DOWNLOADS = '/newsletter/guides/'
UNSUBSCRIBED = '/newsletter/unsubscribed/'


@pytest.fixture
def flow(app_factory, monkeypatch):
    db = Database()
    monkeypatch.setattr(newsletter_store, 'get_datastore_client', lambda project: db)
    app = app_factory(
        SITE_URL='https://site.example',
        GOOGLE_ANALYTICS_MEASUREMENT_ID='G-PORTFOLIO1',
        NEWSLETTER_FROM='Tera <sender@example.org>',
        NEWSLETTER_IDENTITY_KEY='signup-test-key',
        RESEND_API_KEY='test-provider',
        GOOGLE_CLOUD_PROJECT='newsletter-test',
    )
    mail = []
    monkeypatch.setattr(newsletter, 'send_email', lambda key, payload, request_id: mail.append((payload, request_id)))
    return SimpleNamespace(app=app, client=app.test_client(), db=db, mail=mail)


def hidden(response):
    return {tag['name']: tag['value'] for tag in collect_elements(response.text, 'input')
            if tag.get('type') == 'hidden'}


def submit(flow, selection, **changes):
    page = flow.client.get(SIGNUP)
    data = {**hidden(page), 'email': EMAIL, 'guide': selection, 'consent': 'y', **changes}
    return flow.client.post(SIGNUP, data=data)


def assert_redirect(response, path):
    assert response.status_code == 303
    assert response.location == path


def form_post(client, path):
    page = client.get(path)
    assert page.status_code == 200
    return client.post(path, data=hidden(page))


def confirm_path(flow):
    payload, _ = flow.mail[-1]
    url = re.search(r'https://site\.example/newsletter/confirm/\S+', payload['text'])
    assert url
    return urlsplit(url[0]).path


def receipt(response):
    return next((tag for tag in collect_elements(response.text, 'main')
                 if 'data-newsletter-receipt' in tag), {})


def assert_private(response, status=200):
    assert response.status_code == status
    assert response.headers['Cache-Control'] == 'no-store'
    assert response.headers['Referrer-Policy'] == 'no-referrer'
    assert response.headers['X-Robots-Tag'] == 'noindex, nofollow'
    for term in ['analyticsConfig', 'js/analytics.js', 'googletagmanager.com', 'data-consent-choice=']:
        assert term not in response.text
    assert not receipt(response)


@pytest.mark.parametrize(('choice', 'checked'), [('', 'both'), ('?guide=professionals', 'professionals'),
                         ('?guide=teams', 'teams'), ('?guide=unknown', 'both')])
def test_signup_preselects_only_the_intended_guide_and_leaves_consent_open(flow, choice, checked):
    page = flow.client.get(SIGNUP + choice)
    assert page.status_code == 200 and hidden(page)['csrf_token']
    inputs = collect_elements(page.text, 'input')
    assert [tag['value'] for tag in inputs if tag.get('name') == 'guide' and 'checked' in tag] == [checked]
    consent = next(tag for tag in inputs if tag.get('name') == 'consent')
    assert 'checked' not in consent and 'required' in consent
    assert 'analyticsConfig' in page.text


@pytest.mark.parametrize('invalid', [
    {'consent': ''}, {'email': 'invalid'}, {'guide': 'invalid'},
    {'csrf_token': ''}, {'website': 'honey'},
])
def test_invalid_signup_rejects_without_email_writes_or_analytics(flow, invalid):
    response = submit(flow, 'teams', **invalid)
    assert_private(response, 400)
    assert not flow.mail and not flow.db.rows
    assert not receipt(flow.client.get(PENDING))


@pytest.mark.parametrize('guide', ['teams', 'professionals', 'both'])
def test_inbox_confirmation_download_and_once_only_receipts(flow, guide):
    assert_redirect(flow.client.get(DOWNLOADS), SIGNUP)
    assert_redirect(submit(flow, guide), PENDING)
    assert len(flow.mail) == 1
    payload, request_id = flow.mail[0]
    assert payload['to'] == [EMAIL] and 'Confirm' in payload['subject']
    assert request_id.startswith('newsletter-optin-')
    selected = set(newsletter.GUIDES) if guide == 'both' else {guide}
    assert all((title in payload['text']) == (key in selected)
               for key, (title, _) in newsletter.GUIDES.items())
    page = flow.client.get(PENDING)
    assert receipt(page)['data-newsletter-receipt'] == 'newsletter_signup'
    assert receipt(page)['data-guide'] == guide
    assert '"pagePath": "/newsletter/check-email/"' in page.text
    assert not receipt(flow.client.get(PENDING))
    assert_redirect(submit(flow, guide), PENDING)
    assert len(flow.mail) == 1 and not receipt(flow.client.get(PENDING))

    path = confirm_path(flow)
    assert_private(flow.client.get(path))
    assert flow.db.subscribers()[0]['state'] == 'pending'
    assert_private(flow.client.post(path, data={'token': path.split('/')[-1]}), 400)
    token_form = hidden(flow.client.get(path))
    assert_private(flow.client.post(path, data={**token_form, 'token': 'wrong-token'}), 400)
    assert flow.db.subscribers()[0]['state'] == 'pending'
    redirect = flow.client.post(path, data=token_form)
    assert_redirect(redirect, DOWNLOADS)
    assert redirect.headers['Referrer-Policy'] == 'no-referrer'
    assert redirect.headers['Cache-Control'] == 'no-store'
    assert set(flow.db.subscribers()[0]['audiences']) == selected

    page = flow.client.get(DOWNLOADS)
    assert receipt(page)['data-newsletter-receipt'] == 'newsletter_confirm'
    assert receipt(page)['data-guide'] == guide and EMAIL not in page.text and path not in page.text
    assert '"pagePath": "/newsletter/guides/"' in page.text
    links = [tag for tag in collect_elements(page.text, 'a') if 'download' in tag]
    assert {tag['data-guide'] for tag in links} == selected
    for link in links:
        assert link['data-analytics-event'] == 'newsletter_guide_download'
        pdf = flow.client.get(link['href'])
        assert pdf.mimetype == 'application/pdf' and pdf.data.startswith(b'%PDF-')
    assert not receipt(flow.client.get(DOWNLOADS))
    assert_redirect(form_post(flow.client, path), DOWNLOADS)
    assert not receipt(flow.client.get(DOWNLOADS))


def test_signup_with_provider_failure_recovers_using_identical_email_and_request_id(flow, monkeypatch):
    def fail_once(key, payload, request_id):
        flow.mail.append((payload, request_id))
        if len(flow.mail) == 1:
            raise RuntimeError('simulated provider timeout')

    monkeypatch.setattr(newsletter, 'send_email', fail_once)
    assert_private(submit(flow, 'both'), 503)
    assert not receipt(flow.client.get(PENDING))
    assert_redirect(submit(flow, 'both'), PENDING)
    assert len(flow.mail) == 2 and flow.mail[0] == flow.mail[1]
    assert receipt(flow.client.get(PENDING))['data-newsletter-receipt'] == 'newsletter_signup'
    assert_redirect(submit(flow, 'both'), PENDING)
    assert len(flow.mail) == 2 and not receipt(flow.client.get(PENDING))


def test_expired_or_forged_links_expose_no_analytics(flow):
    assert_private(flow.client.get('/newsletter/confirm/not-a-token'), 410)
    assert_private(flow.client.get('/newsletter/unsubscribe/not-a-token'), 410)
    assert_private(flow.client.post('/newsletter/unsubscribe/not-a-token',
                   data={'List-Unsubscribe': 'One-Click'}), 410)
    assert not flow.db.rows


def test_confirming_a_second_audience_adds_access_without_a_new_acquisition(flow):
    for guide in ('teams', 'professionals'):
        assert_redirect(submit(flow, guide), PENDING)
        assert_redirect(form_post(flow.client, confirm_path(flow)), DOWNLOADS)
        event = receipt(flow.client.get(DOWNLOADS))
        assert bool(event) == (guide == 'teams')
    assert set(flow.db.subscribers()[0]['audiences']) == {'teams', 'professionals'}


@pytest.mark.parametrize('machine', [False, True])
def test_unsubscribe_is_idempotent_and_scanners_cannot_trigger_it_with_get(flow, machine):
    assert_redirect(submit(flow, 'teams'), PENDING)
    confirmation = confirm_path(flow)
    assert_redirect(form_post(flow.client, confirmation), DOWNLOADS)
    unsubscription = '/newsletter/unsubscribe/' + flow.db.subscribers()[0]['unsubscribe_token']
    assert_private(flow.client.get(unsubscription))
    assert_private(flow.client.post(unsubscription, data={'token': unsubscription.split('/')[-1]}), 400)
    assert flow.db.subscribers()[0]['state'] == 'active'

    if machine:
        agent = flow.app.test_client()
        for _ in range(2):
            response = agent.post(unsubscription, data={'List-Unsubscribe': 'One-Click'})
            assert response.status_code == 200 and response.data == b''
            assert response.headers['Referrer-Policy'] == 'no-referrer'
        assert_redirect(agent.get(UNSUBSCRIBED), SIGNUP)
    else:
        for first in (True, False):
            assert_redirect(form_post(flow.client, unsubscription), UNSUBSCRIBED)
            page = flow.client.get(UNSUBSCRIBED)
            assert receipt(page).get('data-newsletter-receipt') == ('newsletter_unsubscribe' if first else None)
            assert unsubscription not in page.text and EMAIL not in page.text
            assert '"pagePath": "/newsletter/unsubscribed/"' in page.text
            assert not receipt(flow.client.get(UNSUBSCRIBED))
        assert_redirect(flow.client.get(DOWNLOADS), SIGNUP)
    assert flow.db.subscribers()[0]['state'] == 'unsubscribed'
    assert_private(flow.client.get(confirmation), 410)
