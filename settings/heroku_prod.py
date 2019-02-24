# TODO: merge this config into base.py settings
import os
from . import base
from .utils import update_locals

update_locals(base.__dict__, locals())

# Mailgun settings
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
PP_MAIL_DOMAIN = 'mail.przypispowszechny.pl'
MAILGUN_API_URL = 'https://api.mailgun.net/v3/{}/messages'.format(PP_MAIL_DOMAIN)

ALLOWED_HOSTS = [
    'przypispowszechny.pl', 'www.przypispowszechny.pl',
    'app.przypispowszechny.pl', 'www.app.przypispowszechny.pl',
]

CORS_ORIGIN_WHITELIST = ()
# Allow usage from applications hosted on subdomains
CORS_ORIGIN_REGEX_WHITELIST = (
    r'https?://([0-9a-zA-Z_.-]+\.)?przypispowszechny\.pl(/.*)?'
)
CORS_ALLOW_CREDENTIALS = True

# Allow to share cookies between the primary dev domain and its subdomains such as panel.devdeploy1.przypispowszechny.pl
SESSION_COOKIE_DOMAIN = 'devdeploy1.przypispowszechny.pl'

# Honor the X-Forwarded-Host header to know real domain (one from ALLOWED_HOSTS)
USE_X_FORWARDED_HOST = True
# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
