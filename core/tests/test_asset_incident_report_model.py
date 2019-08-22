# Third-Party Imports
from django.apps import apps
from rest_framework.reverse import reverse

# App Imports
from core import constants
from core.tests import CoreBaseTestCase

from ..models import AssetIncidentReport


class AssetIncidentReportModelTest(CoreBaseTestCase):
    """ Tests for the AssetIncidentReport Model """

    def test_model_string_representation(self):
        incident_report = AssetIncidentReport.objects.create(
            asset=self.test_asset,
            incident_type="Loss",
            incident_location="44",
            incident_description="Mugging",
            injuries_sustained="Black eye",
            loss_of_property="Laptop",
            witnesses="Omosh wa mtura",
            police_abstract_obtained="Yes",
            submitted_by=self.user,
        )
        self.assertEqual(
            str(incident_report),
            f"{incident_report.incident_type}: {incident_report.asset}",
        )


class TestAssetIncidentReportNotifications(CoreBaseTestCase):
    """
    Test Notifications elicited by Asset Incident Report creation
    """

    # Asset_model = apps.get_model("core", "Asset")
    User_model = apps.get_model("core", "User")
    Notifications_model = apps.get_model("core", "Notifications")

    def setUp(self):
        self.admin_user = self.User_model.objects.create(
            email="newuser@andela.com",
            password="devpassword",
            first_name="first",
            last_name="second",
            phone_number="254720900900",
            location=self.centre,
            department=self.department,
            is_securityuser=True,
            is_superuser=True,
        )

    def test_admins_are_notified_when_notification_is_created(self):
        original_notifications_count = self.Notifications_model.objects.count()
        admins = self.User_model.objects.filter(is_superuser=True)
        admin_count = admins.count()
        report = AssetIncidentReport.objects.create(
            asset=self.test_asset, incident_type=constants.LOSS, submitted_by=self.user
        )
        notifications = self.Notifications_model.objects.filter(target__in=admins)
        notification = notifications[0]
        incident_url = "{}/{}".format(reverse("incidence-reports-list"), report.id)
        body = "{} submitted a new incident report {}.".format(
            self.admin_user.email, incident_url
        )

        self.assertEqual(
            admin_count, notifications.count() - original_notifications_count
        )
        self.assertEqual(notification.origin, report.submitted_by)
        self.assertEqual(notification.title, "New Incident Report")

        self.assertEqual(notification.body, body)
