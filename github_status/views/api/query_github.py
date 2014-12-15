import string

from flask import abort, jsonify, request
import json
import requests

from github_status.blueprints import api_query_github
from github_status.extensions import db
from github_status.models.helpers import count
from github_status.models.repositories import Repository

VALID_CHARACTERS = string.ascii_letters + string.digits + '/_-'


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
    repo_url_split = repo_url.split('/', 1)
    req = requests.get('https://localhost/repos/{}/{}/commits'.format(repo_url_split[0], repo_url_split[1]))
    if not req.ok:
        return jsonify(success=False, error='Invalid GitHub URL specified.')
    try:
        json_data = json.loads(req.text)
    except ValueError:
        return jsonify(success=False, error='GitHub responded with invalid JSON.')
    if not json_data:
        return jsonify(success=False, error='GitHub responded with invalid JSON.')

    # Get last commit details and top 3 committers.
    last_commit_message = json_data[0].get('commit', {}).get('message', '')
    last_fifty = [a for a in (c.get('author', {}).get('login', '') for c in json_data[:50]) if a]
    top_three = set()
    for author in sorted(last_fifty, key=last_fifty.count, reverse=True):
        top_three.add(author)
        if len(top_three) >= 3:
            break
    top_three_str = ' '.join(top_three)

    # Get line count.
    line_count = 0

    # Add to database.
    payload = dict(url=repo_url, line_count=line_count, top_committers=top_three_str, last_commit=last_commit_message)
    if add_repo:
        db.session.add(Repository(**payload))
    else:
        row = db.session.query(Repository).filter_by(url=repo_url)
        row.update(payload)
    db.session.commit()
    return jsonify(success=True, error='')
