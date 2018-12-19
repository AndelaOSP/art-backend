from .base import *  # noqa: F403,F401

DEBUG = True

INSTALLED_APPS += [  # noqa ignore=F405
    'silk',
]
ALLOWED_HOSTS += [   # noqa ignore=F405
    'api-staging-art.andela.com', '127.0.0.1'
]

CORS_ORIGIN_WHITELIST = (
    'art-dashboard-staging.herokuapp.com'
)

CORS_ORIGIN_REGEX_WHITELIST = (
    r'^(https?:\/\/)?((localhost)|(127\.0\.0\.1)):\d{4}',
    r'^(https?:\/\/)?(.+\.)?(andela\.com)',
)

INTERNAL_IPS = [
    '0.0.0.0',
    '127.0.0.1'
]

MIDDLEWARE = ['silk.middleware.SilkyMiddleware'] + MIDDLEWARE  # noqa ignore=F405

SILKY_AUTHENTICATION = True  # User must login
SILKY_AUTHORISATION = True  # User must have permissions
SILKY_META = True
SILKY_INTERCEPT_PERCENT = 10  # log only 10% of requests


def SILKY_PERMISSIONS(user): return user.is_superuser
