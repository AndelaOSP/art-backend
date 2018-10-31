from unittest.mock import patch
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from core.models import Asset, AssetModelNumber, SecurityUser, \
    AllocationHistory, AssetCategory, AssetSubCategory, AssetType, \
    AssetMake, AssetAssignee, Department, OfficeWorkspace,\
    OfficeBlock, OfficeFloor, OfficeFloorSection, AndelaCentre
from api.tests import APIBaseTestCase
User = get_user_model()
client = APIClient()


class AllocationTestCase(APIBaseTestCase):
    def setUp(self):
        super(AllocationTestCase, self).setUp()
        self.user = User.objects.create_user(
            email='user@site.com', cohort=20,
            slack_handle='@admin', password='devpassword'
        )
        self.asset_assignee = AssetAssignee.objects.get(user=self.user)
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
        assetmodel = AssetModelNumber(
            model_number="IMN50987", make_label=self.make_label)
        assetmodel.save()
        asset = Asset(
            asset_code="IC001",
            serial_number="SN001",
            model_number=assetmodel,
            purchase_date="2018-07-10"
        )
        asset.save()
        self.asset = asset
        self.checked_by = SecurityUser.objects.create(
            email="sectest1@andela.com",
            password="devpassword",
            first_name="TestFirst",
            last_name="TestLast",
            phone_number="254720900900",
            badge_number="AE23"
        )
        self.centre = AndelaCentre.objects.create(
            centre_name="Dojo", country="Kenya")
        self.office_block = OfficeBlock.objects.create(
            name="Epic Tower", location=self.centre)
        self.office_floor = OfficeFloor.objects.create(
            number=7,
            block=self.office_block
        )
        self.floor_section = OfficeFloorSection.objects.create(
            name='The Big Apple',
            floor=self.office_floor
        )
        self.allocations_urls = reverse('allocations-list')

    def test_non_authenticated_user_view_assets(self):
        response = client.get(self.allocations_urls)
        self.assertEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_get_allocations(self, mock_verify_id_token):
        """Test post new allocation"""
        mock_verify_id_token.return_value = {'email': self.other_user.email}
        response = client.get(
            self.allocations_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_other_user))
        self.assertEqual(response.data['results'], [])
        self.assertEqual(len(response.data['results']),
                         AllocationHistory.objects.count())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_post_allocation_of_asset_to_a_user(self, mock_verify_id_token):
        """Test post new allocation"""
        self.assertEqual(AllocationHistory.objects.all().count(), 0)
        mock_verify_id_token.return_value = {'email': self.other_user.email}
        data = {"asset": self.asset.id,
                "current_owner": self.asset_assignee.id}
        response = client.post(self.allocations_urls, data,
                               HTTP_AUTHORIZATION="Token {}".
                               format(self.token_user)
                               )
        self.assertEqual(AllocationHistory.objects.all().count(), 1)
        self.assertEqual(
            response.data['asset'],
            f"{self.asset.serial_number} - {self.asset.asset_code}")
        self.assertEqual(response.data['current_owner'],
                         self.user.email)
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_post_allocation_of_asset_to_a_department(self,
                                                      mock_verify_id_token):
        """Test allocating an asset to a department"""
        self.assertEqual(AllocationHistory.objects.all().count(), 0)
        mock_verify_id_token.return_value = {'email': self.other_user.email}
        department = Department.objects.create(name="Success")
        asset_assignee = AssetAssignee.objects.get(department=department)
        data = {"asset": self.asset.id,
                "current_owner": asset_assignee.id}
        response = client.post(self.allocations_urls, data,
                               HTTP_AUTHORIZATION="Token {}".
                               format(self.token_user)
                               )
        self.assertEqual(AllocationHistory.objects.all().count(), 1)
        self.assertEqual(
            response.data['asset'],
            f"{self.asset.serial_number} - {self.asset.asset_code}")
        self.assertEqual(response.data['current_owner'],
                         department.name)
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_post_allocation_of_asset_to_a_workspace(
            self,
            mock_verify_id_token):
        """Test allocating an asset to a department"""
        self.assertEqual(AllocationHistory.objects.all().count(), 0)
        mock_verify_id_token.return_value = {'email': self.other_user.email}
        workspace = OfficeWorkspace.objects.create(
            name="4E",
            section=self.floor_section
        )
        asset_assignee = AssetAssignee.objects.get(workspace=workspace)
        data = {"asset": self.asset.id,
                "current_owner": asset_assignee.id}
        response = client.post(self.allocations_urls, data,
                               HTTP_AUTHORIZATION="Token {}".
                               format(self.token_user)
                               )
        self.assertEqual(AllocationHistory.objects.all().count(), 1)
        self.assertEqual(
            response.data['asset'],
            f"{self.asset.serial_number} - {self.asset.asset_code}")
        self.assertEqual(response.data['current_owner'],
                         workspace.name)
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_status_changes_to_allocated(self, mock_verify_id_token):
        """Test allocating asset changes asset status to allocated"""

        mock_verify_id_token.return_value = {'email': self.user.email}
        data = {
            'asset': self.asset.id,
            'current_owner': self.asset_assignee.id}
        token = f"Token {self.token_user}"
        response = client.post(
            self.allocations_urls, data,
            HTTP_AUTHORIZATION=token
        )
        self.assertEqual(response.status_code, 201)
        response = client.get(
            f"{reverse('assets-list')}/{self.asset.uuid}/",
            HTTP_AUTHORIZATION=token)
        self.assertEquals(response.data['current_status'], 'Allocated')
        self.assertEquals(
            response.data['serial_number'], self.asset.serial_number)
        self.assertEquals(response.status_code, 200)
