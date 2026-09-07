import json
import re
import shutil
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree

import pytest


PROJECT_ROOT = Path(__file__).parents[1]
ANALYTICS_JS = PROJECT_ROOT / 'core/home/assets/js/analytics.js'
ANALYTICS_BEHAVIOR_TEST = PROJECT_ROOT / 'tests/analytics_behavior.test.js'
MAIN_CSS = PROJECT_ROOT / 'core/home/assets/css/main.css'
MEASUREMENT_PLAN = PROJECT_ROOT / 'docs/analytics/ga4-measurement-plan.md'

EVENT_PARAMETERS = {
    'navigation_click': ('placement', 'destination_type'),
    'outbound_click': ('placement', 'destination_type'),
    'contact_submit': (),
    'contact_click': ('contact_method', 'placement', 'destination_type'),
}
ALLOWED_VALUES = {
    'contact_method': {'email', 'booking'},
    'placement': {'navigation', 'hero', 'projects', 'contact', 'footer', 'error'},
    'destination_type': {
        'section',
        'github',
        'linkedin',
        'youtube',
        'idea_factory',
        'email',
        'booking',
        'home',
    },
}


class ElementCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = []

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)


def collect_elements(document, tag):
    parser = ElementCollector()
    parser.feed(document)
    return [attributes for element_tag, attributes in parser.elements if element_tag == tag]


def render_home(app):
    response = app.test_client().get('/')
    assert response.status_code == 200
    return response.get_data(as_text=True)


def test_ga_disabled_omits_all_analytics_ui_and_scripts(app_factory):
    document = render_home(app_factory())

    assert 'googletagmanager.com' not in document
    assert 'window.gtag' not in document
    assert 'assets/js/analytics.js' not in document
    assert 'id="analyticsConsent"' not in document
    assert 'data-consent-reopen' not in document


def test_ga_enabled_renders_basic_consent_controls_without_loading_google(
    app_factory,
):
    document = render_home(
        app_factory(
            GOOGLE_ANALYTICS_DEBUG='true',
            GOOGLE_ANALYTICS_MEASUREMENT_ID='G-PORTFOLIO1',
        )
    )

    assert 'id="analyticsConfig"' in document
    assert '"measurementId": "G-PORTFOLIO1"' in document
    assert '"debugMode": true' in document
    assert 'googletagmanager.com' not in document
    assert 'window.gtag' not in document
    assert 'id="analyticsConsent"' in document
    assert 'data-consent-choice="accepted"' in document
    assert 'data-consent-choice="rejected"' in document
    assert 'data-consent-reopen' in document
    assert 'assets/js/analytics.js' in document


def test_public_configuration_is_escaped_in_html_and_inline_json(app_factory):
    measurement_id = 'G-TEST"</script><script>alert(1)</script>'
    verification = 'token"><script>alert(2)</script>'
    document = render_home(
        app_factory(
            GOOGLE_ANALYTICS_MEASUREMENT_ID=measurement_id,
            SEARCH_CONSOLE_VERIFICATION=verification,
            SITE_URL='https://portfolio.example',
        )
    )

    assert '<script>alert(1)</script>' not in document
    assert '<script>alert(2)</script>' not in document
    assert '\\u003c/script\\u003e\\u003cscript\\u003e' in document

    verification_meta = next(
        meta
        for meta in collect_elements(document, 'meta')
        if meta.get('name') == 'google-site-verification'
    )
    assert verification_meta['content'] == verification

    match = re.search(
        r'<script id="analyticsConfig" type="application/json">\s*'
        r'(.*?)\s*</script>',
        document,
        re.DOTALL,
    )
    assert match
    assert json.loads(match.group(1))['measurementId'] == measurement_id


@pytest.mark.parametrize(
    ('configuration', 'has_booking_fallback'),
    [
        ({}, False),
        ({'CONTACT_EMAIL': 'hello@example.test'}, False),
        ({'BOOKING_URL': 'https://calendar.example/book'}, True),
        (
            {
                'CONTACT_EMAIL': 'hello@example.test',
                'BOOKING_URL': 'https://calendar.example/book',
            },
            True,
        ),
    ],
)
def test_contact_form_replaces_email_cta_and_keeps_configured_booking_fallback(
    app_factory,
    configuration,
    has_booking_fallback,
):
    document = render_home(app_factory(**configuration))
    links = collect_elements(document, 'a')
    contact_ctas = [
        link
        for link in links
        if 'contact-cta' in link.get('class', '').split()
    ]

    assert 'data-contact-form' in document
    assert 'mailto:' not in document
    assert {link['data-contact-method'] for link in contact_ctas} == (
        {'booking'} if has_booking_fallback else set()
    )
    for link in contact_ctas:
        assert link['href'] == 'https://calendar.example/book'
        assert link['data-analytics-event'] == 'contact_click'
        assert link['data-placement'] == 'contact'
        assert link['data-destination-type'] == 'booking'
    if has_booking_fallback:
        assert document.count('>Book a fit call</a>') >= 2


def test_homepage_answers_enterprise_buyer_questions_and_leads_to_fit_call(
    app_factory,
):
    document = render_home(
        app_factory(BOOKING_URL='https://calendar.example/book')
    )

    assert (
        'I fix the data systems your reporting, compliance, and AI depend on.'
        in document
    )
    assert (
        'I work with leaders in regulated and critical operations'
        in document
    )
    assert 'Value / Risk Diagnostic' in document
    assert 'Data Foundation Blueprint' in document
    assert 'Production AI Lighthouse' in document
    assert 'Modernize<br>your data.' in document
    assert '9+ years' in document
    assert '500+' in document
    assert '$500K+' in document
    assert 'Block' in document
    assert 'Mercari' in document
    assert document.count('href="https://calendar.example/book"') >= 2
    assert 'Who is Tera Earlywine?' in document
    assert 'What does Tera Earlywine do?' in document
    assert 'When should a company hire Tera?' in document


def test_contact_urls_remain_single_escaped_attributes(app_factory):
    booking_url = 'https://calendar.example/book?source=portfolio&note="quoted"'
    document = render_home(
        app_factory(
            CONTACT_EMAIL='hello+portfolio@example.test',
            BOOKING_URL=booking_url,
        )
    )

    booking_link = next(
        link
        for link in collect_elements(document, 'a')
        if link.get('data-contact-method') == 'booking'
    )
    assert booking_link['href'] == booking_url
    assert 'onmouseover' not in booking_link
    assert 'source=portfolio&amp;note=&#34;quoted&#34;' in document


def test_homepage_renders_canonical_open_graph_verification_and_json_ld(
    app_factory,
):
    document = render_home(
        app_factory(
            SEARCH_CONSOLE_VERIFICATION='verification-token',
            SITE_URL='https://portfolio.example/base/?campaign=ignored#section',
        )
    )
    expected_url = 'https://portfolio.example/base/'
    links = collect_elements(document, 'link')
    metadata = collect_elements(document, 'meta')

    assert {'rel': 'canonical', 'href': expected_url} in links
    assert next(meta for meta in metadata if meta.get('property') == 'og:url')['content'] == expected_url
    assert (
        next(
            meta
            for meta in metadata
            if meta.get('name') == 'google-site-verification'
        )['content']
        == 'verification-token'
    )

    match = re.search(
        r'<script type="application/ld\+json">(.*?)</script>',
        document,
        re.DOTALL,
    )
    assert match
    structured_data = json.loads(match.group(1))
    assert structured_data['@context'] == 'https://schema.org'
    assert {node['@type'] for node in structured_data['@graph']} == {
        'Person',
        'ProfessionalService',
        'FAQPage',
    }
    assert all(node['url'] == expected_url for node in structured_data['@graph'])

    person = next(
        node for node in structured_data['@graph'] if node['@type'] == 'Person'
    )
    assert person['name'] == 'Tera Earlywine'
    assert person['jobTitle'] == 'Independent Data & AI Consultant'
    assert (
        'Production-grade data and AI for regulated, high-consequence operations'
        in person['knowsAbout']
    )

    service = next(
        node
        for node in structured_data['@graph']
        if node['@type'] == 'ProfessionalService'
    )
    assert service['founder'] == {'@id': f'{expected_url}#person'}
    assert 'Data platform modernization' in service['serviceType']

    faq = next(
        node for node in structured_data['@graph'] if node['@type'] == 'FAQPage'
    )
    questions = {
        entity['name']: entity['acceptedAnswer']['text']
        for entity in faq['mainEntity']
    }
    assert questions['Who is Tera Earlywine?'] in document
    assert questions['What does Tera Earlywine do?'] in document


@pytest.mark.parametrize(
    'unsafe_site_url',
    [
        'javascript:alert(1)',
        'https://user:password@portfolio.example',
        'https://portfolio.example:not-a-port',
    ],
)
def test_unsafe_site_urls_do_not_publish_canonical_metadata(
    app_factory,
    unsafe_site_url,
):
    document = render_home(app_factory(SITE_URL=unsafe_site_url))

    assert not any(
        link.get('rel') == 'canonical'
        for link in collect_elements(document, 'link')
    )
    assert not any(
        meta.get('property') == 'og:url'
        for meta in collect_elements(document, 'meta')
    )
    assert 'application/ld+json' not in document


def test_robots_and_sitemap_publish_the_normalized_homepage(app_factory):
    app = app_factory(SITE_URL='https://portfolio.example/base/?ignored=1')
    client = app.test_client()

    robots = client.get('/robots.txt')
    assert robots.status_code == 200
    assert robots.mimetype == 'text/plain'
    assert robots.get_data(as_text=True) == (
        'User-agent: *\n'
        'Allow: /\n'
        '\n'
        'Sitemap: https://portfolio.example/base/sitemap.xml\n'
    )

    sitemap = client.get('/sitemap.xml')
    assert sitemap.status_code == 200
    assert sitemap.mimetype == 'application/xml'
    root = ElementTree.fromstring(sitemap.data)
    assert root.tag == '{http://www.sitemaps.org/schemas/sitemap/0.9}urlset'
    location = root.find(
        '{http://www.sitemaps.org/schemas/sitemap/0.9}url/'
        '{http://www.sitemaps.org/schemas/sitemap/0.9}loc'
    )
    assert location is not None
    assert location.text == 'https://portfolio.example/base/'


def test_sitemap_remains_valid_when_site_url_is_unconfigured(app_factory):
    client = app_factory().test_client()

    assert 'Sitemap:' not in client.get('/robots.txt').get_data(as_text=True)
    root = ElementTree.fromstring(client.get('/sitemap.xml').data)
    assert root.tag == '{http://www.sitemaps.org/schemas/sitemap/0.9}urlset'
    assert list(root) == []


def test_404_and_500_pages_are_noindex_and_track_the_home_link(app_factory):
    app = app_factory(GOOGLE_ANALYTICS_MEASUREMENT_ID='G-PORTFOLIO1')

    @app.route('/_force-server-error')
    def force_server_error():
        raise RuntimeError('intentional test error')

    app.config.update(TESTING=False, PROPAGATE_EXCEPTIONS=False)
    client = app.test_client()

    for response, expected_status in (
        (client.get('/missing'), 404),
        (client.get('/_force-server-error'), 500),
    ):
        assert response.status_code == expected_status
        document = response.get_data(as_text=True)
        robots_meta = next(
            meta
            for meta in collect_elements(document, 'meta')
            if meta.get('name') == 'robots'
        )
        assert robots_meta['content'] == 'noindex, nofollow'
        home_link = next(
            link
            for link in collect_elements(document, 'a')
            if 'btn-primary' in link.get('class', '').split()
        )
        assert home_link['data-analytics-event'] == 'navigation_click'
        assert home_link['data-placement'] == 'error'
        assert home_link['data-destination-type'] == 'home'


def test_analytics_client_has_basic_consent_and_sanitization_contracts():
    source = ANALYTICS_JS.read_text()

    assert "const CONSENT_STORAGE_KEY = 'analytics_consent';" in source
    assert "new Set(['accepted', 'rejected'])" in source
    assert "window.localStorage.setItem(CONSENT_STORAGE_KEY, choice)" in source
    assert "window.localStorage.removeItem(CONSENT_STORAGE_KEY)" in source
    assert "function initializeGoogleAnalytics()" in source
    assert "document.createElement('script')" in source
    assert "readConsentChoice() !== 'accepted'" in source
    assert "window.gtag('consent'" not in source
    assert "const expectedParameters = EVENT_PARAMETERS[eventName]" in source
    assert '!ALLOWED_VALUES[parameterName].has(value)' in source
    assert "cookie_domain: 'none'" in source
    assert "page_referrer: ''" in source
    assert "window.gtag('event', eventName, {" in source
    assert "event.target.closest('[data-analytics-event]')" in source
    assert "document.querySelector('[data-analytics-contact-view]')" in source
    assert 'entry.intersectionRatio >= 0.5' in source
    assert 'observer.disconnect()' in source
    assert 'pageUrl.origin}${pageUrl.pathname}' in source
    assert 'page_path: pageUrl.pathname' in source


def test_rendered_tracking_attributes_follow_the_measurement_allowlist(app_factory):
    document = render_home(
        app_factory(
            BOOKING_URL='https://calendar.example/book',
            CONTACT_EMAIL='hello@example.test',
            GOOGLE_ANALYTICS_MEASUREMENT_ID='G-PORTFOLIO1',
        )
    )
    links = collect_elements(document, 'a')
    tracked_links = [link for link in links if 'data-analytics-event' in link]

    assert tracked_links
    for link in tracked_links:
        event_name = link['data-analytics-event']
        assert event_name in EVENT_PARAMETERS

        for parameter in EVENT_PARAMETERS[event_name]:
            attribute = f"data-{parameter.replace('_', '-')}"
            assert link[attribute] in ALLOWED_VALUES[parameter]

    observed_contracts = {
        (
            link['data-analytics-event'],
            link['data-placement'],
            link['data-destination-type'],
        )
        for link in tracked_links
    }
    assert {
        ('navigation_click', 'navigation', 'home'),
        ('navigation_click', 'navigation', 'section'),
        ('navigation_click', 'hero', 'section'),
        ('contact_click', 'hero', 'booking'),
        ('outbound_click', 'contact', 'github'),
        ('outbound_click', 'contact', 'linkedin'),
        ('contact_click', 'contact', 'booking'),
    } <= observed_contracts

    contact_section = next(
        section
        for section in collect_elements(document, 'section')
        if section.get('id') == 'contact'
    )
    assert 'data-analytics-contact-view' in contact_section


@pytest.mark.parametrize(
    'booking_url',
    [
        'http://calendar.example/book',
        '//calendar.example/book',
        'javascript:alert(1)',
        'https://user:password@calendar.example/book',
        'https://calendar.example:not-a-port/book',
        'https://calendar.example/book path',
    ],
)
def test_invalid_booking_urls_are_hidden_and_warned(
    app_factory,
    booking_url,
    caplog,
):
    document = render_home(app_factory(BOOKING_URL=booking_url))

    assert not any(
        link.get('data-contact-method') == 'booking'
        for link in collect_elements(document, 'a')
    )
    assert 'BOOKING_URL must be an absolute HTTPS URL' in caplog.text


def test_production_configuration_preserves_known_urls_and_optional_fields(
    app_factory,
    caplog,
):
    booking_url = 'https://calendar.app.google/iPH6W8fgvcCws9VA8'
    app = app_factory(
        env='production',
        BOOKING_URL=booking_url,
        GOOGLE_ANALYTICS_MEASUREMENT_ID='G-NF6SVCGZDF',
        SITE_URL='https://www.teraearlywine.com',
    )

    assert app.config['BOOKING_URL'] == booking_url
    assert app.config['SITE_URL'] == 'https://www.teraearlywine.com'
    assert app.config['CONTACT_EMAIL'] == 'tera@idea-factory.io'
    assert app.config['SEARCH_CONSOLE_VERIFICATION'] == ''
    assert 'CONTACT_EMAIL' not in caplog.text
    assert 'SEARCH_CONSOLE_VERIFICATION' not in caplog.text

    deployment_config = (PROJECT_ROOT / 'app.yaml').read_text()
    assert f'BOOKING_URL: "{booking_url}"' in deployment_config
    assert 'SITE_URL: "https://www.teraearlywine.com"' in deployment_config
    assert 'CONTACT_EMAIL: "tera@idea-factory.io"' in deployment_config
    assert 'SEARCH_CONSOLE_VERIFICATION:' not in deployment_config


def test_missing_production_essentials_warn_without_failing(app_factory, caplog):
    app = app_factory(env='production')

    assert app
    assert 'SITE_URL is not configured' in caplog.text
    assert 'BOOKING_URL is not configured' in caplog.text
    assert 'GOOGLE_ANALYTICS_MEASUREMENT_ID is not configured' in caplog.text


def test_homepage_omits_unused_youtube_embed_and_disclosure(
    app_factory,
):
    document = render_home(
        app_factory(GOOGLE_ANALYTICS_MEASUREMENT_ID='G-PORTFOLIO1')
    )

    assert 'youtube.com/embed/' not in document
    assert 'youtube-nocookie.com/embed/' not in document
    assert 'may contact YouTube when it loads' not in document
    assert 'this choice controls site analytics only' not in document


def test_consent_and_footer_colors_meet_wcag_aa_for_small_text():
    source = MAIN_CSS.read_text()

    def contrast_ratio(foreground, background):
        def luminance(color):
            channels = [
                int(color[index:index + 2], 16) / 255
                for index in (1, 3, 5)
            ]
            linear = [
                channel / 12.92
                if channel <= 0.04045
                else ((channel + 0.055) / 1.055) ** 2.4
                for channel in channels
            ]
            return (
                (0.2126 * linear[0])
                + (0.7152 * linear[1])
                + (0.0722 * linear[2])
            )

        lighter, darker = sorted(
            [luminance(foreground), luminance(background)],
            reverse=True,
        )
        return (lighter + 0.05) / (darker + 0.05)

    assert '--color-text-accessible-muted: #5f6368;' in source
    assert '--color-accent-hover: #0041c2;' in source
    assert contrast_ratio('#5f6368', '#ffffff') >= 4.5
    assert contrast_ratio('#0041c2', '#ffffff') >= 4.5
    assert '.consent-banner p {' in source
    assert 'color: var(--color-text-accessible-muted);' in source


def test_measurement_plan_documents_external_ga4_privacy_setup():
    if not MEASUREMENT_PLAN.exists():
        pytest.skip('private analytics measurement plan is not in this checkout')

    contract = MEASUREMENT_PLAN.read_text()

    assert 'The site uses Basic Consent Mode' in contract
    assert 'query strings and fragments are removed' in contract
    assert 'before deploying this implementation' in contract
    assert 'disable automatic outbound click collection' in contract
    assert 'Enable GA4 data redaction' in contract
    assert contract.index('## Pre-release GA4 property prerequisites') < contract.index(
        '## Remaining account setup checklist'
    )
    assert 'full `link_url`' in contract
    assert 'record a second outbound event' in contract
    assert 'rejected consent produces no request to Google Analytics' in contract


def test_javascript_consent_behavior():
    node = shutil.which('node')
    if node is None:
        pytest.skip('Node.js runtime is unavailable')

    subprocess.run(
        [node, str(ANALYTICS_BEHAVIOR_TEST)],
        cwd=PROJECT_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
