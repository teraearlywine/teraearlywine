"""Offline regression checks for the October 2026 eMudhra distrust."""
import hashlib
import logging
from pathlib import Path
import ssl

import certifi
import google.auth
from google.auth.credentials import AnonymousCredentials
from google.cloud import secretmanager
import grpc
import httpx

from core.secrets import load_secret


# The compromised intermediates can chain through G3 and the AAA cross-sign.
# Check DER fingerprints, rather than certificate labels or package versions.
# https://github.com/certifi/python-certifi/releases/tag/2026.10.19
DISTRUSTED_ROOTS = {
    '86a1ecba089c4a8d3bbe2734c612ba341d813e043cf9e8a862cd5c57a36bbe6b',
    'd7a7a0fb5d7e2731d771e9484ebcdef71d5f0c3e0a2948782bc83ee0ea699ef4',
}


def _assert_distrusted(context):
    fingerprints = {
        hashlib.sha256(certificate).hexdigest()
        for certificate in context.get_ca_certs(binary_form=True)
    }
    assert fingerprints, 'TLS verification must retain a usable trust store'
    assert fingerprints.isdisjoint(DISTRUSTED_ROOTS)
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname


def test_httpx_default_trust_rejects_incident_roots(monkeypatch):
    # Deployment CA overrides must be checked separately; this exercises the
    # default used by the application's contact-delivery HTTPX call.
    monkeypatch.delenv('SSL_CERT_FILE', raising=False)
    monkeypatch.delenv('SSL_CERT_DIR', raising=False)
    _assert_distrusted(httpx.create_ssl_context())


def test_secret_manager_uses_patched_roots_with_application_credentials(monkeypatch):
    monkeypatch.delenv('TLS_TEST_SECRET', raising=False)
    monkeypatch.setenv('TLS_TEST_SECRET_SECRET_ID', 'test-secret')
    monkeypatch.setenv('GOOGLE_CLOUD_PROJECT', 'test-project')
    monkeypatch.setattr(
        google.auth, 'default',
        lambda **kwargs: (AnonymousCredentials(), 'test-project'),
    )
    captured = {}
    real_ssl_credentials = grpc.ssl_channel_credentials

    def ssl_credentials(root_certificates=None, **kwargs):
        captured['roots'] = root_certificates
        return real_ssl_credentials(root_certificates, **kwargs)

    def access_secret_version(client, request):
        captured['request'] = request
        captured['transport'] = client.transport
        return secretmanager.AccessSecretVersionResponse(
            payload=secretmanager.SecretPayload(data=b'local-test-value'),
        )

    monkeypatch.setattr(grpc, 'ssl_channel_credentials', ssl_credentials)
    monkeypatch.setattr(
        secretmanager.SecretManagerServiceClient,
        'access_secret_version', access_secret_version,
    )
    try:
        assert load_secret('TLS_TEST_SECRET', logging.getLogger(__name__)) == 'local-test-value'
        assert captured['request'] == {
            'name': 'projects/test-project/secrets/test-secret/versions/latest',
        }
        assert captured['roots'] == Path(certifi.where()).read_bytes()
        _assert_distrusted(ssl.create_default_context(cadata=captured['roots'].decode('ascii')))
        assert isinstance(captured['transport']._credentials, AnonymousCredentials)
    finally:
        if 'transport' in captured:
            captured['transport'].close()
