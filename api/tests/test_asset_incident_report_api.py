from unittest.mock import patch
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from core.models import (
    Asset,
    AssetModelNumber,
    AssetMake,
    AssetType,
    AssetSubCategory,
    AssetCategory,
    User,
    AssetIncidentReport
)

from api.tests import APIBaseTestCase
client = APIClient()


class AssetIncidentReportAPITest(APIBaseTestCase):
    """ Tests for the AssetIncidentReport API """

    def setUp(self):
        super(AssetIncidentReportAPITest, self).setUp()
        asset_category = AssetCategory.objects.create(
            category_name="Computer")
        asset_sub_category = AssetSubCategory.objects.create(
            sub_category_name="Electronics", asset_category=asset_category)
        asset_type = AssetType.objects.create(
            asset_type="Accessory", asset_sub_category=asset_sub_category)
        make_label = AssetMake.objects.create(
            make_label="Sades", asset_type=asset_type)
        self.assetmodel = AssetModelNumber(
            model_number='IMN50987', make_label=make_label)
        self.test_assetmodel = AssetModelNumber(
            model_number="IMN50987", make_label=make_label)
        self.test_assetmodel.save()

        self.user = User.objects.create_user(
            email='user@site.com', cohort=20,
            slack_handle='@admin', password='devpassword'
        )
        self.token_user = 'token'
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
            witnesses="John Doe",
            police_abstract_obtained="Yes"
        )
        self.incident_report_url = reverse('incidence-reports-list')

        self.count_before = AssetIncidentReport.objects.count()

    def test_non_authenticated_user_view_incident_report(self):
        response = client.get(self.incident_report_url)
        self.assertEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_post_incident_report(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        data = {
            "asset": self.test_asset.id,
            "incident_type": "Loss",
            "incident_location": "CDB",
            "incident_description": "Lorem Ipsum",
            "injuries_sustained": "N/a",
            "loss_of_property": "Mobile Phone",
            "witnesses": "John Doe +2347548458457",
            "police_abstract_obtained": "Yes"
        }
        response = client.post(
            f"{self.incident_report_url}",
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn(self.test_asset.id, response.data.values())
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_post_invalid_incident_type(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        data = {
            "asset": self.test_asset.id,
            "incident_type": "Invalid",
            "incident_location": "CDB",
            "incident_description": "Lorem Ipsum",
            "injuries_sustained": "N/a",
            "loss_of_property": "Mobile Phone",
            "witnesses": "John Doe +2347548458457",
            "police_abstract_obtained": "Yes"
        }
        response = client.post(
            f"{self.incident_report_url}",
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEquals(response.data, {
            'incident_type': ['"Invalid" is not a valid choice.']})
        self.assertEqual(response.status_code, 400)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_post_empty_incident_fields(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        data = {
            "asset": self.test_asset.id,
            "incident_type": "Loss",
            "incident_location": "",
            "incident_description": "Lorem",
            "police_abstract_obtained": "Yes"
        }
        response = client.post(
            f"{self.incident_report_url}",
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEquals(response.data, {
            'incident_location': ['This field may not be blank.']})
        self.assertEqual(response.status_code, 400)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_get_incident_report(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.get(
            f"{self.incident_report_url}",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn(self.incident_report.id,
                      response.data[0].values())
        self.assertEqual(len(response.data),
                         AssetIncidentReport.objects.count())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_get_single_incident_report(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.get(
            f"{self.incident_report_url}/{self.incident_report.id}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn(self.incident_report.id, response.data.values())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_cant_allow_put_incident_report(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.put(
            f"{self.incident_report_url}",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PUT" not allowed.'
        })
        self.assertEquals(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_cant_allow_patch_incident_report(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.patch(
            f"{self.incident_report_url}",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PATCH" not allowed.'
        })
        self.assertEquals(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_cant_allow_delete_incident_report(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.delete(
            f"{self.incident_report_url}",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "DELETE" not allowed.'
        })
        self.assertEquals(response.status_code, 405)
