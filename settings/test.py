import sys

from settings.base import *

if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test-db'
    }

# Switch off logs for tests
LOGGING['loggers']['django']['level'] = 'CRITICAL'
LOGGING['loggers']['pp']['level'] = 'CRITICAL'
LOGGING['loggers']['pp.publisher']['level'] = 'CRITICAL'
