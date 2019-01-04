# Standard Library
import os

APP_ENV = os.environ.get('APP_ENV')

if APP_ENV in ('dev', 'prod'):
    exec('from .{} import *'.format(APP_ENV))
