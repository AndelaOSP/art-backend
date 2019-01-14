# Third-Party Imports
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

# App Imports
from core.tests import CoreBaseTestCase

from ..models import Asset, AssetSpecs

User = get_user_model()


class AssetModelNumberTestCase(CoreBaseTestCase):
    def test_can_create_new_asset_specs(self):
        count = AssetSpecs.objects.count()
        asset_specs = AssetSpecs.objects.create(
            screen_size=15,
            year_of_manufacture=2017,
            processor_speed=3.0,
            processor_type="Intel core i5",
            memory=16,
            storage=512,
        )
        self.assertEqual(AssetSpecs.objects.count(), count + 1)

        new_asset = Asset.objects.create(
            asset_code="IC010",
            serial_number="SN00450",
            model_number=self.test_assetmodel,
            purchase_date="2018-07-10",
            assigned_to=self.asset_assignee,
            specs=asset_specs,
        )
        self.assertEqual(new_asset.serial_number, "SN00450")
        self.assertEqual(new_asset.specs.screen_size, 15)

    def test_should_not_create_field_with_invalid_choices(self):
        with self.assertRaises(ValidationError):
            AssetSpecs.objects.create(
                screen_size=19,
                year_of_manufacture=2011,
                processor_speed=3.0,
                processor_type="Intel core i5",
                memory=16,
                storage=512,
            )

    def test_can_create_specs_with_some_empty_fields(self):
        new_asset = AssetSpecs.objects.create(screen_size=15, memory=8, storage=256)
        self.assertEqual(new_asset.screen_size, 15)
