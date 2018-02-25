from settings.base import *

ALLOWED_HOSTS = ['*']

# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Update database configuration with $DATABASE_URL.
import dj_database_url
# db_from_env = dj_database_url.config()
# DATABASES['default'].update(db_from_env)

# Configure Django App for Heroku.
# import django_heroku
# django_heroku.settings(locals())


# DATABASES = {
#      'default': {
#          'ENGINE': 'django.db.backends.postgresql_psycopg2',
#          'NAME': 'pp',
#          'USER': 'pp',
#          'PASSWORD': 'pp',
#          'HOST': 'localhost', # '127.0.0.1' probably works also
#          'PORT': '5432',
#      }
#  }

DATABASES['default'].update(dj_database_url.config(conn_max_age=500))

import logging
DEBUG=False

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# logging.error(STATIC_ROOT)
# logging.error(STATIC_URL)
# logging.error(STATICFILES_DIRS)

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = [
    # os.path.join(PROJECT_ROOT, 'static'),
]

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

logging.error(STATIC_ROOT)
logging.error(STATIC_URL)
logging.error(STATICFILES_DIRS)
