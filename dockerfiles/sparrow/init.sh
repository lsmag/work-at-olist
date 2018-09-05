#!/bin/sh

set -o errexit
set -o xtrace

DB_HOST=$(pipenv run python -c "import dj_database_url; print(dj_database_url.config()['HOST'])")
DB_PORT=$(pipenv run python -c "import dj_database_url; print(dj_database_url.config()['PORT'])")

until pg_isready -h "$DB_HOST" -p "$DB_PORT" > /dev/null 2> /dev/null; do
    sleep 1
done

cd /app/sparrow
pipenv run python -u manage.py migrate
pipenv run python -u manage.py runserver 0.0.0.0:8000
