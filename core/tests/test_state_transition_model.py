from core import constants
from core.models import (
    AllocationHistory,
    Asset,
    AssetIncidentReport,
    AssetStatus,
    StateTransition,
)
from core.tests import CoreBaseTestCase


class StateTransitionModelTest(CoreBaseTestCase):
    """Tests state transition model"""

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


class TestTransitionStateUpdateFromAssetStatusModification(CoreBaseTestCase):
    """
    Test updating of transition state when Asset status is modified
    Update the transition state to CLOSED when an Asset status is changed from (DAMAGED,LOST) to
    either (AVAILABLE,ALLOCATED)
    """

    def setUp(self):
        self.asset = Asset.objects.create(
            asset_code="IC0019009",
            serial_number="SN001000098",
            model_number=self.test_assetmodel,
            purchase_date="2019-07-10",
        )
        self.incident_report = AssetIncidentReport.objects.create(asset=self.asset)
        self.transition_state = StateTransition.objects.get_or_create(
            asset_incident_report_id=self.incident_report.id
        )
        self.transition_state = self.transition_state[0]

    def test_update_asset_status_from_lost_to_available(self):
        status = AssetStatus.objects.get(asset=self.asset)
        # update status to lost
        status.current_status = constants.LOST
        status.save()
        # update status to available
        status = AssetStatus.objects.get(asset=self.asset)
        status.current_status = constants.AVAILABLE
        status.save()
        # verify that transition state has been updated to closed
        transition_state = StateTransition.objects.get(
            asset_incident_report=self.incident_report
        )
        self.assertEqual(transition_state.incident_report_state, constants.CLOSED)

    def test_update_asset_status_from_damaged_to_available(self):
        status = AssetStatus.objects.get(asset=self.asset)

        # update status to lost
        status.current_status = constants.DAMAGED
        status.save()
        # update status to available
        status = AssetStatus.objects.get(asset=self.asset)
        status.current_status = constants.AVAILABLE
        status.save()
        # verify that transition state has been updated to closed
        transition_state = StateTransition.objects.get(
            asset_incident_report=self.incident_report
        )
        self.assertEqual(transition_state.incident_report_state, constants.CLOSED)

    def test_update_asset_status_from_lost_to_allocated(self):
        status = AssetStatus.objects.get(asset=self.asset)

        # update status to lost
        status.current_status = constants.LOST
        status.save()

        # allocate asset  to a user
        AllocationHistory.objects.create(
            asset=self.asset, current_assignee=self.asset_assignee2
        )

        transition_state = StateTransition.objects.get(
            asset_incident_report=self.incident_report
        )

        self.assertEqual(transition_state.incident_report_state, constants.CLOSED)

    def test_update_asset_status_from_damaged_to_allocated(self):
        status = AssetStatus.objects.get(asset=self.asset)

        # update status to lost
        status.current_status = constants.DAMAGED
        status.save()
        # allocate asset  to a user
        AllocationHistory.objects.create(
            asset=self.asset, current_assignee=self.asset_assignee2
        )

        transition_state = StateTransition.objects.get(
            asset_incident_report=self.incident_report
        )

        self.assertEqual(transition_state.incident_report_state, constants.CLOSED)

    def test_update_asset_status_from_allocated_to_available(self):
        status = AssetStatus.objects.get(asset=self.asset)
        self.assertEqual(status.current_status, constants.AVAILABLE)
        # allocate asset  to a user
        AllocationHistory.objects.create(
            asset=self.asset, current_assignee=self.asset_assignee2
        )
        status = AssetStatus.objects.get(asset=self.asset)
        self.assertEqual(status.current_status, constants.ALLOCATED)

        transition_state = StateTransition.objects.get(
            asset_incident_report=self.incident_report
        )
        self.assertEqual(
            transition_state.incident_report_state, constants.NEWLY_REPORTED
        )
