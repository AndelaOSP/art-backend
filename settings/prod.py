from .base import *  # noqa: F403,F401

DEBUG = False

ALLOWED_HOSTS += [  # noqa ignore=F405
    'art-api.andela.com'
]

CORS_ORIGIN_REGEX_WHITELIST = \
    (r'^(https?:\/\/)?(.+\.)?((andela\.com))', )
