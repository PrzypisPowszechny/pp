from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'pp',
        'USER': 'pp',
        'PASSWORD': 'pp',
        'HOST': 'postgres',
        'PORT': '5432',
    }
}

# This allows the regular pp-client scripts to access API in development
# Chrome extension is allowed access as it explicitly defines allowed resource domains in manifest.json permissions
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
