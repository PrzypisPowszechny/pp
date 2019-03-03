from celery import Celery
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

celery_app = Celery('pp-celery')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
# All celery settings should be set within django settings.
celery_app.config_from_object('django.conf:settings')
