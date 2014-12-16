"""All Flask blueprints for the entire application.

All blueprints for all views go here. They shall be imported by the views themselves and by application.py. Blueprint
URL paths are defined here as well.
"""

from flask import Blueprint


def _factory(partial_module_string, url_prefix):
    """Generates blueprint objects for view modules.

    Positional arguments:
    partial_module_string -- string representing a view module without the absolute path (e.g. 'repos.index' for
        github_status.views.repos.index).
    url_prefix -- URL prefix passed to the blueprint.

    Returns:
    Blueprint instance for a view module.
    """
    name = partial_module_string
    import_name = 'github_status.views.{}'.format(partial_module_string)
    template_folder = 'templates'
    blueprint = Blueprint(name, import_name, template_folder=template_folder, url_prefix=url_prefix)
    return blueprint


api_health = _factory('api.health', '/api/health')
api_query_github = _factory('api.query_github', '/api/query_github')
repos_details = _factory('repos.details', '/details')
repos_index = _factory('repos.index', '/')


all_blueprints = (api_health, api_query_github, repos_details, repos_index, )
