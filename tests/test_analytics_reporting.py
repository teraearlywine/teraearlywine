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
CONSULTANCY_CSS = PROJECT_ROOT / 'core/home/assets/css/consultancy.css'

EVENT_PARAMETERS = {
    'newsletter_cta_click': ('placement', 'guide'),
    'navigation_click': ('placement', 'destination_type'),
    'outbound_click': ('placement', 'destination_type'),
    'contact_submit': (),
    'resource_download': ('placement', 'destination_type'),
    'contact_click': ('contact_method', 'placement', 'destination_type'),
}
ALLOWED_VALUES = {
    'guide': {'teams', 'professionals', 'both'},
    'contact_method': {'email', 'booking'},
    'placement': {
        'navigation',
        'hero',
        'services',
        'projects',
        'contact',
        'footer',
        'error',
        'article',
        'signup',
        'writing_stack',
        'featured',
        'archive',
    },
    'destination_type': {
        'teams',
        'professionals',
        'writing',
        'section',
        'service',
        'github',
        'linkedin',
        'youtube',
        'idea_factory',
        'email',
        'booking',
        'home',
        'resource',
        'archive',
        'rss',
        'exercise',
        'dashboard_example',
        'net_sales_demo',
        'decision_note',
        'diagnostic',
        'ai_workflow_review',
        'migration_cutover',
        'readiness_scorecard',
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


def test_production_ga_configuration_disables_debug_and_defers_google(app_factory):
    document = render_home(app_factory(
        GOOGLE_ANALYTICS_MEASUREMENT_ID='G-NF6SVCGZDF',
        SITE_URL='https://www.teraearlywine.com',
    ))
    match = re.search(
        r'<script id="analyticsConfig" type="application/json">\s*(.*?)\s*</script>',
        document,
        re.DOTALL,
    )
    assert json.loads(match.group(1)) == {
        'measurementId': 'G-NF6SVCGZDF', 'debugMode': False, 'pagePath': '/',
    }
    assert 'googletagmanager.com' not in document
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
        booking_links = [
            link
            for link in links
            if link.get('data-contact-method') == 'booking'
        ]
        assert len(booking_links) == 1
        assert booking_links[0]['data-placement'] == 'contact'
        assert document.index('id="contact-heading"') < document.index('Book a 30-minute call') < document.index('data-contact-form')
        teams_html = app_factory(**configuration).test_client().get(
            '/for-teams/'
        ).get_data(as_text=True)
        assert any(
            link.get('data-placement') == 'hero'
            and link.get('href') == configuration['BOOKING_URL']
            for link in collect_elements(teams_html, 'a')
        )


def test_homepage_answers_buyer_questions_and_leads_to_fit_call(
    app_factory,
):
    document = render_home(
        app_factory(BOOKING_URL='https://calendar.example/book')
    )

    text = ' '.join(re.sub(r'<[^>]+>', ' ', document).split())
    assert 'Fix the reporting and workflows slowing your team down.' in text
    assert 'Help me scope it' in document
    assert 'proof of concept' in document
    assert 'projected Snowflake savings' in document
    assert 'Block compliance data engineering engagement through Qbiz' not in document
    assert document.index('id="services"') < document.index('id="projects"')
    assert 'open to applied AI engineering and senior data roles' not in document
    assert 'independent consultant' not in text.lower()
    assert '$500K+' in document
    assert 'Block' in document
    assert 'Mercari' in document
    assert 'Do we need a fully defined project?' in document
    assert 'How does an engagement start?' in document
    assert document.index('id="contact"') < document.index('id="faq"') < document.index('data-contact-form')
    links = collect_elements(document, 'a')
    for path in ['#services', '#projects', '#experience', '#contact', '/blog/', '/for-professionals/']:
        assert any(link.get('href') == path for link in links)


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
    assert person['jobTitle'] == 'Data and AI Consultant'
    assert (
        'Cross-functional collaboration' in person['knowsAbout']
    )

    service = next(
        node
        for node in structured_data['@graph']
        if node['@type'] == 'ProfessionalService'
    )
    assert service['founder'] == {'@id': f'{expected_url}#person'}
    assert 'Data and reporting' in service['serviceType']

    faq = next(
        node for node in structured_data['@graph'] if node['@type'] == 'FAQPage'
    )
    questions = {
        entity['name']: entity['acceptedAnswer']['text']
        for entity in faq['mainEntity']
    }
    assert set(questions) == {'Do we need a fully defined project?', 'How does an engagement start?'}
    assert all(answer in document for answer in questions.values())


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
        body = collect_elements(document, 'body')[0]
        assert 'error-page' in body.get('class', '').split()
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
        analytics_match = re.search(
            r'<script id="analyticsConfig" type="application/json">\s*(.*?)\s*</script>',
            document, re.DOTALL,
        )
        assert json.loads(analytics_match.group(1))['pagePath'] == f'/{expected_status}'



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
    assert 'page_location: window.location.origin + pagePath' in source
    assert 'page_path: pagePath' in source


@pytest.mark.parametrize(('path', 'expected'), [
    ('/for-teams/', [
        ('/services/warehouse-cost-diagnostic', 'services', 'diagnostic'),
        ('/services/production-ai-systems', 'services', 'ai_workflow_review'),
        ('/services/data-migration-rescue', 'services', 'migration_cutover'),
    ]),
    ('/for-professionals/', [
        ('#exercise', 'hero', 'exercise'),
        ('/blog/a-dashboard-needs-a-decision/', 'services', 'dashboard_example'),
        ('#sample', 'services', 'net_sales_demo'),
        ('/blog/a-note-to-my-future-self/', 'services', 'decision_note'),
    ]),
    ('/blog/', [
        ('/services/warehouse-cost-diagnostic', 'services', 'diagnostic'),
        ('/blog/nothing-wasted/', 'archive', 'writing'),
    ]),
    ('/blog/ai-workflow-production-evidence/', [
        ('/services/production-ai-systems', 'article', 'ai_workflow_review'),
        ('/blog/audit-agent-proof-of-concept/', 'article', 'writing'),
        ('/#contact', 'article', 'section'),
    ]),
    ('/', [('/services/warehouse-cost-diagnostic', 'projects', 'diagnostic')]),
    ('/services/data-platform-modernization', [
        ('/services/warehouse-cost-diagnostic', 'services', 'diagnostic'),
    ]),
    ('/blog/sql-techniques-and-the-bottom-line/', [
        ('/services/warehouse-cost-diagnostic', 'article', 'diagnostic'),
    ]),
])
def test_brand_links_emit_navigation_events(app_factory, path, expected):
    document = app_factory().test_client().get(path).get_data(as_text=True)
    links = collect_elements(document, 'a')
    navigation = {
        (link['href'], link['data-placement'], link['data-destination-type'])
        for link in links if link.get('data-analytics-event') == 'navigation_click'
    }
    assert set(expected) <= navigation


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
            link.get('data-destination-type', link.get('data-guide')),
        )
        for link in tracked_links
    }
    assert {
        ('navigation_click', 'navigation', 'home'),
        ('navigation_click', 'navigation', 'section'),
        ('newsletter_cta_click', 'footer', 'both'),
        ('navigation_click', 'hero', 'section'),
        ('navigation_click', 'services', 'service'),
        ('navigation_click', 'footer', 'professionals'),
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


def test_small_text_colors_meet_wcag_aa():
    main_source = MAIN_CSS.read_text()
    consultancy_source = CONSULTANCY_CSS.read_text()

    def declaration(source, selector, property_name):
        block_match = re.search(
            rf'(?m)^{re.escape(selector)}\s*\{{([^}}]*)\}}',
            source,
        )
        assert block_match, f'Missing CSS selector: {selector}'
        value_match = re.search(
            rf'{re.escape(property_name)}:\s*([^;]+);',
            block_match.group(1),
        )
        assert value_match, f'Missing {property_name} in {selector}'
        return value_match.group(1).strip()

    def resolve_color(value):
        variable_match = re.fullmatch(r'var\((--[^)]+)\)', value)
        if variable_match:
            return resolve_color(declaration(
                main_source,
                ':root',
                variable_match.group(1),
            ))
        return value

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

    # Resolve the shared tokens rather than pinning a superseded palette.
    for background in ('var(--white)', 'var(--cool-gray)'):
        for foreground in ('var(--color-text)', 'var(--color-text-secondary)',
                           'var(--color-text-accessible-muted)', 'var(--color-error)'):
            assert contrast_ratio(resolve_color(foreground), resolve_color(background)) >= 4.5
    for background in ('var(--color-accent)', 'var(--color-accent-hover)'):
        assert contrast_ratio(resolve_color('var(--white)'), resolve_color(background)) >= 4.5
    assert '.consent-banner p {' in main_source
    assert 'color: var(--color-text-accessible-muted);' in main_source

    muted = resolve_color('var(--color-text-accessible-muted)')
    section_background = resolve_color(
        declaration(consultancy_source, '.section', 'background')
    )
    project_background = resolve_color(
        declaration(consultancy_source, '#projects', 'background')
    )
    method_background = resolve_color(
        declaration(consultancy_source, '#method', 'background')
    )
    assert contrast_ratio(muted, section_background) >= 4.5
    assert contrast_ratio(muted, project_background) >= 4.5

    selector_backgrounds = {
        '.section-kicker': section_background,
        '.project-card .project-label': project_background,
        '.project-tag': project_background,
        '.timeline-date': section_background,
        '.timeline-company': section_background,
    }
    for selector, background in selector_backgrounds.items():
        foreground = resolve_color(
            declaration(consultancy_source, selector, 'color')
        )
        assert contrast_ratio(foreground, background) >= 4.5

    method_kicker = resolve_color(
        declaration(
            consultancy_source,
            '#method .section-kicker,\n#method .method-list span',
            'color',
        )
    )
    assert contrast_ratio(method_kicker, method_background) >= 4.5


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


@pytest.mark.parametrize('path', [
    '/person@example.com', '/customer/PRIVATE_ID',
    '/blog/PRIVATE_ID/', '/services/PRIVATE_ID',
])
def test_unknown_paths_report_fixed_404_without_raw_path(app_factory, path):
    app = app_factory(GOOGLE_ANALYTICS_MEASUREMENT_ID='G-NF6SVCGZDF')
    response = app.test_client().get(path + '?email=PRIVATE_EMAIL')
    assert response.status_code == 404
    match = re.search(
        r'<script id="analyticsConfig" type="application/json">\s*(.*?)\s*</script>',
        response.get_data(as_text=True), re.DOTALL,
    )
    assert json.loads(match.group(1))['pagePath'] == '/404'
    assert 'PRIVATE_' not in match.group(1)
    assert 'person@example.com' not in match.group(1)


def test_known_content_paths_are_preserved_in_analytics_config(app_factory):
    from core.home.home import ARTICLES, SERVICES
    app = app_factory(GOOGLE_ANALYTICS_MEASUREMENT_ID='G-NF6SVCGZDF')
    paths = ['/', '/blog/', '/for-teams/', '/for-professionals/', '/newsletter/']
    paths += [f'/services/{slug}' for slug in SERVICES]
    paths += [f"/blog/{article['slug']}/" for article in ARTICLES]
    for path in paths:
        response = app.test_client().get(path + '?email=PRIVATE_EMAIL')
        assert response.status_code == 200
        match = re.search(
            r'<script id="analyticsConfig" type="application/json">\s*(.*?)\s*</script>',
            response.get_data(as_text=True), re.DOTALL,
        )
        assert json.loads(match.group(1))['pagePath'] == path
        assert 'PRIVATE_EMAIL' not in match.group(1)
