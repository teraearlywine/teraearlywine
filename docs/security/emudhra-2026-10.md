# eMudhra TLS trust-store remediation — 21 October 2026

The application pinned `certifi==2025.1.31`, whose CA bundle trusts both **emSign ECC Root CA - G3** and **AAA Certificate Services**. The compromised eMudhra intermediates can chain through these roots. A network-positioned attacker could impersonate an HTTPS upstream; an unaffected certificate on this website does not remove that outbound risk.

This change pins **certifi 2026.10.19** and supplies that bundle explicitly to the Google Secret Manager gRPC transport. Updating certifi alone is insufficient for gRPC: the freshly resolved `grpcio==1.84.0` wheel still includes G3 in its independent root bundle. ADC authentication and certificate/hostname verification remain enabled.

## Scope and impact

The source snapshot audited was `ec0ee4f842b3b3a70c7a3adcf08b48762c5b5684`:

- 149 tracked files; all 307 reachable commits and 14,335 distinct reachable blobs (237,574,072 bytes) from fetched branches/tags were searched for PEM material, certificate filenames, incident names, CA overrides, and certificate verification bypasses.
- No incident certificates or application private keys were found in the repository. Historical PEM/key matches are the vendored `selfsigned` package's public README examples: two `example.org` certificates and one `John Doe jdoe123` client certificate, expired in 2014/2016.
- Two current outbound TLS paths need the updated trust: HTTPX contact delivery and Secret Manager gRPC secret retrieval. The contact payload includes name, email, engagement type, message and spam context. The configured Secret Manager resources supply the application session key and contact broker signing secret.
- The old certifi wheel contains both incident-relevant roots; the replacement contains neither. Regression checks inspect parsed DER fingerprints and verify that hostname checks and `CERT_REQUIRED` remain enabled. The Secret Manager check constructs the real SDK transport with anonymous test credentials and intercepts the RPC locally; it makes no cloud request.
- No certificate-verification bypass or custom CA override was found in reachable source. No Git submodules or CI workflow files are present in the current tree.

These are source/dependency exposure findings, **not evidence that data was intercepted or that secrets were stolen**. The audit does not measure impacted users, messages or deployed instances. Reachable historical commits and old branches retain their original pins; do not redeploy them without this patch.

## Release and verification

After review, rebuild and redeploy the App Engine service from the patched revision, replacing stale instances/versions that still serve traffic. Check the deployed environment for `SSL_CERT_FILE`, `SSL_CERT_DIR`, `REQUESTS_CA_BUNDLE`, `CURL_CA_BUNDLE`, proxy trust configuration and independent runtime/OS bundles; none of their live values were inspected here. Confirm the installed certifi bundle omits both root fingerprints below, then smoke-test secret loading and contact delivery using approved test data. App Engine frontend certificates, provider runtime patching, developer machines, browser trust stores, and other services are separate from this repository change. This PR does not deploy or rotate secrets.

| Root | SHA-256 of DER certificate |
| --- | --- |
| emSign ECC Root CA - G3 | `86a1ecba089c4a8d3bbe2734c612ba341d813e043cf9e8a862cd5c57a36bbe6b` |
| AAA Certificate Services | `d7a7a0fb5d7e2731d771e9484ebcdef71d5f0c3e0a2948782bc83ee0ea699ef4` |

Sources: [certifi release](https://github.com/certifi/python-certifi/releases/tag/2026.10.19), [certifi G3 removal](https://github.com/certifi/python-certifi/commit/5cb238caeeb6c30ec1a7309ad3e16a5aa7b10ce8), [restoration of unaffected roots](https://github.com/certifi/python-certifi/commit/662df63d7906df66f1f07c0751a3dfe9da14d914), [Cloudflare incident notice](https://blog.cloudflare.com/emudhra-certificate-compromise/), [gRPC explicit root API](https://grpc.github.io/grpc/python/grpc.html#grpc.ssl_channel_credentials).
