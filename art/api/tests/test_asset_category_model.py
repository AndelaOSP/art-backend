from django.test import TestCase
from ..models import AssetCategory


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
