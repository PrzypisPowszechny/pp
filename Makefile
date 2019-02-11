# Format user_id:group_id
CURRENT_UID := $$(id -u):$$(id -g)

help:                     # Show this help
	@grep '^[^#[:space:]].*:' Makefile

build-image:              # Build docker image
	docker build -t pp/python-venv ./docker/image

install:                  # Install requirements
	docker-compose run --rm --no-deps --user=$(CURRENT_UID) web pip install -r requirements.txt

build:                    # Build from scratch: docker image and install requirements
	${MAKE} build-image
	${MAKE} install

shell:                    # Open bash shell in container
	docker-compose run --rm --user=$(CURRENT_UID) web bash

dbshell:                  # Open database shell in container using django
	docker-compose run --rm --user=$(CURRENT_UID) web python manage.py dbsheel

python-shell:             # Open in container ipython shell with initialized django
	docker-compose run --rm --user=$(CURRENT_UID) web python manage.py shell

migrate:                  # Run django migrate
	docker-compose run --rm --user=$(CURRENT_UID) web python manage.py migrate

makemigrations:           # Run django make migrations
	docker-compose run --rm --user=$(CURRENT_UID) --no-deps web python manage.py makemigrations

makemigrations-dry-run:   # Run django make migrations dry run
	docker-compose run --rm --user=$(CURRENT_UID) --no-deps web python manage.py makemigrations --dry-run

test:                     # Run tests using django
	docker-compose run --rm --no-deps web python manage.py test

start:                    # Start services: web and worker
	docker-compose up web worker

web:                      # Start web service
	docker-compose up web

worker:                   # Start worker service
	docker-compose up worker

start-all:                # Start all services: web, worker and beat
	docker-compose up
