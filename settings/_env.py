import logging
from os import environ

logger = logging.getLogger(__name__)


ENV = environ.get('ENV', 'dev')
assert ENV in ('dev', 'test', 'prod')

DEBUG = bool(environ.get('DEBUG'))
assert not (DEBUG and ENV == 'prod'), "DEBUG can't be set in prod"
if DEBUG and ENV == 'test':
    logger.warning('Ignoring DEBUG value in test env: setting DEBUG to False')
    DEBUG = False

SECRET_KEY = environ.get('PP_SECRET_KEY') or environ.get('SECRET_KEY')
HOST = environ.get('HEROKU_HOST') or environ.get('HOST')
BROKER_URL = environ.get('REDIS_URL')
FACEBOOK_GRAPH_SECRET = environ.get('FACEBOOK_GRAPH_SECRET')
GOOGLE_OAUTH_SECRET = environ.get('GOOGLE_OAUTH_SECRET')
