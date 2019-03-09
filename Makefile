# More about help, the steps are as follows:
# 1. Include only commands with comments.
# 2. Add 25 spaces command and comment
# 3. Include exactly 25 chars from the beginning and the comment
help:  # Show this help (based on comments, generated using grep and sed)
	cat Makefile | grep  '^[^[:space:]][^#]*#' \
				 | sed -r 's/^([^:]+).*#\s*(.*)/\1                         \2/' \
				 | sed -r 's/(.{25})\s*(\w.+)/  \1 \2/'

dev-local.env:
	${MAKE} generate-local-env

generate-local-env:  # Generate from template .env file, it is meant to store credentials to external services
	cp --update dev-local.env.template dev-local.env

build-image:  # Build docker image
	docker build -t pp/python-venv ./docker/image

install: dev-local.env  # Install requirements
	docker-compose run --rm --no-deps web pip install -r requirements.txt

build:  # Build from scratch: docker image and install requirements
	${MAKE} build-image
	${MAKE} install

shell: dev-local.env  # Open bash shell in container
	docker-compose run --rm web bash

dbshell: dev-local.env  # Open database shell in container using django
	docker-compose run --rm web python manage.py dbshell

docker/venv/bin/ipython:
	docker-compose run --rm --no-deps web pip install ipython

python-shell: dev-local.env docker/venv/bin/ipython  # Open in container ipython shell with initialized django
	docker-compose run --rm web python manage.py shell

migrate: dev-local.env  # Run django migrate
	docker-compose run --rm web python manage.py migrate

makemigrations: dev-local.env  # Run django make migrations
	docker-compose run --rm --no-deps web python manage.py makemigrations

makemigrations-dry-run: dev-local.env  # Run django make migrations dry run
	docker-compose run --rm --no-deps web python manage.py makemigrations --dry-run

test: dev-local.env  # Run tests using django
	docker-compose run --rm --no-deps -e ENV=test web python manage.py test

start: dev-local.env  # Start services: web and worker
	docker-compose up web worker

web: dev-local.env  # Start web service
	docker-compose up web 2>&1

worker: dev-local.env  # Start worker service
	docker-compose up worker

start-all: dev-local.env  # Start all services: web, worker and beat
	docker-compose up
