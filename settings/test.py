# TODO: merge this config into base.py settings
from . import base
from .utils import update_locals

update_locals(base.__dict__, locals())

DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': 'test-db'
}

# Switch off logs for tests
LOGGING['loggers']['django']['level'] = 'CRITICAL'
LOGGING['loggers']['pp']['level'] = 'CRITICAL'
LOGGING['loggers']['pp.publisher']['level'] = 'CRITICAL'
LOGGING['loggers'].setdefault('celery', {})['level'] = 'CRITICAL'

# Mailgun settings
MAILGUN_API_KEY = 'mock-mailgun-api-key'
PP_MAIL_DOMAIN = 'mail.przypispowszechny.pl'
MAILGUN_API_URL = 'https://api.mailgun.net/v3/{}/messages'.format(PP_MAIL_DOMAIN)

CELERY_ALWAYS_EAGER = True
