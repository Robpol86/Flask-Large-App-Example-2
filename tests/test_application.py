from github_status.application import get_config


def test_get_config_yaml(tmpdir):
    f = tmpdir.join('config.yml')
    f.write('TEST_VAR: true')

    config = get_config('github_status.config.Testing', yaml_files=[str(f)])

    assert config.TEST_VAR is True
