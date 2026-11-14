"""Transactional sender shared by opt-in and publisher-initiated editions."""
import httpx


def send_email(api_key, payload, idempotency_key):
    """Send without exposing recipient details or credentials in error messages."""
    try:
        response = httpx.post(
            'https://api.resend.com/emails',
            headers={'Authorization': f'Bearer {api_key}', 'Idempotency-Key': idempotency_key},
            json=payload,
            timeout=12,
        )
        if response.status_code not in (200, 201):
            raise RuntimeError(f'Newsletter mail provider returned {response.status_code}')
        message_id = response.json().get('id')
        if not isinstance(message_id, str) or not message_id:
            raise ValueError('missing receipt')
        return message_id
    except (httpx.HTTPError, ValueError, AttributeError):
        raise RuntimeError('Newsletter mail provider did not return a receipt') from None
