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


class Get_AssetConditionAPITest(APIBaseTestCase):
    """ Tests for the AssetCondition endpoint"""

    def test_non_authenciated_user_can_view_asset_condition(self):
        response = client.get(self.asset_condition_urls)
        self.assertEqual(response.status_code, 401)

    def test_view_asset_condition_with_invlaid_token_fails(self):
        response = client.get(
            self.asset_condition_urls,
            HTTP_AUTHORIZATION="Token token",
        )
        self.assertEqual(response.data['detail'],'User not found')
        self.assertEqual(response.status_code, 401)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenciated_user_can_view_asset_conditions(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.get(
            self.asset_condition_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(
            self.asset_condition.notes, response.data["results"][0]["notes"]
        )
        self.assertEqual(self.asset_condition.id, response.data["results"][0]["id"])
        asset = f"{self.asset_condition.asset.serial_number} - {self.asset_condition.asset.asset_code}"
        self.assertEqual(response.data["results"][0]["asset"], asset)
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_can_get_single_asset_condition(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.user.email}
        test_asset = Asset(
            asset_code="IC002",
            serial_number="SN002",
            model_number=self.assetmodel,
            purchase_date="2018-07-10",
            asset_location=self.centre,
        )
        test_asset.save()
        data = {"asset": test_asset.id, "notes": "working perfectly"}
        new_asset_condition = client.post(
            self.asset_condition_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(new_asset_condition.status_code, 201)
        response = client.get(
            "{}/{}/".format(self.asset_condition_urls, new_asset_condition.data["id"]),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data["id"], new_asset_condition.data["id"])
        self.assertEqual(new_asset_condition.data["notes"], response.data["notes"])
        asset = f"{test_asset.serial_number} - {test_asset.asset_code}"
        self.assertEqual(response.data["asset"], asset)
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_cannot_get_asset_condition_with_invalid_id(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        response = client.get(
            "{}/{}/".format(self.asset_condition_urls, 100),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data["detail"], "Not found.")
        self.assertEqual(response.status_code, 404)


class Post_AssetConditionAPITest(APIBaseTestCase):
    def test_non_authenciated_user_cannot_post_asset_condition(self):
        data = {"asset": self.asset.id, "notes": "working perfectly"}
        response = client.post(self.asset_condition_urls, data=data)
        self.assertEqual(response.status_code, 401)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_can_edit_asset_condition(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {"asset": self.asset.id, "notes": "working perfectly"}
        response = client.post(
            self.asset_condition_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn(data["notes"], response.data.values())
        self.assertEqual(response.status_code, 201)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_cannot_post_asset_condition_with_empty_fields(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {"asset": self.asset.id, "notes": ""}
        response = client.post(
            self.asset_condition_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data["notes"][0], "This field may not be blank.")
        self.assertEqual(response.status_code, 400)


class Edit_AssetConditionAPITest(APIBaseTestCase):
    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_condition_api_endpoint_put(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {"asset": self.asset.id, "notes": "note edit"}
        response = client.put(
            "{}/{}/".format(self.asset_condition_urls, self.asset_condition.id),
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data.get("notes"), "note edit")
        self.assertEqual(response.data["id"], self.asset_condition.id)
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_cannot_update_asset_condition_with_invalid_id(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {"asset": self.asset.id, "notes": "note edit"}
        response = client.put(
            "{}/{}/".format(self.asset_condition_urls, 200),
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data["detail"], "Not found.")
        self.assertEqual(response.status_code, 404)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_condition_api_endpoint_cannot_allow_patch(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.patch(
            self.asset_condition_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.status_code, 405)


class Delete_AssetConditionAPITest(APIBaseTestCase):
    @patch("api.authentication.auth.verify_id_token")
    def test_condition_api_endpoint_cannot_allow_delete(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.delete(
            "{}/{}/".format(self.asset_condition_urls, self.asset_condition.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.status_code, 204)

    @patch("api.authentication.auth.verify_id_token")
    def test_authenticated_user_cannot_delete_asset_condition_with_invalid_id(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.delete(
            "{}/{}/".format(self.asset_condition_urls, 200),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data["detail"], "Not found.")
        self.assertEqual(response.status_code, 404)
