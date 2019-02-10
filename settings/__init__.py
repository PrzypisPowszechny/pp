# TODO: load env fully from env to be fully 12-factor-app compliant

import sys
import os

# Initialize celery before anything else
# noinspection PyUnresolvedReferences
import worker

if 'test' in sys.argv:
    os.environ.setdefault('ENV', 'test')
    # For test command by default start with test settings
    from .test import *
else:
    os.environ.setdefault('ENV', 'dev')
    # For all other cases by default start with base settings
    from .dev import *
