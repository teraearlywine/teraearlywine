# GA4 measurement plan

This document is the measurement contract for teraearlywine.com. It covers the
current portfolio only. The site measures consulting interest, not completed
sales.

## Business questions and KPIs

| Area | Question | KPI | Source |
| --- | --- | --- | --- |
| Brand | Is awareness of Tera increasing? | Branded impressions, clicks, CTR, and average position for queries matching `tera earlywine` or `teraearlywine` | Search Console |
| Acquisition | Which channels introduce useful visitors? | New users by first-user source/medium and engaged sessions by session source/medium/campaign | GA4 |
| Content | Which landing pages and destinations create interest? | Organic landing-page engagement and outbound clicks by destination type | GA4 |
| Conversion | Do visitors reach and act on the contact offer? | `contact_view` count, `contact_click` count, and `contact_click / contact_view` intent rate | GA4 |
| SEO | Is organic visibility and site quality improving? | Clicks, impressions, CTR, average position, indexing, and Core Web Vitals | Search Console |

Use a rolling 30-day baseline before setting targets, then review monthly.
Keep first-user acquisition and session acquisition separate: the former
describes how a user was first acquired; the latter describes the current
visit.

## Events

After explicit acceptance, GA4 collects `page_view`, session, engagement, and
approved enhanced-measurement events. Before acceptance, and after rejection,
the Google tag is not loaded and no GA4 request is sent. The site adds only the
events below.

| Event | Trigger | Parameters | Key event |
| --- | --- | --- | --- |
| `navigation_click` | A tagged internal navigation link is selected | `placement`, `destination_type` | No |
| `outbound_click` | A tagged external link is selected | `placement`, `destination_type` | No |
| `contact_view` | At least 50% of the contact section is visible once per page view | `placement` | No |
| `contact_click` | Email or booking CTA is selected | `contact_method`, `placement`, `destination_type` | Yes |

Allowed values:

- `contact_method`: `email`, `booking`
- `placement`: `navigation`, `hero`, `projects`, `contact`, `footer`, `error`
- `destination_type`: `section`, `github`, `linkedin`, `youtube`,
  `idea_factory`, `email`, `booking`, `home`

The client drops unknown event names, unknown parameters, and disallowed values.
It never sends link text, email addresses, full URLs, query strings, or
free-form user input.

GA4 receives only the current origin and path in `page_location`, and only the
path in `page_path`; query strings and fragments are removed before
configuration. `page_referrer` is explicitly blanked on configuration and
custom events so a referring page's URL cannot be transmitted. Custom events
use fixed enum values and contain no URLs.

`contact_click` measures qualified intent, not a completed lead. A confirmed
lead requires a future form success or scheduling-provider confirmation event.

## Campaign naming

Use lowercase, stable values on links controlled by this site:

- `utm_source`: the publisher or platform, such as `linkedin`
- `utm_medium`: the delivery mechanism, such as `social`, `email`, or `referral`
- `utm_campaign`: a durable initiative name, such as `portfolio_launch`
- `utm_content`: optional creative or placement variant

Use underscores, not spaces. Do not put names, emails, or other personal data
in campaign parameters.

## Consent and privacy

The site uses Basic Consent Mode: it does not create `gtag`, configure GA4,
load `gtag.js`, or send any analytics event until the visitor explicitly
accepts. Rejecting stores only the visitor's consent choice and does not grant
analytics storage or contact Google. The visitor can reopen privacy choices
from the footer, which immediately disables further site tracking, removes
known first-party GA cookies, and allows a new choice. GA4 is disabled entirely
when no measurement ID is configured.

New GA cookies are configured as host-only. Revocation attempts to remove
current and legacy GA cookie names from the host-only scope, the
`www.teraearlywine.com` host scope, and both parent-domain forms for
`teraearlywine.com`.

The embedded video uses YouTube's privacy-enhanced `youtube-nocookie.com`
domain. Because the iframe loads with the page, YouTube may still receive a
third-party request independently of the analytics choice; the consent banner
states that boundary.

The site must not place personal data in event parameters. Before adding an
event, update this contract and the allowlist in `analytics.js`.

## Ecommerce boundary

This portfolio has no product catalog, cart, checkout, payment confirmation,
or transaction identifier. Do not emit `view_item`, `add_to_cart`,
`begin_checkout`, `purchase`, revenue, or synthetic transaction data.
Ecommerce is reported as **not applicable**. Introduce GA4 ecommerce events
only when a real checkout can provide server-confirmed transaction data.

## Pre-release GA4 property prerequisites

These GA4 Admin changes are deployment gates. Complete and verify them on the
production data stream **before deploying this implementation**:

1. In enhanced measurement, disable automatic outbound click collection.
   Leaving it enabled can send the full `link_url`, outside this site's
   allowlist, and record a second outbound event alongside the site's
   privacy-reduced `outbound_click` event.
2. Enable GA4 data redaction for query parameters and user-provided email
   addresses. This is required defense in depth in addition to client-side
   sanitization.

Do not release the new GA4 implementation until both prerequisites are
complete.

## Remaining account setup checklist

Keep these account-level setup steps explicit and complete them before release
unless a step inherently requires live production data:

1. Confirm the remaining enhanced-measurement settings and exclude
   internal/developer traffic.
2. Review unwanted referrals and set data retention to the intended period.
3. Register event-scoped custom dimensions for `contact_method`, `placement`,
   and `destination_type`.
4. Mark `contact_click` as a key event.
5. Link the verified Search Console domain property and submit `/sitemap.xml`.
6. Create reports for first-user acquisition, traffic acquisition, organic
   landing pages, and outbound destinations.
7. Create a funnel exploration: `contact_view` then `contact_click`.
8. In Search Console, compare branded queries matching
   `tera earlywine|teraearlywine` with non-branded queries.

## Verification checklist

Before release:

- Run the automated test suite.
- Verify that pages omit GA4 when the measurement ID is blank.
- Verify accept, reject, and privacy-choice reset behavior.
- Confirm one event per tagged click and one `contact_view` per page view.
- Confirm event payloads contain only allowed values.
- Confirm `page_location` and `page_path` contain no query string or fragment.
- Confirm `page_referrer` is blank on configuration and custom events.
- Confirm automatic outbound-click collection is disabled and data redaction
  is enabled in the production GA4 data stream before deployment.

After release:

- Use Tag Assistant and GA4 DebugView to check page and interaction events.
- Confirm rejected consent produces no request to Google Analytics.
- Inspect `/`, `/robots.txt`, and `/sitemap.xml` in Search Console.
- Use URL Inspection to confirm the homepage canonical and structured data.
- Record a 30-day baseline, then review the KPI set monthly.
