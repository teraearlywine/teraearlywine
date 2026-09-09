import json
import re
from contextlib import contextmanager
from html import unescape
from xml.etree import ElementTree

import pytest
from flask import template_rendered

from core.home.blog_content import ARTICLES
from core.home.services import SERVICES
from test_analytics_reporting import collect_elements


SITE_URL = 'https://www.teraearlywine.com'


@contextmanager
def captured_templates(app):
    rendered = []

    def record(sender, template, context, **extra):
        rendered.append((template.name, context))

    template_rendered.connect(record, app)
    try:
        yield rendered
    finally:
        template_rendered.disconnect(record, app)


def structured_graph(document):
    payload = re.search(
        r'<script type="application/ld\+json">(.*?)</script>', document, re.S,
    )
    assert payload is not None
    return json.loads(payload.group(1))['@graph']


def test_blog_cube_has_distinct_destinations_and_safe_data(app_factory):
    app = app_factory()
    with captured_templates(app) as rendered:
        response = app.test_client().get('/blog/')
    assert response.status_code == 200
    name, context = rendered[-1]
    assert name == 'home/blog_index.html'
    assert context['is_blog'] is True
    cube_articles = context['cube_articles']
    assert len(cube_articles) == 27
    assert len({article['id'] for article in cube_articles}) == 27
    assert len({article['url'] for article in cube_articles}) == 27
    assert len({article['title'] for article in cube_articles}) == 27
    assert json.loads(json.dumps(cube_articles)) == cube_articles
    assert all(article['url'] == f"/blog/{article['slug']}/" for article in cube_articles)


@pytest.mark.parametrize('article', ARTICLES, ids=lambda article: article['slug'])
def test_each_cube_destination_renders_its_article_and_metadata(app_factory, article):
    app = app_factory(env='production', SITE_URL=SITE_URL)
    app.config.update(TESTING=False, DEBUG=False)
    with captured_templates(app) as rendered:
        response = app.test_client().get(f"/blog/{article['slug']}/?utm_source=test")
    assert response.status_code == 200
    name, context = rendered[-1]
    assert name == 'home/blog_article.html'
    assert context['article'] == article
    assert context['next_article']['slug'] != article['slug']
    raw_document = response.get_data(as_text=True)
    document = unescape(raw_document)
    assert article['title'] in document
    for section in article['sections']:
        for paragraph in section['paragraphs']:
            assert paragraph in document
    assert len(collect_elements(document, 'h1')) == 1
    canonical = f"{SITE_URL}/blog/{article['slug']}/"
    assert {'rel': 'canonical', 'href': canonical} in collect_elements(document, 'link')
    metas = collect_elements(document, 'meta')
    assert not any(meta.get('name') == 'robots' and 'noindex' in meta.get('content', '') for meta in metas)
    assert next(meta for meta in metas if meta.get('name') == 'description')['content'] == article['dek']
    assert next(meta for meta in metas if meta.get('property') == 'og:url')['content'] == canonical
    assert next(meta for meta in metas if meta.get('property') == 'og:type')['content'] == 'article'
    graph = structured_graph(raw_document)
    posting = next(item for item in graph if item['@type'] == 'BlogPosting')
    assert posting['url'] == posting['mainEntityOfPage'] == canonical
    assert posting['headline'] == article['title']
    assert posting['description'] == article['dek']
    assert posting['articleSection'] == article['category']
    assert posting['author']['name'] == 'Tera Earlywine'
    assert posting['wordCount'] == sum(len(paragraph.split()) for section in article['sections'] for paragraph in section['paragraphs'])
    breadcrumbs = next(item for item in graph if item['@type'] == 'BreadcrumbList')
    assert breadcrumbs['itemListElement'][-1]['item'] == canonical
    assert 'Illustrative preview' not in document
    assert 'sample notes' not in document
    assert 'datePublished' not in posting  # Dates are added from actual release records.


def test_blog_index_is_indexable_and_describes_all_articles(app_factory):
    document = app_factory(SITE_URL=SITE_URL).test_client().get('/blog/').get_data(as_text=True)
    metas = collect_elements(document, 'meta')
    assert not any(meta.get('name') == 'robots' and 'noindex' in meta.get('content', '') for meta in metas)
    assert {'rel': 'canonical', 'href': f'{SITE_URL}/blog/'} in collect_elements(document, 'link')
    assert next(meta for meta in metas if meta.get('property') == 'og:type')['content'] == 'website'
    blog = next(item for item in structured_graph(document) if item['@type'] == 'Blog')
    assert blog['url'] == f'{SITE_URL}/blog/'
    expected_urls = {f"{SITE_URL}/blog/{article['slug']}/" for article in ARTICLES}
    assert {article['url'] for article in blog['blogPost']} == expected_urls
    assert len(blog['blogPost']) == len(ARTICLES)
    assert 'illustrative writing' not in document
    assert 'sample notes' not in document


@pytest.mark.parametrize('path', ['/blog/'] + [f"/blog/{article['slug']}/" for article in ARTICLES])
def test_production_publishes_blog_without_debug_or_testing(app_factory, path):
    app = app_factory(env='production', SITE_URL=SITE_URL)
    app.config.update(TESTING=False, DEBUG=False)
    assert app.test_client().get(path).status_code == 200


def test_production_navigation_places_blog_before_expertise(app_factory):
    app = app_factory(env='production')
    app.config.update(TESTING=False, DEBUG=False)
    document = app.test_client().get('/').get_data(as_text=True)
    links = collect_elements(document, 'a')
    destinations = [link.get('href') for link in links]
    assert destinations.index('/blog/') < destinations.index('#services')
    assert 'css/blog.css' not in document
    assert 'js/blog.js' not in document


def test_unknown_article_and_abandoned_journal_are_unindexed_404s(app_factory):
    client = app_factory(SITE_URL=SITE_URL).test_client()
    for path in ('/blog/unknown/', '/journal/', '/journal/small-systems-clear-ownership/'):
        response = client.get(path)
        assert response.status_code == 404
        document = response.get_data(as_text=True)
        assert 'noindex, nofollow' in document
        assert 'rel="canonical"' not in document
        assert 'application/ld+json' not in document


def test_public_sitemap_includes_every_blog_article(app_factory):
    client = app_factory(SITE_URL=SITE_URL).test_client()
    root = ElementTree.fromstring(client.get('/sitemap.xml').data)
    locations = [loc.text for loc in root.findall('.//{*}loc')]
    assert len(locations) == len(set(locations))
    assert set(locations) == {
        f'{SITE_URL}/',
        *[f'{SITE_URL}/services/{slug}' for slug in SERVICES],
        f'{SITE_URL}/blog/',
        *[f"{SITE_URL}/blog/{article['slug']}/" for article in ARTICLES],
    }


@pytest.mark.parametrize('path', ['/blog/', f"/blog/{ARTICLES[0]['slug']}/"])
def test_blog_without_site_url_omits_canonical_and_schema(app_factory, path):
    response = app_factory().test_client().get(path)
    assert response.status_code == 200
    document = response.get_data(as_text=True)
    assert 'rel="canonical"' not in document
    assert 'application/ld+json' not in document


@pytest.mark.parametrize('path', ['/blog/', f"/blog/{ARTICLES[0]['slug']}/"])
def test_blog_public_origin_redirect_preserves_article_path(app_factory, path):
    app = app_factory(env='production', SITE_URL=SITE_URL)
    app.config.update(TESTING=False, DEBUG=False)
    response = app.test_client().get(path, base_url='http://teraearlywine.com')
    assert response.status_code == 308
    assert response.headers['Location'] == f'{SITE_URL}{path}'
    assert app.test_client().get(response.headers['Location']).status_code == 200
