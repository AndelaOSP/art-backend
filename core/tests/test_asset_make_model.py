from django.test import TestCase
from django.db.models.deletion import ProtectedError

from ..models import AssetMake, AssetType, AssetSubCategory, AssetCategory


class AssetMakeTestCase(TestCase):

    def setUp(self):
        AssetCategory.objects.create(category_name="Accessories")
        self.category = AssetCategory.objects.get(category_name="Accessories")
        self.new_sub_category = AssetSubCategory(
            sub_category_name="Computers Accessories",
            asset_category=self.category
        )
        self.new_sub_category.save()
        self.new_type = AssetType(
            asset_type="Headset",
            asset_sub_category=self.new_sub_category
        )
        self.new_type.save()
        AssetMake.objects.create(
            make_label="Sades",
            asset_type=self.new_type
        )
        self.headset_make = AssetMake.objects.get(
            make_label="Sades"
        )

    def test_can_create_asset_make(self):
        self.assertEqual(AssetMake.objects.count(), 1)
        AssetMake.objects.create(
            make_label="Bose",
            asset_type=self.new_type
        )
        self.assertEqual(AssetMake.objects.count(), 2)

    def test_can_edit_asset_make(self):
        self.headset_make.make_label = "Sony"
        self.assertEqual(self.headset_make.make_label, "Sony")

    def test_can_delete_asset_model(self):
        self.assertEqual(AssetMake.objects.count(), 1)
        self.headset_make.delete()
        self.assertEqual(AssetMake.objects.count(), 0)

    def test_asset_make_model_string_representation(self):
        self.assertEquals(str(self.headset_make), "Sades")

    def test_cannot_add_make_with_non_exisiting_type(self):
        """ Test cannot add make with non-existing type """
        with self.assertRaises(ValueError) as context:
            AssetMake.objects.create(
                make_label="Skull Candy",
                asset_type=6
            )
        self.assertTrue('Cannot assign "6": '
                        '"AssetMake.asset_type" '
                        'must be a "AssetType" instance'
                        in str(context.exception))

    def test_delete_type_protects_make(self):
        """ Test that the make is not deleted when the type is deleted """
        self.assertEqual(AssetType.objects.count(), 1)
        self.assertEqual(AssetMake.objects.count(), 1)
        with self.assertRaises(ProtectedError):
            self.new_type.delete()
        self.assertEqual(AssetType.objects.count(), 1)
        self.assertEqual(AssetMake.objects.count(), 1)
