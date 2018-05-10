from django.test import TestCase
from unittest.mock import patch
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from core.models import User, AssetCategory

client = APIClient()


class AssetCategoryAPITest(TestCase):
    """ Tests for the AssetCategory endpoint"""

    def setUp(self):
        self.user = User.objects.create(
            email='testuser@gmail.com', cohort=19,
            slack_handle='tester', password='qwerty123'
        )

        self.asset_category = AssetCategory.objects.create(
            category_name="Accessories"
        )

        self.category_url = reverse('asset-categories-list')
        self.token_user = 'testtoken'

    @patch('api.authentication.auth.verify_id_token')
    def test_can_post_category(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.user.email}
        data = {
            "category_name": "computer"
        }
        response = client.post(
            self.category_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn("category_name", response.data.keys())
        self.assertIn(data["category_name"], response.data.values())
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_can_get_all_categories(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.user.email}
        response = client.get(
            self.category_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))

        self.assertEqual(len(response.data), AssetCategory.objects.count())
        self.assertIn("category_name", response.data[0].keys())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_can_get_single_category(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.user.email}
        response = client.get(
            f"{self.category_url}{self.asset_category.id}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))

        self.assertIn("category_name", response.data.keys())
        self.assertIn(self.asset_category.category_name,
                      response.data.values())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_categories_api_endpoint_cant_allow_put(self,
                                                    mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        data = {}
        response = client.put(
            self.category_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PUT" not allowed.'
        })
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_categories_api_endpoint_cant_allow_patch(self,
                                                      mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        data = {}
        response = client.patch(
            self.category_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PATCH" not allowed.'
        })
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_categories_api_endpoint_cant_allow_delete(self,
                                                       mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        data = {}
        response = client.delete(
            self.category_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "DELETE" not allowed.'
        })
        self.assertEqual(response.status_code, 405)
