# Third-Party Imports
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError

# App Imports
from core.tests import CoreBaseTestCase

from ..models import AssetCategory


class AssetCategoryModelTest(CoreBaseTestCase):
    """ Tests for the Asset Category Model """

    def test_can_save_a_category(self):
        AssetCategory.objects.create(category_name="Electronics")
        new_category = AssetCategory.objects.get(category_name="Electronics")
        new_category_count = AssetCategory.objects.count()

        self.assertEqual(new_category_count, 2)
        self.assertIn(new_category.category_name, "Electronics")

    def test_cannot_add_existing_category_name(self):
        self.assertEqual(AssetCategory.objects.count(), 1)
        cat_name = AssetCategory.objects.first().category_name
        with self.assertRaises(ValidationError):
            AssetCategory.objects.create(category_name=cat_name)
        self.assertEqual(AssetCategory.objects.count(), 1)

    def test_can_edit_a_category(self):
        self.category.category_name = "Accessory"
        self.category.save()
        self.assertIn("Accessory", self.category.category_name)

    def test_asset_category_model_string_representation(self):
        self.assertEqual(str(self.category), self.category.category_name)

    def test_cannot_delete_category_with_existing_subcategories(self):
        count_before_delete = AssetCategory.objects.count()
        with self.assertRaises(ProtectedError):
            self.category.delete()
        count_after_delete = AssetCategory.objects.count()
        self.assertEqual(count_before_delete, count_after_delete)

    def test_can_delete_category_without_existing_subcategories(self):
        new_category_without_subcategories = AssetCategory.objects.create(
            category_name="New Category"
        )

        count_before_delete = AssetCategory.objects.count()
        new_category_without_subcategories.delete()
        count_after_delete = AssetCategory.objects.count()
        self.assertEqual(count_after_delete, count_before_delete - 1)
