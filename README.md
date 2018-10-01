1. [About](#about)
2. [Development](#development)
   - [Starting from the scratch](#starting-from-the-scratch) 
   - [Special directories](#special-directories) 
   - [Daily operations](#daily-operations) 
   - [Other operations and issues](#other-operations-and-issues) 
   - [Useful resources](#useful-resources) 


# About

This is server application for [PrzypisPowszechny client](https://github.com/PrzypisPowszechny/pp-client) - the browser extension for enhancing websites with annotations 
available to the visitors at the very moment of reading.

**To see how the extension works see 
[_about_ section in the client repository](https://github.com/PrzypisPowszechny/pp-client#about).**

# Development

### Starting from the scratch

Install docker compose

`$ sudo apt install docker-compose`

Then start it all (it's almost done!)

`$ sudo docker-compose up`

Once previous step is complete, you just need to run the migrations

`$ sudo docker-compose run web python manage.py migrate`

Done!

### Special directories

- `data/postgres` - data stored by postgres=databases

- `data/postgres` - data stored by redis

- `docker-env` - python environment created inside web/worker containers
**Important**: _do not activate this environment_ as it was created inside docker container and should be run from it
only. This directory is just for the purpose of sharing env files between containers, so the python environments in 
web/worker stays in sync and thanks to it `pip -r requirements` has to be run once only. 


### Daily operations

Running tests: `$ sudo docker-compose run web python manage.py test`

Migrating database: `$ sudo docker-compose run web python manage.py migrate`

Opening database cmdline: `sudo docker-compose run web python manage.py dbshell`

Installing new python packages:
`$ sudo docker-compose run web pip install ...`

Moving around _inside/- the container: `$ sudo docker-compose run web bash`  
From _inside_ you can of course also run migrations, pip install or do anything... 

All other operation can be run in similar manner: `$ sudo docker-compose run web COMMAND...`


### Other operations and issues

- **Recreating database**: _just remove `data/postgres` directory_.

- **Permissions**: files created from withing docker might be owned by `root`, so if you need to change them either do it 
running the command in container or just use `sudo`. The most probably case when such situation can take place after 
`docker-compose run web python manage.py makemigrations` is run and new migrations are created.   

### Useful resources

[List of docker resources](./docs/docker-resources.md) helpful for better understanding of our dev environment.
