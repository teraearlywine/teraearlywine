"""Distributed admission control for outbound contact delivery.

The bucket contains no raw network address. Datastore TTL may remove expired
ContactAdmissionRate entities, but expiry is enforced when each bucket is read.
"""
from datetime import datetime, timedelta, timezone
import hmac

from google.api_core import exceptions, retry
from google.auth.exceptions import GoogleAuthError
from google.cloud import datastore


ADMISSION_PERIOD = timedelta(minutes=15)
SOURCE_LIMIT = 5
RETRY_CONFLICT = retry.Retry(
    predicate=retry.if_exception_type(
        exceptions.Aborted,
        exceptions.Conflict,
    ),
    initial=0.05,
    maximum=0.4,
    timeout=4,
)


class ContactAdmissionError(RuntimeError):
    """Indicate that admission could not be established safely."""


def _now():
    return datetime.now(timezone.utc)


def get_datastore_client(project):
    if not project:
        raise ContactAdmissionError('missing_datastore_project')
    try:
        return datastore.Client(project=project, _use_grpc=False)
    except (exceptions.GoogleAPIError, GoogleAuthError, ValueError) as error:
        raise ContactAdmissionError('admission_store_unavailable') from error


class ContactAdmissionStore:
    """Reserve a bounded number of broker calls for one trusted source."""

    def __init__(self, project, secret):
        if not secret:
            raise ContactAdmissionError('missing_admission_secret')
        self.client = get_datastore_client(project)
        self.secret = secret.encode() if isinstance(secret, str) else secret

    def _source_key(self, source):
        digest = hmac.digest(
            self.secret,
            f'contact-source\0{source}'.encode('utf-8'),
            'sha256',
        ).hex()
        return self.client.key('ContactAdmissionRate', digest)

    def admit(self, source):
        """Debit one source bucket before an outbound broker attempt."""
        key = self._source_key(source)

        @RETRY_CONFLICT
        def transact():
            now = _now()
            with self.client.transaction() as transaction:
                bucket = self.client.get(key, transaction=transaction)
                if bucket is None:
                    bucket = datastore.Entity(key)
                    bucket.update(count=0, expires_at=now + ADMISSION_PERIOD)
                else:
                    expires_at = bucket.get('expires_at')
                    count = bucket.get('count')
                    if (
                        not isinstance(expires_at, datetime)
                        or not isinstance(count, int)
                        or isinstance(count, bool)
                        or count < 0
                    ):
                        raise ContactAdmissionError('invalid_admission_state')
                    if expires_at <= now:
                        bucket.update(
                            count=0,
                            expires_at=now + ADMISSION_PERIOD,
                        )

                if bucket['count'] >= SOURCE_LIMIT:
                    return False

                bucket['count'] += 1
                transaction.put(bucket)
                return True

        try:
            return transact()
        except ContactAdmissionError:
            raise
        except (exceptions.GoogleAPIError, GoogleAuthError, ValueError) as error:
            raise ContactAdmissionError('admission_store_unavailable') from error
