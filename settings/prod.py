from .base import *  # noqa: F403,F401
import os
DEBUG = False

ALLOWED_HOSTS = [os.environ.get('MY_HOST_IP'), 'api-staging-art.andela.com',
                 'art-backend.herokuapp.com']

CORS_ORIGIN_WHITELIST = (
    'art-dashboard-staging.herokuapp.com'
)

CORS_ORIGIN_REGEX_WHITELIST = \
    (r'^(https?:\/\/)?(\w+\.)?((localhost)|(127\.0\.0\.1)):\d{4}', )
