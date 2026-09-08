import mimetypes


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
