#!/usr/bin/env python
import os
import sys

import firebase_admin
from firebase_admin import credentials

from settings.base import BASE_DIR

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    cred = credentials.Certificate(os.path.join(BASE_DIR,
                                                'serviceAccount.json'))
    firebase_admin.initialize_app(cred)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
