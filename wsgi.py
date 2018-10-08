"""
WSGI config for pp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""
import importlib
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Actual WSGI application
application = get_wsgi_application()

# HOOK for specifying gunicorn config with use of our *real* settings.
# This is for all envs and only for settings we can't set by cmdln args.
_settings = importlib.import_module(os.environ.get("DJANGO_SETTINGS_MODULE"))

# Set logging format, this is not setting for the http application, but for the very start of gunicorn itself
logconfig_dict = _settings.LOGGING
