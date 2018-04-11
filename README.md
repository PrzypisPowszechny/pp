# PrzypisPowszechny server application

## Install guide

#### Database
With default settings development database runs on SQLite.
If you want to use MySQL as your database, install `mysqlclient` system dependencies for python3:
```
sudo apt-get install python3-dev libmysqlclient-dev
```

#### Optional (recommended) virtual environment setup

It might be preferable to use a local package manager:
```
virtualenv -p python3 env
```
To use the environment:
```
source env/bin/activate
```

#### Python packages 
Install python packages
```
pip install -r requirements.txt
```

#### Migrations
Before starting the app, run migrations:
```
./manage.py migrate
```
## Run tests

You may wish to run tests:
```
./manage.py test
```

## Run dev

```
./manage.py runserver
```
