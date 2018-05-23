from django.test import TestCase
from core.models import Asset, AssetModelNumber, User, AssetIncidentReport


class AssetIncidentReportModelTest(TestCase):
    """ Tests for the AssetIncidentReport Model """

    def setUp(self):
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
            police_abstract_obtained=True
        )
        self.incident_report = AssetIncidentReport.objects.all()

    def test_can_save_incident_report(self):
        self.incident_report = AssetIncidentReport.objects.create(
            asset=self.test_asset,
            incident_type="Loss",
            incident_location="44",
            incident_description="Mugging",
            injuries_sustained="Black eye",
            loss_of_property="Laptop",
            witnesses="Omosh wa mtura",
            police_abstract_obtained=True
        )
        self.assertEqual(AssetIncidentReport.objects.count(), 2)

    def test_cannot_submit_invalid_incident_type(self):
        self.incident_report = AssetIncidentReport.objects.create(
            asset=self.test_asset,
            incident_type="Invalid",
            incident_location="44",
            incident_description="Mugging",
            injuries_sustained="Black eye",
            loss_of_property="Laptop",
            witnesses="Omosh wa mtura",
            police_abstract_obtained=True
        )
        self.assertEqual(AssetIncidentReport.objects.count(), 2)

    def test_cannot_submit_without_incident_location(self):
        self.incident_report = AssetIncidentReport.objects.create(
            asset=self.test_asset,
            incident_type="Loss",
            incident_description="Mugging",
            injuries_sustained="Black eye",
            loss_of_property="Laptop",
            witnesses="Omosh wa mtura",
            police_abstract_obtained=True
        )
        self.assertEqual(AssetIncidentReport.objects.count(), 2)
