# App Imports
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
            submitted_by=self.user
        )
        self.assertEqual(str(incident_report), f"{incident_report.incident_type}: {incident_report.asset}")
