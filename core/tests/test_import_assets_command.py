from io import StringIO
from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError


class ImportAssetsCommandTestCase(TestCase):
    def setUp(self):
        self.inmemory_out = StringIO()

    def test_running_command_without_argument_has_custom_error_message(self):
        with self.assertRaises(CommandError) as context:
            call_command("import_assets", stdout=self.inmemory_out)

        self.assertTrue(
            "Specify the path/url to local/remote csv file containing asset data."
            in str(context.exception)
        )
