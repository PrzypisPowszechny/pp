### PrzypisPowszechny server application

## Install guide


### Optional virtual environment setup

It might be preferable to use a local package manager:
```
virtualenv -p -python3 env
```
To use the environment:
```
source env/bin/activate
```
### Necessary 
Install mysqlclient dependencies for python3:
```
sudo apt-get install python3-dev libmysqlclient-dev
```

Install python packages
```
pip install -r requirements.txt
```