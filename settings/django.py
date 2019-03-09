from datetime import timedelta
import os
import dj_database_url

from . import _env

ENV = _env.ENV

DEBUG = _env.DEBUG

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = _env.SECRET_KEY

HOST = _env.HOST

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',

    # Static files
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',

    # API
    'rest_framework',
    'django_filters',
    'djoser',
    'drf_yasg',

    # Main project apps
    'apps.api',
    'apps.auth',
    'apps.annotation',
    'apps.analytics',
    'apps.publisher',
    'apps.pp',
    'apps.site',

    # Additional authentication views and social providers

    # Other
    'social_django',
    'corsheaders',
    'simple_history',
]

SITE_ID = 1

ALLOWED_HOSTS = []
if _env.ENV == 'dev':
    ALLOWED_HOSTS.extend([
        'devdeploy1.przypispowszechny.pl', 'www.devdeploy1.przypispowszechny.pl',
        'devdeploy2.przypispowszechny.pl', 'www.devdeploy2.przypispowszechny.pl',
    ])
    if _env.DEBUG:
        ALLOWED_HOSTS.append('localhost')
elif _env.ENV == 'prod':
    ALLOWED_HOSTS.extend([
        'przypispowszechny.pl', 'www.przypispowszechny.pl',
        'app.przypispowszechny.pl', 'www.app.przypispowszechny.pl',
    ])


CORS_ALLOW_CREDENTIALS = True

if _env.ENV == 'dev' and _env.DEBUG:
    # This allows the regular pp-client scripts to access API in development.
    # Chrome extension is allowed access as it explicitly defines allowed resource domains in manifest.json permissions
    CORS_ORIGIN_ALLOW_ALL = True
else:
    CORS_ORIGIN_WHITELIST = ()
    CORS_ORIGIN_REGEX_WHITELIST = (
        r'https?://([0-9a-zA-Z_.-]+\.)?przypispowszechny\.pl(/.*)?',
    )


USE_X_FORWARDED_HOST = True
# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Set PPUser as Django user model
AUTH_USER_MODEL = 'pp.User'

AUTHENTICATION_BACKENDS = [
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

# Facebook require secret even when already have access_token
SOCIAL_AUTH_FACEBOOK_KEY = '2290339024350798'
SOCIAL_AUTH_FACEBOOK_SECRET = _env.FACEBOOK_GRAPH_SECRET
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email', 'public_profile']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id, name, email, first_name, last_name, verified',
}
SOCIAL_AUTH_FACEBOOK_API_VERSION = '2.9'

# Key and Secret needed only if we want to use implement using refresh token
# Additionally key (client_id) and should be used by frontend client retrieving access_token etc.
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '823340157121-mplb4uvgu5ena8fuuuvvnpn773hpjim4.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ''
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['email', 'profile']

# config per http://psa.matiasaguirre.net/docs/configuration/django.html#django-admin
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'email']

SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',  # this line is not included by default
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

SOCIAL_AUTH_POSTGRES_JSONFIELD = True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',

    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

APPEND_SLASH = False
ROOT_URLCONF = 'urls'

STATIC_ROOT = 'static'
STATIC_URL = '/static/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'wsgi.application'


DATABASES = {
    # Get whole conf from DATABASE_URL in the form of db_engine://user:pass@host:port/db_name
    'default': dj_database_url.config(conn_max_age=500) if _env.ENV != 'test' else
            {'ENGINE': 'django.db.backends.sqlite3', 'NAME': 'test-db'}
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'PAGE_SIZE': 10,
    'ORDERING_PARAM': 'sort',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework_json_api.pagination.LimitOffsetPagination',
    'DEFAULT_PARSER_CLASSES': (
        'apps.api.parsers.JSONAPIParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'apps.api.renderers.JSONAPIRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'TEST_REQUEST_RENDERER_CLASSES': (
        'apps.api.renderers.JSONAPIRenderer',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'vnd.api+json',
}

# djangorestframework_camel_case app used by our JSONAPIRenderer and JSONAPIRenderer
JSON_CAMEL_CASE = {
    'PARSER_CLASS': 'rest_framework.parsers.JSONParser',
    'RENDERER_CLASS': 'rest_framework.renderers.JSONRenderer',
}

SWAGGER_SETTINGS = {
    'DEFAULT_FIELD_INSPECTORS': [
        'drf_yasg.inspectors.CamelCaseJSONFilter',
        'apps.api.inspectors.AppendWriteOnlyFilter',

        'apps.api.inspectors.RootSerializerInspector',
        # ReferencingS... replaced with InlineS... which does not create serializers definitions index,
        # but does not require serializers class names to be unique across whole application
        # 'drf_yasg.inspectors.ReferencingSerializerInspector',
        'drf_yasg.inspectors.InlineSerializerInspector',

        'apps.api.inspectors.IDFieldInspector',
        'apps.api.inspectors.ConstFieldInspector',
        'apps.api.inspectors.ResourceFieldInspector',
        'apps.api.inspectors.RelationFieldInspector',
        'apps.api.inspectors.ObjectFieldInspector',

        'drf_yasg.inspectors.RelatedFieldInspector',
        'drf_yasg.inspectors.ChoiceFieldInspector',
        'drf_yasg.inspectors.FileFieldInspector',
        'drf_yasg.inspectors.DictFieldInspector',
        'drf_yasg.inspectors.HiddenFieldInspector',
        'drf_yasg.inspectors.SimpleFieldInspector',
        'drf_yasg.inspectors.StringDefaultFieldInspector',
    ],

    'SECURITY_DEFINITIONS': {
        'JWT token in format "JWT ${token}" (prepend "JWT" prefix manually)': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
        }
    },

    'PERSIST_AUTH': True,

}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=10) if _env.ENV == 'prod' else timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=10),
    'ROTATE_REFRESH_TOKENS': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': _env.SECRET_KEY,

    'AUTH_HEADER_TYPES': ['JWT'],
}

DJOSER = {
    # Do not use model when using stateless method like JWT
    'TOKEN_MODEL': None
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


if _env.ENV == 'test':
    MAILGUN_API_KEY = 'mock-mailgun-api-key'
    PP_MAIL_DOMAIN = 'mail.przypispowszechny.pl'
    MAILGUN_API_URL = 'https://api.mailgun.net/v3/{}/messages'.format(PP_MAIL_DOMAIN)
elif _env.ENV == 'dev':
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
    PP_MAIL_DOMAIN = 'dev.mail.przypispowszechny.pl'
    MAILGUN_API_URL = 'https://api.mailgun.net/v3/{}/messages'.format(PP_MAIL_DOMAIN)
else:
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
    PP_MAIL_DOMAIN = 'mail.przypispowszechny.pl'
    MAILGUN_API_URL = 'https://api.mailgun.net/v3/{}/messages'.format(PP_MAIL_DOMAIN)



LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}: {levelname}/{processName}][{process:d}][{name}] {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        # Override gunicorn definitions - for the time of running http applicaton, not for the gunicorn host-app itself
        "gunicorn": {
            "level": "INFO",
            "handlers": ["console"],
        },
        "gunicorn.error": {
            "level": "INFO",
            "handlers": ["console"],
            "qualname": "gunicorn.error"

        },
        "gunicorn.access": {
            "level": "INFO",
            "handlers": ["console"],
            "qualname": "gunicorn.access"
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False
        },
        'pp': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False
        },
        'pp.publisher': {
            'handlers': ['console'],
            'level': 'INFO',
            # Avoid duplicating by celery
            'propagate': False,
        },
        # Catch all for any other undefined
        '': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False
        },
    },
}

if _env.ENV == 'test':
    LOGGING['loggers']['django']['level'] = 'CRITICAL'
    LOGGING['loggers']['pp']['level'] = 'CRITICAL'
    LOGGING['loggers']['pp.publisher']['level'] = 'CRITICAL'
    LOGGING['loggers'].setdefault('celery', {})['level'] = 'CRITICAL'

