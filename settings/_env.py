import os

ENV = os.environ.get('ENV')
assert ENV in ('dev', 'test', 'prod')

DEBUG = bool(os.environ.get('DEBUG'))
if ENV in ('prod', 'test'):
    assert not DEBUG, "DEBUG can't be set in test and prod environments"

SECRET_KEY = os.environ.get('PP_SECRET_KEY')
HOST = os.environ.get('HEROKU_HOST')
BROKER_URL = os.environ.get('REDIS_URL')
