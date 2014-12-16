import string
import time

from flask import abort, jsonify, request
import json
import requests

from github_status.blueprints import api_query_github
from github_status.extensions import db
from github_status.models.helpers import count
from github_status.models.repositories import Repository

VALID_CHARACTERS = string.ascii_letters + string.digits + '/_-'


class APIError(Exception):
    pass


def get_committers_details(repo_url):
    """Queries GitHub API for the last commit message and the top 3 committers (within 50 most recent commits).

    Raises:
    APIError -- raised on handled API errors.

    Positional arguments:
    repo_url -- the author and project names, part of the url (e.g. Robpol86/colorclass).

    Returns:
    Tuple, first item is a set of top 3 committers, second item is a string of the latest commit message.
    """
    # Query API.
    req = requests.get('https://localhost/repos/{}/commits'.format(repo_url))
    if not req.ok:
        raise APIError('Invalid GitHub URL specified.')
    try:
        json_data = json.loads(req.text)
    except ValueError:
        raise APIError('GitHub responded with invalid JSON.')
    if not json_data:
        raise APIError('GitHub responded with empty JSON.')

    # Get last commit details and top 3 committers.
    last_commit_message = json_data[0].get('commit', {}).get('message', '')
    last_fifty = [a for a in (c.get('author', {}).get('login', '') for c in json_data[:50]) if a]
    top_three = set()
    for author in sorted(last_fifty, key=last_fifty.count, reverse=True):
        top_three.add(author)
        if len(top_three) >= 3:
            break
    return top_three, last_commit_message


def get_line_count(repo_url):
    """Queries GitHub API for the entire repo's code base line count.

    Raises:
    APIError -- raised on handled API errors.

    Positional arguments:
    repo_url -- the author and project names, part of the url (e.g. Robpol86/colorclass).

    Returns:
    Integer representing the total line count.
    """
    # Query API. GitHub API docs state HTTP202 may be returned if data is not generated yet. Retries up to 3 seconds.
    req = None
    for i in xrange(3):
        if i:
            time.sleep(1)  # Sleep on second and third iterations.
        req = requests.get('https://localhost/repos/{}/stats/contributors'.format(repo_url))
        if req.status_code == 202:
            continue
        if not req.ok:
            raise APIError('Invalid GitHub URL specified.')
        break
    if req.status_code == 202:
        raise APIError('GitHub still generating data, try again later.')
    try:
        json_data = json.loads(req.text)
    except ValueError:
        raise APIError('GitHub responded with invalid JSON.')
    if not json_data:
        raise APIError('GitHub responded with empty JSON.')

    line_count = 0
    for contributor in json_data:
        for week in contributor.get('weeks', []):
            line_count += week.get('a', 0)
            line_count += -1 * week.get('d', 0)
    return line_count


@api_query_github.route('/', defaults=dict(add_repo=True), strict_slashes=False, methods=('POST',))
@api_query_github.route('/update', defaults=dict(add_repo=False), strict_slashes=False, methods=('POST',))
def query(add_repo):
    """Queries GitHub's API for metadata about the repo.

    Positional arguments:
    add_repo -- checks for repo_url collisions if True, otherwise checks for invalid repo_urls if False.

    Returns:
    JSON encoded success boolean and error message if any.
    """
    # Verify POST data.
    repo_url = request.form.get('repo_url')
    if not repo_url:
        return abort(400)
    if repo_url.count('/') != 1:
        return jsonify(success=False, error='Invalid GitHub URL, must have only one slash.')
    for letter in repo_url:
        if letter not in VALID_CHARACTERS:
            return jsonify(success=False, error='Invalid GitHub URL, invalid character(s) found.')

    # Verify add/update request.
    if add_repo and count(Repository.url, repo_url):
        return jsonify(success=False, error='Repository already tracked, cannot add.')
    elif not add_repo and not count(Repository.url, repo_url):
        return jsonify(success=False, error='Repository not being tracked, cannot update.')

    # Query for repo metadata.
    try:
        top_three, last_commit_message = get_committers_details(repo_url)
        line_count = get_line_count(repo_url)
    except APIError as e:
        return jsonify(success=False, error=str(e))
    top_three_str = ' '.join(sorted(top_three))

    # Add to database.
    payload = dict(url=repo_url, line_count=line_count, top_committers=top_three_str, last_commit=last_commit_message)
    if add_repo:
        db.session.add(Repository(**payload))
    else:
        row = db.session.query(Repository).filter_by(url=repo_url)
        row.update(payload)
    db.session.commit()
    return jsonify(success=True, error='')
