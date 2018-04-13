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


[Click here](https://art-backend.herokuapp.com/admin/) to view the app on Heroku.
