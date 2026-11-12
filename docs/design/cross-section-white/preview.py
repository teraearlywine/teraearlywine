"""Run the Mac review site from the repository root with PYTHONPATH=."""

import os
import secrets

from core import create_app


if __name__ == '__main__':
    os.environ.update(
        SECRET_KEY=secrets.token_hex(32),
        CONTACT_BROKER_SECRET='contact-broker-test-secret',
        BOOKING_URL='https://calendar.app.google/iPH6W8fgvcCws9VA8',
        GOOGLE_ANALYTICS_MEASUREMENT_ID='G-PREVIEW0000',
    )
    app = create_app('development')
    app.config.update(
        DEBUG=False,
        TEMPLATES_AUTO_RELOAD=True,
        SITE_URL='http://127.0.0.1:5413',
        CONTACT_BROKER_URL='http://127.0.0.1:8787/contact-deliveries',
    )

    @app.after_request
    def local_review_headers(response):
        response.headers['X-Robots-Tag'] = 'noindex, nofollow'
        response.headers['Content-Security-Policy'] = (
            "script-src 'self' 'unsafe-inline'; connect-src 'self'; object-src 'none'"
        )
        return response

    app.run(host='127.0.0.1', port=5413, use_reloader=True, use_debugger=False)
