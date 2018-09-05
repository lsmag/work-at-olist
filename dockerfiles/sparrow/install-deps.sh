#!/bin/sh

set -o errexit
set -o xtrace

cd /app/sparrow

pipenv --python 3.7
pipenv install --dev

DB_HOST=$(pipenv run python -c "import dj_database_url; print(dj_database_url.config()['HOST'])")
DB_NAME=$(pipenv run python -c "import dj_database_url; print(dj_database_url.config()['NAME'])")
DB_USER=$(pipenv run python -c "import dj_database_url; print(dj_database_url.config()['USER'])")
createdb $DB_NAME -h $DB_HOST -U $DB_USER || true
