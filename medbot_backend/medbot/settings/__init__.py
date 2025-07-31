"""
Settings package for MedBot Django project.
"""

import os
from decouple import config

# Determine which settings to use based on environment
ENVIRONMENT = config('DJANGO_ENVIRONMENT', default='development')

if ENVIRONMENT == 'production':
    from .production import *
elif ENVIRONMENT == 'testing':
    from .testing import *
elif ENVIRONMENT == 'sqlite_dev':
    from .sqlite_dev import *
else:
    from .development import *
