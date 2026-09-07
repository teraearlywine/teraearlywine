# Consultancy redesign QA

Result: passed for local review, 2026-09-07. Deployment remains pending.

Implemented the confirmed warm graphite and glass concept in the existing Flask/Jinja application. Preserved the contact broker integration, CSRF protection, configured booking links, analytics consent, SEO metadata, and App Engine runtime configuration.

## Visual review

- Compared the approved 1122 × 1402 mockup with the same-size desktop crop. Corrected headline italic styling, service-row height, paragraph width, and mobile artwork overlap.
- Local Inter fonts, charcoal mineral artwork, stone accents, oversized typography, chapter notch, and three decision-led service rows follow the approved direction.
- Generated artwork has small differences from the concept; the operational booking link and expandable services are deliberate functional additions. Existing work, experience, FAQ, and contact sections continue below the mockup.
- Reviewed desktop at 1122px and mobile at 390px. No horizontal overflow or broken images; no browser console errors or warnings observed.
- Evidence: [desktop](docs/design/desktop.png), [mobile](docs/design/mobile.png).

## Functional verification

- Mobile menu opens, closes after navigation, and updates its expanded state.
- Service details expand through native accessible disclosure controls.
- Empty contact submission produces required-field validation for name, email, and message without delivery.
- Existing tests cover contact success/failure, idempotency, CSRF, analytics consent, configuration escaping, and SEO rendering.
- Final suite: 52 passed, 1 skipped (private analytics reference document absent). `git diff --check` passed.
- Live message delivery was not exercised; local preview does not contain production broker credentials.

## Run and deploy

Use the repository's existing Python requirements and Flask entry point. Local preview is running at http://127.0.0.1:8088/.

The existing `app.yaml` remains unchanged. Google Cloud CLI authentication expired, and the configured default project was not verified as this site's production project. Reauthenticate and verify the correct App Engine project before deploying this branch with the existing workflow. No production deployment or GitHub push was performed.

## Assets

Hero artwork was generated from the approved visual. The JPEG is served; the PNG is retained as source. Inter is bundled under its accompanying font license. Arrow icons are from Feather under `core/home/assets/images/FEATHER-LICENSE.txt`.
