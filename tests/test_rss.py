from xml.etree import ElementTree

from core.home.blog_content import ARTICLES
from test_analytics_reporting import collect_elements


SITE_URL = 'https://www.teraearlywine.com'


def test_feed_contains_all_articles_with_stable_canonical_links(app_factory):
    client = app_factory(SITE_URL=SITE_URL).test_client()
    response = client.get('/rss.xml', base_url='https://untrusted.example')
    assert response.status_code == 200
    assert response.mimetype == 'application/rss+xml'
    root = ElementTree.fromstring(response.data)
    assert root.tag == 'rss' and root.attrib['version'] == '2.0'
    channel = root.find('channel')
    assert channel.findtext('link') == f'{SITE_URL}/blog/'
    assert channel.findtext('title')
    assert channel.findtext('description')
    assert channel.find('{http://www.w3.org/2005/Atom}link').attrib == {
        'href': f'{SITE_URL}/rss.xml', 'rel': 'self',
        'type': 'application/rss+xml',
    }
    items = channel.findall('item')
    assert len(items) == len(ARTICLES)
    for item, article in zip(items, reversed(ARTICLES)):
        url = f"{SITE_URL}/blog/{article['slug']}/"
        assert item.findtext('title') == article['title']
        assert item.findtext('description') == article['dek']
        assert item.findtext('category') == article['category']
        assert item.findtext('link') == item.findtext('guid') == url
        assert item.find('guid').attrib == {'isPermaLink': 'true'}
        assert item.find('pubDate') is None
        assert client.get(url).status_code == 200
    assert len({item.findtext('guid') for item in items}) == len(items)


def test_feed_escapes_text_and_revalidates_when_content_changes(app_factory, monkeypatch):
    client = app_factory(SITE_URL=SITE_URL).test_client()
    original = client.get('/rss.xml')
    etag = original.headers['ETag']
    assert 'max-age=300' in original.headers['Cache-Control']
    assert client.get('/rss.xml', headers={'If-None-Match': etag}).status_code == 304
    monkeypatch.setitem(ARTICLES[-1], 'title', 'Data & AI <updates>')
    updated = client.get('/rss.xml', headers={'If-None-Match': etag})
    assert updated.status_code == 200
    assert updated.headers['ETag'] != etag
    assert ElementTree.fromstring(updated.data).findtext('channel/item/title') == 'Data & AI <updates>'


def test_feed_discovery_and_missing_configuration(app_factory):
    client = app_factory(SITE_URL=SITE_URL).test_client()
    for path in ('/', '/blog/', f"/blog/{ARTICLES[0]['slug']}/"):
        document = client.get(path).get_data(as_text=True)
        assert any(link.get('rel') == 'alternate' and
                   link.get('type') == 'application/rss+xml' and
                   link.get('href') == f'{SITE_URL}/rss.xml'
                   for link in collect_elements(document, 'link'))
    assert 'Subscribe via RSS' in client.get('/blog/').get_data(as_text=True)
    unconfigured = app_factory().test_client()
    assert unconfigured.get('/rss.xml').status_code == 503
    assert 'application/rss+xml' not in unconfigured.get('/blog/').get_data(as_text=True)


def test_production_feed_redirects_to_configured_origin(app_factory):
    app = app_factory(env='production', SITE_URL=SITE_URL)
    app.config.update(TESTING=False, DEBUG=False)
    client = app.test_client()
    response = client.get('/rss.xml', base_url='http://teraearlywine.com')
    assert response.status_code == 308
    assert response.headers['Location'] == f'{SITE_URL}/rss.xml'
    assert client.get(response.headers['Location']).status_code == 200
