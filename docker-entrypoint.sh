#!/bin/bash
# Perform Database Migrations
python3 manage.py migrate

# Start The Application
python3 manage.py runserver 0.0.0.0:8080
