#!/bin/sh

cd /usr/src/app || exit

cd /usr/src/app; python manage.py migrate
cd /usr/src/app; python manage.py loaddata data_tests.json

bash