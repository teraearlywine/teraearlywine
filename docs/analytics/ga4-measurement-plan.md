# GA4 measurement and lead reporting contract

This contract covers teraearlywine.com consulting interest. GA4 observes visitors
who explicitly accept analytics, not total visitors, verified people, qualified
leads or completed sales. Use native GA4 and Search Console reports; no warehouse
or separate dashboard is in scope.

## Property, scope and acceptance

| Setting | Value or evidence |
| --- | --- |
| Property | `533228502`, idea-factory-io; shared with other streams |
| Website stream | `15512913765`, Professional Website (teraearlywine.com) |
| Production measurement ID | `G-NF6SVCGZDF` |
| Public hostnames | Exact `teraearlywine.com` and `www.teraearlywine.com` |
| Required report filters | Stream ID equals `15512913765` AND Hostname matches `^(www\.)?teraearlywine\.com$` |
| Reporting timezone | September 10, 2026 Admin readback: country United Kingdom; selected label `(GMT-07:00) GMT-07:00`. Do not infer an IANA zone or daylight-saving behavior from this label. |
| Timezone evidence | [Property settings](https://analytics.google.com/analytics/web/#/a391533598p533228502/admin/property/settings); unchanged; historical timezone changes unknown |
| Historical windows | August 13–September 9, 2026; history check June 12–September 9, 2026, inclusive property-calendar dates |
| Release acceptance | Serving version and consent/payload checks verified September 10; native GA4 receipt and internal/test controls pending TER-44. See [acceptance evidence](2026-09-10-acceptance-evidence.md). |
| Report acceptance | Four scoped reports saved and historical exports preserved; fresh dimension/receipt and owner/test acceptance pending TER-45. |
| Baseline start | Not started; next complete property-calendar day after both release and report acceptance |

Public-host filtering removes local hosts, not all owner/testing visits. The
historical Internal Traffic filter was in **Testing**, not active exclusion.
September 10 live Admin shows no internal-traffic rules for this website stream;
the property has 25 streams, including 19 web streams. Matching is unproven and
the filter remains unactivated.
TER-40 must establish actual rules, shared-property impact, a known internal
match and external non-match, and effective state. If reliable matching cannot
be proved, retain Testing, exclude only proven matched tests in reports, and
label residual contamination. Do not call the population clean without evidence.

## Metric definitions

| Metric | Definition and scope | Limit |
| --- | --- | --- |
| Page views | `page_view` event count / native website Views | Repeat views count; not readers |
| GA4 users | Name native Total users or Active users explicitly for each report/window | Identifiers, not verified people; unique users are non-additive across rows |
| Sessions | Native Sessions metric with session-scoped acquisition dimensions | Distinct from users and raw event counts |
| Session starts | Event count filtered to `session_start` | Do not substitute for Sessions |
| Engagement | Native Engaged sessions, Engagement rate and average engagement time with named denominator | Time per active user is not time per visit |
| Contact section views | `contact_view` Event count and Total users | Section exposure; repeat page views may count again |
| CTA intent | `contact_click` Event count and Total users by approved method/placement | Email/booking selection, not delivery or qualification |
| Form success | `contact_submit` after the browser receives an accepted successful server response | Measured success, not a verified inquiry or necessarily one event per delivery |
| Delivered forms | Unique successful deliveries from private broker/intake receipts, excluding idempotent repeats | Operational metric outside GA4 |
| Verified inquiries | Legitimate inquiry confirmed and deduplicated by private intake review | Classify legitimate, test, spam or Unknown; no inferred identities from GA4 |
| Qualified opportunities | Tera's review of an actual inquiry against consulting qualification criteria | Human-reviewed pipeline measure outside GA4 |
| Search visibility | Search Console clicks, impressions, CTR, average position, indexing/canonical evidence | Different population from consented GA4 sessions; totals need not reconcile |

Keep first-user source/medium (initial acquisition) separate from session
source/medium/campaign (visit acquisition). Report homepage, blog index, article
and service-page activity separately. Tiny counts cannot establish a winning
article, underperforming offer, SEO fault, trend or causal release effect.

## Events and parallel contact paths

Before consent and after rejection, do not create `gtag`, load `gtag.js`, configure
GA4 or send analytics requests. After explicit acceptance, eligible hosts may
collect page, session/engagement, reviewed enhanced events and these custom events:

| Event | Trigger | Parameters | Key event |
| --- | --- | --- | --- |
| `navigation_click` | Tagged internal link selected | `placement`, `destination_type` | No |
| `outbound_click` | Tagged external link selected | `placement`, `destination_type` | No |
| `contact_view` | At least 50% of contact section visible once per page view | `placement` | No |
| `contact_click` | Email or booking CTA selected | `contact_method`, `placement`, `destination_type` | No; secondary intent |
| `contact_submit` | Existing contact handler receives accepted successful server response | None | Yes; primary success |

Allowed values:

- `contact_method`: `email`, `booking`.
- `placement`: `navigation`, `hero`, `services`, `projects`, `contact`, `footer`, `error`.
- `destination_type`: `section`, `service`, `github`, `linkedin`, `youtube`, `idea_factory`, `email`, `booking`, `home`.

Drop unknown events, parameters and enum values. Custom events contain no free
text, link text, email, message, URL or submission identifier. Retain server
idempotency and accepted-response semantics. An idempotent retry may receive a
successful response without another delivery; aggregate analytics is not a
receipt ledger.

On September 10, live Admin readback verified these Event-scoped definitions:
Contact method → `contact_method`; CTA placement → `placement`; Destination type
→ `destination_type`. [Custom definitions](https://analytics.google.com/analytics/web/#/a391533598p533228502/admin/customdefinitions/hub)
are registered; new-event population remains pending processing and TER-42
verification. September 10 native Admin verifies `contact_submit` as primary key event,
counting **Once per event**. Its original designation effective date remains
unknown; the readback date does not establish when counting began.
Keep `contact_click` outside key-event totals. Neither designation nor dimension
registration repairs historical data.

The implemented form and booking paths are parallel. Email remains an allowed
measurement method, but the current rendered build has no active mailto CTA;
do not imply an available email path from the enum alone. `form_start` is a candidate enhanced
event, not a validated form stage. TER-43 must validate it against this form
before an ordered, closed, within-session exploration uses `contact_view` →
`form_start` → `contact_submit`. Record the order, open/closed setting and time
constraints. Report email/booking intent separately; count actual bookings from
calendar receipts. Never divide unrelated event totals to infer an ordered
funnel or call `contact_click / contact_view` a qualified-lead conversion rate.

Every rate must name numerator, denominator, population, timeframe and scope.
A validated ordered funnel may use completing users / entering users from that
same exploration/window; otherwise report counts without a funnel rate.

## Consent, host and bounded attribution contract

Production collection is allowed only on the two exact public hosts, using
`G-NF6SVCGZDF` with `debugMode` false. Local/preview defaults to disabled; isolated
debug testing requires a distinct test ID. Automated tests alone do not establish
live acceptance (TER-39/TER-41/TER-44).

`page_location` contains origin plus pathname; `page_path` contains pathname.
Raw query strings, fragments, referrer paths and unknown values stay excluded.
This bounded amendment replaces blanket-blank referrers only for these exact
hosts, evaluated after consent and host eligibility:

| Exact HTTPS referrer hosts | Canonical `page_referrer` |
| --- | --- |
| `google.com`, `www.google.com` | `https://www.google.com/` |
| `bing.com`, `www.bing.com` | `https://www.bing.com/` |
| `linkedin.com`, `www.linkedin.com`, `lnkd.in` | `https://www.linkedin.com/` |

Reject malformed URLs, credentials, non-HTTPS URLs, unsupported ports,
self-referrals, suffix lookalikes and unknown hosts. Unknown referrers remain
blank. Apply the sanitized origin consistently to configuration/custom events;
keep advertising signals disabled. Store no attribution before consent.

The registry permits only complete exact four-value tuples mapped to fixed
`campaign_source`, `campaign_medium`, `campaign_name`, `campaign_content`
configuration fields once per initialization. Reject duplicate, incomplete,
unknown and free-text values. Other query parameters remain excluded.

| Planned placement | utm_source | utm_medium | utm_campaign | utm_content |
| --- | --- | --- | --- | --- |
| LinkedIn profile | `linkedin` | `social` | `website_baseline_2026_09` | `profile` |
| Newsletter footer | `newsletter` | `email` | `website_baseline_2026_09` | `footer` |

These are planned tags, not sent campaigns or observed sources. TER-41 requires
actual network payload inspection to ensure the Google library does not re-read
rejected values, plus native classification of controlled visits. Do not relax
the allowlist to populate a report. This contract is not deployment evidence.

Privacy-choice reset immediately disables further site tracking, removes known
first-party GA cookies and permits a new choice. New cookies are host-only;
revocation attempts current/legacy GA names across host-only, www-host and
parent-domain scopes. A missing measurement ID disables GA4. The YouTube
privacy-enhanced iframe can contact YouTube independently of analytics consent;
retain the banner disclosure.

Before release, read back automatic outbound-click collection disabled (avoiding
full `link_url` and overlap), email/query-parameter redaction enabled, and all
remaining enhanced-measurement settings compatible with this contract. Record
unwanted-referral and retention settings. September 10 native readback confirms automatic outbound OFF, email redaction
ON and query redaction ON for `email`, `firstname`, `lastname`, `address`, `phone`.
Site search was disabled after an intercepted payload demonstrated a `q` marker
leak; OFF persisted after reload and reopening settings. Form interactions,
page views, scroll, video and download collection remain ON. `form_start` still
requires contact-form validation, and configuration readback alone does not prove
all payloads are private. Shared-property changes require impact review. This portfolio has no checkout: ecommerce/revenue are not applicable;
do not emit synthetic purchases or transactions.

## Four reproducible native reports

Save all four reports in the property above. Apply stream ID AND public-host
filters, the same settled fixed inclusive dates, and only proven internal/test
exclusions. Record exclusion definitions, effective dates and residual limits.
Use a native exploration if a standard report cannot express both scope filters.
A navigation URL alone does not prove a saved scoped report.

| Saved name | Layout and dimensions | Metrics | Saved URL / acceptance |
| --- | --- | --- | --- |
| Website — Production traffic | Free-form Date rows; Hostname/Stream ID for scope audit; separate `session_start` event tab | Views, Total users, Active users, Sessions, Engaged sessions; Event count in event tab | [Saved exploration](https://analytics.google.com/analytics/web/#/analysis/a391533598p533228502/edit/Zi76PnDmSdKlCAe6RqVFkA); acceptance pending |
| Website — Production acquisition | Session source / medium rows, Session campaign secondary; separate first-user source / medium tab | Sessions, Engaged sessions, Engagement rate; New users in first-user tab | [Saved exploration](https://analytics.google.com/analytics/web/#/analysis/a391533598p533228502/edit/pWUbebTBTHSLODx2oW-mag); acceptance pending |
| Website — Production content | Page path and screen class rows; separate Landing page tab | Views, Active users, average engagement time per active user; Sessions/Engaged sessions for landing pages | [Saved exploration](https://analytics.google.com/analytics/web/#/analysis/a391533598p533228502/edit/q09eRrmSQ2ijuHPnM63hHw); acceptance pending |
| Website — Production contact | Event name: `contact_view`, `contact_click`, `contact_submit`; `form_start` only after validation; click tabs by registered method/placement/destination | Event count, Total users per event; `contact_submit` key events separately; private verified-inquiry aggregate alongside | [Saved exploration](https://analytics.google.com/analytics/web/#/analysis/a391533598p533228502/edit/XBuxaflaQdykKLcErkJ4FQ); acceptance pending |

The saved historical snapshot uses August 13–September 7, 2026 inclusive. The content metric selector did not offer average engagement time per active user on September 10; this requested metric remains unavailable and is not silently replaced with a session-based average. Saved layouts and remaining acceptance limits are recorded in [the verification record](2026-09-10-acceptance-evidence.md).

Content groups must be non-overlapping: exact `/`, exact `/blog/`, articles under
`/blog/`, service paths under `/services/`, and Other. Unknown dimension rows stay
explicit. Do not sum unique users across page, date, host or event rows.

Repeat the historical acquisition comparison (33 total sessions versus 35 summed
rows) with identical settled dates, report identity, filters and compatible
session dimensions. Capture total and every row, reporting identity,
thresholding/sampling/data-quality notices, row limits and aggregation behavior.
Investigate without preselecting a cause. If unresolved, preserve both totals
and label the limitation; suppress channel shares instead of normalizing rows.

Each export's private manifest must record: saved report name/URL/native ID;
property/stream; timezone label; inclusive dates; dimensions/metrics; exact filters
and exclusions; reporting identity; thresholding/sampling/data-quality state;
native totals/row counts; extraction UTC timestamp; latest complete day and
processing lag; original and retained filenames; SHA-256; settings/release
regime; and readback evidence of scope. CSV headers can omit temporary filters.
Reopen every saved URL, verify scope and export before accepting TER-45.

Use this readout template: window/timezone/regime and acceptance evidence; four
native URLs and manifest; traffic totals; acquisition reconciliation; content
counts by group/path; parallel contact paths and private verified-intake
aggregates; Search Console context; data-quality limitations; evidence-backed
findings; directional observations; untestable hypotheses; and prioritized next
actions with owner. Keep private intake content outside GA4 and public artifacts.

## Preserved history and issue ownership

The original readout, manifest and eight native CSVs remain unchanged in the
private `ga4-evidence` bundle referenced by TER-38. All eight CSV SHA-256 values
were rechecked against the original manifest September 10, 2026. Public git
contains aggregate provenance only. Manifest SHA-256:
`a7b4ab7252c6674c725e77fc3332ed53c1439f2e384ddddbce26aa05e3f1e75d`.
Readout SHA-256: `2de59c95aa43afb1a79ab10c7e7dd7823104d2cd373b586a8fd749775fc32dbc`.
The original manifest did not independently record timezone or an explicit
stream filter; do not retroactively assert those settings for old exports.

| Historical finding | Interpretation | Owner issue |
| --- | --- | --- |
| 90 public-host views, 11 page-view users; September 8 accounts for 55 views (61.1%) | Small concentrated consented sample, no trend conclusion | TER-38, TER-47 |
| 21 local-host events including two CTA clicks | Public-host filtering removes local visits; public owner visits may remain | TER-39, TER-40 |
| Direct and (not set), blank referrer, stripped query | Attribution limited; search/social absence not established | TER-41 |
| No dimensions at historical readout | Registration needs new eligible data; no backfill | TER-42 |
| Two `contact_submit` events from one measured user, August 30 and September 1; zero reported key events | Raw events remain separate from key-event totals; legitimate inquiries Unknown | TER-43 |
| TER-29/TER-37 intake items have different dates | Related context only, not established matches | TER-43 |
| All-host history acquisition total 33 versus rows summing to 35 | Unresolved; no channel-share percentages | TER-45 |
| Homepage 47 views, blog index 21, articles 21, service pages one | Cannot diagnose offer or SEO performance | TER-46, TER-47 |

## Thirty-day baseline gates

TER-47 begins only with TER-44 release and TER-45 report acceptance evidence;
TER-46 supplies Search Console context or an explicit access/no-data limitation.
Record both acceptance timestamps in the property timezone. Day 1 is the next
complete property-calendar day after the later acceptance; Day 30 is Day 1 plus
29 calendar days. Wait at least 48 hours after Day 30 closes before final
extraction, longer if processing is provisional. Current baseline dates remain
pending; September 21 acceptance would imply September 22–October 21 collection
and October 24 review. Rebase Linear dates if acceptance shifts. No reminder
automation is implied.

At days 7 and 14, record continuity, hostname leakage, owner/test contamination,
campaign classification, populated dimensions and intake/delivery reconciliation.
Diagnose missing days before treating them as zero traffic. Log material changes
with effective timestamps; restart or explicitly separate incompatible regimes.

After 30 complete days and processing lag, reproduce all four reports with
provenance, Search Console context and verified inquiry aggregates. Prioritize
proven delivery faults and observed indexing faults; change a contact step only
with a credible denominator. If volumes remain small, extend observation or use
qualitative inquiry evidence. Completion requires check records, final readout,
limitations, owner handoff and evidence-based next actions, not a due date.

## Measurement change log

| Date | Change / observation | Acceptance evidence |
| --- | --- | --- |
| September 10, 2026 historical export | Blank-referrer regime; possible public owner contamination; Testing filter; no custom dimensions | Private manifest/readout, not a clean baseline |
| September 10, 2026 contract revision | Correct success/intent distinction; bounded attribution, report definitions and baseline gates | Documentation only, not release/report acceptance |
| September 10, 2026 timezone readback | United Kingdom; selected `(GMT-07:00) GMT-07:00`, unchanged | Native property settings, no historical timezone-change claim |
| September 10, 2026 live settings | Site search disabled with persisted readback; outbound OFF; redaction ON; internal rules absent; contact_submit Once per event | Native Admin; live payload and receipt acceptance remains separate |
| September 10, 2026 custom dimensions | Three Event-scoped definitions registered and read back | Native Admin definitions; eligible new-event population pending |

Append actual configuration effective dates, code/serving revision, payload and
receipt evidence, saved report URLs, acceptance timestamps and baseline dates
when verified. This document alone does not complete TER-38, TER-45 or TER-47.
