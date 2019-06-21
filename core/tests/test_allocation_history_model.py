# Third-Party Imports
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

# App Imports
from core.tests import CoreBaseTestCase

from ..models import AllocationHistory, AssetStatus

User = get_user_model()


class AllocationHistoryModelTest(CoreBaseTestCase):
    """ Test for Allocation History """

    def test_can_save_to_allocation_history(self):
        """ Test can add an allocation history of an asset """
        count = AllocationHistory.objects.count()
        AssetStatus.objects.create(asset=self.test_asset, current_status="Available")
        AllocationHistory.objects.create(
            asset=self.test_asset, current_assignee=self.asset_assignee2
        )
        self.assertEqual(AllocationHistory.objects.count(), count + 1)

    def test_can_save_history_without_previous_assignee(self):
        new_history = AllocationHistory.objects.create(
            asset=self.test_asset_2, current_assignee=self.asset_assignee2
        )
        self.assertEqual(new_history.previous_assignee, None)
        self.assertEqual(new_history.current_assignee.email, self.asset_assignee2.email)

    def test_cannot_add_history_for_allocated_asset(self):
        AssetStatus.objects.create(asset=self.test_asset, current_status="Available")
        AllocationHistory.objects.create(
            asset=self.test_asset, current_assignee=self.asset_assignee
        )
        initial_count = AllocationHistory.objects.count()
        with self.assertRaises(ValidationError):
            AllocationHistory.objects.create(
                asset=self.test_asset, current_assignee=self.asset_assignee2
            )

        self.assertEqual(AllocationHistory.objects.count(), initial_count)
