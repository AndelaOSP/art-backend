from django.test import TestCase
from django.db.models.deletion import ProtectedError

from ..models import AssetModelNumber, AssetMake, AssetType, \
    AssetCategory, AssetSubCategory


class AssetModelNumberTestCase(TestCase):
    def setUp(self):
        AssetCategory.objects.create(category_name="Accessories")
        self.category = AssetCategory.objects.get(category_name="Accessories")
        self.new_sub_category = AssetSubCategory(
            sub_category_name="Computers Accessories",
            asset_category=self.category
        )
        self.new_sub_category.save()
        self.asset_type_id = AssetType(
            asset_type='test asset type',
            asset_sub_category=self.new_sub_category
        )
        self.asset_type_id.save()
        self.asset_make = AssetMake.objects.create(
            make_label="make test",
            asset_type=self.asset_type_id
        )
        AssetModelNumber.objects.create(
            model_number="101505400",
            make_label=self.asset_make
        )
        self.laptop_model_number = AssetModelNumber.objects.get(
            model_number="101505400"
        )

    def test_can_create_new_model_number(self):
        self.assertEqual(AssetModelNumber.objects.count(), 1)
        AssetModelNumber.objects.create(model_number="101505401",
                                        make_label=self.asset_make)
        self.assertEqual(AssetModelNumber.objects.count(), 2)

    def test_can_edit_model_number(self):
        self.laptop_model_number.model_number = "101505400"
        self.assertEqual(self.laptop_model_number.model_number, "101505400")

    def test_can_delete_model_number(self):
        self.assertEqual(AssetModelNumber.objects.count(), 1)
        self.laptop_model_number.delete()
        self.assertEqual(AssetModelNumber.objects.count(), 0)

    def test_asset_model_number_string_representation(self):
        get_model_number = AssetModelNumber.objects.get(
            model_number="101505400")
        self.assertEquals(str(get_model_number), "101505400")

    def test_cannot_delete_asset_make_with_existing_asset_models(self):
        count_before_delete = AssetMake.objects.count()
        with self.assertRaises(ProtectedError):
            self.asset_make.delete()
        count_after_delete = AssetCategory.objects.count()
        self.assertEqual(count_before_delete, count_after_delete)

    def test_cannot_add_asset_model_with_non_existing_make(self):
        with self.assertRaises(ValueError) as context:
            AssetModelNumber.objects.create(
                model_number="Test Model Number",
                make_label=3
            )
        self.assertEqual('Cannot assign "3": '
                         '"AssetModelNumber.make_label" '
                         'must be a "AssetMake" instance.',
                         str(context.exception))
