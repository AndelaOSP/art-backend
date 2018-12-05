from unittest.mock import patch
from rest_framework.test import APIClient

from core.models import AssetCategory, AssetType

from api.tests import APIBaseTestCase

client = APIClient()


class AssetCategoryAPITest(APIBaseTestCase):
    """ Tests for the AssetCategory endpoint"""

    def test_non_authenticated_user_get_asset_sub_category(self):
        response = client.get(self.asset_type_url)
        self.assertEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_can_post_asset_type(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin_user.email}
        data = {
            "asset_type": "Asset Type Example",
            "asset_sub_category": self.asset_sub_category.id
        }
        response = client.post(
            self.asset_type_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        self.assertIn("asset_type", response.data.keys())
        self.assertIn(data["asset_type"], response.data.values())
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_can_get_all_asset_types(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin_user.email}
        response = client.get(
            self.asset_type_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))

        self.assertEqual(len(response.data['results']),
                         AssetCategory.objects.count())
        self.assertIn("asset_type", response.data['results'][0].keys())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_can_get_single_asset_type(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin_user.email}
        response = client.get(
            f"{self.asset_type_url}/{self.asset_type.id}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))

        self.assertIn("asset_type", response.data.keys())
        self.assertIn(self.asset_type.asset_type,
                      response.data.values())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_type_api_endpoint_cant_allow_put(self,
                                                    mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        data = {}
        response = client.put(
            self.asset_type_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        self.assertEqual(response.data, {
            'detail': 'Method "PUT" not allowed.'
        })
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_type_api_endpoint_cant_allow_patch(self,
                                                      mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        data = {}
        response = client.patch(
            self.asset_type_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        self.assertEqual(response.data, {
            'detail': 'Method "PATCH" not allowed.'
        })
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_type_api_endpoint_cant_allow_delete(self,
                                                       mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        data = {}
        response = client.delete(
            self.asset_type_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        self.assertEqual(response.data, {
            'detail': 'Method "DELETE" not allowed.'
        })
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_type_api_orders_asset_types_by_type(self,
                                                       mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        AssetType.objects.create(
            asset_type="HP",
            asset_sub_category=self.asset_sub_category
        )
        AssetType.objects.create(
            asset_type="Samsung",
            asset_sub_category=self.asset_sub_category
        )
        AssetType.objects.create(
            asset_type="Lenovo",
            asset_sub_category=self.asset_sub_category
        )

        response = client.get(
            self.asset_type_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        # I am always sure that 'Samsung' will be the last in the response
        #  since the asset types are ordered.
        self.assertEqual(4, len(response.data.get('results')))
        self.assertEqual(response.data.get('results')[3].get('asset_type'), "Samsung")
