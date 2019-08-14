# Standard Library
from unittest.mock import patch

# Third-Party Imports
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase

client = APIClient()


class Post_OfficeBlockAPITest(APIBaseTestCase):
    """ Tests for the OfficeBlock endpoint"""

    def test_non_authenticated_user_cannot_create_office_block(self):
        data = {"name": "Block B", "location": self.centre.id}
        response = client.post(
            self.office_block_url,
            data=data,
        )
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_can_post_office_block(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {"name": "Block B", "location": self.centre.id}
        response = client.post(
            self.office_block_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual(response.data['location'], self.centre.id)
    
    @patch("api.authentication.auth.verify_id_token")
    def test_cannot_post_office_block_with_empty_fields(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {"name": "", "location": self.centre.id}
        response = client.post(
            self.office_block_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['name'][0], 'This field may not be blank.')
    
    @patch("api.authentication.auth.verify_id_token")
    def test_cant_post_office_block_with_same_name(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {"name": self.office_block.name, "location": self.centre.id}
        response = client.post(
            self.office_block_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.status_code, 400)


class Get_OfficeBlockAPITest(APIBaseTestCase):
    def test_non_authenticated_user_get_office_block(self):
        response = client.get(self.office_block_url)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_get_office_blocks_in_a_center_by_super_admin(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        token = "Token {}".format(self.token_user)
        response = client.get(self.center_block_url, HTTP_AUTHORIZATION=token)
        self.assertEqual(response.data["results"][0]["name"], self.office_block.name)
        self.assertEqual(response.data["results"][0]["id"], self.office_block.id)
        self.assertEqual(
            response.data["results"][0]["location"], self.office_block.location.id
        )
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_super_admin_can_get_office_blocks_in_other_center(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        token = "Token {}".format(self.token_user)
        response = client.get(self.other_center_block_url, HTTP_AUTHORIZATION=token)
        self.assertEqual(response.data["results"][0]["name"], self.office_block_2.name)
        self.assertEqual(response.data["results"][0]["id"], self.office_block_2.id)
        self.assertEqual(
            response.data["results"][0]["location"], self.office_block_2.location.id
        )
        self.assertEqual(response.status_code, 200)

    @patch("api.authentication.auth.verify_id_token")
    def test_normal_admin_can_get_office_block_in_their_center(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.normal_admin.email}
        token = "Token {}".format(self.test_normaladmin)
        response = client.get(self.center_block_url, HTTP_AUTHORIZATION=token)
        self.assertEqual(response.data["results"][0]["name"], self.office_block.name)
        self.assertEqual(response.data["results"][0]["id"], self.office_block.id)
        self.assertEqual(
            response.data["results"][0]["location"], self.office_block.location.id
        )
        self.assertEqual(response.status_code, 200)
    
    @patch("api.authentication.auth.verify_id_token")
    def test_normal_admin_can_get_office_block_with_valid_id(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.normal_admin.email}
        token = "Token {}".format(self.test_normaladmin)
        response = client.get("{}/{}/".format(self.office_block_url, self.office_block.id), HTTP_AUTHORIZATION=token)
        self.assertEqual(response.data["name"], self.office_block.name)
        self.assertEqual(response.data["id"], self.office_block.id)
        self.assertEqual(
            response.data["location"], self.office_block.location.id
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], self.office_block.name)
        self.assertEqual(response.data["id"], self.office_block.id)
        self.assertEqual(response.data["location"], self.office_block.location.id)
    
    @patch("api.authentication.auth.verify_id_token")
    def test_admin_can_get_office_blocks(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.normal_admin.email}
        token = "Token {}".format(self.test_normaladmin)
        response = client.get(self.office_block_url, HTTP_AUTHORIZATION=token)
        self.assertEqual(response.data["results"][0]["name"], self.office_block.name)
        self.assertEqual(response.data["results"][0]["id"], self.office_block.id)
        self.assertEqual(
            response.data["results"][0]["location"], self.office_block.location.id
        )
        self.assertEqual(response.status_code, 200)
    
    @patch("api.authentication.auth.verify_id_token")
    def test_admin_cannot_get_office_block_with_invalid_id(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.normal_admin.email}
        token = "Token {}".format(self.test_normaladmin)
        response = client.get(f"{self.office_block_url}/{400}/",
        HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data["detail"], "Not found.")
        self.assertEqual(response.status_code, 404)
    

    @patch("api.authentication.auth.verify_id_token")
    def test_normal_admin_cant_get_office_block_in_other_center(
        self, mock_verify_token
    ):
        mock_verify_token.return_value = {"email": self.normal_admin.email}
        token = "Token {}".format(self.test_normaladmin)
        response = client.get(self.other_center_block_url, HTTP_AUTHORIZATION=token)
        self.assertEqual(response.status_code, 403)

class Edit_OfficeBlockAPITest(APIBaseTestCase):
    @patch("api.authentication.auth.verify_id_token")
    def test_office_block_api_endpoint_cant_allow_put(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {}
        response = client.put(
            f"{self.office_block_url}/{self.office_block.id}/",
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"detail": 'Method "PUT" not allowed.'})
        self.assertEqual(response.status_code, 405)

    @patch("api.authentication.auth.verify_id_token")
    def test_office_block_api_endpoint_cant_allow_patch(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        data = {}
        response = client.patch(
            self.office_block_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"detail": 'Method "PATCH" not allowed.'})
        self.assertEqual(response.status_code, 405)

class Delete_OfficeBlockAPITest(APIBaseTestCase):
    @patch("api.authentication.auth.verify_id_token")
    def test_office_block_api_endpoint_cant_allow_delete(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.admin_user.email}
        response = client.delete(
            f"{self.office_block_url}/{self.office_block.id}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"detail": 'Method "DELETE" not allowed.'})
        self.assertEqual(response.status_code, 405)
