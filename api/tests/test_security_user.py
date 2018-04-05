from .test_user import UserTestCase, client, patch
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

    @patch('api.authentication.auth.verify_id_token')
    def test_admin_can_get_security_users_emails(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin_user.email}
        response = client.get(
            self.security_users,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin)
        )
        self.assertEqual(len(response.data["emails"]),
                         SecurityUser.objects.count())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_user_can_get_security_users_emails(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.user.email}
        response = client.get(
            self.security_users,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin)
        )

        self.assertIn(response.data["emails"][0], "sectest1@andela.com")
        self.assertIn(response.data["emails"][1], "sectest2@andela.com")

    @patch('api.authentication.auth.verify_id_token')
    def test_non_user_cannot_get_security_emails(self, mock_verify_token):
        mock_verify_token.return_value = {"email": "nonuser@example.com"}
        response = client.get(
            self.security_users,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {"detail": "Unable to authenticate."})
        self.assertEqual(response.status_code, 401)
