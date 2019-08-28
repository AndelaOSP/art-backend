# Third-Party Imports
from django.apps import apps

# App Imports
from core import constants
from core.tests import CoreBaseTestCase


class StateTransitionModelTest(CoreBaseTestCase):
    """Tests state transition model"""

    def test_create_incident_report_creates_new_state_transition(self):
        incident_report_count = apps.get_model(
            "core", "AssetIncidentReport"
        ).objects.count()
        state_transition_count = apps.get_model(
            "core", "StateTransition"
        ).objects.count()
        apps.get_model("core", "AssetIncidentReport").objects.create(
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
            apps.get_model("core", "AssetIncidentReport").objects.count(),
            incident_report_count + 1,
        )
        self.assertEqual(
            apps.get_model("core", "StateTransition").objects.count(),
            state_transition_count + 1,
        )


class TestTransitionStateUpdateFromAssetStatusModification(CoreBaseTestCase):
    """
    Test updating the transition state to CLOSED when an Asset status is changed from ALLOCATED to
    either (AVAILABLE,DAMAGED,LOST)
    """

    def setUp(self):
        self.asset = apps.get_model("core", "Asset").objects.create(
            asset_code="IC0019009",
            serial_number="SN001000098",
            model_number=self.test_assetmodel,
            purchase_date="2019-07-10",
        )
        self.incident_report = apps.get_model(
            "core", "AssetIncidentReport"
        ).objects.create(asset=self.asset)
        self.transition_state = apps.get_model(
            "core", "StateTransition"
        ).objects.get_or_create(asset_incident_report_id=self.incident_report.id)
        self.transition_state = self.transition_state[0]

    def test_update_asset_status_from_allocated_to_lost(self):
        status = (
            apps.get_model("core", "AssetStatus")
            .objects.filter(asset=self.asset)
            .latest('created_at')
        )

        # allocate asset  to a user
        apps.get_model("core", "AllocationHistory").objects.create(
            asset=self.asset, current_assignee=self.asset_assignee2
        )

        # update status to lost
        status.current_status = constants.LOST
        status.save()

        transition_state = apps.get_model("core", "StateTransition").objects.get(
            asset_incident_report=self.incident_report
        )

        self.assertEqual(transition_state.incident_report_state, constants.CLOSED)

    def test_update_asset_status_from_allocated_to_damaged(self):
        status = (
            apps.get_model("core", "AssetStatus")
            .objects.filter(asset=self.asset)
            .latest('created_at')
        )

        # allocate asset  to a user
        apps.get_model("core", "AllocationHistory").objects.create(
            asset=self.asset, current_assignee=self.asset_assignee2
        )

        # update status to DAMAGED
        status.current_status = constants.DAMAGED
        status.save()

        transition_state = apps.get_model("core", "StateTransition").objects.get(
            asset_incident_report=self.incident_report
        )

        self.assertEqual(transition_state.incident_report_state, constants.CLOSED)

    def test_update_asset_status_from_allocated_to_available(self):
        status = (
            apps.get_model("core", "AssetStatus")
            .objects.filter(asset=self.asset)
            .latest('created_at')
        )
        self.assertEqual(status.current_status, constants.AVAILABLE)
        # allocate asset  to a user
        apps.get_model("core", "AllocationHistory").objects.create(
            asset=self.asset, current_assignee=self.asset_assignee2
        )
        status = (
            apps.get_model("core", "AssetStatus")
            .objects.filter(asset=self.asset)
            .latest('created_at')
        )
        self.assertEqual(status.current_status, constants.ALLOCATED)

        # update status to AVAILABLE
        status.current_status = constants.AVAILABLE
        status.save()

        transition_state = apps.get_model("core", "StateTransition").objects.get(
            asset_incident_report=self.incident_report
        )
        self.assertEqual(transition_state.incident_report_state, constants.CLOSED)
