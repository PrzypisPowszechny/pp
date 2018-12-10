from settings.base import *
import os


SECRET_KEY = os.environ.get('PP_SECRET_KEY')

# Mailgun settings
MAILGUN_API_KEY=os.environ.get('MAILGUN_API_KEY')
PP_MAIL_DOMAIN='mail.przypispowszechny.pl'
MAILGUN_API_URL='https://api.mailgun.net/v3/{}/messages'.format(PP_MAIL_DOMAIN)

ALLOWED_HOSTS = [
    'przypispowszechny.pl', 'www.przypispowszechny.pl', 'app.przypispowszechny.pl',
]

# Honor the X-Forwarded-Host header to know real domain (one from ALLOWED_HOSTS)
USE_X_FORWARDED_HOST = True
# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

GA_TRACKING_ID = GA_TRACKING_ID_PROD
