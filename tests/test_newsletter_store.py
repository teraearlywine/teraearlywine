"""Subscriber transitions, provider retry identities, and transaction conflict replay."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from threading import RLock

from google.api_core.exceptions import Aborted
from google.cloud import datastore
import pytest

from core.home import newsletter_store as newsletter


class Transaction:
    def __init__(self, db):
        self.db = db
        self.writes = {}

    def __enter__(self):
        self.db.lock.acquire()
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            if not exc_type:
                if self.writes and self.db.abort_once:
                    self.db.abort_once = False
                    raise Aborted('synthetic transaction conflict')
                self.db.rows.update(deepcopy(self.writes))
        finally:
            self.db.lock.release()

    def put(self, row):
        self.writes[row.key] = row


class Database:
    def __init__(self):
        self.rows = {}
        self.lock = RLock()
        self.abort_once = False

    def key(self, kind, name):
        return datastore.Key(kind, name, project='newsletter-test')

    def transaction(self):
        return Transaction(self)

    def get(self, key, transaction=None):
        with self.lock:
            return deepcopy(self.rows.get(key))

    def get_multi(self, keys, transaction=None):
        assert transaction is not None
        return [self.get(key, transaction) for key in keys if key in self.rows]

    def subscribers(self):
        return [r for k, r in self.rows.items() if k.kind == 'NewsletterSubscriber']


@pytest.fixture
def store(monkeypatch):
    db = Database()
    monkeypatch.setattr(newsletter, 'get_datastore_client', lambda project: db)
    return newsletter.SubscriberStore('newsletter-test', 'private-test-secret')


@pytest.fixture
def clock(monkeypatch):
    now = [datetime(2026, 1, 1, tzinfo=timezone.utc)]
    monkeypatch.setattr(newsletter, '_now', lambda: now[0])

    def advance(**delta):
        now[0] += timedelta(**delta)

    return advance


def reserve(store, guide='teams', email='person@example.org', ip='192.0.2.2'):
    return store.reserve(email, guide, ip)


def test_pending_delivery_retries_until_sent_and_is_deduplicated_afterward(store, clock):
    first = reserve(store)
    assert first == reserve(store, email='  PERSON@EXAMPLE.ORG  ')
    assert first['email'] == 'person@example.org'
    row, = store.client.subscribers()
    assert first['token'].startswith(row.key.name + '.')
    assert row['state'] == 'pending' and row['audiences'] == []
    assert row['expires_at'] == row['pending_until']
    assert store.inspect(first['token']) == 'teams'
    assert store.mark_sent(first['token'])
    assert reserve(store) is None
    clock(minutes=11)
    second = reserve(store)
    assert second['request_id'] != first['request_id']
    assert second['token'] != first['token']
    assert store.confirm(first['token']) is None
    assert not store.mark_sent(first['token'])
    assert second == reserve(store)


def test_concurrent_reservations_and_conflict_replay_debit_only_one_slot(store):
    store.client.abort_once = True
    with ThreadPoolExecutor(max_workers=6) as pool:
        attempts = list(pool.map(lambda _: reserve(store), range(16)))
    assert all(sent == attempts[0] for sent in attempts)
    row, = store.client.subscribers()
    assert row['rate_count'] == 1
    assert all(v['count'] == 1 for k, v in store.client.rows.items() if k.kind == 'NewsletterSignupRate')


def test_send_acceptance_arriving_after_confirmation_preserves_cooldown(store, clock):
    first = reserve(store)
    assert store.confirm(first['token']) == 'teams'
    assert store.mark_sent(first['token'])
    clock(minutes=9)
    assert not store.mark_sent(first['token'])
    assert reserve(store) is None
    clock(minutes=2)
    assert reserve(store)


def test_active_audiences_change_only_at_confirmation(store, clock):
    one = reserve(store)
    assert store.mark_sent(one['token'])
    assert store.confirm(one['token']) == 'teams'
    assert reserve(store) is None
    row, = store.client.subscribers()
    confirmed_at = row['confirmed_at']
    unsub = row['unsubscribe_token']
    assert row['state'] == 'active' and 'expires_at' not in row
    two = reserve(store, 'professionals')
    assert store.client.subscribers()[0]['audiences'] == ['teams']
    assert store.confirm(one['token']) == 'teams'
    assert store.confirm(two['token']) == 'professionals'
    assert store.confirm(two['token']) == 'professionals'
    row, = store.client.subscribers()
    assert set(row['audiences']) == {'teams', 'professionals'}
    assert row['confirmed_at'] == confirmed_at and row['unsubscribe_token'] == unsub


def test_unsubscribe_cancels_outstanding_consent_and_old_tokens_cannot_reactivate(store):
    old = reserve(store)['token']
    assert store.confirm(old) == 'teams'
    row, = store.client.subscribers()
    optout = row['unsubscribe_token']
    waiting = reserve(store, 'both')['token']
    assert store.is_unsubscribe_token(optout) and store.unsubscribe(optout)
    assert store.unsubscribe(optout)
    assert not store.inspect(old) and not store.confirm(old) and not store.confirm(waiting)
    row, = store.client.subscribers()
    assert row['state'] == 'unsubscribed' and not row['audiences']
    fresh = reserve(store, 'professionals')['token']
    assert store.client.subscribers()[0]['state'] == 'unsubscribed'
    assert store.unsubscribe(optout)
    assert store.confirm(fresh) == 'professionals'
    row, = store.client.subscribers()
    assert row['audiences'] == ['professionals'] and row['unsubscribe_token'] != optout
    assert not store.unsubscribe(optout) and not store.is_unsubscribe_token(optout)
    assert store.confirm(old) is None


def test_expiry_does_not_depend_on_datastore_ttl_sweep(store, clock):
    first = reserve(store, 'both')
    clock(hours=24)
    assert not store.inspect(first['token']) and not store.confirm(first['token'])
    second = reserve(store, 'both')
    assert first['request_id'] != second['request_id']
    store.confirm(second['token'])
    assert set(store.client.subscribers()[0]['audiences']) == {'teams', 'professionals'}


def test_address_limits_apply_across_guide_changes_and_ips(store, monkeypatch, clock):
    monkeypatch.setattr(newsletter, 'ADDRESS_LIMIT', 2)
    assert reserve(store)
    assert reserve(store, 'both')
    assert reserve(store, 'professionals', ip='192.0.2.3') is None
    clock(hours=1)
    assert reserve(store, 'professionals')


def test_ip_and_global_limits_do_not_create_records_for_blocked_addresses(store, monkeypatch, clock):
    monkeypatch.setattr(newsletter, 'IP_LIMIT', 1)
    monkeypatch.setattr(newsletter, 'GLOBAL_LIMIT', 2)
    assert reserve(store)
    assert reserve(store, email='two@example.org') is None
    assert reserve(store, email='two@example.org', ip='192.0.2.3')
    assert reserve(store, email='three@example.org', ip='192.0.2.4') is None
    assert len(store.client.subscribers()) == 2
    clock(hours=1)
    assert reserve(store, email='three@example.org', ip='192.0.2.4')


def test_invalid_and_forged_inputs_do_not_create_rows_or_mutate_consent(store):
    assert reserve(store, guide='bogus') is None
    assert reserve(store, email='a\nb@example.org') is None
    assert reserve(store, email='x' * 280 + '@example.org') is None
    assert not store.client.rows
    first = reserve(store)
    bad = first['token'].split('.')[0] + '.' + 'A' * 43
    for token in ['', 'x', bad, '0' * 64 + '.' + 'A' * 43]:
        assert not store.inspect(token) and not store.confirm(token)
        assert not store.mark_sent(token) and not store.unsubscribe(token)
        assert not store.is_unsubscribe_token(token)
    assert reserve(store) == first


def test_state_transition_flags_fire_once_even_with_conflicts_and_concurrent_clicks(store):
    token = reserve(store)['token']
    with ThreadPoolExecutor(max_workers=5) as pool:
        store.client.abort_once = True
        assert sorted(pool.map(store.mark_sent, [token] * 5)) == [False] * 4 + [True]
        store.client.abort_once = True
        flags = list(pool.map(store.confirm_with_status, [token] * 5))
        assert flags.count(('teams', True)) == 1 and flags.count(('teams', False)) == 4
        assert store.mark_sent(token) is False
        next_request = reserve(store, 'professionals')
        assert store.confirm_with_status(next_request['token']) == ('professionals', False)
        optout = store.client.subscribers()[0]['unsubscribe_token']
        store.client.abort_once = True
        flags = list(pool.map(store.unsubscribe_with_status, [optout] * 5))
        assert flags.count((True, True)) == 1 and flags.count((True, False)) == 4
    assert store.confirm_with_status(next_request['token']) == (None, False)
    assert store.unsubscribe_with_status('bogus') == (False, False)
    assert store.confirm_with_status(reserve(store)['token']) == ('teams', True)
