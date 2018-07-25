from unittest.mock import patch
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from core.models import OfficeBlock, User, FloorSection, OfficeFloor

from api.tests import APIBaseTestCase

client = APIClient()


class FloorSectionAPITest(APIBaseTestCase):
    """ Tests for the FloorSection endpoint"""

    def setUp(self):
        super(FloorSectionAPITest, self).setUp()
        self.admin = User.objects.create_superuser(
            email='testuser@gmail.com', cohort=19,
            slack_handle='tester', password='qwerty123'
        )
        self.building = OfficeBlock.objects.create(
            name="Block A"
        )
        self.floor = OfficeFloor.objects.create(
            number=1,
            block=self.building)
        self.floor_section = FloorSection.objects.create(
            section_name="Big Apple",
            floor_number=self.floor
        )
        self.floor_section_url = reverse('floor-sections-list')
        self.token_user = 'testtoken'

    def test_non_authenticated_user_get_floor_section(self):
        response = client.get(self.floor_section_url)
        self.assertEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_can_post_floor_section(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin.email}
        data = {
            "floor_number": self.floor,
            "section_name": "Gbagada"
        }
        response = client.post(
            self.floor_section_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        gbagada_section = FloorSection.objects.get(section_name="Gbagada")
        self.assertTrue(gbagada_section, "Section doesn't exist in database")
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_cant_post_floor_section_with_same_name(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin.email}
        data = {
            "section_name": "Big Apple",
            "floor_number": self.floor
        }
        response = client.post(
            self.floor_section_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn("floor_number", response.data.keys())
        self.assertEqual(response.status_code, 400)

    @patch('api.authentication.auth.verify_id_token')
    def test_floor_section_api_endpoint_cant_allow_put(self,
                                                       mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin.email}
        data = {}
        response = client.put(
            self.floor_section_url,
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
            self.floor_section_url,
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
            self.floor_section_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Method "DELETE" not allowed.'
        })
        self.assertEqual(response.status_code, 405)
