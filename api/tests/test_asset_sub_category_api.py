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

    def test_non_authenticated_user_get_asset_sub_category(self):
        response = client.get(self.asset_sub_category_url)
        self.assertEqual(
            response.data, {'detail': 'Authentication credentials were not provided.'}
        )

    @patch('api.authentication.auth.verify_id_token')
    def test_can_post_sub_category(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.user.email}
        data = {"name": "Monitor", "asset_category": self.asset_category.id}
        response = client.post(
            self.asset_sub_category_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn("name", response.data.keys())
        self.assertIn(data["name"], response.data.values())
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_can_get_all_sub_categories(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.user.email}
        response = client.get(
            self.asset_sub_category_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )

        self.assertEqual(len(response.data['results']), AssetCategory.objects.count())
        self.assertIn("name", response.data['results'][0].keys())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_can_get_single_sub_category(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.user.email}
        response = client.get(
            f"{self.asset_sub_category_url}/{self.asset_sub_category.id}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )

        self.assertIn("name", response.data.keys())
        self.assertIn(self.asset_sub_category.name, response.data.values())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_sub_categories_api_endpoint_put(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        data = {'name': 'Test Edit', "asset_category": self.asset_category.id}
        response = client.put(
            f"{self.asset_sub_category_url}/{self.asset_sub_category.id}/",
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data.get('name'), 'Test Edit')

    @patch('api.authentication.auth.verify_id_token')
    def test_categories_api_endpoint_cant_allow_patch(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        data = {}
        response = client.patch(
            self.asset_sub_category_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {'detail': 'Method "PATCH" not allowed.'})
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_categories_api_endpoint_cant_allow_delete(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        data = {}
        response = client.delete(
            self.asset_sub_category_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {'detail': 'Method "DELETE" not allowed.'})
        self.assertEqual(response.status_code, 405)
