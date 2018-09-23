"""
Django settings for pp project.

Generated by 'django-admin startproject' using Django 1.11.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

# noinspection PyUnresolvedReferences
from .partial_custom import *
from .partial_celery import *

import os
import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# This default key for development, it is overridden in the production
SECRET_KEY = '_96(y+)c++%-5m6i*4i-4md6o1@zc(5a9fjpoop#%+q=fg3ig9'

DEBUG = False

CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = False

# Application definition

INSTALLED_APPS = [

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # Currently serving
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    # an application that creates account for all anonymous users' requests and associates it with user session
    'lazysignup',

    # framework for creating api
    'rest_framework',

    # Adds cross-origin headers to http request in development
    'corsheaders',

    # Main project apps
    'apps.annotation',
    'apps.publisher',
    'apps.pp',
    'apps.site_test',
    'apps.analytics',

    # Ann app that saves models' states as they change together with the user who produced the change
    'simple_history',

    'drf_yasg',
]

# Set PPUser as Django user model
AUTH_USER_MODEL = 'pp.User'

# Lines below added based on http://django-lazysignup.readthedocs.io/en/latest/install.html#installation
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'lazysignup.backends.LazySignupBackend',
)

# Overwrite default Django behaviour and sends a session cookie to every request (also unlogged ones)
# Crucial for 'lazysignup' to recognize anonymous user in subsequent requests
# NOTE: the session cookie won't be sent to the user anyway after Server Internal Error
SESSION_SAVE_EVERY_REQUEST = True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'apps.log_middleware.ExceptionLoggingMiddleware'
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

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    # Get whole conf from DATABASE_URL in the form of db_engine://user:pass@host:port/db_name
    'default': dj_database_url.config(conn_max_age=500)
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
    # We do not use Django Rest Framework authentication backend
    # User our own authenticator that uses Django authentication instead of Django Rest Framework's
    'DEFAULT_AUTHENTICATION_CLASSES': ['apps.annotation.auth.DjangoRestUseDjangoAuthenticator'],
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
}


JSON_CAMEL_CASE = {
    'PARSER_CLASS': 'rest_framework.parsers.JSONParser',
    'RENDERER_CLASS': 'rest_framework.renderers.JSONRenderer',
}


SWAGGER_SETTINGS = {
    'DEFAULT_FIELD_INSPECTORS': [
        'apps.annotation.inspectors.RootSerializerInspector',
        'apps.annotation.inspectors.IDFieldInspector',
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

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    },
}
