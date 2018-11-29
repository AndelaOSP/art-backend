from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError

from ..models import AssetModelNumber, AssetMake, AssetCategory
from core.tests import CoreBaseTestCase


class AssetModelNumberTestCase(CoreBaseTestCase):
    def test_can_create_new_model_number(self):
        count = AssetModelNumber.objects.count()
        AssetModelNumber.objects.create(model_number="101505401",
                                        make_label=self.asset_make)
        self.assertEqual(AssetModelNumber.objects.count(), count + 1)

    def test_cannot_add_existing_model_number(self):
        count = AssetModelNumber.objects.count()
        with self.assertRaises(ValidationError):
            AssetModelNumber.objects.create(
                model_number=self.test_assetmodel.model_number,
                make_label=self.asset_make
            )
        self.assertEqual(AssetModelNumber.objects.count(), count)

    def test_asset_model_number_string_representation(self):
        get_model_number = AssetModelNumber.objects.first()
        self.assertEqual(str(get_model_number), get_model_number.model_number)

    def test_cannot_delete_asset_make_with_existing_asset_models(self):
        count_before_delete = AssetMake.objects.count()
        with self.assertRaises(ProtectedError):
            self.asset_make.delete()
        count_after_delete = AssetCategory.objects.count()
        self.assertEqual(count_before_delete, count_after_delete)

    def test_cannot_add_asset_model_with_non_existing_make(self):
        with self.assertRaises(ValueError):
            AssetModelNumber.objects.create(
                model_number="Test Model Number",
                make_label=39090
            )
