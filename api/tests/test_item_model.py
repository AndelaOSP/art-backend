from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.contrib.auth import get_user_model

from ..models import Item, ItemModelNumber

User = get_user_model()


class ItemTypeModelTest(TestCase):
    """Tests for the Item Model"""

    def setUp(self):
        self.user = User.objects.create(
            email='test@site.com', cohort=10,
            slack_handle='@test_user', password='devpassword'
        )
        self.test_itemmodel = ItemModelNumber(model_number="IMN50987")
        self.test_itemmodel.save()

        self.test_item = Item(
            item_code="IC001",
            serial_number="SN001",
            model_number=self.test_itemmodel,
            assigned_to=self.user
        )
        self.test_item.save()

        self.all_items = Item.objects.all()
        self.all_itemmodels = ItemModelNumber.objects.all()

    def test_add_new_item(self):
        """Test add new item"""
        self.assertEqual(self.all_items.count(), 1)
        new_item = Item(item_code="IC002",
                        serial_number="SN001",
                        model_number=self.test_itemmodel)
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
        """Test that the Item is not deleted when model number is deleted"""
        self.assertEqual(self.all_items.count(), 1)
        self.assertEqual(self.all_itemmodels.count(), 1)
        get_itemmodel = ItemModelNumber.objects.get(model_number="IMN50987")
        get_item = Item.objects.get(item_code="IC001")
        get_item.model_number = get_itemmodel
        get_item.save()
        with self.assertRaises(ProtectedError):
            get_itemmodel.delete()
        self.assertEqual(self.all_items.count(), 1)
        self.assertEqual(self.all_itemmodels.count(), 1)

    def test_item_status_can_be_changed(self):
        item = Item.objects.get(item_code="IC001")
        item.status = "Allocated"

        self.assertIn("Allocated", item.status)

    def test_item_model_string_representation(self):
        self.assertEqual(str(self.test_item), "IC001, SN001, IMN50987")

    def test_item_status_cannot_be_non_existing_status(self):
        item = Item.objects.get(item_code="IC001")
        item.status = "Unused"
        with self.assertRaises(ValidationError):
            item.save()

        self.assertIn("Available", Item.objects.get(item_code="IC001").status)
