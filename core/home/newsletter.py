"""Email signup, inbox confirmation, guide delivery, and unsubscribe."""
import os
from hmac import compare_digest

from flask import current_app, make_response, redirect, render_template, request, session, url_for
from flask_wtf import FlaskForm
from google.api_core.exceptions import GoogleAPIError
from google.auth.exceptions import GoogleAuthError
from wtforms import BooleanField, HiddenField, RadioField, StringField
from wtforms.validators import DataRequired, Email, Length, Optional

from core.home.home import index_bp
from core.home.newsletter_mail import send_email
from core.home.newsletter_store import SubscriberStore

GUIDES = {
    'teams': ('Choose Your Next AI Workflow', 'choose-your-next-ai-workflow.pdf'),
    'professionals': ('From Technical Work to Business Impact', 'from-technical-work-to-business-impact.pdf'),
}
SERVICE_ERRORS = (GoogleAPIError, GoogleAuthError, RuntimeError)


class SignupForm(FlaskForm):
    email = StringField('Email address', filters=[lambda s: s.strip() if s else s], validators=[
        DataRequired(message='Enter your email address.'), Length(max=254),
        Email(message='Enter a valid email address.', check_deliverability=False),
    ])
    guide = RadioField('Choose your guide', choices=[
        ('teams', GUIDES['teams'][0]), ('professionals', GUIDES['professionals'][0]),
        ('both', 'Both guides'),
    ], validators=[DataRequired()])
    consent = BooleanField('Subscribe to The Business of Technology', validators=[
        DataRequired(message='Check the box to subscribe and receive your guide.'),
    ])
    website = StringField('Website', validators=[Optional(), Length(max=0)])


class TokenForm(FlaskForm):
    token = HiddenField(validators=[DataRequired(), Length(max=200)])


def _store():
    if 'newsletter_store' not in current_app.extensions:
        current_app.extensions['newsletter_store'] = SubscriberStore(
            current_app.config['NEWSLETTER_PROJECT'], current_app.config['NEWSLETTER_IDENTITY_KEY'],
        )
    return current_app.extensions['newsletter_store']


def _response(template, status=200, *, private=True, **values):
    response = make_response(render_template(template, **values), status)
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Referrer-Policy'] = 'no-referrer'
    if private:
        response.headers['X-Robots-Tag'] = 'noindex, nofollow'
    return response


def _status(heading, message, code=200, **context):
    return _response('home/newsletter_status.html', code, heading=heading, message=message,
                     page_title=f'{heading} | Tera Earlywine', **context)


def _unavailable():
    return _status('Please try again', 'I couldn’t complete that request. Please try again in a few minutes.', 503)


def _invalid_link():
    return _status('This link has expired', 'Request a fresh confirmation email to get your guide.', 410, signup_link=True)


def _selection(guide):
    return list(GUIDES.values()) if guide == 'both' else [GUIDES[guide]]


def _send_confirmation(reservation):
    base = current_app.config['SITE_URL'].rstrip('/')
    link = base + url_for('index.newsletter_confirm', token=reservation['token'])
    titles = ' and '.join(title for title, _ in _selection(reservation['guide']))
    payload = {
        'from': current_app.config['NEWSLETTER_FROM'], 'to': [reservation['email']],
        'reply_to': current_app.config['CONTACT_EMAIL'],
        'subject': 'Confirm your email for The Business of Technology',
        'text': (f'You requested {titles} and my email newsletter, The Business of Technology.\n\n'
                 f'Open this link, then choose Confirm subscription to get your guide download:\n{link}\n\n'
                 'If you didn’t request this, you can ignore this email.\n\nTera Earlywine'),
    }
    send_email(current_app.config['RESEND_API_KEY'], payload, 'newsletter-optin-' + reservation['request_id'])


@index_bp.route('/newsletter/', methods=['GET', 'POST'])
def newsletter():
    choice = request.args.get('guide')
    form = SignupForm(guide=choice if choice in GUIDES else 'both')
    code = 200
    if form.validate_on_submit():
        if not all(current_app.config.get(key) for key in ('SITE_URL', 'RESEND_API_KEY', 'NEWSLETTER_FROM', 'NEWSLETTER_PROJECT', 'NEWSLETTER_IDENTITY_KEY')):
            return _unavailable()
        ip = request.remote_addr or 'unknown'
        if os.getenv('GAE_ENV') == 'standard':
            ip = request.headers.get('X-Appengine-User-Ip', ip)
        try:
            store = _store()
            session.pop('newsletter_signup_event', None)
            reservation = store.reserve(form.email.data, form.guide.data, ip)
            if reservation:
                _send_confirmation(reservation)
                if store.mark_sent(reservation['token']):
                    session['newsletter_signup_event'] = reservation['guide']
        except SERVICE_ERRORS as exc:
            current_app.logger.warning('Newsletter signup failed (%s)', type(exc).__name__)
            return _unavailable()
        return redirect(url_for('index.newsletter_pending'), code=303)
    if request.method == 'POST':
        code = 400
    return _response('home/newsletter.html', code, private=code != 200, form=form,
                     page_title='The Business of Technology Newsletter | Tera Earlywine',
                     page_description='Get Tera Earlywine’s field notes on data, AI, and business decisions. Subscribe and choose a free guide.')


@index_bp.get('/newsletter/check-email/')
def newsletter_pending():
    guide = session.pop('newsletter_signup_event', None)
    return _status('Check your inbox', 'Open the confirmation email from Tera Earlywine to complete your signup and download your guide. If you recently requested one, check your existing message and spam folder.',
                   analytics_safe_status=True, analytics_page_path='/newsletter/check-email/',
                   newsletter_event={'name': 'newsletter_signup', 'guide': guide} if guide else None)


def _valid_post(form, token):
    return form.validate_on_submit() and compare_digest(form.token.data.encode(), token.encode())


@index_bp.route('/newsletter/confirm/<token>', methods=['GET', 'POST'])
def newsletter_confirm(token):
    form = TokenForm(token=token)
    try:
        store = _store()
        if request.method == 'GET':
            if not store.inspect(token):
                return _invalid_link()
            return _status('Confirm your subscription', 'Confirm to join The Business of Technology and open the guide you requested.', form=form)
        if not _valid_post(form, token):
            return _status('Please reopen your link', 'Open the link from your confirmation email and try again.', 400)
        choice, activated = store.confirm_with_status(token)
        if not choice:
            return _invalid_link()
    except SERVICE_ERRORS:
        return _unavailable()
    session['newsletter_download_choice'] = choice
    session['newsletter_confirmation_event'] = activated
    return _receipt_redirect('index.newsletter_downloads')


def _receipt_redirect(endpoint):
    response = redirect(url_for(endpoint), code=303)
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['X-Robots-Tag'] = 'noindex, nofollow'
    return response


@index_bp.get('/newsletter/guides/')
def newsletter_downloads():
    choice = session.get('newsletter_download_choice')
    if choice not in (*GUIDES, 'both'):
        return redirect(url_for('index.newsletter'), code=303)
    guides = [{'key': key, 'title': title, 'url': url_for('index.static', filename=f'downloads/{filename}')}
              for key, (title, filename) in GUIDES.items() if choice in (key, 'both')]
    activated = session.pop('newsletter_confirmation_event', False)
    return _status('Your guides are ready' if len(guides) == 2 else 'Your guide is ready',
                   'Download your worksheet below and keep it for your next project.', guides=guides,
                   analytics_safe_status=True, analytics_page_path='/newsletter/guides/',
                   newsletter_event={'name': 'newsletter_confirm', 'guide': choice} if activated else None)


@index_bp.route('/newsletter/unsubscribe/<token>', methods=['GET', 'POST'])
def newsletter_unsubscribe(token):
    form = TokenForm(token=token)
    try:
        store = _store()
        if request.method == 'GET':
            if not store.is_unsubscribe_token(token):
                return _status('Link unavailable', 'Open the unsubscribe link in your latest newsletter.', 410)
            return _status('Unsubscribe from the newsletter', 'Choose Unsubscribe to stop future issues of The Business of Technology.', form=form, action_label='Unsubscribe')
        # RFC 8058 mail clients post the bearer URL without a browser session.
        one_click = request.form.get('List-Unsubscribe') == 'One-Click'
        if not one_click and not _valid_post(form, token):
            return _status('Please reopen your link', 'Open the unsubscribe link in your newsletter and try again.', 400)
        valid, changed = store.unsubscribe_with_status(token)
        if not valid:
            return _status('Link unavailable', 'Open the unsubscribe link in your latest newsletter.', 410)
    except SERVICE_ERRORS:
        return _unavailable()
    if one_click:
        response = make_response('', 200)
        response.headers.update({'Cache-Control': 'no-store', 'Referrer-Policy': 'no-referrer'})
        return response
    session['newsletter_unsubscribe_event'] = changed
    session.pop('newsletter_download_choice', None)
    session.pop('newsletter_confirmation_event', None)
    return _receipt_redirect('index.newsletter_unsubscribed')


@index_bp.get('/newsletter/unsubscribed/')
def newsletter_unsubscribed():
    if 'newsletter_unsubscribe_event' not in session:
        return redirect(url_for('index.newsletter'), code=303)
    changed = session.pop('newsletter_unsubscribe_event')
    return _status('You’re unsubscribed', 'You won’t receive further issues of The Business of Technology at this address.',
                   analytics_safe_status=True, analytics_page_path='/newsletter/unsubscribed/',
                   newsletter_event={'name': 'newsletter_unsubscribe'} if changed else None)
