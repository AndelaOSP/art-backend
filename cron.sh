#!/bin/sh

source .env
cd scripts
python sync_users.py >> .log.log 2>&1
