"""Real HTTP broker + Firestore emulator. See docs/contact-spam.md to run."""
import os

import httpx
import pytest

from test_contact import _contact_form, _post_contact

BROKER = os.environ.get('CONTACT_E2E_BROKER', '')
pytestmark = pytest.mark.skipif(not BROKER, reason='local broker/emulator not requested')
TEMPLATES = [
    'হাই, আমি আপনার মূল্য জানতে চেয়েছিলাম.',
    'Ողջույն, ես ուզում էի իմանալ ձեր գինը.',
    'Hæ, ég vildi vita verð þitt.',
    'Salam, qiymətinizi bilmək istədim.',
    'Hi, ego volo scire vestri pretium.',
    'Ola, quería saber o seu prezo.',
    'Ciao, volevo sapere il tuo prezzo.',
]


@pytest.fixture
def e2e(app_factory):
    assert BROKER == 'http://127.0.0.1:8787'
    httpx.post(f'{BROKER}/_test/reset').raise_for_status()
    app = app_factory(CONTACT_BROKER_SECRET='contact-broker-test-secret')
    app.config['CONTACT_BROKER_URL'] = f'{BROKER}/contact-deliveries'
    return app


def counts():
    return httpx.get(f'{BROKER}/_test/counts').json()


def submit(app, **changes):
    client = app.test_client()
    form, _ = _contact_form(client)
    form.update(changes)
    return _post_contact(client, form)


@pytest.mark.parametrize('message', TEMPLATES)
@pytest.mark.parametrize('email', ['hsilojhonaisy@gmail.com', 'gregoryj8tl2g@gmail.com', 'changed@example.com'])
def test_known_spam_has_zero_downstream_effects(e2e, message, email):
    response = submit(e2e, name='Roberttek', email=email, message=message)
    assert response.status_code == 403
    assert counts() == dict(requests=1, reservations=0, emails=0, linear=0, completions=0)


@pytest.mark.parametrize('message', TEMPLATES + ['What is the price of a data assessment?'])
def test_normal_gmail_robert_prefix_and_multilingual_price_pass(e2e, message):
    response = submit(e2e, name='Robert Smith', email='normal@gmail.com', message=message)
    assert response.status_code == 200
    assert response.json['ok'] is True
    assert counts() == dict(requests=1, reservations=1, emails=1, linear=1, completions=1)


def test_cross_session_normalized_duplicate_is_suppressed(e2e):
    assert submit(e2e, email='NORMAL@gmail.com', message='Please discuss pricing!').json['ok'] is True
    response = submit(e2e, email=' normal@GMAIL.com ', message='Please\n discuss pricing？？')
    assert response.status_code == 200
    assert response.json['ok'] is False
    assert counts()['emails'] == counts()['linear'] == 1


def test_honeypot_does_not_even_reach_broker(e2e):
    assert submit(e2e, website='populated').status_code == 400
    assert counts() == dict(requests=0, reservations=0, emails=0, linear=0, completions=0)


def test_rate_limit_stops_new_delivery(e2e):
    for i in range(5):
        assert submit(e2e, message=f'Unique legitimate inquiry {i}').json['ok'] is True
    assert submit(e2e, message='Another legitimate inquiry').status_code == 429
    assert counts()['emails'] == counts()['linear'] == 5


def test_challenge_required_and_solved_retry(e2e):
    for i in range(2):
        assert submit(e2e, email=f'person{i}@gmail.com', message='Tell me the price please.').json['ok'] is True
    client = e2e.test_client()
    form, _ = _contact_form(client)
    form.update(email='person3@gmail.com', message='Tell me the price please.')
    response = _post_contact(client, form)
    assert response.status_code == 403
    assert response.json['challenge_required'] is True
    assert counts()['emails'] == 2
    form['cf-turnstile-response'] = 'forged'
    assert _post_contact(client, form).status_code == 403
    assert counts()['emails'] == 2
    form['cf-turnstile-response'] = 'test-fixture-solved'
    assert _post_contact(client, form).json['ok'] is True
    assert counts()['emails'] == counts()['linear'] == 3


def test_november_richard_template_has_zero_effects(e2e):
    response = submit(e2e, name='RichardVax', email='changed@gmx.com',
                      message='Gfihudwgfyehjwowjifwhu fuehiqokewwfueiweqijwihrwu ifwiqdjwrhwijwijwirhwu teraearlywine.com')
    assert response.status_code == 403
    assert counts() == dict(requests=1, reservations=0, emails=0, linear=0, completions=0)


@pytest.mark.parametrize('name,email', [
    ('Roberttek', 'rotated@gmail.com'),
    ('RichardVax', 'rotated@gmx.com'),
    ('Changed name', 'aveyekoha655@gmail.com'),
    ('Changed name', 'alan-baker424245242@gmx.com'),
])
def test_rotated_campaign_requires_verification_and_delivers_once(e2e, name, email):
    client = e2e.test_client()
    form, _ = _contact_form(client)
    form.update(name=name, email=email, message='Could we discuss a data assessment for our team?')
    response = _post_contact(client, form)
    assert response.status_code == 403
    assert response.json['challenge_required'] is True
    assert counts() == dict(requests=1, reservations=0, emails=0, linear=0, completions=0)
    form['cf-turnstile-response'] = 'forged'
    assert _post_contact(client, form).status_code == 403
    assert counts() == dict(requests=2, reservations=0, emails=0, linear=0, completions=0)
    form['cf-turnstile-response'] = 'test-fixture-solved'
    assert _post_contact(client, form).json['ok'] is True
    assert counts() == dict(requests=3, reservations=1, emails=1, linear=1, completions=1)
    # Session retry and a new-session duplicate must not create new deliveries.
    form['cf-turnstile-response'] = ''
    assert _post_contact(client, form).json['ok'] is True
    duplicate = submit(e2e, name=name, email=email, message=form['message'])
    assert duplicate.status_code == 200
    assert duplicate.json['ok'] is False
    assert counts() == dict(requests=4, reservations=1, emails=1, linear=1, completions=1)


@pytest.mark.parametrize('name,email', [('Richard Vax', 'normal@gmx.com'), ('Robert Smith', 'normal@gmail.com')])
def test_ordinary_names_domains_and_generic_price_question_pass(e2e, name, email):
    response = submit(e2e, name=name, email=email, message='What is your price?')
    assert response.json['ok'] is True
    assert counts()['emails'] == counts()['linear'] == 1
