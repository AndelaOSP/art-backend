# Standard Library
from unittest.mock import patch

# Third-Party Imports
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase
from core.models import Asset

User = get_user_model()
client = APIClient()


class Get_AssetStatusAPITest(APIBaseTestCase):
    """Tests for the Asset Status API"""

    def test_non_authenticated_user_view_asset_status(self):
        response = client.get(self.asset_status_urls)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_view_asset_status(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            self.asset_status_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn(
            f"{self.asset.asset_code} - {self.asset.serial_number}",
            str(response.data["results"]),
        )
        self.assertEqual(len(response.data["results"]), Asset.objects.count())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][3]["id"], self.asset_status.id)
        self.assertEqual(
            response.data["results"][3]["current_status"],
            self.asset_status.current_status,
        )
        self.assertEqual(
            response.data["results"][3]["asset"],
            f"{self.asset.asset_code} - {self.asset.serial_number}",
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_view_single_asset_status(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            "{}/{}/".format(self.asset_status_urls, self.asset_status.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.asset_status.id)
        self.assertEqual(
            response.data["current_status"], self.asset_status.current_status
        )
        self.assertEqual(
            response.data["asset"],
            f"{self.asset.asset_code} - {self.asset.serial_number}",
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_cannot_get__asset_status_by_invalid_id(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            f"{self.asset_status_urls}/{300}",
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data["detail"], "Not found.")
        self.assertEqual(response.status_code, 404)


class post_AssetStatusAPITest(APIBaseTestCase):
    def test_non_authenticated_user_cannot_create_asset_status(self):
        data = {"asset": self.asset.id, "current_status": "Available"}
        response = client.post(self.asset_status_urls, data=data)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_post_asset_status(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {"asset": self.asset.id, "current_status": "Available"}
        response = client.post(
            self.asset_status_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data["current_status"], data["current_status"])
        self.assertEqual(
            response.data["asset"],
            f"{self.asset.asset_code} - {self.asset.serial_number}",
        )
        self.assertEqual(response.status_code, 201)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_post_invalid_serial_number(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {"asset": 100_000, "current_status": "Available"}
        response = client.post(
            self.asset_status_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(
            response.data, {"asset": ['Invalid pk "100000" - object does not exist.']}
        )

        self.assertEqual(response.status_code, 400)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_post_invalid_status(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {"asset": self.asset.id, "current_status": "Invalid"}
        response = client.post(
            self.asset_status_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(
            response.data, {"current_status": ['"Invalid" is not a valid choice.']}
        )

        self.assertEqual(response.status_code, 400)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_post_empty_payload(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {}
        response = client.post(
            self.asset_status_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"asset": ["This field is required."]})

        self.assertEqual(response.status_code, 400)


class Edit_AssetStatusAPITest(APIBaseTestCase):
    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_put_not_allowed(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {}
        response = client.put(
            "{}/{}/".format(self.asset_status_urls, self.asset_status.id),
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"detail": 'Method "PUT" not allowed.'})
        self.assertEqual(response.status_code, 405)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_patch_not_allowed(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {}
        response = client.patch(
            self.asset_status_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"detail": 'Method "PATCH" not allowed.'})
        self.assertEqual(response.status_code, 405)


class Delete_AssetStatusAPITest(APIBaseTestCase):
    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_delete_not_allowed(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.delete(
            self.asset_status_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"detail": 'Method "DELETE" not allowed.'})
        self.assertEqual(response.status_code, 405)
