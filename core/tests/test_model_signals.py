# App Imports
from core import constants
from core.models import Asset, AssetIncidentReport, StateTransition
from core.tests import CoreBaseTestCase


# noinspection DuplicatedCode
class ModelSignalsTest(CoreBaseTestCase):
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

    def test_update_transition_state_for_damaged_item_under_internal_assessment(self):
        self.transition_state.incident_report_state = constants.INTERNAL_ASSESSMENT
        self.transition_state.save()

        self.incident_report.incident_type = constants.DAMAGE
        self.incident_report.save()

        updated_transition = StateTransition.objects.get(id=self.transition_state.id)

        self.assertEqual(updated_transition.incident_report_state, constants.CLOSED)

    def test_update_transition_state_for_damaged_item_under_external_assessment(self):
        self.transition_state.incident_report_state = constants.EXTERNAL_ASSESSMENT
        self.transition_state.save()

        self.incident_report.incident_type = constants.DAMAGE
        self.incident_report.save()

        updated_transition = StateTransition.objects.get(id=self.transition_state.id)

        self.assertEqual(updated_transition.incident_report_state, constants.CLOSED)

    def test_update_transition_state_for_damaged_item_under_out_for_repair(self):
        self.transition_state.incident_report_state = constants.OUT_FOR_REPAIR
        self.transition_state.save()

        self.incident_report.incident_type = constants.DAMAGE
        self.incident_report.save()

        updated_transition = StateTransition.objects.get(id=self.transition_state.id)

        self.assertEqual(updated_transition.incident_report_state, constants.CLOSED)

    def test_update_transition_state_for_lost_item_under_internal_assessment(self):
        self.transition_state.incident_report_state = constants.INTERNAL_ASSESSMENT
        self.transition_state.save()

        self.incident_report.incident_type = constants.LOSS
        self.incident_report.save()

        updated_transition = StateTransition.objects.get(id=self.transition_state.id)

        self.assertEqual(updated_transition.incident_report_state, constants.CLOSED)

    def test_update_transition_state_for_LOST_item_under_external_assessment(self):
        self.transition_state.incident_report_state = constants.EXTERNAL_ASSESSMENT
        self.transition_state.save()

        self.incident_report.incident_type = constants.LOSS
        self.incident_report.save()

        updated_transition = StateTransition.objects.get(id=self.transition_state.id)

        self.assertEqual(updated_transition.incident_report_state, constants.CLOSED)

    def test_update_transition_state_for_lost_item_under_out_for_repair(self):
        self.transition_state.incident_report_state = constants.OUT_FOR_REPAIR
        self.transition_state.save()

        self.incident_report.incident_type = constants.LOSS
        self.incident_report.save()

        updated_transition = StateTransition.objects.get(id=self.transition_state.id)

        self.assertEqual(updated_transition.incident_report_state, constants.CLOSED)

    def test_update_transition_state_for_lost_item_under_newly_reported(self):
        self.transition_state.incident_report_state = constants.NEWLY_REPORTED
        self.transition_state.save()

        self.incident_report.incident_type = constants.LOSS
        self.incident_report.save()

        updated_transition = StateTransition.objects.get(id=self.transition_state.id)

        self.assertEqual(
            updated_transition.incident_report_state, constants.NEWLY_REPORTED
        )

    def test_update_transition_state_for_damaged_item_under_newly_reported(self):
        self.transition_state.incident_report_state = constants.NEWLY_REPORTED
        self.transition_state.save()

        self.incident_report.incident_type = constants.DAMAGE
        self.incident_report.save()

        updated_transition = StateTransition.objects.get(id=self.transition_state.id)

        self.assertEqual(
            updated_transition.incident_report_state, constants.NEWLY_REPORTED
        )
