# Glass-cube blog

The blog at `/blog/` uses the website's graphite, ivory, stone, and Inter visual language. Each article adds one point to the interactive sculpture. The first nine articles form a square, and 27 complete a 3 × 3 × 3 cube. Later articles extend the next outer shell while retaining the existing point coordinates.

## GTM-aligned collection

`core/home/blog_content.py` contains 27 articles written in third person for enterprise data and platform leaders, with financial services and fintech as the initial audience. The collection follows the Consulting GTM Strategy reviewed on September 10, 2026: lead with avoidable warehouse processing, then connect reliability, data foundations, production AI, and delivery ownership to the next investment decision.

The featured reading path contains three practical pieces: cloud bills versus carbon evidence, dashboard refresh frequency, and repeated processing before AI scales. Existing IDs, slugs, and article order remain stable, preserving published URLs and cube positions. Other articles retain their underlying topic while replacing personal reflections with a recognizable problem, an investigation, and a useful first step.

The index and each article include a relevant offer and a link to the existing contact section. The primary offer is the paid Data Waste & Efficiency Diagnostic; follow-on articles connect to the AI-Ready Data Foundation Blueprint, Production AI Lighthouse, or Data & AI Reliability Office. Copy describes scope and deliverables without inventing prices, available capacity, client results, affiliations, or guaranteed savings.

The refresh-frequency calculation is explicitly illustrative. Cost, resource use, and provider-reported emissions remain separate measurements. Environmental claims retain reporting boundaries and uncertainty; implementation and formal carbon assurance are separately scoped. Technical and measurement sections link to the Google Cloud and FinOps sources that support them. The internal strategy and acquisition operating details are not public article content.

The user approved generating and publishing this collection. The blog routes are public in production without enabling debug or testing. Blog appears before Expertise in the shared navigation. Every article is also available through the HTML article list, including when the interactive cube cannot run.

Canonical URLs follow the configured `SITE_URL`. The index uses Blog structured data, articles use BlogPosting structured data, and both include breadcrumbs. All article URLs are included in the public sitemap. Publication dates remain unset until they can be grounded in an actual release record. Unknown article URLs return an unindexed 404.

The older abandoned journal content and documentation are not used by these routes. This change does not create a content calendar or release schedule.

## Article contract

Each article has:

- `id`: a unique integer identifying the article.
- `slug`: a unique URL segment.
- `title`, `category`, and `dek`: plain-text display content.
- `read_minutes`: an estimated reading time.
- `sections`: a list of `{title, paragraphs, sources}` objects; `sources` contains optional reference links with `title` and `url`.
- `offer`: the relevant offer's `name`, `description`, and `cta`, selected from `OFFERS`.

Cube coordinates follow the order of `ARTICLES`. Append new entries to preserve existing points; do not prepend or reorder this list. `FEATURED_ARTICLES` selects entries 25, 4, and 2 independently of cube order and publication scheduling. The archive lists all remaining articles.

The index template receives `articles`, `featured_articles`, `diagnostic_offer`, and `cube_articles`. The latter is a JSON-safe list with `id`, `slug`, `title`, `category`, `dek`, `read_minutes`, and a server-generated `url`, rendered through Jinja's `tojson` filter. `BLOG_DESCRIPTION` keeps the index metadata and structured-data description consistent.

The article template receives `article`, `next_article`, and `articles`. Both routes pass `is_blog=True` so shared templates load the blog styles and identify the current navigation item.

## RSS subscriptions

`/rss.xml` publishes an RSS 2.0 feed from the same article collection, with titles, summaries, categories, and canonical article links. Appended articles appear first without changing cube order. Article URLs serve as stable GUIDs, so edits do not create new subscriptions entries. Publication dates are omitted until actual release dates are recorded. The shared page header advertises the feed to readers, and the blog introduction includes a visible subscription link.

The visible subscription link opens `/blog/subscribe/`, a styled HTML page explaining how to add the feed to a reader. It offers the canonical address in a selectable field and a copy button that confirms a successful copy or selects the address for manual copying if clipboard access is unavailable. The field and instructions work without JavaScript. A separate, explicitly labeled link opens the raw XML. The shared discovery link still points directly to `/rss.xml` for feed readers.

The feed requires `SITE_URL`; without it the endpoint returns 503, the subscription page explains that subscriptions are temporarily unavailable, and the blog's subscription link is hidden. Feed responses support ETag revalidation and a five-minute public cache. New posts enter the feed when the updated website is deployed.

## Verification

Production-mode tests exercise the index and all 27 article URLs with debug and testing explicitly disabled. They also check article content, canonical URLs, structured data, sitemap coverage, navigation order, missing-site-configuration behavior, and unknown-article 404s. Publishing still requires a separate live deployment and native readback; local tests alone do not establish that the site is live.
