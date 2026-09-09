import json
import re
from xml.etree import ElementTree

import pytest

from core.home.blog_content import ARTICLES
from core.home.services import SERVICES
from test_analytics_reporting import ALLOWED_VALUES, EVENT_PARAMETERS, collect_elements


@pytest.mark.parametrize('origin', [
    'http://teraearlywine.com',
    'http://www.teraearlywine.com',
    'https://teraearlywine.com',
])
@pytest.mark.parametrize('path', [
    '/', '/robots.txt', '/sitemap.xml',
    '/services/data-migration-rescue?utm_source=search&next=%2Fcontact',
])
def test_public_variants_permanently_redirect_in_one_hop(app_factory, origin, path):
    client = app_factory(env='production', SITE_URL='https://www.teraearlywine.com').test_client()
    response = client.get(path, base_url=origin)
    assert response.status_code == 308
    assert response.headers['Location'] == f'https://www.teraearlywine.com{path}'
    assert client.get(response.headers['Location']).status_code == 200


def test_redirect_preserves_contact_method_and_body_without_delivery(app_factory):
    app = app_factory(env='production', SITE_URL='https://www.teraearlywine.com')
    # A temporary probe proves 308 replay semantics without sending a real lead.
    from flask import request

    @app.post('/method-probe')
    def method_probe():
        return {'method': request.method, 'body': request.get_data(as_text=True)}

    response = app.test_client().post(
        '/method-probe', base_url='http://www.teraearlywine.com',
        data='opaque-test-payload', follow_redirects=True,
    )
    assert response.json == {'method': 'POST', 'body': 'opaque-test-payload'}
    assert response.history[0].status_code == 308


@pytest.mark.parametrize('env,origin', [
    ('development', 'http://www.teraearlywine.com'),
    ('production', 'http://localhost'),
    ('production', 'http://127.0.0.1:5001'),
    ('production', 'https://preview.example.appspot.com'),
    ('production', 'https://www.teraearlywine.com'),
])
def test_canonical_and_preview_origins_remain_accessible(app_factory, env, origin):
    client = app_factory(env=env, SITE_URL='https://www.teraearlywine.com').test_client()
    assert client.get('/', base_url=origin).status_code == 200


@pytest.mark.parametrize('app_engine,forwarded_scheme,status', [
    (True, 'https', 200),
    (True, 'http', 308),
    (False, 'https', 308),
])
def test_only_app_engine_frontend_scheme_is_trusted(
    app_factory, monkeypatch, app_engine, forwarded_scheme, status,
):
    if app_engine:
        monkeypatch.setenv('GAE_ENV', 'standard')
    else:
        monkeypatch.delenv('GAE_ENV', raising=False)
    client = app_factory(env='production', SITE_URL='https://www.teraearlywine.com').test_client()
    response = client.get('/', base_url='http://www.teraearlywine.com', headers={
        'X-Forwarded-Proto': forwarded_scheme,
        'X-Forwarded-Host': 'attacker.example',
    })
    assert response.status_code == status
    if status == 308:
        assert response.headers['Location'] == 'https://www.teraearlywine.com/'


def test_redirect_safely_encodes_path_and_preserves_query(app_factory):
    client = app_factory(env='production', SITE_URL='https://www.teraearlywine.com').test_client()
    response = client.get('/a%20b/%C3%A9?next=https%3A%2F%2Fother.example',
                          base_url='http://teraearlywine.com')
    assert response.headers['Location'] == (
        'https://www.teraearlywine.com/a%20b/%C3%A9?next=https%3A%2F%2Fother.example'
    )


@pytest.mark.parametrize('slug', SERVICES)
def test_service_pages_have_unique_metadata_content_and_conversion_path(app_factory, slug):
    client = app_factory(SITE_URL='https://www.teraearlywine.com',
                         BOOKING_URL='https://calendar.example/book',
                         GOOGLE_ANALYTICS_MEASUREMENT_ID='G-TEST').test_client()
    response = client.get(f'/services/{slug}?utm_source=test')
    assert response.status_code == 200
    document = response.get_data(as_text=True)
    service = SERVICES[slug]
    canonical = f'https://www.teraearlywine.com/services/{slug}'
    assert len(collect_elements(document, 'h1')) == 1
    assert len(collect_elements(document, 'title')) == 1
    assert service['name'] in document
    assert service['title'] in document
    assert service['problem'] in document
    assert {'rel': 'canonical', 'href': canonical} in collect_elements(document, 'link')
    metas = collect_elements(document, 'meta')
    assert next(m for m in metas if m.get('property') == 'og:url')['content'] == canonical
    assert next(m for m in metas if m.get('name') == 'description')['content'] == service['description']
    image = next(m for m in metas if m.get('property') == 'og:image')['content']
    assert image.startswith('https://www.teraearlywine.com/static/assets/images/')
    assert next(m for m in metas if m.get('name') == 'twitter:image')['content'] == image
    assert next(m for m in metas if m.get('name') == 'twitter:card')['content'] == 'summary_large_image'
    assert not any(m.get('name') == 'robots' and 'noindex' in m.get('content', '') for m in metas)
    links = collect_elements(document, 'a')
    assert any(a.get('href') == '/#contact' for a in links)
    assert any(a.get('href') == 'https://calendar.example/book' for a in links)
    assert all(a['href'].startswith('/#') for a in links if a.get('data-placement') == 'navigation' and a.get('data-destination-type') == 'section')
    assert 'assets/js/analytics.js' in document
    assert 'googletagmanager.com' not in document
    for link in links:
        event = link.get('data-analytics-event')
        if event:
            for parameter in EVENT_PARAMETERS[event]:
                assert link[f"data-{parameter.replace('_', '-')}"] in ALLOWED_VALUES[parameter]
    graph = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', document, re.S).group(1))['@graph']
    schema_service = next(n for n in graph if n['@type'] == 'Service')
    assert schema_service['url'] == canonical
    assert schema_service['name'] == service['name']
    breadcrumb = next(n for n in graph if n['@type'] == 'BreadcrumbList')
    assert breadcrumb['itemListElement'][-1]['item'] == canonical
    assert len({s['title'] for s in SERVICES.values()}) == len(SERVICES)
    assert len({s['description'] for s in SERVICES.values()}) == len(SERVICES)


def test_sitemap_and_internal_links_cover_all_service_pages(app_factory):
    client = app_factory(SITE_URL='https://www.teraearlywine.com').test_client()
    paths = {f'/services/{slug}' for slug in SERVICES}
    root = ElementTree.fromstring(client.get('/sitemap.xml').data)
    blog_paths = {'/blog/'} | {f"/blog/{article['slug']}/" for article in ARTICLES}
    assert {loc.text for loc in root.findall('.//{*}loc')} == {
        f'https://www.teraearlywine.com{path}' for path in paths | {'/'} | blog_paths
    }
    for path in paths | {'/'}:
        document = client.get(path).get_data(as_text=True)
        links = {a.get('href') for a in collect_elements(document, 'a')}
        assert paths - {path} <= links
        for target in paths - {path}:
            assert client.get(target).status_code == 200


def test_unknown_service_is_a_true_noindex_404(app_factory):
    response = app_factory(SITE_URL='https://www.teraearlywine.com').test_client().get('/services/unknown')
    assert response.status_code == 404
    document = response.get_data(as_text=True)
    assert 'noindex, nofollow' in document
    assert 'rel="canonical"' not in document


def test_service_without_site_configuration_omits_canonical_and_schema(app_factory):
    document = app_factory().test_client().get('/services/data-migration-rescue').get_data(as_text=True)
    assert 'rel="canonical"' not in document
    assert 'application/ld+json' not in document


def test_old_about_url_has_a_permanent_redirect(app_factory):
    response = app_factory().test_client().get('/about-me')
    assert response.status_code == 301
    assert response.headers['Location'] == '/#experience'
