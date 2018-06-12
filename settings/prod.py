from .base import *  # noqa: F403,F401

DEBUG = False

ALLOWED_HOSTS = [
    'art-backend.herokuapp.com',
    'art-dashboard-staging.herokuapp.com'
]

CORS_ORIGIN_WHITELIST = (
    'art-dashboard-staging.herokuapp.com'
)
