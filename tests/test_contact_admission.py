"""Transactional source budgets for the public contact broker boundary."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from threading import RLock

from google.cloud import datastore
import pytest

from core.home import contact_admission as admission


class Transaction:
    def __init__(self, database):
        self.database = database
        self.writes = {}

    def __enter__(self):
        self.database.lock.acquire()
        return self

    def __exit__(self, exc_type, exc, traceback):
        try:
            if not exc_type:
                self.database.rows.update(deepcopy(self.writes))
        finally:
            self.database.lock.release()

    def put(self, row):
        self.writes[row.key] = row


class Database:
    def __init__(self):
        self.rows = {}
        self.lock = RLock()

    def key(self, kind, name):
        return datastore.Key(kind, name, project='contact-admission-test')

    def transaction(self):
        return Transaction(self)

    def get(self, key, transaction=None):
        with self.lock:
            return deepcopy(self.rows.get(key))


@pytest.fixture
def store(monkeypatch):
    database = Database()
    monkeypatch.setattr(
        admission,
        'get_datastore_client',
        lambda project: database,
    )
    return admission.ContactAdmissionStore(
        'contact-admission-test',
        'private-test-secret',
    )


@pytest.fixture
def clock(monkeypatch):
    now = [datetime(2026, 1, 1, tzinfo=timezone.utc)]
    monkeypatch.setattr(admission, '_now', lambda: now[0])

    def advance(**delta):
        now[0] += timedelta(**delta)

    return advance


def test_source_budget_isolated_and_hides_network_address(
    store,
    monkeypatch,
):
    monkeypatch.setattr(admission, 'SOURCE_LIMIT', 2)

    assert store.admit('192.0.2.8')
    assert store.admit('192.0.2.8')
    assert not store.admit('192.0.2.8')
    assert store.admit('198.51.100.9')

    assert len(store.client.rows) == 2
    assert all(key.kind == 'ContactAdmissionRate' for key in store.client.rows)
    assert all(len(key.name) == 64 for key in store.client.rows)
    assert '192.0.2.8' not in repr(store.client.rows)
    assert '198.51.100.9' not in repr(store.client.rows)


def test_expired_bucket_reopens_without_ttl_deletion(
    store,
    monkeypatch,
    clock,
):
    monkeypatch.setattr(admission, 'SOURCE_LIMIT', 1)

    assert store.admit('192.0.2.8')
    assert not store.admit('192.0.2.8')
    clock(minutes=15)
    assert store.admit('192.0.2.8')

    bucket, = store.client.rows.values()
    assert bucket['count'] == 1
    assert bucket['expires_at'] == datetime(
        2026,
        1,
        1,
        0,
        30,
        tzinfo=timezone.utc,
    )


def test_concurrent_attempts_cannot_overdraw_source_budget(
    store,
    monkeypatch,
):
    monkeypatch.setattr(admission, 'SOURCE_LIMIT', 5)

    with ThreadPoolExecutor(max_workers=12) as pool:
        decisions = list(pool.map(
            lambda _: store.admit('192.0.2.8'),
            range(20),
        ))

    assert decisions.count(True) == 5
    assert decisions.count(False) == 15
    bucket, = store.client.rows.values()
    assert bucket['count'] == 5


def test_invalid_persisted_bucket_fails_closed(store):
    key = store._source_key('192.0.2.8')
    bucket = datastore.Entity(key)
    bucket.update(count='1', expires_at='later')
    store.client.rows[key] = bucket

    with pytest.raises(admission.ContactAdmissionError):
        store.admit('192.0.2.8')
