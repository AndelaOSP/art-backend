#!/bin/bash

set pass "admin123"

install_system_dependencies()
{
    if ! which python3; then

    brew install python3

    fi

    if ! which virtualenv; then
    
    pip3 install virtualenv

    fi

    virtualenv --python=python3 env

    
    
    source env/bin/activate

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

install_art_requirements()
{
    pip3 install -r requirements.txt
}


start_the_application()
{
    python3 manage.py migrate
    python manage.py createsuperuser --email 'waldo@gmail.com' --slack_handle '@waldo' --cohort '99'


    # Enter your email
    # Enter the Slack handle  
    # Enter the Cohort number
    # Enter a password

    python3 manage.py runserver
}

main()
{
    install_system_dependencies

    create_postgres_instance

    source_environmentalvariables

    run_database_migrations
    
    install_art_requirements

    start_the_application

}

main "$@"
