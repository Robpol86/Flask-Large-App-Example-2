from flask import render_template

from github_status.blueprints import repos_details
from github_status.models.repositories import Repository


@repos_details.route('/<owner>/<project>')
def index(owner, project):
    repo_url = '{}/{}'.format(owner, project)
    row = Repository.query.filter_by(url=repo_url).first_or_404()
    return render_template('repos_details.html', url=row.url, line_count='{:,}'.format(row.line_count),
                           top_committers=row.top_committers.split(' '),
                           last_commit=row.last_commit.replace('\n', '<br>'))
