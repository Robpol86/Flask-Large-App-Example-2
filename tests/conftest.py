import xmlrpclib

import pytest

from github_status.application import create_app, get_config
from github_status.extensions import db


class FakeServerProxy(object):
    VALUE = None

    def __init__(self, _):
        pass

    def search(self, _):
        return self.VALUE


@pytest.fixture(autouse=True, scope='session')
def create_all():
    """Create all database tables."""
    db.create_all()


# Initialize the application and sets the app context to avoid needing 'with app.app_context():'.
# This must happen before any Celery tasks are imported automatically by py.test during test discovery.
create_app(get_config('github_status.config.Testing')).app_context().push()
