from settings.base import *
import os


SECRET_KEY = os.environ.get('PP_SECRET_KEY')

ALLOWED_HOSTS = [
    'przypispowszechny.pl', 'www.przypispowszechny.pl',
]

# Honor the X-Forwarded-Host header to know real domain (one from ALLOWED_HOSTS)
USE_X_FORWARDED_HOST = True
# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
