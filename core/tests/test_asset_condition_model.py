from django.contrib.auth import get_user_model

from ..models import (
    Asset,
    AssetModelNumber,
    AssetMake,
    AssetType,
    AssetSubCategory,
    AssetCategory,
    AssetCondition
)

from core.tests import CoreBaseTestCase
User = get_user_model()


class AssetConditionModelTest(CoreBaseTestCase):
    """Tests for the Asset Model"""

    def setUp(self):
        super(AssetConditionModelTest, self).setUp()
        self.user = User.objects.create(
            email='test@site.com', cohort=10,
            slack_handle='@test_user', password='devpassword'
        )
        self.user2 = User.objects.create(
            email='test15@site.com', cohort=15,
            slack_handle='@test_user', password='devpassword'
        )
        asset_category = AssetCategory.objects.create(
            category_name="Computer")
        asset_sub_category = AssetSubCategory.objects.create(
            sub_category_name="Electronics", asset_category=asset_category)
        asset_type = AssetType.objects.create(
            asset_type="Accessory", asset_sub_category=asset_sub_category)
        make_label = AssetMake.objects.create(
            make_label="Sades", asset_type=asset_type)
        self.test_assetmodel = AssetModelNumber(
            model_number="12345", make_label=make_label)
        test_assetmodel = AssetModelNumber(
            model_number="IMN50987", make_label=make_label)
        test_assetmodel.save()

        self.test_asset = Asset(
            asset_code="IC001",
            serial_number="SN001",
            model_number=test_assetmodel,
            purchase_date="2018-07-10"
        )
        self.test_asset.save()

        self.assetcondition = AssetCondition(
            asset_condition='Brand New',
            asset=self.test_asset
        )
        self.assetcondition.save()

    def test_create_asset_creates_default_assest_condition(self):
        self.assertEqual(AssetCondition.objects.count(), 1)
        self.assertEqual(self.assetcondition.asset_condition,
                         'Brand New')

    def test_edit_asset_condition(self):
        self.assetcondition.asset_condition = 'Working'

        self.assertEqual(AssetCondition.objects.count(), 1)
        self.assertEqual(self.assetcondition.asset_condition, 'Working')
