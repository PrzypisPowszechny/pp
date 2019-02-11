[![CircleCI master](https://circleci.com/gh/PrzypisPowszechny/pp/tree/master.svg?style=shield)](https://circleci.com/gh/PrzypisPowszechny/pp/tree/master)


1. [About](#about)
2. [REST API Documentation](#rest-api-documentation)
2. [Development](#development)
   - [Starting from the scratch](#starting-from-the-scratch)  
   - [Daily operations](#daily-operations) 
   - [Other operations and issues](#other-operations-and-issues)
   - [Docker-related directories](#docker-related-directories) 
   - [Useful resources](#useful-resources) 


# About

This is server application for [PrzypisPowszechny client](https://github.com/PrzypisPowszechny/pp-client) - the browser extension for enhancing websites with annotations 
available to the visitors at the very moment of reading.

To see how the extension works go to 
**[_about_ section in the client repository](https://github.com/PrzypisPowszechny/pp-client#about)**.


# REST API Documentation 

Check **[swagger documentation of the latest release](https://app.przypispowszechny.pl/api/docs/)**.

# Development

### Starting from the scratch

Install docker compose

`$ sudo apt install docker-compose`

To run docker as non-root (you live without it, but it's saves a bit of effort with sudo typing everyday):

```
$ sudo groupadd docker
$ sudo usermod -aG docker $USER

# Now log out and log in
```
(
[From docker docs](https://docs.docker.com/install/linux/linux-postinstall/#manage-docker-as-a-non-root-user) - 
this creates docker group and add your user to group
)

Let's build our image and install python requirements:

`$ make build`

Once previous step is complete, you just need to run the migrations:

`$ make migrate`

And run it all:

`$ make start-all`

Done!

### Development environment

#### `dev.env`
Defined the environment for development. 

#### `.env`
Is for setting local development variables that cannot be committed to public repo.
Currently consists of: 
 
 `MAILGUN_API_KEY`- Sending emails depends on this setting, so it might not work properly if real private key 
 (but intended for dev, of course) is not set.    

### Daily operations

- `make test` - run tests
- `make migrate` - run django migrate command to migrate SQL DB
- `make makemigrations` - run django makemigrations command
- `make makemigrations-dry-run` - run django makemigrations command in dry-run mode
- `make dbshell` - open database cmdline
- `make shell` - open bash shell in container 
- `make python-shell` - open ipython shell with initialized django 
- `make install` - (re)install python requirements using `pip install`

##### `make help` lists all available commands

You can also always bypass `make` commands and run any command in container : 

`$ sudo docker-compose run --rm web COMMAND...`


### Other operations and issues

- **Recreating database**: _just remove `docker/data/postgres` directory_, it is owned by root, so use `sudo`.


### Docker-related directories

- `docker/data/postgres` - data stored by postgres SQL DB

- `docker/data/redis` - data stored by redis

- `docker/venv/` - python environment created inside web/worker containers
**Important**: _do not activate this environment_ as it was created inside docker container and should be run from it
only. This directory is just for the purpose of sharing env files between containers, so the python environments in 
web/worker stays in sync and thanks to it `pip -r requirements` has to be run once only. 



### Useful resources

[List of docker resources](./docs/docker-resources.md) helpful for better understanding of our dev environment.
