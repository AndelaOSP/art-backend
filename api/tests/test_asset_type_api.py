from django.test import TestCase
from unittest.mock import patch
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from core.models import User, AssetCategory, AssetSubCategory, \
    AssetType

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
        self.asset_sub_category = AssetSubCategory.objects.create(
            sub_category_name="Key Board",
            asset_category=self.asset_category
        )
        self.asset_type = AssetType.objects.create(
            asset_type="Dell",
            asset_sub_category=self.asset_sub_category
        )

        self.asset_type_url = reverse('asset-types-list')
        self.token_user = 'testtoken'

    def test_non_authenticated_user_get_asset_sub_category(self):
        response = client.get(self.asset_type_url)
        self.assertEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_can_post_asset_type(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.user.email}
        data = {
            "asset_type": "Asset Type Example",
            "asset_sub_category": self.asset_sub_category.id
        }
        response = client.post(
            self.asset_type_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn("asset_type", response.data.keys())
        self.assertIn(data["asset_type"], response.data.values())
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_can_get_all_asset_types(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.user.email}
        response = client.get(
            self.asset_type_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))

        self.assertEqual(len(response.data), AssetCategory.objects.count())
        self.assertIn("asset_type", response.data[0].keys())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_can_get_single_asset_type(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.user.email}
        response = client.get(
            f"{self.asset_type_url}{self.asset_type.id}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))

        self.assertIn("asset_type", response.data.keys())
        self.assertIn(self.asset_type.asset_type,
                      response.data.values())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_type_api_endpoint_cant_allow_put(self,
                                                    mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        data = {}
        response = client.put(
            self.asset_type_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PUT" not allowed.'
        })
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_type_api_endpoint_cant_allow_patch(self,
                                                      mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        data = {}
        response = client.patch(
            self.asset_type_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PATCH" not allowed.'
        })
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_type_api_endpoint_cant_allow_delete(self,
                                                       mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        data = {}
        response = client.delete(
            self.asset_type_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "DELETE" not allowed.'
        })
        self.assertEqual(response.status_code, 405)
