# Third-Party Imports
from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = "api"

    def ready(self):
        import api.signals # noqa: F401
