# Contact outcome reconciliation — TER-43

Audit date: September 10, 2026. Source implementation: `46519e2a8222f9dd6022805d578422f345c9fbf3` (origin/main). Status: **Review; live acceptance incomplete**.

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
| `contact_submit` | The enhanced form dispatches `contact:submitted` after an accepted success response. Analytics then gates collection on consent and sends no contact fields or ID. | GA4 receipt, exact unique-delivery counts and an actual business inquiry require separate evidence. A non-JavaScript successful form has no browser success event. |
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

The existing analytics harness separately checks that accepted-consent `contact:submitted` produces `contact_submit` without private event detail. These are local contract tests, not real broker, mailbox, calendar or GA4 receipts. No contact submission or message was sent during this audit.

## Remaining acceptance evidence

1. Preserve the fixed property timezone readback and the original GA4 export provenance with the private audit evidence. Keep both historical events **Unknown** unless a unique, evidence-supported match becomes available; the later Linear records cannot supply that match.
2. For one separately authorized controlled production success, record a private QA marker, exact timestamp/offset, submitted opaque ID, accepted broker receipt, exactly one provider/intake delivery and the corresponding consented `contact_submit` receipt in the intended GA4 stream. Keep private identifiers out of GA4 and public evidence.
3. Repeat the same opaque request in a controlled fixture or explicitly authorized production test and establish one delivery total. Verify invalid validation and delivery failure produce no `contact_submit`; a simulated local upstream failure is not a production-provider failure receipt.
4. Verify consent acceptance/refusal/revocation and actual network payloads on the serving release. Do not mark live acceptance complete based on mocked tests.
5. Verify any claimed booked call with its native calendar receipt. If email is later exposed as a CTA, verify its rendered destination and report its click as intent only.
6. Validate enhanced `form_start` against the actual form in an isolated test collection context. Until that happens, retain it as an unvalidated metric and omit ordered-form conversion rates.
