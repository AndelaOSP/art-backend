#!/bin/bash
# Make Migrations
python3 manage.py makemigrations

# Perform Database Migrations
python3 manage.py migrate

# collect static files
python3 manage.py collectstatic --noinput

# Start The Application
python3 manage.py runserver 0.0.0.0:8000
