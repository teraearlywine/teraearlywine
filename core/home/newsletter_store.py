"""Confirmed newsletter subscriptions in the default Datastore database.

NewsletterSubscriber.expires_at is set only on never-confirmed pending signups.
NewsletterSignupRate.expires_at is the end of each one-hour bucket. Both fields
are suitable for Datastore TTL; authorization and rate checks enforce expiry
even before asynchronous deletion. Subscriber keys and IP bucket keys use HMAC.
"""
from datetime import datetime, timedelta, timezone
from functools import lru_cache
import hmac
import re
import secrets

from email_validator import EmailNotValidError, validate_email
from google.api_core import exceptions, retry
from google.cloud import datastore

GUIDES = {
    'teams': ('teams',),
    'professionals': ('professionals',),
    'both': ('teams', 'professionals'),
}
CONFIRMATION_TTL = timedelta(hours=24)
RESEND_DELAY = timedelta(minutes=10)
RATE_PERIOD = timedelta(hours=1)
ADDRESS_LIMIT = 6
IP_LIMIT = 20
GLOBAL_LIMIT = 200
TOKEN = re.compile(r'([a-f0-9]{64})\.[A-Za-z0-9_-]{43}')
PRIVATE_FIELDS = ('email', 'pending_token', 'request_id', 'confirmed_token', 'unsubscribe_token')
PENDING_FIELDS = ('pending_token', 'pending_guide', 'pending_until', 'sent_at', 'request_id')
RETRY_CONFLICT = retry.Retry(
    predicate=retry.if_exception_type(exceptions.Conflict),
    initial=0.05, maximum=0.4, timeout=4,
)


@lru_cache(maxsize=4)
def get_datastore_client(project):
    """The HTTP transport shares Requests' certifi trust store with the site."""
    if not project:
        raise ValueError('Missing newsletter Datastore project')
    return datastore.Client(project=project, _use_grpc=False)


def _now():
    return datetime.now(timezone.utc)


def _token(key_name):
    return f'{key_name}.{secrets.token_urlsafe(32)}'


def _clear(record, fields):
    for field in fields:
        record.pop(field, None)


def _matches(record, field, candidate):
    return bool(record and hmac.compare_digest(record.get(field, ''), candidate))


def _pending(record, token, now):
    return _matches(record, 'pending_token', token) and now < record['pending_until']


def _confirmed(record, token):
    return _matches(record, 'confirmed_token', token) and record['state'] == 'active'


class SubscriberStore:
    def __init__(self, project, secret):
        if not secret:
            raise ValueError('Missing newsletter key secret')
        self.client = get_datastore_client(project)
        self.secret = secret.encode() if isinstance(secret, str) else secret

    def _hash(self, category, value):
        return hmac.digest(self.secret, f'{category}\0{value}'.encode(), 'sha256').hex()

    def _subscriber_key(self, token):
        match = TOKEN.fullmatch(token) if isinstance(token, str) else None
        return self.client.key('NewsletterSubscriber', match[1]) if match else None

    def reserve(self, email, guide, ip):
        if guide not in GUIDES or not isinstance(email, str) or len(email) > 254:
            return None
        try:
            address = validate_email(email.strip(), check_deliverability=False).normalized.lower()
        except EmailNotValidError:
            return None
        subscriber_key = self.client.key('NewsletterSubscriber', self._hash('address', address))
        ip_bucket = self.client.key('NewsletterSignupRate', self._hash('ip', ip or 'unknown'))
        global_bucket = self.client.key('NewsletterSignupRate', 'global')
        limits = ((ip_bucket, IP_LIMIT), (global_bucket, GLOBAL_LIMIT))

        @RETRY_CONFLICT
        def transact():
            now = _now()
            with self.client.transaction() as tx:
                rows = {row.key: row for row in self.client.get_multi(
                    [subscriber_key, ip_bucket, global_bucket], transaction=tx,
                )}
                record = rows.get(subscriber_key)
                if record is None:
                    record = datastore.Entity(subscriber_key, exclude_from_indexes=PRIVATE_FIELDS)
                    record.update(state='pending', email=address, audiences=[])

                if record.get('pending_guide') == guide and now < record['pending_until']:
                    if not record.get('sent_at'):
                        # Concurrent calls and ambiguous provider outcomes must use the same
                        # token and provider idempotency key until acceptance is recorded.
                        return self._delivery(record)
                    if now - record['sent_at'] < RESEND_DELAY:
                        return None
                if (record.get('confirmed_guide') == guide and record.get('confirmed_sent_at')
                        and now - record['confirmed_sent_at'] < RESEND_DELAY):
                    return None

                if record.get('rate_until', now) <= now:
                    record.update(rate_until=now + RATE_PERIOD, rate_count=0)
                if record.get('rate_count', 0) >= ADDRESS_LIMIT:
                    return None
                buckets = []
                for key, limit in limits:
                    bucket = rows.get(key)
                    if bucket is None or bucket['expires_at'] <= now:
                        bucket = datastore.Entity(key)
                        bucket.update(count=0, expires_at=now + RATE_PERIOD)
                    if bucket['count'] >= limit:
                        return None
                    buckets.append(bucket)
                for bucket in buckets:
                    bucket['count'] += 1
                    tx.put(bucket)

                record.update(rate_count=record.get('rate_count', 0) + 1,
                              pending_guide=guide, pending_until=now + CONFIRMATION_TTL,
                              pending_token=_token(subscriber_key.name), request_id=secrets.token_hex(16))
                record.pop('sent_at', None)
                if record['state'] == 'pending':
                    record['expires_at'] = record['pending_until']
                tx.put(record)
                return self._delivery(record)

        return transact()

    @staticmethod
    def _delivery(record):
        return dict(email=record['email'], guide=record['pending_guide'],
                    token=record['pending_token'], request_id=record['request_id'])

    def inspect(self, token):
        key = self._subscriber_key(token)
        if key:
            record = self.client.get(key)
            if _pending(record, token, _now()):
                return record['pending_guide']
            if _confirmed(record, token):
                return record['confirmed_guide']
        return None

    def is_unsubscribe_token(self, token):
        key = self._subscriber_key(token)
        return bool(key and _matches(self.client.get(key), 'unsubscribe_token', token))

    @RETRY_CONFLICT
    def mark_sent(self, token):
        key = self._subscriber_key(token)
        if not key:
            return False
        with self.client.transaction() as tx:
            record = self.client.get(key, transaction=tx)
            now = _now()
            if _pending(record, token, now):
                field = 'sent_at'
            elif _confirmed(record, token):
                # A recipient can open the email before its sender records acceptance.
                field = 'confirmed_sent_at'
            else:
                return False
            if record.get(field):
                return False
            record[field] = now
            tx.put(record)
        return True

    def confirm(self, token):
        guide, _ = self.confirm_with_status(token)
        return guide

    @RETRY_CONFLICT
    def confirm_with_status(self, token):
        key = self._subscriber_key(token)
        if not key:
            return None, False
        with self.client.transaction() as tx:
            record = self.client.get(key, transaction=tx)
            now = _now()
            if _confirmed(record, token):
                return record['confirmed_guide'], False
            if not _pending(record, token, now):
                return None, False
            guide = record['pending_guide']
            became_active = record['state'] != 'active'
            if became_active:
                record.update(confirmed_at=now, audiences=[], unsubscribe_token=_token(key.name))
            record.update(state='active', confirmed_token=token, confirmed_guide=guide,
                          audiences=sorted(set(record['audiences']).union(GUIDES[guide])))
            record.pop('confirmed_sent_at', None)
            if record.get('sent_at'):
                record['confirmed_sent_at'] = record['sent_at']
            _clear(record, PENDING_FIELDS + ('expires_at', 'unsubscribed_at'))
            tx.put(record)
            return guide, became_active

    def unsubscribe(self, token):
        valid, _ = self.unsubscribe_with_status(token)
        return valid

    @RETRY_CONFLICT
    def unsubscribe_with_status(self, token):
        key = self._subscriber_key(token)
        if not key:
            return False, False
        with self.client.transaction() as tx:
            record = self.client.get(key, transaction=tx)
            if not _matches(record, 'unsubscribe_token', token):
                return False, False
            # Repeat clicks on a previously completed opt-out do not invalidate a
            # subsequent resubscription request. Reconfirmation rotates this token.
            if record['state'] == 'unsubscribed':
                return True, False
            record.update(state='unsubscribed', audiences=[], unsubscribed_at=_now())
            _clear(record, PENDING_FIELDS + ('confirmed_token', 'confirmed_guide',
                                            'confirmed_sent_at', 'confirmed_at', 'expires_at'))
            tx.put(record)
            return True, True
