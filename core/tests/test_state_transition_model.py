# App Imports
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
            state="Newly reported",
        )
        self.assertEqual(AssetIncidentReport.objects.count(), incident_report_count + 1)
        self.assertEqual(StateTransition.objects.count(), state_transition_count + 1)
