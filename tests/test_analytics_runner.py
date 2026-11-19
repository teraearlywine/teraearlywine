from datetime import datetime, timezone
import json
import pytest
from scripts import run_website_analytics as runner
from tests.test_ga4_aggregate import response, START, END


def test_closed_window_before_midnight():
    start, end = runner.closed_window(datetime(2026, 11, 19, 1, tzinfo=timezone.utc))
    assert str(start) == '2026-11-15' and str(end) == '2026-11-17'


def test_closed_window_after_midnight():
    start, end = runner.closed_window(datetime(2026, 11, 19, 8, tzinfo=timezone.utc))
    assert str(start) == '2026-11-16' and str(end) == '2026-11-18'


def test_scoped_metadata_and_filtered_request():
    calls = []
    def reader(req):
        calls.append(req)
        if len(calls) == 1:
            assert 'analytics.readonly' in req.full_url
            assert req.get_header('Metadata-flavor') == 'Google'
            return {'access_token': 'synthetic'}
        payload = json.loads(req.data)
        assert len(payload['dimensionFilter']['andGroup']['expressions']) == 3
        r = response(); r['metadata']['timeZone'] = 'Etc/GMT+7'
        return r
    rows = runner.fetch_report(START, END, reader)
    assert rows[0]['event_count'] == 3 and len(calls) == 2


def test_timezone_drift_fails_closed():
    def reader(req):
        return {'access_token':'synthetic'} if req.data is None else response()
    with pytest.raises(ValueError, match='timezone'):
        runner.fetch_report(START, END, reader)


def test_atomic_zero_row_watermark_contract():
    sql = runner.publication_sql('teraearlywine.website_reporting_staging.test')
    assert 'COUNT(*) = 1' in sql
    assert 'observed_at < @observed_at' in sql
    assert 'UPDATE `teraearlywine.website_reporting.aggregate_head`' in sql
    assert sql.startswith('BEGIN TRANSACTION') and sql.endswith('COMMIT TRANSACTION;')


def test_publish_zero_rows_is_bounded_and_updates_freshness():
    from tests.test_website_warehouse import Warehouse
    client = Warehouse()
    observed = datetime(2026, 11, 19, tzinfo=timezone.utc)
    # Existing fake Result has no timeout argument; adapt its response.
    class Job:
        def result(self, **kwargs):
            assert kwargs['timeout'] == 40
    original_load, original_query = client.load_table_from_json, client.query
    def load(*args, **kwargs):
        original_load(*args, **kwargs); return Job()
    def query(*args, **kwargs):
        original_query(*args, **kwargs); return Job()
    client.load_table_from_json, client.query = load, query
    result = runner.publish(client, [], START, END, observed, 'US')
    assert result['rows'] == 0
    assert client.queries[0][1]['job_config'].maximum_bytes_billed == 100_000_000
    assert client.loads[0][2]['job_config'].write_disposition == 'WRITE_EMPTY'


def test_publish_rejects_bad_stage_before_loading():
    from tests.test_website_warehouse import Warehouse
    client = Warehouse(ttl=None)
    with pytest.raises(ValueError, match='expire'):
        runner.publish(client, [], START, END, datetime.now(timezone.utc), 'US')
    assert not client.loads and not client.queries
