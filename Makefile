
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build:  ## Builds containers and install dependencies
	docker-compose build sparrow
	docker-compose run --rm sparrow dockerfiles/sparrow/install-deps.sh

flush:  ## Removes ALL DATA from the database, including schemas!
	docker-compose run --rm sparrow dockerfiles/sparrow/flush-database.sh

run:  ## Runs all services in non-detachable mode
	docker-compose up

all: build run  ## Builds and runs the project

test:  ## Runs the Python test suite with tox
	docker-compose run --rm sparrow pipenv run tox

.PHONY: help build run all flush

