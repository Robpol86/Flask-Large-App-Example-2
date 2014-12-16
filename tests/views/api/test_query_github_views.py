import json
import re

from flask import current_app
import httpretty
import pytest

from github_status.extensions import db
from github_status.models.repositories import Repository


@pytest.mark.httpretty
def test_invalid_post_data():
    Repository.query.delete()
    db.session.commit()

    httpretty.register_uri(httpretty.GET, re.compile('.*/commits'), body='', status=500)
    httpretty.register_uri(httpretty.GET, re.compile('.*/contributors'), body='', status=500)

    assert '405 METHOD NOT ALLOWED' == current_app.test_client().get('/api/query_github').status
    assert [] == Repository.query.all()

    assert '400 BAD REQUEST' == current_app.test_client().post('/api/query_github').status
    assert [] == Repository.query.all()

    with current_app.test_client() as c:
        resp = json.loads(c.post('/api/query_github', data=dict(repo_url='1/2/3')).data)
        assert resp['success'] is False
        assert 'Invalid GitHub URL, must have only one slash.' == resp['error']

        resp = json.loads(c.post('/api/query_github', data=dict(repo_url='1')).data)
        assert resp['success'] is False
        assert 'Invalid GitHub URL, must have only one slash.' == resp['error']

        resp = json.loads(c.post('/api/query_github', data=dict(repo_url='1/2#')).data)
        assert resp['success'] is False
        assert 'Invalid GitHub URL, invalid character(s) found.' == resp['error']

        resp = json.loads(c.post('/api/query_github', data=dict(repo_url='1/2')).data)
        assert resp['success'] is False
        assert 'Invalid GitHub URL specified.' == resp['error']
    assert [] == Repository.query.all()


@pytest.mark.httpretty
def test_add_data():
    httpretty.register_uri(httpretty.GET, re.compile('.*/commits'), status=200, body=json.dumps([
        {'author': {'login': 'Myself'}, 'commit': {'message': 'New setup.py.'}},
        {'author': {'login': 'You'}, 'commit': {'message': 'Old setup.py.'}},
    ]))
    httpretty.register_uri(httpretty.GET, re.compile('.*/contributors'), status=200, body='[{"weeks": [{"a": 1}]}]')

    assert '200 OK' == current_app.test_client().post('/api/query_github', data=dict(repo_url='1/2')).status
    expected = [('1/2', 1, 'Myself You', 'New setup.py.')]
    actual = db.session.query(Repository.url, Repository.line_count, Repository.top_committers,
                              Repository.last_commit).all()
    assert expected == actual


@pytest.mark.httpretty
def test_update_data():
    assert 1 == Repository.query.count()

    httpretty.register_uri(httpretty.GET, re.compile('.*/commits'), status=200, body=json.dumps([
        {'author': {'login': 'Myself'}, 'commit': {'message': 'Newer setup.py.'}},
        {'author': {'login': 'You2'}, 'commit': {'message': 'Old setup.py.'}},
    ]))
    httpretty.register_uri(httpretty.GET, re.compile('.*/contributors'), status=200, body='[{"weeks": [{"a": 2}]}]')

    assert '200 OK' == current_app.test_client().post('/api/query_github/update', data=dict(repo_url='1/2')).status
    expected = [('1/2', 2, 'Myself You2', 'Newer setup.py.')]
    actual = db.session.query(Repository.url, Repository.line_count, Repository.top_committers,
                              Repository.last_commit).all()
    assert expected == actual

    assert 1 == Repository.query.count()


def test_collisions_missing():
    assert 1 == Repository.query.count()

    with current_app.test_client() as c:
        resp = json.loads(c.post('/api/query_github', data=dict(repo_url='1/2')).data)
        assert resp['success'] is False
        assert 'Repository already tracked, cannot add.' == resp['error']

        resp = json.loads(c.post('/api/query_github/update', data=dict(repo_url='1/3')).data)
        assert resp['success'] is False
        assert 'Repository not being tracked, cannot update.' == resp['error']

    assert 1 == Repository.query.count()
