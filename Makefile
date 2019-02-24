# Format user_id:group_id
CURRENT_UID := $$(id -u):$$(id -g)


help:                     # Show this help
	@grep '^[^#[:space:]].*:' Makefile

generate-local-env:       # Generate from template .env file, it is meant to store credentials to external services
	cp --update dev-local.env.template dev-local.env

build-image:              # Build docker image
	docker build -t pp/python-venv ./docker/image

install:                  # Install requirements
	${MAKE} generate-local-env
	docker-compose run --rm --no-deps --user=$(CURRENT_UID) web pip install -r requirements.txt

build:                    # Build from scratch: docker image and install requirements
	${MAKE} build-image
	${MAKE} install

shell:                    # Open bash shell in container
	${MAKE} generate-local-env
	docker-compose run --rm --user=$(CURRENT_UID) web bash

dbshell:                  # Open database shell in container using django
	${MAKE} generate-local-env
	docker-compose run --rm --user=$(CURRENT_UID) web python manage.py dbshell

python-shell:             # Open in container ipython shell with initialized django
	${MAKE} generate-local-env
	docker-compose run --rm --user=$(CURRENT_UID) web python manage.py shell

migrate:                  # Run django migrate
	${MAKE} generate-local-env
	docker-compose run --rm --user=$(CURRENT_UID) web python manage.py migrate

makemigrations:           # Run django make migrations
	${MAKE} generate-local-env
	docker-compose run --rm --user=$(CURRENT_UID) --no-deps web python manage.py makemigrations

makemigrations-dry-run:   # Run django make migrations dry run
	${MAKE} generate-local-env
	docker-compose run --rm --user=$(CURRENT_UID) --no-deps web python manage.py makemigrations --dry-run

test:                     # Run tests using django
	${MAKE} generate-local-env
	docker-compose run --rm --no-deps -e ENV=test web python manage.py test

start:                    # Start services: web and worker
	${MAKE} generate-local-env
	docker-compose up web worker

web:                      # Start web service
	${MAKE} generate-local-env
	docker-compose up web

worker:                   # Start worker service
	${MAKE} generate-local-env
	docker-compose up worker

start-all:                # Start all services: web, worker and beat
	${MAKE} generate-local-env
	docker-compose up
