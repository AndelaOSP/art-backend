from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from ..models import (
    AssetStatus,
    AllocationHistory,
)

from core.tests import CoreBaseTestCase
User = get_user_model()
client = APIClient()


class AllocationHistoryModelTest(CoreBaseTestCase):
    """ Test for Allocation History """
    def test_can_save_to_allocation_history(self):
        """ Test can add an allocation history of an asset """
        count = AllocationHistory.objects.count()
        AssetStatus.objects.create(asset=self.test_asset, current_status='Available')
        AllocationHistory.objects.create(asset=self.test_asset, current_owner=self.asset_assignee2)
        self.assertEqual(AllocationHistory.objects.count(), count + 1)

    def test_can_save_history_without_previous_owner(self):
        new_history = AllocationHistory.objects.create(
            asset=self.test_asset_2,
            current_owner=self.asset_assignee2,
        )
        self.assertEqual(new_history.previous_owner, None)
        self.assertEqual(new_history.current_owner.email,
                         self.asset_assignee2.email)

    def test_cannot_add_history_for_allocated_asset(self):
        AssetStatus.objects.create(asset=self.test_asset, current_status='Available')
        AllocationHistory.objects.create(asset=self.test_asset, current_owner=self.asset_assignee)
        initial_count = AllocationHistory.objects.count()
        with self.assertRaises(ValidationError):
            AllocationHistory.objects.create(
                asset=self.test_asset,
                current_owner=self.asset_assignee2
            )

        self.assertEqual(AllocationHistory.objects.count(), initial_count)
