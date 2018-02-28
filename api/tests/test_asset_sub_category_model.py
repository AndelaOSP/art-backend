from django.test import TestCase
from ..models import AssetSubCategory


class AssetSubCategoryModelTest(TestCase):
    """Tests for the assets subcategory model"""
    def setUp(self):
        AssetSubCategory.objects.create(
            sub_category_name="Computer Accessories"
        )
        self.subcategory = AssetSubCategory.objects.get(
            sub_category_name="Computer Accessories"
        )

    def test_can_save_a_sub_category(self):
        self.assertEqual(AssetSubCategory.objects.count(), 1)
        AssetSubCategory.objects.create(sub_category_name="Gadgets")
        self.assertEqual(AssetSubCategory.objects.count(), 2)

    def test_can_edit_a_Sub_category(self):
        self.subcategory.sub_category_name = "Computer Gadgets"
        self.assertEqual(
            self.subcategory.sub_category_name, "Computer Gadgets"
        )

    def test_can_delete_a_sub_category(self):
        self.assertEqual(AssetSubCategory.objects.count(), 1)
        self.subcategory.delete()
        self.assertEqual(AssetSubCategory.objects.count(), 0)
