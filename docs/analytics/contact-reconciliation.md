# Contact outcome reconciliation — TER-43

Audit and acceptance date: September 10, 2026. Original audit implementation: `46519e2a8222f9dd6022805d578422f345c9fbf3`. Status: **Acceptance complete for TER-43 scoped criteria**; continuing evidence boundaries are recorded below.

## Current acceptance closure

The [acceptance evidence](2026-09-10-acceptance-evidence.md), completed in [PR #31](https://github.com/teraearlywine/teraearlywine/pull/31) and [PR #32](https://github.com/teraearlywine/teraearlywine/pull/32), closes TER-43's scoped acceptance. One corrected-release QA submission at `2026-09-10T19:39:33.197Z` produced one observed mailbox notification and one matching intake receipt, [TER-49](https://linear.app/idea-factory-lab/issue/TER-49), explicitly canceled as QA. The private request marker matched those two delivery records and remains outside analytics.

A subsequent native QA exploration filtered to Stream ID `15512913765` and public-host regex `^(www\.)?teraearlywine\.com$` showed **1 `contact_submit` event, 1 user and 1 key event**. Hour `2026091012` at GMT-07:00 is consistent with the controlled submission; it is not a unique join to the private delivery records. Source remained `(not set)`. The Today selector resolved to September 10 at observation, rather than defining an immutable report window.

Existing controlled fixtures establish invalid/failure, repeated-request and concurrent-submit behavior within their tested scope. Serving-release consent and actual network checks are recorded in the acceptance evidence. Together with the controlled delivery and scoped native success receipt, these satisfy TER-43; a live provider failure/replay exercise or private-identifier analytics join is not an additional closure requirement. Provider-wide persistence/idempotency remains unproved, historical outcomes remain **Unknown**, enhanced `form_start` remains excluded pending follow-up, and booking clicks remain intent only. This contact-specific closure does not establish campaign attribution, a clean traffic baseline or a completed booking.

## Historical evidence

The September 10 GA4 readout reports one `contact_submit` on August 30 and one on September 1, from one measured user across those events. Neither event establishes a legitimate inquiry or a qualified lead. The property timezone was read back in native Admin as **`(GMT-07:00) GMT-07:00`** on September 10. The timestamps below use that fixed offset; no geographic timezone or daylight-saving rule is inferred.

A read-only Gmail search used `in:anywhere after:2026/08/29 before:2026/09/03 {subject:"Website contact" "portfolio-contact:"}`. All eight returned messages were inspected: seven original contact notifications and one reply. This is a scoped mailbox search, not proof of complete broker/provider history. Names, email addresses, message text, Gmail identifiers and request markers stay in the original private systems.

| GA4 event date (GMT-07:00) | Candidate original mailbox receipt times (GMT-07:00) | Reconciliation |
| --- | --- | --- |
| 2026-08-30 | 18:36:25, 19:45:22, 21:20:10, 21:25:35 | **Unknown**; four receipts cannot uniquely identify one aggregate success event. |
| 2026-09-01 | 05:13:16, 07:47:56, 07:57:54 | **Unknown**; three receipts cannot uniquely identify one aggregate success event. |

The four August 30 receipts have UTC dates of August 31. The September 1 reply at 08:24:58 GMT-07:00 is not an additional form submission. Three original notifications contain generic test or automation indicators. Those indicators are insufficient to assign either GA4 event to a test, or to classify other candidates as legitimate inquiries or spam. None of the seven original notifications contains a `portfolio-contact:` request marker. Mailbox presence establishes receipt of a notification; the original broker response, provider delivery status and one-to-one GA4 linkage remain **Unknown**.

The full [TER-29](https://linear.app/idea-factory-lab/issue/TER-29) and [TER-37](https://linear.app/idea-factory-lab/issue/TER-37) intake records were read on September 10. Their submitted timestamps are respectively `2026-09-03T18:29:36.969Z` and `2026-09-09T04:36:46.604Z` (September 3 11:29:36.969 and September 8 21:36:46.604 at GMT-07:00). Their later dates do not match either historical event day. Both are related context only; no identity is inferred from GA4. TER-29, TER-37 and [TER-43](https://linear.app/idea-factory-lab/issue/TER-43) had no comments on readback. Their content, projects and statuses were preserved.

## Contact paths and evidence boundaries

| Path or metric | What is established | What is not established |
| --- | --- | --- |
| Contact form | `/contact` validates fields, CSRF, honeypot and the session-issued opaque ID. It accepts a broker receipt only with a matching submission ID and boolean replay flag. | A success response alone does not establish a legitimate inquiry, provider delivery status or qualified opportunity. |
| Repeated form request | Session state reuses successful delivery state; normalized content is bound to the ID. Broker HMAC requests reuse that ID on retry. | Local tests do not prove broker persistence, provider idempotency or production behavior under concurrent requests with stale cookies. |
| `contact_submit` | The enhanced form dispatches `contact:submitted` after an accepted success response. Analytics then gates collection on consent and sends no contact fields or ID. | A scoped native QA success receipt is now observed; exact unique-delivery counts and an actual business inquiry require separate evidence. A non-JavaScript successful form has no browser success event. |
| `contact_click` booking | Configured booking links occur in homepage hero/contact and service hero templates. The configured destination is a Google Calendar booking link. | A click does not establish a booked call. Count bookings only after a native calendar booking receipt is reviewed. |
| Email intent | The analytics schema can represent `contact_method=email`. | No `mailto:` link exists in the audited templates. Email is not an active measured contact path in this build. A delivered inbound email must be verified in intake/mailbox evidence. |
| Enhanced `form_start` | No application-specific `form_start` implementation exists in the audited source. | Correspondence to this contact form has not been established. Exclude it from conversion calculations until a controlled native browser/GA4 check confirms the originating form and ordering. |

Consent refusal, blockers, retries and timing can separate true intake from GA4 events. Do not add private submission identifiers to analytics to force a join. Counts across independent paths and event-specific users are not an ordered funnel.

## Local verification

The existing `tests/test_contact.py` suite passed all 25 cases with mocked broker delivery. It exercises invalid fields, CSRF, honeypot, successful signed delivery, failure/retry, repeated successful requests, changed content under a reused ID, timeout, invalid receipt and oversized requests. The browser form harness previously discarded dispatched events, so it could not catch a regression that emitted success on failure. Focused assertions now verify:

- Accepted success emits exactly one `contact:submitted` and rotates the form ID.
- Invalid local validation, HTTP 400/502/503, unsuccessful or incomplete success payloads, invalid JSON and timeout emit no success event.
- A second submit while the first request is in flight makes no second request and emits no extra success.
- Failure keeps the original form ID for a safe retry.

The existing analytics harness separately checks that accepted-consent `contact:submitted` produces `contact_submit` without private event detail. These are local contract tests, not real broker, mailbox, calendar or GA4 receipts. No contact submission or message was sent during the original local audit; the later authorized controlled production receipt is recorded above.

## Historical acceptance checklist and continuing boundaries

The original checklist is resolved for TER-43 as follows; these entries distinguish completed scoped checks from ongoing reporting limits.

1. **Fulfilled:** fixed property timezone and original export provenance are retained. Both historical events remain **Unknown**; later Linear records do not establish a match.
2. **Fulfilled:** the authorized corrected-release success has one observed mailbox notification, one matching intake receipt and a scoped native `contact_submit`/key-event receipt. Hour-level consistency does not establish a unique analytics-to-delivery join. Private identifiers remain outside GA4 and public evidence.
3. **Fulfilled within fixture scope:** invalid/failure, repeated-success and concurrent-submit checks establish the tested behavior. They do not prove provider-wide persistence/idempotency or a live provider failure. Those broader claims are outside this closure; another production failure/replay test is not required for TER-43 acceptance.
4. **Fulfilled:** serving-release consent acceptance/refusal/revocation and actual network payload checks are recorded in the acceptance evidence, separately from mocked tests.
5. **Continuing boundary:** a booked call requires a native calendar receipt. No booking is claimed; booking clicks are intent only. Any future email CTA requires destination and intent verification.
6. **Follow-up, excluded from current metrics:** enhanced `form_start` remains unvalidated against the actual contact form. Omit it and ordered-form conversion rates until isolated validation establishes the originating form and ordering.
