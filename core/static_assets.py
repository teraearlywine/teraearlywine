"""Content-versioned URLs and caching for public static assets."""

import hashlib
from functools import lru_cache
from pathlib import Path

from flask import request
from werkzeug.security import safe_join


@lru_cache(maxsize=256)
def _digest(path, modified_ns, size):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:12]


def register_static_assets(app):
    def asset_version(endpoint, filename):
        if endpoint == 'static':
            folder = app.static_folder
        elif endpoint == 'index.static':
            folder = app.blueprints['index'].static_folder
        else:
            return None
        path = safe_join(folder, filename)
        if not path:
            return None
        try:
            stat = Path(path).stat()
            return _digest(path, stat.st_mtime_ns, stat.st_size)
        except (OSError, ValueError):
            return None

    @app.url_defaults
    def version_static_url(endpoint, values):
        filename = values.get('filename')
        if filename:
            version = asset_version(endpoint, filename)
            if version and f'.{version}.' not in filename:
                values.setdefault('v', version)

    @app.after_request
    def cache_versioned_asset(response):
        if request.endpoint not in {'static', 'index.static'}:
            return response
        filename = (request.view_args or {}).get('filename', '')
        version = asset_version(request.endpoint, filename)
        # CSS references fonts by content-hashed filename, without a query.
        fingerprinted = version and f'.{version}.' in filename
        if response.status_code in {200, 304} and version and (
            request.args.get('v') == version or fingerprinted
        ):
            response.cache_control.no_cache = False
            response.cache_control.public = True
            response.cache_control.max_age = 31536000
            response.cache_control.immutable = True
            response.expires = None
        return response
