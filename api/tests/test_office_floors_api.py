from unittest.mock import patch
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from core.models import OfficeBlock, User, OfficeFloor, \
    AndelaCentre

from api.tests import APIBaseTestCase

client = APIClient()


class OfficeFloorAPITest(APIBaseTestCase):
    """ Tests for the OfficeFloor endpoint"""

    def setUp(self):
        super(OfficeFloorAPITest, self).setUp()
        self.centre = AndelaCentre.objects.create(
            centre_name="Dojo",
            country="Kenya"
        )
        self.centre2 = AndelaCentre.objects.create(
            centre_name="Epic Towers",
            country="Nigeria"
        )
        self.admin = User.objects.create_superuser(
            email='testuser@gmail.com', cohort=19,
            slack_handle='tester', password='qwerty123',
            location=self.centre
        )

        self.admin2 = User.objects.create_superuser(
            email='testuser2@gmail.com', cohort=19,
            slack_handle='tester2', password='qwerty123',
            location=self.centre2
        )

        self.building = OfficeBlock.objects.create(
            name="Block A",
            location=self.centre
        )

        self.building2 = OfficeBlock.objects.create(
            name="Block B",
            location=self.centre2
        )

        self.floor_number = OfficeFloor.objects.create(
            number=5,
            block=self.building
        )

        self.floor_number = OfficeFloor.objects.create(
            number=2,
            block=self.building2
        )

        self.floor_number_url = reverse('office-floors-list')
        self.token_user = 'testtoken'

    def test_non_authenticated_user_get_office_block(self):
        response = client.get(self.floor_number_url)
        self.assertEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_admin_can_view_office_in_location(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin.email}
        response = client.get(
            self.floor_number_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['count'], 1)

    @patch('api.authentication.auth.verify_id_token')
    def test_can_post_floor_number(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin.email}
        data = {
            "number": 25,
            "block": self.building.id
        }
        response = client.post(
            self.floor_number_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn("number", response.data.keys())
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_cant_post_floor_number_with_same_name(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin.email}
        data = {
            "number": 5,
            "block": self.building.id
        }
        response = client.post(
            self.floor_number_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'non_field_errors': [
                'The fields block, number must make a unique set.'
            ]
        })
        self.assertEqual(response.status_code, 400)

    @patch('api.authentication.auth.verify_id_token')
    def test_floor_number_api_endpoint_cant_allow_put(self,
                                                      mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin.email}
        data = {}
        response = client.put(
            self.floor_number_url,
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
            self.floor_number_url,
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
            self.floor_number_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "DELETE" not allowed.'
        })
        self.assertEqual(response.status_code, 405)
