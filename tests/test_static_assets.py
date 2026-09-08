import mimetypes
import re
from urllib.parse import urlsplit

from test_analytics_reporting import collect_elements


def test_webp_assets_have_image_content_type_without_system_support(
    app_factory, monkeypatch,
):
    # Reproduce the generic content type observed in App Engine's runtime.
    mimetypes.init()
    monkeypatch.setitem(
        mimetypes.types_map, '.webp', 'application/octet-stream',
    )
    client = app_factory().test_client()

    for width in (768, 1536, 2304, 3072):
        response = client.get(
            f'/static/assets/images/hero-glass-retina-{width}.webp',
        )
        assert response.status_code == 200
        assert response.mimetype == 'image/webp'
        assert response.data[:4] == b'RIFF'
        assert response.data[8:12] == b'WEBP'


def test_public_asset_urls_are_versioned_and_cacheable(app_factory):
    client = app_factory().test_client()
    document = client.get('/').get_data(as_text=True)
    links = collect_elements(document, 'link')
    assets = [link for link in links if link.get('rel') in {'stylesheet', 'preload', 'icon'}]
    assert assets
    for asset in assets:
        url = asset['href']
        assert re.search(r'(\?v=[a-f0-9]{12}$|\.[a-f0-9]{12}\.woff2$)', url)
        response = client.get(url)
        assert response.status_code == 200
        assert response.cache_control.public
        assert response.cache_control.immutable
        assert response.cache_control.max_age == 31536000
        assert not response.cache_control.no_cache
        if asset.get('as') == 'font':
            assert asset['type'] == 'font/woff2'
            assert response.data[:4] == b'wOF2'
            # Relative CSS font references use a content-hashed filename.
            font = client.get(urlsplit(url).path)
            assert font.cache_control.immutable
            assert len(font.data) < 120000


def test_unversioned_and_wrong_version_assets_require_revalidation(app_factory):
    client = app_factory().test_client()
    for path in ('/static/assets/css/consultancy.css',
                 '/static/assets/css/consultancy.css?v=incorrect'):
        response = client.get(path)
        assert response.status_code == 200
        assert not response.cache_control.immutable
        assert response.cache_control.no_cache


def test_asset_url_changes_when_contents_change(app_factory, tmp_path):
    from flask import url_for

    app = app_factory()
    app.blueprints['index'].static_folder = str(tmp_path)
    asset = tmp_path / 'test.css'
    asset.write_text('body { color: red; }')
    with app.test_request_context():
        first = url_for('index.static', filename='test.css')
        asset.write_text('body { color: blue; }')
        second = url_for('index.static', filename='test.css')
    assert first != second
    client = app.test_client()
    assert not client.get(first).cache_control.immutable
    assert client.get(second).cache_control.immutable


def test_page_and_error_responses_never_get_immutable_cache(app_factory):
    client = app_factory().test_client()
    for path in ('/', '/services/data-migration-rescue', '/static/assets/missing.css?v=123'):
        assert not client.get(path).cache_control.immutable
