from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from ..models import (
    AssetSpecs,
    Asset,
    AssetCategory,
    AssetSubCategory,
    AssetType,
    AssetMake,
    AssetModelNumber
)
from core.tests import CoreBaseTestCase
User = get_user_model()


class AssetModelNumberTestCase(CoreBaseTestCase):
    def setUp(self):
        super(AssetModelNumberTestCase, self).setUp()
        self.user = User.objects.create(
            email='test@site.com', cohort=10,
            slack_handle='@test_user', password='devpassword'
        )

        asset_category = AssetCategory.objects.create(
            category_name="Computer")
        asset_sub_category = AssetSubCategory.objects.create(
            sub_category_name="Laptops", asset_category=asset_category)
        asset_type = AssetType.objects.create(
            asset_type="Mini Laptops", asset_sub_category=asset_sub_category)
        make_label = AssetMake.objects.create(
            make_label="Apple", asset_type=asset_type)
        self.test_assetmodel = AssetModelNumber.objects.create(
            model_number="IMN50045", make_label=make_label)

        self.asset_specs = AssetSpecs.objects.create(
            screen_size=13,
            year_of_manufacture=2018,
            processor_speed=3.0,
            processor_type="Intel core i5",
            memory=16,
            storage=256
        )

    def test_can_create_new_asset_specs(self):
        self.assertEqual(AssetSpecs.objects.count(), 1)
        AssetSpecs.objects.create(
            screen_size=15,
            year_of_manufacture=2017,
            processor_speed=3.0,
            processor_type="Intel core i5",
            memory=16,
            storage=512
        )
        self.assertEqual(AssetSpecs.objects.count(), 2)

    def test_create_new_asset_with_specs(self):
        new_asset = Asset.objects.create(asset_code="IC010",
                                         serial_number="SN00450",
                                         model_number=self.test_assetmodel,
                                         purchase_date="2018-07-10",
                                         assigned_to=self.user,
                                         specs=self.asset_specs)
        self.assertEqual(new_asset.serial_number, "SN00450")
        self.assertEqual(new_asset.specs.screen_size, 13)

    def test_should_not_create_field_with_invalid_choices(self):
        with self.assertRaises(ValidationError):
            AssetSpecs.objects.create(
                screen_size=19,
                year_of_manufacture=2011,
                processor_speed=3.0,
                processor_type="Intel core i5",
                memory=16,
                storage=512
            )

    def test_can_create_specs_with_some_empty_fields(self):
        new_asset = AssetSpecs.objects.create(
            screen_size=15,
            memory=8,
            storage=256
        )
        self.assertEqual(new_asset.screen_size, 15)
