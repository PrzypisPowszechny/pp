import sys

from settings.base import *

TEST = True

if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test-db'
    }

# Switch off logs for tests
LOGGING['loggers']['django']['level'] = 'CRITICAL'
LOGGING['loggers']['pp']['level'] = 'CRITICAL'
LOGGING['loggers']['pp.publisher']['level'] = 'CRITICAL'

# Mailgun settings
MAILGUN_API_KEY='mock-mailgun-api-key'
PP_MAIL_DOMAIN='mail.przypispowszechny.pl'
MAILGUN_API_URL='https://api.mailgun.net/v3/{}/messages'.format(PP_MAIL_DOMAIN)
