from flask import Response

from github_status.blueprints import api_health


@api_health.route('/', strict_slashes=False)
def index():
    return Response('Running', content_type='text/plain;charset=UTF-8')
