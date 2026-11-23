# Set up home blueprint
import hashlib
from ipaddress import ip_address
import os
import time
import uuid
from urllib.parse import urlsplit, urlunsplit
from xml.etree import ElementTree

from flask import (
    Blueprint,
    Response,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from core.home.blog_content import (
    ARTICLES, ARTICLES_BY_SLUG, BLOG_DESCRIPTION, FEATURED_ARTICLES,
)
from core.home.contact_admission import ContactAdmissionError, ContactAdmissionStore
from core.home.contact_delivery import (
    ContactDeliveryError,
    ContactFiltered,
    ContactSubmission,
    deliver_contact_submission,
)
from core.home.forms import (
    AI_AUTOMATION_ENGAGEMENT, DATA_REPORTING_ENGAGEMENT, MIGRATION_RESCUE_ENGAGEMENT,
    PROJECT_DELIVERY_ENGAGEMENT,
    UNSCOPED_ENGAGEMENT, WAREHOUSE_DIAGNOSTIC_ENGAGEMENT, ContactForm,
)
from core.home.services import SERVICES, WAREHOUSE_DIAGNOSTIC_SLUG


index_bp = Blueprint(
    name='index',  # Blueprint name for endpoint. endpoint -> 'users.login', 'users.update', 'users.delete_account'
    import_name=__name__, 
    template_folder='templates', 
    static_folder='assets',
    static_url_path='/static/assets',   # URL path to serve static files
    url_prefix='/'
)

CONTACT_SUBMISSIONS_SESSION_KEY = 'contact_submissions'
CONTACT_SUBMISSION_TTL_SECONDS = 3600
MAX_PENDING_CONTACT_SUBMISSIONS = 5
SERVICE_INQUIRY_TOPICS = {
    'data-platform-modernization': DATA_REPORTING_ENGAGEMENT,
    'data-migration-rescue': MIGRATION_RESCUE_ENGAGEMENT,
    'production-ai-systems': AI_AUTOMATION_ENGAGEMENT,
    'fractional-data-leadership': PROJECT_DELIVERY_ENGAGEMENT,
    WAREHOUSE_DIAGNOSTIC_SLUG: WAREHOUSE_DIAGNOSTIC_ENGAGEMENT,
}
FAQ_ITEMS = (
    {
        'question': 'Do we need a fully defined project?',
        'answer': 'No. A few sentences about what’s happening and what you’d like to change are enough to get started.',
    },
    {
        'question': 'How does an engagement start?',
        'answer': 'If the first conversation points to a fit, we’ll agree on the scope, who does what, and what your team will take away.',
    },
)


def _contact_submission_states():
    """Return recent delivery state without storing contact form contents."""
    now = int(time.time())
    stored_states = session.get(CONTACT_SUBMISSIONS_SESSION_KEY, {})
    if not isinstance(stored_states, dict):
        stored_states = {}

    valid_states = {}
    for submission_id, state in stored_states.items():
        if (
            isinstance(state, dict)
            and isinstance(state.get('created_at'), int)
            and now - state['created_at'] <= CONTACT_SUBMISSION_TTL_SECONDS
        ):
            valid_states[submission_id] = {
                'created_at': state['created_at'],
                'delivered': (
                    state.get('delivered') is True
                    or (
                        state.get('resend') is True
                        and state.get('linear') is True
                    )
                ),
                'fingerprint': (
                    state.get('fingerprint')
                    if isinstance(state.get('fingerprint'), str)
                    else ''
                ),
            }

    return dict(
        sorted(
            valid_states.items(),
            key=lambda item: item[1]['created_at'],
        )[-MAX_PENDING_CONTACT_SUBMISSIONS:]
    )


def _store_contact_submission_states(states):
    session[CONTACT_SUBMISSIONS_SESSION_KEY] = states
    session.modified = True


def _new_contact_submission():
    states = _contact_submission_states()
    submission_id = str(uuid.uuid4())
    states[submission_id] = {
        'created_at': int(time.time()),
        'delivered': False,
        'fingerprint': '',
    }
    _store_contact_submission_states(states)
    return submission_id


def _contact_form_response(form, message, status_code, challenge=False):
    if request.accept_mimetypes.best == 'application/json':
        field_errors = {
            field_name: errors
            for field_name, errors in form.errors.items()
            if field_name in {
                'name',
                'email',
                'engagement_type',
                'message',
            }
        }
        return jsonify(
            {
                'ok': False,
                'message': message,
                'errors': field_errors,
                **({'challenge_required': True} if challenge else {}),
            }
        ), status_code

    selected_topic = form.engagement_type.data
    safe_form = ContactForm(
        formdata=None,
        submission_id=_new_contact_submission(),
        engagement_type=(
            selected_topic
            if any(value == selected_topic for value, _ in form.engagement_type.choices) else None
        ),
    )
    for field_name in ('name', 'email', 'engagement_type', 'message'):
        safe_form[field_name].errors = list(form.errors.get(field_name, ()))

    return render_template(
        'home/home.html',
        contact_form=safe_form,
        contact_error=message,
        contact_challenge=challenge,
    ), status_code


def _is_valid_submission_id(value):
    try:
        parsed = uuid.UUID(str(value), version=4)
    except (ValueError, TypeError, AttributeError):
        return False
    return str(parsed) == value


def _contact_submission_fingerprint(submission):
    """Bind one opaque ID to one normalized payload without storing PII."""
    private_payload = '\0'.join(
        (
            submission.name,
            submission.email,
            submission.engagement_type or '',
            submission.message,
        )
    )
    return hashlib.sha256(private_payload.encode('utf-8')).hexdigest()


def _contact_source_identity():
    """Return a canonical address from a server-controlled request source."""
    source = request.remote_addr or ''
    if os.environ.get('GAE_ENV') == 'standard':
        # App Engine may supply this internal value; never infer an identity
        # from caller-provided forwarding headers or an App Engine proxy peer.
        source = request.headers.get('X-Appengine-User-Ip', '')
    try:
        return ip_address(str(source).strip()).compressed
    except ValueError:
        return None


def _contact_admission_store():
    if 'contact_admission_store' not in current_app.extensions:
        current_app.extensions['contact_admission_store'] = ContactAdmissionStore(
            current_app.config['CONTACT_ADMISSION_PROJECT'],
            current_app.config['SECRET_KEY'],
        )
    return current_app.extensions['contact_admission_store']


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
    service_slug = (request.view_args or {}).get('slug')
    service = SERVICES.get(service_slug) if request.endpoint == 'index.service' else None
    is_blog_index = request.endpoint == 'index.blog'
    is_rss_subscription = request.endpoint == 'index.rss_subscription'
    article = (
        ARTICLES_BY_SLUG.get(service_slug)
        if request.endpoint == 'index.blog_article' else None
    )
    is_blog = request.endpoint in {'index.blog', 'index.blog_article', 'index.rss_subscription'}
    canonical_url = homepage_url if is_homepage else ''
    # Derive analytics paths from registered routes and known content, never
    # request.path: even a 404 URL may contain an email or private identifier.
    analytics_page_path = '/404'
    if is_homepage or request.endpoint == 'index.contact':
        analytics_page_path = '/'
    elif request.endpoint in {'index.for_teams', 'index.for_professionals', 'index.newsletter'}:
        analytics_page_path = url_for(request.endpoint)
        canonical_url = f'{site_url}{analytics_page_path}' if site_url else ''
    elif service:
        analytics_page_path = url_for('index.service', slug=service_slug)
    elif is_blog_index:
        analytics_page_path = url_for('index.blog')
    elif article:
        analytics_page_path = url_for('index.blog_article', slug=article['slug'])
    elif is_rss_subscription:
        analytics_page_path = url_for('index.rss_subscription')
        canonical_url = f'{site_url}{analytics_page_path}' if site_url else ''

    structured_data = None
    if is_homepage and homepage_url:
        person_id = f'{homepage_url}#person'
        service_id = f'{homepage_url}#professional-service'
        structured_data = {
            '@context': 'https://schema.org',
            '@graph': [
                {
                    '@type': 'Person',
                    '@id': person_id,
                    'name': 'Tera Earlywine',
                    'url': homepage_url,
                    'jobTitle': 'Data and AI Consultant',
                    'description': (
                        'Data and AI consulting to improve reporting, automate repetitive '
                        'work, and help business and technical teams move projects forward.'
                    ),
                    'knowsAbout': [
                        'Data and reporting',
                        'Workflow automation',
                        'Cross-functional collaboration',
                        'Data platform modernization',
                        'Data reliability',
                        'AI-ready data foundations',
                        'Agent orchestration and operational controls',
                        'Data governance',
                    ],
                    'sameAs': [
                        'https://github.com/teraearlywine',
                        'https://www.linkedin.com/in/teraearlywine/',
                    ],
                },
                {
                    '@type': 'ProfessionalService',
                    '@id': service_id,
                    'name': 'Tera Earlywine Consulting',
                    'url': homepage_url,
                    'description': (
                        'Consulting for data and reporting, practical AI and workflow '
                        'automation, and data and AI project delivery.'
                    ),
                    'founder': {'@id': person_id},
                    'serviceType': [
                        'Data and reporting',
                        SERVICES['production-ai-systems']['name'],
                        'Data and AI project delivery',
                    ],
                    'areaServed': 'United States',
                },
                {
                    '@type': 'FAQPage',
                    '@id': f'{homepage_url}#faq',
                    'url': homepage_url,
                    'mainEntity': [
                        {
                            '@type': 'Question',
                            'name': item['question'],
                            'acceptedAnswer': {
                                '@type': 'Answer',
                                'text': item['answer'],
                            },
                        }
                        for item in FAQ_ITEMS
                    ],
                },
            ],
        }

    if service and homepage_url:
        canonical_url = f'{site_url}/services/{service_slug}'
        structured_data = {
            '@context': 'https://schema.org',
            '@graph': [
                {
                    '@type': 'Service',
                    '@id': f'{canonical_url}#service',
                    'url': canonical_url,
                    'name': service['name'],
                    'description': service['description'],
                    'serviceType': service['name'],
                    'provider': {
                        '@type': 'Person',
                        '@id': f'{homepage_url}#person',
                        'name': 'Tera Earlywine',
                        'url': homepage_url,
                    },
                    'areaServed': 'United States',
                },
                {
                    '@type': 'BreadcrumbList',
                    'itemListElement': [
                        {'@type': 'ListItem', 'position': 1,
                         'name': 'Home', 'item': homepage_url},
                        {'@type': 'ListItem', 'position': 2,
                         'name': service['name'], 'item': canonical_url},
                    ],
                },
            ],
        }

    if (is_blog_index or article) and homepage_url:
        blog_url = f'{site_url}/blog/'
        canonical_url = f"{blog_url}{article['slug']}/" if article else blog_url
        author = {
            '@type': 'Person',
            '@id': f'{homepage_url}#person',
            'name': 'Tera Earlywine',
            'url': homepage_url,
        }
        breadcrumbs = [
            {'@type': 'ListItem', 'position': 1,
             'name': 'Home', 'item': homepage_url},
            {'@type': 'ListItem', 'position': 2,
             'name': 'Writing', 'item': blog_url},
        ]
        if article:
            entity = {
                '@type': 'BlogPosting',
                '@id': f'{canonical_url}#article',
                'url': canonical_url,
                'mainEntityOfPage': canonical_url,
                'headline': article['title'],
                'description': article['dek'],
                'articleSection': article['category'],
                'wordCount': sum(
                    len(paragraph.split())
                    for section in article['sections']
                    for paragraph in section['paragraphs']
                ),
                'author': author,
                'isPartOf': {'@type': 'Blog', '@id': f'{blog_url}#blog'},
            }
            breadcrumbs.append({
                '@type': 'ListItem', 'position': 3,
                'name': article['title'], 'item': canonical_url,
            })
        else:
            entity = {
                '@type': 'Blog',
                '@id': f'{blog_url}#blog',
                'url': blog_url,
                'name': 'The Business of Technology | Tera Earlywine',
                'description': BLOG_DESCRIPTION,
                'author': author,
                'blogPost': [
                    {'@type': 'BlogPosting', 'headline': item['title'],
                     'url': f"{blog_url}{item['slug']}/"}
                    for item in ARTICLES
                ],
            }
        structured_data = {
            '@context': 'https://schema.org',
            '@graph': [
                entity,
                {'@type': 'BreadcrumbList', 'itemListElement': breadcrumbs},
            ],
        }

    return {
        'canonical_url': canonical_url,
        'analytics_page_path': analytics_page_path,
        'rss_url': f'{site_url}/rss.xml' if site_url else '',
        'is_homepage': is_homepage,
        'page_og_type': 'article' if article else 'website',
        'is_blog': is_blog,
        'services': SERVICES,
        'warehouse_diagnostic_slug': WAREHOUSE_DIAGNOSTIC_SLUG,
        'social_image_url': (
            f"{site_url}{url_for('index.static', filename='images/consulting-social.jpg')}"
            if site_url else ''
        ),
        'search_console_verification': str(
            current_app.config.get('SEARCH_CONSOLE_VERIFICATION') or ''
        ).strip(),
        'seo_structured_data': structured_data,
        'faq_items': FAQ_ITEMS,
    }


@index_bp.route("/")
def index():
    """

    Browser home page for www.teraearlywine.com
    """
    engagement = SERVICE_INQUIRY_TOPICS.get(request.args.get('topic'))
    form = ContactForm(submission_id=_new_contact_submission(), engagement_type=engagement)
    return render_template('home/home.html', contact_form=form)


@index_bp.post('/contact')
def contact():
    """Validate and deliver a website contact submission."""
    form = ContactForm()
    invalid_message = 'Please check the highlighted fields and try again.'
    if form.website.data:
        current_app.logger.warning('contact_spam_decision ruleId=honeypot timestamp=%s count=1', int(time.time()))
        return _contact_form_response(form, 'Your submission could not be accepted. Please try again later.', 400)
    if not form.validate_on_submit():
        return _contact_form_response(form, invalid_message, 400)

    submission_id = form.submission_id.data
    states = _contact_submission_states()
    state = states.get(submission_id)
    if (
        not _is_valid_submission_id(submission_id)
        or state is None
        or form.website.data
    ):
        return _contact_form_response(
            form,
            'Please refresh the page and try again.',
            400,
        )

    required_config = (
        current_app.config['CONTACT_BROKER_URL'],
        current_app.config['CONTACT_BROKER_SECRET'],
    )
    if not all(required_config):
        current_app.logger.error(
            'Contact delivery is not fully configured for submission %s',
            submission_id,
        )
        return _contact_form_response(
            form,
            'Message delivery is temporarily unavailable. Please try again later.',
            503,
        )

    # Map the public choices to the categories the delivery broker supports.
    engagement = {
        UNSCOPED_ENGAGEMENT: None,
        MIGRATION_RESCUE_ENGAGEMENT: DATA_REPORTING_ENGAGEMENT,
        WAREHOUSE_DIAGNOSTIC_ENGAGEMENT: PROJECT_DELIVERY_ENGAGEMENT,
    }.get(form.engagement_type.data, form.engagement_type.data) or None
    submission = ContactSubmission(
        submission_id=submission_id,
        name=form.name.data,
        email=''.join(form.email.data.split()).lower(),
        engagement_type=engagement,
        message=form.message.data,
        spam_context={
            'honeypot': form.website.data or '',
            'elapsedSeconds': max(0, int(time.time()) - state['created_at']),
            'challengeToken': request.form.get('cf-turnstile-response', '')[:2048],
        },
    )
    fingerprint = _contact_submission_fingerprint(submission)
    if state['fingerprint'] and state['fingerprint'] != fingerprint:
        return _contact_form_response(
            form,
            'Please refresh the page and try again.',
            400,
        )
    if not state['fingerprint']:
        state['fingerprint'] = fingerprint
        states[submission_id] = state
        _store_contact_submission_states(states)

    timeout_seconds = current_app.config[
        'CONTACT_DELIVERY_TIMEOUT_SECONDS'
    ]

    if not state['delivered']:
        source = _contact_source_identity() if current_app.config['CONTACT_ADMISSION_ENABLED'] else None
        # An unavailable identity must not turn every visitor into one shared bucket.
        # The delivery broker retains its independent controls on every request.
        if source is not None:
            try:
                admitted = _contact_admission_store().admit(source)
            except ContactAdmissionError as error:
                current_app.logger.warning(
                    'Contact admission unavailable for submission %s: %s',
                    submission_id,
                    error,
                )
                return _contact_form_response(
                    form,
                    'Message delivery is temporarily unavailable. Please try again later.',
                    503,
                )

            if not admitted:
                current_app.logger.warning(
                    'contact_spam_decision ruleId=source_rate timestamp=%s count=1',
                    int(time.time()),
                )
                return _contact_form_response(
                    form,
                    'Your submission could not be accepted. Please try again later.',
                    429,
                )

        try:
            deliver_contact_submission(
                submission,
                broker_url=current_app.config['CONTACT_BROKER_URL'],
                secret=current_app.config['CONTACT_BROKER_SECRET'],
                timeout_seconds=timeout_seconds,
            )
            state['delivered'] = True
            states[submission_id] = state
            _store_contact_submission_states(states)
        except ContactFiltered as error:
            return _contact_form_response(
                form,
                ('Please complete the verification and submit again.' if error.challenge
                 else 'Your submission could not be accepted. Please try again later.'),
                error.status,
                challenge=error.challenge,
            )
        except ContactDeliveryError as error:
            current_app.logger.warning(
                'Contact delivery failed for submission %s: %s',
                submission_id,
                error,
            )
            return _contact_form_response(
                form,
                'The message could not be sent right now. Please try again.',
                502,
            )

    if request.accept_mimetypes.best == 'application/json':
        return jsonify(
            {
                'ok': True,
                'message': 'Thanks — your message has been sent.',
                'submission_id': _new_contact_submission(),
            }
        )

    flash('Thanks — your message has been sent.', 'contact-success')
    return redirect(url_for('index.index') + '#contact')


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
    """Publish the homepage, services, blog, and every article."""
    namespace = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ElementTree.register_namespace('', namespace)
    urlset = ElementTree.Element(f'{{{namespace}}}urlset')

    site_url = _site_url()
    if site_url:
        paths = (
            ['/', '/for-teams/', '/for-professionals/', '/newsletter/'] + [f'/services/{slug}' for slug in SERVICES]
            + ['/blog/']
            + [f"/blog/{article['slug']}/" for article in ARTICLES]
        )
        for path in paths:
            url_element = ElementTree.SubElement(urlset, f'{{{namespace}}}url')
            location = ElementTree.SubElement(url_element, f'{{{namespace}}}loc')
            location.text = f'{site_url}{path}'

    document = ElementTree.tostring(
        urlset,
        encoding='utf-8',
        xml_declaration=True,
    )
    return Response(document, mimetype='application/xml')


@index_bp.route('/rss.xml')
def rss():
    """Publish article summaries using canonical links and stable identities."""
    site_url = _site_url()
    if not site_url:
        abort(503)

    atom = 'http://www.w3.org/2005/Atom'
    ElementTree.register_namespace('atom', atom)
    root = ElementTree.Element('rss', version='2.0')
    channel = ElementTree.SubElement(root, 'channel')
    for name, value in (
        ('title', 'The Business of Technology by Tera Earlywine'),
        ('link', f'{site_url}/blog/'),
        ('description', BLOG_DESCRIPTION),
        ('language', 'en-us'),
    ):
        ElementTree.SubElement(channel, name).text = value
    ElementTree.SubElement(channel, f'{{{atom}}}link', {
        'href': f'{site_url}/rss.xml', 'rel': 'self',
        'type': 'application/rss+xml',
    })
    # Articles are appended to the collection. Publish newest first.
    for article in reversed(ARTICLES):
        item = ElementTree.SubElement(channel, 'item')
        article_url = f"{site_url}/blog/{article['slug']}/"
        for name, value in (
            ('title', article['title']), ('link', article_url),
            ('description', article['dek']), ('category', article['category']),
        ):
            ElementTree.SubElement(item, name).text = value
        ElementTree.SubElement(item, 'guid', isPermaLink='true').text = article_url

    response = Response(
        ElementTree.tostring(root, encoding='utf-8', xml_declaration=True),
        mimetype='application/rss+xml',
    )
    response.cache_control.public = True
    response.cache_control.max_age = 300
    response.add_etag()
    return response.make_conditional(request)


@index_bp.route('/for-teams/')
def for_teams():
    return render_template(
        'home/for_teams.html',
        page_title='Data & AI Consulting for Teams | Tera Earlywine',
        page_description=(
            'Get help with data and reporting, practical AI and workflow '
            'automation, and data and AI projects that need to move forward.'
        ),
    )


@index_bp.route('/for-professionals/')
def for_professionals():
    return render_template(
        'home/for_professionals.html',
        page_title='From Technical Work to Business Decisions | Tera Earlywine',
        page_description=(
            'Try a short exercise in explaining technical trade-offs. Use a real '
            'decision, a net-sales demo, and a three-sentence recommendation.'
        ),
    )


@index_bp.route('/blog/subscribe/')
def rss_subscription():
    """Help visitors add the RSS feed to their preferred reader."""
    return render_template(
        'home/rss_subscription.html',
        page_title='Subscribe via RSS | Tera Earlywine',
        page_description=(
            'Follow Tera Earlywine’s field notes on data, AI at work, and technology '
            'investment decisions in your RSS reader.'
        ),
    ), 200 if _site_url() else 503


@index_bp.route('/blog/')
def blog():
    """Explore the growing collection of essays and notes."""
    stack_articles = [
        {
            **{key: article[key] for key in (
                'id', 'slug', 'title', 'category', 'dek', 'read_minutes',
            )},
            'url': url_for('index.blog_article', slug=article['slug']),
        }
        for article in ARTICLES
    ]
    return render_template(
        'home/blog_index.html',
        articles=ARTICLES,
        featured_articles=FEATURED_ARTICLES,
        stack_articles=stack_articles,
        is_blog=True,
        page_title='The Business of Technology | Tera Earlywine',
        page_description=BLOG_DESCRIPTION,
    )


@index_bp.route('/blog/<slug>/')
def blog_article(slug):
    """Read one article and its recommended next step."""
    article = ARTICLES_BY_SLUG.get(slug)
    if article is None:
        abort(404)
    kind, target = article['next_step']
    if kind == 'article':
        next_step = {
            'heading': 'Read next',
            'label': ARTICLES_BY_SLUG[target]['title'],
            'url': url_for('index.blog_article', slug=target),
            'destination': 'writing',
        }
    elif kind == 'service':
        destination = {
            WAREHOUSE_DIAGNOSTIC_SLUG: 'diagnostic',
            'production-ai-systems': 'ai_workflow_review',
            'data-migration-rescue': 'migration_cutover',
        }.get(target, 'service')
        next_step = {
            'heading': 'Get help with this',
            'label': SERVICES[target]['name'],
            'url': url_for('index.service', slug=target),
            'destination': destination,
        }
    elif kind == 'demo':
        next_step = {
            'heading': 'Try it yourself',
            'label': 'Try the net-sales demo',
            'url': url_for('index.for_professionals', _anchor=target),
            'destination': 'net_sales_demo',
        }
    elif kind == 'download':
        next_step = {
            'heading': 'Review your own workflow',
            'description': 'Use this free worksheet to find gaps and assign a next action before release. No email required.',
            'label': 'Download the readiness scorecard',
            'url': url_for('index.static', filename=target),
            'destination': 'resource',
            'download': True,
        }
    else:
        raise ValueError(f'Unknown next-step kind: {kind}')
    return render_template(
        'home/blog_article.html',
        article=article,
        next_step=next_step,
        is_blog=True,
        page_title=f"{article['title']} | Tera Earlywine",
        page_description=article['dek'],
    )


@index_bp.route('/services/<slug>')
def service(slug):
    service = SERVICES.get(slug)
    if not service:
        abort(404)
    return render_template(
        'home/service.html',
        service=service,
        service_slug=slug,
        inquiry_url=url_for('index.index', topic=slug, _anchor='contact'),
        page_title=service['title'],
        page_description=service['description'],
    )


@index_bp.route("/about-me")
def about_me():
    """
    Redirect to experience section on homepage.
    """
    return redirect(url_for('index.index') + '#experience', code=301)
