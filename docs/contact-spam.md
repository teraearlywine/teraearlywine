# Contact spam controls

The website POST `/contact` validates CSRF, fields and its honeypot, then signs a request to the `pj-engine` broker POST `/api/contact-deliveries`. The broker applies one shared spam filter before reserving delivery, queuing email or creating Linear issues. The website does not maintain a separate lead store. Rejections and suppressed duplicates never claim successful delivery or emit the contact conversion event.

The broker configuration in `packages/shared/src/contact-spam.ts` contains the two exact blocked addresses and Bengali, Armenian and Icelandic source templates from TER-29, TER-37 and TER-50. Only the exact name Roberttek plus an exact normalized template triggers the name rule. Normalization preserves scripts and combining marks. Gmail, Robert prefixes and price questions are allowed.

Firestore transactions enforce 24-hour duplicates across sessions and instances, 5 requests per email and 100 global requests per 15 minutes by default. The broker's CONTACT_SPAM_* variables configure bounds. Only HMAC fingerprints, owner IDs, expiry and counters are retained in `contactSpamState`; enable TTL on `expiresAt`. Rejection logs contain rule ID, timestamp and count, with no message body. Cloud Logging can sum counts grouped by rule ID.

Short text repeated three times plus completion under three seconds requires Turnstile verification. The website signs elapsed time derived from its server-issued session record; client-supplied timing is ignored. The broker retains challenge state to prevent waiting before retry from bypassing verification. The broker verifies tokens with Cloudflare, including expected hostname and `contact` action. Tokens are not stored or logged. Missing provider credentials or provider errors cannot grant verification.

Configure CONTACT_TURNSTILE_SITE_KEY on the website and CONTACT_TURNSTILE_SECRET (Secret Manager) plus CONTACT_TURNSTILE_HOSTNAME on the broker. Follow https://developers.cloudflare.com/turnstile/get-started/server-side-validation/. Until credentials are configured, flagged visitors receive verification-unavailable feedback and cannot complete that challenged submission. This is a release acceptance gap, not completed bot verification.

Deploy the broker before this website change because the HMAC payload now includes `spamContext`. Broker delivery identity excludes this changing context, preserving recovery after timeouts and challenge retries. Roll back the website before rolling back the broker. A broker outage fails closed with no local fallback delivery.

## Reproduce tests

Run `python -m pytest -q` for website regressions. To exercise real website-to-broker HTTP, build the coordinated pj-engine branch, start a local Firestore emulator at 127.0.0.1:8686 for project demo-contact-spam, then run its `scripts/contact-spam-e2e-server.mjs` with FIRESTORE_EMULATOR_HOST=127.0.0.1:8686 and GOOGLE_CLOUD_PROJECT=demo-contact-spam. In this checkout run:

    CONTACT_E2E_BROKER=http://127.0.0.1:8787 python -m pytest tests/test_contact_e2e.py -q

The broker fixture uses the real signature validation, spam rules and Firestore transaction. It counts mail, Linear and operation calls instead of contacting providers. Its challenge verifier accepts only the explicit test token; separate broker tests exercise the real provider verifier against success, wrong hostname/action, invalid tokens and network failure. The fixture is loopback-only and refuses a production project.

The 17 HTTP scenarios cover nine spam replays, four legitimate language/price cases, cross-session normalized duplicates, honeypot rejection, rate limiting, and challenge rejection/solved retry. Native staged Gmail and Linear receipts must be verified separately; fixture success is not provider delivery evidence.

## Staged acceptance — 2026-09-11 19:39 UTC

Website PR: https://github.com/teraearlywine/teraearlywine/pull/34. Broker PR: https://github.com/idea-factory-lab/pj-engine/pull/142.

The Cloud Build ba6c912d-105c-4b4c-a069-25cbdb246901 image deployed as if-api-contact-spam-7e3c724. Website version contact-spam-1f30629 points to that tagged broker. Both serve 0% of production traffic. The staged website is https://contact-spam-1f30629-dot-teraearlywine.uw.r.appspot.com.

All three source spam replays returned HTTP 403 with generic text. For each submission below, Firestore returned no contactDeliveries document and no mail document. Gmail exact-ID search returned no messages; the complete Linear creation window contained only the approved QA receipt. Cloud Logging contained exactly three blocked_email count=1 events, with no submitted text.

- dfa325df-eaff-4287-891f-3cebf316838e — rejected; no delivery or mail record.
- abad6b8b-3b15-4635-9c0b-2a46e6b3056f — rejected; no delivery or mail record.
- 2100a3d3-c5dd-4a3b-8432-7d74dd27bd81 — rejected; no delivery or mail record.

Approved test submission 98cc8162-2d9f-45c9-ae48-13fcee3a37d2 returned HTTP 200. Firestore delivery status is completed and mail delivery state SUCCESS. Native Gmail receipt: https://mail.google.com/mail/#all/1a091fb0d07f746a. Native Linear receipt: https://linear.app/idea-factory-lab/issue/TER-51/qa-only-contact-spam-filter-acceptance-receipt (marked QA-only and canceled after verification). Marker: contact-spam-acceptance-20260911T193851Z.

Validation totals: website 171 passed; shared 160 passed; database 31 passed; API 376 passed, one existing skip. All 17 separately enabled HTTP end-to-end scenarios passed. The Firestore emulator concurrency/expiry/rate/challenge scenario passed, and scoped build, lint and typecheck passed. Firestore TTL on contactSpamState.expiresAt is ACTIVE.

Production has not been promoted. Live Turnstile challenge completion remains unverified because the public site key and broker secret are not configured. Supply the site key and a Secret Manager reference for the secret to finish provider acceptance and production rollout. Local challenge rendering, server verification checks and solved/rejected retry paths are tested; they are not a substitute for provider acceptance.
