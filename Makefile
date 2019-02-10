help: # Show this help
	@grep '^[^#[:space:]].*:' Makefile

build-image: # Build docker image
	docker build -t pp/python-venv ./docker

install: # Install requirements
	docker-compose run --rm --no-deps web pip install -r requirements.txt

build: # Build from scratch: docker image and install requirements
	make build-image
	make install

shell: # Open shell in container
	docker-compose run --rm web bash

migrate: # Migrate the apps
	docker-compose run --rm web python manage.py migrate

test: # Run tests
	docker-compose run --rm --no-deps web python manage.py test

start-web: # Start web service
	docker-compose up web

start-all: # Start all services
	docker-compose up
