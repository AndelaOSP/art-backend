from django.test import TestCase

from ..models import AssetType, AssetSubCategory, AssetCategory


class AssetTypeModelTest(TestCase):
    """Tests for the Asset Types Model"""

    def setUp(self):
        AssetCategory.objects.create(
            category_name="Accessories"
        )
        self.category = AssetCategory.objects.get(
            category_name="Accessories"
        )
        self.new_sub_category = AssetSubCategory(
            sub_category_name="Computer Assessories",
            asset_category=self.category
        )
        self.new_sub_category.save()
        AssetType.objects.create(asset_type="Headset",
                                 asset_sub_category=self.new_sub_category)
        self.all_assettypes = AssetType.objects.all()

    def test_add_new_asset_type(self):
        """Test add new asset type in model"""
        self.assertEqual(self.all_assettypes.count(), 1)
        new_assettype = AssetType(asset_type="Macbook",
                                  asset_sub_category=self.new_sub_category)
        new_assettype.save()
        self.assertEqual(self.all_assettypes.count(), 2)

    def test_edit_asset_type(self):
        """Test edit an asset type in model"""
        get_asset = AssetType.objects.get(asset_type="Headset")
        get_asset.asset_type = "New Name"
        get_asset.save()
        self.assertEqual(self.all_assettypes.count(), 1)
        get_asset = AssetType.objects.get(asset_type="New Name")
        self.assertEqual(get_asset.asset_type, "New Name")

    def test_delete_asset_type(self):
        """Test delete an asset type in model"""
        self.assertEqual(self.all_assettypes.count(), 1)
        get_asset = AssetType.objects.get(asset_type="Headset")
        get_asset.delete()
        self.assertEqual(self.all_assettypes.count(), 0)

    def test_asset_type_model_string_representation(self):
        get_asset = AssetType.objects.get(asset_type="Headset")
        self.assertEquals(str(get_asset), "Headset")

    def test_cannot_add_type_with_non_exisitng_subcategory(self):
        """ Test cannot add type with non-existing subcategory """
        with self.assertRaises(ValueError) as context:
            AssetType.objects.create(asset_type="Dongles",
                                     asset_sub_category=6)
        self.assertTrue('Cannot assign "6": '
                        '"AssetType.asset_sub_category" must '
                        'be a "AssetSubCategory" instance'
                        in str(context.exception))
