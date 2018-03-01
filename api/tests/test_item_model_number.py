from django.test import TestCase

from ..models import ItemModelNumber


class ItemModelNumberTestCase(TestCase):
    def setUp(self):
        ItemModelNumber.objects.create(model_number="101505400")
        self.laptop_model_number = ItemModelNumber.objects.get(
            model_number="101505400"
        )

    def test_can_create_new_model_number(self):
        self.assertEqual(ItemModelNumber.objects.count(), 1)
        ItemModelNumber.objects.create(model_number="101505401")
        self.assertEqual(ItemModelNumber.objects.count(), 2)

    def test_can_edit_model_number(self):
        self.laptop_model_number.model_number = "101505400"
        self.assertEqual(self.laptop_model_number.model_number, "101505400")

    def test_can_delete_model_number(self):
        self.assertEqual(ItemModelNumber.objects.count(), 1)
        self.laptop_model_number.delete()
        self.assertEqual(ItemModelNumber.objects.count(), 0)

    def test_item_model_number_string_representation(self):
        get_model_number = ItemModelNumber.objects.get(
            model_number="101505400")
        self.assertEquals(str(get_model_number), "101505400")
