from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.models import (AssetAssignee,
                         AssetCategory,
                         AssetSubCategory,
                         AssetType,
                         AssetMake,
                         AssetModelNumber,
                         Asset,
                         AllocationHistory)

from rest_framework.test import APIClient
from api.tests import APIBaseTestCase
User = get_user_model()
client = APIClient()


class FilterValuesApiTest(APIBaseTestCase):
    def setUp(self):
        super(FilterValuesApiTest, self).setUp()
        self.admin = User.objects.create_superuser(
            email='admin@site.com', cohort=0,
            slack_handle='@admin', password='devpassword'
        )
        self.token_admin = "tokenadmin"
        self.user = User.objects.create_user(
            email='user@site.com', cohort=20,
            slack_handle='@admin', password='devpassword'
        )
        self.asset_assignee = AssetAssignee.objects.get(user=self.user)
        self.token_user = 'testtoken'

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
            assigned_to=self.asset_assignee,
            model_number=self.assetmodel,
            purchase_date="2018-07-10"
        )
        self.asset.save()

        allocation_history = AllocationHistory(
            asset=self.asset,
            current_owner=self.asset_assignee
        )

        allocation_history.save()

        self.filter_values_urls = reverse('available-filters')

    def test_non_authenticated_admin_view_filter_values(self):
        response = client.get(self.filter_values_urls)
        self.assertEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_admin_view_filter_values(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin.email}
        response = client.get(
            self.filter_values_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin))
        self.assertEqual(0, response.data['cohorts'][0].get('option'))
        self.assertEqual(20, response.data['cohorts'][1].get('option'))
        self.assertEqual(0, response.data['asset_count'][0].get('option'))
        self.assertEqual(1, response.data['asset_count'][1].get('option'))
        self.assertEqual(response.status_code, 200)
