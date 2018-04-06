from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from ..models import SecurityUser
client = APIClient()


class SecurityUserTestCase(TestCase):
    def setUp(self):
        self.security_users_url = reverse('security_users-list')

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

    def test_admin_can_get_security_users_emails(self):
        response = client.get(self.security_users_url)
        self.assertEqual(len(response.data["emails"]),
                         SecurityUser.objects.count())
        self.assertEqual(response.status_code, 200)
