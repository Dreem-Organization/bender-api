#!/bin/sh

getent hosts db || exit 2 # exit if the DB is not reachable

cd /usr/src/app || exit
python manage.py migrate
gunicorn --config gunicorn_config.py bender_service.wsgi
