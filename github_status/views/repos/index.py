from flask import render_template

from github_status.blueprints import repos_index
from github_status.extensions import db
from github_status.models.repositories import Repository


@repos_index.route('/')
def index():
    table_rows = list()
    for row in db.session.query(Repository.url, Repository.top_committers, Repository.last_commit):
        last_commit = row[2].splitlines()[0][:80]
        table_rows.append(dict(url=row[0], top_committers=row[1].split(' '), last_commit=last_commit))
    return render_template('repos_index.html', table_rows=table_rows)
