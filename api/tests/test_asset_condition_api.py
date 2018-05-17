from django.test import TestCase
from unittest.mock import patch
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from core.models import (Asset,
                         AssetModelNumber,
                         AssetCondition)

User = get_user_model()
client = APIClient()


class AssetConditionAPITest(TestCase):
    """ Tests for the AssetCondition endpoint"""

    def setUp(self):
        self.user = User.objects.create(
            email='testuser@gmail.com', cohort=19,
            slack_handle='tester', password='qwerty123'
        )
        self.assetmodel = AssetModelNumber(model_number="IMN50987")
        self.assetmodel.save()
        self.token_user = 'testtoken'

        self.test_asset = Asset(
            asset_code="IC001",
            serial_number="SN001",
            assigned_to=self.user,
            model_number=self.assetmodel,
        )
        self.test_asset.save()
        self.asset = Asset.objects.get(serial_number="SN001")
        self.asset_condition = AssetCondition(
                                    asset=self.asset,
                                    asset_condition="working"
                                    )
        self.asset_condition.save()
        self.asset_conditon = AssetCondition.objects.get(asset=self.asset)
        # print("asset condition", self.asset_conditon)
        self.asset_condition_urls = reverse('asset-condition-list')

    def test_non_authenciated_user_can_view_asset_condition(self):
        response = client.get(self.asset_condition_urls)
        self.assertEqual(response.status_code, 401)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenciated_user_can_view_asset_condition(
                            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.get(
            self.asset_condition_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn(self.asset_condition.asset_condition,
                      response.data[0].values())
        self.assertEqual(len(response.data), Asset.objects.count())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_can_post_asset_condition(self,
                                                         mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        test_asset = Asset(
            asset_code="IC002",
            serial_number="SN002",
            assigned_to=self.user,
            model_number=self.assetmodel,
        )
        test_asset.save()
        data = {
            "asset": test_asset.serial_number,
            "asset_condition": "working perfectly"
        }
        response = client.post(
            self.asset_condition_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn(data['asset_condition'], response.data.values())
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_cant_post_invalid_asset_serial_number(
                            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        invalid_asset = Asset(
            asset_code="IC0024",
            serial_number="SN0014",
            assigned_to=self.user,
            model_number=self.assetmodel,
        )
        data = {
            "asset": invalid_asset,
            "asset_condition": "working perfectly"
        }
        response = client.post(
            self.asset_condition_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.status_code, 400)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_can_get_all_asset_condition(
                                self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.get(
                self.asset_condition_urls,
                HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_can_get_single_asset_condition(
                                    self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        test_asset = Asset(
            asset_code="IC002",
            serial_number="SN002",
            assigned_to=self.user,
            model_number=self.assetmodel,
        )
        test_asset.save()
        data = {
            "asset": test_asset.serial_number,
            "asset_condition": "working perfectly"
        }
        new_asset_condition = client.post(
            self.asset_condition_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(new_asset_condition.status_code, 201)
        response = client.get(
            '{}{}/'.format(self.asset_condition_urls,
                           new_asset_condition.data['id']),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data['id'], new_asset_condition.data['id'])
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_condition_api_endpoint_cannot_allow_put(
                            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.put(
            self.asset_condition_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_condition_api_endpoint_cannot_allow_patch(
                            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.patch(
            self.asset_condition_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_condition_api_endpoint_cannot_allow_delete(
                            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.delete(
            self.asset_condition_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.status_code, 405)
