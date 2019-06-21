# Standard Library
from unittest.mock import patch

# Third-Party Imports
from django.apps import apps
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase
from core.models import AllocationHistory, Asset

User = get_user_model()
client = APIClient()


class PrintAssetsDetailsTestCase(APIBaseTestCase):
    def test_non_authenticated_user_print_assets(self):
        response = client.get(self.print_asset_url)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_non_admin_cannot_print_asset(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            self.print_asset_url, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        self.assertEqual(response.status_code, 403)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_admin_can_print_assets(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            self.print_asset_url, HTTP_AUTHORIZATION="Token {}".format(self.token_admin)
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.json().keys())

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_admin_cant_print_assets_in_diffrent_location(
        self, mock_verify_id_token
    ):
        country = apps.get_model("core", "Country").objects.create(name="Nigeria")
        centre = apps.get_model("core", "AndelaCentre").objects.create(
            name="Epic Towers", country=country
        )
        admin_user = User.objects.create_superuser(
            email="newadmin@andela.com",
            cohort=2,
            password="adminZpassword",
            location=centre,
        )
        token_admin = "admintesttoken"
        mock_verify_id_token.return_value = {"email": admin_user.email}
        response = client.get(
            self.print_asset_url, HTTP_AUTHORIZATION="Token {}".format(token_admin)
        )
        self.assertEqual(response.status_code, 400)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_admin_put_not_allowed(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {}
        response = client.put(
            self.print_asset_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data, {"detail": 'Method "PUT" not allowed.'})
        self.assertEqual(response.status_code, 405)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_admin_patch_not_allowed(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {}
        response = client.patch(
            self.print_asset_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data, {"detail": 'Method "PATCH" not allowed.'})
        self.assertEqual(response.status_code, 405)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_admin_delete_not_allowed(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        response = client.delete(
            self.print_asset_url, HTTP_AUTHORIZATION="Token {}".format(self.token_admin)
        )
        self.assertEqual(response.data, {"detail": 'Method "DELETE" not allowed.'})
        self.assertEqual(response.status_code, 405)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_admin_can_print_assets_with_filters(
        self, mock_verify_id_token
    ):
        Asset.objects.create(
            asset_code="IC00145328",
            serial_number="SN50123455S",
            model_number=self.assetmodel,
            asset_location=self.centre,
        )
        available_assets = Asset.objects.filter(current_status="Available")
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            "{}?current_status=Available".format(self.print_asset_url),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "{} assets exported".format(available_assets.count()),
            response.data["success"],
        )

        AllocationHistory.objects.create(
            asset=available_assets[0], current_assignee=self.user.assetassignee
        )
        available_assets = Asset.objects.filter(current_status="Available")
        response = client.get(
            "{}?current_status=Available".format(self.print_asset_url),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "{} assets exported".format(available_assets.count()),
            response.data["success"],
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_admin_can_print_assets_with_multiple_filters(
        self, mock_verify_id_token
    ):
        Asset.objects.create(
            asset_code="IC00145328",
            serial_number="SN50123455S",
            model_number=self.assetmodel,
            asset_location=self.centre,
        )
        available_assets = Asset.objects.filter(
            Q(current_status="Available") | Q(current_status="Allocated")
        )
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        AllocationHistory.objects.create(
            asset=available_assets[0], current_assignee=self.user.assetassignee
        )
        response = client.get(
            "{}?current_status=Available&current_status=Allocated".format(
                self.print_asset_url
            ),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "{} assets exported".format(available_assets.count()),
            response.data["success"],
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_admin_can_print_assets_with_invalid_filters(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            "{}?test=test".format(self.print_asset_url),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.status_code, 400)
