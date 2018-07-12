from unittest.mock import patch
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from core.models import (Asset,
                         AssetModelNumber,
                         AllocationHistory,
                         AssetMake,
                         AssetType,
                         AssetSubCategory,
                         AssetCategory)

from api.tests import APIBaseTestCase
User = get_user_model()
client = APIClient()


class AssetHealthTestCase(APIBaseTestCase):
    def setUp(self):
        super(AssetHealthTestCase, self).setUp()
        self.admin = User.objects.create_superuser(
            email='admin@site.com', cohort=20,
            slack_handle='@admin', password='devpassword'
        )
        self.token_admin = "tokenadmin"
        self.user = User.objects.create_user(
            email='user@site.com', cohort=20,
            slack_handle='@admin', password='devpassword'
        )
        self.token_user = 'testtoken'
        self.other_user = User.objects.create_user(
            email='user1@site.com', cohort=20,
            slack_handle='@admin', password='devpassword'
        )
        self.token_other_user = 'otherusertesttoken'
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
            purchase_date="2018-07-10",
        )
        self.asset.save()

        allocation_history = AllocationHistory(
            asset=self.asset,
            current_owner=self.user
        )

        allocation_history.save()

        self.asset_urls = reverse('asset-health-list')

    def test_non_authenticated_user_view_assets_health(self):
        response = client.get(self.asset_urls)
        self.assertEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_non_admin_cannot_view_asset_health(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.get(
            self.asset_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data,
                         {'detail': ['You do not have authorization']})
        self.assertEqual(response.status_code, 403)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_admin_view_assets_health(self,
                                                    mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin.email}
        response = client.get(
            self.asset_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        self.assertEqual(len(response.data), Asset.objects.count())
        self.assertEqual(response.data[0]['model_number'],
                         self.asset.model_number.model_number)
        self.assertEqual(response.data[0]['count_by_status']['Allocated'], 1)
        self.assertEqual(response.data[0]['count_by_status']['Available'], 0)
        self.assertEqual(response.data[0]['count_by_status']['Damaged'], 0)
        self.assertEqual(response.data[0]['count_by_status']['Lost'], 0)
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_assets_health_api_endpoint_cant_allow_put(self,
                                                       mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.put(
            self.asset_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PUT" not allowed.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_assets_health_api_endpoint_cant_allow_patch(self,
                                                         mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.patch(
            self.asset_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PATCH" not allowed.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_assets_health__endpoint_cant_allow_delete(self,
                                                       mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.delete(
            '{}/{}/'.format(self.asset_urls, self.asset.serial_number),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "DELETE" not allowed.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_type_in_asset_health_api(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin.email}
        response = client.get(
            self.asset_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        self.assertIn('asset_type', response.data[0])
        self.assertEqual(response.data[0]['asset_type'],
                         self.asset_type.asset_type)
        self.assertEqual(response.status_code, 200)
