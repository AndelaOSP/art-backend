from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from ..models import (Asset, AssetModelNumber,
                      AssetStatus, AllocationHistory)

User = get_user_model()
client = APIClient()


class AllocationHistoryModelTest(TestCase):
    """ Test for Allocation History """

    def setUp(self):
        self.user = User.objects.create(
            email='test@site.com', cohort=10,
            slack_handle='@test_user', password='devpassword'
        )
        self.user2 = User.objects.create(
            email='test15@site.com', cohort=15,
            slack_handle='@test_user', password='devpassword'
        )

        test_assetmodel = AssetModelNumber(model_number="IMN50987")
        test_assetmodel.save()

        self.test_asset = Asset(
            asset_code="IC001",
            serial_number="SN001",
            model_number=test_assetmodel
        )
        self.test_asset.save()

        self.allocation_history = AllocationHistory(
            asset=self.test_asset,
            current_owner=self.user
        )

        self.allocation_history.save()

    def test_can_save_to_allocation_history(self):
        """ Test can add an allocation history of an asset """

        user3 = User.objects.create(
            email='test21@site.com', cohort=21,
            slack_handle='@test_user', password='devpassword'
        )

        self.assertEqual(AllocationHistory.objects.count(), 1)
        new_history = AllocationHistory(
            asset=self.test_asset,
            current_owner=user3,
            previous_owner=self.user
        )
        new_history.save()
        self.assertEqual(AllocationHistory.objects.count(), 2)

    def test_can_change_previous_owner_and_current_owner(self):
        new_user = User.objects.create(
            email='test23@site.com', cohort=23,
            slack_handle='@test_user', password='devpassword'
        )

        new_history = AllocationHistory(
            asset=self.test_asset,
            current_owner=new_user,
            previous_owner=self.user
        )

        new_history.save()
        self.assertIn(str(new_history.previous_owner), 'test@site.com')
        self.assertIn(str(new_history.current_owner), 'test23@site.com')

    def test_can_save_history_without_previous_owner(self):
        new_user = User.objects.create(
            email='test23@site.com', cohort=23,
            slack_handle='@test_user', password='devpassword'
        )

        new_history = AllocationHistory(
            asset=self.test_asset,
            current_owner=new_user,
        )

        new_history.save()
        self.assertIn(str(new_history.previous_owner), 'test@site.com')

    def test_cannot_add_history_for_allocated_asset(self):

        self.assertEqual(AllocationHistory.objects.count(), 1)

        asset_status = AssetStatus(
            asset=self.test_asset,
            current_status="Allocated")

        asset_status.save()

        new_history = AllocationHistory(
            asset=self.test_asset,
            current_owner=self.user2
        )

        with self.assertRaises(ValidationError):
            new_history.save()

        self.assertEqual(AllocationHistory.objects.count(), 1)
