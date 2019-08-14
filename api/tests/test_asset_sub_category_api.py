# Standard Library
from unittest.mock import patch

# Third-Party Imports
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase
from core.models import AssetCategory

client = APIClient()


class Post_AssetCategoryAPITest(APIBaseTestCase):
    """ Tests for the AssetCategory endpoint"""

    def test_non_authenticated_user_get_asset_sub_category(self):
        data = {"name": "Monitor", "asset_category": self.asset_category.id}
        response = client.post(self.asset_sub_category_url, data=data)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_can_post_sub_category(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        data = {"name": "Monitor", "asset_category": self.asset_category.id}
        response = client.post(
            self.asset_sub_category_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], data["name"])
        self.assertEqual(response.data["asset_category"], self.asset_category.name)
        self.assertEqual(response.data["sub_category_name"], data["name"])

    @patch("api.authentication.auth.verify_id_token")
    def test_cannot_post_sub_category_with_empty_fields(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        data = {"name": "", "asset_category": self.asset_category.id}
        response = client.post(
            self.asset_sub_category_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["name"][0], "This field may not be null.")


class Get_AssetCategoryAPITest(APIBaseTestCase):
    def test_non_authenticated_user_get_asset_sub_category(self):
        response = client.get(self.asset_sub_category_url)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_can_get_all_sub_categories(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        response = client.get(
            self.asset_sub_category_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )

        self.assertEqual(len(response.data["results"]), AssetCategory.objects.count())
        self.assertEqual(
            response.data["results"][0]["name"], self.asset_sub_category.name
        )
        self.assertEqual(response.data["results"][0]["id"], self.asset_sub_category.id)
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_can_get_single_sub_category(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        response = client.get(
            f"{self.asset_sub_category_url}/{self.asset_sub_category.id}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )

        self.assertEqual(response.data["name"], self.asset_sub_category.name)
        self.assertEqual(response.data["id"], self.asset_sub_category.id)
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_cannot_get_sub_category_with_invalid_id(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            f"{self.asset_sub_category_url}/{300}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data["detail"], "Not found.")
        self.assertEqual(response.status_code, 404)


class Edit_AssetCategoryAPITest(APIBaseTestCase):
    @patch("api.authentication.auth.verify_id_token")
    def test_sub_categories_api_endpoint_put(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {"name": "Test Edit", "asset_category": self.asset_category.id}
        response = client.put(
            f"{self.asset_sub_category_url}/{self.asset_sub_category.id}/",
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data["name"], data["name"])
        self.assertEqual(response.data["id"], self.asset_sub_category.id)
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_cannot_update_sub_category_with_invalid_id(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {"name": "Test Edit", "asset_category": self.asset_category.id}
        response = client.put(
            f"{self.asset_sub_category_url}/{400}/",
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data["detail"], "Not found.")
        self.assertEqual(response.status_code, 404)

    @patch("api.authentication.auth.verify_id_token")
    def test_categories_api_endpoint_cant_allow_patch(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {}
        response = client.patch(
            self.asset_sub_category_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"detail": 'Method "PATCH" not allowed.'})
        self.assertEqual(response.status_code, 405)


class Delete_AssetCategoryAPITest(APIBaseTestCase):
    @patch("api.authentication.auth.verify_id_token")
    def test_can_delete_sub_category(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        data = {"name": "mouse", "asset_category": self.asset_category.id}
        response = client.post(
            self.asset_sub_category_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        response = client.delete(
            f"{self.asset_sub_category_url}/{response.data['id']}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.status_code, 204)

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_cannot_delete_sub_category_with_invalid_id(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        response = client.delete(
            f"{self.asset_sub_category_url}/{400}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data["detail"], "Not found.")
        self.assertEqual(response.status_code, 404)
