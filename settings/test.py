import sys

from settings.base import *

if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test-db'
    }

LOGGING['loggers']['django'].update({
    'handlers': ['console', 'file'],
    'level': 'ERROR',
})
