# GitHub Status

Simple Flask application that queries GitHub's API for repository metadata and displays it in a jQuery-powered view.

Requirements:

* Python 2.7
* OS X or Ubuntu
* MySQL (development or production)
* SQLite (testing)

[![Build Status](https://img.shields.io/travis/Robpol86/Flask-Large-App-Example-2/master.svg?style=flat-square)]
(https://travis-ci.org/Robpol86/Flask-Large-App-Example-2)
[![Coverage Status](https://img.shields.io/codecov/c/github/Robpol86/Flask-Large-App-Example-2/master.svg?style=flat-square)]
(https://codecov.io/github/Robpol86/Flask-Large-App-Example-2)

## Testing

Testing the project is simple. You run these commands after cloning the git repo on OS X or Ubuntu:

* `pip install -r requirements.txt -r tests/requirements.txt`
* `py.test --cov-report term-missing --cov github_status tests`

SQLite is used as the testing database. It will automatically be created in the git repo's root directory.

## Development

To work on the project on your OS X development environment you just clone the git repo and run:
`pip install -r requirements.txt`

Then you need to setup your MySQL database. Reference `./github_status/config.py` under the `HardCoded` class for
the MySQL user name and password to create, as well as the database name to create. Give that user `create`, `delete`,
`drop`, `insert`, `select`, and `update` privileges on that database.

Now run this command to create the schema:
`./manage.py create_all`

To start the development server locally, run:
`./manage.py devserver`

Then browse to [http://localhost:5000](http://localhost:5000).

## Production

Running the project in a production environment requires installing requirements and running the Tornado production
server. Run these commands after cloning the git repo or SCP'ing the project files to the host:

* `pip install -r requirements.txt`
* `sudo mkdir /var/log/github_status /etc/github_status; sudo chown ghs:root /var/log/github_status /etc/github_status`

Create the GitHub Status config file `/etc/github_status/config.yml` with something like this:

```yaml
_SQLALCHEMY_DATABASE_DATABASE: 'github_status'
_SQLALCHEMY_DATABASE_HOSTNAME: 'localhost'
_SQLALCHEMY_DATABASE_PASSWORD: 'github_p@ssword'
_SQLALCHEMY_DATABASE_USERNAME: 'github_service'
```

Now run this command to create the schema:
`./manage.py create_all --config_prod`

Finally start the production server:
`./manage.py prodserver --config_prod -p 8080 -l /var/log/github_status &`

The above commands assumes you've created the `ghs` user to run the application and will listen on TCP port 8080, which a
load balancer or such will forward traffic to. You may want to write an init script to have the application run as a
service instead of running the last command.
