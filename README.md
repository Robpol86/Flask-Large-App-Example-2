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

To start the development server locally, run:
`./manage.py devserver`

Then browse to http://localhost:8080

## Production

Running the project in a production environment requires installing requirements and running the Tornado production
server. Run these commands after cloning the git repo or SCP'ing the project files to the host:

* `pip install -r requirements.txt`
* `sudo mkdir /var/log/github_status; sudo chown ghs:root /var/log/github_status`
* `./manage.py prodserver -p 8080 -l /var/log/github_status &`

The above commands assumes you've created the `ghs` user to run the application and will listen on TCP port 8080, which a
load balancer or such will forward traffic to. You may want to write an init script to have the application run as a
service instead of running the last command.
