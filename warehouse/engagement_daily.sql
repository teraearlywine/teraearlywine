-- BLOCKED: native export does not meet strict pre-warehouse PII/host filtering.
-- Reference only; never enable under the current aggregate-only requirement.
-- @run_started_at is the UTC extraction start, preserved across any retry.
-- REVIEW ONLY: GA4 export link does not exist yet. Dataset name is proposed.
-- Run as a daily scheduled query into an aggregate-only reporting dataset.
-- Parameters @start_date and @end_date are DATEs (inclusive Pacific dates).
-- Replace affected reporting-date partitions atomically; never append duplicates.
-- Scan one extra table date each side to account for property timezone != Pacific.
-- Native export is consented/incomplete and may update for three days.
ASSERT @start_date <= @end_date AS 'Invalid reporting window';
ASSERT (
 SELECT COUNT(*) FROM `teraearlywine.analytics_533228502.INFORMATION_SCHEMA.TABLES`
 WHERE table_name BETWEEN CONCAT('events_', FORMAT_DATE('%Y%m%d', DATE_SUB(@start_date, INTERVAL 1 DAY)))
                      AND CONCAT('events_', FORMAT_DATE('%Y%m%d', DATE_ADD(@end_date, INTERVAL 1 DAY)))
 AND REGEXP_CONTAINS(table_name, r'^events_[0-9]{8}$')
) = DATE_DIFF(@end_date, @start_date, DAY) + 3 AS 'GA4 source window incomplete';
BEGIN TRANSACTION;
ASSERT @run_started_at IS NOT NULL AND @run_started_at <= CURRENT_TIMESTAMP()
 AS 'Invalid run start';
ASSERT (SELECT COUNT(*) = 1 FROM `teraearlywine.website_reporting.engagement_refresh`)
 AS 'Expected singleton refresh watermark';
ASSERT (SELECT run_started_at IS NULL OR run_started_at < @run_started_at
 FROM `teraearlywine.website_reporting.engagement_refresh`) AS 'Stale GA4 run';
DELETE FROM `teraearlywine.website_reporting.engagement_daily`
WHERE reporting_date BETWEEN @start_date AND @end_date;
INSERT INTO `teraearlywine.website_reporting.engagement_daily`
WITH events AS (
 SELECT
   DATE(TIMESTAMP_MICROS(event_timestamp), 'America/Los_Angeles') AS reporting_date,
   PARSE_DATE('%Y%m%d', event_date) AS source_event_date,
   event_name,
   (SELECT value.string_value FROM UNNEST(event_params) WHERE key='guide' LIMIT 1) AS guide
 FROM `teraearlywine.analytics_533228502.events_*`
 WHERE _TABLE_SUFFIX BETWEEN FORMAT_DATE('%Y%m%d', DATE_SUB(@start_date, INTERVAL 1 DAY))
                         AND FORMAT_DATE('%Y%m%d', DATE_ADD(@end_date, INTERVAL 1 DAY))
   AND stream_id = '15512913765'
   AND LOWER(NET.HOST((SELECT value.string_value FROM UNNEST(event_params)
                      WHERE key='page_location' LIMIT 1)))
       IN ('teraearlywine.com', 'www.teraearlywine.com')
   AND event_name IN ('page_view', 'newsletter_cta_click', 'newsletter_guide_select',
     'newsletter_signup', 'newsletter_confirm', 'newsletter_guide_download',
     'newsletter_unsubscribe', 'resource_download', 'navigation_click',
     'outbound_click', 'contact_view', 'contact_click', 'contact_submit')
)
SELECT reporting_date, source_event_date, event_name,
 CASE WHEN guide IN ('teams', 'professionals', 'both') THEN guide ELSE 'other_or_unset' END AS guide,
 -- Placement deliberately omitted from publication until its fixed vocabulary is reviewed.
 COUNT(*) AS event_count, CURRENT_TIMESTAMP() AS refreshed_at
FROM events
WHERE reporting_date BETWEEN @start_date AND @end_date
GROUP BY 1, 2, 3, 4;

UPDATE `teraearlywine.website_reporting.engagement_refresh`
SET window_start = @start_date, window_end = @end_date,
 refreshed_at = CURRENT_TIMESTAMP(), run_started_at = @run_started_at
WHERE TRUE;
COMMIT TRANSACTION;
