# Third-Party Imports
from django.apps import apps

# App Imports
from core import constants
from core.models import AssetIncidentReport, StateTransition
from core.tests import CoreBaseTestCase


class StateTransitionModelTest(CoreBaseTestCase):
    "Tests state trensition model"

    def test_create_incident_report_creates_new_state_transition(self):
        incident_report_count = AssetIncidentReport.objects.count()
        state_transition_count = StateTransition.objects.count()
        AssetIncidentReport.objects.create(
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
        self.assertEqual(AssetIncidentReport.objects.count(), incident_report_count + 1)
        self.assertEqual(StateTransition.objects.count(), state_transition_count + 1)


class TestStateTransitionNotifications(CoreBaseTestCase):
    """
    Test notifications are created when  Transition states are modified appropriately
    """

    Notifications = apps.get_model("core", "Notifications")

    def test_notification_created_when_Transition_state_is_created(self):
        state_transition_count = StateTransition.objects.count()
        notifications_count = self.Notifications.objects.filter(
            target=self.user
        ).count()
        incident = AssetIncidentReport.objects.create(
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
        self.assertEqual(StateTransition.objects.count(), state_transition_count + 1)
        self.assertEqual(
            self.Notifications.objects.filter(target=incident.submitted_by).count(),
            notifications_count + 1,
        )

    def test_notification_created_when_transition_state_is_updated(self):
        incident = AssetIncidentReport.objects.create(
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
        # state_transition_count = StateTransition.objects.count()
        notifications_count = self.Notifications.objects.filter(
            target=self.user
        ).count()
        transition_state = StateTransition.objects.get(asset_incident_report=incident)
        transition_state.incident_report_state = constants.INTERNAL_ASSESSMENT
        transition_state.save()
        new_notification = self.Notifications.objects.filter(target=self.user).latest(
            'created_at'
        )

        self.assertEqual(
            self.Notifications.objects.filter(target=incident.submitted_by).count(),
            notifications_count + 1,
        )
        self.assertEqual(
            new_notification.title,
            constants.INCIDENT_REPORT_STATUS_UPDATED_NOTIFICATION_TITLE,
        )
