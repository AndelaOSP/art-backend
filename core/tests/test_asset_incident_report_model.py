from core.models import Asset, AssetModelNumber, User, AssetIncidentReport
from core.tests import CoreBaseTestCase


class AssetIncidentReportModelTest(CoreBaseTestCase):
    """ Tests for the AssetIncidentReport Model """

    def setUp(self):
        super(AssetIncidentReportModelTest, self).setUp()
        self.test_assetmodel = AssetModelNumber(model_number="12345")
        self.test_assetmodel.save()

        self.user = User.objects.create(
            email='andela@gmail.com', cohort=0,
            slack_handle='ndel', password='wakanda1'
        )
        self.test_asset = Asset(
            asset_code="qaz123",
            serial_number="123qaz",
            model_number=self.test_assetmodel,
            assigned_to=self.user
        )
        self.test_asset.save()

        self.incident_report = AssetIncidentReport.objects.create(
            asset=self.test_asset,
            incident_type="Loss",
            incident_location="44",
            incident_description="Mugging",
            injuries_sustained="Black eye",
            loss_of_property="Laptop",
            witnesses="Omosh wa mtura",
            police_abstract_obtained="Yes"
        )
        self.count_before = AssetIncidentReport.objects.count()

    def test_add_incident_report(self):
        AssetIncidentReport.objects.create(
            asset=self.test_asset,
            incident_type="Loss",
            incident_location="CBD",
            incident_description="Mugging",
            police_abstract_obtained="Yes"
        )
        self.assertEqual(
            AssetIncidentReport.objects.count(), self.count_before + 1)

    def test_edit_incident_report(self):
        self.incident_report.witnesses = "John Doe"
        self.incident_report.save()
        self.assertEqual(AssetIncidentReport.objects.get(
            id=self.incident_report.id).witnesses, "John Doe")

    def test_delete_incident_report(self):
        self.incident_report.delete()
        self.assertEqual(AssetIncidentReport.objects.count(),
                         self.count_before - 1)

    def test_model_string_representation(self):
        self.assertEqual(str(self.incident_report),
                         f"{self.incident_report.incident_type}: "
                         f"{self.incident_report.asset}")
