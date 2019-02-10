from . import _env

# Unique identifier of user that is used to create Demagog annotations with.
DEMAGOG_USERNAME = 'demagog.org.pl'
DEMAGOG_API_URL = 'http://demagog.org.pl/factchecked/jsonapi/v1'

_GA_TRACKING_ID_PROD = 'UA-123054125-1'
_GA_TRACKING_ID_DEV = 'UA-123054125-2'

if _env.ENV == 'prod':
    GA_TRACKING_ID = _GA_TRACKING_ID_PROD
else:
    GA_TRACKING_ID = _GA_TRACKING_ID_DEV
