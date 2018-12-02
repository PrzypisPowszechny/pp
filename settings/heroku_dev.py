from settings.base import *
import os


SECRET_KEY = os.environ.get('PP_SECRET_KEY')

# Mailgun settings
MAILGUN_API_KEY=os.environ.get('MAILGUN_API_KEY')
PP_MAIL_DOMAIN='dev.mail.przypispowszechny.pl'
MAILGUN_API_URL='https://api.mailgun.net/v3/{}/messages'.format(PP_MAIL_DOMAIN)

ALLOWED_HOSTS = [
    'devdeploy1.przypispowszechny.pl', 'www.devdeploy1.przypispowszechny.pl',
    'devdeploy2.przypispowszechny.pl', 'www.devdeploy2.przypispowszechny.pl',
]

# Allow localhost applications to use dev API
CORS_ORIGIN_WHITELIST = ()
CORS_ORIGIN_REGEX_WHITELIST = (
    r'https?://localhost:.*',
)


# Honor the X-Forwarded-Host header to know real domain (one from ALLOWED_HOSTS)
USE_X_FORWARDED_HOST = True
# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
