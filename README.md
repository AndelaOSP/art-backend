# Andela Resource Tracker (ART) Backend
[![CircleCI](https://circleci.com/gh/AndelaOSP/art-backend/tree/develop.svg?style=svg)](https://circleci.com/gh/AndelaOSP/art-backend/tree/develop)
[![Coverage Status](https://coveralls.io/repos/github/AndelaOSP/art-backend/badge.svg)](https://coveralls.io/github/AndelaOSP/art-backend)

## Description
This repository contains the API endpoints and models for the ART project implemented using Django. Here in is also the implementation of the admin dashboards using Django templates.

## Setup

### Getting Started
- Create the project virtual environment:
> $ mkvirtualenv python -p python3  art-backend

- Clone the repository:
> $ git clone https://github.com/AndelaOSP/art-backend.git

- Open the project directory:
> $ cd art-backend

### Set up environment variables
- To set up environment variables, define the following in your virtual environment postactivate file or `.env` file:

> DATABASE_URL

> SECRET_KEY

> PROJECT_ID

> PRIVATE_KEY

> CLIENT_EMAIL

> SLACK_TOKEN

- To set up the pre-commit Git hooks with the standard styling conventions, follow the instructions on the Wiki [here](https://github.com/AndelaOSP/art-backend/wiki/Styling-Conventions).
### Dependencies
- Install the project dependencies:
> $ pip install -r requirements.txt

### Testing
- To run tests:
> $ python manage.py test

### Set up Database
- Create a database:
> $ createdb db_name

- Run migrations:
> $ python manage.py migrate

### Running the app
- Run the app:
> $ python manage.py runserver

### Create a Superuser account
- To create a super user account for accessing the admin dashboard, run the following command:
> python manage.py createsuperuser
- Enter your email
- Enter the Cohort number
- Enter the Slack handle
- Enter a password
- You can log into the admin dashboard using those credentials on `http://127.0.0.1:8000/admin/`


## Local Development Docker Setup
To use the Docker setup, ensure you have Docker installed.

### Create the `docker-compose.yml` file
Run the `make compose` task to create the docker-compose file from the template alredy in the repository.
```
$ make compose
```
This will generate the file. Open the file with your preferred editor and make changes on the environment section under the `art-backend` service in the `docker-compose.yml` file that you just created. Replace the values of the varaibles whose values are enclosed in angle brackets with values provided by a fellow team member or team lead:
```
PRIVATE_KEY: "<enter-provided-private-key>"
PROJECT_ID: "<enter-project-id>"
CLIENT_EMAIL: "<enter-client-email>"
```

### Start The Services
To start the services you run the make start task i.e.
```
$ make start
```

### Create the superuser account
To create the superuser account, we are going to first connect the container of our application using the exec task in the Makefile. Run the task as shown:
```
$ make exec
```
If the task runs successfully, you will land inside a terminal session in the container. The prompt should look as follows:
```
root@<container-id>:/usr/src/app#
```
The `<container-id>` will vary on different machines but should be string of random letters and numbers for instance `6c6f455638d8`. While on this prompt, run the command `python manage.py createsuperuser` and enter the different values you are prompted for i.e. email address, cohort number, Slack handle and password.
After successfully completing this, navigate to `http://127.0.0.1:8000/admin/` on your browser or run `make open` and use the credentials you just created to login.

[Click here](https://art-backend.herokuapp.com/admin/) to view the app on Heroku.
