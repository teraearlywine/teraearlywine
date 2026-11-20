from html import unescape


def test_case_study_is_anonymized_and_sitemap_includes_it(app_factory):
    client = app_factory(SITE_URL='https://www.teraearlywine.com').test_client()
    response = client.get('/blog/audit-agent-proof-of-concept/')
    assert response.status_code == 200
    html = unescape(response.get_data(as_text=True))
    assert 'during an engagement, I designed an audit-agent proof of concept' in html
    assert 'Agents logged idempotent events from start-to-finish in a snowflake table' in html
    assert 'proof of concept, not a production deployment' in html
    assert 'Block' not in html and 'Qbiz' not in html
    assert 'staging runs' not in html
    assert 'https://www.teraearlywine.com/blog/audit-agent-proof-of-concept/' in html
    sitemap = client.get('/sitemap.xml').get_data(as_text=True)
    assert '/blog/audit-agent-proof-of-concept/' in sitemap
    assert '/blog/ai-workflow-production-evidence/' in sitemap


def test_article_connects_readiness_journey(app_factory):
    client = app_factory().test_client()
    html = unescape(client.get('/blog/ai-workflow-production-evidence/').get_data(as_text=True))
    assert 'This is an example, not a description of a client system.' in html
    assert 'downloads/data-ai-production-readiness-scorecard.pdf' in html
    assert 'data-analytics-event="resource_download"' in html
    assert 'No email required.' in html
    case_study = client.get('/blog/audit-agent-proof-of-concept/').get_data(as_text=True)
    assert 'class="blog-text-link essay-next-link" href="/blog/ai-workflow-production-evidence/"' in case_study
