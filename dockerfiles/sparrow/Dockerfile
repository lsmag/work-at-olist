FROM python:3.6-alpine3.8

RUN \
    apk add --no-cache \
    build-base \
    postgresql-client \
    postgresql-dev

RUN pip install pipenv

WORKDIR /app/sparrow

EXPOSE 8000