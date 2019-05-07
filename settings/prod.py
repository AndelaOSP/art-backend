from .base import *  # noqa: F403,F401

DEBUG = False

ALLOWED_HOSTS += ["art-api.andela.com"]  # noqa ignore=F405

CORS_ORIGIN_REGEX_WHITELIST = (r"^(https?:\/\/)?(.+\.)?((andela\.com))",)
