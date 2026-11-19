-- REVIEW ONLY: do not execute until deployment/cost/IAM approval.
-- Provision these datasets separately in an approved SAME BigQuery location:
-- website_private (restricted; no automatic table expiry)
-- website_private_staging (same restricted principals; default table expiry <=24h)
-- Do not grant public, workspace-wide or dashboard-wide access to either.
CREATE TABLE IF NOT EXISTS `teraearlywine.website_private.subscribers_current` (
 subscriber_id STRING, email STRING, state STRING, audiences ARRAY<STRING>,
 confirmed_at TIMESTAMP, unsubscribed_at TIMESTAMP, snapshot_at TIMESTAMP
);
CREATE TABLE IF NOT EXISTS `teraearlywine.website_private.snapshot_head` (
 snapshot_at TIMESTAMP, row_count INT64, run_id STRING
);
-- Bootstrap once, before scheduling any runs. Exactly one row is required.
INSERT INTO `teraearlywine.website_private.snapshot_head`
SELECT CAST(NULL AS TIMESTAMP), 0, CAST(NULL AS STRING)
WHERE NOT EXISTS (SELECT 1 FROM `teraearlywine.website_private.snapshot_head`);
CREATE TABLE IF NOT EXISTS `teraearlywine.website_private.subscriber_daily_totals` (
 snapshot_date DATE, snapshot_at TIMESTAMP, total INT64,
 active INT64, pending INT64, unsubscribed INT64
) PARTITION BY snapshot_date;

-- Provision website_reporting separately in the same location, private initially.
CREATE TABLE IF NOT EXISTS `teraearlywine.website_reporting.engagement_daily` (
 reporting_date DATE, source_event_date DATE, event_name STRING, guide STRING,
 event_count INT64, refreshed_at TIMESTAMP
) PARTITION BY reporting_date;

CREATE TABLE IF NOT EXISTS `teraearlywine.website_reporting.engagement_refresh` (
 window_start DATE, window_end DATE, refreshed_at TIMESTAMP,
 run_started_at TIMESTAMP
);

-- Bootstrap exactly once, before any executions. All writers update this row.
INSERT INTO `teraearlywine.website_reporting.engagement_refresh`
SELECT CAST(NULL AS DATE), CAST(NULL AS DATE), CAST(NULL AS TIMESTAMP), CAST(NULL AS TIMESTAMP)
WHERE NOT EXISTS (SELECT 1 FROM `teraearlywine.website_reporting.engagement_refresh`);
