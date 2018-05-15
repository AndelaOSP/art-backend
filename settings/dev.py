from .base import *  # noqa: F403,F401

DEBUG = True

INSTALLED_APPS += [  # noqa ignore=F405
    'debug_toolbar',
]

MIDDLEWARE += [  # noqa ignore=F405
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ALLOWED_HOSTS = [
    '0.0.0.0',
    '127.0.0.1',
    'art-backend.herokuapp.com'
]

INTERNAL_IPS = [
    '0.0.0.0',
    '127.0.0.1'
]
