import sys

# Initialize celery before anything else
# noinspection PyUnresolvedReferences
import worker

if 'test' in sys.argv:
    # For test command by default start with test settings
    from .test import *
else:
    # For all other cases by default start with base settings
    from .dev import *
