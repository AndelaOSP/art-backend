# Standard Library
from unittest.mock import patch

# Third-Party Imports
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase
from core.models import AllocationHistory, AssetAssignee, Department, OfficeWorkspace

User = get_user_model()
client = APIClient()


class AllocationTestCase(APIBaseTestCase):
    def test_non_authenticated_user_view_assets(self):
        response = client.get(self.allocations_urls)
        self.assertEqual(
            response.data, {'detail': 'Authentication credentials were not provided.'}
        )

    @patch('api.authentication.auth.verify_id_token')
    def test_get_allocations(self, mock_verify_id_token):
        """Test post new allocation"""
        mock_verify_id_token.return_value = {'email': self.other_user.email}
        response = client.get(
            self.allocations_urls,
            HTTP_AUTHORIZATION="Token {}".format(self.token_other_user),
        )
        self.assertEqual(response.data['results'], [])
        self.assertEqual(
            len(response.data['results']), AllocationHistory.objects.count()
        )
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_post_allocation_of_asset_to_a_user(self, mock_verify_id_token):
        """Test post new allocation"""
        count = AllocationHistory.objects.count()
        mock_verify_id_token.return_value = {'email': self.other_user.email}
        data = {"asset": self.asset.id, "current_owner": self.asset_assignee.id}
        response = client.post(
            self.allocations_urls,
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(AllocationHistory.objects.count(), count + 1)
        self.assertEqual(
            response.data['asset'],
            f"{self.asset.serial_number} - {self.asset.asset_code}",
        )
        self.assertEqual(response.data['current_owner'], self.user.email)
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_post_allocation_of_asset_to_a_department(self, mock_verify_id_token):
        """Test allocating an asset to a department"""
        count = AllocationHistory.objects.count()
        mock_verify_id_token.return_value = {'email': self.other_user.email}
        department = Department.objects.create(name="Success")
        asset_assignee = AssetAssignee.objects.get(department=department)
        data = {"asset": self.asset.id, "current_owner": asset_assignee.id}
        response = client.post(
            self.allocations_urls,
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(AllocationHistory.objects.all().count(), count + 1)
        self.assertEqual(
            response.data['asset'],
            f"{self.asset.serial_number} - {self.asset.asset_code}",
        )
        self.assertEqual(response.data['current_owner'], department.name)
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_post_allocation_of_asset_to_a_workspace(self, mock_verify_id_token):
        """Test allocating an asset to a department"""
        count = AllocationHistory.objects.count()
        mock_verify_id_token.return_value = {'email': self.other_user.email}
        workspace = OfficeWorkspace.objects.create(
            name="4E", section=self.floor_section
        )
        asset_assignee = AssetAssignee.objects.get(workspace=workspace)
        data = {"asset": self.asset.id, "current_owner": asset_assignee.id}
        response = client.post(
            self.allocations_urls,
            data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(AllocationHistory.objects.all().count(), count + 1)
        self.assertEqual(
            response.data['asset'],
            f"{self.asset.serial_number} - {self.asset.asset_code}",
        )
        self.assertEqual(response.data['current_owner'], workspace.name)
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_asset_status_changes_to_allocated(self, mock_verify_id_token):
        """Test allocating asset changes asset status to allocated"""

        mock_verify_id_token.return_value = {'email': self.user.email}
        data = {'asset': self.asset.id, 'current_owner': self.asset_assignee.id}
        token = f"Token {self.token_user}"
        response = client.post(self.allocations_urls, data, HTTP_AUTHORIZATION=token)
        self.assertEqual(response.status_code, 201)
        response = client.get(
            f"{reverse('assets-list')}/{self.asset.uuid}/", HTTP_AUTHORIZATION=token
        )
        self.assertEqual(response.data['current_status'], 'Allocated')
        self.assertEqual(response.data['serial_number'], self.asset.serial_number)
        self.assertEqual(response.status_code, 200)
