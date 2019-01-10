# Third-Party Imports
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError

# App Imports
from core.tests import CoreBaseTestCase

from ..models import AssetCategory, AssetMake, AssetModelNumber


class AssetModelNumberTestCase(CoreBaseTestCase):
    def test_can_create_new_model_number(self):
        count = AssetModelNumber.objects.count()
        AssetModelNumber.objects.create(name="101505401", asset_make=self.asset_make)
        self.assertEqual(AssetModelNumber.objects.count(), count + 1)

    def test_cannot_add_existing_model_number(self):
        count = AssetModelNumber.objects.count()
        with self.assertRaises(ValidationError):
            AssetModelNumber.objects.create(
                name=self.test_assetmodel.name, asset_make=self.asset_make
            )
        self.assertEqual(AssetModelNumber.objects.count(), count)

    def test_asset_model_number_string_representation(self):
        get_model_number = AssetModelNumber.objects.first()
        self.assertEqual(str(get_model_number), get_model_number.name)

    def test_cannot_delete_asset_make_with_existing_asset_models(self):
        count_before_delete = AssetMake.objects.count()
        with self.assertRaises(ProtectedError):
            self.asset_make.delete()
        count_after_delete = AssetCategory.objects.count()
        self.assertEqual(count_before_delete, count_after_delete)

    def test_cannot_add_asset_model_with_non_existing_make(self):
        with self.assertRaises(ValueError):
            AssetModelNumber.objects.create(name="Test Model Number", asset_make=39090)
