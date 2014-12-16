import json

from flask import current_app

from github_status.extensions import db
from github_status.models.repositories import Repository


def test_invalid_post_data():
    Repository.query.delete()
    db.session.commit()

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
    assert [] == Repository.query.all()
