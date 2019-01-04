# Third-Party Imports
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError

# App Imports
from core.tests import CoreBaseTestCase

from ..models import Asset, AssetModelNumber

User = get_user_model()


class AssetTypeModelTest(CoreBaseTestCase):
    """Tests for the Asset Model"""
    def test_add_new_asset(self):
        """Test add new asset"""
        count = Asset.objects.count()
        Asset.objects.create(
            asset_code="testIC002", serial_number="testSN0045", model_number=self.test_assetmodel,
            assigned_to=self.asset_assignee, purchase_date="2018-07-10"
        )
        self.assertEqual(Asset.objects.count(), count + 1)

    def test_cannot_add_existing_serial_number(self):
        """Test cannot add an asset existing serial number"""
        count = Asset.objects.count()
        serial_no = Asset.objects.first().serial_number
        with self.assertRaises(ValidationError):
            Asset.objects.create(
                asset_code="IC002", serial_number=serial_no, model_number=self.test_assetmodel,
                assigned_to=self.asset_assignee, purchase_date="2018-07-10"
            )
        self.assertEqual(Asset.objects.count(), count)

    def test_cannot_add_existing_asset_code(self):
        """Test cannot add an asset existing asset code"""
        count = Asset.objects.count()
        asset_code = Asset.objects.first().asset_code
        with self.assertRaises(ValidationError):
            Asset.objects.create(
                asset_code=asset_code, serial_number="serial_no", model_number=self.test_assetmodel,
                assigned_to=self.asset_assignee, purchase_date="2018-07-10"
            )
        self.assertEqual(Asset.objects.count(), count)

    def test_asset_without_code(self):
        """Test error when new asset lacks serial number and asset code"""
        count = Asset.objects.count()
        new_asset = Asset()
        with self.assertRaises(ValidationError):
            new_asset.save()
        self.assertEqual(Asset.objects.count(), count)

    def test_delete_assetmodel_protects(self):
        """Test cannot delete model number with existing asset"""
        asset_count = Asset.objects.count()
        model_no_count = AssetModelNumber.objects.count()
        with self.assertRaises(ProtectedError):
            self.test_assetmodel.delete()
        self.assertEqual(Asset.objects.count(), asset_count)
        self.assertEqual(AssetModelNumber.objects.count(), model_no_count)

    def test_asset_model_string_representation(self):
        repr_name = "{}, {}, {}".format(
            self.test_asset.asset_code, self.test_asset.serial_number, self.test_asset.model_number
        )
        self.assertEqual(str(self.test_asset), repr_name)

    def test_can_add_asset_without_purchase_date_field(self):
        new_asset = Asset(asset_code="IC0050",
                          serial_number="SN0055",
                          model_number=self.test_assetmodel)
        new_asset.save()
        self.assertIsNone(new_asset.purchase_date)

    def test_that_the_default_verification_status_on_asset_is_true(self):
        self.assertTrue(self.test_asset.verified)
