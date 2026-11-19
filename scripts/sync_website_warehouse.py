"""Daily private newsletter snapshot. No email sending or service provisioning.

Run only after approving infrastructure/costs and applying warehouse/schema.sql.
The live subscriber database, never this snapshot, authorizes email sends.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import logging
import re
import uuid

from google.cloud import bigquery, datastore

FIELDS = ('subscriber_id', 'email', 'state', 'audiences', 'confirmed_at',
          'unsubscribed_at', 'snapshot_at')
SCHEMA = [bigquery.SchemaField(name, 'TIMESTAMP' if name.endswith('_at') else 'STRING',
                               mode='REPEATED' if name == 'audiences' else 'NULLABLE')
          for name in FIELDS]


def table_ref(project, dataset, table):
    if not re.fullmatch(r'[a-z][a-z0-9-]{4,61}[a-z0-9]', project):
        raise ValueError('Invalid project identifier')
    if not all(re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', value) for value in (dataset, table)):
        raise ValueError('Invalid dataset/table identifier')
    return f'{project}.{dataset}.{table}'


def timestamp(value):
    if value is None:
        return None
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise ValueError('Invalid source timestamp')
    return value.astimezone(timezone.utc).isoformat()


def snapshot_rows(entities, snapshot_at, max_rows=100000):
    observed = timestamp(snapshot_at)
    rows, seen = [], set()
    for entity in entities:  # Exhaust every page before any load/publication.
        if len(rows) >= max_rows:
            raise ValueError('Snapshot row limit exceeded')
        identity = getattr(entity.key, 'name', None)
        if not isinstance(identity, str) or not re.fullmatch(r'[a-f0-9]{64}', identity):
            raise ValueError('Invalid subscriber ID')
        if identity in seen:
            raise ValueError('Duplicate subscriber ID')
        seen.add(identity)
        state, audiences = entity.get('state'), entity.get('audiences')
        if state not in ('pending', 'active', 'unsubscribed'):
            raise ValueError('Invalid subscriber state')
        if not isinstance(audiences, list) or any(a not in ('teams', 'professionals') for a in audiences):
            raise ValueError('Invalid subscriber audiences')
        email = entity.get('email')
        if not isinstance(email, str) or not email or len(email) > 254 or '@' not in email:
            raise ValueError('Invalid subscriber email')
        rows.append(dict(subscriber_id=identity, email=email, state=state,
                         audiences=sorted(set(audiences)), confirmed_at=timestamp(entity.get('confirmed_at')),
                         unsubscribed_at=timestamp(entity.get('unsubscribed_at')), snapshot_at=observed))
    return sorted(rows, key=lambda row: row['subscriber_id'])


def publish_sql(project, dataset, staging):
    current = table_ref(project, dataset, 'subscribers_current')
    head = table_ref(project, dataset, 'snapshot_head')
    totals = table_ref(project, dataset, 'subscriber_daily_totals')
    return f'''BEGIN TRANSACTION;
ASSERT (SELECT COUNT(*) FROM `{head}`) = 1 AS 'Invalid publication watermark';
ASSERT (SELECT snapshot_at IS NULL OR snapshot_at < @snapshot_at FROM `{head}`)
  AS 'Stale snapshot rejected';
ASSERT @allow_drop OR (SELECT row_count = 0 OR @row_count >= row_count * 0.5 FROM `{head}`)
  AS 'Unexpected source count drop; investigate before override';
ASSERT (SELECT COUNT(*) FROM `{staging}`) = @row_count AS 'Staging count mismatch';
DELETE FROM `{current}` WHERE TRUE;
INSERT INTO `{current}` ({", ".join(FIELDS)})
SELECT {", ".join(FIELDS)} FROM `{staging}`;
UPDATE `{head}` SET snapshot_at=@snapshot_at, row_count=@row_count, run_id=@run_id WHERE TRUE;
DELETE FROM `{totals}` WHERE snapshot_date=DATE(@snapshot_at, 'America/Los_Angeles');
INSERT INTO `{totals}`
SELECT DATE(@snapshot_at, 'America/Los_Angeles'), @snapshot_at, @row_count,
 COUNTIF(state='active'), COUNTIF(state='pending'), COUNTIF(state='unsubscribed')
FROM `{current}`;
COMMIT TRANSACTION;'''


def run(ds_client, bq_client, project, dataset, staging_dataset, location, allow_drop=False):
    if dataset == staging_dataset:
        raise ValueError("Use separate current and expiring staging datasets")
    # Validate all interpolated identifiers before doing any external work.
    table_ref(project, dataset, 'subscribers_current')
    stage = table_ref(project, staging_dataset, 'snapshot_' + uuid.uuid4().hex)
    stage_config = bq_client.get_dataset(f'{project}.{staging_dataset}')
    ttl = stage_config.default_table_expiration_ms
    if not ttl or ttl > 86400000 or stage_config.location.upper() != location.upper():
        raise ValueError('Staging requires <=24-hour default expiry and matching location')
    if bq_client.get_dataset(f'{project}.{dataset}').location.upper() != location.upper():
        raise ValueError('Destination location mismatch')
    observed = datetime.now(timezone.utc)
    rows = snapshot_rows(ds_client.query(kind='NewsletterSubscriber').fetch(), observed)
    # No PII in run IDs or logs. Rows remain in memory, never a local export file.
    run_id = hashlib.sha256((observed.isoformat() + json.dumps(rows, sort_keys=True)).encode()).hexdigest()
    logging.getLogger(__name__).info('Snapshot jobs: website_load_%s website_publish_%s', run_id, run_id)
    load_config = bigquery.LoadJobConfig(schema=SCHEMA, write_disposition='WRITE_EMPTY')
    bq_client.load_table_from_json(rows, stage, job_config=load_config,
                                   job_id='website_load_' + run_id, location=location).result()
    parameters = [bigquery.ScalarQueryParameter('snapshot_at', 'TIMESTAMP', observed),
                  bigquery.ScalarQueryParameter('row_count', 'INT64', len(rows)),
                  bigquery.ScalarQueryParameter('run_id', 'STRING', run_id),
                  bigquery.ScalarQueryParameter('allow_drop', 'BOOL', allow_drop)]
    config = bigquery.QueryJobConfig(query_parameters=parameters, maximum_bytes_billed=1000000000)
    # A failed/uncertain publication is never retried with different SQL or data.
    bq_client.query(publish_sql(project, dataset, stage), job_config=config,
                    job_id='website_publish_' + run_id, location=location).result()
    return {'run_id': run_id, 'rows': len(rows), 'snapshot_at': observed.isoformat()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', default='teraearlywine')
    parser.add_argument('--dataset', default='website_private')
    parser.add_argument('--staging-dataset', default='website_private_staging')
    parser.add_argument('--location', required=True)
    parser.add_argument('--execute', action='store_true', help='Actually read source and publish snapshot')
    parser.add_argument('--allow-drop', action='store_true', help='Operator-reviewed count-drop override')
    args = parser.parse_args()
    if not args.execute:
        parser.exit(message='Preview only: no cloud calls. Read docs/website-warehouse.md before --execute.\n')
    logging.basicConfig(level=logging.INFO)
    result = run(datastore.Client(project=args.project, _use_grpc=False),
                 bigquery.Client(project=args.project), args.project, args.dataset,
                 args.staging_dataset, args.location, args.allow_drop)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
