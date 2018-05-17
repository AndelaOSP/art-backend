from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from core.models import (Asset,
                         AssetModelNumber,
                         SecurityUser,
                         AssetLog,
                         AllocationHistory,
                         AssetMake,
                         AssetType,
                         AssetSubCategory,
                         AssetCategory)

User = get_user_model()
client = APIClient()


class AssetTestCase(TestCase):
    def setUp(self):
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
        )
        self.asset.save()

        allocation_history = AllocationHistory(
            asset=self.asset,
            current_owner=self.user
        )

        allocation_history.save()

        self.checked_by = SecurityUser.objects.create(
            email="sectest1@andela.com",
            password="devpassword",
            first_name="TestFirst",
            last_name="TestLast",
            phone_number="254720900900",
            badge_number="AE23"
        )
        self.asset_urls = reverse('assets-list')

    def test_non_authenticated_user_view_assets(self):
        response = client.get(self.asset_urls)
        self.assertEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_view_assets(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.other_user.email}
        response = client.get(
            self.asset_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_other_user))
        self.assertEqual(response.data, [])
        self.assertEqual(len(response.data), Asset.objects.count() - 1)
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_owner_view_assets(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.get(
            self.asset_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn(self.asset.asset_code, response.data[0].values())
        self.assertEqual(len(response.data), Asset.objects.count())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_get_single_asset(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.other_user.email}
        response = client.get(
            "{}{}/".format(self.asset_urls, self.asset.serial_number),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn(self.asset.asset_code, response.data.values())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_can_post_asset(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        data = {
            "asset_code": "IC002",
            "serial_number": "SN002",
            "model_number": self.assetmodel.id,
        }
        response = client.post(
            self.asset_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        res_data = response.data
        self.assertEqual(
            data.get("asset_code"), res_data.get("asset_code"))
        self.assertEqual(
            data.get("serial_number"), res_data.get("serial_number"))
        self.assertEqual(
            data.get("model_number"), res_data.get("model_number"))
        self.assertEqual(Asset.objects.count(), 2)
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_can_post_asset_with_invalid_model_number(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}

        self.assetmodel.id = 300

        data = {
            "asset_code": "IC002",
            "serial_number": "SN002",
            "model_number": self.assetmodel.id
        }
        response = client.post(
            self.asset_urls,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'model_number': ['Invalid pk "300" - object does not exist.']
        })
        self.assertEqual(response.status_code, 400)

    @patch('api.authentication.auth.verify_id_token')
    def test_assets_api_endpoint_cant_allow_put(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.put(
            '{}{}/'.format(self.asset_urls, self.asset.serial_number),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PUT" not allowed.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_assets_api_endpoint_cant_allow_patch(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.patch(
            '{}{}/'.format(self.asset_urls, self.asset.serial_number),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PATCH" not allowed.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_assets_api_endpoint_cant_allow_delete(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.delete(
            '{}{}/'.format(self.asset_urls, self.asset.serial_number),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "DELETE" not allowed.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_assets_detail_api_endpoint_contain_assigned_to_details(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.get(
            '{}{}/'.format(self.asset_urls, self.asset.serial_number),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn(self.user.email,
                      response.data['assigned_to'].values())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_assets_assigned_to_details_has_no_password(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.get(
            '{}{}/'.format(self.asset_urls, self.asset.serial_number),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertNotIn('password', response.data['assigned_to'].keys())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_checkin_status_for_non_checked_asset(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.get(
            '{}{}/'.format(self.asset_urls, self.asset.serial_number),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn('checkin_status', response.data.keys())
        self.assertEqual(response.data['checkin_status'], None)
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_checkin_status_for_checked_in_asset(
            self, mock_verify_id_token):
        AssetLog.objects.create(
            checked_by=self.checked_by,
            asset=self.asset,
            log_type="Checkin"
        )

        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.get(
            '{}{}/'.format(self.asset_urls, self.asset.serial_number),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn('checkin_status', response.data.keys())
        self.assertEqual(response.data['checkin_status'],
                         "checked_in")
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_checkin_status_for_checkout_in_asset(
            self, mock_verify_id_token):
        AssetLog.objects.create(
            checked_by=self.checked_by,
            asset=self.asset,
            log_type="Checkout"
        )
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.get(
            '{}{}/'.format(self.asset_urls, self.asset.serial_number),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn('checkin_status', response.data.keys())
        self.assertEqual(response.data['checkin_status'],
                         "checked_out")
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_type_in_asset_api(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        response = client.get(
            '{}{}/'.format(self.asset_urls, self.asset.serial_number),
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn('asset_type', response.data.keys())
        self.assertEqual(response.data['asset_type'],
                         self.asset_type.asset_type)
        self.assertEqual(response.status_code, 200)
