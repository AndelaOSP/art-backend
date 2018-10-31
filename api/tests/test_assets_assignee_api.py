from unittest.mock import patch
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from core.models import (
    User, AssetAssignee, Department, OfficeBlock,
    OfficeFloor, OfficeFloorSection, AssetCategory, OfficeWorkspace,
    AssetSubCategory, AssetType, AssetMake, AssetModelNumber, Asset,
    AllocationHistory, AndelaCentre,
)

from api.tests import APIBaseTestCase
client = APIClient()


class AssetAssigneeAPITest(APIBaseTestCase):
    """ Tests for the AssetAssignee endpoint"""

    def setUp(self):
        super(AssetAssigneeAPITest, self).setUp()
        self.user = User.objects.create(
            email='testuser@gmail.com', cohort=19,
            slack_handle='tester', password='qwerty123'
        )

        self.department = Department.objects.create(name="Finance")
        self.centre = AndelaCentre.objects.create(
            centre_name="Dojo",
            country="Kenya"
        )
        self.office_block = OfficeBlock.objects.create(
            name='Andela Tower',
            location=self.centre
        )
        self.office_floor = OfficeFloor.objects.create(
            block=self.office_block,
            number=14
        )

        self.office_section = OfficeFloorSection.objects.create(
            name='Safari',
            floor=self.office_floor
        )
        self.office_workspace = OfficeWorkspace.objects.create(
            name="Yaba",
            section=self.office_section
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
        self.assetmodel = AssetModelNumber.objects.create(
            model_number="IMN50987", make_label=self.make_label)
        self.assetmodel_2 = AssetModelNumber.objects.create(
            model_number="IMN509889", make_label=self.make_label)
        self.assetmodel_3 = AssetModelNumber.objects.create(
            model_number="IMN509887868", make_label=self.make_label)

        self.asset = Asset.objects.create(
            asset_code="IC001",
            serial_number="SN001",
            purchase_date="2018-07-10",
            current_status="Available",
            model_number=self.assetmodel
        )

        self.asset_2 = Asset.objects.create(
            asset_code="IC002",
            serial_number="SN002",
            purchase_date="2018-07-12",
            current_status="Available",
            model_number=self.assetmodel_2
        )

        self.asset_3 = Asset.objects.create(
            asset_code="IC003",
            serial_number="SN003",
            purchase_date="2018-07-14",
            current_status="Available",
            model_number=self.assetmodel_3
        )

        self.allocation_user = AllocationHistory.objects.create(
            asset=self.asset,
            current_owner=self.user.assetassignee
        )

        self.allocation_department = AllocationHistory.objects.create(
            asset=self.asset_2,
            current_owner=self.department.assetassignee
        )

        self.allocation_workspace = AllocationHistory.objects.create(
            asset=self.asset_3,
            current_owner=self.office_workspace.assetassignee
        )

        self.asset_assignee_url = reverse('asset-assignee-list')
        self.token_user = 'testtoken'

    def test_non_authenticated_user_get_assets_assignee(self):
        response = client.get(self.asset_assignee_url)
        self.assertEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_can_get_assets_assignee(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.user.email}
        response = client.get(
            self.asset_assignee_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(len(response.data['results']),
                         AssetAssignee.objects.count())
        self.assertIn("assignee", response.data['results'][0].keys())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_assets_assignee_api_endpoint_cant_allow_put(self,
                                                         mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        data = {}
        response = client.put(
            self.asset_assignee_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PUT" not allowed.'
        })
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_assets_assignee_api_cant_allow_delete(self,
                                                   mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.user.email}
        data = {}
        response = client.delete(
            self.asset_assignee_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "DELETE" not allowed.'
        })
        self.assertEqual(response.status_code, 405)
