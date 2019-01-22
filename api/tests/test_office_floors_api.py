# Standard Library
from unittest.mock import patch

# Third-Party Imports
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase

client = APIClient()


class OfficeFloorAPITest(APIBaseTestCase):
    """ Tests for the OfficeFloor endpoint"""

    def test_non_authenticated_user_get_office_block(self):
        response = client.get(self.floor_number_url)
        self.assertEqual(
            response.data, {'detail': 'Authentication credentials were not provided.'}
        )

    @patch('api.authentication.auth.verify_id_token')
    def test_can_post_floor_number(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin_user.email}
        data = {"number": 25, "block": self.office_block.id}
        response = client.post(
            self.floor_number_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn("number", response.data.keys())
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_cant_post_floor_number_with_same_name(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin_user.email}
        data = {"number": self.office_floor.number, "block": self.office_block.id}
        response = client.post(
            self.floor_number_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(
            response.data,
            {'non_field_errors': ['The fields block, number must make a unique set.']},
        )
        self.assertEqual(response.status_code, 400)

    @patch('api.authentication.auth.verify_id_token')
    def test_floor_number_api_endpoint_cant_allow_put(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        data = {}
        response = client.put(
            self.floor_number_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {'detail': 'Method "PUT" not allowed.'})
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_office_block_api_endpoint_cant_allow_patch(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        data = {}
        response = client.patch(
            self.floor_number_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {'detail': 'Method "PATCH" not allowed.'})
        self.assertEqual(response.status_code, 405)

    @patch('api.authentication.auth.verify_id_token')
    def test_office_block_api_endpoint_cant_allow_delete(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        data = {}
        response = client.delete(
            self.floor_number_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {'detail': 'Method "DELETE" not allowed.'})
        self.assertEqual(response.status_code, 405)
