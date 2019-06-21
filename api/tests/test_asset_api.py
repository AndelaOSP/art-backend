# Standard Library
from unittest.mock import patch

# Third-Party Imports
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase
from core.models import AllocationHistory, Asset, AssetLog, AssetStatus

User = get_user_model()
client = APIClient()


class AssetTestCase(APIBaseTestCase):
    def setUp(self):
        AssetStatus.objects.create(asset=self.asset, current_status="Available")
        AllocationHistory.objects.create(
            asset=self.asset, current_assignee=self.asset_assignee
        )

    def test_non_authenticated_user_view_assets(self):
        response = client.get(self.asset_urls)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_assignee_view_assets(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            self.asset_urls, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        self.assertIn(self.asset.asset_code, response.data["results"][0].values())
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_securityuser_view_assets_in_their_department_and_location(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.security_user.email}
        response = client.get(
            self.asset_urls, HTTP_AUTHORIZATION="Token {}".format(self.token_checked_by)
        )
        self.assertIn(self.asset.asset_code, str(response.json().values()))
        self.assertEqual(len(response.data["results"]), Asset.objects.count())
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_get_single_asset(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            "{}/{}/".format(self.asset_urls, self.asset.uuid),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn(self.asset.asset_code, response.data.values())
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_get_single_asset_via_asset_code(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            "{}?asset_code={}".format(self.asset_urls, self.asset.asset_code),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn(self.asset.asset_code, response.data["results"][0]["asset_code"])
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_securityuser_get_single_asset_via_asset_code(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.security_user.email}
        response = client.get(
            "{}?asset_code={}".format(self.asset_urls, self.asset.asset_code),
            HTTP_AUTHORIZATION="Token {}".format(self.token_checked_by),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.asset.asset_code, response.data["results"][0]["asset_code"])

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_get_single_asset_via_serial_number(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            "{}?serial_number={}".format(self.asset_urls, self.asset.serial_number),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn(
            self.asset.serial_number, response.data["results"][0]["serial_number"]
        )
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_securityuser_get_single_asset_via_serial_number(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.security_user.email}
        response = client.get(
            "{}?serial_number={}".format(self.asset_urls, self.asset.serial_number),
            HTTP_AUTHORIZATION="Token {}".format(self.token_checked_by),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            self.asset.serial_number, response.data["results"][0]["serial_number"]
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_assets_api_endpoint_cant_allow_put(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.put(
            "{}/{}/".format(self.asset_urls, self.asset.uuid),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"detail": 'Method "PUT" not allowed.'})

    @patch("api.authentication.auth.verify_id_token")
    def test_assets_api_endpoint_cant_allow_patch(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.patch(
            "{}/{}/".format(self.asset_urls, self.asset.uuid),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"detail": 'Method "PATCH" not allowed.'})

    @patch("api.authentication.auth.verify_id_token")
    def test_assets_api_endpoint_cant_allow_delete(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.delete(
            "{}/{}/".format(self.asset_urls, self.asset.uuid),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"detail": 'Method "DELETE" not allowed.'})

    @patch("api.authentication.auth.verify_id_token")
    def test_asset_filter_by_email(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            "{}?email={}".format(self.asset_urls, self.user.email),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn(
            self.user.email, response.data["results"][0]["assigned_to"]["email"]
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_non_admin_cannot_filter_asset_by_asset_status(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        url = reverse("manage-assets-list")
        response = client.get(
            "{}?current_status={}".format(url, "Allocated"),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(
            response.data,
            {"detail": "You do not have permission to perform this action."},
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_can_filter_asset_by_asset_status(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        url = reverse("manage-assets-list")
        response = client.get(
            "{}?current_status={}".format(url, "Allocated"),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )

        self.assertEqual(response.data["count"], 1)

        response = client.get(
            "{}?current_status={}".format(url, "Available"),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        count = response.data.get("count")
        Asset(
            asset_code="IC002",
            serial_number="SN002",
            model_number=self.assetmodel,
            purchase_date="2018-07-10",
            asset_location=self.centre,
            department=self.department,
        ).save()
        response = client.get(
            "{}?current_status={}".format(url, "Available"),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data["count"], count + 1)

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_can_filter_asset_by_assignee_department(self, mock_verify_id_token):
        self.asset_3.assigned_to = self.asset_assignee_department
        self.asset_3.save()
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            "{}?department={}".format(
                self.manage_asset_urls, self.department_travel.id
            ),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        returned_data = response.data["results"][0]

        self.assertEqual(returned_data["id"], self.asset_3.id)
        self.assertEqual(returned_data["asset_category"], self.asset_3.asset_category)
        self.assertEqual(
            returned_data["asset_sub_category"], self.asset_3.asset_sub_category
        )
        self.assertEqual(returned_data["asset_make"], self.asset_3.asset_make)
        self.assertEqual(returned_data["asset_code"], self.asset_3.asset_code)
        self.assertEqual(returned_data["asset_type"], self.asset_3.asset_type)
        self.assertEqual(returned_data["serial_number"], self.asset_3.serial_number)
        self.assertEqual(
            returned_data["asset_location"], self.asset_3.asset_location.name
        )
        self.assertEqual(
            returned_data["assigned_to"]["id"],
            self.asset_assignee_department.department_id,
        )
        self.assertEqual(
            len(response.data["results"]),
            Asset.objects.filter(assigned_to=self.asset_assignee_department.id).count(),
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_assets_detail_api_endpoint_contain_assigned_to_details(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            "{}/{}/".format(self.asset_urls, self.asset.uuid),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn(self.user.email, response.data["assigned_to"].values())
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_assets_assigned_to_details_has_no_password(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            "{}/{}/".format(self.asset_urls, self.asset.uuid),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertNotIn("password", response.data["assigned_to"].keys())
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_checkin_status_for_non_checked_asset(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            "{}/{}/".format(self.asset_urls, self.asset.uuid),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn("checkin_status", response.data.keys())
        self.assertEqual(response.data["checkin_status"], None)
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_checkin_status_for_checked_in_asset(self, mock_verify_id_token):
        AssetLog.objects.create(
            checked_by=self.security_user, asset=self.asset, log_type="Checkin"
        )

        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            "{}/{}/".format(self.asset_urls, self.asset.uuid),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn("checkin_status", response.data.keys())
        self.assertEqual(response.data["checkin_status"], "checked_in")
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_checkin_status_for_checkout_in_asset(self, mock_verify_id_token):
        AssetLog.objects.create(
            checked_by=self.security_user, asset=self.asset, log_type="Checkout"
        )
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            "{}/{}/".format(self.asset_urls, self.asset.uuid),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn("checkin_status", response.data.keys())
        self.assertEqual(response.data["checkin_status"], "checked_out")
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_asset_type_in_asset_api(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            "{}/{}/".format(self.asset_urls, self.asset.uuid),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn("asset_type", response.data.keys())
        self.assertEqual(response.data["asset_type"], self.asset_type.name)
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_assets_have_allocation_history(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            "{}/{}/".format(self.asset_urls, self.asset.uuid),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn("allocation_history", response.data.keys())
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_assets_have_asset_category(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            "{}/{}/".format(self.asset_urls, self.asset.uuid),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn("asset_category", response.data.keys())
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_assets_have_asset_sub_category(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            "{}/{}/".format(self.asset_urls, self.asset.uuid),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn("asset_sub_category", response.data.keys())
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_assets_have_asset_make(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            "{}/{}/".format(self.asset_urls, self.asset.uuid),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn("asset_make", response.data.keys())
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_assets_have_notes(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            "{}/{}/".format(self.asset_urls, self.asset.uuid),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn("notes", response.data.keys())
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_can_filter_assets_by_verified_status(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        url = reverse("manage-assets-list")
        res = client.get(
            "{}?verified={}".format(url, self.asset.verified),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        count = res.data["count"]
        Asset.objects.create(
            asset_code="IC0014532",
            serial_number="SN50123455",
            purchase_date="2018-07-10",
            model_number=self.assetmodel,
            asset_location=self.centre,
            department=self.department,
            verified=True,
        )
        response = client.get(
            "{}?verified={}".format(url, self.asset.verified),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data["count"], count + 1)
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_asset_allocation_history_has_assigner(self, mock_verify_id_token):
        """When I request to view an asset
        Then I should see the list of allocation history
        with timestamps and the list of people who assigned it
        in different instances"""

        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            "{}/{}/".format(self.asset_urls, self.asset.uuid),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn("assigner", response.data["allocation_history"][0].keys())
        self.assertEqual(response.status_code, 200)
