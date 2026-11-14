"""Preview a plain-text newsletter issue or deliver it to confirmed subscribers."""
import argparse
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
import logging
import os
from pathlib import Path
import re
import sys
from urllib.parse import quote, urlsplit

from google.api_core.exceptions import Aborted, GoogleAPICallError
from google.cloud import datastore
from google.cloud.datastore.query import PropertyFilter

from core.home.newsletter_mail import send_email
from core.home.newsletter_store import get_datastore_client
from core.secrets import load_secret


class IssueContentConflict(ValueError):
    """The operator reused a published edition's ID with changed content."""


@dataclass(frozen=True)
class Issue:
    slug: str
    subject: str
    body: str
    address: str
    sender: str
    site: str
    audience: str

    def fingerprint(self):
        return hashlib.sha256(json.dumps(asdict(self), sort_keys=True).encode()).hexdigest()

    def payload(self, email, token):
        unsubscribe = f'{self.site}/newsletter/unsubscribe/{quote(token, safe="")}'
        field_notes = (f'{self.site}/blog/?utm_source=newsletter&utm_medium=email'
                       '&utm_campaign=business_of_technology&utm_content=issue')
        return {
            'from': self.sender,
            'to': [email],
            'subject': self.subject,
            'text': (
                f'{self.body}\n\n— Tera Earlywine\n{self.address}\n\n'
                f'Read more field notes: {field_notes}\n'
                f'You subscribed to The Business of Technology.\nUnsubscribe: {unsubscribe}'
            ),
            'headers': {
                'List-Unsubscribe': f'<{unsubscribe}>',
                'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click',
            },
        }


def bind_issue(client, issue, now):
    key = client.key('NewsletterIssue', issue.slug)
    with client.transaction() as tx:
        record = client.get(key, transaction=tx)
        if record:
            if record['fingerprint'] != issue.fingerprint():
                raise IssueContentConflict('The issue ID already identifies different content, settings, or an audience.')
            return record['started_at']
        record = datastore.Entity(key)
        record.update(fingerprint=issue.fingerprint(), started_at=now)
        tx.put(record)
    return now


def claim_delivery(client, issue, subscriber_key, cutoff, now):
    delivery_key = client.key('NewsletterIssueDelivery', f'{issue.slug}.{subscriber_key.name}')
    with client.transaction() as tx:
        subscriber = client.get(subscriber_key, transaction=tx)
        if (not subscriber or subscriber.get('state') != 'active'
                or not subscriber.get('confirmed_at') or subscriber['confirmed_at'] > cutoff
                or (issue.audience != 'all' and issue.audience not in subscriber.get('audiences', []))):
            return 'ineligible', None
        record = client.get(delivery_key, transaction=tx)
        if record and record.get('provider_id'):
            return 'already accepted', None

        payload = issue.payload(subscriber['email'], subscriber['unsubscribe_token'])
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        if record:
            # A timed-out send may already have reached Resend. Leave a cushion
            # before its 24-hour idempotency retention ends; never replay after it.
            if now - record['first_attempt_at'] >= timedelta(hours=23):
                return 'needs review', None
            if record['payload_hash'] != digest:
                return 'needs review', None
            if now < record['lease_until']:
                return 'in progress', None
        else:
            record = datastore.Entity(delivery_key)
            record.update(issue=issue.slug, first_attempt_at=now, payload_hash=digest)
        record['lease_until'] = now + timedelta(minutes=2)
        tx.put(record)
    return 'ready', payload


def deliver_issue(client, issue, api_key):
    cutoff = bind_issue(client, issue, datetime.now(timezone.utc))
    query = client.query(kind='NewsletterSubscriber')
    query.add_filter(filter=PropertyFilter('state', '=', 'active'))
    query.keys_only()
    counts = Counter()
    for subscriber in query.fetch():
        try:
            state, payload = claim_delivery(
                client, issue, subscriber.key, cutoff, datetime.now(timezone.utc),
            )
        except Aborted:
            counts['in progress'] += 1
            continue
        if state != 'ready':
            counts[state] += 1
            continue

        name = f'{issue.slug}.{subscriber.key.name}'
        provider_id = send_email(api_key, payload, f'newsletter-issue/{name}')
        with client.transaction() as tx:
            record = client.get(client.key('NewsletterIssueDelivery', name), transaction=tx)
            record.update(provider_id=provider_id, accepted_at=datetime.now(timezone.utc))
            tx.put(record)
        counts['accepted'] += 1
    return counts


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--issue', required=True, help='Stable, unique ID such as 2026-12-cloud-bills')
    p.add_argument('--subject', required=True)
    p.add_argument('--body', required=True, type=Path, help='UTF-8 plain-text file')
    p.add_argument('--address', required=True, help='Business mailing address for the issue footer')
    p.add_argument('--audience', choices=['all', 'teams', 'professionals'], default='all')
    p.add_argument('--send', action='store_true', help='Deliver this edition to the selected audience')
    args = p.parse_args(argv)
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,79}', args.issue):
        p.error('--issue must contain 1–80 lowercase letters, numbers, or hyphens.')
    if not args.subject.strip() or any(c in args.subject for c in '\r\n'):
        p.error('--subject must be a nonempty single line.')
    site = os.environ.get('SITE_URL', 'https://www.teraearlywine.com').rstrip('/')
    url = urlsplit(site)
    if url.scheme != 'https' or not url.netloc or url.path or url.query or url.fragment or url.username:
        p.error('SITE_URL must be an HTTPS origin.')
    sender = os.environ.get('NEWSLETTER_FROM', '').strip()
    if not sender or not args.address.strip():
        p.error('Set NEWSLETTER_FROM to the verified sender and supply the business mailing address.')
    try:
        body = args.body.read_text(encoding='utf-8').strip()
    except OSError as error:
        p.error(str(error))
    if not body:
        p.error('--body is empty.')
    issue = Issue(args.issue, args.subject.strip(), body, args.address.strip(), sender, site, args.audience)
    if not args.send:
        payload = issue.payload('preview@example.com', 'preview')
        print(f'Preview · {issue.audience}\nFrom: {sender}\nSubject: {issue.subject}\n\n{payload["text"]}')
        return 0

    project = os.environ.get('GOOGLE_CLOUD_PROJECT', '').strip()
    if not project:
        p.error('Set GOOGLE_CLOUD_PROJECT to the website subscriber database project.')
    api_key = load_secret('RESEND_API_KEY', logging.getLogger(__name__))
    if not api_key:
        p.error('Configure RESEND_API_KEY_SECRET_ID or RESEND_API_KEY.')
    try:
        counts = deliver_issue(get_datastore_client(project), issue, api_key)
    except IssueContentConflict as error:
        print(str(error), file=sys.stderr)
        return 1
    except (ValueError, RuntimeError, GoogleAPICallError) as error:
        # Keep recipient addresses, tokens and raw provider errors out of the console.
        print('Delivery stopped. Rerun the identical edition after checking the provider '
              f'and database. Error type: {type(error).__name__}.', file=sys.stderr)
        return 1
    print('Delivery summary:', dict(counts))
    return 1 if counts['needs review'] or counts['in progress'] else 0


if __name__ == '__main__':
    sys.exit(main())
