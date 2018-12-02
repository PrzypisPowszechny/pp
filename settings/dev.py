from .base import *

DEBUG = True

# This allows the regular pp-client scripts to access API in development
# Chrome extension is allowed access as it explicitly defines allowed resource domains in manifest.json permissions
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

# Mailgun settings
MAILGUN_API_KEY=os.environ.get('MAILGUN_API_KEY')
PP_MAIL_DOMAIN='dev.mail.przypispowszechny.pl'
MAILGUN_API_URL='https://api.mailgun.net/v3/{}/messages'.format(PP_MAIL_DOMAIN)
