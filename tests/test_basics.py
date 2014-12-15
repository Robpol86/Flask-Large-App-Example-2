"""Test basic things such as that the front page (aka "index.html") returns HTTP 200.

Just a basic test to make sure the front page doesn't get an internal server error.
"""

import sys

from flask import current_app


def test_python_version():
    """Application runs under Python 2.7, not 2.6."""
    assert 2 == sys.version_info.major
    assert 7 == sys.version_info.minor


def test_testing_mode():
    """Most basic of tests: make sure TESTING = True in app.config."""
    assert current_app.config['TESTING']


def test_index_200():
    """Makes sure the front page returns HTTP 200.

    A very basic test, if the front page is broken, something has obviously failed.
    """
    assert '200 OK' == current_app.test_client().get('/').status
