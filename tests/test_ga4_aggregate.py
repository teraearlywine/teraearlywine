from datetime import date
import pytest
from scripts.ga4_aggregate import build_request, validate_response

START = date(2026, 11, 1)
END = date(2026, 11, 2)

def response():
    return {'dimensionHeaders': [{'name': x} for x in ('date', 'eventName', 'streamId', 'hostName')],
            'metricHeaders': [{'name': 'eventCount'}], 'rowCount': 1,
            'metadata': {'timeZone': 'America/Los_Angeles'},
            'rows': [{'dimensionValues': [{'value': x} for x in ('20261101', 'page_view', '15512913765', 'teraearlywine.com')],
                      'metricValues': [{'value': '3'}]}]}

def test_server_filters_before_return():
    r = build_request(START, END)
    filters = r['dimensionFilter']['andGroup']['expressions']
    assert [f['filter']['fieldName'] for f in filters] == ['streamId', 'hostName', 'eventName']
    assert filters[0]['filter']['stringFilter']['matchType'] == 'EXACT'
    assert r['limit'] == 1000

@pytest.mark.parametrize('end', [date(2026, 10, 31), date(2026, 11, 8)])
def test_bounded_window(end):
    with pytest.raises(ValueError): build_request(START, end)

def test_safe_output_source_dates_not_mislabeled_pacific():
    result = validate_response(response(), START, END)
    assert result == {'source_timezone': 'America/Los_Angeles', 'rows': [{'source_date': '2026-11-01', 'event_name': 'page_view', 'event_count': 3}]}

@pytest.mark.parametrize('index,value', [(0,'20261103'), (1,'email@example.com'), (2,'other'), (3,'other.example')])
def test_out_of_scope_rejected(index, value):
    r = response(); r['rows'][0]['dimensionValues'][index]['value'] = value
    with pytest.raises(ValueError): validate_response(r, START, END)

@pytest.mark.parametrize('metadata', [{'subjectToThresholding': True}, {'dataLossFromOtherRow': True}, {'samplingMetadatas': [{}]}])
def test_incomplete_fails(metadata):
    r = response(); r['metadata'].update(metadata)
    with pytest.raises(ValueError): validate_response(r, START, END)

def test_truncated_fails():
    r = response(); r['rowCount'] = 2
    with pytest.raises(ValueError): validate_response(r, START, END)

def test_schema_unexpected_fails():
    r = response(); r['dimensionHeaders'][0]['name'] = 'pageLocation'
    with pytest.raises(ValueError): validate_response(r, START, END)

def test_zero_results_has_timezone():
    r = response(); r['rowCount'] = 0; r['rows'] = []
    assert validate_response(r, START, END)['rows'] == []
