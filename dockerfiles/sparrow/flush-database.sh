#!/bin/sh

set -o errexit
set -o xtrace

cd /app/sparrow

DB_HOST=$(pipenv run python -c "import dj_database_url; print(dj_database_url.config()['HOST'])")
DB_NAME=$(pipenv run python -c "import dj_database_url; print(dj_database_url.config()['NAME'])")
DB_USER=$(pipenv run python -c "import dj_database_url; print(dj_database_url.config()['USER'])")

dropdb $DB_NAME -h $DB_HOST -U $DB_USER || true
createdb $DB_NAME -h $DB_HOST -U $DB_USER || true
