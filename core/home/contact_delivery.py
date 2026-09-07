from dataclasses import dataclass
import hashlib
import hmac
import json
import time

import httpx


class ContactDeliveryError(RuntimeError):
    """Represent a broker failure without retaining its response or payload."""


@dataclass(frozen=True)
class ContactSubmission:
    submission_id: str
    name: str
    email: str
    engagement_type: str
    message: str


def _canonical_payload(submission):
    payload = {
        'email': submission.email,
        'engagementType': submission.engagement_type,
        'message': submission.message,
        'name': submission.name,
        'submissionId': submission.submission_id,
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(',', ':'),
    )
    return payload, canonical


def deliver_contact_submission(
    submission,
    *,
    broker_url,
    secret,
    timeout_seconds,
):
    """Send one HMAC-authenticated, replay-safe broker request."""
    payload, canonical = _canonical_payload(submission)
    timestamp = str(int(time.time()))
    signature = hmac.new(
        secret.encode('utf-8'),
        f'{timestamp}.{canonical}'.encode('utf-8'),
        hashlib.sha256,
    ).hexdigest()

    try:
        response = httpx.post(
            broker_url,
            headers={
                'Content-Type': 'application/json',
                'X-Contact-Signature': signature,
                'X-Contact-Timestamp': timestamp,
            },
            json=payload,
            timeout=timeout_seconds,
        )
        response.raise_for_status()
        receipt = response.json()
    except (httpx.HTTPError, ValueError) as error:
        raise ContactDeliveryError('broker_delivery_failed') from error

    if (
        not isinstance(receipt, dict)
        or receipt.get('submissionId') != submission.submission_id
        or not isinstance(receipt.get('replayed'), bool)
    ):
        raise ContactDeliveryError('broker_invalid_receipt')
