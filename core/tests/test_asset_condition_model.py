from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Asset, AssetCondition, AssetModelNumber

User = get_user_model()


class AssetConditionModelTest(TestCase):
    """Tests for the Asset Model"""

    def setUp(self):
        self.user = User.objects.create(
            email='test@site.com', cohort=10,
            slack_handle='@test_user', password='devpassword'
        )
        self.user2 = User.objects.create(
            email='test15@site.com', cohort=15,
            slack_handle='@test_user', password='devpassword'
        )

        test_assetmodel = AssetModelNumber(model_number="IMN50987")
        test_assetmodel.save()

        self.asset_condition = AssetCondition()
        self.asset_condition.save()

        self.test_asset = Asset(
            asset_code="IC001",
            serial_number="SN001",
            model_number=test_assetmodel,
            current_condition=self.asset_condition
        )
        self.test_asset.save()

    def test_create_asset_creates_default_assest_condition(self):
        self.assertEqual(AssetCondition.objects.count(), 1)
        self.assertEqual(self.asset_condition.current_condition, 'Brand New')

    def test_edit_assest_condition(self):
        self.asset_condition.current_condition = 'Working'
        self.asset_condition.condition_description = 'Working'

        self.assertEqual(AssetCondition.objects.count(), 1)
        self.assertEqual(self.asset_condition.current_condition, 'Working')
