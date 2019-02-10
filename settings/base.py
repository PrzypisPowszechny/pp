from datetime import timedelta
import os
import dj_database_url

from . import _env, partial_celery, partial_internal
from .utils import update_locals

update_locals(partial_celery.__dict__, locals())
update_locals(partial_internal.__dict__, locals())

DEBUG = _env.DEBUG

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = _env.SECRET_KEY
if SECRET_KEY is None and _env.ENV not in ['prod']:
    SECRET_KEY = '_96(y+)c++%-5m6i*4i-4md6o1@zc(5a9fjpoop#%+q=fg3ig9'

HOST = _env.HOST
if DEBUG and HOST is None:
    HOST = 'https://localhost:8000'

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
    'rest_auth',
    'rest_auth.registration',
    'django_filters',
    'drf_yasg',

    # Main project apps
    'apps.annotation',
    'apps.publisher',
    'apps.pp',
    'apps.site',
    'apps.analytics',

    # Additional authentication providers by allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',

    # Other
    'corsheaders',
    'simple_history',
]

SITE_ID = 1

# Set PPUser as Django user model
AUTH_USER_MODEL = 'pp.User'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'offline',
        },
    },
    'facebook': {
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
            'verified',
        ],
        'EXCHANGE_TOKEN': True,
        'VERIFIED_EMAIL': True,
        'VERSION': 'v2.12',
    }
}

ACCOUNT_ADAPTER = 'apps.auth.allauth.AccountAdapter'

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
    'default': dj_database_url.config(conn_max_age=500)
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
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'PAGE_SIZE': 10,
    'ORDERING_PARAM': 'sort',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework_json_api.pagination.LimitOffsetPagination',
    'DEFAULT_PARSER_CLASSES': (
        'apps.annotation.parsers.JSONAPIParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'apps.annotation.renderers.JSONAPIRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'TEST_REQUEST_RENDERER_CLASSES': (
        'apps.annotation.renderers.JSONAPIRenderer',
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
        'apps.annotation.inspectors.RootSerializerInspector',
        'apps.annotation.inspectors.IDFieldInspector',
        'apps.annotation.inspectors.ConstFieldInspector',
        'apps.annotation.inspectors.ResourceFieldInspector',
        'apps.annotation.inspectors.RelationFieldInspector',
        'apps.annotation.inspectors.ObjectFieldInspector',
        'drf_yasg.inspectors.CamelCaseJSONFilter',
        # ReferencingS... replaced with InlineS... which does not create serializers definitions index,
        # but does not require serializers class names to be unique across whole application
        # 'drf_yasg.inspectors.ReferencingSerializerInspector',
        'drf_yasg.inspectors.InlineSerializerInspector',
        'drf_yasg.inspectors.RelatedFieldInspector',
        'drf_yasg.inspectors.ChoiceFieldInspector',
        'drf_yasg.inspectors.FileFieldInspector',
        'drf_yasg.inspectors.DictFieldInspector',
        'drf_yasg.inspectors.HiddenFieldInspector',
        'drf_yasg.inspectors.SimpleFieldInspector',
        'drf_yasg.inspectors.StringDefaultFieldInspector',
    ]
}

# rest_auth app
REST_USE_JWT = True

# apps.auth
PP_AUTH_REST_SESSION_LOGIN = False

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

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
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filters': ['require_debug_true'],
            'filename': 'django.log',
            'formatter': 'verbose',
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
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False
        },
        'pp': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False
        },
        'pp.publisher': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            # Avoid duplicating by celery
            'propagate': False,
        },
        # Catch all for any other undefined
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False
        },
    },
}
