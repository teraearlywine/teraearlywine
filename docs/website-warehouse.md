# Website warehouse tools

The aggregate runner fetches bounded, anonymous GA4 event totals and publishes them
transactionally to BigQuery. Subscriber synchronization is separate scaffolding:
it is not included in the analytics container, scheduled, or enabled by this code.
Nothing in this repository automatically provisions resources or deploys on merge.

## Aggregate runner

`python -m scripts.run_website_analytics` previews the reporting window without
cloud calls. `--execute` performs a refresh using an explicitly scoped, keyless
runtime metadata credential for Analytics and separate default credentials for
BigQuery. Build with `warehouse/Dockerfile.analytics`; its command executes a refresh.
Do not run that image against production until access and destination checks pass.

The source contract fixes property, stream, hostnames and a finite event allowlist.
Only source date, event name and count are persisted with timezone/freshness metadata.
No URLs, user identifiers, subscriber emails, arbitrary parameters or source/campaign
strings are exported. The shared property permission is property-wide: output filters
are not an IAM boundary. Do not configure raw shared-property BigQuery export.

The last three fully closed source days are refreshed. Preserve the configured source
timezone rather than relabeling source dates as Pacific dates. Consented browser events
are incomplete observations; a download click is not proof of a completed download.
Missing/thresholded/sampled/oversized/malformed responses fail closed, not as zero.

Publication uses a unique staging table, row-count assertion and transactional
singleton watermark. Stale runs and conflicting transactions abort. Retry with a new
extraction; inspect logged BigQuery job IDs before retrying ambiguous outcomes. Jobs
may continue after the client stops waiting. A successful empty window advances
freshness. Outages longer than the refresh window need a reviewed bounded backfill.

## Deployment checklist

Review project, dataset locations, existing resources, costs and permissions first.
Use private reporting and staging datasets with no public access. The runner needs
Analytics Viewer, BigQuery job submission, and write access only to its destinations.
Restrict cost/revenue metrics in Analytics where available. Do not create service-account
keys or use browser credentials for unattended work. Use an already-authorized builder
and a private image repository, then pin the deployed image digest.

Apply `warehouse/aggregate_schema.sql` only to reviewed destinations. Staging dataset
default expiration must be at most 24 hours; event partitions expire after 90 days.
Use one runtime task, parallelism one, finite timeout, and zero automatic retries.
The publisher bounds each query to 100 MB and its response to 1 MiB. A scheduler
identity needs invocation access only to this job, not data access.

Before enabling a daily schedule, run one manual keyless execution in the target
runtime and independently read back the published window, row count and watermark.
Verify empty-load, failure, stale-run and concurrent-run behavior. Configure the
schedule timezone explicitly. Keep the live website runtime and dependencies unchanged.

Monitor execution count/duration, errors, freshness, query billed bytes, staging and
artifact growth, and actual billed charges. Billing reports are delayed; budgets are
not hard spending caps. Resource limits do not impose a total monthly spending cap.
Pause the schedule for unexplained repeated starts, stale data, broken scope invariants
or unexpectedly rising costs. Pausing does not stop already-running work.

## Subscriber scaffolding (not activated)

`scripts/sync_website_warehouse.py`, `warehouse/schema.sql` and the separate
`warehouse/requirements.txt` are optional, unactivated subscriber snapshot tooling.
Preview is the default; production access requires `--execute` and separately approved
source/destination permissions. The aggregate runtime has no subscriber source grant.

Snapshots use an explicit allowlist and exclude tokens, IP addresses and unrecognized
fields. A full replacement reconciles opt-outs and absent records; an unexpected drop
requires operator review. This is not a historical signup ledger or transactional
source snapshot. Source consent remains authoritative immediately before any email
sending. These tools never send email or join subscriber identities to Analytics.
Email-bearing datasets require separate restricted access and retention/privacy review,
including staging, time travel and backup copies. Do not expose them through public
reports or broadly shared dashboard credentials.

`warehouse/engagement_daily.sql` is an inactive export-based reporting prototype,
not the aggregate runner's input and not an instruction to enable raw export. It
requires separately approved, privacy-safe source data. No dashboard is included.

## Tests

Run the three focused suites:

```
pytest tests/test_ga4_aggregate.py tests/test_analytics_runner.py tests/test_website_warehouse.py
```

Unit tests use synthetic data and do not establish live deployment readiness.
