# Standard Library
from unittest.mock import patch

# Third-Party Imports
from rest_framework.test import APIClient

# App Imports
from api.tests import APIBaseTestCase
from core.models import AssetCategory, AssetModelNumber

client = APIClient()


class Post_AssetModelNumberAPITest(APIBaseTestCase):
    """ Tests for the Asset Model Number endpoint"""

    def test_non_authenticated_user_get_asset_model_number(self):
        response = client.get(self.asset_model_no_url)
        self.assertEqual(
            response.data, {"detail": "Authentication credentials were not provided."}
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_can_post_asset_model_number(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        data = {"name": "TEST-MODEL-NO-1", "asset_make": self.asset_make.id}
        response = client.post(
            self.asset_model_no_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], data["name"])
        self.assertEqual(response.data["asset_make"], self.asset_make.name)
        self.assertEqual(response.data["model_number"], data["name"])
        self.assertEqual(response.data["make_label"], self.asset_make.name)

    @patch("api.authentication.auth.verify_id_token")
    def test_cannot_post_empty_model_number(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        data = {"name": "", "asset_make": self.asset_make.id}
        response = client.post(
            self.asset_model_no_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.status_code, 400)
        # remove comment after deprecation of old fields
        # self.assertEqual(response.data, {'name': ['This field may not be blank.']})

    @patch("api.authentication.auth.verify_id_token")
    def test_cannot_post_invalid_asset_make(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        data = {"name": "TEST", "asset_make": "Invalid"}
        response = client.post(
            self.asset_model_no_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(
            response.data,
            {
                "asset_make": [
                    f'Invalid pk "{data["asset_make"]}" - object does not exist.'
                ]
            },
        )
        self.assertEqual(response.status_code, 400)

    @patch("api.authentication.auth.verify_id_token")
    def test_cannot_post_empty_asset_make(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        data = {"name": "TEST", "asset_make": ""}
        response = client.post(
            self.asset_model_no_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"asset_make": ["This field is required."]})
        self.assertEqual(response.status_code, 400)


class Get_AssetModelNumberAPITest(APIBaseTestCase):
    @patch("api.authentication.auth.verify_id_token")
    def test_can_get_all_asset_model_numbers(self, mock_verify_token):

        mock_verify_token.return_value = {"email": self.user.email}
        response = client.get(
            self.asset_model_no_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )

        self.assertEqual(len(response.data["results"]), AssetCategory.objects.count())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["name"], self.assetmodel.name)
        self.assertEqual(
            response.data["results"][0]["asset_make"], self.asset_make.name
        )
        self.assertEqual(
            response.data["results"][0]["model_number"], self.assetmodel.name
        )
        self.assertEqual(
            response.data["results"][0]["make_label"], self.asset_make.name
        )

    @patch("api.authentication.auth.verify_id_token")
    def test_can_get_single_asset_model_number(self, mock_verify_token):
        mock_verify_token.return_value = {"email": self.user.email}
        response = client.get(
            f"{self.asset_model_no_url}/{self.assetmodel.id}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], self.assetmodel.name)
        self.assertEqual(response.data["asset_make"], self.asset_make.name)
        self.assertEqual(response.data["model_number"], self.assetmodel.name)
        self.assertEqual(response.data["make_label"], self.asset_make.name)

    @patch("api.authentication.auth.verify_id_token")
    def test_cannot_get_single_asset_model_number_with_invlaid_id(
        self, mock_verify_token
    ):
        mock_verify_token.return_value = {"email": self.user.email}
        response = client.get(
            f"{self.asset_model_no_url}/{300}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data["detail"], "Not found.")
        self.assertEqual(response.status_code, 404)

    @patch("api.authentication.auth.verify_id_token")
    def test_asset_model_number_api_orders_asset_models_by_model_number(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.user.email}
        AssetModelNumber.objects.create(name="BCD6G4D6 1F", asset_make=self.asset_make)
        AssetModelNumber.objects.create(name="XD6GRD6 Q3", asset_make=self.asset_make)

        response = client.get(
            self.asset_model_no_url,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(3, len(response.data.get("results")))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("results")[2].get("name"), "XD6GRD6 Q3")


class Edit_AssetModelNumberAPITest(APIBaseTestCase):
    @patch("api.authentication.auth.verify_id_token")
    def test_edit_asset_model_number_api_endpoint(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {"name": "TEST EDIT", "asset_make": self.asset_make.id}
        response = client.put(
            f"{self.asset_model_no_url}/{self.assetmodel.id}/",
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data.get("name"), "TEST EDIT")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["asset_make"], self.asset_make.name)
        self.assertEqual(response.data["model_number"], "TEST EDIT")
        self.assertEqual(response.data["make_label"], self.asset_make.name)

    @patch("api.authentication.auth.verify_id_token")
    def test_asset_model_number_api_endpoint_cant_allow_patch(
        self, mock_verify_id_token
    ):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {}
        response = client.patch(
            self.asset_model_no_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data, {"detail": 'Method "PATCH" not allowed.'})
        self.assertEqual(response.status_code, 405)

    @patch("api.authentication.auth.verify_id_token")
    def test_cannot_edit_single_asset_model_number_with_invlaid_id(
        self, mock_verify_token
    ):
        mock_verify_token.return_value = {"email": self.user.email}
        response = client.get(
            f"{self.asset_model_no_url}/{300}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data["detail"], "Not found.")
        self.assertEqual(response.status_code, 404)


class Delete_AssetModelNumberAPITest(APIBaseTestCase):
    @patch("api.authentication.auth.verify_id_token")
    def test_delete_asset_model_number_succeeds(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"email": self.user.email}
        data = {"name": "TEST-MODEL-NO-1", "asset_make": self.asset_make.id}
        response = client.post(
            self.asset_model_no_url,
            data=data,
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        response = client.delete(
            f"{self.asset_model_no_url}/{response.data['id']}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.status_code, 204)

    @patch("api.authentication.auth.verify_id_token")
    def test_cannot_delete_single_asset_model_number_with_invlaid_id(
        self, mock_verify_token
    ):
        mock_verify_token.return_value = {"email": self.user.email}
        response = client.delete(
            f"{self.asset_model_no_url}/{300}/",
            HTTP_AUTHORIZATION="Token {}".format(self.token_user),
        )
        self.assertEqual(response.data["detail"], "Not found.")
        self.assertEqual(response.status_code, 404)
