# Standard Library
import os

APP_ENV = os.environ.get('APP_ENV')

if APP_ENV == 'dev':
    from .dev import *   # noqa
elif APP_ENV == 'prod':
    from .prod import *   # noqa
