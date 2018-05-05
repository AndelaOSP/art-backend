import json
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from core.models import SecurityUser, APIUser

client = APIClient()


class SecurityUserTestCase(TestCase):
    def setUp(self):
        self.security_users_url = reverse('security-user-emails-list')

        SecurityUser.objects.create(
            email="sectest1@andela.com",
            password="devpassword",
            first_name="TestFirst",
            last_name="TestLast",
            phone_number="254720900900",
            badge_number="AE23"
        )
        SecurityUser.objects.create(
            email="sectest2@andela.com",
            password="devpassword",
            first_name="TestFirst2",
            last_name="TestLast2",
            phone_number="254720900900",
            badge_number="AE24"
        )

        api_user = APIUser.objects.create(
            name="test_api_app"
        )
        url = '/api/v1/o/token/'

        payload = {
            "grant_type": "client_credentials",
            "client_secret": api_user.client_secret,
            "client_id": api_user.client_id
        }

        response = client.post(url, data=payload)

        self.access_token = json.loads(response.content)["access_token"]

    def test_app_can_get_security_users_emails(self):
        response = client.get(
            self.security_users_url,
            HTTP_AUTHORIZATION="Bearer {}".format(self.access_token))
        self.assertEqual(len(response.data["emails"]),
                         SecurityUser.objects.count())
        self.assertEqual(response.status_code, 200)

    def test_app_cannot_get_security_users_emails_without_token(self):
        response = client.get(self.security_users_url)
        self.assertEqual(response.status_code, 401)
        self.assertIn(json.loads(response.content)["detail"],
                      'Authentication credentials were not provided.')

    def test_app_cannot_get_security_users_emails_with_wrong_token(self):
        response = client.get(
            self.security_users_url,
            HTTP_AUTHORIZATION="Bearer 8UfdDKsanuqJLRWblvcQC1fRUGOcp1")
        self.assertEqual(response.status_code, 401)
        self.assertIn(json.loads(response.content)["detail"],
                      'Authentication credentials were not provided.')
