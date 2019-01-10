# Third-Party Imports
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError

# App Imports
from core.models import AssetType
from core.tests import CoreBaseTestCase


class AssetTypeModelTest(CoreBaseTestCase):
    """Tests for the Asset Types Model"""
    def test_add_new_asset_type(self):
        """Test add new asset type in model"""
        count = AssetType.objects.count()
        new_assettype = AssetType(name="Macbook", asset_sub_category=self.asset_sub_category)
        new_assettype.save()
        self.assertEqual(AssetType.objects.count(), count + 1)

    def test_cannot_add_existing_asset_type(self):
        count = AssetType.objects.count()
        with self.assertRaises(ValidationError):
            AssetType.objects.create(name=self.asset_type.name,
                                     asset_sub_category=self.asset_sub_category)
        self.assertEqual(AssetType.objects.count(), count)

    def test_delete_asset_type(self):
        """Test delete an asset type in model"""
        count = AssetType.objects.count()
        asset_type = AssetType.objects.first()
        with self.assertRaises(ProtectedError):
            asset_type.delete()
        self.assertEqual(AssetType.objects.count(), count)

    def test_asset_type_model_string_representation(self):
        get_asset = AssetType.objects.first()
        self.assertEqual(str(get_asset), get_asset.name)

    def test_cannot_add_type_with_non_exisitng_subcategory(self):
        """ Test cannot add type with non-existing subcategory """
        with self.assertRaises(ValueError) as context:
            AssetType.objects.create(name="Dongles",
                                     asset_sub_category=6)
        self.assertTrue('Cannot assign "6": '
                        '"AssetType.asset_sub_category" must '
                        'be a "AssetSubCategory" instance'
                        in str(context.exception))
