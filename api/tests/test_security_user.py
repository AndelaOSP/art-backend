
from .test_user import UserTestCase, client
from ..models import SecurityUser


class SecurityUserTestCase(UserTestCase):
    def setUp(self):
        UserTestCase.setUp(self)

        self.security_users = "/api/v1/security_users/"

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
        client.login(username='admin@site.com', password='devpassword')
        response = client.get(self.security_users)
        self.assertEqual(len(response.data), SecurityUser.objects.count())
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_user_cannot_get_security_users_emails(self):
        response = client.get(self.security_users)
        self.assertEqual(response.data, {
            "detail": "Authentication credentials were not provided."
        })
        self.assertEqual(response.status_code, 403)
