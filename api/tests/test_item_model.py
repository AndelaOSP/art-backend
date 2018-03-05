from django.test import TestCase
from django.core.exceptions import ValidationError

from ..models import Item, ItemModelNumber


class ItemTypeModelTest(TestCase):
    """Tests for the Item Model"""

    def setUp(self):
        test_item = Item(
            item_code="IC001",
            serial_number="SN001"
        )
        test_item.save()
        test_itemmodel = ItemModelNumber(model_number="IMN50987")
        test_itemmodel.save()
        self.all_items = Item.objects.all()
        self.all_itemmodels = ItemModelNumber.objects.all()

    def test_add_new_item(self):
        """Test add new item"""
        self.assertEqual(self.all_items.count(), 1)
        new_item = Item(item_code="IC002")
        new_item.save()
        self.assertEqual(self.all_items.count(), 2)

    def test_item_without_code(self):
        """Test error when new item lacks serial number and item code"""
        self.assertEqual(self.all_items.count(), 1)
        new_item = Item()
        with self.assertRaises(ValidationError):
            new_item.save()
        self.assertEqual(self.all_items.count(), 1)

    def test_edit_asset_type(self):
        """Test edit an item in model"""
        get_item = Item.objects.get(item_code="IC001")
        get_item.item_code = "IC003"
        get_item.save()
        self.assertEqual(self.all_items.count(), 1)
        get_item = Item.objects.get(item_code="IC003")
        self.assertEqual(get_item.item_code, "IC003")

    def test_delete_asset_type(self):
        """Test delete an asset type in model"""
        self.assertEqual(self.all_items.count(), 1)
        get_item = Item.objects.get(item_code="IC001")
        get_item.delete()
        self.assertEqual(self.all_items.count(), 0)

    def test_give_item_model_number(self):
        """Test that an item can be assigned a model number"""
        self.assertEqual(self.all_items.count(), 1)
        self.assertEqual(self.all_itemmodels.count(), 1)
        get_itemmodel = ItemModelNumber.objects.get(model_number="IMN50987")
        get_item = Item.objects.get(item_code="IC001")
        get_item.model_number = get_itemmodel
        get_item.save()
        self.assertEqual(str(get_item.model_number), "IMN50987")

    def test_delete_itemmodel_cascades(self):
        """Test that the Item is deleted when model number is deleted"""
        self.assertEqual(self.all_items.count(), 1)
        self.assertEqual(self.all_itemmodels.count(), 1)
        get_itemmodel = ItemModelNumber.objects.get(model_number="IMN50987")
        get_item = Item.objects.get(item_code="IC001")
        get_item.model_number = get_itemmodel
        get_item.save()
        get_itemmodel.delete()
        self.assertEqual(self.all_items.count(), 0)
        self.assertEqual(self.all_itemmodels.count(), 0)
