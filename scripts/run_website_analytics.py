"""Aggregate-only batch; preview by default. No mail or Datastore access."""
import argparse
import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from uuid import uuid4

from scripts.ga4_aggregate import PROPERTY, build_request, validate_response

SOURCE_ZONE = 'Etc/GMT+7'
PROJECT = 'teraearlywine'
DATASET = 'website_reporting'
STAGING = 'website_reporting_staging'


def closed_window(now):
    if now.tzinfo is None:
        raise ValueError('Aware timestamp required')
    end = now.astimezone(ZoneInfo(SOURCE_ZONE)).date() - timedelta(days=1)
    return end - timedelta(days=2), end


def read_json(request):
    # Never log request headers, raw errors or response bodies.
    with urllib.request.urlopen(request, timeout=20) as response:
        raw = response.read(1024 * 1024 + 1)
    if len(raw) > 1024 * 1024:
        raise ValueError('Response too large')
    return json.loads(raw)


def fetch_report(start, end, reader=read_json):
    scope = urllib.parse.quote('https://www.googleapis.com/auth/analytics.readonly', safe='')
    request = urllib.request.Request(
        'http://metadata.google.internal/computeMetadata/v1/instance/'
        'service-accounts/default/token?scopes=' + scope,
        headers={'Metadata-Flavor': 'Google'})
    credentials = reader(request)
    token = credentials['access_token']
    request = urllib.request.Request(
        'https://analyticsdata.googleapis.com/v1beta/' + PROPERTY + ':runReport',
        data=json.dumps(build_request(start, end)).encode(),
        headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
    result = validate_response(reader(request), start, end)
    if result['source_timezone'] != SOURCE_ZONE:
        raise ValueError('Source timezone changed; do not publish')
    return result['rows']


def publication_sql(stage):
    # stage is created internally, not supplied by users.
    return f'''BEGIN TRANSACTION;
ASSERT (SELECT COUNT(*) = 1 FROM `{PROJECT}.{DATASET}.aggregate_head`)
 AS 'Expected singleton watermark';
ASSERT (SELECT observed_at IS NULL OR observed_at < @observed_at
 FROM `{PROJECT}.{DATASET}.aggregate_head`) AS 'Stale execution';
ASSERT @observed_at <= CURRENT_TIMESTAMP() AS 'Future execution';
ASSERT (SELECT COUNT(*) FROM `{stage}`) = @row_count AS 'Stage count mismatch';
DELETE FROM `{PROJECT}.{DATASET}.events_daily`
WHERE source_date BETWEEN @start_date AND @end_date;
INSERT INTO `{PROJECT}.{DATASET}.events_daily`
SELECT source_date, event_name, event_count, @source_timezone, @observed_at
FROM `{stage}`;
UPDATE `{PROJECT}.{DATASET}.aggregate_head`
SET observed_at = @observed_at, window_start = @start_date, window_end = @end_date,
 source_timezone = @source_timezone, row_count = @row_count, run_id = @run_id
WHERE TRUE;
COMMIT TRANSACTION;'''


def publish(client, rows, start, end, observed, location):
    from google.cloud import bigquery
    for dataset in (DATASET, STAGING):
        info = client.get_dataset(f'{PROJECT}.{dataset}')
        if info.location.upper() != location.upper():
            raise ValueError('Dataset location mismatch')
        if dataset == STAGING and not 0 < (info.default_table_expiration_ms or 0) <= 86400000:
            raise ValueError('Stage must expire within 24 hours')
    run_id = uuid4().hex
    stage = f'{PROJECT}.{STAGING}.aggregate_{run_id}'
    schema = [bigquery.SchemaField('source_date', 'DATE'),
              bigquery.SchemaField('event_name', 'STRING'),
              bigquery.SchemaField('event_count', 'INTEGER')]
    config = bigquery.LoadJobConfig(schema=schema, write_disposition='WRITE_EMPTY')
    print(json.dumps({'run_id': run_id, 'load_job': 'aggregate_load_' + run_id,
                      'publish_job': 'aggregate_publish_' + run_id}), flush=True)
    # Explicit schema also applies for empty result sets. Cloud acceptance test required.
    client.load_table_from_json(rows, stage, job_config=config, location=location,
                                job_id='aggregate_load_' + run_id).result(timeout=40)
    params = [
        bigquery.ScalarQueryParameter('start_date', 'DATE', start),
        bigquery.ScalarQueryParameter('end_date', 'DATE', end),
        bigquery.ScalarQueryParameter('observed_at', 'TIMESTAMP', observed),
        bigquery.ScalarQueryParameter('source_timezone', 'STRING', SOURCE_ZONE),
        bigquery.ScalarQueryParameter('row_count', 'INT64', len(rows)),
        bigquery.ScalarQueryParameter('run_id', 'STRING', run_id)]
    config = bigquery.QueryJobConfig(query_parameters=params, maximum_bytes_billed=100_000_000)
    client.query(publication_sql(stage), job_config=config, location=location,
                 job_id='aggregate_publish_' + run_id).result(timeout=40)
    return {'rows': len(rows), 'window_start': start.isoformat(),
            'window_end': end.isoformat(), 'run_id': run_id}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    observed = datetime.now(timezone.utc)
    start, end = closed_window(observed)
    if not args.execute:
        print(json.dumps({'preview': True, 'start': str(start), 'end': str(end),
                          'source_timezone': SOURCE_ZONE}))
        return
    try:
        from google.cloud import bigquery
        rows = fetch_report(start, end)
        result = publish(bigquery.Client(project=PROJECT), rows, start, end, observed, 'US')
        print(json.dumps(result))
    except Exception as exc:
        # Deliberately omit exception messages/tracebacks, which may include payloads.
        print(json.dumps({'status': 'failed', 'error_type': type(exc).__name__}))
        raise SystemExit(1) from None


if __name__ == '__main__':
    main()
