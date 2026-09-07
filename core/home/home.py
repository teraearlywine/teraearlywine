# Set up home blueprint
import hashlib
import time
import uuid
from urllib.parse import urlsplit, urlunsplit
from xml.etree import ElementTree

from flask import (
    Blueprint,
    Response,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from core.home.contact_delivery import (
    ContactDeliveryError,
    ContactSubmission,
    deliver_contact_submission,
)
from core.home.forms import ContactForm


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
FAQ_ITEMS = (
    {
        'question': 'Who is Tera Earlywine?',
        'answer': (
            'Tera Earlywine is an independent data and AI consultant with '
            '9+ years of experience building and modernizing enterprise data '
            'platforms across fintech, marketplaces, and regulated operations.'
        ),
    },
    {
        'question': 'What does Tera Earlywine do?',
        'answer': (
            'She helps enterprise teams stabilize data platforms, rescue '
            'migrations, build AI-ready data foundations, and move agentic AI '
            'workflows into reliable production services.'
        ),
    },
    {
        'question': 'Who does Tera work with?',
        'answer': (
            'Tera works with data, engineering, compliance, risk, and '
            'operations leaders—especially in fintech, B2B software, '
            'marketplaces, and other high-consequence environments.'
        ),
    },
    {
        'question': 'When should a company hire Tera?',
        'answer': (
            'Bring Tera in when a critical data platform is fragile, a '
            'migration is stalled, ownership is unclear, or an AI pilot needs '
            'the controls and infrastructure required for production.'
        ),
    },
    {
        'question': 'How does an engagement start?',
        'answer': (
            'It starts with a 20–30 minute fit call. If the problem is a match, '
            'the first engagement usually diagnoses the risk, defines the '
            'smallest useful path, and produces a concrete next decision.'
        ),
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


def _contact_form_response(form, message, status_code):
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
            }
        ), status_code

    safe_form = ContactForm(
        formdata=None,
        submission_id=_new_contact_submission(),
    )
    for field_name in ('name', 'email', 'engagement_type', 'message'):
        safe_form[field_name].errors = list(form.errors.get(field_name, ()))

    return render_template(
        'home/home.html',
        contact_form=safe_form,
        contact_error=message,
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
            submission.engagement_type,
            submission.message,
        )
    )
    return hashlib.sha256(private_payload.encode('utf-8')).hexdigest()


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
        service_id = f'{homepage_url}#professional-service'
        structured_data = {
            '@context': 'https://schema.org',
            '@graph': [
                {
                    '@type': 'Person',
                    '@id': person_id,
                    'name': 'Tera Earlywine',
                    'url': homepage_url,
                    'jobTitle': 'Independent Data & AI Consultant',
                    'description': (
                        'Enterprise data and AI consultant focused on '
                        'production-grade systems for regulated, '
                        'high-consequence operations.'
                    ),
                    'knowsAbout': [
                        'Production-grade data and AI for regulated, high-consequence operations',
                        'Data platform modernization',
                        'Data reliability',
                        'AI-ready data foundations',
                        'Agentic AI productionization',
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
                        'Production-grade data and AI consulting for regulated, '
                        'high-consequence operations.'
                    ),
                    'founder': {'@id': person_id},
                    'serviceType': [
                        'Data platform modernization',
                        'Reliability and migration rescue',
                        'AI-ready data foundations',
                        'Production AI systems',
                        'Fractional platform leadership',
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

    return {
        'canonical_url': homepage_url if is_homepage else '',
        'is_homepage': is_homepage,
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
    form = ContactForm(submission_id=_new_contact_submission())
    return render_template('home/home.html', contact_form=form)


@index_bp.post('/contact')
def contact():
    """Validate and deliver a website contact submission."""
    form = ContactForm()
    invalid_message = 'Please check the highlighted fields and try again.'
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

    submission = ContactSubmission(
        submission_id=submission_id,
        name=form.name.data,
        email=form.email.data,
        engagement_type=form.engagement_type.data,
        message=form.message.data,
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

    try:
        if not state['delivered']:
            deliver_contact_submission(
                submission,
                broker_url=current_app.config['CONTACT_BROKER_URL'],
                secret=current_app.config['CONTACT_BROKER_SECRET'],
                timeout_seconds=timeout_seconds,
            )
            state['delivered'] = True
            states[submission_id] = state
            _store_contact_submission_states(states)
    except ContactDeliveryError as error:
        current_app.logger.warning(
            'Contact delivery failed for submission %s: %s',
            submission_id,
            error,
        )
        return _contact_form_response(
            form,
            'We could not send your message right now. Please try again.',
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
