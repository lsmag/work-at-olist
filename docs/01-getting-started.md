Getting started
===================

This project uses Django 2.1, Python 3.7 and PostgreSQL for the call
records API, and it's named "sparrow" (because naming is hard). It was
developed using Arch Linux, written in Emacs and uses a small number
of libraries for testing: pytest, flake8, coverage.py, freezegun,
model_mommy. The dependencies are _both_ managed by setup.py and by
Pipenv.

It was written to be developed using docker-compose for both running
the server and the test suite. The next chapters, listed below, will
guide you on how to set it up locally.  Another chapter will document
sparrow's API, and finally, the final chapter will contain
documentation on deployment.

For now, take a look at:
- `docs/02-installing.md`
- `docs/03-running-tests.md`
- `docs/04-interacting-with-the-api.md`
