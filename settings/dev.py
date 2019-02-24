# TODO: merge this config into base.py settings
import os
from . import base
from .utils import update_locals

update_locals(base.__dict__, locals())

# This allows the regular pp-client scripts to access API in development
# Chrome extension is allowed access as it explicitly defines allowed resource domains in manifest.json permissions
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

