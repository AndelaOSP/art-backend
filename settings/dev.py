from .base import *  # noqa: F403,F401

DEBUG = True

ALLOWED_HOSTS += ["api-staging-art.andela.com", "127.0.0.1"]  # noqa ignore=F405

CORS_ORIGIN_WHITELIST = "art-dashboard-staging.herokuapp.com"

CORS_ORIGIN_REGEX_WHITELIST = (
    r"^(https?:\/\/)?((localhost)|(127\.0\.0\.1)):\d{4}",
    r"^(https?:\/\/)?(.+\.)?(andela\.com)",
)

INTERNAL_IPS = ["0.0.0.0", "127.0.0.1"]
