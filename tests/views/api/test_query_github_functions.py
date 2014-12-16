import json
import os
import re

import httpretty
import pytest

from github_status.views.api.query_github import APIError, get_committers_details, get_line_count


@pytest.mark.httpretty
def test_get_committers_details_errors():
    httpretty.register_uri(httpretty.GET, re.compile('.*/commits'), responses=[
        httpretty.Response(body='', status=500),
        httpretty.Response(body='', status=200),
        httpretty.Response(body='{}', status=200),
    ])

    with pytest.raises(APIError) as e:
        get_committers_details('user/project')
    assert 'Invalid GitHub URL specified.' == e.value.message

    with pytest.raises(APIError) as e:
        get_committers_details('user/project')
    assert 'GitHub responded with invalid JSON.' == e.value.message

    with pytest.raises(APIError) as e:
        get_committers_details('user/project')
    assert 'GitHub responded with empty JSON.' == e.value.message


@pytest.mark.httpretty
def test_get_committers_details_partial():
    first_payload = json.dumps([{}])  # List of empty dicts.
    second_payload = json.dumps([dict(commit=dict(message='New setup.py.'))])  # No authors.
    third_payload = json.dumps([dict(author=dict(login='Myself'))])  # No commit messages.
    fourth_payload = json.dumps([dict(author=dict(login=u)) for u in 'abbcccdd'])  # Over 3 different contributors.
    httpretty.register_uri(httpretty.GET, re.compile('.*/commits'), responses=[
        httpretty.Response(body=first_payload, status=200),
        httpretty.Response(body=second_payload, status=200),
        httpretty.Response(body=third_payload, status=200),
        httpretty.Response(body=fourth_payload, status=200),
    ])

    assert (set(), '') == get_committers_details('user/project')
    assert (set(), 'New setup.py.') == get_committers_details('user/project')
    assert ({'Myself', }, '') == get_committers_details('user/project')
    assert ({'b', 'c', 'd'}, '') == get_committers_details('user/project')


@pytest.mark.httpretty
def test_get_committers_details_full():
    with open(os.path.join(os.path.dirname(__file__), 'example_commits.json')) as f:
        payload = f.read(110000)
    httpretty.register_uri(httpretty.GET, re.compile('.*/commits'), body=payload)

    expected = {'Robpol86', }, 'New setup.py, codecov.io, shields.io.\n\nNormalizing across all of my projects.'
    assert expected == get_committers_details('user/project')


@pytest.mark.httpretty
def test_get_line_count_errors():
    httpretty.register_uri(httpretty.GET, re.compile('.*/contributors'), responses=[
        httpretty.Response(body='', status=500),
        httpretty.Response(body='', status=200),
        httpretty.Response(body='{}', status=200),
    ])

    with pytest.raises(APIError) as e:
        get_line_count('user/project')
    assert 'Invalid GitHub URL specified.' == e.value.message

    with pytest.raises(APIError) as e:
        get_line_count('user/project')
    assert 'GitHub responded with invalid JSON.' == e.value.message

    with pytest.raises(APIError) as e:
        get_line_count('user/project')
    assert 'GitHub responded with empty JSON.' == e.value.message


@pytest.mark.httpretty
def test_get_line_count_202():
    httpretty.register_uri(httpretty.GET, re.compile('.*/contributors'), responses=[
        httpretty.Response(body='{}', status=202),
        httpretty.Response(body='{}', status=202),
        httpretty.Response(body='{}', status=202),  # GitHub still generating data, try again later.

        httpretty.Response(body='{}', status=202),
        httpretty.Response(body='{}', status=202),
        httpretty.Response(body='[{"weeks": [{"a": 1}]}]', status=200),

        httpretty.Response(body='{}', status=202),
        httpretty.Response(body='[{"weeks": [{"a": 2}]}]', status=200),
        httpretty.Response(body='{}', status=202),  # Should never reach.
    ])

    with pytest.raises(APIError) as e:
        get_line_count('user/project')
    assert 'GitHub still generating data, try again later.' == e.value.message

    assert 1 == get_line_count('user/project')

    assert 2 == get_line_count('user/project')


@pytest.mark.httpretty
def test_get_line_count_full():
    with open(os.path.join(os.path.dirname(__file__), 'example_contributors.json')) as f:
        payload = f.read(110000)
    httpretty.register_uri(httpretty.GET, re.compile('.*/contributors'), body=payload)

    assert 654 == get_line_count('user/project')
