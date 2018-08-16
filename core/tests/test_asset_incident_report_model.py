from core.tests import CoreBaseTestCase

from ..models import (
    Asset,
    AssetModelNumber,
    AssetMake,
    AssetType,
    AssetSubCategory,
    AssetCategory,
    User,
    AssetIncidentReport,
    AssetAssignee)


class AssetIncidentReportModelTest(CoreBaseTestCase):
    """ Tests for the AssetIncidentReport Model """

    def setUp(self):
        super(AssetIncidentReportModelTest, self).setUp()
        asset_category = AssetCategory.objects.create(
            category_name="Computer")
        asset_sub_category = AssetSubCategory.objects.create(
            sub_category_name="Electronics", asset_category=asset_category)
        asset_type = AssetType.objects.create(
            asset_type="Accessory", asset_sub_category=asset_sub_category)
        make_label = AssetMake.objects.create(
            make_label="Sades", asset_type=asset_type)
        self.test_assetmodel = AssetModelNumber(
            model_number="12345", make_label=make_label)
        self.test_assetmodel.save()

        self.user = User.objects.create(
            email='andela@gmail.com', cohort=0,
            slack_handle='ndel', password='wakanda1'
        )
        self.asset_assignee = AssetAssignee.objects.get(user=self.user)
        self.test_asset = Asset(
            asset_code="qaz123",
            serial_number="123qaz",
            model_number=self.test_assetmodel,
            assigned_to=self.asset_assignee,
            purchase_date="2018-07-10"
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
            police_abstract_obtained="Yes",
            submitted_by=self.user
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

    def test_incident_report_contain_submitted_by(self):
        self.assertEqual(self.incident_report.submitted_by, self.user)
