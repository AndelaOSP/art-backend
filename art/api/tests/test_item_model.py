from django.test import TestCase

from ..models import Item


class AssetTypeModelTest(TestCase):
    """Tests for the Item Model"""

    def setUp(self):
        test_item = Item(item_name="TestItem")
        test_item.save()
        self.all_items = Item.objects.all()

    def test_add_new_item(self):
        """Test add new item"""
        self.assertEqual(self.all_items.count(), 1)
        new_item = Item(item_name="Macbook")
        new_item.save()
        self.assertEqual(self.all_items.count(), 2)

    def test_edit_asset_type(self):
        """Test edit an item in model"""
        get_item = Item.objects.get(item_name="TestItem")
        get_item.item_name = "New Item"
        get_item.save()
        self.assertEqual(self.all_items.count(), 1)
        get_item = Item.objects.get(item_name="New Item")
        self.assertEqual(get_item.item_name, "New Item")

    def test_delete_asset_type(self):
        """Test delete an asset type in model"""
        self.assertEqual(self.all_items.count(), 1)
        get_item = Item.objects.get(item_name="TestItem")
        get_item.delete()
        self.assertEqual(self.all_items.count(), 0)
