from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from core.models import Asset, AssetModelNumber, AssetStatus

User = get_user_model()
client = APIClient()


class AssetStatusAPITest(TestCase):
    """Tests for the Asset Status API"""

    def setUp(self):
        self.test_assetmodel1 = AssetModelNumber(model_number="IMN50987")
        self.test_assetmodel1.save()
        self.token_user = 'testtoken'

        self.normal_user = User.objects.create(
            email='test@site.com', cohort=10,
            slack_handle='@test_user', password='devpassword'
        )

        self.test_asset = Asset(
            asset_code="IC001",
            serial_number="SN001",
            model_number=self.test_assetmodel1,
            assigned_to=self.normal_user
        )
        self.test_asset.save()
        self.asset = Asset.objects.get(asset_code="IC001")
        self.asset_status = AssetStatus.objects.get(asset=self.asset)

        self.asset_status_urls = reverse('asset-status-list')

    def test_non_authenticated_user_view_asset_status(self):
        response = client.get(self.asset_status_urls)
        self.assertEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_view_asset_status(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.normal_user.email}
        response = client.get(
            self.asset_status_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn(self.asset_status.asset_id, response.data[0].values())

        self.assertEqual(len(response.data), Asset.objects.count())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_view_single_asset_status(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.normal_user.email}
        response = client.get(
            '{}{}/'.format(self.asset_status_urls, self.asset_status.id),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn(self.asset_status.asset_id, response.data.values())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_post_asset_status(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.normal_user.email}
        data = {
            "asset": self.test_asset.serial_number,
            "current_status": "Available"
        }
        response = client.post(
            self.asset_status_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn(data['asset'], response.data.values())

        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_post_invalid_serial_number(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.normal_user.email}
        data = {
            "asset": "Invalid",
            "current_status": "Available"
        }
        response = client.post(
            self.asset_status_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'asset': ['Object with serial_number=Invalid does not exist.']
        })

        self.assertEqual(response.status_code, 400)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_post_invalid_status(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.normal_user.email}
        data = {
            "asset": self.test_asset.serial_number,
            "current_status": "Invalid"
        }
        response = client.post(
            self.asset_status_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'current_status': ['"Invalid" is not a valid choice.']
        })

        self.assertEqual(response.status_code, 400)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_post_empty_payload(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.normal_user.email}
        data = {}
        response = client.post(
            self.asset_status_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'asset': ['This field is required.'],
            'current_status': ['This field is required.']
        })

        self.assertEqual(response.status_code, 400)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_put_not_allowed(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.normal_user.email}
        data = {}
        response = client.put(
            self.asset_status_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PUT" not allowed.'
        })
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_patch_not_allowed(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.normal_user.email}
        data = {}
        response = client.patch(
            self.asset_status_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PATCH" not allowed.'
        })
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_delete_not_allowed(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.normal_user.email}
        response = client.delete(
            self.asset_status_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "DELETE" not allowed.'
        })
        self.assertEqual(response.status_code, 405)
