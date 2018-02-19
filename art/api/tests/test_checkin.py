from json import loads, dumps
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from ..models import Asset


class CheckinTestCase(TestCase):
    """ Test suit for the checkin endpoints """

    def setUp(self):
        """ Setup test user, test client and save test asset """
        user = User(username="nerd")
        user.is_superuser = True
        user.save()

        self.client = APIClient()
        self.client.force_authenticate(user=user)

        asset = Asset()

        asset.full_name = 'John Doe'
        asset.cohort = '20'
        asset.mac_book_sn = 'SCWE23'
        asset.mac_book_tag = 'AND/1235'
        asset.charger_tag = 'AND/PRO'
        asset.tb_dongle_tag = 'TB/34'
        asset.headsets_sn = 'SN492'
        asset.date_created = '2018-02-09'
        asset.date_modified = '2018-02-09'

        asset.save()

    def test_create_one_checkin_log(self):
        """ Test create one checkin log """
        checkin_data = {
            "user_id": 1,
            "mac_book": True,
            "charger": False,
            "tb_dongle": True,
            "head_set": False,
        }
        response = self.client.post('/art_api/checkin', data=checkin_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user_id", loads(dumps(response.data)))

    def test_get_one_checkin_log(self):
        """ Test get one checkin log """
        checkin_data = {
            "user_id": 2,
            "mac_book": True,
            "charger": False,
            "tb_dongle": False,
            "head_set": False,
        }
        self.client.post('/art_api/checkin', data=checkin_data, format="json")

        response = self.client.get('/art_api/checkin/2', format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(loads(dumps(response.data))[0]["tb_dongle"])

