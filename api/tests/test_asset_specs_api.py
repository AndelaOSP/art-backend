# Standard Library
from unittest.mock import patch

# Third-Party Imports
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase

client = APIClient()


class Post_AssetSpecsAPITest(APIBaseTestCase):
    """ Tests for the AssetCategory endpoint"""

    def test_non_authenticated_user_cannot_create_asset_specs(self):
        data = {
            "year_of_manufacture": 2015,
            "processor_type": "Intel core i5",
            "screen_size": 13,
            "storage": 256,
            "memory": 8,
        }
        response = client.post(self.asset_specs_url, data=data)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_can_create_asset_specs(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {
            "year_of_manufacture": 2015,
            "processor_type": "Intel core i5",
            "screen_size": 13,
            "storage": 256,
            "memory": 8,
        }
        response = client.post(
            self.asset_specs_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data["year_of_manufacture"], data["year_of_manufacture"]
        )
        self.assertEqual(response.data["screen_size"], data["screen_size"])
        self.assertEqual(response.data["processor_type"], data["processor_type"])
        self.assertEqual(response.data["storage"], data["storage"])
        self.assertEqual(response.data["memory"], data["memory"])

    @patch("api.authentication.auth.verify_id_token")
    def test_non_admin_cannot_create_specs(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        data = {
            "year_of_manufacture": 2015,
            "processor_type": "Intel core i5",
            "screen_size": 13,
            "storage": 256,
            "memory": 8,
        }
        response = client.post(
            self.asset_specs_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.status_code, 403)

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_can_create_specs_with_missing_fields(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {
            "year_of_manufacture": 2016,
            "processor_type": "Intel core i3",
            "screen_size": 15,
        }
        response = client.post(
            self.asset_specs_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["processor_type"], response.data["processor_type"])
        self.assertEqual(
            response.data["year_of_manufacture"], data["year_of_manufacture"]
        )
        self.assertEqual(response.data["screen_size"], data["screen_size"])

    @patch("api.authentication.auth.verify_id_token")
    def test_asset_specs_unique_validation(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {
            "year_of_manufacture": 2017,
            "processor_type": "Intel core i7",
            "screen_size": 15,
            "storage": 512,
            "memory": 8,
        }
        response = client.post(
            f"{self.asset_specs_url}",
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["non_field_errors"],
            ["Similar asset specification already exist"],
        )


class Get_AssetSpecsAPITest(APIBaseTestCase):
    def test_non_authenticated_user_get_asset_specs(self):
        response = client.get(self.asset_specs_url)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_can_get_single_asset_specs(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            f"{self.asset_specs_url}/{self.asset_specs.id}",
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["processor_type"], self.asset_specs.processor_type
        )
        self.assertEqual(response.data["id"], self.asset_specs.id)
        self.assertEqual(
            response.data["year_of_manufacture"], self.asset_specs.year_of_manufacture
        )
        self.assertEqual(
            response.data["processor_speed"], self.asset_specs.processor_speed
        )
        self.assertEqual(response.data["screen_size"], self.asset_specs.screen_size)
        self.assertEqual(response.data["storage"], self.asset_specs.storage)
        self.assertEqual(response.data["memory"], self.asset_specs.memory)

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_can_get_asset_specs(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        response = client.get(
            self.asset_specs_url, HTTP_AUTHORIZATION="Token {}".format(self.token_admin)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["results"][0]["processor_type"],
            self.asset_specs.processor_type,
        )
        self.assertEqual(response.data["results"][0]["id"], self.asset_specs.id)
        self.assertEqual(
            response.data["results"][0]["year_of_manufacture"],
            self.asset_specs.year_of_manufacture,
        )
        self.assertEqual(
            response.data["results"][0]["processor_speed"],
            self.asset_specs.processor_speed,
        )
        self.assertEqual(
            response.data["results"][0]["screen_size"], self.asset_specs.screen_size
        )
        self.assertEqual(
            response.data["results"][0]["storage"], self.asset_specs.storage
        )
        self.assertEqual(response.data["results"][0]["memory"], self.asset_specs.memory)

    @patch("api.authentication.auth.verify_id_token")
    def test_non_admin_cannot_get_asset_specs(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        response = client.get(
            self.asset_specs_url, HTTP_AUTHORIZATION="Token {}".format(self.token_admin)
        )
        self.assertEqual(response.status_code, 403)

    @patch("api.authentication.auth.verify_id_token")
    def test_cannot_get_single_asset_asset_specs_with_invlaid_id(
        self, mock_verify_token
    ):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        response = client.delete(
            f"{self.asset_specs_url}/{300}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data["detail"], "Not found.")
        self.assertEqual(response.status_code, 404)

    @patch("api.authentication.auth.verify_id_token")
    def test_cannot_create_specs_with_invalid_fields(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        data = {
            "year_of_manufacture": 2011,
            "processor_type": "Intel core i5",
            "screen_size": 12,
            "storage": 256,
            "memory": 8,
        }
        response = client.post(
            self.asset_specs_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.status_code, 403)


class Edit_AssetSpecsAPITest(APIBaseTestCase):
    @patch("api.authentication.auth.verify_id_token")
    def test_admin_can_update_asset_specs(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {"storage": 128, "memory": 32}
        response = client.put(
            f"{self.asset_specs_url}/{self.asset_specs.id}",
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["memory"], response.data["memory"])
        self.assertEqual(data["storage"], response.data["storage"])
        self.assertEqual(response.data["id"], self.asset_specs.id)
        self.assertEqual(
            response.data["year_of_manufacture"], self.asset_specs.year_of_manufacture
        )
        self.assertEqual(
            response.data["processor_speed"], self.asset_specs.processor_speed
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_cannot_update_asset_specs_by_invalid_id(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {"storage": 128, "memory": 32}
        response = client.put(
            f"{self.asset_specs_url}/{300}",
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data["detail"], "Not found.")
        self.assertEqual(response.status_code, 404)


class Delete_AssetSpecsAPITest(APIBaseTestCase):
    @patch("api.authentication.auth.verify_id_token")
    def test_admin_can_update_asset_specs(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        data = {
            "year_of_manufacture": 2014,
            "processor_type": "Intel core i3",
            "screen_size": 15,
            "storage": 256,
            "memory": 16,
        }
        response = client.post(
            self.asset_specs_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        response = client.delete(
            f"{self.asset_specs_url}/{response.data['id']}",
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.status_code, 204)

    @patch("api.authentication.auth.verify_id_token")
    def test_admin_cannot_update_asset_specs_by_invalid_id(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.admin_user.email}
        response = client.delete(
            f"{self.asset_specs_url}/{300}",
            HTTP_AUTHORIZATION="Token {}".format(self.token_admin),
        )
        self.assertEqual(response.data["detail"], "Not found.")
        self.assertEqual(response.status_code, 404)
