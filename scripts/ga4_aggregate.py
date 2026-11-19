"""Bounded, aggregate-only GA Data API contract; no network or warehouse writes.

Dates are PROPERTY dates, never silently relabeled as Pacific dates. The caller
must verify API compatibility/authorization and timezone before deployment.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

PROPERTY = 'properties/533228502'
STREAM = '15512913765'
HOSTS = ('teraearlywine.com', 'www.teraearlywine.com')
EVENTS = ('page_view', 'newsletter_cta_click', 'newsletter_guide_select',
          'newsletter_signup', 'newsletter_confirm', 'newsletter_guide_download',
          'newsletter_unsubscribe', 'resource_download', 'navigation_click',
          'outbound_click', 'contact_view', 'contact_click', 'contact_submit')
DIMENSIONS = ('date', 'eventName', 'streamId', 'hostName')


def build_request(start, end):
    if not 0 <= (end - start).days <= 6:
        raise ValueError('Report window must contain one to seven days')
    return {
        'dateRanges': [{'startDate': start.isoformat(), 'endDate': end.isoformat()}],
        'dimensions': [{'name': x} for x in DIMENSIONS],
        'metrics': [{'name': 'eventCount'}],
        'dimensionFilter': {'andGroup': {'expressions': [
            {'filter': {'fieldName': 'streamId', 'stringFilter': {
                'matchType': 'EXACT', 'value': STREAM, 'caseSensitive': True}}},
            {'filter': {'fieldName': 'hostName', 'inListFilter': {
                'values': list(HOSTS), 'caseSensitive': False}}},
            {'filter': {'fieldName': 'eventName', 'inListFilter': {
                'values': list(EVENTS), 'caseSensitive': True}}},
        ]}},
        'limit': 1000, 'returnPropertyQuota': True,
    }


def validate_response(data, start, end):
    """Fail closed on partial, unexpected or out-of-scope reports; strip fields."""
    build_request(start, end)
    if [x['name'] for x in data.get('dimensionHeaders', [])] != list(DIMENSIONS):
        raise ValueError('Unexpected dimensions')
    if [x['name'] for x in data.get('metricHeaders', [])] != ['eventCount']:
        raise ValueError('Unexpected metrics')
    meta = data.get('metadata', {})
    partial_keys = ('subjectToThresholding', 'dataLossFromOtherRow',
                    'samplingMetadatas')
    if any(meta.get(x) for x in partial_keys):
        raise ValueError('Incomplete or thresholded report')
    timezone = meta.get('timeZone')
    if not isinstance(timezone, str):
        raise ValueError('Missing source timezone')
    ZoneInfo(timezone)
    rows = data.get('rows', [])
    # At most seven dates x thirteen events x two exact hosts, one exact stream.
    if data.get('rowCount', 0) != len(rows) or len(rows) > 182:
        raise ValueError('Truncated or oversized report')
    totals, seen = {}, set()
    for row in rows:
        dims, metrics = row['dimensionValues'], row['metricValues']
        if len(dims) != 4 or len(metrics) != 1:
            raise ValueError('Unexpected row shape')
        raw_date, event, stream, host = (x['value'] for x in dims)
        day = datetime.strptime(raw_date, '%Y%m%d').date()
        if (not start <= day <= end or event not in EVENTS or stream != STREAM
                or host.lower() not in HOSTS):
            raise ValueError('Out-of-scope data')
        key = (day, event, host.lower())
        if key in seen:
            raise ValueError('Duplicate dimension row')
        seen.add(key)
        raw_count = metrics[0]['value']
        if not raw_count.isdigit() or len(raw_count) > 18:
            raise ValueError('Invalid event count')
        target = (day.isoformat(), event)
        totals[target] = totals.get(target, 0) + int(raw_count)
    return {'source_timezone': timezone, 'rows': [
        {'source_date': d, 'event_name': e, 'event_count': n}
        for (d, e), n in sorted(totals.items())]}
