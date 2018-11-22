from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from core.models import AssetSubCategory
from core.tests import CoreBaseTestCase


class AssetSubCategoryModelTest(CoreBaseTestCase):
    """Tests for the assets subcategory model"""
    def test_can_save_a_sub_category(self):
        count = AssetSubCategory.objects.count()
        AssetSubCategory.objects.create(sub_category_name="Gadgets", asset_category=self.category)
        self.assertEqual(AssetSubCategory.objects.count(), count + 1)

    def test_cannot_add_existing_sub_category(self):
        count = AssetSubCategory.objects.count()
        with self.assertRaises(ValidationError):
            AssetSubCategory.objects.create(
                sub_category_name="Computer Accessories",
                asset_category=self.category,
            )
        self.assertEqual(AssetSubCategory.objects.count(), count)

    def test_can_delete_a_sub_category(self):
        count = AssetSubCategory.objects.count()
        with self.assertRaises(ProtectedError):
            self.asset_sub_category.delete()
        self.assertEqual(AssetSubCategory.objects.count(), count)

    def test_asset_subcategory_model_string_representation(self):
        self.assertEqual(str(self.asset_sub_category), "Computer Accessories")
