# Standard Library
import os
from unittest.mock import patch

# Third-Party Imports
from django.test import override_settings
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase
from core import constants
from core.models import AllocationHistory, AssetType, User

client = APIClient()


class AssetCategoryAPITest(APIBaseTestCase):
    """ Tests for the AssetCategory endpoint"""

    def test_non_authenticated_user_get_asset_sub_category(self):
        response = client.get(self.asset_type_url)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_can_post_asset_type(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {
            "name": "Asset Type Example",
            "asset_sub_category": self.asset_sub_category.id,
            "threshold": 50,
        }
        response = client.post(
            self.asset_type_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertIn("name", response.data.keys())
        self.assertIn(data["name"], response.data.values())
        self.assertEqual(response.status_code, 201)

    @patch("api.authentication.auth.verify_id_token")
    def test_can_get_all_asset_types(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            self.asset_type_url, HTTP_AUTHORIZATION="Token {}".format(self.token_admin)
        )

        self.assertEqual(len(response.data["results"]), AssetType.objects.count())
        self.assertIn("name", response.data["results"][0].keys())
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_can_get_single_asset_type(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            f"{self.asset_type_url}/{self.asset_type.id}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )

        self.assertIn("name", response.data.keys())
        self.assertIn(self.asset_type.name, response.data.values())
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_asset_type_api_endpoint_cant_allow_put(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {"name": "Test Edit", "asset_sub_category": self.asset_sub_category.id}
        response = client.put(
            f"{self.asset_type_url}/{self.asset_type.id}/",
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data.get("name"), "Test Edit")

    @patch("api.authentication.auth.verify_id_token")
    def test_asset_type_api_endpoint_cant_allow_patch(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {}
        response = client.patch(
            self.asset_type_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data, {"detail": 'Method "PATCH" not allowed.'})
        self.assertEqual(response.status_code, 405)

    @patch("api.authentication.auth.verify_id_token")
    def test_asset_type_api_endpoint_cant_allow_delete(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {}
        response = client.delete(
            self.asset_type_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data, {"detail": 'Method "DELETE" not allowed.'})
        self.assertEqual(response.status_code, 405)

    @patch("api.authentication.auth.verify_id_token")
    def test_asset_type_api_orders_asset_types_by_type(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        AssetType.objects.create(name="HP", asset_sub_category=self.asset_sub_category)
        AssetType.objects.create(
            name="Samsung", asset_sub_category=self.asset_sub_category
        )
        AssetType.objects.create(
            name="Lenovo", asset_sub_category=self.asset_sub_category
        )

        response = client.get(
            self.asset_type_url, HTTP_AUTHORIZATION="Token {}".format(self.token_admin)
        )
        # I am always sure that 'Samsung' will be the last in the response
        #  since the asset types are ordered.
        self.assertEqual(AssetType.objects.count(), len(response.data.get("results")))
        self.assertEqual(response.data.get("results")[-1].get("name"), "Samsung")

    @patch("api.send_email.async_task")
    @patch("api.authentication.auth.verify_id_token")
    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_email_is_sent_when_asset_type_threshold_critical(
        self, mock_verify_token, mail
    ):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        assettype = AssetType(
            name="Andelaheadsets",
            asset_sub_category=self.asset_sub_category,
            threshold=20,
        )
        assettype.save()
        self.asset_make.asset_type = assettype
        self.asset_make.save()
        allocate = AllocationHistory(
            asset=self.asset_1, current_assignee=self.asset_assignee
        )
        allocate.save()
        data = User.objects.filter(is_staff=True)
        emails = mail._mock_call_args_list[0]
        self.assertEqual(emails[0][1], constants.SUBJECT)
        self.assertEqual(emails[0][3], os.getenv("EMAIL_SENDER"))
        self.assertEqual(emails[0][2], constants.MSG.format(assettype.name))
        self.assertEqual(emails[0][4][0], data[0].email)
