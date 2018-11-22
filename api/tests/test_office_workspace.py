from unittest.mock import patch
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from core.models import OfficeWorkspace, User, \
    OfficeFloor, OfficeBlock, OfficeFloorSection, AndelaCentre

from api.tests import APIBaseTestCase

client = APIClient()


class OfficeWorkspaceAPITest(APIBaseTestCase):
    """ Tests for the Office Workspace endpoint"""

    def setUp(self):
        super(OfficeWorkspaceAPITest, self).setUp()
        self.centre = AndelaCentre.objects.create(
            centre_name="Dojo",
            country="Kenya"
        )
        self.admin = User.objects.create_superuser(
            email='testuser@gmail.com', cohort=19,
            slack_handle='tester', password='qwerty123',
            location=self.centre
        )
        self.building = OfficeBlock.objects.create(
            name="Block A",
            location=self.centre
        )
        self.floor_number = OfficeFloor.objects.create(
            number=5,
            block=self.building
        )
        self.floor_section = OfficeFloorSection.objects.create(
            name="kitchenette",
            floor=self.floor_number
        )
        self.office_workspace = OfficeWorkspace.objects.create(
            name="Oculus",
            section=self.floor_section
        )
        self.office_workspace_url = reverse('office-workspaces-list')
        self.token_user = 'testtoken'

    def test_non_authenticated_user_get_office_workspace(self):
        response = client.get(self.office_workspace_url)
        self.assertEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })

    @patch('api.authentication.auth.verify_id_token')
    def test_can_post_office_workspace(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin.email}
        data = {
            "name": "Entebe",
            "section": self.floor_section.id
        }
        response = client.post(
            self.office_workspace_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertIn("name", response.data.keys())
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_cant_post_workspace_with_same_name(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin.email}
        data = {
            "name": "Oculus",
            "section": self.floor_section.id
        }
        response = client.post(
            self.office_workspace_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(
            {'non_field_errors':
             ['The fields name, section must make a unique set.']},
            response.data)
        self.assertEqual(response.status_code, 400)

    @patch('api.authentication.auth.verify_id_token')
    def test_can_edit_workspace(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin.email}
        data = {
            "name": "Deva Workspace",
            "section": self.floor_section.id
        }
        res = client.post(
            self.office_workspace_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        office_workspace_url = reverse("office-workspaces-detail",
                                       args={res.data.get("id")})
        response = client.put(
            office_workspace_url,
            data={"name": "Devb Workspace", "section": self.floor_section.id},
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data.get('name'), 'Devb Workspace')
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_delete_of_an_office_workspace(
            self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin.email}
        data = {
            "name": "Oculus1",
            "section": self.floor_section.id
        }

        res = client.post(
            self.office_workspace_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        office_workspace_url = reverse("office-workspaces-detail",
                                       args={res.data.get("id")})
        response = client.delete(
            office_workspace_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user))
        self.assertEqual(response.data, {
            'detail': 'Deleted Successfully'
        })
        self.assertEqual(response.status_code, 204)
