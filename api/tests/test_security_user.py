# Standard Library
import json
from unittest.mock import patch

# Third-Party Imports
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase
from core.models import APIUser, SecurityUser

client = APIClient()
User = get_user_model()


class SecurityUserTestCase(APIBaseTestCase):
    def setUp(self):
        api_user = APIUser.objects.create(name="test_api_app")
        url = '/api/v1/o/token/'

        payload = {
            "grant_type": "client_credentials",
            "client_secret": api_user.client_secret,
            "client_id": api_user.client_id,
        }

        response = client.post(url, data=payload)

        self.access_token = json.loads(response.content)["access_token"]

    def test_app_can_get_security_users_emails(self):
        response = client.get(
            self.security_users_url,
            HTTP_AUTHORIZATION="Bearer {}".format(self.access_token),
        )
        self.assertEqual(len(response.data["emails"]), SecurityUser.objects.count())
        self.assertEqual(response.status_code, 200)

    def test_app_cannot_get_security_users_emails_without_token(self):
        response = client.get(self.security_users_url)
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            json.loads(response.content)["detail"],
            'Authentication credentials were not provided.',
        )

    def test_app_cannot_get_security_users_emails_with_wrong_token(self):
        response = client.get(
            self.security_users_url,
            HTTP_AUTHORIZATION="Bearer 8UfdDKsanuqJLRWblvcQC1fRUGOcp1",
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            json.loads(response.content)["detail"],
            'Authentication credentials were not provided.',
        )

    def test_non_authenticated_user_view_security_user_api_endpoint(self):
        response = client.get(self.security_users_admin_url)
        self.assertEqual(
            response.data, {'detail': 'Authentication credentials were not provided.'}
        )
        self.assertEqual(response.status_code, 401)

    @patch('api.authentication.auth.verify_id_token')
    def test_non_admin_user_can_view_security_user_api_endpoint(
        self, mock_verify_token
    ):
        mock_verify_token.return_value = {'email': self.user.email}
        response = client.get(
            self.security_users_admin_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(
            response.data,
            {'detail': 'You do not have permission to perform this action.'},
        )
        self.assertEqual(response.status_code, 403)

    @patch('api.authentication.auth.verify_id_token')
    def test_admin_user_add_security_users_from_api_endpoint(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin_user.email}
        users_count_before = User.objects.count()
        data = {"email": "security@mail.com", "badge_number": "B-A-D-G-E-N-O"}
        response = client.post(
            self.security_users_admin_url,
            data=data,
            format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        users_count_after = User.objects.count()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(users_count_after, users_count_before + 1)
        response = client.get(
            self.security_users_admin_url,
            format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertIn(data.get('email'), str(response.json().get('results')))

    @patch('api.authentication.auth.verify_id_token')
    def test_admin_user_view_security_users_from_api_endpoint(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin_user.email}
        response = client.get(
            self.security_users_admin_url,
            format='json',
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), SecurityUser.objects.count())

    @patch('api.authentication.auth.verify_id_token')
    def test_security_user_api_endpoint_cant_allow_patch(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin_user.email}
        response = client.patch(
            self.security_users_admin_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data, {'detail': 'Method "PATCH" not allowed.'})

    @patch('api.authentication.auth.verify_id_token')
    def test_security_user_api_endpoint_cant_allow_delete(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin_user.email}
        response = client.delete(
            self.security_users_admin_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data, {'detail': 'Method "DELETE" not allowed.'})

    @patch('api.authentication.auth.verify_id_token')
    def test_admin_can_filter_security_users_by_status(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        response = client.get(
            '{}?active={}'.format(
                self.security_users_admin_url, self.security_user.is_active
            ),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['email'], self.security_user.email)

    @patch('api.authentication.auth.verify_id_token')
    def test_user_not_in_filter_of_in_active_security_user(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        response = client.get(
            '{}?active={}'.format(
                self.security_users_admin_url, not self.security_user.is_active
            ),
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data, self.security_user.email)
