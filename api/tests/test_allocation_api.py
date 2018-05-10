from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from core.models import Asset, AssetModelNumber, SecurityUser, \
    AllocationHistory

User = get_user_model()
client = APIClient()


class AllocationTestCase(TestCase):
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
        assetmodel = AssetModelNumber(model_number="IMN50987")
        assetmodel.save()
        asset = Asset(
            asset_code="IC001",
            serial_number="SN001",
            model_number=assetmodel,
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
        self.assertEqual(response.data, [])
        self.assertEqual(len(response.data), AllocationHistory.objects.count())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_post_allocations(self, mock_verify_id_token):
        """Test post new allocation"""
        self.assertEqual(AllocationHistory.objects.all().count(), 0)
        mock_verify_id_token.return_value = {'email': self.other_user.email}
        data = {"asset": "SN001",
                "current_owner": self.user.id}
        response = client.post(self.allocations_urls, data,
                               HTTP_AUTHORIZATION="Token {}".
                               format(self.token_user)
                               )
        self.assertEqual(AllocationHistory.objects.all().count(), 1)
        self.assertEqual(response.data['asset'],
                         self.asset.serial_number)
        self.assertEqual(response.data['current_owner'],
                         self.user.id)
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_rellocate_to_new_owner(self, mock_verify_id_token):
        """Test post new allocation"""
        self.assertEqual(AllocationHistory.objects.all().count(), 0)
        mock_verify_id_token.return_value = {'email': self.other_user.email}
        data = {"asset": "SN001",
                "current_owner": self.user.id}
        response = client.post(self.allocations_urls, data,
                               HTTP_AUTHORIZATION="Token {}".
                               format(self.token_user)
                               )
        self.assertEqual(response.status_code, 201)
        data = {"asset": "SN001",
                "current_owner": self.other_user.id}
        response = client.post(self.allocations_urls, data,
                               HTTP_AUTHORIZATION="Token {}".
                               format(self.token_user)
                               )
        self.assertEqual(AllocationHistory.objects.all().count(), 2)
        self.assertEqual(response.data['asset'], self.asset.serial_number)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['current_owner'],
                         self.other_user.id)
        self.assertEqual(response.data['previous_owner'],
                         self.user.id)
