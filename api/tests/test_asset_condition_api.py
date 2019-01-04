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


class AssetConditionAPITest(APIBaseTestCase):
    ''' Tests for the AssetCondition endpoint'''

    def test_non_authenciated_user_can_view_asset_condition(self):
        response = client.get(self.asset_condition_urls)
        self.assertEqual(response.status_code, 401)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenciated_user_can_view_asset_condition(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.get(self.asset_condition_urls, HTTP_AUTHORIZATION='Token {}'.format(self.token_user))
        self.assertIn(self.asset_condition.notes, response.data['results'][0].values())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_can_post_asset_condition(self,
                                                         mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        test_asset = Asset(
            asset_code='IC002',
            serial_number='SN002',
            assigned_to=self.asset_assignee,
            model_number=self.assetmodel,
            purchase_date="2018-07-10"
        )
        test_asset.save()
        data = {
            'asset': test_asset.id,
            'notes': 'working perfectly'
        }
        response = client.post(
            self.asset_condition_urls,
            data=data,
            HTTP_AUTHORIZATION='Token {}'.format(self.token_user))
        self.assertIn(data['notes'], response.data.values())
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_cant_post_invalid_asset_serial_number(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        invalid_asset = Asset(
            asset_code='IC0024',
            serial_number='SN0014',
            assigned_to=self.asset_assignee,
            model_number=self.assetmodel,
        )
        data = {
            'asset': invalid_asset,
            'notes': 'working perfectly'
        }
        response = client.post(
            self.asset_condition_urls,
            data=data,
            HTTP_AUTHORIZATION='Token {}'.format(self.token_user))
        self.assertEqual(response.status_code, 400)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_can_get_all_asset_condition(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.get(
            self.asset_condition_urls,
            HTTP_AUTHORIZATION='Token {}'.format(self.token_user))
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_can_get_single_asset_condition(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        test_asset = Asset(
            asset_code='IC002',
            serial_number='SN002',
            assigned_to=self.asset_assignee,
            model_number=self.assetmodel,
            purchase_date="2018-07-10",
            asset_location=self.centre
        )
        test_asset.save()
        data = {
            'asset': test_asset.id,
            'notes': 'working perfectly'
        }
        new_asset_condition = client.post(
            self.asset_condition_urls,
            data=data,
            HTTP_AUTHORIZATION='Token {}'.format(self.token_user))
        self.assertEqual(new_asset_condition.status_code, 201)
        response = client.get(
            '{}/{}/'.format(self.asset_condition_urls,
                            new_asset_condition.data['id']),
            HTTP_AUTHORIZATION='Token {}'.format(self.token_user))
        self.assertEqual(response.data['id'],
                         new_asset_condition.data['id'])
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_condition_api_endpoint_cannot_allow_put(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.put(
            self.asset_condition_urls,
            HTTP_AUTHORIZATION='Token {}'.format(self.token_user))
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_condition_api_endpoint_cannot_allow_patch(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.patch(
            self.asset_condition_urls,
            HTTP_AUTHORIZATION='Token {}'.format(self.token_user))
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_condition_api_endpoint_cannot_allow_delete(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.delete(
            self.asset_condition_urls,
            HTTP_AUTHORIZATION='Token {}'.format(self.token_user))
        self.assertEqual(response.status_code, 405)
