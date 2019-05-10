# Standard Library
from unittest.mock import patch

# Third-Party Imports
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase
from core.models import OfficeFloorSection

client = APIClient()


class OfficeFloorSectionAPITest(APIBaseTestCase):
    """ Tests for the OfficeFloorSection endpoint"""

    def test_non_authenticated_user_get_floor_section(self):
        response = client.get(self.floor_section_url)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_can_post_floor_section(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {"floor": self.office_floor.id, "name": "Gbagada"}
        response = client.post(
            self.floor_section_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        gbagada_section = OfficeFloorSection.objects.get(name="Gbagada")
        self.assertTrue(gbagada_section, "Section doesn't exist in database")
        self.assertEqual(response.status_code, 201)

    @patch("api.authentication.auth.verify_id_token")
    def test_can_get_floor_section(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            f"{self.floor_section_url}/{self.floor_section.id}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.floor_section.id)
        self.assertEqual(response.data["name"], self.floor_section.name)
        self.assertEqual(response.data["floor"]["id"], self.floor_section.floor.id)
        self.assertEqual(
            response.data["floor"]["number"], self.floor_section.floor.number
        )
        self.assertEqual(
            response.data["block"]["id"], self.floor_section.floor.block.id
        )
        self.assertEqual(
            response.data["block"]["name"], self.floor_section.floor.block.name
        )
        self.assertEqual(response.data["workspaces"][0]["id"], self.office_workspace.id)
        self.assertEqual(
            response.data["workspaces"][0]["name"], self.office_workspace.name
        )
        self.assertEqual(
            response.data["workspaces"][0]["section"], self.office_workspace.section.id
        )
        self.assertEqual(
            response.data["workspaces"][0]["floor"],
            self.office_workspace.section.floor.number,
        )
        self.assertEqual(
            response.data["workspaces"][0]["block"],
            self.office_workspace.section.floor.block.name,
        )
        longname = (
            f"{self.office_workspace.section.floor.block.name}-"
            f"{self.office_workspace.section.floor.number}-"
            f"{self.office_workspace.section.name}-"
            f"{self.office_workspace.name}"
        )
        self.assertEqual(response.data["workspaces"][0]["long_name"], longname)

    @patch("api.authentication.auth.verify_id_token")
    def test_cant_post_floor_section_with_same_name(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {"name": self.floor_section.name, "floor": self.office_floor}
        response = client.post(
            self.floor_section_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertIn("floor", response.data.keys())

    @patch("api.authentication.auth.verify_id_token")
    def test_office_block_api_endpoint_cant_allow_patch(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {}
        response = client.patch(
            self.floor_section_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"detail": 'Method "PATCH" not allowed.'})
        self.assertEqual(response.status_code, 405)

    @patch("api.authentication.auth.verify_id_token")
    def test_office_block_api_endpoint_cant_allow_delete(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {}
        response = client.delete(
            self.floor_section_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"detail": 'Method "DELETE" not allowed.'})
        self.assertEqual(response.status_code, 405)
