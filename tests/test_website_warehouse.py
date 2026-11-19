"""Pure safety tests; no credentials or external data."""
from datetime import datetime, timezone
from types import SimpleNamespace
import pytest
from scripts import sync_website_warehouse as sync

NOW = datetime(2026, 11, 18, 16, tzinfo=timezone.utc)

class Entity(dict):
    key = SimpleNamespace(name='a' * 64)

def entity(**kwargs):
    return Entity(email='reader@example.com', state='active', audiences=['teams'],
                  confirmed_at=NOW, pending_token='secret', **kwargs)

def test_allowlist_excludes_private_fields():
    row = sync.snapshot_rows([entity(ip='private', future_secret='secret')], NOW)[0]
    assert set(row) == {'subscriber_id', 'email', 'state', 'audiences', 'confirmed_at',
                        'unsubscribed_at', 'snapshot_at'}
    assert row['subscriber_id'] == 'a' * 64
    assert row['snapshot_at'] == NOW.isoformat()

def test_unsubscribed_kept_without_active_timestamp():
    row = Entity(email='reader@example.com', state='unsubscribed', audiences=[], unsubscribed_at=NOW)
    result = sync.snapshot_rows([row], NOW)[0]
    assert result['state'] == 'unsubscribed'
    assert result['confirmed_at'] is None

def test_duplicate_ids_fail():
    with pytest.raises(ValueError, match='Duplicate'):
        sync.snapshot_rows([entity(), entity()], NOW)

@pytest.mark.parametrize('field,value', [('state', 'unknown'), ('audiences', ['other']),
                                         ('email', ''), ('confirmed_at', 'bad')])
def test_invalid_source_fails(field, value):
    row = entity()
    row[field] = value
    with pytest.raises(ValueError):
        sync.snapshot_rows([row], NOW)

def test_partial_read_fails_before_return():
    def partial():
        yield entity()
        raise RuntimeError('pagination failed')
    with pytest.raises(RuntimeError):
        sync.snapshot_rows(partial(), NOW)

def test_bounded_extraction():
    with pytest.raises(ValueError, match='limit'):
        sync.snapshot_rows([entity()], NOW, max_rows=0)

def test_identifier_validation():
    with pytest.raises(ValueError):
        sync.table_ref('project', 'bad;DELETE', 'table')

class Result:
    def result(self):
        return []

class Warehouse:
    def __init__(self, ttl=86400000, location='US'):
        self.ttl, self.location = ttl, location
        self.loads, self.queries = [], []
    def get_dataset(self, name):
        return SimpleNamespace(default_table_expiration_ms=self.ttl, location=self.location)
    def load_table_from_json(self, rows, destination, **kwargs):
        self.loads.append((rows, destination, kwargs))
        return Result()
    def query(self, sql, **kwargs):
        self.queries.append((sql, kwargs))
        return Result()

class Source:
    def __init__(self, rows):
        self.rows = rows
    def query(self, kind):
        assert kind == 'NewsletterSubscriber'
        return SimpleNamespace(fetch=lambda: iter(self.rows))

def test_runner_refuses_same_staging_dataset():
    bq = Warehouse()
    with pytest.raises(ValueError, match='separate'):
        sync.run(Source([entity()]), bq, 'teraearlywine', 'private', 'private', 'US')
    assert not bq.loads

@pytest.mark.parametrize('ttl', [None, 0, 86400001])
def test_stage_requires_short_expiry(ttl):
    bq = Warehouse(ttl=ttl)
    with pytest.raises(ValueError):
        sync.run(Source([entity()]), bq, 'teraearlywine', 'private', 'staging', 'US')
    assert not bq.loads

def test_runner_never_loads_partial_extraction():
    def broken():
        yield entity()
        raise RuntimeError('lost source')
    bq = Warehouse()
    with pytest.raises(RuntimeError):
        sync.run(Source(broken()), bq, 'teraearlywine', 'private', 'staging', 'US')
    assert not bq.loads and not bq.queries

def test_runner_load_failure_never_publishes():
    class BrokenWarehouse(Warehouse):
        def load_table_from_json(self, *args, **kwargs):
            raise RuntimeError('load unavailable')
    bq = BrokenWarehouse()
    with pytest.raises(RuntimeError):
        sync.run(Source([entity()]), bq, 'teraearlywine', 'private', 'staging', 'US')
    assert not bq.queries

def test_publication_is_atomic_reconciliation_with_stale_and_drop_guards():
    bq = Warehouse()
    result = sync.run(Source([entity()]), bq, 'teraearlywine', 'private', 'staging', 'US')
    sql, kwargs = bq.queries[0]
    assert sql.startswith('BEGIN TRANSACTION;') and sql.endswith('COMMIT TRANSACTION;')
    assert 'snapshot_at < @snapshot_at' in sql
    assert '@row_count >= row_count * 0.5' in sql
    assert 'DELETE FROM `teraearlywine.private.subscribers_current` WHERE TRUE' in sql
    assert kwargs['job_config'].maximum_bytes_billed == 1000000000
    assert result['rows'] == 1
    assert 'email' not in result

def test_ga4_query_checks_complete_source_window_before_publish():
    from pathlib import Path
    sql = Path('warehouse/engagement_daily.sql').read_text()
    assert 'INFORMATION_SCHEMA.TABLES' in sql
    assert "AS 'GA4 source window incomplete'" in sql
    assert sql.index('ASSERT') < sql.index('DELETE FROM')
    assert 'BEGIN TRANSACTION;' in sql and 'COMMIT TRANSACTION;' in sql
    assert "stream_id = '15512913765'" in sql
    assert "'America/Los_Angeles'" in sql

def test_run_ids_logged_before_uncertain_load(caplog):
    class BrokenWarehouse(Warehouse):
        def load_table_from_json(self, *args, **kwargs):
            assert kwargs['job_id'] in caplog.text
            raise RuntimeError('uncertain submit')
    with caplog.at_level('INFO'), pytest.raises(RuntimeError):
        sync.run(Source([entity()]), BrokenWarehouse(), 'teraearlywine', 'private', 'staging', 'US')
    assert 'reader@example.com' not in caplog.text

def test_ga4_zero_rows_still_updates_successful_refresh():
    from pathlib import Path
    sql = Path('warehouse/engagement_daily.sql').read_text()
    assert 'UPDATE `teraearlywine.website_reporting.engagement_refresh`' in sql
    assert 'refreshed_at = CURRENT_TIMESTAMP()' in sql

def test_ga4_publication_updates_singleton_and_rejects_stale_runs():
    from pathlib import Path
    sql = Path('warehouse/engagement_daily.sql').read_text()
    assert 'COUNT(*) = 1' in sql
    assert 'run_started_at < @run_started_at' in sql
    assert 'UPDATE `teraearlywine.website_reporting.engagement_refresh`' in sql
    assert sql.index('BEGIN TRANSACTION') < sql.index('COUNT(*) = 1') < sql.index('DELETE FROM')
