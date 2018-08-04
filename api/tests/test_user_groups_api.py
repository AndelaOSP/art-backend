from unittest.mock import patch
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from core.models import User
from django.contrib.auth.models import Group

from api.tests import APIBaseTestCase
client = APIClient()


class UserGroupTestCase(APIBaseTestCase):
    """ Tests fro the UserGroup endpoint """

    def setUp(self):
        super(UserGroupTestCase, self).setUp()
        self.admin = User.objects.create_superuser(
            email='adminuser@gmail.com', cohort=1,
            slack_handle='admintester', password='admin1234'
        )

        self.user_group = Group.objects.create(
            name='admin'
        )

        self.user_group_url = reverse('user-groups-list')
        self.token_user = 'testtoken'

    @patch('api.authentication.auth.verify_id_token')
    def test_can_post_user_group(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin.email}
        data = {
            "name": "super admin"
        }
        response = client.post(
            self.user_group_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn("name", response.data.keys())
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_can_get_all_user_groups(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin.email}
        response = client.get(
            self.user_group_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))

        self.assertEqual(len(response.data['results']),
                         Group.objects.count())
        self.assertIn("name", response.data['results'][0].keys())
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_user_groups_api_endpoint_cant_allow_put(self,
                                                     mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin.email}
        data = {}
        response = client.put(
            self.user_group_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PUT" not allowed.'
        })
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_user_groups_api_endpoint_cant_allow_patch(self,
                                                       mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin.email}
        data = {}
        response = client.patch(
            self.user_group_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PATCH" not allowed.'
        })
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_user_groups_api_endpoint_cant_allow_delete(self,
                                                        mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin.email}
        data = {}
        response = client.delete(
            self.user_group_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "DELETE" not allowed.'
        })
        self.assertEqual(response.status_code, 405)
