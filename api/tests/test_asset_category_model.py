from django.db.models import ProtectedError
from django.test import TestCase
from ..models import AssetCategory, AssetSubCategory


class AssetCategoryModelTest(TestCase):
    """ Tests for the Asset Category Model """

    def setUp(self):
        AssetCategory.objects.create(category_name="Accessories")
        self.category = AssetCategory.objects.get(category_name="Accessories")

    def test_can_save_a_category(self):
        AssetCategory.objects.create(category_name="Electronics")
        new_category = AssetCategory.objects.get(category_name="Electronics")
        new_category_count = AssetCategory.objects.count()

        self.assertEqual(new_category_count, 2)
        self.assertIn(new_category.category_name, "Electronics")

    def test_can_edit_a_category(self):
        self.category.category_name = "Accessory"
        self.category.save()
        self.assertIn("Accessory", self.category.category_name)

    def test_can_delete_a_category(self):
        new_category = AssetCategory.objects.create(category_name="Screens")
        new_category_count = AssetCategory.objects.count()
        new_category.delete()
        count_after_deletion = AssetCategory.objects.count()

        self.assertEqual(new_category_count, 2)
        self.assertEqual(count_after_deletion, 1)

    def test_asset_category_model_string_representation(self):
        self.assertEquals(str(self.category), "Accessories")

    def test_cannot_delete_category_with_existing_subcategories(self):
        AssetSubCategory.objects.create(
            sub_category_name="Computer Accessories",
            asset_category=self.category
        )
        self.subcategory = AssetSubCategory.objects.get(
            sub_category_name="Computer Accessories"
        )
        count_before_delete = AssetCategory.objects.count()
        with self.assertRaises(ProtectedError):
            self.category.delete()
        count_after_delete = AssetCategory.objects.count()
        self.assertEqual(count_before_delete, count_after_delete)

    def test_can_delete_category_without_existing_subcategories(self):
        new_category_without_subcategories = \
            AssetCategory.objects.create(category_name="New Category")

        count_before_delete = AssetCategory.objects.count()
        new_category_without_subcategories.delete()
        count_after_delete = AssetCategory.objects.count()
        self.assertEqual(count_before_delete, count_after_delete + 1)
