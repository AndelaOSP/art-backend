# Third-Party Imports
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

# App Imports
from core.models import AllocationHistory, Asset, AssetStatus
from core.tests import CoreBaseTestCase

User = get_user_model()


class AssetStatusModelTest(CoreBaseTestCase):
    """Tests for the Asset Status Model"""

    def test_create_asset_creates_new_status(self):
        """Tests that creating a new asset creates a new asset status log"""
        status_count = AssetStatus.objects.count()
        asset_count = Asset.objects.count()
        Asset.objects.create(
            asset_code="kkIC002",
            serial_number="kkSN002",
            model_number=self.test_assetmodel,
            purchase_date="2018-07-10",
        )
        self.assertEqual(AssetStatus.objects.count(), status_count + 1)
        self.assertEqual(Asset.objects.count(), asset_count + 1)

    def test_create_asset_status(self):
        """
        Tests that:
        - creating a new asset status of the same asset,
        - changing an assets current status saves the previous current status
        as the new previous status
        """
        count = AssetStatus.objects.all().count()
        asset_status = AssetStatus(asset=self.test_asset, current_status="Damaged")
        asset_status.save()
        new_asset_status = AssetStatus.objects.filter(asset=self.test_asset).latest(
            "created_at"
        )
        self.assertEqual(new_asset_status.previous_status, "Available")
        self.assertEqual(new_asset_status.current_status, "Damaged")
        self.assertEqual(AssetStatus.objects.all().count(), count + 1)

    def test_default_status_is_available(self):
        """
        Tests that a new asset gets a 'Available' as default current status
        """
        self.assertEqual(self.test_asset_2.current_status, "Available")

    def test_status_validation(self):
        """Test that status has to be in list of choices"""
        asset_status = AssetStatus(asset=self.test_asset, current_status="Unused")
        with self.assertRaises(ValidationError):
            asset_status.save()

    def test_change_assigned_to_none(self):
        allocation_history = AllocationHistory(
            asset=self.test_asset, current_assignee=self.asset_assignee
        )

        asset_status = AssetStatus(asset=self.test_asset, current_status="Available")

        allocation_history.save()

        test_assignee = str(self.test_asset.assigned_to)

        asset_status.save()

        new_history = AllocationHistory.objects.filter(asset=self.test_asset).latest(
            "created_at"
        )

        self.assertIn(test_assignee, "test@andela.com")
        self.assertIsNone(self.test_asset.assigned_to)
        self.assertIsNone(new_history.current_assignee)
        self.assertIn(str(new_history.previous_assignee), "test@andela.com")
