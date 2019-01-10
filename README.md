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

| Variable | Description | |
| --- | --- | --- |
| `DATABASE_URL` | **Required** - Used by [dj_database_url](https://github.com/kennethreitz/dj-database-url#url-schema) to connect to the database. Format: 	 DATABASE_URL=postgresql://<user>:<password>@localhost:5432/<db> |
| `SECRET_KEY` | **Required** - String of random characters used to provide cryptographic signing for [Django](https://docs.djangoproject.com/en/2.1/ref/settings/#std:setting-SECRET_KEY) projects. |
| `PROJECT_ID` | **Required** - The Firebase project ID (We use Firebase for authentication) |
| `PRIVATE_KEY` | **Required** - The Firebase private key |
| `CLIENT_EMAIL` | **Required** - The firebase client email value |
| `DJANGO_SETTINGS_MODULE` | **Required** (if running the app using gunicorn `gunicorn art.wsgi`) - `settings.prod` for prod, `settings.dev` optional for dev/staging |
| `SLACK_TOKEN` | **Optional** - The token to authenticate/authorize the slack app used to send slack notifications |
| `ASSET_LIMIT` | **Optional** - A number representing the minimum number of allowed available assets to trigger notification on shortage to slack. |
| `AIS_URL` | **Optional** - Needed to sync users from AIS |
| `AIS_TOKEN` | **Optional** - Needed to sync users from AIS |

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

#### Development using Docker
To use the Docker setup, ensure you have Docker installed then run the following commands:

- `make compose` to create the docker-compose file from the template already in the repository. Open the file with your preferred editor and update the environment section under the `art-backend` service. Replace the values of the varaibles whose values are enclosed in angle brackets with values provided by a fellow team member or team lead.

- `make start` to build and start the app services. Migrations will be ran here.
- `make exec` to run any other commands as necessary. eg `python manage.py createsuperuser`
- `make open` to run the application

### Running the app
- Create a Superuser account: `python manage.py createsuperuser`
- To run tests: `pytest`
- Run the app: `python manage.py runserver`
- You can now log into the admin dashboard on `http://127.0.0.1:8000/admin/`

## CI / CD
We use CircleCI for this. Merging to develop deploys to [staging](https://staging-art.andela.com), and merging to master deploys to [production](https://art.andela.com).

To ensure consistency we have automated checks for a couple of things:
- Project tests - `pytest`
- Python (pep8) styling checks - `flake8 .`
- [Black](https://github.com/ambv/black) formatter checks - `black . -S` (include the `-S` or `--skip-string-normalization` option to allow single quotes on strings.)
- Shell scripts styling checks - `for file in $(find . -type f -name "*.sh"); do shellcheck --format=gcc $file; done;`
- Imports sorting - `isort -rc --diff --atomic .`. Using `--check-only` will perform a dry-run
 - Imports should be in the following order:
   - Future imports
   - Python standard library imports
   - Third party packages
   - Local app imports - absolute
   - Local app imports - relative

You can set up the pre-commit Git hooks with the standard styling conventions as per the guide inn the [Wiki](https://github.com/AndelaOSP/art-backend/wiki/Styling-Conventions).
