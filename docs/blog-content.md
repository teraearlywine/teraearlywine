# Glass-cube blog

The blog at `/blog/` uses the website's graphite, ivory, stone, and Inter visual language. Each article adds one point to the interactive sculpture. The first nine articles form a square, and 27 complete a 3 × 3 × 3 cube. Later articles extend the next outer shell while retaining the existing point coordinates.

## First collection

`core/home/blog_content.py` contains 27 original essays and notes about systems, AI and work, and the human side of building. They use Tera's first-person voice to express design principles and working practices, without invented client anecdotes or outcome claims. The first three entries offer a longer reading experience; the other notes explore distinct ideas.

The user approved generating and publishing this collection. The blog routes are public in production without enabling debug or testing. Blog appears before Expertise in the shared navigation. Every article is also available through the HTML article list, including when the interactive cube cannot run.

Canonical URLs follow the configured `SITE_URL`. The index uses Blog structured data, articles use BlogPosting structured data, and both include breadcrumbs. All article URLs are included in the public sitemap. Publication dates remain unset until they can be grounded in an actual release record. Unknown article URLs return an unindexed 404.

The older abandoned journal content and documentation are not used by these routes. This change does not create a content calendar or release schedule.

## Article contract

Each article has:

- `id`: a unique integer identifying the article.
- `slug`: a unique URL segment.
- `title`, `category`, and `dek`: plain-text display content.
- `read_minutes`: an estimated reading time.
- `sections`: a list of `{title, paragraphs}` objects.

Cube coordinates follow the order of `ARTICLES`. Append new entries to preserve existing points; do not prepend or reorder this list. The two featured writing rows are currently an editorial selection of entries 2 and 3, independent of future publication scheduling.

The index template receives `articles` and `cube_articles`. The latter is a JSON-safe list with `id`, `slug`, `title`, `category`, `dek`, `read_minutes`, and a server-generated `url`, rendered through Jinja's `tojson` filter.

The article template receives `article`, `next_article`, and `articles`. Both routes pass `is_blog=True` so shared templates load the blog styles and identify the current navigation item.

## Verification

Production-mode tests exercise the index and all 27 article URLs with debug and testing explicitly disabled. They also check article content, canonical URLs, structured data, sitemap coverage, navigation order, missing-site-configuration behavior, and unknown-article 404s. Publishing still requires a separate live deployment and native readback; local tests alone do not establish that the site is live.
