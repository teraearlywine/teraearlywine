# Measurement execution evidence — September 10, 2026

This record distinguishes code/configuration delivery from project acceptance. The clean baseline has **not started**. TER-47 requires 30 complete property-calendar days after release AND reporting acceptance, then at least 48 hours for processing. No scheduled notification was created.

## Native GA4 readback

Property `533228502`, account `391533598`; website stream `15512913765`, measurement `G-NF6SVCGZDF`. [Property details](https://analytics.google.com/analytics/web/#/a391533598p533228502/admin/property/settings) displayed country United Kingdom and reporting timezone **`(GMT-07:00) GMT-07:00`**. This record does not infer a geographic zone or DST behavior. Property settings were not changed.

The property lists 25 streams, including 19 web streams. The website stream has zero connected site tags. Its Google tag has the website destination.

[Custom definitions](https://analytics.google.com/analytics/web/#/a391533598p533228502/admin/customdefinitions/hub) were created and read back as Event scope on September 10:

| Label | Parameter |
| --- | --- |
| Contact method | `contact_method` |
| CTA placement | `placement` |
| Destination type | `destination_type` |

Registration is complete; population by new eligible events and settled breakdowns remain pending. Definitions do not backfill historical data.

[Events](https://analytics.google.com/analytics/web/#/a391533598p533228502/admin/events/hub) lists `contact_submit` as a key event for the Professional Website stream. Its counting-method panel has **Once per event** selected. `contact_click` is absent from the complete six-row key-event list. Existing designation/counting settings were retained.

[Website stream settings](https://analytics.google.com/analytics/web/#/a391533598p533228502/admin/streams/table/15512913765): outbound-click automatic collection OFF; email redaction ON; URL query redaction ON for `email`, `firstname`, `lastname`, `address`, `phone`. Page views, scrolls, form interactions, video engagement and file downloads ON.

A real Google-library experiment with intercepted/aborted collection reproduced automatic `view_search_results` leaking a synthetic `q` value despite sanitized page_location. **Site search was disabled for this website stream**, saved, and read back OFF after a full page reload. The website has no search feature. The expanded intercepted regression then passed. The experiment did not ingest test events and does not prove a native GA4 receipt.

## Internal traffic — unresolved

[Data filters](https://analytics.google.com/analytics/web/#/a391533598p533228502/admin/datapolicies/datafilters) shows **Internal Traffic / Exclude / Testing**. Its exact rule is `traffic_type` equals `internal`. The website tag's **Define internal traffic** panel says **No rules yet**. No matching owner visit or external non-match has been demonstrated. The user is unsure which stable public IP/network to use.

The shared property filter was left in Testing. No IP address was guessed, no broad network was excluded, and no historical data was changed. Public-host reports still contain unidentifiable owner/test activity. This prevents a claim of clean baseline acceptance. A future check must establish an intended match and external non-match before exclusion is activated; exclusion would discard future data irreversibly.

## Search Console diagnostic

The existing `sc-domain:teraearlywine.com` property is accessible through the already signed-in owner account. No duplicate property or access grant was created.

[Native sitemap view](https://search.google.com/u/3/search-console/sitemaps?resource_id=sc-domain%3Ateraearlywine.com) shows `https://www.teraearlywine.com/sitemap.xml`, submitted September 8, last read September 8, **Success**, five discovered pages. The live sitemap now contains 33 URLs. This is a lagging observed crawl record, not a demonstrated sitemap fault; it was not needlessly resubmitted.

[Performance by page](https://search.google.com/u/3/search-console/performance/search-analytics?resource_id=sc-domain%3Ateraearlywine.com&metrics=CLICKS%2CIMPRESSIONS%2CCTR%2CPOSITION&breakdown=page) displayed June 9–September 8, 2026, Web search, last update 8.5 hours earlier at readback. The URL uses the native relative three-month selection; freeze the recorded dates when reproducing this readout.

| Scope/page | Clicks | Impressions | CTR | Average position |
| --- | ---: | ---: | ---: | ---: |
| All search | 3 | 120 | 2.5% | 6.4 |
| `https://teraearlywine.com/` | 3 | 119 | 2.5% | 6.5 |
| `https://www.teraearlywine.com/` | 0 | 1 | 0% | 1.0 |

CTR is clicks divided by impressions for the named search scope and date window. Average position is a Search Console aggregate, not a rank guarantee. No service or article row appeared in this window.

[Brand group](https://search.google.com/u/3/search-console/performance/search-analytics?resource_id=sc-domain%3Ateraearlywine.com&metrics=CLICKS%2CIMPRESSIONS%2CCTR%2CPOSITION&breakdown=page&query=~tera%20earlywine%7Cteraearlywine) uses regex `tera earlywine|teraearlywine`: native view shows No data (zero clicks/impressions). CTR and position are not meaningful with no data.

[Non-brand complement](https://search.google.com/u/3/search-console/performance/search-analytics?resource_id=sc-domain%3Ateraearlywine.com&metrics=CLICKS%2CIMPRESSIONS%2CCTR%2CPOSITION&breakdown=page&query=_tera%20earlywine%7Cteraearlywine): zero clicks, 12 impressions, 0% CTR, average position 14; only the non-www homepage appears. This mechanical complement contains surname-only/ambiguous searches; it does not establish commercial non-brand discovery. Filtered chart/table results are explicitly partial. The remaining impressions and clicks cannot be assigned to either query group; suppressed query information remains **Unknown**.

[Page indexing](https://search.google.com/u/3/search-console/index?resource_id=sc-domain%3Ateraearlywine.com), last updated September 3, shows two indexed/two not indexed: one redirect and one duplicate without user-selected canonical (validation Started). That snapshot predates the September 8 canonical release; it is not evidence of a current regression.

[Service URL inspection](https://search.google.com/u/3/search-console/inspect?resource_id=sc-domain%3Ateraearlywine.com&id=qhbXKcwwEjjkwhiIyoqEDg) for `/services/data-platform-modernization` shows **Discovered - currently not indexed**, known from the sitemap, no crawl/canonical data yet. Discovery without a crawl does not prove a technical indexing fault.

The companion `indexability-check-2026-09-10.json` inventories all 33 live sitemap URLs: each returned HTTP 200, self-canonical, and no noindex meta tag. This checks current HTTP markup; it does not establish Google's indexing decision. No repair issue or redesign recommendation is justified by these observations alone.

Search Console measures Google search exposure and clicks, while GA4 measures consented, unblocked browser events. They have different populations, reporting dates and processing rules and need not reconcile. The sample does not support offer/channel/article winners or A/B testing.

## Release and reporting gates

PR #25 added contact success/failure/concurrent-submit tests and private-safe historical reconciliation; PR #26 added the measurement contract. Both received independent spec/quality review and were merged. The controlled intake receipt is recorded below; native GA4 receipt and live provider repeated-request idempotency remain pending. Both historical success events remain Unknown.

PR #27 implements host/attribution safeguards. Independent review found inherited arbitrary error-path collection; the correction supplies only server-validated public paths or fixed error paths, passed scoped re-review, and was merged. PR #28 removes an obsolete optional document-wording test exposed by restoring the contract; independent integration review passed and all 160 pytest tests now pass. Serving deployment verification and native receipt limitations are recorded below. Four scoped native GA4 reports were saved; their fixed-window readout and acceptance limits are recorded below.

[Homepage URL inspection](https://search.google.com/u/3/search-console/inspect?resource_id=sc-domain%3Ateraearlywine.com&id=SuEOqfuvEWE5CUvEMliDjg) confirms **URL is on Google / Page is indexed**. Last crawl displayed September 9, 2026, 6:44:30 PM (UI display; timezone not independently established), Googlebot smartphone; crawl allowed Yes, successful fetch, indexing allowed Yes. User-declared canonical is `https://www.teraearlywine.com/`; Google-selected canonical is the inspected URL. This recent exact-URL evidence supersedes the older aggregate duplicate warning for the homepage.

## Serving release and actual-page checks

Reviewed merged code: `f6c4f1bb2609618d40a0445120dee239c0daabac`. App Engine deployment **`ga4-20260910-f6c4f1b`** completed; a separate versions query read back **SERVING, 1.00 traffic allocation**. Previous serving version: `consulting-20260910-46519e2` (rollback target). The public homepage returned production measurement ID, `debugMode: false`, `pagePath: /`.

Live `/static/assets/js/analytics.js?v=502a1f7e7454` SHA256 is `502a1f7e745497f4c1ac3a413e1f86b2391bfc62ad168a597a695b697afd8812`, byte-for-byte equal to the reviewed source. `serving-check-2026-09-10.json` records this readback.

Actual public HTML/assets were tested from 17:04:14 through 17:05:10 UTC on September 10. All four cases (approved LinkedIn, approved newsletter, unknown campaign, unknown private pathname) passed no-consent, reject, accept, actual CTA click, payload privacy and revocation checks. The HTTP 404 page reports fixed `/404`; no synthetic private path/query/referrer marker appeared in URL, body or request headers. `_dbg` was absent. The 24 collection requests were all intercepted and aborted; no contact form was submitted in this network matrix. See `live-network-check-2026-09-10.json`. This is serialized-payload evidence, distinct from native ingestion.

## Controlled intake receipt

A separate browser visit to the serving homepage explicitly accepted analytics. Empty form submission stayed on the form and focused the required name field. A single labeled QA submission then displayed **Thanks — your message has been sent.** The record was explicitly a measurement acceptance test, not a sales inquiry.

Scoped native mailbox search returned one original notification timestamped `2026-09-10T17:04:56Z`. The matching intake was submitted `2026-09-10T17:04:50.691Z` and created in Linear at `17:04:58.018Z`. [TER-48](https://linear.app/idea-factory-lab/issue/TER-48) was renamed **QA ONLY — website measurement acceptance receipt** and set Canceled, preventing treatment as a sales opportunity. Full message, email, opaque submission ID and private mailbox identifier remain in the original private systems.

One mailbox and one intake receipt were observed for this one test. The success path is verified at those destinations; provider-level repeated-request idempotency was not retested live. Local tests cover repeated success, failure and concurrent submission; they are not production broker persistence evidence. Native GA4 receipt for this controlled success is not yet established. All September 10 QA activity must remain outside a clean baseline; neither a test success nor a CTA click is a legitimate inquiry or booking.

## Collection acknowledgment is not reporting acceptance

A separate fresh QA browser sent an approved LinkedIn landing page_view and one actual hero booking contact_click; booking navigation was prevented and no form was submitted. Google Analytics returned HTTP 204 at `2026-09-10T17:07:00.272Z` and `17:07:05.376Z`. Payloads held only the approved campaign tuple, canonical page location, blank unknown referrer, and bounded booking/hero parameters. `collection-acknowledgment-2026-09-10.json` records these responses; Chromium also emitted `net::ERR_ABORTED` after each 204, retained without inventing a cause.

Native Realtime initially showed no contact_submit or contact_click and no key events after these tests. HTTP acknowledgment, code tests and intake delivery do not establish settled GA4 processing or source classification. TER-41/42/43/44 acceptance remains open until the expected native records and dimension breakdowns can be established. Avoid repeated test hits merely to make a chart populate.

## Debug configuration correction

After the first serving check, the receipt investigation checked [Google's DebugView guidance](https://support.google.com/analytics/answer/7201382?hl=en). It states that setting `debug_mode` false does not disable debug mode; the parameter must be excluded. The application-level JSON `debugMode: false` correctly gates production host collection, but passing that value through as a Google config field was insufficient. PR #29, independently reviewed and merged, corrects this by omitting Google's `debug_mode` field for production and emitting it only for explicitly enabled isolated test streams. This is a documented defect; it does not prove why the initial Realtime receipts were missing. The corrected release must supersede the initial version for debug acceptance.

[Reporting identity](https://analytics.google.com/analytics/web/#/a391533598p533228502/admin/identityspace) was read back as **Blended** on September 10. The expanded detail says modeling is unavailable for this property; when available it would be enabled by default. No identity setting was changed. This is provenance, not an established explanation for the historical acquisition discrepancy.

## Saved production reports and settled historical readout

All views use property `533228502`, **Stream ID exactly matches `15512913765` AND Hostname matches `^(www\.)?teraearlywine\.com$`**, custom inclusive **August 13–September 7, 2026**, and the property timezone label recorded above. This is a settled historical window, not the new baseline. No owner/test exclusion is proven; report tabs state that limitation. Native quality badges say 100% of available data; that alone does not establish completeness or freedom from every privacy/aggregation limitation.

| Saved native report | Observed result in this window |
| --- | --- |
| [Production traffic](https://analytics.google.com/analytics/web/#/analysis/a391533598p533228502/edit/Zi76PnDmSdKlCAe6RqVFkA) | 29 views, 7 active users, 7 total users, 17 sessions, 11 engaged sessions. A distinct session_start tab reports 17 events; event count is not defined as Sessions. |
| [Production acquisition](https://analytics.google.com/analytics/web/#/analysis/a391533598p533228502/edit/pWUbebTBTHSLODx2oW-mag) | One `(direct) / (none)` row with `(direct)` session campaign: 17 sessions, matching total 17; 11 engaged sessions. Channel shares withheld. |
| [Production content](https://analytics.google.com/analytics/web/#/analysis/a391533598p533228502/edit/q09eRrmSQ2ijuHPnM63hHw) | Page-path view: homepage `/` has all 29 views. No service/article row in this settled window. Later September 8–9 activity is deliberately outside this snapshot. |
| [Production contact](https://analytics.google.com/analytics/web/#/analysis/a391533598p533228502/edit/XBuxaflaQdykKLcErkJ4FQ) | 13 contact_view events/4 event-specific users; 2 contact_click events/1 user; 2 contact_submit events/1 user; 0 reported key events. These parallel paths are not a funnel. |

The acquisition engagement rate is 11 engaged sessions / 17 sessions = 64.7% for that scope/window. Unique users are non-additive and are never summed across days, paths or event rows. Historical CTA breakdowns show `(not set)` for all three new dimensions; this is not a backfill failure. Form progression and verified inquiry conversion rates remain unreported.

The original all-host August 13–September 9 standard acquisition view was also observed with total 33 versus Direct 33 plus Unassigned 2. The scoped, earlier settled window reconciles at 17, but **does not resolve the original 33-versus-35 discrepancy** because the dates/scope differ. No explanation is selected in advance; original denominator provenance remains a data-quality limitation, and historical channel-share percentages are withheld.

Original downloads and hashes are preserved privately under the current task's `ga4-native-reports/manifest.json`. The manifest records exact filters, native URLs, fixed dates, download/extraction times, identity, quality badge and processing limitations. The execution agent independently verified all five initial CSV hashes against the copied original bytes. Report definitions and links are delivered; reporting acceptance for a clean baseline still depends on expected fresh receipts, dimension population and proven owner/test handling.

## Final corrected deployment

PR #29 was independently reviewed, merged, and deployed as **`ga4-20260910-6a44b81`**, reviewed commit `6a44b8117aa5859ab4a3a7d890ebc94c1d44b9d5`. A separate App Engine readback confirms **SERVING / 1.00 traffic allocation**. Its analytics asset `/static/assets/js/analytics.js?v=6a5c5f658cf9` has SHA256 `6a5c5f658cf90f073d2e6b6ea1798e0f6d418ad334b677ad358552b21115f26e`, byte-for-byte matching reviewed source. `final-serving-check-2026-09-10.json` supersedes the earlier serving check. The app JSON retains debugMode false for the production guard; Google's debug_mode parameter is omitted for production.

All 160 tests and the real-library network regression passed for the corrected code before merge. The earlier intake acknowledgment and HTTP204 tests occurred on the first release and remain labeled as such. They do not substitute for corrected-release native reporting acceptance.

The final actual-serving matrix passed from `17:13:35` through `17:14:28 UTC`: all four cases, explicit consent/rejection/revocation, actual CTA event and payload privacy passed. Both `_dbg` and `ep.debug_mode` were absent across production payloads; live asset hash matched the reviewed corrected commit. All 24 requests were aborted, with zero new ingestion or form submissions. See `final-live-network-check-2026-09-10.json`. Realtime still did not establish the earlier expected contact events, and no native corrected-release receipt is claimed.

## Final saved report layouts

The reporting agent reopened the saved first-user and landing-page tabs and recorded these eight final layouts. Every tab retains the fixed dates and both production scope filters above; event-specific filters are additional.

| Report / tab | Ordered dimensions and metrics | Additional event filter |
|---|---|---|
| traffic / Daily; owner tests may remain | Date, Views, Active users, Total users, Sessions, Engaged sessions | None |
| traffic / Session-start events; not Sessions | Date, Event count | Event name exactly matches session_start |
| acquisition / Session sources; shares withheld | Session source / medium, Session campaign, Active users, Total users, Sessions, Engaged sessions, Engagement rate | None |
| acquisition / First-user sources; owner tests may remain | First user source / medium, New users | None |
| content / Page paths; owner tests may remain | Page path and screen class, Active users, Total users, Views | None |
| content / Landing pages; owner tests may remain | Landing page, Sessions, Engaged sessions, Engagement rate | None |
| contact / Parallel paths; inquiries Unknown | Event name, Total users, Event count, Key events | Event name matches regex `^contact_(view\|click\|submit)$` |
| contact / CTA dimensions; population pending | Event name, Contact method, CTA placement, Destination type, Total users, Event count, Key events | Event name matches regex ^contact_click$ |


The first-user tab shows `(direct) / (none)` with 7 New users. The landing-page tab uses Landing page without query strings and shows `/`, 17 Sessions, 11 Engaged sessions and 64.71% Engagement rate. The exact requested average engagement time per active user metric was unavailable in the native Exploration selector; no session-based substitute is presented under that label. Verified legitimate-inquiry counts remain Unknown, and the private controlled QA receipt is excluded from such counts.

The execution agent verified all 10 preserved CSV hashes, including two explicitly superseded exports. The private final manifest SHA256 is `9ce76eaf0970094247cda139490b44f38da549adeb3cf514c077059be50f66dc`. It records all eight final tab layouts and each export's complete filter list. The saved report contract still awaits native fresh receipts, dimension population, and owner/test acceptance.
