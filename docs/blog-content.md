# Writing and the paper-stack explorer

The Writing index at `/blog/` renders one ultramarine paper sheet per essay. The newest essay is selected first. Moving the mouse onto the stack turns one sheet older. The selected essay stays in place while the pointer moves to its link. Older and Newer give keyboard and touch visitors the same controls. Each selection updates the orange edge, title, category, reading time, summary and article link. The featured links and complete newest-first archive also work without JavaScript.

Each essay ends with the 3.3-second “Nothing Wasted” sign-off before its related offer. The final still is the default. The muted video loads when that signature enters view, plays once, and returns to its still frame. Reduced motion and unavailable playback use the same still.

## GTM-aligned collection

`core/home/blog_content.py` contains the published articles for enterprise data and platform leaders, with financial services and fintech as the initial audience. The collection follows the Consulting GTM Strategy reviewed on September 10, 2026: lead with avoidable warehouse processing, then connect reliability, data foundations, production AI, and delivery ownership to the next investment decision.

The featured reading path includes “Nothing Wasted,” cloud bills versus carbon evidence, and dashboard refresh frequency. Existing IDs, slugs, and article order remain stable, preserving published URLs and publication order. Other articles retain their underlying topic while replacing personal reflections with a recognizable problem, an investigation, and a useful first step.

The index and each article include a relevant offer and a link to the existing contact section. The primary offer is the paid Data Waste & Efficiency Diagnostic; follow-on articles connect to the AI-Ready Data Foundation Blueprint, Production AI Lighthouse, or Data & AI Reliability Office. Copy describes scope and deliverables without inventing prices, available capacity, client results, affiliations, or guaranteed savings.

The refresh-frequency calculation is explicitly illustrative. Cost, resource use, and provider-reported emissions remain separate measurements. Environmental claims retain reporting boundaries and uncertainty; implementation and formal carbon assurance are separately scoped. Technical and measurement sections link to the Google Cloud and FinOps sources that support them. The internal strategy and acquisition operating details are not public article content.

The user approved generating and publishing this collection. The blog routes are public in production without enabling debug or testing. The shared navigation calls the collection Writing.

Canonical URLs follow the configured `SITE_URL`. The index uses Blog structured data, articles use BlogPosting structured data, and both include breadcrumbs. All article URLs are included in the public sitemap. Publication dates remain unset until they can be grounded in an actual release record. Unknown article URLs return an unindexed 404.

The older abandoned journal content and documentation are not used by these routes. This change does not create a content calendar or release schedule.

The original collection uses third person. At Tera's request, article 28, `pomodoro-for-ai-agents`, uses a casual first-person voice to develop her timer-and-agent tweet into a practical launch, focus, and review rhythm. It retains its place after the original 27 articles.

## Article contract

Article 29, `sql-techniques-and-the-bottom-line`, was prepared on September 22, 2026. It connects SQL techniques to billing models, maintenance costs, payback, and operating profit, using linked provider documentation and explicitly hypothetical financial examples. It appends to the existing collection; preparation does not establish a live publication date.

Published September 22, 2026 after explicit approval. Source commit `59733b21` deployed as App Engine version `sql-20260922-59733b21` in project `teraearlywine`, service `default`. Native service readback confirmed 100% traffic on the new version. The public article, full text and source links, blog listing, newest RSS entry (29 total), sitemap, homepage, and 14 article assets passed live checks. The local regression suite passed 176 tests; 17 broker/emulator tests were skipped because that integration environment was not requested.

The normal CLI upload could not replace aging objects in the staging bucket because the deployer lacks `storage.objects.delete`. The release used the App Engine Admin API with fresh objects under `releases/sql-20260922-59733b21/` in the existing staging bucket, preserving runtime configuration and permissions. Application sources were compared with the prior production manifest: only `core/home/blog_content.py` changed. Local test-cache files were excluded and the source revision metadata was refreshed. The previous production version, `blog-align-20260920`, remains available for rollback.

Each article has:

- `id`: a unique integer identifying the article.
- `slug`: a unique URL segment.
- `title`, `category`, and `dek`: plain-text display content.
- `read_minutes`: an estimated reading time.
- `sections`: a list of `{title, paragraphs, sources}` objects; `sources` contains optional reference links with `title` and `url`.
- `offer`: the relevant offer's `name`, `description`, and `cta`, selected from `OFFERS`.

Append new entries to `ARTICLES` so publication order and RSS identities remain stable. `FEATURED_ARTICLES` is independent of the stack and the archive.

The index receives `articles`, `featured_articles`, `diagnostic_offer`, and `stack_articles`. The last holds the ID, slug, title, category, summary, reading time, and server-generated URL for each sheet. The JSON goes through Jinja’s `tojson` filter. Article pages still receive their article and next article.

## RSS subscriptions

`/rss.xml` publishes an RSS 2.0 feed from the same article collection, with titles, summaries, categories, and canonical article links. Appended articles appear first in the feed. Article URLs serve as stable GUIDs, so edits do not create new subscription entries. Publication dates are omitted until actual release dates are recorded. The shared page header advertises the feed to readers, and the blog introduction includes a visible subscription link.

The visible subscription link opens `/blog/subscribe/`, a styled HTML page explaining how to add the feed to a reader. It offers the canonical address in a selectable field and a copy button that confirms a successful copy or selects the address for manual copying if clipboard access is unavailable. The field and instructions work without JavaScript. A separate, explicitly labeled link opens the raw XML. The shared discovery link still points directly to `/rss.xml` for feed readers.

The feed requires `SITE_URL`; without it the endpoint returns 503, the subscription page explains that subscriptions are temporarily unavailable, and the blog's subscription link is hidden. Feed responses support ETag revalidation and a five-minute public cache. New posts enter the feed when the updated website is deployed.

## Verification

Production-mode tests exercise the index and all article URLs with debug and testing explicitly disabled. They also check article content, canonical URLs, structured data, sitemap coverage, navigation order, missing-site-configuration behavior, and unknown-article 404s. Publishing still requires a separate live deployment and native readback; local tests alone do not establish that the site is live.
