from datetime import datetime, timedelta, timezone

from google.cloud.datastore import Entity, Key

from scripts import send_newsletter as newsletter


class LocalDatastore:
    def __init__(self):
        self.records = {}
        self.selected = []

    def key(self, kind, name):
        return Key(kind, name, project='test')

    def transaction(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def get(self, key, transaction):
        return self.records.get(key)

    def put(self, entity):
        self.records[entity.key] = entity

    def query(self, kind):
        assert kind == 'NewsletterSubscriber'
        return self

    def add_filter(self, *, filter):
        assert filter.property_name == 'state' and filter.value == 'active'

    def keys_only(self):
        pass

    def fetch(self):
        return list(self.selected)

    def create_subscriber(self, name, **updates):
        entity = Entity(self.key('NewsletterSubscriber', name))
        entity.update(state='active', email=f'{name}@example.test', audiences=['teams'],
                      unsubscribe_token=f'{name}.abc123',
                      confirmed_at=datetime.now(timezone.utc) - timedelta(days=1))
        entity.update(updates)
        self.put(entity)
        self.selected.append(entity)
        return entity


def edition(**updates):
    return newsletter.Issue(**{
        'slug': 'november', 'subject': 'Choosing a pilot', 'body': 'Try one workflow.',
        'address': 'Example Business, 100 Example Road', 'sender': 'Tera <tera@example.test>',
        'site': 'https://example.test', 'audience': 'teams', **updates,
    })


def test_repeated_runs_deliver_once_only_to_confirmed_matching_readers(monkeypatch):
    client = LocalDatastore()
    client.create_subscriber('eligible')
    client.create_subscriber('other-audience', audiences=['professionals'])
    client.create_subscriber('no-longer-active', state='unsubscribed')
    client.create_subscriber('unconfirmed', confirmed_at=None)
    issued = []
    def accept(api_key, payload, key):
        issued.append((payload, key))
        return 'receipt'
    monkeypatch.setattr(newsletter, 'send_email', accept)
    assert newsletter.deliver_issue(client, edition(), 'test') == {'accepted': 1, 'ineligible': 3}

    client.create_subscriber('new', confirmed_at=datetime.now(timezone.utc) + timedelta(seconds=1))
    assert newsletter.deliver_issue(client, edition(), 'test') == {'already accepted': 1, 'ineligible': 4}
    assert len(issued) == 1
    payload, key = issued[0]
    assert key == 'newsletter-issue/november.eligible'
    assert payload['to'] == ['eligible@example.test']
    assert payload['headers']['List-Unsubscribe-Post'] == 'List-Unsubscribe=One-Click'
    assert payload['headers']['List-Unsubscribe'] == '<https://example.test/newsletter/unsubscribe/eligible.abc123>'
    assert edition().address in payload['text'] and 'eligible.abc123' in payload['text']
    assert ('https://example.test/blog/?utm_source=newsletter&utm_medium=email'
            '&utm_campaign=business_of_technology&utm_content=issue') in payload['text']


def test_campaign_cannot_change_content_or_audience_after_start():
    import pytest
    client = LocalDatastore()
    now = datetime.now(timezone.utc)
    assert newsletter.bind_issue(client, edition(), now) == now
    for changed in [edition(subject='Edited subject'), edition(audience='all')]:
        with pytest.raises(ValueError):
            newsletter.bind_issue(client, changed, now)


def test_unknown_outcome_retries_only_identical_payload_within_provider_window():
    client = LocalDatastore()
    subscriber = client.create_subscriber('reader')
    now = datetime.now(timezone.utc)
    def claim(elapsed):
        return newsletter.claim_delivery(client, edition(), subscriber.key, now, now + elapsed)
    status, original = claim(timedelta())
    assert status == 'ready'
    assert claim(timedelta(seconds=20))[0] == 'in progress'
    assert claim(timedelta(minutes=3)) == ('ready', original)
    subscriber['unsubscribe_token'] = 'rotated'
    assert claim(timedelta(minutes=7))[0] == 'needs review'
    subscriber['unsubscribe_token'] = 'reader.abc123'
    assert claim(timedelta(hours=23))[0] == 'needs review'
    subscriber['state'] = 'unsubscribed'
    assert claim(timedelta(hours=24))[0] == 'ineligible'


def test_preview_never_opens_datastore_or_sends(monkeypatch, tmp_path, capsys):
    def forbidden(*args, **kwargs):
        raise AssertionError('preview touched a live service')
    monkeypatch.setattr(newsletter, 'get_datastore_client', forbidden)
    monkeypatch.setattr(newsletter, 'send_email', forbidden)
    monkeypatch.setattr(newsletter, 'load_secret', forbidden)
    monkeypatch.setenv('NEWSLETTER_FROM', 'Tera <tera@example.test>')
    body = tmp_path / 'issue.txt'
    body.write_text('Try one workflow.')
    assert newsletter.main(['--issue', 'november', '--subject', 'One pilot', '--body', str(body),
                            '--address', 'Example Business, 100 Example Road']) == 0
    output = capsys.readouterr().out
    assert 'One pilot' in output and 'Try one workflow.' in output and 'Unsubscribe:' in output
