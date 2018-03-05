from .base import *  # noqa: F403,F401

DEBUG = True

INSTALLED_APPS += [
    'debug_toolbar',
]
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]

ALLOWED_HOSTS = [
    '0.0.0.0',
    '127.0.0.1'
]

INTERNAL_IPS = [
    '0.0.0.0',
    '127.0.0.1'
]
