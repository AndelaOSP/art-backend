# Andela Resource Tracker (ART) Backend
[![CircleCI](https://circleci.com/gh/AndelaOSP/art-backend/tree/develop.svg?style=svg)](https://circleci.com/gh/AndelaOSP/art-backend/tree/develop)
[![Coverage Status](https://coveralls.io/repos/github/AndelaOSP/art-backend/badge.svg)](https://coveralls.io/github/AndelaOSP/art-backend)

## Description
This repository contains the API endpoints and models for the ART project implemented using Django.
 - [Local Development](#Local-Development)
    - [Env setup](#Env-setup)
    - [Project setup](#Project-setup)
      - [Installation script](#Installation-script)
      - [Manual setup](#Manual-setup)
      - [Development using Docker](#Development-using-Docker)
    - [Running the app](#Running-the-app)
 - [CI / CD](#CI-/-CD)

## Local Development
### Env setup
- Clone the repository: `git clone https://github.com/AndelaOSP/art-backend.git`
- Open the project directory: `cd art-backend`
- Create a .env file. We currrently use the following env variables.

| Variable | Description | Default |
| --- | --- | --- |
| <sup>**DATABASE_URL**</sup> | <sup>**Required** - Used by [dj_database_url](https://github.com/kennethreitz/dj-database-url#url-schema) to connect to the database. Format: 	 DATABASE_URL=postgresql://<user>:<password>@localhost:5432/<db>.</sup> | |
| <sup>**SECRET_KEY**</sup> | <sup>**Required** - String of random characters used to provide cryptographic signing for [Django](https://docs.djangoproject.com/en/2.1/ref/settings/#std:setting-SECRET_KEY) projects.</sup> | |
| <sup>**PROJECT_ID**</sup> | <sup>**Required** - The Firebase project ID (We use Firebase for authentication).</sup> | |
| <sup>**PRIVATE_KEY**</sup> | <sup>**Required** - The Firebase private key.</sup> | |
| <sup>**CLIENT_EMAIL**</sup> | <sup>**Required** - The firebase client email value.</sup> | |
| <sup>**DJANGO_SETTINGS_MODULE**</sup> | <sup>**Required** (if running the app using gunicorn _gunicorn art.wsgi_) - _settings.prod_ for prod, _settings.dev_ optional for dev/staging.</sup> | <sup>**settings.dev**</sup> |
| <sup>**SLACK_TOKEN**</sup> | <sup>**Optional** - The token to authenticate/authorize the slack app used to send slack notifications.</sup> | |
| <sup>**SLACK_LIMIT**</sup> | <sup>**Optional** - The number of results per page for slack calls.</sup> | <sup>**1000**</sup> |
| <sup>**SLACK_CALLS**</sup> | <sup>**Optional** - The number of calls to make to clask API before exiting.</sup> | <sup>**10**</sup> |
| <sup>**ASSET_LIMIT**</sup> | <sup>**Optional** - A number representing the minimum number of allowed available assets to trigger notification on shortage to slack.</sup> | <sup>**0**</sup> |
| <sup>**AIS_URL**</sup> | <sup>**Optional** - Needed to sync users from AIS.</sup> | |
| <sup>**AIS_TOKEN**</sup> | <sup>**Optional** - Needed to sync users from AIS.</sup> | |
| <sup>**AIS_LIMIT**</sup> | <sup>**Optional** - Number of records to fetch from AIS per request (call it pagination).</sup> | <sup>**5000**</sup> |
| <sup>**ART_BUILDS_CHANNEL**</sup> | <sup>**Optional** - Slack channel when logs will be posted.</sup> | <sup>**#art-builds**</sup> |
| <sup>**OPS_CHANNEL**</sup> | <sup>**Optional** - Slack channel when art bot posts ops related messages if recipient isn't defined.</sup> | <sup>**#art-test**</sup> |
| <sup>**RETRIES**</sup> | <sup>**Optional** - Number of times to retry an external request (currently to AIS) if an error other than 401 is received.</sup> | <sup>**3**</sup> |
| <sup>**RETRY_TIMEOUT**</sup> | <sup>**Optional** - Number of seconds to wait before retrying an external request (currently to AIS) if an error other than 401 is received.</sup> | <sup>**10**</sup> |
| <sup>**LOGLEVEL**</sup> | <sup>**Optional** - Default log level - error, warning, info, debug.</sup> | <sup>**info**</sup> |
| <sup>**ADMINS**</sup> | <sup>**Optional** - Email addresses to send error logs to.</sup> | <sup>**art:art.andela@andela.com,art_group:art@andela.com**</sup> |
| <sup>**DEFAULT_THRESHOLD**</sup> | <sup>**REQUIRED** - Minimal asset threshold</sup> | <sup>**Integer value EG 20**</sup>|
| <sup>**EMAIL_HOST**</sup> | <sup>**REQUIRED** - email host.</sup> | <sup>**smtp.gmail.com**</sup> |
| <sup>**EMAIL_HOST_USER**</sup> | <sup>**REQUIRED** - email host user account</sup> | |
| <sup>**EMAIL_HOST_PASSWORD**</sup> | <sup>**REQUIRED** - email host user account password</sup> | |
| <sup>**EMAIL_PORT**</sup> | <sup>**REQUIRED** - email port.</sup> | <sup>**587**</sup> |
| <sup>**EMAIL_USE_TLS**</sup> | <sup>**REQUIRED** - email TLS.</sup> | <sup>**True**</sup> |
| <sup>**EMAIL_SENDER**</sup> | <sup>**REQUIRED** - email sender's address.</sup> | |


### Project setup
#### Installation script
The easiest way to set up is to run `. ./install_art.sh` which does the following:
  - Installs the following if they don't exist:
    - HomeBrew
    - Python 3
    - Pipenv
    - dependencies
    - ShellCheck
    - PostgreSQL
  - Creates a .env file if it doesn't exist
  - Gives you an option to set up the database

#### Manual setup
- Create a database and add its url to your project environment. eg `DATABASE_URL=postgresql://<user>:<password>@localhost:5432/<db>`
- Create and activate a virtual environment - we recommend using [pipenv](https://github.com/pypa/pipenv) for this by running `pipenv shell`
- Install the project dependencies stored in [Pipfile](/Pipfile). Run `pipenv install --dev`.
- Run migrations - `python manage.py migrate`
- Create cache table `python manage.py createcachetable`
-Open a terminal tab then run the command `python manage.py qcluster` to start django q to enable in sending email notifications

#### Development using Docker
To use the Docker setup, ensure you have Docker installed then run the following commands:

- `make compose` to create the docker-compose file from the template already in the repository. Open the file with your preferred editor and update the environment section under the `art-backend` service. Replace the values of the varaibles whose values are enclosed in angle brackets with values provided by a fellow team member or team lead.

- `make start` to build and start the app services. Migrations will be ran here.
- `make exec` to run any other commands as necessary. eg `python manage.py createsuperuser`
- `make open` to run the application

### Running the app
- Create a Superuser account: `python manage.py createsuperuser`
- To create cache tables `python manage.py createcachetable`
- To run tests: `pytest`
- Run the app: `python manage.py runserver`
- You can now log into the admin dashboard on `http://127.0.0.1:8000/admin/`

## CI / CD
We use CircleCI for this. Merging to develop deploys to [staging](https://staging-art.andela.com), and merging to master deploys to [production](https://art.andela.com).

To ensure consistency we have automated checks for a couple of things. (To run these commands activate the env first `pipenv shell`, or use pipenv's `run` command. eg `pipenv run pytest`):
- Project tests - `pytest`
- Python (pep8) styling checks - `flake8 .`
- [Black](https://github.com/ambv/black) formatter checks - `black --diff -S --exclude="migrations|.venv" .` (include the `-S` or `--skip-string-normalization` option to allow single quotes on strings.)
- Shell scripts styling checks - `for file in $(find . -type f -name "*.sh"); do shellcheck --format=gcc $file; done;`
- Imports sorting - `isort -rc --diff --atomic .`. Using `--check-only` will perform a dry-run
  - Imports should be in the following order:
    - Future imports
    - Python standard library imports
    - Third party packages
    - Local app imports - absolute
    - Local app imports - relative


You can set up the pre-commit Git hooks with the standard styling conventions as per the guide inn the [Wiki](https://github.com/AndelaOSP/art-backend/wiki/Styling-Conventions).
