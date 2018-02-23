from django.test import TestCase

from ..models import AssetMake


class AssetMakeTestCase(TestCase):
    def setUp(self):
        AssetMake.objects.create(make_label="Microsoft Lifechat LX-6000")
        self.laptop_make = AssetMake.objects.get (make_label="Microsoft Lifechat LX-6000")

    def test_can_create_asset_make(self):
        self.assertEqual(AssetMake.objects.count(), 1)
        AssetMake.objects.create (make_label="OS X 10.6 Snow Leopard")
        self.assertEqual (AssetMake.objects.count(), 2)

    def test_can_edit_asset_make(self):
        self.laptop_make.make_label = "LionOS X 10.7.x"
        self.assertEqual(self.laptop_make.make_label, "LionOS X 10.7.x")

    def test_can_delete_asset_model(self):
        self.assertEqual(AssetMake.objects.count(), 1)
        self.laptop_make.delete()
        self.assertEqual(AssetMake.objects.count(), 0)
