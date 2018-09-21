import os
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from api.tests import APIBaseTestCase
from core.models import AssetCategory, Asset, AssetSubCategory, AssetType, AssetMake, AssetModelNumber

User = get_user_model()
client = APIClient()


class AssetsUploadTestCase(APIBaseTestCase):
    def setUp(self):
        super(AssetsUploadTestCase, self).setUp()
        self.admin_user = User.objects.create_superuser(
            email='admin@site.com', cohort=20,
            slack_handle='@admin', password='devpassword'
        )
        self.token_admin = 'admintesttoken'
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

        self.asset_uploads_url = reverse('import-assets')

    def test_non_authenticated_user_view_assets(self):
        response = client.get(self.asset_uploads_url)
        self.assertEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_authenticated_user_can_upload_csv_file_to_save_assets(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        data = {'model_number': "IMN50987", 'year_of_manufacture': "2017",
                'processor_speed': "3.4"}

        file_location = os.path.join(os.path.dirname(__file__), 'sample_import.csv')

        with open(file_location) as csv:
            data['file'] = csv
            response = client.post(
                self.asset_uploads_url,
                data=data,
                HTTP_AUTHORIZATION="Token {}".format(self.token_admin))

        self.assertEqual(4, Asset.objects.count())
        self.assertEqual(204, response.status_code)
