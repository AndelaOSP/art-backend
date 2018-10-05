#!/bin/bash

set pass "admin123"

install_system_dependencies()
{
    if ! which python3; then

    brew install python3

    fi

    if ! which pipenv; then

    brew install pipenv

    fi

}

create_postgres_instance()
{
    if ! which psql; then

    brew install postgresql

    fi

    # create database art_postgres
    echo "Enter your password for postgres database"
    psql --command "CREATE DATABASE art_postgres;" -U postgres
    # Create role/user art_postgres
    echo "Enter your password for postgres database"
    psql --command "CREATE ROLE art_postgres WITH PASSWORD 'art_postgres' LOGIN;" -U postgres
    # Grant all privileges to database `art_postgres` to user 'art_postgres'
    echo "Enter your password for postgres database"
    psql --command "GRANT ALL PRIVILEGES ON DATABASE "art_postgres" to art_postgres;" -U postgres
}

install_art_requirements()
{
    pipenv install

    pipenv shell
}


source_environmentalvariables()
{
    echo "Setup the environmental variable manually"
    source .env
    # research on how to populate the .env file
    # consider populating manually
}

run_database_migrations()
{
    python manage.py migrate
}


start_the_application()
{
    python manage.py migrate
    python manage.py createsuperuser --email 'waldo@gmail.com' --slack_handle '@waldo' --cohort '99'


    # Enter your email
    # Enter the Slack handle
    # Enter the Cohort number
    # Enter a password

    python manage.py runserver
}

main()
{
    install_system_dependencies

    create_postgres_instance

    install_art_requirements

    source_environmentalvariables

    run_database_migrations

    start_the_application

}

main "$@"
