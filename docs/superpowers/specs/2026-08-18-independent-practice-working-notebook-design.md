# Independent Practice + Working Notebook Design

Date: 2026-08-18
Status: Approved for implementation planning

## Summary

Refactor `www.teraearlywine.com` from a resume-oriented portfolio into Tera Earlywine's independent data practice and working notebook. The site must serve two goals with equal prominence:

1. Help data and engineering leaders at established companies understand and initiate consulting work.
2. Publish Tera's articles, videos, tools, and downloadable resources directly on the site.

The implementation will retain the existing Flask/Jinja application and Google App Engine deployment. Publishing will use repository-managed Markdown rather than a database or external CMS.

## Audience and Positioning

Primary consulting audience: data and engineering leaders at established companies.

Consulting offer: a focused mix of platform direction, hands-on engineering delivery, and improvements to operating practices.

Positioning statement: Tera works where platform decisions, operating reality, and business trust meet. The site should demonstrate this through useful work and writing rather than resume density or unsupported marketing claims.

## Success Criteria

- Consulting and publishing receive equal prominence in the first viewport.
- A buyer can understand the consulting offer and reach email or scheduling options without reading a career timeline.
- A reader can discover notes and resources from the homepage and browse their dedicated indexes.
- New notes and resources can be published by adding validated Markdown files to the repository.
- The existing embedded YouTube video remains featured media.
- The layout is polished and usable on desktop and mobile.
- Existing uncommitted hero/video work is preserved during implementation.

## Approved Visual Direction

Theme: independent studio + working notebook.

The site preserves the current minimalist character while becoming more editorial:

- Near-white `#FAFAFA` background, not cream or beige.
- Charcoal `#1D1D1F` text and muted gray secondary copy.
- Crisp `#0071E3` blue for links, focus, and primary actions.
- Editorial serif headings paired with a disciplined modern sans-serif for navigation, body text, metadata, and controls.
- Open bands, lists, and document rails rather than generic card grids.
- Hairline rules, restrained shadows, 8–12px media radii, and generous whitespace.
- Sparse folio notation such as `01 / 04` as a recurring editorial detail.
- Subtle entrance and hover motion with a reduced-motion alternative.

The four approved concepts are the visual source of truth:

1. [Opening](assets/2026-08-18-independent-practice/01-opening.png)
2. [Consulting and selected work](assets/2026-08-18-independent-practice/02-consulting-work.png)
3. [Notebook and resources](assets/2026-08-18-independent-practice/03-notebook-resources.png)
4. [About and contact](assets/2026-08-18-independent-practice/04-about-contact.png)

Implementation must match their hierarchy, spacing, palette, typography relationships, container model, and section rhythm. Concept imagery is reference material, not a raster replacement for code-native interface text or controls.

## Information Architecture

Primary navigation:

- Services
- Work
- Notebook
- Resources
- About

Routes:

- `/` — composed homepage
- `/notebook` — published note index
- `/notebook/<slug>` — note detail
- `/resources` — published resource index
- `/resources/<slug>` — resource detail when the resource has a Markdown page
- Existing `/about-me` redirect may continue to route to the homepage About section

Downloadable resources may link from a resource detail page or directly from the resource index when no narrative page is needed.

## Homepage Composition

### 01 — Opening

- Quiet single-line header using the full `Tera Earlywine` wordmark.
- Main statement: `Data systems people can trust—and teams can run.`
- Supporting copy: `I help data leaders improve the systems, practices, and decisions behind reliable analytics. I also publish the notes, tools, and experiments behind the work.`
- Equal primary paths: `Work with me` and `Explore the notebook`.
- Existing YouTube embed retained as featured media in a 16:9 frame.
- The video title is stored as site content rather than hard-coded inside the media component.

### 02 — Consulting and Selected Work

Three workstreams displayed as an open ruled band:

- Platform direction — clarify architecture, ownership, and investment choices.
- Hands-on delivery — turn a roadmap into reliable pipelines, models, and operating systems.
- Ways of working — improve reviews, incident response, documentation, and decision-making.

Selected work uses rows with a consistent `situation / contribution / outcome` structure. Initial copy must remain truthful, avoid invented metrics, and be editable separately from the template.

### 03 — Notebook and Resources

- One featured note with summary and optional editorial thumbnail.
- A compact index of recent notes.
- A horizontal resource shelf for guides, templates, and checklists.
- `View all notes` and `Browse resources` links lead to dedicated index pages.
- Homepage content is selected from Markdown metadata, not duplicated in templates.

### 04 — About and Contact

- Compact credibility statement rather than a full resume timeline.
- Selected experience may name Block, Mercari, Cowgirl AI, and independent consulting.
- Closing statement: `Bring me the problem that doesn't fit neatly in a ticket.`
- Equal contact actions: `Book a conversation` and `Email Tera`.
- Scheduling URL and email address live in centralized site configuration.
- Production requires a configured scheduling URL. When absent in local development, the booking action falls back to a pre-addressed email requesting a conversation, so the interface never contains a broken link.

## Content Architecture

Repository content directories:

```text
content/
  notes/
  resources/
  work/
```

Each item is Markdown with YAML front matter. The content model includes:

```yaml
title: Designing durable data operations
slug: designing-durable-data-operations
summary: A practical look at ownership, failure handling, and operational controls.
published_at: 2026-08-18
status: published
featured: true
kind: note
asset_path: null
external_url: null
```

Required fields:

- `title`
- `slug`
- `summary`
- `published_at`
- `status`
- `kind`

Optional fields:

- `featured`
- `asset_path`
- `external_url`
- `thumbnail`

Rules:

- `status` is `draft` or `published`.
- Drafts never appear in production routes or homepage queries.
- Slugs are unique within a collection and remain stable after publication.
- Dates use ISO `YYYY-MM-DD` format.
- A resource may define either Markdown body content, `asset_path`, or `external_url`.
- Local assets must resolve inside the repository's static asset boundary.
- At most one featured note is selected for the homepage; the newest featured note wins if content temporarily violates the rule, while validation reports the duplicate.

## Application Structure

The existing Flask application remains the runtime. New responsibilities are separated into focused units:

- Content model: normalized metadata and rendered Markdown body.
- Content loader: reads collections, validates front matter, renders Markdown, and sorts published items.
- Content repository: exposes queries such as featured note, recent notes, resources, and item-by-slug.
- Routes: homepage composition, indexes, and detail pages.
- Templates: shared site shell plus focused section, index-row, resource-item, and article-body partials.
- Site configuration: email, booking URL, featured video URL/title, social links, and production metadata.

The homepage route asks the content repository for the approved content groups and passes them to Jinja. Templates do not scan files or parse Markdown.

## Data Flow

1. The app initializes the content repository from the repository content directories.
2. The loader parses front matter, validates each item, and renders Markdown to sanitized HTML.
3. The repository filters drafts and provides sorted published collections.
4. Routes request only the data needed by each page.
5. Jinja renders code-native navigation, headings, links, controls, and article content.
6. Browser navigation follows stable routes; downloadable assets are served from approved static paths.

Content may be cached for the lifetime of a production process. Development mode reloads content after file changes so Markdown editing remains fast.

## Validation and Error Handling

- Content validation runs in automated tests and as a dedicated pre-deployment command.
- Missing required fields, invalid dates, duplicate slugs, unsafe asset paths, and unsupported statuses fail validation with a file-specific message.
- Invalid published content blocks deployment rather than disappearing silently.
- Unknown slugs return the styled 404 page.
- Missing configured thumbnails use the text-forward article layout; no placeholder box is shown.
- Missing scheduling configuration uses the documented email fallback in development and fails production validation.
- Markdown HTML is sanitized before rendering.
- External links use safe `rel` attributes and clear labeling.

## Responsive and Accessible Behavior

- Desktop layouts collapse into a single readable column without changing content order.
- Navigation becomes a keyboard-operable mobile menu.
- The two primary homepage paths retain equal visual weight on mobile.
- Tables or case-study rows reflow into labeled blocks rather than horizontal overflow.
- Video preserves a 16:9 ratio and uses an explicit accessible title.
- Focus states use the approved blue accent and remain visible against the near-white background.
- Heading order, landmarks, link text, and color contrast meet common accessibility expectations.
- Motion respects `prefers-reduced-motion`.

## Testing and Verification

Automated coverage:

- Front-matter parsing and required-field validation.
- Draft filtering and publication ordering.
- Duplicate slug, invalid date, and unsafe asset-path failures.
- Featured note and homepage collection selection.
- Homepage, index, detail, redirect, and 404 routes.
- Markdown sanitization.

Browser verification:

- Compare each implemented section against its corresponding approved concept.
- Verify desktop and mobile layouts.
- Exercise navigation, featured video, article links, resource links/downloads, mobile menu, scheduling action, and email action.
- Confirm keyboard focus and reduced-motion behavior.
- Confirm above-the-fold copy matches the approved copy exactly.

## Deployment

- Continue deploying the Flask application through the existing Python 3.12 Google App Engine configuration.
- Add only the dependencies required for Markdown parsing, YAML front matter, and sanitization.
- Validate content and run tests before deployment.
- Production configuration supplies the scheduling URL and other environment-specific values.
- Deployment and domain changes are outside the implementation step unless explicitly requested.

## Existing Worktree Protection

The repository begins this work with:

- A local commit not yet present on `origin/main` that updates the footer year.
- Uncommitted edits to the hero template and main stylesheet that add and style the YouTube embed.

Implementation must preserve the intent of those changes, avoid resetting the worktree, and make any overlapping edits deliberately.

## Out of Scope for the First Release

- Browser-based CMS or admin interface.
- Database-backed content.
- Newsletter subscription system.
- Search, comments, accounts, payments, or analytics dashboards.
- Automatic deployment or production DNS changes.
- Invented client metrics, testimonials, or company claims.

## Acceptance Criteria

- The approved four-part visual direction is faithfully implemented.
- Consulting and publishing are equally prominent.
- The current video remains featured and functional.
- Notes and resources render from validated Markdown.
- Dedicated notebook and resource routes work with stable slugs.
- Email and scheduling actions are functional and never point to placeholders.
- The site passes automated content/route tests and desktop/mobile browser verification.
- No existing user-authored changes are lost.
