from json import loads, dumps

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Asset


class CheckoutTestCase(TestCase):
    """ This class defines the test suite for the CheckoutLog model """

    def setUp(self):
        """ Define the test client and other test variables """
        # create user
        user = User(username='testuser')
        user.is_superuser = True
        user.save()

        # create test client
        self.client = APIClient()
        self.client.force_authenticate(user=user)

        # create asset
        asset = Asset()
        asset.full_name = 'Test User'
        asset.charger_tag = 'AND/CHARG/01'
        asset.cohort = '19'
        asset.headsets_sn = 'AND/HS/01'
        asset.headsets_tag = 'AND/HT/01'
        asset.mac_book_sn = 'AND/TMAC/01'
        asset.tb_dongle_tag = 'AND/TB/01'
        asset.mac_book_tag = 'AND/TMAC/01'
        asset.date_created = '2018-08-08'
        asset.date_modified = '2018-08-08'
        asset.save()

    def test_model_can_create_a_checkout_log(self):
        """ Test checkoutlog model can create a checkout """
        checkout_data = {
            'user_id': 1,
            'mac_book': False,
            'charger': False,
            'tb_dongle': False,
            'head_set': False
        }
        res = self.client.post('/art_api/checkout',
                               data=checkout_data, format="json")
        self.assertEqual(res.status_code,  status.HTTP_201_CREATED)
        self.assertEqual(res.data.get('charger'), checkout_data.get('charger'))

    def test_model_can_get_checkoutlog(self):
        """ Test checkoutlog model can get previous checkoutlogs """
        checkout_data = {
            'user_id': 2,
            'mac_book': False,
            'charger': False,
            'tb_dongle': False,
            'head_set': False
        }
        self.client.post('/art_api/checkout',
                         data=checkout_data, format="json")
        res = self.client.get('/art_api/checkout/2', format="json")
        self.assertEqual(res.status_code,  status.HTTP_200_OK)
        self.assertEqual(loads(dumps(res.data))[0].get(
            'mac_book'), checkout_data.get('mac_book'))
