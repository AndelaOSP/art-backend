# Standard Library
from unittest.mock import patch

# Third-Party Imports
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase

client = APIClient()


class OfficeWorkspaceAPITest(APIBaseTestCase):
    """ Tests for the Office Workspace endpoint"""

    def test_non_authenticated_user_get_office_workspace(self):
        response = client.get(self.office_workspace_url)
        self.assertEqual(
            response.data, {'detail': 'Authentication credentials were not provided.'}
        )

    @patch('api.authentication.auth.verify_id_token')
    def test_can_post_office_workspace(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin_user.email}
        data = {"name": "Entebe", "section": self.floor_section.id}
        response = client.post(
            self.office_workspace_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn("name", response.data.keys())
        self.assertEqual(response.status_code, 201)

    @patch('api.authentication.auth.verify_id_token')
    def test_cant_post_workspace_with_same_name(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin_user.email}
        data = {"name": self.office_workspace.name, "section": self.floor_section.id}
        response = client.post(
            self.office_workspace_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(
            {'non_field_errors': ['The fields name, section must make a unique set.']},
            response.data,
        )
        self.assertEqual(response.status_code, 400)

    @patch('api.authentication.auth.verify_id_token')
    def test_can_edit_workspace(self, mock_verify_token):
        mock_verify_token.return_value = {'email': self.admin_user.email}
        data = {"name": "Deva Workspace", "section": self.floor_section.id}
        res = client.post(
            self.office_workspace_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        office_workspace_url = reverse(
            "office-workspaces-detail", args={res.data.get("id")}
        )
        response = client.put(
            office_workspace_url,
            data={"name": "Devb Workspace", "section": self.floor_section.id},
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data.get('name'), 'Devb Workspace')
        self.assertEqual(response.status_code, 200)

    @patch('api.authentication.auth.verify_id_token')
    def test_delete_of_an_office_workspace(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {'email': self.admin_user.email}
        data = {"name": "Oculus1", "section": self.floor_section.id}

        res = client.post(
            self.office_workspace_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        office_workspace_url = reverse(
            "office-workspaces-detail", args={res.data.get("id")}
        )
        response = client.delete(
            office_workspace_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {'detail': 'Deleted Successfully'})
        self.assertEqual(response.status_code, 204)
