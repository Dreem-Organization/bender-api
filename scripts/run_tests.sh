#!/bin/sh

cd /usr/src/app

rm SECRET
coverage run --source='.' ./manage.py test --cover-min-percentage=0 --noinput
rm SECRET
python manage.py test --noinput
