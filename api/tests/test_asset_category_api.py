# Standard Library
from unittest.mock import patch

# Third-Party Imports
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase
from core.models import AssetCategory

client = APIClient()


class AssetCategoryAPITest(APIBaseTestCase):
    """ Tests for the AssetCategory endpoint"""

    @patch("api.authentication.auth.verify_id_token")
    def test_can_post_category(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        data = {"name": "computer"}
        response = client.post(
            self.category_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn("name", response.data.keys())
        self.assertIn(data["name"].title(), response.data.values())
        self.assertEqual(response.status_code, 201)

    @patch("api.authentication.auth.verify_id_token")
    def test_can_get_all_categories(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        response = client.get(
            self.category_url, HTTP_AUTHORIZATION="Token {}".format(self.token_user)
        )

        self.assertEqual(len(response.data["results"]), AssetCategory.objects.count())
        self.assertIn("name", response.data["results"][0].keys())
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_can_get_single_category(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        response = client.get(
            f"{self.category_url}/{self.asset_category.id}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )

        self.assertIn("name", response.data.keys())
        self.assertIn(self.asset_category.name, response.data.values())
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_categories_api_endpoint_cant_allow_put(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {"name": "Edited"}
        response = client.put(
            f"{self.category_url}/{self.asset_category.id}/",
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data.get("name"), "Edited")

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

    @patch("api.authentication.auth.verify_id_token")
    def test_categories_api_endpoint_cant_allow_delete(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {}
        response = client.delete(
            self.category_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"detail": 'Method "DELETE" not allowed.'})
        self.assertEqual(response.status_code, 405)

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
        # I am always sure that Electronics will be the last in the response
        #  since the categories are ordered.
        self.assertEqual(3, len(response.data.get("results")))
        self.assertEqual(response.data.get("results")[2].get("name"), "Electronics")
