from .base import *  # noqa: F403,F401
import os
DEBUG = True

INSTALLED_APPS += [  # noqa ignore=F405
    'debug_toolbar',
]

MIDDLEWARE += [  # noqa ignore=F405
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ALLOWED_HOSTS = [os.environ.get('MY_HOST_IP'), 'api-staging-art.andela.com']

INTERNAL_IPS = [
    '0.0.0.0',
    '127.0.0.1'
]
