# Third-Party Imports
from django.apps import apps

# App Imports
from core.tests import CoreBaseTestCase


class TestNotificationsModel(CoreBaseTestCase):
    """test the Notifications models methods"""

    Notification = apps.get_model("core", "Notifications")

    def setUp(self):
        self.notification = self.Notification.objects.create(
            title="new notification", body="", target=self.user
        )

    def test_create_notification(self):
        self.assertEqual(self.Notification.objects.count(), 1)

    def test_mark_notification_as_read(self):
        self.notification.mark_as_read()
        self.assertEqual(self.notification.read, True)

    def test_mark_notification_as_unread(self):
        self.notification.mark_as_read()
        self.notification.mark_as_unread()
        self.assertEqual(self.notification.read, False)

    def test_get_time_since(self):
        timesince = self.notification.timesince()
        self.assertTrue(isinstance(timesince, str))
