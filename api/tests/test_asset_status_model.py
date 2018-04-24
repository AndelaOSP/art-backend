
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from ..models import Asset, AssetModelNumber, AssetStatus

User = get_user_model()
client = APIClient()


class AssetStatusModelTest(TestCase):
    """Tests for the Asset Status Model"""

    def setUp(self):
        self.test_assetmodel1 = AssetModelNumber(model_number="IMN50987")
        self.test_assetmodel2 = AssetModelNumber(model_number="IMN50986")
        self.test_assetmodel1.save()
        self.test_assetmodel2.save()

        self.normal_user = User.objects.create(
            email='test@site.com', cohort=10,
            slack_handle='@test_user', password='devpassword'
        )

        self.test_asset = Asset(
            asset_code="IC001",
            serial_number="SN001",
            model_number=self.test_assetmodel1,
            assigned_to=self.normal_user
        )
        self.test_asset.save()
        self.get_asset = Asset.objects.get(asset_code="IC001")
        self.asset_status = AssetStatus.objects.get(asset=self.get_asset)

    def test_create_asset_creates_new_status(self):
        """Tests that creating a new asset creates a new asset status log"""
        self.assertEqual(AssetStatus.objects.all().count(), 1)
        self.assertEqual(Asset.objects.all().count(), 1)
        test_asset2 = Asset(
            asset_code="IC002",
            serial_number="SN002",
            model_number=self.test_assetmodel2,
            assigned_to=self.normal_user
        )
        test_asset2.save()
        self.assertEqual(AssetStatus.objects.all().count(), 2)
        self.assertEqual(Asset.objects.all().count(), 2)

    def test_create_asset_status(self):
        """
        Tests that:
        - creating a new asset status of the same asset,
        - changing an assets current status saves the previous current status
        as the new previous status
        """
        self.assertEqual(AssetStatus.objects.all().count(), 1)
        asset_status = AssetStatus(
            asset=self.get_asset,
            current_status="Damaged")
        asset_status.save()
        new_asset_status = AssetStatus.objects.filter(asset=self.get_asset).\
            latest('created_at')
        self.assertEqual(new_asset_status.previous_status, "Available")
        self.assertEqual(new_asset_status.current_status, "Damaged")
        self.assertEqual(AssetStatus.objects.all().count(), 2)

    def test_default_status_is_available(self):
        """
        Tests that a new asset gets a 'Available' as default current status
        """
        model_count = AssetStatus.objects.all().count()
        self.assertEqual(self.asset_status.current_status, "Available")
        self.assertEqual(self.asset_status.previous_status, None)
        self.assertEqual(model_count, 1)

    def test_status_has_to_be_in_options(self):
        """Test that status has to be in list of choices"""
        model_count = AssetStatus.objects.all().count()
        self.assertEqual(model_count, 1)
        asset_status = AssetStatus(
            asset=self.get_asset,
            current_status="Unused")
        with self.assertRaises(ValidationError):
            asset_status.save()
        new_asset_status = AssetStatus.objects.filter(asset=self.get_asset).\
            latest('created_at')
        self.assertEqual(new_asset_status.current_status, "Available")
        self.assertEqual(new_asset_status.previous_status, None)
        self.assertEqual(model_count, 1)
