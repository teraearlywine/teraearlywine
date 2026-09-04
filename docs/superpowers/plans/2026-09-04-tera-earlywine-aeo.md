# Tera Earlywine AEO Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert `teraearlywine.com` into the canonical answer-engine authority hub for Tera Earlywine and generate qualified enterprise data and AI consulting fit calls.

**Architecture:** Preserve the Flask single-page application and make the homepage the source of truth for identity, services, proof, and conversion. Keep visible copy and JSON-LD derived from the same fixed public claims, align the GitHub profile README, and preserve existing contact, analytics, sitemap, and robots behavior.

**Tech Stack:** Python 3.12, Flask 3.1, Jinja2, semantic HTML, CSS, JSON-LD, pytest.

**Spec:** `docs/superpowers/specs/2026-09-04-tera-earlywine-aeo-design.md`

## Global Constraints

- Lead category: `production-grade data and AI for regulated, high-consequence operations`.
- Primary entity: `Tera Earlywine`.
- Primary CTA label: `Book a fit call`.
- Voice: casual, direct, technically credible, and human.
- Proof: named employers and clients with sanitized outcomes only.
- Preserve the existing Flask architecture, secure contact delivery, analytics consent, accessibility, responsiveness, canonical URL, robots, sitemap, and Search Console support.
- Never publish confidential client systems, incidents, data, or unsupported attribution.

---

### Task 1: Lock the AEO content contract in tests

**Files:**
- Modify: `tests/test_analytics_reporting.py`
- Modify: `tests/test_contact.py`

**Interfaces:**
- Consumes: `render_home(app)` and `collect_elements(document, tag)`.
- Produces: regression expectations for public positioning, CTAs, visible FAQ answers, and JSON-LD graph nodes.

- [ ] **Step 1: Add a failing homepage positioning test**

Assert that the rendered page includes the exact specialty, the four buyer problem categories, the sanitized proof figures, and at least two `Book a fit call` links when `BOOKING_URL` is configured.

- [ ] **Step 2: Add a failing structured-data test**

Parse the JSON-LD block and assert that the graph contains `Person`, `ProfessionalService`, and `FAQPage`; verify Tera's name, consulting job title, specialty, same-as URLs, and FAQ parity with the visible page.

- [ ] **Step 3: Update the existing CTA contract test**

Keep the configured booking URL, analytics event, placement, and destination assertions while asserting the new buyer-facing CTA label.

- [ ] **Step 4: Run the focused tests and confirm they fail for missing AEO content**

Run: `.venv/bin/pytest tests/test_analytics_reporting.py tests/test_contact.py -q`

Expected: new AEO assertions fail; existing contact and security assertions remain passing except the known ignored analytics-document fixture.

- [ ] **Step 5: Commit the test contract**

Run: `git add tests && git commit -m "test: define AEO positioning contract"`

### Task 2: Rewrite the public authority and conversion surface

**Files:**
- Modify: `core/home/templates/home/home.html`
- Modify: `core/home/templates/home/sections/hero.html`
- Modify: `core/home/templates/home/sections/projects.html`
- Modify: `core/home/templates/home/sections/skills.html`
- Modify: `core/home/templates/home/sections/timeline.html`
- Modify: `core/home/templates/home/sections/contact.html`
- Modify: `core/home/templates/home/core/navigation.html`
- Create: `core/home/templates/home/sections/method.html`
- Create: `core/home/templates/home/sections/faq.html`

**Interfaces:**
- Consumes: `config['BOOKING_URL']`, existing analytics data attributes, and the secure contact form.
- Produces: one coherent narrative from specialty to proof to fit-call booking, plus visible FAQ content mirrored by JSON-LD.

- [ ] **Step 1: Replace the hero identity and actions**

Use `Independent Data & AI Consultant` as the role, the exact specialty in the eyebrow copy, and the headline `I fix the data systems your reporting, compliance, and AI depend on.` Add `Book a fit call` and `See the work` actions without exposing a dead link when booking is unconfigured.

- [ ] **Step 2: Replace generic projects with sanitized commercial proof**

Show `Enterprise platform modernization`, `Compliance operations automation`, and `Data infrastructure efficiency`. Support only the public claims: 500+ workflows, $500K+ savings, Block compliance advisory, and experience across Block and Mercari.

- [ ] **Step 3: Turn the skills inventory into buyer problems**

Present reliability and migration rescue, AI-ready data foundations, production AI systems, and fractional platform leadership. Retain technical tools as supporting evidence rather than the main message.

- [ ] **Step 4: Add the engagement method and FAQ**

Render Diagnose → Blueprint → Prove → Scale → Operate and direct answers to the five buyer questions in the spec.

- [ ] **Step 5: Reframe experience and contact**

Make independent consulting the current primary role, keep the accurate career chronology, and make the booking action primary while retaining the form.

- [ ] **Step 6: Run the focused test suite**

Run: `.venv/bin/pytest tests/test_analytics_reporting.py tests/test_contact.py -q`

Expected: all new content and CTA tests pass; only the pre-existing ignored analytics-plan fixture may fail.

- [ ] **Step 7: Commit the public surface**

Run: `git add core tests && git commit -m "feat: position Tera for enterprise data and AI consulting"`

### Task 3: Add semantic styling and answer-engine metadata

**Files:**
- Modify: `core/home/assets/css/main.css`
- Modify: `core/home/assets/css/media.css`
- Modify: `core/home/templates/home/includes/header.html`
- Modify: `core/home/home.py`

**Interfaces:**
- Consumes: `_site_url()`, `request.endpoint`, `seo_metadata()`, and the visible FAQ contract.
- Produces: responsive lead-generation styling, consistent page metadata, and JSON-LD nodes whose claims match the page.

- [ ] **Step 1: Style proof, services, method, FAQ, and hero actions**

Extend existing tokens and layout patterns. Keep body text at least 1rem, preserve strong contrast, add visible focus states, and collapse grids cleanly below 768px.

- [ ] **Step 2: Replace generic page metadata**

Set the title to `Tera Earlywine | Enterprise Data & AI Consultant` and describe the exact specialty plus the reliability, modernization, governance, and production-AI services.

- [ ] **Step 3: Extend the JSON-LD graph**

Update `Person.jobTitle`, add `knowsAbout`, connect the person and professional service, list supported service types and areas served, and add a `FAQPage` node with answers identical to visible FAQ content.

- [ ] **Step 4: Run all tests except the known missing ignored document**

Run: `.venv/bin/pytest -q --ignore-glob='*ga4-measurement-plan.md'`

Expected: 52 collected tests with only the pre-existing missing-document assertion requiring a local fixture.

- [ ] **Step 5: Commit metadata and presentation**

Run: `git add core tests && git commit -m "feat: add AEO metadata and conversion styling"`

### Task 4: Align the public GitHub identity and ship the branch

**Files:**
- Modify: `README.md`
- Create: `docs/aeo/90-day-acquisition-plan.md`

**Interfaces:**
- Consumes: the homepage positioning and CTA.
- Produces: consistent GitHub identity and a sequenced 90-day corroboration plan.

- [ ] **Step 1: Rewrite the profile README**

Identify Tera as an independent data and AI consultant for regulated, high-consequence operations; summarize sanitized proof; link to the canonical website and LinkedIn; remove `Open to senior analytics engineering roles`.

- [ ] **Step 2: Write the 90-day acquisition plan**

Sequence profile alignment, case studies, content clusters, third-party corroboration, stale-profile cleanup, answer-engine query testing, and conversion review. Include weekly outputs and measurable lead indicators.

- [ ] **Step 3: Run the complete verification suite**

Run: `.venv/bin/pytest -q`

Expected: all executable application tests pass; if the ignored analytics measurement-plan fixture remains absent, document it as a pre-existing repository packaging defect and separately verify every test except that single assertion.

- [ ] **Step 4: Inspect the rendered HTML contract**

Run Flask's test client to save the homepage response, validate one H1, booking URLs, canonical metadata, parseable JSON-LD, visible FAQ parity, and absence of confidential terms.

- [ ] **Step 5: Commit the alignment and plan**

Run: `git add README.md docs && git commit -m "docs: align public identity and AEO rollout"`

- [ ] **Step 6: Push the exact branch state and open a pull request**

Push `codex/aeo-conversion`, open a pull request to `main`, and do not merge until CI or equivalent verification is green.
