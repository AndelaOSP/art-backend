# Third-Party Imports
from django.apps import apps

# App Imports
from core.tests import CoreBaseTestCase

app = apps.get_app_config("core")


class GeneralStuffTest(CoreBaseTestCase):
    def test_save_validation_error_raised(self):
        all_models = app.models.items()
        for model_name, model in all_models:
            try:
                obj = model.objects.first()
            except Exception:
                continue
            else:
                with self.assertRaises(Exception):
                    obj.save(force_insert=True, force_update=True)
