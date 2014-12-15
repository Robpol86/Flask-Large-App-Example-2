from flask import render_template

from github_status.blueprints import repos_index


@repos_index.route('/')
def index():
    return render_template('repos_index.html')
