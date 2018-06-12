from .base import *  # noqa: F403,F401

DEBUG = False

ALLOWED_HOSTS = [
    'art-backend.herokuapp.com'
]

CORS_ORIGIN_WHITELIST = (
    'localhost:3000',
    'art-dashboard-staging.herokuapp.com'
)
