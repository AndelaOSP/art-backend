from django.test import TestCase
from unittest.mock import patch
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from core.models import (Asset,
                         AssetModelNumber,
                         AssetMake,
                         AssetType,
                         AssetSubCategory,
                         AssetCategory)

User = get_user_model()
client = APIClient()


class AssetConditionAPITest(TestCase):
    """ Tests for the AssetCondition endpoint"""

    def setUp(self):
        self.user = User.objects.create(
            email='testuser@gmail.com', cohort=19,
            slack_handle='tester', password='qwerty123'
        )
        self.asset_category = AssetCategory.objects.create(
            category_name="Accessories")
        self.asset_sub_category = AssetSubCategory.objects.create(
            sub_category_name="Sub Category name",
            asset_category=self.asset_category)
        self.asset_type = AssetType.objects.create(
            asset_type="Asset Type",
            asset_sub_category=self.asset_sub_category)
        self.make_label = AssetMake.objects.create(
            make_label="Asset Make", asset_type=self.asset_type)
        self.assetmodel = AssetModelNumber(
            model_number="IMN50987", make_label=self.make_label)
        self.assetmodel.save()
        self.asset = Asset(
            asset_code="IC001",
            serial_number="SN001",
            assigned_to=self.user,
            model_number=self.assetmodel,
        )
        self.asset.save()

        self.condition_url = reverse('asset-condition-list')
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
