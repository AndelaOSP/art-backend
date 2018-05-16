from django.test import TestCase
from unittest.mock import patch
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from core.models import User, Asset, AssetModelNumber
client = APIClient()


class AssetConditionAPITest(TestCase):
    """ Tests for the AssetCondition endpoint"""

    def setUp(self):
        self.user = User.objects.create(
            email='testuser@gmail.com', cohort=19,
            slack_handle='tester', password='qwerty123'
        )
        self.assetmodel = AssetModelNumber(
            model_number="IMN50987", make_label=self.make_label)
        self.asset = Asset(
            asset_code="IC001",
            serial_number="SN001",
            assigned_to=self.user,
            model_number=self.assetmodel,
        )
        self.asset.save()

        self.condition_url = reverse('asset-condition')
        self.token_user = 'testtoken'

    @patch('api.authentication.auth.verify_id_token')
    def test_can_post_condition(self, mock_verify_token):
        pass

    @patch('api.authentication.auth.verify_id_token')
    def test_can_get_all_condition(self, mock_verify_token):
        pass

    @patch('api.authentication.auth.verify_id_token')
    def test_can_get_single_condition(self, mock_verify_token):
        pass

    @patch('api.authentication.auth.verify_id_token')
    def test_condition_api_endpoint_cant_allow_put(
                            self, mock_verify_id_token):
        pass

    @patch('api.authentication.auth.verify_id_token')
    def test_condition_api_endpoint_cant_allow_patch(
                            self, mock_verify_id_token):
        pass

    @patch('api.authentication.auth.verify_id_token')
    def test_condition_api_endpoint_cant_allow_delete(
                            self, mock_verify_id_token):
        pass
