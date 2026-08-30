# Set up home blueprint
from urllib.parse import urlsplit, urlunsplit
from xml.etree import ElementTree

from flask import (
    Blueprint,
    Response,
    current_app,
    redirect,
    render_template,
    request,
    url_for,
)


index_bp = Blueprint(
    name='index',  # Blueprint name for endpoint. endpoint -> 'users.login', 'users.update', 'users.delete_account'
    import_name=__name__, 
    template_folder='templates', 
    static_folder='assets',
    static_url_path='/static/assets',   # URL path to serve static files
    url_prefix='/'
)


def _site_url():
    """Return a normalized, absolute site URL or an empty string."""
    configured_url = str(current_app.config.get('SITE_URL') or '').strip()
    if not configured_url:
        return ''

    try:
        parsed_url = urlsplit(configured_url)
        if (
            parsed_url.scheme.lower() not in {'http', 'https'}
            or not parsed_url.hostname
            or parsed_url.username
            or parsed_url.password
        ):
            return ''
        # Accessing port validates malformed values such as ":not-a-port".
        parsed_url.port
    except ValueError:
        return ''

    path = parsed_url.path.rstrip('/')
    return urlunsplit(
        (
            parsed_url.scheme.lower(),
            parsed_url.netloc,
            path,
            '',
            '',
        )
    )


@index_bp.app_context_processor
def seo_metadata():
    """Provide safe, site-wide metadata and homepage structured data."""
    site_url = _site_url()
    homepage_url = f'{site_url}/' if site_url else ''
    is_homepage = request.endpoint == 'index.index'

    structured_data = None
    if is_homepage and homepage_url:
        person_id = f'{homepage_url}#person'
        structured_data = {
            '@context': 'https://schema.org',
            '@graph': [
                {
                    '@type': 'Person',
                    '@id': person_id,
                    'name': 'Tera Earlywine',
                    'url': homepage_url,
                    'jobTitle': 'Staff Data Engineer, Advisor, and Consultant',
                    'sameAs': [
                        'https://github.com/teraearlywine',
                        'https://www.linkedin.com/in/teraearlywine/',
                    ],
                },
                {
                    '@type': 'ProfessionalService',
                    '@id': f'{homepage_url}#professional-service',
                    'name': 'Tera Earlywine Data Consulting',
                    'url': homepage_url,
                    'description': (
                        'Data engineering advisory and consulting for '
                        'trusted, scalable data products.'
                    ),
                    'founder': {'@id': person_id},
                },
            ],
        }

    return {
        'canonical_url': homepage_url if is_homepage else '',
        'is_homepage': is_homepage,
        'search_console_verification': str(
            current_app.config.get('SEARCH_CONSOLE_VERIFICATION') or ''
        ).strip(),
        'seo_structured_data': structured_data,
    }


@index_bp.route("/")
def index():
    """

    Browser home page for www.teraearlywine.com
    """
    return render_template('home/home.html')


@index_bp.route('/robots.txt')
def robots():
    """Publish crawler rules and the canonical sitemap location."""
    site_url = _site_url()
    directives = ['User-agent: *', 'Allow: /']
    if site_url:
        directives.extend(['', f'Sitemap: {site_url}/sitemap.xml'])

    return Response('\n'.join(directives) + '\n', mimetype='text/plain')


@index_bp.route('/sitemap.xml')
def sitemap():
    """Publish a minimal, safely escaped sitemap for the canonical homepage."""
    namespace = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ElementTree.register_namespace('', namespace)
    urlset = ElementTree.Element(f'{{{namespace}}}urlset')

    site_url = _site_url()
    if site_url:
        url_element = ElementTree.SubElement(urlset, f'{{{namespace}}}url')
        location = ElementTree.SubElement(url_element, f'{{{namespace}}}loc')
        location.text = f'{site_url}/'

    document = ElementTree.tostring(
        urlset,
        encoding='utf-8',
        xml_declaration=True,
    )
    return Response(document, mimetype='application/xml')


@index_bp.route("/about-me")
def about_me():
    """
    Redirect to experience section on homepage.
    """
    return redirect(url_for('index.index') + '#experience')
