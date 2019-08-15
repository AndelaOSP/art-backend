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

    def test_non_authenticated_users_cannot_add_asset_category(self):
        data = {"name": "computer"}
        response = client.post(self.category_url, data=data)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    def test_add_asset_category_with_invlaid_token(self):
        data = {"name": "computer"}
        response = client.post(
            self.category_url, data=data, HTTP_AUTHORIZATION="Token token"
        )
        self.assertEqual(response.data["detail"], "User not found")
        self.assertEqual(response.status_code, 401)

    @patch("api.authentication.auth.verify_id_token")
    def test_can_post_category(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        data = {"name": "computer"}
        response = client.post(
            self.category_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(data["name"].title(), response.data["name"])
        self.assertEqual(data["name"].title(), response.data["category_name"])
        self.assertEqual(response.status_code, 201)

    @patch("api.authentication.auth.verify_id_token")
    def test_cannot_post_category_with_empty_values(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        data = {"name": ""}
        response = client.post(
            self.category_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data["name"][0], "This field may not be null.")
        self.assertEqual(response.status_code, 400)


class Get_AssetCategoryAPITest(APIBaseTestCase):
    def test_non_authenticated_users_cannot_get_asset_categories(self):
        response = client.get(self.category_url)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_can_get_all_categories(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        response = client.get(
            self.category_url, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )

        self.assertEqual(len(response.data["results"]), AssetCategory.objects.count())
        self.assertEqual(self.asset_category.name, response.data["results"][0]["name"])
        self.assertEqual(self.asset_category.id, response.data["results"][0]["id"])
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_can_get_single_category(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        response = client.get(
            f"{self.category_url}/{self.asset_category.id}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(self.asset_category.name, response.data["name"])
        self.assertEqual(self.asset_category.id, response.data["id"])
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_cannot_get_asset_category_with_invalid_id(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        response = client.get(
            f"{self.category_url}/{400}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data["detail"], "Not found.")
        self.assertEqual(response.status_code, 404)

    @patch("api.authentication.auth.verify_id_token")
    def test_categories_api_endpoint_orders_categories_by_name_by_default(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.user.email}
        AssetCategory.objects.create(name="Electronics")
        AssetCategory.objects.create(name="Computer Accessories")
        response = client.get(
            self.category_url, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )
        self.assertEqual(3, len(response.data.get("results")))
        self.assertEqual(response.data.get("results")[2].get("name"), "Electronics")


class Edit_AssetCategoryAPITest(APIBaseTestCase):
    @patch("api.authentication.auth.verify_id_token")
    def test_editing_categories_api_endpoint(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {"name": "Edited"}
        response = client.put(
            f"{self.category_url}/{self.asset_category.id}/",
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data.get("name"), "Edited")
        self.assertEqual(self.asset_category.id, response.data["id"])
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_cannot_edit_category_with_invalid_id(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {"name": "Edit"}
        response = client.put(
            f"{self.category_url}/{40}/",
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
            self.category_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"detail": 'Method "PATCH" not allowed.'})
        self.assertEqual(response.status_code, 405)


class Delete_AssetCategoryAPITest(APIBaseTestCase):
    @patch("api.authentication.auth.verify_id_token")
    def test_delete_asset_categories_api_endpoint(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {"name": "macbookPros"}
        res = client.post(
            self.category_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        response = client.delete(
            f"{self.category_url}/{res.data['id']}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.status_code, 204)

    @patch("api.authentication.auth.verify_id_token")
    def test_cannot_delete_asset_categories_api_with_invalid_id(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.user.email}
        response = client.delete(
            f"{self.category_url}/{50}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data["detail"], "Not found.")
        self.assertEqual(response.status_code, 404)
