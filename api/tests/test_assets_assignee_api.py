# Standard Library
from unittest.mock import patch

# Third-Party Imports
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase
from core.models import AllocationHistory, Asset, AssetAssignee, AssetModelNumber

client = APIClient()


class AssetAssigneeAPITest(APIBaseTestCase):
    """ Tests for the AssetAssignee endpoint"""

    def setUp(self):
        self.assetmodel_2 = AssetModelNumber.objects.create(
            name="IMN509889", asset_make=self.asset_make
        )
        self.assetmodel_3 = AssetModelNumber.objects.create(
            name="IMN509887868", asset_make=self.asset_make
        )

        self.asset = Asset.objects.create(
            asset_code="IC001",
            serial_number="SN001",
            purchase_date="2018-07-10",
            current_status="Available",
            model_number=self.assetmodel,
        )

        self.asset_2 = Asset.objects.create(
            asset_code="IC002",
            serial_number="SN002",
            purchase_date="2018-07-12",
            current_status="Available",
            model_number=self.assetmodel_2,
        )

        self.asset_3 = Asset.objects.create(
            asset_code="IC003",
            serial_number="SN003",
            purchase_date="2018-07-14",
            current_status="Available",
            model_number=self.assetmodel_3,
        )

        self.allocation_user = AllocationHistory.objects.create(
            asset=self.asset, current_assignee=self.user.assetassignee
        )

        self.allocation_department = AllocationHistory.objects.create(
            asset=self.asset_2, current_assignee=self.department.assetassignee
        )

        self.allocation_workspace = AllocationHistory.objects.create(
            asset=self.asset_3, current_assignee=self.office_workspace.assetassignee
        )

    def test_non_authenticated_user_get_assets_assignee(self):
        response = client.get(self.asset_assignee_url)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_can_get_assets_assignee(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        response = client.get(
            self.asset_assignee_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn("assignee", response.data["results"][0].keys())
        self.assertEqual(len(response.data["results"]), AssetAssignee.objects.count())
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_assets_assignee_api_endpoint_cant_allow_put(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {}
        response = client.put(
            f"{self.asset_assignee_url}/{self.asset_assignee.id}/",
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"detail": 'Method "PUT" not allowed.'})
        self.assertEqual(response.status_code, 405)

    @patch("api.authentication.auth.verify_id_token")
    def test_assets_assignee_api_cant_allow_delete(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {}
        response = client.delete(
            self.asset_assignee_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"detail": 'Method "DELETE" not allowed.'})
        self.assertEqual(response.status_code, 405)
