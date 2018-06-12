from .base import *  # noqa: F403,F401

DEBUG = False

ALLOWED_HOSTS = [
    'art-backend.herokuapp.com'
]

CORS_ORIGIN_WHITELIST = (
    'art-dashboard-staging.herokuapp.com'
)

CORS_ORIGIN_REGEX_WHITELIST = \
    (r'^(https?:\/\/)?(\w+\.)?((localhost)|(127\.0\.0\.1)):\d{4}', )
