#!/bin/sh

username=${1:-'superuser'}
email=${2:-'superuser@bender.com'}
password=${3:-'superuser'}

cd /usr/src/app || exit

while ! pg_isready -h bender-database -p 5432 > /dev/null 2> /dev/null; do
    echo "Failed to connect to bender-database..."
    echo "Trying again in 5 seconds !"
    sleep 5
  done

cd /usr/src/app; python manage.py migrate
cd /usr/src/app; python manage.py loaddata data_tests.json

echo "from bender.models import User; User.objects.create_superuser(username='${username}', email='${email}', password='${password}')" | python manage.py shell

python manage.py runserver 0.0.0.0:8000 --settings=bender_service.settings.development
