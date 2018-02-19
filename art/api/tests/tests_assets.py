from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.test import TestCase
from django.contrib.auth.models import User

from ..models import Asset, CheckinLogs, CheckoutLogs
from ..views import AssetCreateApiView, AssetGetUpdateDelete


class AssetCreateApiView(TestCase):
    """This class tests the methods of the Asset view classes"""

    def setUp(self):
        self.client = APIClient()
        self.asset_data_1 = {
            "full_name": "Test Asset",
            "cohort": "13",
            "mac_book_sn": "sn_mac_001",
            "mac_book_tag": "tag_mac_001",
            "charger_tag": "tag_chg_001",
            "tb_dongle_tag": "tag_dng_001",
            "headsets_sn": "sn_hdst_001",
            "headsets_tag": "tag_hdst_001"
        }
        self.asset_data_2 = {
            "full_name": "Test Asset 2",
            "cohort": "4",
            "mac_book_sn": "sn_mac_002",
            "mac_book_tag": "tag_mac_002",
            "charger_tag": "tag_chg_002",
            "tb_dongle_tag": "tag_dng_002",
            "headsets_sn": "sn_hdst_002",
            "headsets_tag": "tag_hdst_002"
        }
        new_user = User.objects.create_superuser(username="test_user",
                                                 email="test@email.com",
                                                 password="password")
        new_user.save()
        self.client.login(username="test_user", password="password")

    def test_create_new_asset(self):
        """Create a new asset using the POST request"""

        self.response = self.client.post(reverse('create_assets'),
                                         self.asset_data_1, format='json')
        self.assertEqual(self.response.status_code, 201)

    def test_create_existing_asset(self):
        """Create already existing asset"""

        self.response = self.client.post(reverse('create_assets'),
                                         self.asset_data_1, format='json')
        self.assertEqual(self.response.status_code, 201)
        self.response = self.client.post(reverse('create_assets'),
                                         self.asset_data_1, format='json')
        self.assertEqual(self.response.status_code, 409)

    def test_get_all_assets(self):
        """ GET all assets"""

        self.client.post(reverse('create_assets'), self.asset_data_1,
                         format='json')
        self.client.post(reverse('create_assets'), self.asset_data_2,
                         format='json')
        self.response = self.client.get(reverse('create_assets'))
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(len(self.response.data), 2)

    def test_get_one_asset(self):
        """GET one asset by id"""

        self.client.post(reverse('create_assets'), self.asset_data_1,
                         format='json')
        self.asset = Asset.objects.get(full_name='Test Asset')
        self.response = self.client.get(reverse('edit_assets',
                                                args=[self.asset.id]),
                                        format='json')
        self.assertEqual(self.response.status_code, 200)

    def test_edit_one_asset(self):
        """Edit one asset using PUT request"""

        self.edit_name = {"full_name": "New name"}
        self.client.post(reverse('create_assets'), self.asset_data_1,
                         format='json')
        self.asset = Asset.objects.get(full_name='Test Asset')
        self.response = self.client.put(reverse('edit_assets',
                                                args=[self.asset.id]),
                                        self.edit_name, format='json')
        self.assertEqual(self.response.status_code, 200)

    def test_delete_asset(self):
        """DELETE one asset"""

        self.client.post(reverse('create_assets'), self.asset_data_1,
                         format='json')
        self.asset = Asset.objects.get(full_name='Test Asset')
        self.response = self.client.delete(reverse('edit_assets',
                                                   args=[self.asset.id]),
                                           format='json')
        self.assertEqual(self.response.status_code, 204)
