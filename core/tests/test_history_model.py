# App Imports
from core.tests import CoreBaseTestCase

from ..models import History


class HistoryModelTest(CoreBaseTestCase):
    """Tests for the History Model"""

    def test_add_Hsitory(self):
        "test add history"
        count = History.objects.count()
        History.objects.create(
            table_name="core_asset",
            user=self.user,
            item_id="123",
            action="POST",
            body="body",
        )
        self.assertEqual(History.objects.count(), count + 1)

    def test_cannot_add_history_with_nonexisting_user(self):
        """test cannot add history without action name"""
        count = History.objects.count()
        with self.assertRaises(ValueError):
            history = History.objects.create(
                table_name="core_asset", user="oiuyt", item_id="12", body="body"
            )
        self.assertEqual(History.objects.count(), count)
