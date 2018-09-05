Running tests
=================

We're using `tox` to run the test suite. You can take a look at
`tox.ini` but, in short, it'll run pytest for the Python tests and
flake8 for linting.

The command for invoking tox is `make test`, which itself is a
shortcut for `docker-compose run --rm sparrow pipenv run tox`. Please
note that'll create a new container for the purpose of running the
tests and remove it when execution is done.

