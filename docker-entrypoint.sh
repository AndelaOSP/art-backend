#!/bin/bash
# Make Migrations
python3 manage.py makemigrations

# Perform Database Migrations
python3 manage.py migrate

# Start The Application
python3 manage.py runserver 0.0.0.0:8080
