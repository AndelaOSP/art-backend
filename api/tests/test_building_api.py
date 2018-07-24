from unittest.mock import patch
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from core.models import OfficeBlock, User

from api.tests import APIBaseTestCase

client = APIClient()


class OfficeBlockAPITest(APIBaseTestCase):
    """ Tests for the OfficeBlock endpoint"""

    def setUp(self):
        super(OfficeBlockAPITest, self).setUp()
        self.admin = User.objects.create_superuser(
            email='testuser@gmail.com', cohort=19,
            slack_handle='tester', password='qwerty123'
        )

        self.building = OfficeBlock.objects.create(
            name="Block A"
        )
        self.office_block_url = reverse('office-blocks-list')
        self.token_user = 'testtoken'

    def test_non_authenticated_user_get_office_block(self):
        response = client.get(self.office_block_url)
        self.assertEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_can_post_office_block(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin.email}
        data = {
            "name": "Block B",
        }
        response = client.post(
            self.office_block_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn("name", response.data.keys())
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_cant_post_office_block_with_same_name(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin.email}
        data = {
            "name": "Block A",
        }
        response = client.post(
            self.office_block_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn("name", response.data.keys())
        self.assertEqual(response.status_code, 400)

    @patch('api.authentication.auth.verify_id_token')
    def test_office_block_api_endpoint_cant_allow_put(self,
                                                      mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin.email}
        data = {}
        response = client.put(
            self.office_block_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PUT" not allowed.'
        })
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_office_block_api_endpoint_cant_allow_patch(self,
                                                        mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin.email}
        data = {}
        response = client.patch(
            self.office_block_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "PATCH" not allowed.'
        })
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_office_block_api_endpoint_cant_allow_delete(self,
                                                         mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin.email}
        data = {}
        response = client.delete(
            self.office_block_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "DELETE" not allowed.'
        })
        self.assertEqual(response.status_code, 405)
