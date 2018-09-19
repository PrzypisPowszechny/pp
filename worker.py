from celery import Celery
from django.conf import settings
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

celery_app = Celery('pp-celery')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
# All celery settings should be set within django settings.
celery_app.config_from_object('django.conf:settings')

# NOTE: lambda makes it lazy here, so importing recursion is avoided
celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
