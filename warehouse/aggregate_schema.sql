-- Run only after resource/permission approval. All identifiers are fixed.
CREATE TABLE IF NOT EXISTS `teraearlywine.website_reporting.events_daily` (
 source_date DATE, event_name STRING, event_count INT64,
 source_timezone STRING, observed_at TIMESTAMP
) PARTITION BY source_date
OPTIONS(partition_expiration_days=90, require_partition_filter=TRUE);
CREATE TABLE IF NOT EXISTS `teraearlywine.website_reporting.aggregate_head` (
 observed_at TIMESTAMP, window_start DATE, window_end DATE,
 source_timezone STRING, row_count INT64, run_id STRING
);
INSERT INTO `teraearlywine.website_reporting.aggregate_head`
SELECT CAST(NULL AS TIMESTAMP), CAST(NULL AS DATE), CAST(NULL AS DATE),
 CAST(NULL AS STRING), 0, CAST(NULL AS STRING)
FROM UNNEST([1]) AS bootstrap
WHERE NOT EXISTS (SELECT 1 FROM `teraearlywine.website_reporting.aggregate_head`);
