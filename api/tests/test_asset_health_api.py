# Standard Library
from unittest.mock import patch

# Third-Party Imports
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase
from core.models import AllocationHistory, Asset

User = get_user_model()
client = APIClient()


class AssetHealthTestCase(APIBaseTestCase):
    def test_non_authenticated_user_view_assets_health(self):
        response = client.get(self.asset_health_urls)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_non_admin_cannot_view_asset_health(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            self.asset_health_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.status_code, 403)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_admin_view_assets_health(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        AllocationHistory.objects.create(
            asset=self.asset, current_assignee=self.asset_assignee
        )
        allocated = Asset.objects.filter(current_status="Allocated").count()
        available = Asset.objects.filter(current_status="Available").count()
        damaged = Asset.objects.filter(current_status="Damaged").count()
        lost = Asset.objects.filter(current_status="Lost").count()
        response = client.get(
            self.asset_health_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data[0]["count_by_status"]["Allocated"], allocated)
        self.assertEqual(response.data[0]["count_by_status"]["Available"], available)
        self.assertEqual(response.data[0]["count_by_status"]["Damaged"], damaged)
        self.assertEqual(response.data[0]["count_by_status"]["Lost"], lost)
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_assets_health_api_endpoint_cant_allow_put(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        response = client.put(
            "{}/{}/".format(self.asset_health_urls, self.asset.serial_number),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data, {"detail": 'Method "PUT" not allowed.'})

    @patch("api.authentication.auth.verify_id_token")
    def test_assets_health_api_endpoint_cant_allow_patch(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        response = client.patch(
            self.asset_health_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data, {"detail": 'Method "PATCH" not allowed.'})

    @patch("api.authentication.auth.verify_id_token")
    def test_assets_health__endpoint_cant_allow_delete(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        response = client.delete(
            "{}/{}/".format(self.asset_health_urls, self.asset.serial_number),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data, {"detail": 'Method "DELETE" not allowed.'})

    @patch("api.authentication.auth.verify_id_token")
    def test_asset_type_in_asset_health_api(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            self.asset_health_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertIn("asset_type", response.data[0])
        self.assertEqual(response.data[0]["asset_type"], self.asset_type.name)
        self.assertEqual(response.status_code, 200)
