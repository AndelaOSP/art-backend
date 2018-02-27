from django.test import TestCase

from ..models import AssetType


class AssetTypeModelTest(TestCase):
    """Tests for the Asset Types Model"""

    def setUp(self):
        test_asset = AssetType(asset_type="TestAsset")
        test_asset.save()
        self.all_assettypes = AssetType.objects.all()

    def test_add_new_asset_type(self):
        """Test add new asset type in model"""
        self.assertEqual(self.all_assettypes.count(), 1)
        new_assettype = AssetType(asset_type="Macbook")
        new_assettype.save()
        self.assertEqual(self.all_assettypes.count(), 2)

    def test_edit_asset_type(self):
        """Test edit an asset type in model"""
        get_asset = AssetType.objects.get(asset_type="TestAsset")
        get_asset.asset_type = "New Name"
        get_asset.save()
        self.assertEqual(self.all_assettypes.count(), 1)
        get_asset = AssetType.objects.get(asset_type="New Name")
        self.assertEqual(get_asset.asset_type, "New Name")

    def test_delete_asset_type(self):
        """Test delete an asset type in model"""
        self.assertEqual(self.all_assettypes.count(), 1)
        get_asset = AssetType.objects.get(asset_type="TestAsset")
        get_asset.delete()
        self.assertEqual(self.all_assettypes.count(), 0)
