# Initialize celery before anything else
# noinspection PyUnresolvedReferences
import worker

from .django import *
from .celery import *
from .pp import *
